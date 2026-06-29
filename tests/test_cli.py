import json
import tomllib
from pathlib import Path

from typer.testing import CliRunner

from modelwright.cli import app
from modelwright.extraction import extract_workbook
from modelwright.extraction import CellRecord, WorkbookRecord
from modelwright.formulas import translate_formula_cell
from modelwright.generation import (
    GeneratedModuleContract,
    GeneratedSymbol,
    generate_python_module,
    symbol_name_for_cell_ref,
)
from modelwright.graph import build_dependency_graph
from tests.fixtures.synthetic_model.build_workbook import build_workbook


runner = CliRunner()


def test_cli_script_entrypoint_is_declared() -> None:
    pyproject = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))

    assert pyproject["project"]["scripts"]["modelwright"] == "modelwright.cli:app"


def test_cli_help_exposes_fresh_style_workflow_groups() -> None:
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "workbook" in result.stdout
    assert "model" in result.stdout
    assert "validation" in result.stdout
    assert "conversion" in result.stdout


def test_workbook_extract_command_outputs_workbook_json(tmp_path: Path) -> None:
    workbook_path = build_workbook(tmp_path / "synthetic_model.xlsx")

    result = runner.invoke(app, ["workbook", "extract", str(workbook_path)])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["workbook_id"] == "synthetic_model.xlsx"
    assert {sheet["title"] for sheet in payload["sheets"]} == {"Inputs", "Calc", "Summary"}
    assert any(cell["cell_ref"] == "Summary!B3" and cell["formula"] for cell in payload["cells"])


def test_workbook_graph_command_outputs_dependency_json(tmp_path: Path) -> None:
    workbook_path = build_workbook(tmp_path / "synthetic_model.xlsx")

    result = runner.invoke(app, ["workbook", "graph", str(workbook_path)])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    execution_edges = [edge for edge in payload["edges"] if edge["edge_kind"] == "execution"]
    assert payload["workbook_id"] == "synthetic_model.xlsx"
    assert any(edge["source"]["normalized"] == "Calc!B4" for edge in execution_edges)
    assert any(edge["target"]["normalized"] == "Summary!B3" for edge in execution_edges)


