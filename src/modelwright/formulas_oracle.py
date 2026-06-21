"""`formulas`-backed workbook oracle."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from modelwright.oracles import (
    OracleDiagnostic,
    OracleRequest,
    OracleResult,
    WorkbookOracle,
    missing_optional_dependency_diagnostic,
)
from modelwright.validation import JsonValue


class FormulasWorkbookOracle(WorkbookOracle):
    """Evaluate workbook outputs with the optional `formulas` package."""

    backend_name = "formulas"

    def evaluate(self, request: OracleRequest) -> OracleResult:
        if request.inputs:
            return OracleResult(
                backend=self.backend_name,
                source_workbook=request.source_workbook,
                diagnostics=(
                    OracleDiagnostic(
                        diagnostic_code="unsupported_oracle_inputs",
                        message="formulas oracle input overrides are not supported yet",
                        severity="error",
                    ),
                ),
            )

        try:
            import formulas
        except ImportError:
            return OracleResult(
                backend=self.backend_name,
                source_workbook=request.source_workbook,
                diagnostics=(
                    missing_optional_dependency_diagnostic(
                        dependency="formulas",
                        extra="oracle",
                        backend=self.backend_name,
                    ),
                ),
            )

        workbook_path = Path(request.source_workbook)
        if not workbook_path.exists():
            return OracleResult(
                backend=self.backend_name,
                source_workbook=request.source_workbook,
                diagnostics=(
                    OracleDiagnostic(
                        diagnostic_code="missing_source_workbook",
                        message="source workbook does not exist",
                        severity="error",
                        location=str(workbook_path),
                    ),
                ),
            )

        try:
            model = formulas.ExcelModel().loads(str(workbook_path)).finish()
            calculated = model.calculate()
        except Exception as exc:
            return OracleResult(
                backend=self.backend_name,
                source_workbook=request.source_workbook,
                diagnostics=(
                    OracleDiagnostic(
                        diagnostic_code="oracle_calculation_failed",
                        message=str(exc),
                        severity="error",
                        location=str(workbook_path),
                        raw_value=exc.__class__.__name__,
                    ),
                ),
            )

        outputs: dict[str, JsonValue] = {}
        diagnostics: list[OracleDiagnostic] = []
        for output in request.outputs:
            matched_key, value = _find_output_value(calculated, output.cell_ref)
            if matched_key is None:
                diagnostics.append(
                    OracleDiagnostic(
                        diagnostic_code="missing_oracle_output",
                        message="formulas did not return the requested workbook output",
                        severity="error",
                        location=output.cell_ref,
                    )
                )
                continue

            try:
                outputs[output.cell_ref] = _to_json_scalar(value)
            except ValueError as exc:
                diagnostics.append(
                    OracleDiagnostic(
                        diagnostic_code="unsupported_oracle_value",
                        message=str(exc),
                        severity="error",
                        location=output.cell_ref,
                        raw_value=str(matched_key),
                    )
                )

        return OracleResult(
            backend=self.backend_name,
            source_workbook=request.source_workbook,
            outputs=outputs,
            diagnostics=tuple(diagnostics),
        )


def _find_output_value(calculated: Any, cell_ref: str) -> tuple[Any | None, Any | None]:
    for key, value in calculated.items():
        if _matches_cell_ref(str(key), cell_ref):
            return key, value
    return None, None


def _matches_cell_ref(formulas_key: str, cell_ref: str) -> bool:
    if "!" not in cell_ref:
        return False

    sheet_name, coordinate = cell_ref.split("!", 1)
    expected_suffix = f"]{sheet_name.upper()}'!{coordinate.upper().replace('$', '')}"
    return formulas_key.upper().replace("$", "").endswith(expected_suffix)


def _to_json_scalar(value: Any) -> JsonValue:
    if hasattr(value, "value"):
        value = value.value

    if hasattr(value, "tolist"):
        value = value.tolist()

    while isinstance(value, list) and len(value) == 1:
        value = value[0]

    if hasattr(value, "item"):
        value = value.item()

    if value is None or isinstance(value, str | int | float | bool):
        return value

    raise ValueError(f"unsupported oracle value type: {type(value).__name__}")
