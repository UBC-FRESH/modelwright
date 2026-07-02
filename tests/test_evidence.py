import json
from pathlib import Path

import pytest

from modelwright.evidence import (
    extract_matrix_evidence,
    extract_validation_evidence,
    matrix_evidence_paths,
    validation_evidence_paths,
    write_matrix_evidence,
    write_validation_evidence,
)


def test_complete_pass_evidence_reports_zero_mismatch_equivalence(tmp_path: Path) -> None:
    paths = validation_evidence_paths(artifact_dir=tmp_path / "artifacts", output_dir=tmp_path / "evidence")
    _write_artifacts(paths.artifact_dir, comparison={"comparable_output_count": 2, "match_count": 2, "mismatch_count": 0})

    summary = extract_validation_evidence(paths, require_artifacts=True)

    assert summary.evidence_status == "complete"
    assert summary.equivalence_status == "pass"
    assert summary.comparison["comparable_output_count"] == 2
    assert summary.comparison["match_count"] == 2
    assert summary.comparison["mismatch_count"] == 0


def test_explicit_mismatch_counts_fail_equivalence(tmp_path: Path) -> None:
    paths = validation_evidence_paths(artifact_dir=tmp_path / "artifacts", output_dir=tmp_path / "evidence")
    _write_artifacts(paths.artifact_dir, comparison={"comparable_output_count": 2, "match_count": 1, "mismatch_count": 1})

    summary = extract_validation_evidence(paths)

    assert summary.evidence_status == "complete"
    assert summary.equivalence_status == "fail"


def test_validation_report_comparisons_are_summarized_without_raw_payloads(tmp_path: Path) -> None:
    paths = validation_evidence_paths(artifact_dir=tmp_path / "artifacts", output_dir=tmp_path / "evidence")
    _write_artifacts(
        paths.artifact_dir,
        comparison_rows=[
            {"cell_ref": "Summary!B2", "matches": True, "generated": 10, "oracle": 10},
            {"cell_ref": "Summary!B3", "matches": False, "generated": 11, "oracle": 12},
        ],
    )

    summary = extract_validation_evidence(paths)
    written = write_validation_evidence(summary, paths)
    summary_json = Path(str(written["summary_json_path"])).read_text(encoding="utf-8")

    assert summary.equivalence_status == "fail"
    assert summary.comparison["comparable_output_count"] == 2
    assert summary.comparison["match_count"] == 1
    assert summary.comparison["mismatch_count"] == 1
    assert "source_code" not in summary_json
    assert "output_values" not in summary_json
    assert "Summary!B2" not in summary_json
    assert "generated secret" not in summary_json
    assert "oracle secret" not in summary_json


def test_missing_comparison_counts_are_incomplete(tmp_path: Path) -> None:
    paths = validation_evidence_paths(artifact_dir=tmp_path / "artifacts", output_dir=tmp_path / "evidence")
    _write_artifacts(paths.artifact_dir, include_report=False)

    summary = extract_validation_evidence(paths)

    assert summary.evidence_status == "incomplete"
    assert summary.equivalence_status == "incomplete"
    assert "Explicit comparable-output" in summary.notes[0]


def test_missing_artifacts_skip_by_default(tmp_path: Path) -> None:
    paths = validation_evidence_paths(artifact_dir=tmp_path / "missing", output_dir=tmp_path / "evidence")

    summary = extract_validation_evidence(paths)

    assert summary.evidence_status == "skipped"
    assert summary.equivalence_status == "incomplete"
    assert summary.missing_artifacts


def test_missing_artifacts_can_be_required(tmp_path: Path) -> None:
    paths = validation_evidence_paths(artifact_dir=tmp_path / "missing", output_dir=tmp_path / "evidence")

    with pytest.raises(FileNotFoundError, match="missing validation evidence artifact"):
        extract_validation_evidence(paths, require_artifacts=True)


def test_write_validation_evidence_writes_stable_json_and_markdown(tmp_path: Path) -> None:
    paths = validation_evidence_paths(
        evidence_id="synthetic-example",
        artifact_dir=tmp_path / "artifacts",
        output_dir=tmp_path / "evidence",
    )
    _write_artifacts(paths.artifact_dir, comparison={"comparable_output_count": 1, "match_count": 1, "mismatch_count": 0})
    summary = extract_validation_evidence(paths)

    written = write_validation_evidence(summary, paths)

    payload = json.loads(Path(str(written["summary_json_path"])).read_text(encoding="utf-8"))
    markdown = Path(str(written["summary_markdown_path"])).read_text(encoding="utf-8")
    assert payload["evidence_id"] == "synthetic-example"
    assert payload["equivalence_status"] == "pass"
    assert "# Modelwright Validation Evidence: synthetic-example" in markdown
    assert "Equivalence status: `pass`" in markdown


def test_matrix_evidence_aggregates_pass_and_fail_cases(tmp_path: Path) -> None:
    matrix_run = tmp_path / "matrix-run.json"
    artifact_root = tmp_path / "artifacts"
    output_dir = tmp_path / "matrix-evidence"
    _write_matrix_run(matrix_run, cases=("output-columns", "headline-only"))
    _write_artifacts(
        artifact_root / "strategy" / "output-columns",
        comparison={"comparable_output_count": 2, "match_count": 2, "mismatch_count": 0},
    )
    _write_artifacts(
        artifact_root / "strategy" / "headline-only",
        comparison={"comparable_output_count": 2, "match_count": 1, "mismatch_count": 1},
    )
    paths = matrix_evidence_paths(
        evidence_id="strategy-matrix",
        matrix_run_path=matrix_run,
        artifact_root=artifact_root,
        output_dir=output_dir,
    )

    summary = extract_matrix_evidence(paths, require_evidence=True)

    assert summary.evidence_status == "complete"
    assert summary.equivalence_status == "fail"
    assert summary.case_count == 2
    assert summary.pass_count == 1
    assert summary.fail_count == 1
    assert [case.case_id for case in summary.cases] == ["output-columns", "headline-only"]
    assert summary.cases[0].comparable_output_count == 2
    assert summary.cases[1].mismatch_count == 1


