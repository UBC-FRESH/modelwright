from __future__ import annotations

import json
import subprocess
import sys
import tomllib
from pathlib import Path
from types import SimpleNamespace

import pytest

from modelwright.extraction import CellRecord, WorkbookRecord
from modelwright.freshforge import MODELWRIGHT_PROVIDER_ID, provider_factory
from tests.fixtures.synthetic_model.build_workbook import build_workbook


EXAMPLE_PATH = Path("examples/freshforge/generated_model_workflow.yaml")
EXPECTED_PLAN_ORDER = [
    "extract_workbook",
    "build_graph",
    "infer_contract",
    "generate_model",
    "execute_model",
    "evaluate_model",
    "summarize_conversion",
]


def _registry_with_modelwright_provider():
    from freshforge.providers import ProviderRegistry

    registry = ProviderRegistry()
    registry.register(provider_factory())
    return registry


def test_provider_factory_returns_modelwright_provider() -> None:
    provider = provider_factory()

    assert provider.__class__.__name__ == "ModelwrightFreshForgeProvider"
    assert MODELWRIGHT_PROVIDER_ID == "modelwright"


def test_provider_metadata_serializes_deterministically() -> None:
    pytest.importorskip("freshforge")
    metadata = provider_factory().metadata()

    assert metadata.to_dict() == {
        "id": "modelwright",
        "version": "0.1.0a8",
        "node_types": [
            {
                "id": "workbook_extract",
                "inputs": [],
                "outputs": ["workbook_record"],
                "parameters": ["workbook"],
                "artifacts": ["workbook_record"],
                "name": "Extract workbook",
                "description": "Declare extraction of workbook facts into a WorkbookRecord.",
            },
            {
                "id": "workbook_graph",
                "inputs": ["workbook_record"],
                "outputs": ["dependency_graph"],
                "parameters": [],
                "artifacts": ["dependency_graph"],
                "name": "Build workbook dependency graph",
                "description": "Declare dependency graph construction from an extracted workbook record.",
            },
            {
                "id": "model_infer_contract",
                "inputs": [],
                "outputs": ["generated_contract", "formula_expressions", "input_constants"],
                "parameters": ["workbook", "module_name"],
                "artifacts": ["output_refs", "contract", "expressions", "constants", "inference_result"],
                "name": "Infer generated-model contract",
                "description": "Declare selected-output generated-model contract inference.",
            },
            {
                "id": "model_generate",
                "inputs": ["generated_contract", "formula_expressions", "input_constants"],
                "outputs": ["generated_model"],
                "parameters": [],
                "artifacts": [
                    "contract",
                    "expressions",
                    "constants",
                    "generated_model",
                    "generation_result",
                ],
                "name": "Generate Python model",
                "description": "Declare standalone Python model generation from explicit JSON artifacts.",
            },
            {
                "id": "model_execute",
                "inputs": ["generated_contract", "generated_model"],
                "outputs": ["generated_values"],
                "parameters": [],
                "artifacts": ["contract", "generated_model", "generated_values"],
                "name": "Execute generated model",
                "description": "Declare generated-model execution for selected outputs.",
            },
            {
                "id": "validation_evaluate",
                "inputs": ["generated_contract", "generated_model"],
                "outputs": ["validation_report"],
                "parameters": ["scenario"],
                "artifacts": ["contract", "generated_model", "scenario", "evaluation_report"],
                "name": "Evaluate generated model",
                "description": "Declare generated-model evaluation against cached or oracle-backed values.",
            },
            {
                "id": "conversion_plan",
                "inputs": ["workbook_record", "dependency_graph"],
                "outputs": ["conversion_plan"],
                "parameters": ["benchmark_role"],
                "artifacts": ["conversion_plan"],
                "name": "Build conversion plan",
                "description": "Declare a Modelwright conversion-plan summary for the workflow boundary.",
            },
        ],
        "name": "Modelwright workflow provider",
            "description": (
                "Provider for Modelwright workbook extraction, generated-model "
                "materialization, and validation workflow planning/execution."
            ),
    }


