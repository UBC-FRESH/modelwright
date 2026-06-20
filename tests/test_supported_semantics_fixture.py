from pathlib import Path

from sheetforge.extraction import extract_workbook
from sheetforge.formulas import translate_formula_cell
from sheetforge.generation import GeneratedModuleContract, GeneratedSymbol, generate_python_module, symbol_name_for_cell_ref
from sheetforge.graph import build_dependency_graph
from tests.fixtures.supported_semantics.build_workbook import EXPECTED_OUTPUTS, build_workbook
from tests.test_python_generation import load_module


def test_supported_semantics_fixture_translates_and_generates(tmp_path: Path) -> None:
    workbook = extract_workbook(build_workbook(tmp_path / "supported_semantics.xlsx"))
    graph = build_dependency_graph(workbook)
    formula_cells = {cell.cell_ref: cell for cell in workbook.cells if cell.formula is not None}
    expressions = {cell_ref: translate_formula_cell(cell, graph) for cell_ref, cell in formula_cells.items()}
    constants = {
        cell.cell_ref: cell.raw_value
        for cell in workbook.cells
        if cell.formula is None and (cell.cell_ref.startswith("Inputs!B") or cell.cell_ref in {"TableData!A2", "TableData!A3"})
    }
    formula_order = tuple(f"Calc!B{index}" for index in range(1, 27)) + ("TableData!B2", "TableData!B3")
    contract = GeneratedModuleContract(
        workbook_id=workbook.workbook_id,
        module_name="supported_semantics",
        input_refs=tuple(constants),
        output_refs=formula_order,
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
                    kind="output",
                    raw_formula=formula_cells[cell_ref].formula.raw_formula,
                )
                for cell_ref in formula_order
            )
        ),
    )
    output_path = tmp_path / "generated_supported_semantics.py"

    assert {cell_ref: expression.translated for cell_ref, expression in expressions.items()} == {
        cell_ref: True for cell_ref in formula_order
    }
    result = generate_python_module(
        contract=contract,
        expressions=expressions,
        constants=constants,
        output_path=output_path,
    )
    module = load_module(output_path)

    assert result.generated is True
    assert module.calculate() == EXPECTED_OUTPUTS
