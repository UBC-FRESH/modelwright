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


def test_validation_evidence_help_is_available() -> None:
    result = runner.invoke(app, ["validation", "evidence", "--help"])

    assert result.exit_code == 0
    assert "Package compact validation evidence" in result.stdout


def test_validation_evidence_json_skips_missing_artifacts_by_default(tmp_path: Path) -> None:
    artifact_dir = tmp_path / "missing-artifacts"
    output_dir = tmp_path / "evidence"

    result = runner.invoke(
        app,
        [
            "validation",
            "evidence",
            "--evidence-id",
            "empty",
            "--artifact-dir",
            str(artifact_dir),
            "--output-dir",
            str(output_dir),
            "--json",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["evidence_status"] == "skipped"
    assert payload["equivalence_status"] == "incomplete"
    assert payload["missing_artifacts"]
    assert (output_dir / "summary.json").exists()
    assert (output_dir / "summary.md").exists()


def test_validation_evidence_require_artifacts_fails(tmp_path: Path) -> None:
    result = runner.invoke(
        app,
        [
            "validation",
            "evidence",
            "--artifact-dir",
            str(tmp_path / "missing-artifacts"),
            "--require-artifacts",
            "--json",
        ],
    )

    assert result.exit_code != 0
    payload = json.loads(result.stdout)
    assert payload["ok"] is False
    assert "missing validation evidence artifact" in payload["error"]


def test_validation_evidence_uses_custom_artifact_output_and_scenario_paths(tmp_path: Path) -> None:
    artifact_dir = tmp_path / "artifacts"
    output_dir = tmp_path / "evidence"
    scenario_path = tmp_path / "custom-scenario.json"
    _write_validation_evidence_artifacts(artifact_dir, scenario_path)

    result = runner.invoke(
        app,
        [
            "validation",
            "evidence",
            "--evidence-id",
            "synthetic",
            "--artifact-dir",
            str(artifact_dir),
            "--output-dir",
            str(output_dir),
            "--scenario",
            str(scenario_path),
            "--json",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["evidence_status"] == "complete"
    assert payload["equivalence_status"] == "pass"
    assert payload["comparison"]["comparable_output_count"] == 2
    assert payload["summary_json_path"] == str(output_dir / "summary.json")
    assert json.loads((output_dir / "summary.json").read_text(encoding="utf-8"))["evidence_id"] == "synthetic"


def test_validation_matrix_evidence_help_is_available() -> None:
    result = runner.invoke(app, ["validation", "matrix-evidence", "--help"])

    assert result.exit_code == 0
    assert "Package compact validation evidence for a FreshForge matrix run" in result.stdout


def test_validation_matrix_evidence_json_output(tmp_path: Path) -> None:
    matrix_run = tmp_path / "matrix-run.json"
    artifact_root = tmp_path / "artifacts"
    output_dir = tmp_path / "matrix-evidence"
    case_dir = artifact_root / "strategy" / "output-columns"
    _write_matrix_run(matrix_run, case_ids=("output-columns",))
    _write_validation_evidence_artifacts(case_dir, case_dir / "validation-scenario.json")

    result = runner.invoke(
        app,
        [
            "validation",
            "matrix-evidence",
            "--evidence-id",
            "strategy-matrix",
            "--matrix-run",
            str(matrix_run),
            "--artifact-root",
            str(artifact_root),
            "--output-dir",
            str(output_dir),
            "--json",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["evidence_status"] == "complete"
    assert payload["equivalence_status"] == "pass"
    assert payload["case_count"] == 1
    assert payload["summary"]["cases"][0]["case_id"] == "output-columns"
    assert (output_dir / "summary.json").exists()
    assert (output_dir / "summary.md").exists()


def test_validation_matrix_evidence_require_evidence_fails(tmp_path: Path) -> None:
    matrix_run = tmp_path / "matrix-run.json"
    _write_matrix_run(matrix_run, case_ids=("output-columns",))

    result = runner.invoke(
        app,
        [
            "validation",
            "matrix-evidence",
            "--matrix-run",
            str(matrix_run),
            "--artifact-root",
            str(tmp_path / "missing"),
            "--require-evidence",
            "--json",
        ],
    )

    assert result.exit_code != 0
    payload = json.loads(result.stdout)
    assert payload["ok"] is False
    assert "missing matrix case evidence" in payload["error"]


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


def _write_validation_evidence_artifacts(artifact_dir: Path, scenario_path: Path) -> None:
    artifact_dir.mkdir(parents=True, exist_ok=True)
    _write_json(
        artifact_dir / "inference-result.json",
        {
            "inferred": True,
            "contract": {"input_refs": ["Inputs!B2"], "output_refs": ["Summary!B2", "Summary!B3"], "symbols": {}},
            "expressions": {"Summary!B2": {}, "Summary!B3": {}},
            "constants": {"Inputs!B2": 100},
            "diagnostics": [],
        },
    )
    _write_json(
        artifact_dir / "generation-result.json",
        {
            "generated": True,
            "contract": {"input_refs": ["Inputs!B2"], "output_refs": ["Summary!B2", "Summary!B3"], "symbols": {}},
            "source_code": "def calculate(inputs=None):\n    return {}\n",
            "diagnostics": [],
        },
    )
    _write_json(
        artifact_dir / "generated-values.json",
        {
            "executed": True,
            "contract": {"output_refs": ["Summary!B2", "Summary!B3"]},
            "output_values": {"Summary!B2": 70.2, "Summary!B3": "ok"},
            "diagnostics": [],
        },
    )
    _write_json(
        scenario_path,
        {
            "scenario_id": "baseline",
            "inputs": [{"cell_ref": "Inputs!B2", "kind": "number", "value": 100}],
            "outputs": [
                {"cell_ref": "Summary!B2", "kind": "number"},
                {"cell_ref": "Summary!B3", "kind": "text"},
            ],
        },
    )
    _write_json(
        artifact_dir / "evaluation-report.json",
        {
            "scenario_id": "baseline",
            "generated_execution": {"executed": True, "output_values": {"Summary!B2": 70.2}, "diagnostics": []},
            "cached_validation_report": {
                "scenario_id": "baseline",
                "oracle_backend": "cached_workbook",
                "status": "pass",
                "comparisons": [
                    {"cell_ref": "Summary!B2", "matches": True, "generated": 70.2, "oracle": 70.2},
                    {"cell_ref": "Summary!B3", "matches": True, "generated": "ok", "oracle": "ok"},
                ],
                "mismatches": [],
                "diagnostics": [],
            },
            "oracle_validation_report": None,
            "diagnostics": [],
        },
    )


def _write_matrix_run(path: Path, *, case_ids: tuple[str, ...]) -> None:
    _write_json(
        path,
        {
            "ok": True,
            "run": {
                "matrix_id": "strategy",
                "status": "success",
                "cases": [
                    {
                        "case_id": case_id,
                        "namespace": f"strategy/{case_id}",
                        "run": {
                            "workflow_id": f"workflow-{case_id}",
                            "run_namespace": f"strategy/{case_id}",
                            "status": "success",
                            "nodes": [],
                            "diagnostics": [],
                        },
                        "summary": {
                            "workflow_id": f"workflow-{case_id}",
                            "run_namespace": f"strategy/{case_id}",
                            "status": "success",
                            "node_count": 0,
                            "diagnostic_count": 0,
                            "error_count": 0,
                            "warning_count": 0,
                            "artifact_count": 0,
                            "nodes": [],
                        },
                        "diagnostics": [],
                    }
                    for case_id in case_ids
                ],
                "diagnostics": [],
            },
            "summary": {
                "matrix_id": "strategy",
                "status": "success",
                "case_count": len(case_ids),
                "succeeded_count": len(case_ids),
                "failed_count": 0,
                "skipped_count": 0,
                "diagnostic_count": 0,
                "error_count": 0,
                "warning_count": 0,
                "cases": [
                    {
                        "workflow_id": f"workflow-{case_id}",
                        "run_namespace": f"strategy/{case_id}",
                        "status": "success",
                        "node_count": 0,
                        "diagnostic_count": 0,
                        "error_count": 0,
                        "warning_count": 0,
                        "artifact_count": 0,
                        "nodes": [],
                    }
                    for case_id in case_ids
                ],
            },
        },
    )