def test_pyproject_declares_freshforge_entry_point_without_direct_dependency() -> None:
    pyproject = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))

    entry_points = pyproject["project"]["entry-points"]["freshforge.providers"]
    assert entry_points["modelwright"] == "modelwright.freshforge:provider_factory"
    optional = pyproject["project"]["optional-dependencies"]
    assert "freshforge" not in optional
    assert "freshforge" not in "\n".join(pyproject["project"]["dependencies"])


def test_modelwright_import_does_not_import_freshforge_eagerly() -> None:
    script = "import sys; import modelwright; print('freshforge' in sys.modules)"
    result = subprocess.run(
        [sys.executable, "-c", script],
        check=True,
        capture_output=True,
        text=True,
    )

    assert result.stdout.strip() == "False"


def test_example_workflow_validates_and_plans() -> None:
    pytest.importorskip("freshforge")
    from freshforge.loading import load_workflow
    from freshforge.planning import create_run_plan
    from freshforge.validation import validate_workflow_with_providers

    spec, load_diagnostics = load_workflow(EXAMPLE_PATH)
    assert spec is not None
    assert load_diagnostics == []

    diagnostics = validate_workflow_with_providers(
        spec,
        registry=_registry_with_modelwright_provider(),
        structural_diagnostics=load_diagnostics,
    )
    assert diagnostics == []

    plan = create_run_plan(
        spec,
        diagnostics=diagnostics,
        registry=_registry_with_modelwright_provider(),
    )
    assert not plan.has_errors
    assert [node.id for node in plan.nodes] == EXPECTED_PLAN_ORDER
    assert {node.provider_id for node in plan.nodes} == {"modelwright"}


def test_missing_required_parameter_returns_provider_diagnostic() -> None:
    pytest.importorskip("freshforge")
    from freshforge.loading import load_workflow_document
    from freshforge.validation import validate_workflow_document, validate_workflow_with_providers

    document = load_workflow_document(EXAMPLE_PATH)
    del document["nodes"][0]["parameters"]["workbook"]
    spec, structural = validate_workflow_document(document)

    assert spec is not None
    diagnostics = validate_workflow_with_providers(
        spec,
        registry=_registry_with_modelwright_provider(),
        structural_diagnostics=structural,
    )

    assert {diagnostic.code for diagnostic in diagnostics} == {
        "modelwright.parameters.missing"
    }
    assert diagnostics[0].location == "nodes[0].parameters.workbook"


def test_empty_required_outputs_and_artifacts_return_provider_diagnostics() -> None:
    pytest.importorskip("freshforge")
    from freshforge.loading import load_workflow_document
    from freshforge.validation import validate_workflow_document, validate_workflow_with_providers

    document = load_workflow_document(EXAMPLE_PATH)
    document["nodes"][3]["outputs"]["generated_model"] = " "
    document["nodes"][3]["artifacts"]["generated_model"] = ""
    spec, structural = validate_workflow_document(document)

    assert spec is not None
    diagnostics = validate_workflow_with_providers(
        spec,
        registry=_registry_with_modelwright_provider(),
        structural_diagnostics=structural,
    )

    assert {diagnostic.code for diagnostic in diagnostics} == {
        "modelwright.outputs.empty",
        "modelwright.artifacts.empty",
    }


