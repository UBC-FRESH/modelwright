"""Sheetforge package skeleton."""

from sheetforge.validation import (
    ComparisonResult,
    ComparisonRules,
    Diagnostic,
    OracleConfig,
    ScenarioInput,
    ScenarioOutput,
    ValidationReport,
    ValidationScenario,
    load_validation_scenario,
)

__version__ = "0.0.0"

__all__ = [
    "ComparisonResult",
    "ComparisonRules",
    "Diagnostic",
    "OracleConfig",
    "ScenarioInput",
    "ScenarioOutput",
    "ValidationReport",
    "ValidationScenario",
    "__version__",
    "load_validation_scenario",
]
