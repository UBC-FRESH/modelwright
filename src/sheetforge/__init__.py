"""Sheetforge package skeleton."""

from sheetforge.validation import (
    ComparisonResult,
    ComparisonRules,
    Diagnostic,
    MISSING_VALUE,
    OracleConfig,
    ScenarioInput,
    ScenarioOutput,
    ValidationReport,
    ValidationScenario,
    build_validation_report,
    compare_scalar_output,
    load_validation_scenario,
)

__version__ = "0.0.0"

__all__ = [
    "ComparisonResult",
    "ComparisonRules",
    "Diagnostic",
    "MISSING_VALUE",
    "OracleConfig",
    "ScenarioInput",
    "ScenarioOutput",
    "ValidationReport",
    "ValidationScenario",
    "__version__",
    "build_validation_report",
    "compare_scalar_output",
    "load_validation_scenario",
]
