from pathlib import Path

from sheetforge.extraction import CellRecord, extract_workbook
from sheetforge.formulas import translate_formula_cell
from sheetforge.graph import build_dependency_graph
from tests.fixtures.synthetic_model.build_workbook import build_workbook


def synthetic_formula_cells(tmp_path: Path) -> tuple[dict[str, CellRecord], object]:
    workbook = extract_workbook(build_workbook(tmp_path / "synthetic_model.xlsx"))
    graph = build_dependency_graph(workbook)
    return {cell.cell_ref: cell for cell in workbook.cells if cell.formula is not None}, graph


def test_translate_named_range_arithmetic_formula(tmp_path: Path) -> None:
    cells, graph = synthetic_formula_cells(tmp_path)

    expression = translate_formula_cell(cells["Calc!B2"], graph)

    assert expression.translated is True
    assert expression.root is not None
    assert expression.root.kind == "binary"
    assert expression.root.operator == "*"
    assert expression.root.operands[0].reference is not None
    assert expression.root.operands[0].reference.normalized == "Inputs!B2"
    assert expression.root.operands[1].kind == "binary"
    assert expression.root.operands[1].operator == "+"
    assert expression.root.operands[1].operands[0].value == 1
    assert expression.root.operands[1].operands[1].reference is not None
    assert expression.root.operands[1].operands[1].reference.normalized == "Inputs!B3"


def test_translate_sheet_relative_arithmetic_formula(tmp_path: Path) -> None:
    cells, graph = synthetic_formula_cells(tmp_path)

    expression = translate_formula_cell(cells["Calc!B3"], graph)

    assert expression.root is not None
    assert expression.root.operator == "*"
    assert expression.root.operands[0].reference is not None
    assert expression.root.operands[0].reference.normalized == "Calc!B2"
    assert expression.root.operands[1].reference is not None
    assert expression.root.operands[1].reference.normalized == "Inputs!B4"


def test_translate_round_formula(tmp_path: Path) -> None:
    cells, graph = synthetic_formula_cells(tmp_path)

    expression = translate_formula_cell(cells["Calc!B4"], graph)

    assert expression.root is not None
    assert expression.root.kind == "function_call"
    assert expression.root.function_name == "ROUND"
    assert expression.root.operands[0].reference is not None
    assert expression.root.operands[0].reference.normalized == "Calc!B3"
    assert expression.root.operands[1].value == 2


def test_translate_direct_reference_formula(tmp_path: Path) -> None:
    cells, graph = synthetic_formula_cells(tmp_path)

    expression = translate_formula_cell(cells["Summary!B2"], graph)

    assert expression.root is not None
    assert expression.root.kind == "reference"
    assert expression.root.reference is not None
    assert expression.root.reference.normalized == "Calc!B4"


def test_translate_if_formula(tmp_path: Path) -> None:
    cells, graph = synthetic_formula_cells(tmp_path)

    expression = translate_formula_cell(cells["Summary!B3"], graph)

    assert expression.root is not None
    assert expression.root.kind == "function_call"
    assert expression.root.function_name == "IF"
    assert expression.root.operands[0].kind == "comparison"
    assert expression.root.operands[0].operator == ">"
    assert expression.root.operands[0].operands[0].reference is not None
    assert expression.root.operands[0].operands[0].reference.normalized == "Summary!B2"
    assert expression.root.operands[0].operands[1].value == 50
    assert expression.root.operands[1].value == "ok"
    assert expression.root.operands[2].value == "low"
