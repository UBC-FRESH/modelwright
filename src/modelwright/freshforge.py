"""FreshForge provider integration for Modelwright workflow stages."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

MODELWRIGHT_PROVIDER_ID = "modelwright"
MODELWRIGHT_PROVIDER_VERSION = "0.1.0a8"


@dataclass(frozen=True)
class _NodeContract:
    id: str
    name: str
    description: str
    inputs: tuple[str, ...] = ()
    outputs: tuple[str, ...] = ()
    parameters: tuple[str, ...] = ()
    artifacts: tuple[str, ...] = ()


_NODE_CONTRACTS: tuple[_NodeContract, ...] = (
    _NodeContract(
        id="workbook_extract",
        name="Extract workbook",
        description="Declare extraction of workbook facts into a WorkbookRecord.",
        outputs=("workbook_record",),
        parameters=("workbook",),
        artifacts=("workbook_record",),
    ),
    _NodeContract(
        id="workbook_graph",
        name="Build workbook dependency graph",
        description="Declare dependency graph construction from an extracted workbook record.",
        inputs=("workbook_record",),
        outputs=("dependency_graph",),
        artifacts=("dependency_graph",),
    ),
    _NodeContract(
        id="model_infer_contract",
        name="Infer generated-model contract",
        description="Declare selected-output generated-model contract inference.",
        outputs=("generated_contract", "formula_expressions", "input_constants"),
        parameters=("workbook", "module_name"),
        artifacts=("output_refs", "contract", "expressions", "constants", "inference_result"),
    ),
    _NodeContract(
        id="model_generate",
        name="Generate Python model",
        description="Declare standalone Python model generation from explicit JSON artifacts.",
        inputs=("generated_contract", "formula_expressions", "input_constants"),
        outputs=("generated_model",),
        artifacts=("contract", "expressions", "constants", "generated_model", "generation_result"),
    ),
    _NodeContract(
        id="model_execute",
        name="Execute generated model",
        description="Declare generated-model execution for selected outputs.",
        inputs=("generated_contract", "generated_model"),
        outputs=("generated_values",),
        artifacts=("contract", "generated_model", "generated_values"),
    ),
    _NodeContract(
        id="validation_evaluate",
        name="Evaluate generated model",
        description="Declare generated-model evaluation against cached or oracle-backed values.",
        inputs=("generated_contract", "generated_model"),
        outputs=("validation_report",),
        parameters=("scenario",),
        artifacts=("contract", "generated_model", "scenario", "evaluation_report"),
    ),
    _NodeContract(
        id="conversion_plan",
        name="Build conversion plan",
        description="Declare a Modelwright conversion-plan summary for the workflow boundary.",
        inputs=("workbook_record", "dependency_graph"),
        outputs=("conversion_plan",),
        parameters=("benchmark_role",),
        artifacts=("conversion_plan",),
    ),
)


class ModelwrightFreshForgeProvider:
    """FreshForge provider for Modelwright workflow stages."""

    def metadata(self) -> Any:
        """Return FreshForge provider metadata."""
        node_type_metadata, provider_metadata = _freshforge_metadata_types()
        return provider_metadata(
            id=MODELWRIGHT_PROVIDER_ID,
            version=MODELWRIGHT_PROVIDER_VERSION,
            name="Modelwright workflow provider",
            description=(
                "Provider for Modelwright workbook extraction, generated-model "
                "materialization, and validation workflow planning/execution."
            ),
            node_types=tuple(
                node_type_metadata(
                    id=contract.id,
                    name=contract.name,
                    description=contract.description,
                    inputs=contract.inputs,
                    outputs=contract.outputs,
                    parameters=contract.parameters,
                    artifacts=contract.artifacts,
                )
                for contract in _NODE_CONTRACTS
            ),
        )

    def validate_node(
        self,
        node: Any,
        node_type: Any,
        *,
        location: str,
    ) -> tuple[Any, ...]:
        """Validate broad Modelwright node shape without executing Modelwright."""
        diagnostic, severity = _freshforge_diagnostic_types()
        diagnostics: list[Any] = []
        diagnostics.extend(
            _missing_key_diagnostics(
                diagnostic=diagnostic,
                severity=severity,
                required=tuple(node_type.inputs),
                actual=node.inputs,
                field_name="inputs",
                location=location,
            )
        )
        diagnostics.extend(
            _missing_key_diagnostics(
                diagnostic=diagnostic,
                severity=severity,
                required=tuple(node_type.outputs),
                actual=node.outputs,
                field_name="outputs",
                location=location,
            )
        )
        diagnostics.extend(
            _missing_key_diagnostics(
                diagnostic=diagnostic,
                severity=severity,
                required=tuple(node_type.parameters),
                actual=node.parameters,
                field_name="parameters",
                location=location,
            )
        )
        artifacts = node.artifacts if isinstance(node.artifacts, dict) else {}
        diagnostics.extend(
            _missing_key_diagnostics(
                diagnostic=diagnostic,
                severity=severity,
                required=tuple(node_type.artifacts),
                actual=artifacts,
                field_name="artifacts",
                location=location,
            )
        )
        diagnostics.extend(
            _empty_parameter_diagnostics(
                diagnostic=diagnostic,
                severity=severity,
                parameters=node.parameters,
                required=tuple(node_type.parameters),
                location=location,
            )
        )
        diagnostics.extend(
            _empty_value_diagnostics(
                diagnostic=diagnostic,
                severity=severity,
                values=node.outputs,
                required=tuple(node_type.outputs),
                field_name="outputs",
                location=location,
            )
        )
        diagnostics.extend(
            _empty_value_diagnostics(
                diagnostic=diagnostic,
                severity=severity,
                values=artifacts,
                required=tuple(node_type.artifacts),
                field_name="artifacts",
                location=location,
            )
        )
        return tuple(diagnostics)

    def run_node(
        self,
        node: Any,
        node_type: Any,
        *,
        context: Any,
    ) -> Any:
        """Execute one supported generated-model workflow node."""
        diagnostic, severity, provider_result, run_status = _freshforge_run_types()
        try:
            artifacts = _resolved_artifacts(node, context)
            if node_type.id == "model_infer_contract":
                payload = _run_model_infer_contract(node, artifacts, context)
                summary = _infer_contract_summary(payload)
                _write_json(artifacts["inference_result"], payload)
                return provider_result(
                    status=run_status.SUCCESS,
                    outputs={
                        "generated_contract": str(artifacts["contract"]),
                        "formula_expressions": str(artifacts["expressions"]),
                        "input_constants": str(artifacts["constants"]),
                    },
                    artifacts=_string_artifacts(artifacts),
                    data={"inferred": payload.get("inferred"), "summary": summary},
                )
            if node_type.id == "model_generate":
                payload = _run_model_generate(artifacts)
                summary = _model_generate_summary(payload)
                stage_diagnostics = _stage_failure_diagnostics(
                    diagnostic=diagnostic,
                    severity=severity,
                    failed=not bool(payload.get("generated")),
                    code="modelwright.model_generate.failed",
                    message="Modelwright generated-model source generation failed.",
                    location=f"nodes.{node.id}",
                )
                _write_json(artifacts["generation_result"], payload)
                return provider_result(
                    status=run_status.SUCCESS if payload.get("generated") else run_status.FAILED,
                    outputs={"generated_model": str(artifacts["generated_model"])},
                    artifacts=_string_artifacts(artifacts),
                    diagnostics=stage_diagnostics,
                    data={"generated": payload.get("generated"), "summary": summary},
                )
            if node_type.id == "model_execute":
                payload = _run_model_execute(artifacts)
                summary = _model_execute_summary(payload)
                stage_diagnostics = _stage_failure_diagnostics(
                    diagnostic=diagnostic,
                    severity=severity,
                    failed=not bool(payload.get("executed")),
                    code="modelwright.model_execute.failed",
                    message="Modelwright generated-model execution failed.",
                    location=f"nodes.{node.id}",
                )
                _write_json(artifacts["generated_values"], payload)
                return provider_result(
                    status=run_status.SUCCESS if payload.get("executed") else run_status.FAILED,
                    outputs={"generated_values": str(artifacts["generated_values"])},
                    artifacts=_string_artifacts(artifacts),
                    diagnostics=stage_diagnostics,
                    data={"executed": payload.get("executed"), "summary": summary},
                )
            if node_type.id == "validation_evaluate":
                payload = _run_validation_evaluate(node, artifacts, context)
                summary = _validation_evaluate_summary(payload)
                validation_failed = _validation_evaluate_failed(payload)
                stage_diagnostics = _stage_failure_diagnostics(
                    diagnostic=diagnostic,
                    severity=severity,
                    failed=validation_failed,
                    code="modelwright.validation_evaluate.failed",
                    message="Modelwright generated-model validation evaluation failed.",
                    location=f"nodes.{node.id}",
                )
                _write_json(artifacts["evaluation_report"], payload)
                return provider_result(
                    status=run_status.FAILED if validation_failed else run_status.SUCCESS,
                    outputs={"validation_report": str(artifacts["evaluation_report"])},
                    artifacts=_string_artifacts(artifacts),
                    diagnostics=stage_diagnostics,
                    data={
                        "cached_validation_status": (
                            payload.get("cached_validation_report", {}) or {}
                        ).get("status"),
                        "summary": summary,
                    },
                )
        except Exception as exc:  # noqa: BLE001
            return provider_result(
                status=run_status.FAILED,
                diagnostics=(
                    diagnostic(
                        severity=severity.ERROR,
                        code="modelwright.execution.failed",
                        message=f"Modelwright FreshForge node failed: {exc}",
                        location=f"nodes.{node.id}",
                    ),
                ),
            )
        return provider_result(
            status=run_status.FAILED,
            diagnostics=(
                diagnostic(
                    severity=severity.ERROR,
                    code="modelwright.execution.unsupported",
                    message=f"Modelwright node type '{node_type.id}' is not executable.",
                    location=f"nodes.{node.id}",
                ),
            ),
        )


def provider_factory() -> ModelwrightFreshForgeProvider:
    """Return the Modelwright FreshForge provider for entry-point discovery."""
    return ModelwrightFreshForgeProvider()


def _freshforge_metadata_types() -> tuple[Any, Any]:
    try:
        from freshforge.providers import (  # type: ignore[import-untyped]
            NodeTypeMetadata,
            ProviderMetadata,
        )
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "The Modelwright FreshForge integration requires FreshForge to be installed separately."
        ) from exc
    return NodeTypeMetadata, ProviderMetadata


def _freshforge_diagnostic_types() -> tuple[Any, Any]:
    try:
        from freshforge.records import (  # type: ignore[import-untyped]
            Diagnostic,
            DiagnosticSeverity,
        )
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "The Modelwright FreshForge integration requires FreshForge to be installed separately."
        ) from exc
    return Diagnostic, DiagnosticSeverity


def _freshforge_run_types() -> tuple[Any, Any, Any, Any]:
    try:
        from freshforge.records import (  # type: ignore[import-untyped]
            Diagnostic,
            DiagnosticSeverity,
            ProviderRunResult,
            RunStatus,
        )
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "The Modelwright FreshForge integration requires FreshForge to be installed separately."
        ) from exc
    return Diagnostic, DiagnosticSeverity, ProviderRunResult, RunStatus


def _run_model_infer_contract(
    node: Any,
    artifacts: dict[str, Path],
    context: Any,
) -> dict[str, Any]:
    from modelwright.cli import _infer_contract_payload

    return _infer_contract_payload(
        workbook=context.resolve_path(node.parameters["workbook"]),
        module_name=node.parameters["module_name"],
        output_refs=(),
        output_refs_file=artifacts["output_refs"],
        contract=artifacts["contract"],
        expressions=artifacts["expressions"],
        constants=artifacts["constants"],
        verbose=False,
    )


def _run_model_generate(artifacts: dict[str, Path]) -> dict[str, Any]:
    from modelwright.cli import _generate_payload

    return _generate_payload(
        contract=artifacts["contract"],
        expressions=artifacts["expressions"],
        constants=artifacts["constants"],
        output=artifacts["generated_model"],
    )


def _run_model_execute(artifacts: dict[str, Path]) -> dict[str, Any]:
    from modelwright.cli import _execute_payload

    return _execute_payload(
        contract=artifacts["contract"],
        model=artifacts["generated_model"],
        inputs=artifacts.get("inputs"),
    )


def _run_validation_evaluate(
    node: Any,
    artifacts: dict[str, Path],
    context: Any,
) -> dict[str, Any]:
    from modelwright.cli import _evaluate_payload

    workbook = node.parameters.get("workbook")
    return _evaluate_payload(
        contract=artifacts["contract"],
        model=artifacts["generated_model"],
        scenario=artifacts["scenario"],
        workbook=context.resolve_path(workbook) if isinstance(workbook, str) else None,
        workbook_record=artifacts.get("workbook_record"),
        oracle_result=artifacts.get("oracle_result"),
        verbose=False,
    )


def _resolved_artifacts(node: Any, context: Any) -> dict[str, Path]:
    if not isinstance(node.artifacts, dict):
        return {}
    return {
        key: context.resolve_path(value)
        for key, value in node.artifacts.items()
        if isinstance(value, str)
    }


def _string_artifacts(artifacts: dict[str, Path]) -> dict[str, str]:
    return {key: str(value) for key, value in artifacts.items()}


def _write_json(path: Path, payload: Any) -> None:
    import json

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _infer_contract_summary(payload: dict[str, Any]) -> dict[str, Any]:
    contract = _dict(payload.get("contract"))
    diagnostics = _list(payload.get("diagnostics"))
    return {
        "stage": "model_infer_contract",
        "inferred": bool(payload.get("inferred")),
        "input_ref_count": len(_list(contract.get("input_refs"))),
        "output_ref_count": len(_list(contract.get("output_refs"))),
        "symbol_count": len(_list(contract.get("symbols"))),
        "expression_count": len(_dict(payload.get("expressions"))),
        "constant_count": len(_dict(payload.get("constants"))),
        **_diagnostic_counts(diagnostics),
    }


def _model_generate_summary(payload: dict[str, Any]) -> dict[str, Any]:
    contract = _dict(payload.get("contract"))
    source_code = payload.get("source_code")
    source = source_code if isinstance(source_code, str) else ""
    diagnostics = _list(payload.get("diagnostics"))
    return {
        "stage": "model_generate",
        "generated": bool(payload.get("generated")),
        "source_line_count": len(source.splitlines()),
        "source_byte_count": len(source.encode("utf-8")),
        "input_ref_count": len(_list(contract.get("input_refs"))),
        "output_ref_count": len(_list(contract.get("output_refs"))),
        "symbol_count": len(_list(contract.get("symbols"))),
        **_diagnostic_counts(diagnostics),
    }


def _model_execute_summary(payload: dict[str, Any]) -> dict[str, Any]:
    contract = _dict(payload.get("contract"))
    output_values = _dict(payload.get("output_values"))
    diagnostics = _list(payload.get("diagnostics"))
    return {
        "stage": "model_execute",
        "executed": bool(payload.get("executed")),
        "declared_output_count": len(_list(contract.get("output_refs"))),
        "generated_output_count": len(output_values),
        "missing_output_diagnostic_count": _diagnostic_code_count(
            diagnostics,
            "missing_generated_output",
        ),
        **_diagnostic_counts(diagnostics),
    }


def _validation_evaluate_summary(payload: dict[str, Any]) -> dict[str, Any]:
    generated_execution = _dict(payload.get("generated_execution"))
    generated_diagnostics = _list(generated_execution.get("diagnostics"))
    diagnostics = (*generated_diagnostics, *_list(payload.get("diagnostics")))
    return {
        "stage": "validation_evaluate",
        "scenario_id": payload.get("scenario_id"),
        "generated_execution": {
            "executed": bool(generated_execution.get("executed")),
            "declared_output_count": len(
                _list(_dict(generated_execution.get("contract")).get("output_refs"))
            ),
            "generated_output_count": len(_dict(generated_execution.get("output_values"))),
            **_diagnostic_counts(generated_diagnostics),
        },
        "cached_validation": _validation_report_summary(
            _dict_or_none(payload.get("cached_validation_report"))
        ),
        "oracle_validation": _validation_report_summary(
            _dict_or_none(payload.get("oracle_validation_report"))
        ),
        **_diagnostic_counts(diagnostics),
    }


def _validation_report_summary(report: dict[str, Any] | None) -> dict[str, Any]:
    if report is None:
        return {
            "available": False,
            "status": None,
            "comparison_count": 0,
            "match_count": 0,
            "mismatch_count": 0,
            "diagnostic_count": 0,
            "error_count": 0,
            "warning_count": 0,
        }
    comparisons = _list(report.get("comparisons"))
    mismatches = _list(report.get("mismatches"))
    diagnostics = _list(report.get("diagnostics"))
    return {
        "available": True,
        "status": report.get("status"),
        "comparison_count": len(comparisons),
        "match_count": len(comparisons) - len(mismatches),
        "mismatch_count": len(mismatches),
        **_diagnostic_counts(diagnostics),
    }


def _validation_evaluate_failed(payload: dict[str, Any]) -> bool:
    generated_execution = _dict(payload.get("generated_execution"))
    if not bool(generated_execution.get("executed")):
        return True
    reports = (
        _dict_or_none(payload.get("cached_validation_report")),
        _dict_or_none(payload.get("oracle_validation_report")),
    )
    if any(report is not None and report.get("status") == "fail" for report in reports):
        return True
    diagnostics = (*_list(generated_execution.get("diagnostics")), *_list(payload.get("diagnostics")))
    return _diagnostic_counts(diagnostics)["error_count"] > 0


def _stage_failure_diagnostics(
    *,
    diagnostic: Any,
    severity: Any,
    failed: bool,
    code: str,
    message: str,
    location: str,
) -> tuple[Any, ...]:
    if not failed:
        return ()
    return (
        diagnostic(
            severity=severity.ERROR,
            code=code,
            message=message,
            location=location,
        ),
    )


def _diagnostic_counts(diagnostics: tuple[Any, ...]) -> dict[str, int]:
    return {
        "diagnostic_count": len(diagnostics),
        "error_count": sum(1 for diagnostic in diagnostics if _diagnostic_severity(diagnostic) == "error"),
        "warning_count": sum(1 for diagnostic in diagnostics if _diagnostic_severity(diagnostic) == "warning"),
    }


def _diagnostic_code_count(diagnostics: tuple[Any, ...], code: str) -> int:
    return sum(1 for diagnostic in diagnostics if _diagnostic_code(diagnostic) == code)


def _diagnostic_severity(diagnostic: Any) -> str | None:
    if isinstance(diagnostic, dict):
        value = diagnostic.get("severity")
        return value if isinstance(value, str) else None
    value = getattr(diagnostic, "severity", None)
    return value if isinstance(value, str) else None


def _diagnostic_code(diagnostic: Any) -> str | None:
    if isinstance(diagnostic, dict):
        value = diagnostic.get("code") or diagnostic.get("diagnostic_code")
        return value if isinstance(value, str) else None
    value = getattr(diagnostic, "code", None) or getattr(diagnostic, "diagnostic_code", None)
    return value if isinstance(value, str) else None


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _dict_or_none(value: Any) -> dict[str, Any] | None:
    return value if isinstance(value, dict) else None


def _list(value: Any) -> tuple[Any, ...]:
    return tuple(value) if isinstance(value, list) else ()


def _missing_key_diagnostics(
    *,
    diagnostic: Any,
    severity: Any,
    required: tuple[str, ...],
    actual: dict[str, Any],
    field_name: str,
    location: str,
) -> tuple[Any, ...]:
    return tuple(
        diagnostic(
            severity=severity.ERROR,
            code=f"modelwright.{field_name}.missing",
            message=(
                f"Modelwright node requires {field_name} key '{key}' for "
                "non-executing workflow planning."
            ),
            location=f"{location}.{field_name}.{key}",
        )
        for key in required
        if key not in actual
    )


def _empty_parameter_diagnostics(
    *,
    diagnostic: Any,
    severity: Any,
    parameters: dict[str, Any],
    required: tuple[str, ...],
    location: str,
) -> tuple[Any, ...]:
    diagnostics: list[Any] = []
    for key in required:
        value = parameters.get(key)
        if isinstance(value, str) and not value.strip():
            diagnostics.append(
                diagnostic(
                    severity=severity.ERROR,
                    code="modelwright.parameters.empty",
                    message=f"Modelwright node parameter '{key}' must be nonempty.",
                    location=f"{location}.parameters.{key}",
                )
            )
    return tuple(diagnostics)


def _empty_value_diagnostics(
    *,
    diagnostic: Any,
    severity: Any,
    values: dict[str, Any],
    required: tuple[str, ...],
    field_name: str,
    location: str,
) -> tuple[Any, ...]:
    diagnostics: list[Any] = []
    for key in required:
        value = values.get(key)
        if isinstance(value, str) and not value.strip():
            diagnostics.append(
                diagnostic(
                    severity=severity.ERROR,
                    code=f"modelwright.{field_name}.empty",
                    message=f"Modelwright node {field_name} key '{key}' must be nonempty.",
                    location=f"{location}.{field_name}.{key}",
                )
            )
    return tuple(diagnostics)
