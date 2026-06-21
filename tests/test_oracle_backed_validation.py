import importlib.util
import sys
from pathlib import Path
from types import ModuleType

from modelwright.extraction import extract_workbook
from modelwright.formulas import translate_formula_cell
from modelwright.formulas_oracle import FormulasWorkbookOracle
from modelwright.generation import (
    GeneratedModuleContract,
    GeneratedSymbol,
    generate_python_module,
    symbol_name_for_cell_ref,
)
from modelwright.graph import build_dependency_graph
from modelwright.oracle_validation import build_oracle_validation_report
from modelwright.oracles import OracleDiagnostic, OracleRequest, OracleResult
from modelwright.validation import (
    ComparisonRules,
    OracleConfig,
    ScenarioOutput,
    ValidationScenario,
)
from tests.fixtures.synthetic_model.build_workbook import build_workbook


def test_generated_synthetic_model_validates_against_formulas_oracle(tmp_path: Path) -> None:
    workbook_path = build_workbook(tmp_path / "synthetic_model.xlsx")
    generated_values = _generated_synthetic_outputs(workbook_path, tmp_path / "generated_model.py")
    scenario = _baseline_scenario(workbook_path, tmp_path / "generated_model.py")
    oracle_result = FormulasWorkbookOracle().evaluate(
        OracleRequest(
            source_workbook=str(workbook_path),
            outputs=scenario.outputs,
        )
    )

    report = build_oracle_validation_report(
        scenario=scenario,
        generated_values=generated_values,
        oracle_result=oracle_result,
    )

    assert report.status == "pass"
    assert report.oracle_backend == "formulas"
    assert report.diagnostics == ()
    assert [comparison.to_dict() for comparison in report.comparisons] == [
        {
            "scenario_id": "synthetic_model_baseline",
            "cell_ref": "Summary!B2",
            "kind": "number",
            "generated": 70.2,
            "oracle": 70.2,
            "matches": True,
            "tolerance": 1e-9,
            "difference": 0.0,
            "diagnostic_code": None,
            "message": "values match",
            "oracle_backend": "formulas",
        },
        {
            "scenario_id": "synthetic_model_baseline",
            "cell_ref": "Summary!B3",
            "kind": "text",
            "generated": "ok",
            "oracle": "ok",
            "matches": True,
            "tolerance": None,
            "difference": None,
            "diagnostic_code": None,
            "message": "values match",
            "oracle_backend": "formulas",
        },
    ]


def test_oracle_validation_report_preserves_oracle_errors() -> None:
    scenario = _baseline_scenario(Path("synthetic_model.xlsx"), Path("generated_model.py"))
    oracle_result = OracleResult(
        backend="formulas",
        source_workbook="synthetic_model.xlsx",
        diagnostics=(
            OracleDiagnostic(
                diagnostic_code="oracle_calculation_failed",
                message="calculation failed",
                severity="error",
                location="synthetic_model.xlsx",
            ),
        ),
    )

    report = build_oracle_validation_report(
        scenario=scenario,
        generated_values={"Summary!B2": 70.2, "Summary!B3": "ok"},
        oracle_result=oracle_result,
    )

    assert report.status == "fail"
    assert report.diagnostics[0].diagnostic_code == "oracle_calculation_failed"
    assert {comparison.diagnostic_code for comparison in report.comparisons} == {"missing_oracle_output"}


def _generated_synthetic_outputs(workbook_path: Path, generated_model_path: Path) -> dict:
    workbook = extract_workbook(workbook_path)
    graph = build_dependency_graph(workbook)
    formula_cells = {cell.cell_ref: cell for cell in workbook.cells if cell.formula is not None}
    expressions = {
        cell_ref: translate_formula_cell(cell, graph)
        for cell_ref, cell in formula_cells.items()
    }
    constants = {
        cell.cell_ref: cell.raw_value
        for cell in workbook.cells
        if cell.formula is None and cell.cell_ref in {"Inputs!B2", "Inputs!B3", "Inputs!B4"}
    }
    formula_order = ("Calc!B2", "Calc!B3", "Calc!B4", "Summary!B2", "Summary!B3")
    contract = GeneratedModuleContract(
        workbook_id=workbook.workbook_id,
        module_name="synthetic_model",
        input_refs=tuple(constants),
        output_refs=("Summary!B2", "Summary!B3"),
        symbols=(
            tuple(
                GeneratedSymbol(
                    cell_ref=cell_ref,
                    symbol_name=symbol_name_for_cell_ref(cell_ref),
                    kind="input",
                )
                for cell_ref in constants
            )
            + tuple(
                GeneratedSymbol(
                    cell_ref=cell_ref,
                    symbol_name=symbol_name_for_cell_ref(cell_ref),
                    kind="output" if cell_ref.startswith("Summary!") else "intermediate",
                    raw_formula=formula_cells[cell_ref].formula.raw_formula if formula_cells[cell_ref].formula else None,
                )
                for cell_ref in formula_order
            )
        ),
    )

    result = generate_python_module(
        contract=contract,
        expressions=expressions,
        constants=constants,
        output_path=generated_model_path,
    )
    assert result.generated is True
    return _load_module(generated_model_path).calculate()


def _load_module(path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location("generated_synthetic_model_for_validation", path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _baseline_scenario(workbook_path: Path, generated_model_path: Path) -> ValidationScenario:
    return ValidationScenario(
        scenario_id="synthetic_model_baseline",
        description="Baseline validation for the controlled synthetic workbook.",
        source_workbook=str(workbook_path),
        generated_model=str(generated_model_path),
        oracle=OracleConfig(backend="formulas"),
        inputs=(),
        outputs=(
            ScenarioOutput(cell_ref="Summary!B2", kind="number", tolerance=1e-9),
            ScenarioOutput(cell_ref="Summary!B3", kind="text"),
        ),
        comparison=ComparisonRules(),
    )
