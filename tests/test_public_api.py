import modelwright


def test_root_facade_exports_primary_entrypoints() -> None:
    assert "extract_workbook" in modelwright.__all__
    assert "build_dependency_graph" in modelwright.__all__
    assert "translate_formula_cell" in modelwright.__all__
    assert "generate_python_module" in modelwright.__all__
    assert "build_validation_report" in modelwright.__all__
    assert "FormulasWorkbookOracle" in modelwright.__all__
    assert "build_conversion_plan" in modelwright.__all__
    assert "ConversionPlan" in modelwright.__all__
    assert "execute_generated_model" in modelwright.__all__
    assert "GeneratedExecutionResult" in modelwright.__all__
    assert "evaluate_generated_model" in modelwright.__all__
    assert "ValidationEvaluationResult" in modelwright.__all__
    assert "validation_evidence_paths" in modelwright.__all__
    assert "extract_validation_evidence" in modelwright.__all__
    assert "write_validation_evidence" in modelwright.__all__
    assert "ValidationEvidencePaths" in modelwright.__all__
    assert "ValidationEvidenceSummary" in modelwright.__all__
    assert "matrix_evidence_paths" in modelwright.__all__
    assert "extract_matrix_evidence" in modelwright.__all__
    assert "write_matrix_evidence" in modelwright.__all__
    assert "MatrixEvidencePaths" in modelwright.__all__
    assert "MatrixEvidenceSummary" in modelwright.__all__
    assert "MatrixEvidenceCaseSummary" in modelwright.__all__
    assert "infer_generated_module_contract" in modelwright.__all__
    assert "GeneratedContractInferenceResult" in modelwright.__all__
    assert "ModelFacade" in modelwright.__all__
    assert "Scenario" in modelwright.__all__
    assert "cell" in modelwright.__all__
    assert "table" in modelwright.__all__
    assert "report" in modelwright.__all__
    assert "inputs_frame" in modelwright.__all__
    assert "outputs_frame" in modelwright.__all__
    assert "table_frame" in modelwright.__all__
    assert "compare_scenarios_frame" in modelwright.__all__


def test_root_facade_does_not_export_internal_helpers() -> None:
    assert "FormulaReferenceIndex" not in modelwright.__all__
    assert "OracleOutputs" not in modelwright.__all__
    assert "missing_optional_dependency_diagnostic" not in modelwright.__all__
    assert "symbol_name_for_cell_ref" not in modelwright.__all__
