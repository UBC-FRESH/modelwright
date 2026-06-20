"""Sheetforge package skeleton."""

from sheetforge.extraction import (
    CellRecord,
    ExtractionDiagnostic,
    FormulaRecord,
    NamedRangeRecord,
    SheetRecord,
    WorkbookRecord,
    extract_workbook,
)
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
    "CellRecord",
    "ComparisonResult",
    "ComparisonRules",
    "Diagnostic",
    "ExtractionDiagnostic",
    "FormulaRecord",
    "MISSING_VALUE",
    "NamedRangeRecord",
    "OracleConfig",
    "ScenarioInput",
    "ScenarioOutput",
    "SheetRecord",
    "ValidationReport",
    "ValidationScenario",
    "WorkbookRecord",
    "__version__",
    "build_validation_report",
    "compare_scalar_output",
    "extract_workbook",
    "load_validation_scenario",
]
