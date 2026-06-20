import json
import tomllib
from pathlib import Path

from typer.testing import CliRunner

from sheetforge.cli import app
from sheetforge.extraction import extract_workbook
from sheetforge.formulas import translate_formula_cell
from sheetforge.generation import (
    GeneratedModuleContract,
    GeneratedSymbol,
    symbol_name_for_cell_ref,
)
from sheetforge.graph import build_dependency_graph
from tests.fixtures.synthetic_model.build_workbook import build_workbook


runner = CliRunner()


def test_cli_script_entrypoint_is_declared() -> None:
    pyproject = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))

    assert pyproject["project"]["scripts"]["sheetforge"] == "sheetforge.cli:app"


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
            "--sheetforge-commit",
            "test-commit",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["plan_id"] == "synthetic-plan"
    assert payload["sheetforge_commit"] == "test-commit"
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
