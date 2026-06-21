"""Modelwright package skeleton."""

from modelwright.extraction import (
    CellRecord,
    ExtractionDiagnostic,
    FormulaRecord,
    NamedRangeRecord,
    SheetRecord,
    TableRecord,
    WorkbookRecord,
    extract_workbook,
)
from modelwright.execution import (
    ExecutionDiagnostic,
    GeneratedExecutionResult,
    execute_generated_model,
)
from modelwright.evaluation import (
    ValidationEvaluationResult,
    evaluate_generated_model,
)
from modelwright.conversion import (
    ConversionPlan,
    ConversionSource,
    CoverageSummary,
    DiagnosticSummary,
    GenerationSummary,
    PlanRecommendation,
    PrivacyReview,
    ResidualBlocker,
    ValidationSummary,
    WorkflowStatus,
    build_conversion_plan,
)
from modelwright.formulas import (
    FormulaExpression,
    FormulaExpressionNode,
    FormulaTranslationDiagnostic,
    build_formula_reference_index,
    translate_formula_cell,
)
from modelwright.formulas_oracle import FormulasWorkbookOracle
from modelwright.generation import (
    GeneratedContractInferenceResult,
    GeneratedModuleContract,
    GeneratedSymbol,
    GenerationDiagnostic,
    GenerationResult,
    generate_python_module,
    infer_generated_module_contract,
)
from modelwright.graph import (
    DependencyEdge,
    DependencyGraph,
    build_dependency_graph,
)
from modelwright.oracles import (
    OracleDiagnostic,
    OracleRequest,
    OracleResult,
    WorkbookOracle,
)
from modelwright.oracle_validation import build_oracle_validation_report
from modelwright.references import (
    WorkbookReference,
    normalize_cell_reference,
    normalize_reference,
)
from modelwright.validation import (
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

__version__ = "0.1.0a2"

__all__ = [
    "CellRecord",
    "ComparisonResult",
    "ComparisonRules",
    "ConversionPlan",
    "ConversionSource",
    "CoverageSummary",
    "DependencyEdge",
    "DependencyGraph",
    "Diagnostic",
    "DiagnosticSummary",
    "ExtractionDiagnostic",
    "ExecutionDiagnostic",
    "FormulaExpression",
    "FormulaExpressionNode",
    "FormulaRecord",
    "FormulaTranslationDiagnostic",
    "FormulasWorkbookOracle",
    "GeneratedModuleContract",
    "GeneratedExecutionResult",
    "GeneratedContractInferenceResult",
    "GeneratedSymbol",
    "GenerationSummary",
    "GenerationDiagnostic",
    "GenerationResult",
    "MISSING_VALUE",
    "NamedRangeRecord",
    "OracleConfig",
    "OracleDiagnostic",
    "OracleRequest",
    "OracleResult",
    "PlanRecommendation",
    "PrivacyReview",
    "ResidualBlocker",
    "ScenarioInput",
    "ScenarioOutput",
    "SheetRecord",
    "TableRecord",
    "ValidationReport",
    "ValidationEvaluationResult",
    "ValidationScenario",
    "ValidationSummary",
    "WorkbookOracle",
    "WorkbookReference",
    "WorkbookRecord",
    "WorkflowStatus",
    "__version__",
    "build_dependency_graph",
    "build_conversion_plan",
    "build_formula_reference_index",
    "build_oracle_validation_report",
    "build_validation_report",
    "compare_scalar_output",
    "execute_generated_model",
    "evaluate_generated_model",
    "extract_workbook",
    "generate_python_module",
    "infer_generated_module_contract",
    "load_validation_scenario",
    "normalize_cell_reference",
    "normalize_reference",
    "translate_formula_cell",
]
