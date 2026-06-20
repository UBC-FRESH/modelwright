import json
from pathlib import Path

from openpyxl import Workbook

from sheetforge.extraction import extract_workbook
from tests.fixtures.synthetic_model.build_workbook import build_workbook


def test_extract_workbook_reads_synthetic_fixture(tmp_path: Path) -> None:
    workbook_path = build_workbook(tmp_path / "synthetic_model.xlsx")

    workbook = extract_workbook(workbook_path)

    assert workbook.workbook_id == "synthetic_model.xlsx"
    assert workbook.source_path == str(workbook_path)
    assert [sheet.sheet_id for sheet in workbook.sheets] == ["Inputs", "Calc", "Summary"]
    assert [sheet.state for sheet in workbook.sheets] == ["visible", "visible", "visible"]
    assert len(workbook.cells) == 22
    assert workbook.diagnostics == ()

    named_ranges = {named_range.name: named_range for named_range in workbook.named_ranges}
    assert sorted(named_ranges) == ["BaseVolume", "GrowthRate"]
    assert named_ranges["BaseVolume"].scope == "workbook"
    assert named_ranges["BaseVolume"].raw_definition == "'Inputs'!$B$2"
    assert named_ranges["BaseVolume"].destinations == ("Inputs!B2",)
    assert named_ranges["BaseVolume"].status == "resolved"

    cells = {cell.cell_ref: cell for cell in workbook.cells}
    assert cells["Inputs!B2"].kind == "value"
    assert cells["Inputs!B2"].raw_value == 100
    assert cells["Inputs!B2"].data_type == "n"
    assert cells["Inputs!B2"].formula is None
    assert cells["Calc!B2"].kind == "formula"
    assert cells["Calc!B2"].raw_value == "=BaseVolume*(1+GrowthRate)"
    assert cells["Calc!B2"].formula is not None
    assert cells["Calc!B2"].formula.raw_references == ("BaseVolume", "GrowthRate")
    assert cells["Calc!B2"].formula.functions == ()
    assert cells["Calc!B4"].formula is not None
    assert cells["Calc!B4"].formula.functions == ("ROUND",)
    assert cells["Summary!B3"].formula is not None
    assert cells["Summary!B3"].formula.functions == ("IF",)


def test_extract_workbook_emits_missing_cached_formula_diagnostics(tmp_path: Path) -> None:
    workbook_path = build_workbook(tmp_path / "synthetic_model.xlsx")

    workbook = extract_workbook(workbook_path)
    formula_cells = [cell for cell in workbook.cells if cell.kind == "formula"]
    diagnostics = [
        diagnostic
        for cell in formula_cells
        if cell.formula is not None
        for diagnostic in cell.formula.diagnostics
    ]

    assert [cell.cell_ref for cell in formula_cells] == [
        "Calc!B2",
        "Calc!B3",
        "Calc!B4",
        "Summary!B2",
        "Summary!B3",
    ]
    assert len(diagnostics) == 5
    assert {diagnostic.code for diagnostic in diagnostics} == {"missing_cached_formula_value"}
    assert diagnostics[0].severity == "warning"


def test_extract_workbook_payload_round_trips(tmp_path: Path) -> None:
    workbook_path = build_workbook(tmp_path / "synthetic_model.xlsx")

    workbook = extract_workbook(workbook_path)
    payload = workbook.to_dict()

    assert json.loads(json.dumps(payload)) == payload
    assert type(workbook).from_dict(payload) == workbook


def test_extract_workbook_reports_volatile_formula(tmp_path: Path) -> None:
    workbook_path = tmp_path / "volatile.xlsx"
    source = Workbook()
    sheet = source.active
    sheet.title = "Inputs"
    sheet["A1"] = "=NOW()"
    source.save(workbook_path)

    workbook = extract_workbook(workbook_path)
    cell = workbook.cells[0]

    assert cell.cell_ref == "Inputs!A1"
    assert cell.formula is not None
    assert {diagnostic.code for diagnostic in cell.formula.diagnostics} == {
        "missing_cached_formula_value",
        "unsupported_volatile_function",
    }