def test_model_generate_command_outputs_result_json_and_writes_model(tmp_path: Path) -> None:
    contract, expressions, constants = _synthetic_generation_inputs(tmp_path)
    contract_path = tmp_path / "contract.json"
    expressions_path = tmp_path / "expressions.json"
    constants_path = tmp_path / "constants.json"
    output_path = tmp_path / "generated_model.py"
    _write_json(contract_path, contract.to_dict())
    _write_json(expressions_path, {cell_ref: expression.to_dict() for cell_ref, expression in expressions.items()})
    _write_json(constants_path, constants)

    result = runner.invoke(
        app,
        [
            "model",
            "generate",
            "--contract",
            str(contract_path),
            "--expressions",
            str(expressions_path),
            "--constants",
            str(constants_path),
            "--out",
            str(output_path),
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["generated"] is True
    assert payload["contract"]["module_name"] == "synthetic_model"
    assert output_path.exists()
    assert "def calculate(inputs=None):" in output_path.read_text(encoding="utf-8")


def test_model_generate_rejects_removed_output_option(tmp_path: Path) -> None:
    contract, expressions, constants = _synthetic_generation_inputs(tmp_path)
    contract_path = tmp_path / "contract.json"
    expressions_path = tmp_path / "expressions.json"
    constants_path = tmp_path / "constants.json"
    output_path = tmp_path / "generated_model.py"
    _write_json(contract_path, contract.to_dict())
    _write_json(expressions_path, {cell_ref: expression.to_dict() for cell_ref, expression in expressions.items()})
    _write_json(constants_path, constants)

    result = runner.invoke(
        app,
        [
            "model",
            "generate",
            "--contract",
            str(contract_path),
            "--expressions",
            str(expressions_path),
            "--constants",
            str(constants_path),
            "--output",
            str(output_path),
        ],
    )

    assert result.exit_code != 0
    assert not output_path.exists()


def test_model_infer_contract_command_writes_generation_inputs(tmp_path: Path) -> None:
    workbook_path = build_workbook(tmp_path / "synthetic_model.xlsx")
    artifact_dir = tmp_path / "artifacts"
    contract_path = artifact_dir / "contract.json"
    expressions_path = artifact_dir / "expressions.json"
    constants_path = artifact_dir / "constants.json"

    result = runner.invoke(
        app,
        [
            "model",
            "infer-contract",
            str(workbook_path),
            "--module-name",
            "synthetic_model",
            "--output-ref",
            "Summary!B2",
            "--output-ref",
            "Summary!B3",
            "--contract",
            str(contract_path),
            "--expressions",
            str(expressions_path),
            "--constants",
            str(constants_path),
            "--verbose",
        ],
    )

    assert result.exit_code == 0
    assert "extract workbook start" in result.stderr
    payload = json.loads(result.stdout)
    assert payload["inferred"] is True
    assert payload["contract"]["output_refs"] == ["Summary!B2", "Summary!B3"]
    assert json.loads(contract_path.read_text(encoding="utf-8"))["module_name"] == "synthetic_model"
    assert set(json.loads(expressions_path.read_text(encoding="utf-8"))) == {
        "Calc!B2",
        "Calc!B3",
        "Calc!B4",
        "Summary!B2",
        "Summary!B3",
    }
    assert json.loads(constants_path.read_text(encoding="utf-8")) == {
        "Inputs!B2": 100,
        "Inputs!B3": 0.08,
        "Inputs!B4": 0.65,
    }


def test_model_infer_contract_output_refs_file_can_feed_model_generate(tmp_path: Path) -> None:
    workbook_path = build_workbook(tmp_path / "synthetic_model.xlsx")
    artifact_dir = tmp_path / "generated-model"
    output_refs_path = artifact_dir / "output_refs.json"
    contract_path = artifact_dir / "contract.json"
    expressions_path = artifact_dir / "expressions.json"
    constants_path = artifact_dir / "constants.json"
    generated_model_path = artifact_dir / "generated_model.py"
    artifact_dir.mkdir()
    _write_json(output_refs_path, ["Summary!B2", "Summary!B3"])

    inference = runner.invoke(
        app,
        [
            "model",
            "infer-contract",
            str(workbook_path),
            "--module-name",
            "synthetic_model",
            "--output-refs-file",
            str(output_refs_path),
            "--contract",
            str(contract_path),
            "--expressions",
            str(expressions_path),
            "--constants",
            str(constants_path),
        ],
    )
    generation = runner.invoke(
        app,
        [
            "model",
            "generate",
            "--contract",
            str(contract_path),
            "--expressions",
            str(expressions_path),
            "--constants",
            str(constants_path),
            "--out",
            str(generated_model_path),
        ],
    )
    execution = runner.invoke(
        app,
        [
            "model",
            "execute",
            "--contract",
            str(contract_path),
            "--model",
            str(generated_model_path),
        ],
    )

    assert inference.exit_code == 0
    assert json.loads(inference.stdout)["contract"]["output_refs"] == ["Summary!B2", "Summary!B3"]
    assert generation.exit_code == 0
    assert json.loads(generation.stdout)["generated"] is True
    assert execution.exit_code == 0
    assert json.loads(execution.stdout)["output_values"] == {"Summary!B2": 70.2, "Summary!B3": "ok"}


def test_model_infer_contract_rejects_missing_output_refs_without_writes(tmp_path: Path) -> None:
    workbook_path = build_workbook(tmp_path / "synthetic_model.xlsx")
    contract_path = tmp_path / "contract.json"

    result = runner.invoke(
        app,
        [
            "model",
            "infer-contract",
            str(workbook_path),
            "--module-name",
            "synthetic_model",
            "--contract",
            str(contract_path),
            "--expressions",
            str(tmp_path / "expressions.json"),
            "--constants",
            str(tmp_path / "constants.json"),
        ],
    )

    assert result.exit_code != 0
    assert "provide at least one --output-ref or --output-refs-file entry" in result.stderr
    assert not contract_path.exists()


def test_model_infer_contract_rejects_invalid_output_refs_file_without_writes(tmp_path: Path) -> None:
    workbook_path = build_workbook(tmp_path / "synthetic_model.xlsx")
    output_refs_path = tmp_path / "output_refs.json"
    contract_path = tmp_path / "contract.json"
    _write_json(output_refs_path, {"not": "a list"})

    result = runner.invoke(
        app,
        [
            "model",
            "infer-contract",
            str(workbook_path),
            "--module-name",
            "synthetic_model",
            "--output-refs-file",
            str(output_refs_path),
            "--contract",
            str(contract_path),
            "--expressions",
            str(tmp_path / "expressions.json"),
            "--constants",
            str(tmp_path / "constants.json"),
        ],
    )

    assert result.exit_code != 0
    assert "expected JSON array of strings" in result.stderr
    assert not contract_path.exists()


def test_model_execute_command_outputs_generated_values(tmp_path: Path) -> None:
    contract, expressions, constants = _synthetic_generation_inputs(tmp_path)
    contract_path = tmp_path / "contract.json"
    output_path = tmp_path / "generated_model.py"
    _write_json(contract_path, contract.to_dict())
    generation_result = generate_python_module(
        contract=contract,
        expressions=expressions,
        constants=constants,
        output_path=output_path,
    )
    assert generation_result.generated is True

    result = runner.invoke(
        app,
        [
            "model",
            "execute",
            "--contract",
            str(contract_path),
            "--model",
            str(output_path),
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["executed"] is True
    assert payload["output_values"] == {"Summary!B2": 70.2, "Summary!B3": "ok"}


def test_validation_report_command_outputs_report_json(tmp_path: Path) -> None:
    fixture_root = Path(__file__).parent / "fixtures" / "synthetic_model"
    generated_values = {"Summary!B2": 70.2, "Summary!B3": "ok"}
    oracle_values = {"Summary!B2": 70.2, "Summary!B3": "ok"}
    generated_values_path = tmp_path / "generated_values.json"
    oracle_values_path = tmp_path / "oracle_values.json"
    _write_json(generated_values_path, generated_values)
    _write_json(oracle_values_path, oracle_values)

    result = runner.invoke(
        app,
        [
            "validation",
            "report",
            "--scenario",
            str(fixture_root / "baseline_scenario.json"),
            "--generated-values",
            str(generated_values_path),
            "--oracle-values",
            str(oracle_values_path),
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["scenario_id"] == "synthetic_model_baseline"
    assert payload["status"] == "pass"
    assert payload["mismatches"] == []


def test_validation_evaluate_command_outputs_evaluation_json(tmp_path: Path) -> None:
    fixture_root = Path(__file__).parent / "fixtures" / "synthetic_model"
    contract, expressions, constants = _synthetic_generation_inputs(tmp_path)
    contract_path = tmp_path / "contract.json"
    output_path = tmp_path / "generated_model.py"
    workbook_record_path = tmp_path / "workbook-record.json"
    _write_json(contract_path, contract.to_dict())
    _write_json(
        workbook_record_path,
        WorkbookRecord(
            workbook_id="synthetic_model.xlsx",
            source_path="synthetic_model.xlsx",
            cells=(
                CellRecord(cell_ref="Summary!B2", kind="formula", raw_value="=Calc!B4", cached_value=70.2),
                CellRecord(cell_ref="Summary!B3", kind="formula", raw_value='=IF(B2>100,"high","ok")', cached_value="ok"),
            ),
        ).to_dict(),
    )
    generation_result = generate_python_module(
        contract=contract,
        expressions=expressions,
        constants=constants,
        output_path=output_path,
    )
    assert generation_result.generated is True

    result = runner.invoke(
        app,
        [
            "validation",
            "evaluate",
            "--contract",
            str(contract_path),
            "--model",
            str(output_path),
            "--scenario",
            str(fixture_root / "baseline_scenario.json"),
            "--workbook-record",
            str(workbook_record_path),
            "--verbose",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert "evaluate generated model" in result.stderr
    assert payload["generated_execution"]["executed"] is True
    assert payload["cached_validation_report"]["status"] == "pass"
    assert payload["cached_validation_report"]["oracle_backend"] == "cached_workbook"
    assert payload["oracle_validation_report"] is None


def test_conversion_plan_command_outputs_plan_json(tmp_path: Path) -> None:
    workbook_path = build_workbook(tmp_path / "synthetic_model.xlsx")

    result = runner.invoke(
        app,
        [
            "conversion",
            "plan",
            str(workbook_path),
            "--plan-id",
            "synthetic-plan",
            "--benchmark-role",
            "synthetic_fixture",
            "--modelwright-commit",
            "test-commit",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["plan_id"] == "synthetic-plan"
    assert payload["modelwright_commit"] == "test-commit"
    assert payload["source"]["workbook_id"] == "synthetic_model.xlsx"
    assert payload["source"]["benchmark_role"] == "synthetic_fixture"
    assert payload["source"]["source_path"] is None
    assert payload["workflow_status"]["extraction"] == "pass"
    assert payload["workflow_status"]["dependency_graph"] == "pass"
    assert payload["workflow_status"]["formula_translation"] == "pass"
    assert payload["workflow_status"]["generation"] == "not_run"
    assert payload["coverage"]["translation_coverage"] == 1.0


def test_conversion_plan_command_rejects_unknown_benchmark_role(tmp_path: Path) -> None:
    workbook_path = build_workbook(tmp_path / "synthetic_model.xlsx")

    result = runner.invoke(
        app,
        [
            "conversion",
            "plan",
            str(workbook_path),
            "--benchmark-role",
            "not-a-role",
        ],
    )

    assert result.exit_code != 0
    assert "unsupported benchmark role" in result.stderr


def _synthetic_generation_inputs(tmp_path: Path):
    workbook = extract_workbook(build_workbook(tmp_path / "synthetic_model.xlsx"))
    graph = build_dependency_graph(workbook)
    formula_cells = {cell.cell_ref: cell for cell in workbook.cells if cell.formula is not None}
    expressions = {
        cell_ref: translate_formula_cell(cell, graph)
        for cell_ref, cell in formula_cells.items()
    }
    constants = {
        cell.cell_ref: cell.raw_value
        for cell in workbook.cells
        if cell.formula is None and cell.cell_ref in {"Inputs!B2", "Inputs!B3", "Inputs!B4"}
    }
    formula_order = ("Calc!B2", "Calc!B3", "Calc!B4", "Summary!B2", "Summary!B3")
    contract = GeneratedModuleContract(
        workbook_id=workbook.workbook_id,
        module_name="synthetic_model",
        input_refs=tuple(constants),
        output_refs=("Summary!B2", "Summary!B3"),
        symbols=(
            tuple(
                GeneratedSymbol(
                    cell_ref=cell_ref,
                    symbol_name=symbol_name_for_cell_ref(cell_ref),
                    kind="input",
                )
                for cell_ref in constants
            )
            + tuple(
                GeneratedSymbol(
                    cell_ref=cell_ref,
                    symbol_name=symbol_name_for_cell_ref(cell_ref),
                    kind="output" if cell_ref.startswith("Summary!") else "intermediate",
                    raw_formula=formula_cells[cell_ref].formula.raw_formula,
                )
                for cell_ref in formula_order
            )
        ),
    )
    return contract, expressions, constants


def _write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload), encoding="utf-8")
