import sheetforge


def test_root_facade_exports_primary_entrypoints() -> None:
    assert "extract_workbook" in sheetforge.__all__
    assert "build_dependency_graph" in sheetforge.__all__
    assert "translate_formula_cell" in sheetforge.__all__
    assert "generate_python_module" in sheetforge.__all__
    assert "build_validation_report" in sheetforge.__all__
    assert "FormulasWorkbookOracle" in sheetforge.__all__
    assert "build_conversion_plan" in sheetforge.__all__
    assert "ConversionPlan" in sheetforge.__all__
    assert "execute_generated_model" in sheetforge.__all__
    assert "GeneratedExecutionResult" in sheetforge.__all__


def test_root_facade_does_not_export_internal_helpers() -> None:
    assert "FormulaReferenceIndex" not in sheetforge.__all__
    assert "OracleOutputs" not in sheetforge.__all__
    assert "missing_optional_dependency_diagnostic" not in sheetforge.__all__
    assert "symbol_name_for_cell_ref" not in sheetforge.__all__
