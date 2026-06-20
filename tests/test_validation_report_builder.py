import json
from pathlib import Path

from sheetforge.validation import build_validation_report, load_validation_scenario


FIXTURE_ROOT = Path(__file__).parent / "fixtures" / "synthetic_model"


def load_expected_values() -> dict[str, object]:
    payload = json.loads((FIXTURE_ROOT / "baseline_expected_outputs.json").read_text(encoding="utf-8"))
    return {cell_ref: output["value"] for cell_ref, output in payload["outputs"].items()}


def test_build_validation_report_passes_for_baseline_values() -> None:
    scenario = load_validation_scenario(FIXTURE_ROOT / "baseline_scenario.json")
    expected_values = load_expected_values()

    report = build_validation_report(
        scenario=scenario,
        generated_values=expected_values,
        oracle_values=expected_values,
    )
    payload = report.to_dict()

    assert report.status == "pass"
    assert report.mismatches == ()
    assert payload["comparisons"] == [
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
    json.dumps(payload)


def test_build_validation_report_fails_for_observed_mismatch() -> None:
    scenario = load_validation_scenario(FIXTURE_ROOT / "baseline_scenario.json")
    oracle_values = load_expected_values()
    generated_values = {**oracle_values, "Summary!B2": 70.1}

    report = build_validation_report(
        scenario=scenario,
        generated_values=generated_values,
        oracle_values=oracle_values,
    )

    assert report.status == "fail"
    assert len(report.mismatches) == 1
    mismatch = report.mismatches[0]
    assert mismatch.cell_ref == "Summary!B2"
    assert mismatch.diagnostic_code == "numeric_mismatch"
    assert mismatch.generated == 70.1
    assert mismatch.oracle == 70.2


def test_build_validation_report_marks_missing_observed_values() -> None:
    scenario = load_validation_scenario(FIXTURE_ROOT / "baseline_scenario.json")
    oracle_values = load_expected_values()

    report = build_validation_report(
        scenario=scenario,
        generated_values={"Summary!B3": "ok"},
        oracle_values=oracle_values,
    )

    assert report.status == "fail"
    assert len(report.mismatches) == 1
    mismatch = report.mismatches[0]
    assert mismatch.cell_ref == "Summary!B2"
    assert mismatch.diagnostic_code == "missing_generated_output"
    assert mismatch.generated is None
    assert mismatch.oracle == 70.2