def test_matrix_evidence_marks_missing_case_evidence_skipped(tmp_path: Path) -> None:
    matrix_run = tmp_path / "matrix-run.json"
    _write_matrix_run(matrix_run, cases=("output-columns",))

    summary = extract_matrix_evidence(matrix_run_path=matrix_run, artifact_root=tmp_path / "missing")

    assert summary.evidence_status == "skipped"
    assert summary.equivalence_status == "incomplete"
    assert summary.cases[0].evidence_status == "skipped"
    assert "No per-case evidence" in summary.cases[0].notes[0]


def test_matrix_evidence_missing_case_can_be_required(tmp_path: Path) -> None:
    matrix_run = tmp_path / "matrix-run.json"
    _write_matrix_run(matrix_run, cases=("output-columns",))

    with pytest.raises(FileNotFoundError, match="missing matrix case evidence"):
        extract_matrix_evidence(matrix_run_path=matrix_run, artifact_root=tmp_path / "missing", require_evidence=True)


def test_write_matrix_evidence_writes_sanitized_json_and_markdown(tmp_path: Path) -> None:
    matrix_run = tmp_path / "matrix-run.json"
    artifact_root = tmp_path / "artifacts"
    paths = matrix_evidence_paths(
        evidence_id="strategy-matrix",
        matrix_run_path=matrix_run,
        artifact_root=artifact_root,
        output_dir=tmp_path / "matrix-evidence",
    )
    _write_matrix_run(matrix_run, cases=("output-columns",))
    _write_artifacts(
        artifact_root / "strategy" / "output-columns",
        comparison_rows=[{"cell_ref": "Summary!B2", "matches": True, "generated": "generated secret"}],
    )

    summary = extract_matrix_evidence(paths)
    written = write_matrix_evidence(summary, paths)

    payload = Path(str(written["summary_json_path"])).read_text(encoding="utf-8")
    markdown = Path(str(written["summary_markdown_path"])).read_text(encoding="utf-8")
    assert "strategy-matrix" in payload
    assert "# Modelwright Matrix Evidence: strategy-matrix" in markdown
    assert "source_code" not in payload
    assert "output_values" not in payload
    assert "Summary!B2" not in payload
    assert "generated secret" not in payload


def _write_artifacts(
    artifact_dir: Path,
    *,
    comparison: dict[str, int] | None = None,
    comparison_rows: list[dict[str, object]] | None = None,
    include_report: bool = True,
) -> None:
    artifact_dir.mkdir(parents=True, exist_ok=True)
    _write_json(
        artifact_dir / "inference-result.json",
        {
            "inferred": True,
            "contract": {
                "input_refs": ["Inputs!B2"],
                "output_refs": ["Summary!B2", "Summary!B3"],
                "symbols": {"Inputs!B2": {}, "Summary!B2": {}, "Summary!B3": {}},
            },
            "expressions": {"Summary!B2": {}, "Summary!B3": {}},
            "constants": {"Inputs!B2": 5},
            "diagnostics": [],
        },
    )
    _write_json(
        artifact_dir / "generation-result.json",
        {
            "generated": True,
            "contract": {"input_refs": ["Inputs!B2"], "output_refs": ["Summary!B2", "Summary!B3"], "symbols": {}},
            "source_code": "def calculate(inputs=None):\n    return {'Summary!B2': 'generated secret'}\n",
            "diagnostics": [],
        },
    )
    _write_json(
        artifact_dir / "generated-values.json",
        {
            "executed": True,
            "contract": {"output_refs": ["Summary!B2", "Summary!B3"]},
            "output_values": {"Summary!B2": "generated secret", "Summary!B3": 12},
            "diagnostics": [],
        },
    )
    _write_json(
        artifact_dir / "validation-scenario.json",
        {
            "scenario_id": "baseline",
            "inputs": [{"cell_ref": "Inputs!B2", "kind": "number", "value": 5}],
            "outputs": [
                {"cell_ref": "Summary!B2", "kind": "text"},
                {"cell_ref": "Summary!B3", "kind": "number"},
            ],
        },
    )
    report = None
    if include_report:
        report = {
            "scenario_id": "baseline",
            "oracle_backend": "cached_workbook",
            "status": "fail" if comparison_rows else "pass",
            "diagnostics": [],
        }
        if comparison_rows is not None:
            report["comparisons"] = comparison_rows
            report["mismatches"] = [row for row in comparison_rows if row.get("matches") is False]
        elif comparison is not None:
            report["comparison"] = comparison
    _write_json(
        artifact_dir / "evaluation-report.json",
        {
            "scenario_id": "baseline",
            "generated_execution": {
                "executed": True,
                "output_values": {"Summary!B2": "generated secret"},
                "diagnostics": [],
            },
            "cached_validation_report": report,
            "oracle_validation_report": None,
            "diagnostics": [],
        },
    )


def _write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _write_matrix_run(path: Path, *, cases: tuple[str, ...]) -> None:
    path.write_text(
        json.dumps(
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
                        for case_id in cases
                    ],
                    "diagnostics": [],
                },
                "summary": {
                    "matrix_id": "strategy",
                    "status": "success",
                    "case_count": len(cases),
                    "succeeded_count": len(cases),
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
                        for case_id in cases
                    ],
                },
            },
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )
