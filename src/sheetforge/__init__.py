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
from sheetforge.formulas_oracle import FormulasWorkbookOracle
from sheetforge.generation import (
    GeneratedModuleContract,
    GeneratedSymbol,
    GenerationDiagnostic,
    GenerationResult,
    generate_python_module,
    symbol_name_for_cell_ref,
)
from sheetforge.graph import (
    DependencyEdge,
    DependencyGraph,
    build_dependency_graph,
)
from sheetforge.oracles import (
    OracleDiagnostic,
    OracleOutputs,
    OracleRequest,
    OracleResult,
    WorkbookOracle,
    missing_optional_dependency_diagnostic,
)
from sheetforge.oracle_validation import build_oracle_validation_report
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
    "FormulasWorkbookOracle",
    "GeneratedModuleContract",
    "GeneratedSymbol",
    "GenerationDiagnostic",
    "GenerationResult",
    "MISSING_VALUE",
    "NamedRangeRecord",
    "OracleConfig",
    "OracleDiagnostic",
    "OracleOutputs",
    "OracleRequest",
    "OracleResult",
    "ScenarioInput",
    "ScenarioOutput",
    "SheetRecord",
    "ValidationReport",
    "ValidationScenario",
    "WorkbookOracle",
    "WorkbookReference",
    "WorkbookRecord",
    "__version__",
    "build_dependency_graph",
    "build_oracle_validation_report",
    "build_validation_report",
    "compare_scalar_output",
    "extract_workbook",
    "generate_python_module",
    "load_validation_scenario",
    "missing_optional_dependency_diagnostic",
    "normalize_cell_reference",
    "normalize_reference",
    "symbol_name_for_cell_ref",
    "translate_formula_cell",
]
