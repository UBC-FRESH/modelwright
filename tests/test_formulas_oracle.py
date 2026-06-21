from pathlib import Path

from modelwright.formulas_oracle import FormulasWorkbookOracle
from modelwright.oracles import OracleRequest
from modelwright.validation import ScenarioInput, ScenarioOutput
from tests.fixtures.synthetic_model.build_workbook import build_workbook


def test_formulas_oracle_evaluates_synthetic_workbook_outputs(tmp_path: Path) -> None:
    workbook_path = build_workbook(tmp_path / "synthetic_model.xlsx")
    request = OracleRequest(
        source_workbook=str(workbook_path),
        outputs=(
            ScenarioOutput(cell_ref="Summary!B2", kind="number", tolerance=1e-9),
            ScenarioOutput(cell_ref="Summary!B3", kind="text"),
        ),
    )

    result = FormulasWorkbookOracle().evaluate(request)

    assert result.success is True
    assert result.backend == "formulas"
    assert result.outputs == {"Summary!B2": 70.2, "Summary!B3": "ok"}
    assert result.diagnostics == ()


def test_formulas_oracle_reports_missing_output(tmp_path: Path) -> None:
    workbook_path = build_workbook(tmp_path / "synthetic_model.xlsx")
    request = OracleRequest(
        source_workbook=str(workbook_path),
        outputs=(ScenarioOutput(cell_ref="Summary!Z99", kind="number"),),
    )

    result = FormulasWorkbookOracle().evaluate(request)

    assert result.success is False
    assert result.outputs == {}
    assert result.diagnostics[0].diagnostic_code == "missing_oracle_output"
    assert result.diagnostics[0].location == "Summary!Z99"


def test_formulas_oracle_fails_closed_on_input_overrides(tmp_path: Path) -> None:
    workbook_path = build_workbook(tmp_path / "synthetic_model.xlsx")
    request = OracleRequest(
        source_workbook=str(workbook_path),
        inputs=(ScenarioInput(cell_ref="Inputs!B2", value=10, kind="number"),),
        outputs=(ScenarioOutput(cell_ref="Summary!B2", kind="number"),),
    )

    result = FormulasWorkbookOracle().evaluate(request)

    assert result.success is False
    assert result.outputs == {}
    assert result.diagnostics[0].diagnostic_code == "unsupported_oracle_inputs"
