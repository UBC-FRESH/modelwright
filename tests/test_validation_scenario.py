import json
from pathlib import Path

from modelwright.validation import (
    ComparisonRules,
    OracleConfig,
    ScenarioOutput,
    ValidationScenario,
    load_validation_scenario,
)


FIXTURE_ROOT = Path(__file__).parent / "fixtures" / "synthetic_model"


def test_load_validation_scenario_from_fixture() -> None:
    scenario = load_validation_scenario(FIXTURE_ROOT / "baseline_scenario.json")

    assert scenario == ValidationScenario(
        scenario_id="synthetic_model_baseline",
        description="Baseline validation for the controlled synthetic workbook.",
        source_workbook="synthetic_model.xlsx",
        generated_model="generated_model.py",
        oracle=OracleConfig(backend="formulas"),
        inputs=(),
        outputs=(
            ScenarioOutput(cell_ref="Summary!B2", kind="number", tolerance=1e-9),
            ScenarioOutput(cell_ref="Summary!B3", kind="text"),
        ),
        comparison=ComparisonRules(
            default_numeric_tolerance=1e-9,
            text="exact",
            boolean="exact",
        ),
    )


def test_validation_scenario_round_trips_to_json_boundary() -> None:
    fixture_path = FIXTURE_ROOT / "baseline_scenario.json"
    scenario = load_validation_scenario(fixture_path)
    payload = scenario.to_dict()

    assert payload == json.loads(fixture_path.read_text(encoding="utf-8"))
    json.dumps(payload)


def test_validation_scenario_preserves_input_overrides() -> None:
    scenario = ValidationScenario.from_dict(
        {
            "scenario_id": "input_override_case",
            "description": "Input override example.",
            "source_workbook": "synthetic_model.xlsx",
            "generated_model": "generated_model.py",
            "oracle": {"backend": "formulas", "mode": "local"},
            "inputs": [
                {
                    "cell_ref": "Inputs!B2",
                    "value": 120,
                    "kind": "number",
                    "source": "scenario fixture",
                }
            ],
            "outputs": [{"cell_ref": "Summary!B2", "kind": "number"}],
            "comparison": {},
        }
    )

    assert scenario.oracle.to_dict() == {"backend": "formulas", "mode": "local"}
    assert scenario.inputs[0].to_dict() == {
        "cell_ref": "Inputs!B2",
        "value": 120,
        "kind": "number",
        "source": "scenario fixture",
    }
    assert scenario.comparison == ComparisonRules()
