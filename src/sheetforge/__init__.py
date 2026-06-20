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
from sheetforge.formulas import (
    FormulaExpression,
    FormulaExpressionNode,
    FormulaTranslationDiagnostic,
    translate_formula_cell,
)
from sheetforge.graph import (
    DependencyEdge,
    DependencyGraph,
    build_dependency_graph,
)
from sheetforge.references import (
    WorkbookReference,
    normalize_cell_reference,
    normalize_reference,
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
    "DependencyEdge",
    "DependencyGraph",
    "Diagnostic",
    "ExtractionDiagnostic",
    "FormulaExpression",
    "FormulaExpressionNode",
    "FormulaRecord",
    "FormulaTranslationDiagnostic",
    "MISSING_VALUE",
    "NamedRangeRecord",
    "OracleConfig",
    "ScenarioInput",
    "ScenarioOutput",
    "SheetRecord",
    "ValidationReport",
    "ValidationScenario",
    "WorkbookReference",
    "WorkbookRecord",
    "__version__",
    "build_dependency_graph",
    "build_validation_report",
    "compare_scalar_output",
    "extract_workbook",
    "load_validation_scenario",
    "normalize_cell_reference",
    "normalize_reference",
    "translate_formula_cell",
]
