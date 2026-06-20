import json

from sheetforge.references import WorkbookReference, normalize_cell_reference, normalize_reference


def test_normalize_sheet_relative_cell_reference() -> None:
    reference = normalize_reference("B2", current_sheet="Calc")

    assert reference == WorkbookReference(
        kind="cell",
        original="B2",
        normalized="Calc!B2",
        sheet="Calc",
        start_cell="B2",
        end_cell="B2",
    )
    json.dumps(reference.to_dict())


def test_normalize_absolute_and_quoted_sheet_references() -> None:
    reference = normalize_reference("'Input Data'!$B$2")

    assert reference.kind == "cell"
    assert reference.original == "'Input Data'!$B$2"
    assert reference.normalized == "Input Data!B2"
    assert reference.sheet == "Input Data"
    assert reference.start_cell == "B2"


def test_normalize_range_reference() -> None:
    reference = normalize_reference("Calc!$B$2:$B$4")

    assert reference.kind == "range"
    assert reference.normalized == "Calc!B2:B4"
    assert reference.sheet == "Calc"
    assert reference.start_cell == "B2"
    assert reference.end_cell == "B4"


def test_normalize_named_range_reference() -> None:
    reference = normalize_reference("BaseVolume", current_sheet="Calc")

    assert reference.kind == "named_range"
    assert reference.original == "BaseVolume"
    assert reference.normalized == "BaseVolume"
    assert reference.name == "BaseVolume"
    assert reference.sheet is None


def test_normalize_external_reference() -> None:
    reference = normalize_reference("[other.xlsx]Inputs!A1", current_sheet="Calc")

    assert reference.kind == "external"
    assert reference.original == "[other.xlsx]Inputs!A1"
    assert reference.normalized == "[other.xlsx]Inputs!A1"
    assert reference.workbook == "other.xlsx"
    assert reference.diagnostic_code == "external_reference"


def test_normalize_indexed_external_reference() -> None:
    reference = normalize_reference("[0]Inputs!A1", current_sheet="Calc")

    assert reference.kind == "external"
    assert reference.original == "[0]Inputs!A1"
    assert reference.normalized == "[0]Inputs!A1"
    assert reference.workbook == "0"
    assert reference.diagnostic_code == "external_reference"


def test_normalize_structured_reference() -> None:
    reference = normalize_reference("Table1[Amount]", current_sheet="Calc")

    assert reference.kind == "structured"
    assert reference.original == "Table1[Amount]"
    assert reference.normalized == "Table1[Amount]"
    assert reference.diagnostic_code == "unsupported_structured_reference"


def test_normalize_unresolved_reference() -> None:
    reference = normalize_reference("1:2:3", current_sheet="Calc")

    assert reference.kind == "unresolved"
    assert reference.original == "1:2:3"
    assert reference.diagnostic_code == "unresolved_reference"


def test_normalize_cell_reference_rejects_non_cell() -> None:
    reference = normalize_cell_reference("B2:B4", current_sheet="Calc")

    assert reference.kind == "unresolved"
    assert reference.diagnostic_code == "not_a_cell_reference"


def test_workbook_reference_round_trips_from_dict() -> None:
    reference = normalize_reference("Summary!B3")
    payload = reference.to_dict()

    assert WorkbookReference.from_dict(payload) == reference
