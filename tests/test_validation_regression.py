import json
from pathlib import Path

from sheetforge.validation import ComparisonResult, ValidationReport


FIXTURE_ROOT = Path(__file__).parent / "fixtures" / "synthetic_model"


def load_json_fixture(name: str) -> dict:
    return json.loads((FIXTURE_ROOT / name).read_text(encoding="utf-8"))


def build_baseline_report() -> ValidationReport:
    scenario = load_json_fixture("baseline_scenario.json")
    expected = load_json_fixture("baseline_expected_outputs.json")

    comparisons = []
    for output in scenario["outputs"]:
        cell_ref = output["cell_ref"]
        expected_output = expected["outputs"][cell_ref]
        comparisons.append(
            ComparisonResult(
                scenario_id=scenario["scenario_id"],
                cell_ref=cell_ref,
                kind=output["kind"],
                generated=expected_output["value"],
                oracle=expected_output["value"],
                matches=True,
                tolerance=output.get("tolerance"),
                difference=0.0 if output["kind"] == "number" else None,
                diagnostic_code=None,
                message="values match",
                oracle_backend=scenario["oracle"]["backend"],
            )
        )

    return ValidationReport(
        scenario_id=scenario["scenario_id"],
        oracle_backend=scenario["oracle"]["backend"],
        comparisons=tuple(comparisons),
    )


def test_synthetic_baseline_validation_report_passes(tmp_path: Path) -> None:
    report = build_baseline_report()
    payload = report.to_dict()

    report_path = tmp_path / "baseline_validation_report.json"
    report_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    assert payload["status"] == "pass"
    assert payload["mismatches"] == []
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
    assert report_path.read_text(encoding="utf-8").startswith("{\n")


def test_synthetic_numeric_mismatch_report_fails(tmp_path: Path) -> None:
    scenario = load_json_fixture("baseline_scenario.json")
    expected = load_json_fixture("baseline_expected_outputs.json")
    expected_number = expected["outputs"]["Summary!B2"]["value"]
    generated_number = 70.1
    difference = abs(generated_number - expected_number)

    mismatch = ComparisonResult(
        scenario_id="synthetic_model_numeric_mismatch",
        cell_ref="Summary!B2",
        kind="number",
        generated=generated_number,
        oracle=expected_number,
        matches=False,
        tolerance=expected["outputs"]["Summary!B2"]["tolerance"],
        difference=difference,
        diagnostic_code="numeric_mismatch",
        message="generated value differs from oracle value",
        oracle_backend=scenario["oracle"]["backend"],
    )
    report = ValidationReport(
        scenario_id="synthetic_model_numeric_mismatch",
        oracle_backend=scenario["oracle"]["backend"],
        comparisons=(mismatch,),
    )
    payload = report.to_dict()

    report_path = tmp_path / "numeric_mismatch_report.json"
    report_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    assert payload["status"] == "fail"
    assert payload["mismatches"] == [mismatch.to_dict()]
    assert payload["mismatches"][0]["diagnostic_code"] == "numeric_mismatch"
    assert payload["mismatches"][0]["generated"] == 70.1
    assert payload["mismatches"][0]["oracle"] == 70.2
    assert payload["mismatches"][0]["tolerance"] == 1e-9
    assert payload["mismatches"][0]["difference"] == difference
    assert report_path.exists()
