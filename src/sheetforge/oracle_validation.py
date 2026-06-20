"""Validation report helpers for oracle-backed comparisons."""

from __future__ import annotations

from collections.abc import Mapping

from sheetforge.oracles import OracleResult
from sheetforge.validation import (
    Diagnostic,
    JsonValue,
    ValidationReport,
    ValidationScenario,
    build_validation_report,
)


def build_oracle_validation_report(
    *,
    scenario: ValidationScenario,
    generated_values: Mapping[str, JsonValue],
    oracle_result: OracleResult,
) -> ValidationReport:
    """Compare generated values against an oracle result for one scenario."""

    report = build_validation_report(
        scenario=scenario,
        generated_values=generated_values,
        oracle_values=oracle_result.outputs,
    )
    diagnostics = list(_oracle_diagnostics(oracle_result))

    if scenario.oracle.backend != oracle_result.backend:
        diagnostics.append(
            Diagnostic(
                diagnostic_code="oracle_backend_mismatch",
                message="scenario oracle backend does not match oracle result backend",
                severity="error",
                location=scenario.scenario_id,
            )
        )

    return ValidationReport(
        scenario_id=report.scenario_id,
        oracle_backend=oracle_result.backend,
        comparisons=report.comparisons,
        diagnostics=tuple(diagnostics),
    )


def _oracle_diagnostics(oracle_result: OracleResult) -> tuple[Diagnostic, ...]:
    return tuple(
        Diagnostic(
            diagnostic_code=diagnostic.diagnostic_code,
            message=diagnostic.message,
            severity=diagnostic.severity,
            location=diagnostic.location,
        )
        for diagnostic in oracle_result.diagnostics
    )
