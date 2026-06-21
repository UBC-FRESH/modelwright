import json

from modelwright.validation import MISSING_VALUE, ScenarioOutput, compare_scalar_output


def test_compare_number_uses_absolute_tolerance() -> None:
    result = compare_scalar_output(
        scenario_id="synthetic_model_baseline",
        output=ScenarioOutput(cell_ref="Summary!B2", kind="number", tolerance=1e-9),
        generated=70.2,
        oracle=70.2,
        oracle_backend="formulas",
    )

    assert result.matches is True
    assert result.diagnostic_code is None
    assert result.difference == 0.0
    assert result.to_dict()["tolerance"] == 1e-9
    json.dumps(result.to_dict())


def test_compare_number_reports_mismatch() -> None:
    result = compare_scalar_output(
        scenario_id="synthetic_model_numeric_mismatch",
        output=ScenarioOutput(cell_ref="Summary!B2", kind="number", tolerance=1e-9),
        generated=70.1,
        oracle=70.2,
        oracle_backend="formulas",
    )

    assert result.matches is False
    assert result.diagnostic_code == "numeric_mismatch"
    assert result.difference == abs(70.1 - 70.2)
    assert result.message == "generated value differs from oracle value"
    json.dumps(result.to_dict())


def test_compare_text_requires_exact_match() -> None:
    match = compare_scalar_output(
        scenario_id="synthetic_model_baseline",
        output=ScenarioOutput(cell_ref="Summary!B3", kind="text"),
        generated="ok",
        oracle="ok",
        oracle_backend="formulas",
    )
    mismatch = compare_scalar_output(
        scenario_id="synthetic_model_text_mismatch",
        output=ScenarioOutput(cell_ref="Summary!B3", kind="text"),
        generated="OK",
        oracle="ok",
        oracle_backend="formulas",
    )

    assert match.matches is True
    assert match.diagnostic_code is None
    assert mismatch.matches is False
    assert mismatch.diagnostic_code == "text_mismatch"
    json.dumps(mismatch.to_dict())


def test_compare_missing_outputs() -> None:
    output = ScenarioOutput(cell_ref="Summary!B2", kind="number", tolerance=1e-9)

    missing_generated = compare_scalar_output(
        scenario_id="missing_generated",
        output=output,
        generated=MISSING_VALUE,
        oracle=70.2,
        oracle_backend="formulas",
    )
    missing_oracle = compare_scalar_output(
        scenario_id="missing_oracle",
        output=output,
        generated=70.2,
        oracle=MISSING_VALUE,
        oracle_backend="formulas",
    )
    missing_both = compare_scalar_output(
        scenario_id="missing_both",
        output=output,
        generated=MISSING_VALUE,
        oracle=MISSING_VALUE,
        oracle_backend="formulas",
    )

    assert missing_generated.diagnostic_code == "missing_generated_output"
    assert missing_generated.to_dict()["generated"] is None
    assert missing_oracle.diagnostic_code == "missing_oracle_output"
    assert missing_oracle.to_dict()["oracle"] is None
    assert missing_both.diagnostic_code == "missing_generated_and_oracle_output"
    json.dumps(missing_both.to_dict())
