import json

from sheetforge.extraction import (
    CellRecord,
    ExtractionDiagnostic,
    FormulaRecord,
    NamedRangeRecord,
    SheetRecord,
    WorkbookRecord,
)


def test_workbook_record_serializes_extracted_facts() -> None:
    diagnostic = ExtractionDiagnostic(
        code="missing_cached_formula_value",
        message="formula cell has no cached value",
        severity="warning",
        location="Calc!B2",
        raw_value="=BaseVolume*GrowthRate",
    )
    formula = FormulaRecord(
        raw_formula="=BaseVolume*GrowthRate",
        tokens=("BaseVolume", "*", "GrowthRate"),
        raw_references=("BaseVolume", "GrowthRate"),
        normalized_references=("Inputs!B2", "Inputs!B3"),
        functions=(),
        diagnostics=(diagnostic,),
    )
    workbook = WorkbookRecord(
        workbook_id="synthetic_model.xlsx",
        source_path="tmp/synthetic_model.xlsx",
        sheets=(
            SheetRecord(sheet_id="Inputs", title="Inputs", state="visible", index=0),
            SheetRecord(sheet_id="Calc", title="Calc", state="visible", index=1),
        ),
        cells=(
            CellRecord(
                cell_ref="Calc!B2",
                kind="formula",
                raw_value="=BaseVolume*GrowthRate",
                data_type="f",
                cached_value=None,
                formula=formula,
            ),
        ),
        named_ranges=(
            NamedRangeRecord(
                name="BaseVolume",
                scope="workbook",
                raw_definition="'Inputs'!$B$2",
                destinations=("Inputs!B2",),
                status="resolved",
            ),
        ),
        diagnostics=(),
    )

    payload = workbook.to_dict()

    assert payload == {
        "workbook_id": "synthetic_model.xlsx",
        "source_path": "tmp/synthetic_model.xlsx",
        "sheets": [
            {"sheet_id": "Inputs", "title": "Inputs", "state": "visible", "index": 0},
            {"sheet_id": "Calc", "title": "Calc", "state": "visible", "index": 1},
        ],
        "cells": [
            {
                "cell_ref": "Calc!B2",
                "kind": "formula",
                "raw_value": "=BaseVolume*GrowthRate",
                "data_type": "f",
                "cached_value": None,
                "formula": {
                    "raw_formula": "=BaseVolume*GrowthRate",
                    "tokens": ["BaseVolume", "*", "GrowthRate"],
                    "raw_references": ["BaseVolume", "GrowthRate"],
                    "normalized_references": ["Inputs!B2", "Inputs!B3"],
                    "functions": [],
                    "diagnostics": [
                        {
                            "code": "missing_cached_formula_value",
                            "message": "formula cell has no cached value",
                            "severity": "warning",
                            "location": "Calc!B2",
                            "raw_value": "=BaseVolume*GrowthRate",
                        }
                    ],
                },
            }
        ],
        "named_ranges": [
            {
                "name": "BaseVolume",
                "scope": "workbook",
                "raw_definition": "'Inputs'!$B$2",
                "destinations": ["Inputs!B2"],
                "status": "resolved",
                "diagnostics": [],
            }
        ],
        "diagnostics": [],
    }
    json.dumps(payload)


def test_workbook_record_round_trips_from_dict() -> None:
    payload = {
        "workbook_id": "synthetic_model.xlsx",
        "source_path": "tmp/synthetic_model.xlsx",
        "sheets": [{"sheet_id": "Summary", "title": "Summary", "state": "visible", "index": 2}],
        "cells": [
            {
                "cell_ref": "Summary!B3",
                "kind": "formula",
                "raw_value": '=IF(Summary!B2>50,"ok","review")',
                "data_type": "f",
                "cached_value": None,
                "formula": {
                    "raw_formula": '=IF(Summary!B2>50,"ok","review")',
                    "tokens": ["IF", "Summary!B2", ">", "50"],
                    "raw_references": ["Summary!B2"],
                    "normalized_references": ["Summary!B2"],
                    "functions": ["IF"],
                    "diagnostics": [],
                },
            }
        ],
        "named_ranges": [],
        "diagnostics": [
            {
                "code": "unsupported_array_formula",
                "message": "array formulas are not supported yet",
                "severity": "warning",
                "location": "Summary!B3",
                "raw_value": None,
            }
        ],
    }

    workbook = WorkbookRecord.from_dict(payload)

    assert workbook.workbook_id == "synthetic_model.xlsx"
    assert workbook.sheets[0].sheet_id == "Summary"
    assert workbook.cells[0].formula is not None
    assert workbook.cells[0].formula.functions == ("IF",)
    assert workbook.diagnostics[0].code == "unsupported_array_formula"
    assert workbook.to_dict() == payload
