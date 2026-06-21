import json
from pathlib import Path

from modelwright.evaluation import ValidationEvaluationResult, evaluate_generated_model
from modelwright.extraction import CellRecord, WorkbookRecord
from modelwright.generation import GeneratedModuleContract
from modelwright.oracles import OracleDiagnostic, OracleResult
from modelwright.validation import (
    ComparisonRules,
    OracleConfig,
    ScenarioOutput,
    ValidationScenario,
)


def write_generated_model(path: Path, outputs: dict[str, object]) -> Path:
    path.write_text(
        "def calculate(inputs=None):\n"
        f"    return {outputs!r}\n",
        encoding="utf-8",
    )
    return path


def scenario(generated_model_path: Path) -> ValidationScenario:
    return ValidationScenario(
        scenario_id="scenario",
        description="scenario",
        source_workbook="source.xlsx",
        generated_model=str(generated_model_path),
        oracle=OracleConfig(backend="formulas"),
        inputs=(),
        outputs=(
            ScenarioOutput(cell_ref="Calc!A1", kind="number", tolerance=1e-9),
            ScenarioOutput(cell_ref="Calc!A2", kind="text"),
        ),
        comparison=ComparisonRules(),
    )


def contract() -> GeneratedModuleContract:
    return GeneratedModuleContract(
        workbook_id="source.xlsx",
        module_name="generated",
        output_refs=("Calc!A1", "Calc!A2"),
        symbols=(),
    )


def workbook_with_cached_values(*, include_second_cache: bool = True) -> WorkbookRecord:
    return WorkbookRecord(
        workbook_id="source.xlsx",
        source_path="source.xlsx",
        cells=(
            CellRecord(cell_ref="Calc!A1", kind="formula", raw_value="=1+1", cached_value=2),
            CellRecord(
                cell_ref="Calc!A2",
                kind="formula",
                raw_value='="ok"',
                cached_value="ok" if include_second_cache else None,
            ),
        ),
    )


def test_evaluate_generated_model_builds_cached_validation_report(tmp_path: Path) -> None:
    model_path = write_generated_model(tmp_path / "generated.py", {"Calc!A1": 2, "Calc!A2": "ok"})

    result = evaluate_generated_model(
        contract=contract(),
        module_path=model_path,
        scenario=scenario(model_path),
        workbook=workbook_with_cached_values(),
    )

    assert result.generated_execution.executed is True
    assert result.cached_validation_report is not None
    assert result.cached_validation_report.status == "pass"
    assert result.cached_validation_report.oracle_backend == "cached_workbook"
    assert result.oracle_validation_report is None
    assert result.diagnostics == ()


def test_evaluate_generated_model_preserves_missing_cached_values(tmp_path: Path) -> None:
    model_path = write_generated_model(tmp_path / "generated.py", {"Calc!A1": 2, "Calc!A2": "ok"})

    result = evaluate_generated_model(
        contract=contract(),
        module_path=model_path,
        scenario=scenario(model_path),
        workbook=workbook_with_cached_values(include_second_cache=False),
    )

    assert result.cached_validation_report is not None
    assert result.cached_validation_report.status == "fail"
    assert result.cached_validation_report.diagnostics[0].diagnostic_code == "missing_cached_formula_value"
    assert result.cached_validation_report.mismatches[0].diagnostic_code == "missing_oracle_output"
    assert result.cached_validation_report.mismatches[0].cell_ref == "Calc!A2"


def test_evaluate_generated_model_preserves_oracle_blockers(tmp_path: Path) -> None:
    model_path = write_generated_model(tmp_path / "generated.py", {"Calc!A1": 2, "Calc!A2": "ok"})
    oracle_result = OracleResult(
        backend="formulas",
        source_workbook="source.xlsx",
        diagnostics=(
            OracleDiagnostic(
                diagnostic_code="oracle_calculation_failed",
                message="calculation failed",
                severity="error",
                location="source.xlsx",
            ),
        ),
    )

    result = evaluate_generated_model(
        contract=contract(),
        module_path=model_path,
        scenario=scenario(model_path),
        oracle_result=oracle_result,
    )

    assert result.oracle_validation_report is not None
    assert result.oracle_validation_report.status == "fail"
    assert result.oracle_validation_report.diagnostics[0].diagnostic_code == "oracle_calculation_failed"
    assert {comparison.diagnostic_code for comparison in result.oracle_validation_report.comparisons} == {
        "missing_oracle_output"
    }


def test_validation_evaluation_result_payload_round_trips(tmp_path: Path) -> None:
    model_path = write_generated_model(tmp_path / "generated.py", {"Calc!A1": 2, "Calc!A2": "ok"})
    result = evaluate_generated_model(
        contract=contract(),
        module_path=model_path,
        scenario=scenario(model_path),
        workbook=workbook_with_cached_values(),
    )

    payload = result.to_dict()

    assert json.loads(json.dumps(payload)) == payload
    assert ValidationEvaluationResult.from_dict(payload) == result