def test_model_generate_failure_returns_stage_specific_diagnostic(tmp_path: Path) -> None:
    pytest.importorskip("freshforge")
    from freshforge.records import RunStatus

    contract_path = tmp_path / "contract.json"
    expressions_path = tmp_path / "expressions.json"
    constants_path = tmp_path / "constants.json"
    contract_path.write_text(
        json.dumps(
            {
                "workbook_id": "synthetic",
                "module_name": "generated_synthetic_model",
                "entrypoint": "calculate",
                "input_refs": [],
                "output_refs": ["Calc!B1"],
                "symbols": [
                    {
                        "cell_ref": "Calc!B1",
                        "symbol_name": "calc_b1",
                        "kind": "output",
                        "raw_formula": "=Inputs!B1",
                    }
                ],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    expressions_path.write_text("{}", encoding="utf-8")
    constants_path.write_text("{}", encoding="utf-8")

    result = provider_factory().run_node(
        SimpleNamespace(
            id="generate_model",
            artifacts={
                "contract": str(contract_path),
                "expressions": str(expressions_path),
                "constants": str(constants_path),
                "generated_model": str(tmp_path / "generated_synthetic_model.py"),
                "generation_result": str(tmp_path / "generation-result.json"),
            },
        ),
        _provider_node_type("model_generate"),
        context=_context(),
    )

    assert result.status is RunStatus.FAILED
    assert {diagnostic.code for diagnostic in result.diagnostics} == {
        "modelwright.model_generate.failed"
    }
    assert result.data["summary"]["generated"] is False
    assert result.data["summary"]["error_count"] == 1


def test_model_execute_failure_returns_stage_specific_diagnostic(tmp_path: Path) -> None:
    pytest.importorskip("freshforge")
    from freshforge.records import RunStatus

    contract_path = tmp_path / "contract.json"
    contract_path.write_text(
        json.dumps(
            {
                "workbook_id": "synthetic",
                "module_name": "generated_synthetic_model",
                "entrypoint": "calculate",
                "input_refs": [],
                "output_refs": ["Calc!B1"],
                "symbols": [
                    {
                        "cell_ref": "Calc!B1",
                        "symbol_name": "calc_b1",
                        "kind": "output",
                        "raw_formula": None,
                    }
                ],
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    result = provider_factory().run_node(
        SimpleNamespace(
            id="execute_model",
            artifacts={
                "contract": str(contract_path),
                "generated_model": str(tmp_path / "missing_generated_model.py"),
                "generated_values": str(tmp_path / "generated-values.json"),
            },
        ),
        _provider_node_type("model_execute"),
        context=_context(),
    )

    assert result.status is RunStatus.FAILED
    assert {diagnostic.code for diagnostic in result.diagnostics} == {
        "modelwright.model_execute.failed"
    }
    assert result.data["summary"]["executed"] is False
    assert result.data["summary"]["error_count"] == 1


def test_freshforge_run_executes_synthetic_generated_model_workflow_with_summaries(
    tmp_path: Path,
) -> None:
    pytest.importorskip("freshforge")
    from freshforge.execution import run_workflow
    from freshforge.validation import validate_workflow_document

    workbook_path = build_workbook(tmp_path / "synthetic_model.xlsx")
    namespace = "strategy/output-columns"
    workflow, artifact_dir = _synthetic_generated_model_workflow(
        tmp_path=tmp_path,
        workbook_path=workbook_path,
        run_namespace=namespace,
        cached_summary_b2=70.2,
    )
    spec, diagnostics = validate_workflow_document(workflow)
    assert spec is not None

    result = run_workflow(
        spec,
        diagnostics=diagnostics,
        registry=_registry_with_modelwright_provider(),
        workdir=tmp_path,
        run_namespace=namespace,
    )

    assert result.ok
    assert [node.id for node in result.nodes] == [
        "infer_contract",
        "generate_model",
        "execute_model",
        "evaluate_model",
    ]
    assert json.loads((artifact_dir / "generated-values.json").read_text(encoding="utf-8"))[
        "output_values"
    ] == {"Summary!B2": 70.2, "Summary!B3": "ok"}
    evaluation = json.loads((artifact_dir / "evaluation-report.json").read_text(encoding="utf-8"))
    assert evaluation["generated_execution"]["executed"] is True
    assert evaluation["cached_validation_report"]["status"] == "pass"
    assert (artifact_dir / "generated_synthetic_model.py").exists()

    run_summary = result.summary()
    assert run_summary.run_namespace == namespace
    assert run_summary.node_count == 4
    assert run_summary.artifact_count == 18
    assert {node.id for node in run_summary.nodes} == {
        "infer_contract",
        "generate_model",
        "execute_model",
        "evaluate_model",
    }

    node_summaries = {node.id: node.data["summary"] for node in result.nodes}
    assert node_summaries["infer_contract"] == {
        "stage": "model_infer_contract",
        "inferred": True,
        "input_ref_count": 3,
        "output_ref_count": 2,
        "symbol_count": 8,
        "expression_count": 5,
        "constant_count": 3,
        "diagnostic_count": 0,
        "error_count": 0,
        "warning_count": 0,
    }
    assert node_summaries["generate_model"]["stage"] == "model_generate"
    assert node_summaries["generate_model"]["generated"] is True
    assert node_summaries["generate_model"]["source_line_count"] > 0
    assert node_summaries["execute_model"] == {
        "stage": "model_execute",
        "executed": True,
        "declared_output_count": 2,
        "generated_output_count": 2,
        "missing_output_diagnostic_count": 0,
        "diagnostic_count": 0,
        "error_count": 0,
        "warning_count": 0,
    }
    assert node_summaries["evaluate_model"]["cached_validation"] == {
        "available": True,
        "status": "pass",
        "comparison_count": 2,
        "match_count": 2,
        "mismatch_count": 0,
        "diagnostic_count": 0,
        "error_count": 0,
        "warning_count": 0,
    }
    assert node_summaries["evaluate_model"]["oracle_validation"]["available"] is False


def test_validation_evaluate_failure_fails_freshforge_node(tmp_path: Path) -> None:
    pytest.importorskip("freshforge")
    from freshforge.execution import run_workflow
    from freshforge.validation import validate_workflow_document

    workbook_path = build_workbook(tmp_path / "synthetic_model.xlsx")
    workflow, artifact_dir = _synthetic_generated_model_workflow(
        tmp_path=tmp_path,
        workbook_path=workbook_path,
        run_namespace=None,
        cached_summary_b2=999.0,
    )
    spec, diagnostics = validate_workflow_document(workflow)
    assert spec is not None

    result = run_workflow(
        spec,
        diagnostics=diagnostics,
        registry=_registry_with_modelwright_provider(),
        workdir=tmp_path,
    )

    assert not result.ok
    assert result.nodes[-1].id == "evaluate_model"
    assert result.nodes[-1].status.value == "failed"
    assert {diagnostic.code for diagnostic in result.nodes[-1].diagnostics} == {
        "modelwright.validation_evaluate.failed"
    }
    summary = result.nodes[-1].data["summary"]
    assert summary["cached_validation"]["status"] == "fail"
    assert summary["cached_validation"]["mismatch_count"] == 1
    evaluation = json.loads((artifact_dir / "evaluation-report.json").read_text(encoding="utf-8"))
    assert evaluation["cached_validation_report"]["status"] == "fail"


def _provider_node_type(node_type_id: str):
    for node_type in provider_factory().metadata().node_types:
        if node_type.id == node_type_id:
            return node_type
    raise AssertionError(f"missing Modelwright provider node type {node_type_id}")


def _context():
    return SimpleNamespace(resolve_path=lambda value: Path(value))


def _synthetic_generated_model_workflow(
    *,
    tmp_path: Path,
    workbook_path: Path,
    run_namespace: str | None,
    cached_summary_b2: float,
) -> tuple[dict[str, object], Path]:
    artifact_dir = tmp_path / "freshforge-run"
    if run_namespace is not None:
        artifact_dir = tmp_path / run_namespace / "freshforge-run"
    artifact_dir.mkdir(parents=True)
    output_refs_path = artifact_dir / "output_refs.json"
    output_refs_path.write_text(
        json.dumps(["Summary!B2", "Summary!B3"], indent=2),
        encoding="utf-8",
    )
    workbook_record_path = artifact_dir / "workbook-record.json"
    workbook_record_path.write_text(
        json.dumps(
            WorkbookRecord(
                workbook_id="synthetic_model.xlsx",
                source_path="synthetic_model.xlsx",
                cells=(
                    CellRecord(
                        cell_ref="Summary!B2",
                        kind="formula",
                        raw_value="=Calc!B4",
                        cached_value=cached_summary_b2,
                    ),
                    CellRecord(
                        cell_ref="Summary!B3",
                        kind="formula",
                        raw_value='=IF(B2>100,"high","ok")',
                        cached_value="ok",
                    ),
                ),
            ).to_dict(),
            indent=2,
        ),
        encoding="utf-8",
    )
    scenario_path = Path("tests/fixtures/synthetic_model/baseline_scenario.json").resolve()

    return (
        {
            "workflow": {"id": "modelwright_freshforge_run"},
            "nodes": [
                {
                    "id": "infer_contract",
                    "provider": "modelwright.model_infer_contract",
                    "outputs": {
                        "generated_contract": "generated_contract",
                        "formula_expressions": "formula_expressions",
                        "input_constants": "input_constants",
                    },
                    "parameters": {
                        "workbook": str(workbook_path),
                        "module_name": "generated_synthetic_model",
                    },
                    "artifacts": {
                        "output_refs": "freshforge-run/output_refs.json",
                        "contract": "freshforge-run/contract.json",
                        "expressions": "freshforge-run/expressions.json",
                        "constants": "freshforge-run/constants.json",
                        "inference_result": "freshforge-run/inference-result.json",
                    },
                },
                {
                    "id": "generate_model",
                    "provider": "modelwright.model_generate",
                    "needs": ["infer_contract"],
                    "inputs": {
                        "generated_contract": "infer_contract.generated_contract",
                        "formula_expressions": "infer_contract.formula_expressions",
                        "input_constants": "infer_contract.input_constants",
                    },
                    "outputs": {"generated_model": "generated_synthetic_model"},
                    "artifacts": {
                        "contract": "freshforge-run/contract.json",
                        "expressions": "freshforge-run/expressions.json",
                        "constants": "freshforge-run/constants.json",
                        "generated_model": "freshforge-run/generated_synthetic_model.py",
                        "generation_result": "freshforge-run/generation-result.json",
                    },
                },
                {
                    "id": "execute_model",
                    "provider": "modelwright.model_execute",
                    "needs": ["generate_model"],
                    "inputs": {
                        "generated_contract": "infer_contract.generated_contract",
                        "generated_model": "generate_model.generated_model",
                    },
                    "outputs": {"generated_values": "generated_values"},
                    "artifacts": {
                        "contract": "freshforge-run/contract.json",
                        "generated_model": "freshforge-run/generated_synthetic_model.py",
                        "generated_values": "freshforge-run/generated-values.json",
                    },
                },
                {
                    "id": "evaluate_model",
                    "provider": "modelwright.validation_evaluate",
                    "needs": ["execute_model"],
                    "inputs": {
                        "generated_contract": "infer_contract.generated_contract",
                        "generated_model": "generate_model.generated_model",
                    },
                    "outputs": {"validation_report": "validation_report"},
                    "parameters": {
                        "scenario": str(scenario_path),
                    },
                    "artifacts": {
                        "contract": "freshforge-run/contract.json",
                        "generated_model": "freshforge-run/generated_synthetic_model.py",
                        "scenario": str(scenario_path),
                        "workbook_record": "freshforge-run/workbook-record.json",
                        "evaluation_report": "freshforge-run/evaluation-report.json",
                    },
                },
            ],
        },
        artifact_dir,
    )
