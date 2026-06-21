import json
import tomllib
from pathlib import Path

from modelwright.oracles import (
    OracleRequest,
    OracleResult,
    missing_optional_dependency_diagnostic,
)
from modelwright.validation import ScenarioInput, ScenarioOutput


class StaticOracle:
    backend_name = "static"

    def evaluate(self, request: OracleRequest) -> OracleResult:
        return OracleResult(
            backend=self.backend_name,
            source_workbook=request.source_workbook,
            outputs={output.cell_ref: 70.2 for output in request.outputs},
        )


def test_oracle_request_round_trips_to_json_boundary() -> None:
    request = OracleRequest(
        source_workbook="tmp/source.xlsx",
        inputs=(
            ScenarioInput(
                cell_ref="Inputs!B2",
                value=54,
                kind="number",
                source="scenario",
            ),
        ),
        outputs=(
            ScenarioOutput(
                cell_ref="Summary!B2",
                kind="number",
                tolerance=1e-9,
            ),
        ),
        options={"calculation_mode": "default"},
    )

    payload = request.to_dict()
    restored = OracleRequest.from_dict(json.loads(json.dumps(payload)))

    assert restored == request
    assert payload == {
        "source_workbook": "tmp/source.xlsx",
        "outputs": [
            {
                "cell_ref": "Summary!B2",
                "kind": "number",
                "tolerance": 1e-09,
            }
        ],
        "inputs": [
            {
                "cell_ref": "Inputs!B2",
                "value": 54,
                "kind": "number",
                "source": "scenario",
            }
        ],
        "options": {"calculation_mode": "default"},
    }


def test_oracle_result_reports_success_and_diagnostics() -> None:
    diagnostic = missing_optional_dependency_diagnostic(
        dependency="formulas",
        extra="oracle",
        backend="formulas",
    )
    result = OracleResult(
        backend="formulas",
        source_workbook="tmp/source.xlsx",
        diagnostics=(diagnostic,),
    )

    payload = result.to_dict()
    restored = OracleResult.from_dict(json.loads(json.dumps(payload)))

    assert result.success is False
    assert restored == result
    assert payload["success"] is False
    assert payload["diagnostics"] == [
        {
            "diagnostic_code": "missing_optional_dependency",
            "message": "Install modelwright[oracle] to use the formulas oracle backend.",
            "severity": "error",
            "raw_value": "formulas",
        }
    ]


def test_workbook_oracle_protocol_shape_returns_outputs() -> None:
    request = OracleRequest(
        source_workbook="tmp/source.xlsx",
        outputs=(ScenarioOutput(cell_ref="Summary!B2", kind="number"),),
    )
    result = StaticOracle().evaluate(request)

    assert result.success is True
    assert result.backend == "static"
    assert result.outputs == {"Summary!B2": 70.2}


def test_oracle_optional_dependency_group_stays_formula_only() -> None:
    pyproject = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))

    optional_dependencies = pyproject["project"]["optional-dependencies"]

    assert optional_dependencies["oracle"] == ["formulas"]
    assert "xlwings" not in optional_dependencies["oracle"]
