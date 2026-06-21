import json
from pathlib import Path

from modelwright.execution import GeneratedExecutionResult, execute_generated_model
from modelwright.extraction import extract_workbook
from modelwright.formulas import translate_formula_cell
from modelwright.generation import (
    GeneratedModuleContract,
    GeneratedSymbol,
    generate_python_module,
    symbol_name_for_cell_ref,
)
from modelwright.graph import build_dependency_graph
from tests.fixtures.synthetic_model.build_workbook import build_workbook


def synthetic_generated_model(tmp_path: Path) -> tuple[GeneratedModuleContract, Path]:
    workbook = extract_workbook(build_workbook(tmp_path / "synthetic_model.xlsx"))
    graph = build_dependency_graph(workbook)
    formula_cells = {cell.cell_ref: cell for cell in workbook.cells if cell.formula is not None}
    expressions = {cell_ref: translate_formula_cell(cell, graph) for cell_ref, cell in formula_cells.items()}
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
    output_path = tmp_path / "generated_model.py"
    generation_result = generate_python_module(
        contract=contract,
        expressions=expressions,
        constants=constants,
        output_path=output_path,
    )
    assert generation_result.generated is True
    return contract, output_path


def test_execute_generated_model_returns_declared_outputs(tmp_path: Path) -> None:
    contract, model_path = synthetic_generated_model(tmp_path)

    result = execute_generated_model(contract=contract, module_path=model_path)

    assert result.executed is True
    assert result.diagnostics == ()
    assert result.output_values == {"Summary!B2": 70.2, "Summary!B3": "ok"}


def test_execute_generated_model_passes_input_overrides(tmp_path: Path) -> None:
    contract, model_path = synthetic_generated_model(tmp_path)

    result = execute_generated_model(
        contract=contract,
        module_path=model_path,
        inputs={"Inputs!B2": 10},
    )

    assert result.executed is True
    assert result.output_values == {"Summary!B2": 7.02, "Summary!B3": "low"}


def test_execute_generated_model_payload_round_trips(tmp_path: Path) -> None:
    contract, model_path = synthetic_generated_model(tmp_path)

    result = execute_generated_model(contract=contract, module_path=model_path)
    payload = result.to_dict()

    assert json.loads(json.dumps(payload)) == payload
    assert GeneratedExecutionResult.from_dict(payload) == result


def test_execute_generated_model_reports_missing_file(tmp_path: Path) -> None:
    contract, _model_path = synthetic_generated_model(tmp_path)

    result = execute_generated_model(contract=contract, module_path=tmp_path / "missing.py")

    assert result.executed is False
    assert result.diagnostics[0].code == "generated_model_not_found"
    assert result.diagnostics[0].severity == "error"


def test_execute_generated_model_reports_missing_declared_output(tmp_path: Path) -> None:
    contract = GeneratedModuleContract(
        workbook_id="missing-output.xlsx",
        module_name="missing_output",
        output_refs=("Calc!A1", "Calc!A2"),
        symbols=(),
    )
    model_path = tmp_path / "missing_output.py"
    model_path.write_text(
        "def calculate(inputs=None):\n"
        "    return {'Calc!A1': 1}\n",
        encoding="utf-8",
    )

    result = execute_generated_model(contract=contract, module_path=model_path)

    assert result.executed is True
    assert result.output_values == {"Calc!A1": 1}
    assert result.diagnostics[0].code == "missing_generated_output"
    assert result.diagnostics[0].location == "Calc!A2"
