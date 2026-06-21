"""Validation orchestration over generated outputs, cached values, and oracles."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from modelwright.execution import GeneratedExecutionResult, execute_generated_model
from modelwright.extraction import WorkbookRecord
from modelwright.generation import GeneratedModuleContract
from modelwright.oracle_validation import build_oracle_validation_report
from modelwright.oracles import OracleResult
from modelwright.validation import (
    Diagnostic,
    JsonValue,
    OracleConfig,
    ValidationReport,
    ValidationScenario,
    build_validation_report,
)


@dataclass(frozen=True)
class ValidationEvaluationResult:
    """Generated-model execution plus validation reports for one scenario."""

    scenario_id: str
    generated_execution: GeneratedExecutionResult
    cached_validation_report: ValidationReport | None = None
    oracle_validation_report: ValidationReport | None = None
    diagnostics: tuple[Diagnostic, ...] = field(default_factory=tuple)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ValidationEvaluationResult":
        cached_report_data = data.get("cached_validation_report")
        oracle_report_data = data.get("oracle_validation_report")
        return cls(
            scenario_id=data["scenario_id"],
            generated_execution=GeneratedExecutionResult.from_dict(data["generated_execution"]),
            cached_validation_report=ValidationReport.from_dict(cached_report_data)
            if cached_report_data is not None
            else None,
            oracle_validation_report=ValidationReport.from_dict(oracle_report_data)
            if oracle_report_data is not None
            else None,
            diagnostics=tuple(Diagnostic.from_dict(item) for item in data.get("diagnostics", [])),
        )

    def to_dict(self) -> dict[str, JsonValue]:
        return {
            "scenario_id": self.scenario_id,
            "generated_execution": self.generated_execution.to_dict(),
            "cached_validation_report": self.cached_validation_report.to_dict()
            if self.cached_validation_report is not None
            else None,
            "oracle_validation_report": self.oracle_validation_report.to_dict()
            if self.oracle_validation_report is not None
            else None,
            "diagnostics": [diagnostic.to_dict() for diagnostic in self.diagnostics],
        }


def evaluate_generated_model(
    *,
    contract: GeneratedModuleContract,
    module_path: str | Path,
    scenario: ValidationScenario,
    workbook: WorkbookRecord | None = None,
    oracle_result: OracleResult | None = None,
) -> ValidationEvaluationResult:
    """Execute a generated model and build available validation reports."""

    generated_execution = execute_generated_model(
        contract=contract,
        module_path=module_path,
        inputs={scenario_input.cell_ref: scenario_input.value for scenario_input in scenario.inputs},
    )
    diagnostics = _execution_diagnostics(generated_execution)

    cached_validation_report = None
    if workbook is not None:
        cached_values, cached_diagnostics = _cached_output_values(workbook=workbook, scenario=scenario)
        diagnostics.extend(cached_diagnostics)
        cached_report = build_validation_report(
            scenario=_scenario_with_oracle_backend(scenario, "cached_workbook"),
            generated_values=generated_execution.output_values,
            oracle_values=cached_values,
        )
        cached_validation_report = _report_with_diagnostics(
            cached_report,
            tuple(diagnostics),
        )

    oracle_validation_report = None
    if oracle_result is not None:
        oracle_report = build_oracle_validation_report(
            scenario=scenario,
            generated_values=generated_execution.output_values,
            oracle_result=oracle_result,
        )
        oracle_validation_report = _report_with_diagnostics(
            oracle_report,
            tuple(_execution_diagnostics(generated_execution)),
        )

    return ValidationEvaluationResult(
        scenario_id=scenario.scenario_id,
        generated_execution=generated_execution,
        cached_validation_report=cached_validation_report,
        oracle_validation_report=oracle_validation_report,
        diagnostics=tuple(diagnostics),
    )


def _cached_output_values(
    *,
    workbook: WorkbookRecord,
    scenario: ValidationScenario,
) -> tuple[dict[str, JsonValue], tuple[Diagnostic, ...]]:
    cells_by_ref = {cell.cell_ref: cell for cell in workbook.cells}
    values: dict[str, JsonValue] = {}
    diagnostics: list[Diagnostic] = []
    for output in scenario.outputs:
        cell = cells_by_ref.get(output.cell_ref)
        if cell is None or cell.cached_value is None:
            diagnostics.append(
                Diagnostic(
                    diagnostic_code="missing_cached_formula_value",
                    message="cached workbook value is unavailable for validation output",
                    location=output.cell_ref,
                )
            )
            continue
        values[output.cell_ref] = cell.cached_value
    return values, tuple(diagnostics)


def _execution_diagnostics(generated_execution: GeneratedExecutionResult) -> list[Diagnostic]:
    return [
        Diagnostic(
            diagnostic_code=diagnostic.code,
            message=diagnostic.message,
            severity=diagnostic.severity,
            location=diagnostic.location,
        )
        for diagnostic in generated_execution.diagnostics
    ]


def _scenario_with_oracle_backend(scenario: ValidationScenario, backend: str) -> ValidationScenario:
    return ValidationScenario(
        scenario_id=scenario.scenario_id,
        description=scenario.description,
        source_workbook=scenario.source_workbook,
        generated_model=scenario.generated_model,
        oracle=OracleConfig(backend=backend),
        inputs=scenario.inputs,
        outputs=scenario.outputs,
        comparison=scenario.comparison,
    )


def _report_with_diagnostics(
    report: ValidationReport,
    diagnostics: tuple[Diagnostic, ...],
) -> ValidationReport:
    return ValidationReport(
        scenario_id=report.scenario_id,
        oracle_backend=report.oracle_backend,
        comparisons=report.comparisons,
        diagnostics=(*report.diagnostics, *diagnostics),
    )
