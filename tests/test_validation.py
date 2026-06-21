import json

from modelwright.validation import ComparisonResult, Diagnostic, ValidationReport


def test_validation_report_serializes_passing_comparisons() -> None:
    comparison = ComparisonResult(
        scenario_id="synthetic_model_baseline",
        cell_ref="Summary!B2",
        kind="number",
        generated=70.2,
        oracle=70.2,
        matches=True,
        tolerance=1e-9,
        difference=0.0,
        diagnostic_code=None,
        message="values match",
        oracle_backend="formulas",
    )

    report = ValidationReport(
        scenario_id="synthetic_model_baseline",
        oracle_backend="formulas",
        comparisons=(comparison,),
    )

    payload = report.to_dict()

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
        }
    ]
    json.dumps(payload)


def test_validation_report_serializes_mismatch_details() -> None:
    comparison = ComparisonResult(
        scenario_id="synthetic_model_numeric_mismatch",
        cell_ref="Summary!B2",
        kind="number",
        generated=70.1,
        oracle=70.2,
        matches=False,
        tolerance=1e-9,
        difference=0.1,
        diagnostic_code="numeric_mismatch",
        message="generated value differs from oracle value",
        oracle_backend="formulas",
    )

    report = ValidationReport(
        scenario_id="synthetic_model_numeric_mismatch",
        oracle_backend="formulas",
        comparisons=(comparison,),
    )

    payload = report.to_dict()

    assert payload["status"] == "fail"
    assert payload["mismatches"] == [comparison.to_dict()]
    assert payload["mismatches"][0]["diagnostic_code"] == "numeric_mismatch"
    assert payload["mismatches"][0]["cell_ref"] == "Summary!B2"
    json.dumps(payload)


def test_error_diagnostic_fails_report_without_comparisons() -> None:
    report = ValidationReport(
        scenario_id="invalid_scenario",
        oracle_backend="formulas",
        diagnostics=(
            Diagnostic(
                diagnostic_code="invalid_scenario",
                message="scenario could not be parsed",
                severity="error",
                location="scenario.json",
            ),
        ),
    )

    payload = report.to_dict()

    assert payload["status"] == "fail"
    assert payload["diagnostics"] == [
        {
            "diagnostic_code": "invalid_scenario",
            "message": "scenario could not be parsed",
            "severity": "error",
            "location": "scenario.json",
        }
    ]
    json.dumps(payload)
