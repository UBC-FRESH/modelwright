"""Compact validation-evidence summaries for generated-model workflows.

This module summarizes artifacts that were already produced by Modelwright
generation, execution, and validation steps. It deliberately does not rerun
those steps, and it does not copy raw generated source, raw generated output
values, workbook contents, or full comparison rows into the shareable summary.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

JsonValue = str | int | float | bool | None | list[Any] | dict[str, Any]
EvidenceStatus = Literal["skipped", "incomplete", "complete"]
EquivalenceStatus = Literal["pass", "fail", "incomplete"]


@dataclass(frozen=True)
class ValidationEvidencePaths:
    """Filesystem contract for compact validation-evidence extraction."""

    evidence_id: str
    artifact_dir: Path
    output_dir: Path
    inference_result_path: Path
    generation_result_path: Path
    generated_values_path: Path
    validation_scenario_path: Path
    evaluation_report_path: Path
    summary_json_path: Path
    summary_markdown_path: Path

    @property
    def required_artifact_paths(self) -> tuple[Path, ...]:
        """Return artifacts used as evidence inputs."""

        return (
            self.inference_result_path,
            self.generation_result_path,
            self.generated_values_path,
            self.validation_scenario_path,
            self.evaluation_report_path,
        )


@dataclass(frozen=True)
class ValidationEvidenceSummary:
    """Sanitized validation-evidence summary for publication or CI artifacts."""

    evidence_id: str
    evidence_status: EvidenceStatus
    equivalence_status: EquivalenceStatus
    missing_artifacts: tuple[str, ...] = field(default_factory=tuple)
    artifacts: dict[str, str] = field(default_factory=dict)
    stages: dict[str, JsonValue] = field(default_factory=dict)
    comparison: dict[str, JsonValue] = field(default_factory=dict)
    notes: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, JsonValue]:
        """Serialize the compact evidence summary."""

        return {
            "evidence_id": self.evidence_id,
            "evidence_status": self.evidence_status,
            "equivalence_status": self.equivalence_status,
            "missing_artifacts": list(self.missing_artifacts),
            "artifacts": self.artifacts,
            "stages": self.stages,
            "comparison": self.comparison,
            "notes": list(self.notes),
        }


@dataclass(frozen=True)
class MatrixEvidencePaths:
    """Filesystem contract for compact matrix-evidence aggregation."""

    evidence_id: str
    output_dir: Path
    matrix_run_path: Path | None = None
    matrix_summary_path: Path | None = None
    artifact_root: Path | None = None
    summary_json_path: Path | None = None
    summary_markdown_path: Path | None = None

    def __post_init__(self) -> None:
        if self.matrix_run_path is None and self.matrix_summary_path is None:
            raise ValueError("matrix_run_path or matrix_summary_path is required")
        if self.summary_json_path is None:
            object.__setattr__(self, "summary_json_path", self.output_dir / "summary.json")
        if self.summary_markdown_path is None:
            object.__setattr__(self, "summary_markdown_path", self.output_dir / "summary.md")


@dataclass(frozen=True)
class MatrixEvidenceCaseSummary:
    """Sanitized generated-model evidence summary for one matrix case."""

    case_id: str
    namespace: str | None
    run_status: str | None
    evidence_status: EvidenceStatus
    equivalence_status: EquivalenceStatus
    comparable_output_count: int | None = None
    match_count: int | None = None
    mismatch_count: int | None = None
    diagnostic_count: int = 0
    error_count: int = 0
    warning_count: int = 0
    artifact_dir: str | None = None
    evidence_source: str = "missing"
    notes: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, JsonValue]:
        """Serialize the compact matrix case summary."""

        return {
            "case_id": self.case_id,
            "namespace": self.namespace,
            "run_status": self.run_status,
            "evidence_status": self.evidence_status,
            "equivalence_status": self.equivalence_status,
            "comparable_output_count": self.comparable_output_count,
            "match_count": self.match_count,
            "mismatch_count": self.mismatch_count,
            "diagnostic_count": self.diagnostic_count,
            "error_count": self.error_count,
            "warning_count": self.warning_count,
            "artifact_dir": self.artifact_dir,
            "evidence_source": self.evidence_source,
            "notes": list(self.notes),
        }


@dataclass(frozen=True)
class MatrixEvidenceSummary:
    """Sanitized generated-model evidence summary for a FreshForge matrix."""

    evidence_id: str
    matrix_id: str | None
    evidence_status: EvidenceStatus
    equivalence_status: EquivalenceStatus
    case_count: int
    complete_count: int
    incomplete_count: int
    skipped_count: int
    pass_count: int
    fail_count: int
    diagnostic_count: int = 0
    error_count: int = 0
    warning_count: int = 0
    artifacts: dict[str, str] = field(default_factory=dict)
    cases: tuple[MatrixEvidenceCaseSummary, ...] = field(default_factory=tuple)
    notes: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, JsonValue]:
        """Serialize the compact matrix evidence summary."""

        return {
            "evidence_id": self.evidence_id,
            "matrix_id": self.matrix_id,
            "evidence_status": self.evidence_status,
            "equivalence_status": self.equivalence_status,
            "case_count": self.case_count,
            "complete_count": self.complete_count,
            "incomplete_count": self.incomplete_count,
            "skipped_count": self.skipped_count,
            "pass_count": self.pass_count,
            "fail_count": self.fail_count,
            "diagnostic_count": self.diagnostic_count,
            "error_count": self.error_count,
            "warning_count": self.warning_count,
            "artifacts": self.artifacts,
            "cases": [case.to_dict() for case in self.cases],
            "notes": list(self.notes),
        }


def validation_evidence_paths(
    *,
    evidence_id: str = "generated-model",
    artifact_dir: str | Path | None = None,
    output_dir: str | Path | None = None,
    validation_scenario_path: str | Path | None = None,
) -> ValidationEvidencePaths:
    """Build the generic path contract for validation-evidence extraction."""

    artifact_root = Path(artifact_dir) if artifact_dir is not None else Path("tmp/generated-model")
    output_root = Path(output_dir) if output_dir is not None else Path("tmp/validation-evidence") / evidence_id
    scenario_path = (
        Path(validation_scenario_path) if validation_scenario_path is not None else artifact_root / "validation-scenario.json"
    )
    return ValidationEvidencePaths(
        evidence_id=evidence_id,
        artifact_dir=artifact_root,
        output_dir=output_root,
        inference_result_path=artifact_root / "inference-result.json",
        generation_result_path=artifact_root / "generation-result.json",
        generated_values_path=artifact_root / "generated-values.json",
        validation_scenario_path=scenario_path,
        evaluation_report_path=artifact_root / "evaluation-report.json",
        summary_json_path=output_root / "summary.json",
        summary_markdown_path=output_root / "summary.md",
    )


def matrix_evidence_paths(
    *,
    evidence_id: str = "generated-model-matrix",
    output_dir: str | Path | None = None,
    matrix_run_path: str | Path | None = None,
    matrix_summary_path: str | Path | None = None,
    artifact_root: str | Path | None = None,
) -> MatrixEvidencePaths:
    """Build the generic path contract for matrix evidence aggregation."""

    output_root = Path(output_dir) if output_dir is not None else Path("tmp/validation-evidence") / evidence_id
    return MatrixEvidencePaths(
        evidence_id=evidence_id,
        output_dir=output_root,
        matrix_run_path=Path(matrix_run_path) if matrix_run_path is not None else None,
        matrix_summary_path=Path(matrix_summary_path) if matrix_summary_path is not None else None,
        artifact_root=Path(artifact_root) if artifact_root is not None else None,
    )


def extract_validation_evidence(
    paths: ValidationEvidencePaths | None = None,
    *,
    evidence_id: str = "generated-model",
    artifact_dir: str | Path | None = None,
    output_dir: str | Path | None = None,
    validation_scenario_path: str | Path | None = None,
    require_artifacts: bool = False,
) -> ValidationEvidenceSummary:
    """Extract compact evidence from existing generated-model workflow artifacts."""

    evidence_paths = paths or validation_evidence_paths(
        evidence_id=evidence_id,
        artifact_dir=artifact_dir,
        output_dir=output_dir,
        validation_scenario_path=validation_scenario_path,
    )
    missing = tuple(str(path) for path in evidence_paths.required_artifact_paths if not path.exists())
    if missing and require_artifacts:
        missing_list = ", ".join(missing)
        raise FileNotFoundError(f"missing validation evidence artifact(s): {missing_list}")

    artifacts = _artifact_summary(evidence_paths)
    if missing:
        return ValidationEvidenceSummary(
            evidence_id=evidence_paths.evidence_id,
            evidence_status="skipped",
            equivalence_status="incomplete",
            missing_artifacts=missing,
            artifacts=artifacts,
            notes=("Validation artifacts are missing; evidence extraction was skipped.",),
        )

    inference = _load_json_object(evidence_paths.inference_result_path)
    generation = _load_json_object(evidence_paths.generation_result_path)
    generated_values = _load_json_object(evidence_paths.generated_values_path)
    scenario = _load_json_object(evidence_paths.validation_scenario_path)
    evaluation = _load_json_object(evidence_paths.evaluation_report_path)

    stages: dict[str, JsonValue] = {
        "inference": _inference_stage(inference),
        "generation": _generation_stage(generation),
        "generated_values": _generated_values_stage(generated_values),
        "validation_scenario": _validation_scenario_stage(scenario),
        "evaluation": _evaluation_stage(evaluation),
    }
    comparison = _comparison_summary(evaluation)
    equivalence_status = _equivalence_status(comparison)
    evidence_status: EvidenceStatus = "complete" if equivalence_status in {"pass", "fail"} else "incomplete"
    notes = _summary_notes(missing=(), stages=stages, comparison=comparison)
    return ValidationEvidenceSummary(
        evidence_id=evidence_paths.evidence_id,
        evidence_status=evidence_status,
        equivalence_status=equivalence_status,
        artifacts=artifacts,
        stages=stages,
        comparison=comparison,
        notes=notes,
    )


def extract_matrix_evidence(
    paths: MatrixEvidencePaths | None = None,
    *,
    evidence_id: str = "generated-model-matrix",
    matrix_run_path: str | Path | None = None,
    matrix_summary_path: str | Path | None = None,
    artifact_root: str | Path | None = None,
    output_dir: str | Path | None = None,
    require_evidence: bool = False,
) -> MatrixEvidenceSummary:
    """Aggregate compact evidence from an existing FreshForge matrix run or summary."""

    evidence_paths = paths or matrix_evidence_paths(
        evidence_id=evidence_id,
        matrix_run_path=matrix_run_path,
        matrix_summary_path=matrix_summary_path,
        artifact_root=artifact_root,
        output_dir=output_dir,
    )
    payload = _load_matrix_payload(evidence_paths)
    matrix = _matrix_summary_object(payload)
    cases = tuple(
        _matrix_case_summary(
            evidence_paths=evidence_paths,
            case=_object(case),
            require_evidence=require_evidence,
        )
        for case in _sequence(matrix.get("cases"))
    )
    if not cases and require_evidence:
        raise FileNotFoundError("matrix evidence contains no cases")

    evidence_status = _matrix_evidence_status(cases)
    equivalence_status = _matrix_equivalence_status(cases)
    artifacts = _matrix_artifact_summary(evidence_paths)
    notes = _matrix_notes(cases)
    return MatrixEvidenceSummary(
        evidence_id=evidence_paths.evidence_id,
        matrix_id=_string(matrix.get("matrix_id")) or _string(_object(payload.get("run")).get("matrix_id")),
        evidence_status=evidence_status,
        equivalence_status=equivalence_status,
        case_count=len(cases),
        complete_count=sum(1 for case in cases if case.evidence_status == "complete"),
        incomplete_count=sum(1 for case in cases if case.evidence_status == "incomplete"),
        skipped_count=sum(1 for case in cases if case.evidence_status == "skipped"),
        pass_count=sum(1 for case in cases if case.equivalence_status == "pass"),
        fail_count=sum(1 for case in cases if case.equivalence_status == "fail"),
        diagnostic_count=sum(case.diagnostic_count for case in cases),
        error_count=sum(case.error_count for case in cases),
        warning_count=sum(case.warning_count for case in cases),
        artifacts=artifacts,
        cases=cases,
        notes=notes,
    )


def write_validation_evidence(
    summary: ValidationEvidenceSummary,
    paths: ValidationEvidencePaths | None = None,
    *,
    output_dir: str | Path | None = None,
) -> dict[str, JsonValue]:
    """Write ``summary.json`` and ``summary.md`` for compact evidence."""

    if paths is not None:
        json_path = paths.summary_json_path
        markdown_path = paths.summary_markdown_path
    else:
        output_root = Path(output_dir) if output_dir is not None else Path("tmp/validation-evidence") / summary.evidence_id
        json_path = output_root / "summary.json"
        markdown_path = output_root / "summary.md"

    json_path.parent.mkdir(parents=True, exist_ok=True)
    payload = summary.to_dict()
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    markdown_path.write_text(_summary_markdown(summary), encoding="utf-8")
    return {
        "summary": payload,
        "summary_json_path": str(json_path),
        "summary_markdown_path": str(markdown_path),
    }


def write_matrix_evidence(
    summary: MatrixEvidenceSummary,
    paths: MatrixEvidencePaths | None = None,
    *,
    output_dir: str | Path | None = None,
) -> dict[str, JsonValue]:
    """Write compact matrix evidence ``summary.json`` and ``summary.md``."""

    if paths is not None:
        json_path = paths.summary_json_path or paths.output_dir / "summary.json"
        markdown_path = paths.summary_markdown_path or paths.output_dir / "summary.md"
    else:
        output_root = Path(output_dir) if output_dir is not None else Path("tmp/validation-evidence") / summary.evidence_id
        json_path = output_root / "summary.json"
        markdown_path = output_root / "summary.md"

    json_path.parent.mkdir(parents=True, exist_ok=True)
    payload = summary.to_dict()
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    markdown_path.write_text(_matrix_summary_markdown(summary), encoding="utf-8")
    return {
        "summary": payload,
        "summary_json_path": str(json_path),
        "summary_markdown_path": str(markdown_path),
    }


def _artifact_summary(paths: ValidationEvidencePaths) -> dict[str, str]:
    return {
        "artifact_dir": str(paths.artifact_dir),
        "inference_result": str(paths.inference_result_path),
        "generation_result": str(paths.generation_result_path),
        "generated_values": str(paths.generated_values_path),
        "validation_scenario": str(paths.validation_scenario_path),
        "evaluation_report": str(paths.evaluation_report_path),
        "summary_json": str(paths.summary_json_path),
        "summary_markdown": str(paths.summary_markdown_path),
    }


def _inference_stage(data: dict[str, JsonValue]) -> dict[str, JsonValue]:
    contract = _object(data.get("contract"))
    return {
        "available": True,
        "inferred": bool(data.get("inferred", False)),
        "input_ref_count": _length(contract.get("input_refs")),
        "output_ref_count": _length(contract.get("output_refs")),
        "symbol_count": _length(contract.get("symbols")),
        "expression_count": _length(data.get("expressions")),
        "constant_count": _length(data.get("constants")),
        "diagnostic_count": _diagnostic_count(data),
        "error_diagnostic_count": _diagnostic_count(data, severity="error"),
    }


def _generation_stage(data: dict[str, JsonValue]) -> dict[str, JsonValue]:
    contract = _object(data.get("contract"))
    source_code = data.get("source_code")
    source_size = len(source_code.encode("utf-8")) if isinstance(source_code, str) else None
    source_lines = source_code.count("\n") + 1 if isinstance(source_code, str) and source_code else None
    return {
        "available": True,
        "generated": bool(data.get("generated", False)),
        "input_ref_count": _length(contract.get("input_refs")),
        "output_ref_count": _length(contract.get("output_refs")),
        "symbol_count": _length(contract.get("symbols")),
        "source_size_bytes": source_size,
        "source_line_count": source_lines,
        "diagnostic_count": _diagnostic_count(data),
        "error_diagnostic_count": _diagnostic_count(data, severity="error"),
    }


def _generated_values_stage(data: dict[str, JsonValue]) -> dict[str, JsonValue]:
    contract = _object(data.get("contract"))
    output_values = _object(data.get("output_values"))
    return {
        "available": True,
        "executed": bool(data.get("executed", False)),
        "declared_output_count": _length(contract.get("output_refs")),
        "generated_output_count": len(output_values),
        "diagnostic_count": _diagnostic_count(data),
        "error_diagnostic_count": _diagnostic_count(data, severity="error"),
    }


def _validation_scenario_stage(data: dict[str, JsonValue]) -> dict[str, JsonValue]:
    outputs = _sequence(data.get("outputs"))
    output_kinds = sorted(
        {item.get("kind") for item in outputs if isinstance(item, dict) and isinstance(item.get("kind"), str)}
    )
    return {
        "available": True,
        "scenario_id": data.get("scenario_id"),
        "input_count": _length(data.get("inputs")),
        "output_count": len(outputs),
        "output_kinds": output_kinds,
    }


def _evaluation_stage(data: dict[str, JsonValue]) -> dict[str, JsonValue]:
    generated_execution = _object(data.get("generated_execution"))
    cached_report = _object(data.get("cached_validation_report"))
    oracle_report = _object(data.get("oracle_validation_report"))
    return {
        "available": True,
        "scenario_id": data.get("scenario_id"),
        "generated_executed": bool(generated_execution.get("executed", False)),
        "generated_output_count": _length(generated_execution.get("output_values")),
        "has_cached_validation_report": bool(cached_report),
        "has_oracle_validation_report": bool(oracle_report),
        "cached_validation_status": cached_report.get("status"),
        "oracle_validation_status": oracle_report.get("status"),
        "diagnostic_count": _diagnostic_count(data),
        "error_diagnostic_count": _diagnostic_count(data, severity="error"),
    }


def _comparison_summary(evaluation: dict[str, JsonValue]) -> dict[str, JsonValue]:
    reports = [
        _object(evaluation.get("cached_validation_report")),
        _object(evaluation.get("oracle_validation_report")),
    ]
    report = next((item for item in reports if item), None)
    if report is None:
        return {
            "comparison_counts_available": False,
            "comparable_output_count": None,
            "match_count": None,
            "mismatch_count": None,
            "validation_report_status": None,
            "validation_backend": None,
        }

    comparisons = _sequence(report.get("comparisons"))
    mismatches = _sequence(report.get("mismatches"))
    comparable_count = _find_count(report, _COMPARABLE_KEYS)
    match_count = _find_count(report, _MATCH_KEYS)
    mismatch_count = _find_count(report, _MISMATCH_KEYS)
    if comparable_count is None and comparisons:
        comparable_count = len(comparisons)
    if match_count is None and comparisons:
        match_count = sum(1 for item in comparisons if isinstance(item, dict) and item.get("matches") is True)
    if mismatch_count is None and (comparisons or mismatches):
        mismatch_count = len(mismatches) if mismatches else sum(
            1 for item in comparisons if isinstance(item, dict) and item.get("matches") is False
        )

    counts_available = comparable_count is not None and match_count is not None and mismatch_count is not None
    return {
        "comparison_counts_available": counts_available,
        "comparable_output_count": comparable_count,
        "match_count": match_count,
        "mismatch_count": mismatch_count,
        "validation_report_status": report.get("status"),
        "validation_backend": report.get("oracle_backend"),
        "validation_diagnostic_count": _diagnostic_count(report),
        "validation_error_diagnostic_count": _diagnostic_count(report, severity="error"),
    }


def _equivalence_status(comparison: dict[str, JsonValue]) -> EquivalenceStatus:
    comparable = comparison.get("comparable_output_count")
    matches = comparison.get("match_count")
    mismatches = comparison.get("mismatch_count")
    if not all(isinstance(value, int) and not isinstance(value, bool) for value in (comparable, matches, mismatches)):
        return "incomplete"
    if comparable == matches and mismatches == 0:
        return "pass"
    return "fail"


def _summary_notes(
    *,
    missing: tuple[str, ...],
    stages: dict[str, JsonValue],
    comparison: dict[str, JsonValue],
) -> tuple[str, ...]:
    notes: list[str] = []
    if missing:
        notes.append("Validation artifacts are missing; evidence extraction was skipped.")
    if comparison.get("comparison_counts_available") is not True:
        notes.append("Explicit comparable-output, match, and mismatch counts were not found.")
    diagnostics = sum(
        int(stage.get("diagnostic_count", 0))
        for stage in stages.values()
        if isinstance(stage, dict) and isinstance(stage.get("diagnostic_count"), int)
    )
    if diagnostics:
        notes.append(f"Stage diagnostics were reported: {diagnostics}.")
    return tuple(notes)


def _summary_markdown(summary: ValidationEvidenceSummary) -> str:
    comparison = summary.comparison
    lines = [
        f"# Modelwright Validation Evidence: {summary.evidence_id}",
        "",
        f"- Evidence status: `{summary.evidence_status}`",
        f"- Equivalence status: `{summary.equivalence_status}`",
        f"- Comparable outputs: `{comparison.get('comparable_output_count')}`",
        f"- Matches: `{comparison.get('match_count')}`",
        f"- Mismatches: `{comparison.get('mismatch_count')}`",
        "",
        "## Artifacts",
        "",
    ]
    for key, path in summary.artifacts.items():
        lines.append(f"- `{key}`: `{path}`")
    if summary.missing_artifacts:
        lines.extend(["", "## Missing Artifacts", ""])
        lines.extend(f"- `{path}`" for path in summary.missing_artifacts)
    if summary.notes:
        lines.extend(["", "## Notes", ""])
        lines.extend(f"- {note}" for note in summary.notes)
    lines.append("")
    return "\n".join(lines)


def _load_matrix_payload(paths: MatrixEvidencePaths) -> dict[str, JsonValue]:
    if paths.matrix_run_path is not None:
        return _load_json_object(paths.matrix_run_path)
    if paths.matrix_summary_path is not None:
        return _load_json_object(paths.matrix_summary_path)
    raise ValueError("matrix_run_path or matrix_summary_path is required")


def _matrix_summary_object(payload: dict[str, JsonValue]) -> dict[str, JsonValue]:
    summary = _object(payload.get("summary"))
    if summary:
        return summary
    if "cases" in payload:
        return payload
    run = _object(payload.get("run"))
    if run:
        return run
    return {}


def _matrix_case_summary(
    *,
    evidence_paths: MatrixEvidencePaths,
    case: dict[str, JsonValue],
    require_evidence: bool,
) -> MatrixEvidenceCaseSummary:
    case_id = _case_id(case)
    namespace = _case_namespace(case)
    run_status = _string(case.get("status")) or _string(_object(case.get("summary")).get("status"))
    diagnostic_count = _int(case.get("diagnostic_count")) or _diagnostic_count(case)
    error_count = _int(case.get("error_count")) or _diagnostic_count(case, severity="error")
    warning_count = _int(case.get("warning_count")) or _diagnostic_count(case, severity="warning")

    evidence = _case_validation_evidence(
        evidence_paths=evidence_paths,
        case_id=case_id,
        namespace=namespace,
        require_evidence=require_evidence,
    )
    if evidence is None:
        if require_evidence:
            raise FileNotFoundError(f"missing matrix case evidence for {case_id}")
        return MatrixEvidenceCaseSummary(
            case_id=case_id,
            namespace=namespace,
            run_status=run_status,
            evidence_status="skipped",
            equivalence_status="incomplete",
            diagnostic_count=diagnostic_count,
            error_count=error_count,
            warning_count=warning_count,
            notes=("No per-case evidence directory was found.",),
        )

    comparison = evidence.comparison
    return MatrixEvidenceCaseSummary(
        case_id=case_id,
        namespace=namespace,
        run_status=run_status,
        evidence_status=evidence.evidence_status,
        equivalence_status=evidence.equivalence_status,
        comparable_output_count=_int(comparison.get("comparable_output_count")),
        match_count=_int(comparison.get("match_count")),
        mismatch_count=_int(comparison.get("mismatch_count")),
        diagnostic_count=diagnostic_count + _stage_diagnostic_count(evidence.stages),
        error_count=error_count + _stage_diagnostic_count(evidence.stages, key="error_diagnostic_count"),
        warning_count=warning_count,
        artifact_dir=evidence.artifacts.get("artifact_dir"),
        evidence_source="validation-summary" if _loaded_from_summary(evidence) else "artifact-extraction",
        notes=evidence.notes,
    )


def _case_validation_evidence(
    *,
    evidence_paths: MatrixEvidencePaths,
    case_id: str,
    namespace: str | None,
    require_evidence: bool,
) -> ValidationEvidenceSummary | None:
    if evidence_paths.artifact_root is None:
        return None
    for artifact_dir in _candidate_case_dirs(evidence_paths.artifact_root, case_id, namespace):
        summary_path = artifact_dir / "summary.json"
        if summary_path.exists():
            return _validation_summary_from_dict(_load_json_object(summary_path))
        if artifact_dir.exists():
            paths = validation_evidence_paths(
                evidence_id=f"{evidence_paths.evidence_id}:{case_id}",
                artifact_dir=artifact_dir,
                output_dir=artifact_dir / "validation-evidence",
            )
            return extract_validation_evidence(paths, require_artifacts=require_evidence)
    return None


def _candidate_case_dirs(artifact_root: Path, case_id: str, namespace: str | None) -> tuple[Path, ...]:
    candidates = [artifact_root / case_id]
    if namespace:
        namespace_path = Path(namespace)
        if not namespace_path.is_absolute() and ".." not in namespace_path.parts:
            candidates.append(artifact_root / namespace_path)
    unique: list[Path] = []
    for candidate in candidates:
        if candidate not in unique:
            unique.append(candidate)
    return tuple(unique)


def _validation_summary_from_dict(data: dict[str, JsonValue]) -> ValidationEvidenceSummary:
    return ValidationEvidenceSummary(
        evidence_id=_string(data.get("evidence_id")) or "generated-model",
        evidence_status=_evidence_status(data.get("evidence_status")),
        equivalence_status=_equivalence_value(data.get("equivalence_status")),
        missing_artifacts=tuple(str(item) for item in _sequence(data.get("missing_artifacts"))),
        artifacts={str(key): str(value) for key, value in _object(data.get("artifacts")).items()},
        stages=_object(data.get("stages")),
        comparison=_object(data.get("comparison")),
        notes=tuple(str(item) for item in _sequence(data.get("notes"))),
    )


def _loaded_from_summary(summary: ValidationEvidenceSummary) -> bool:
    return "summary_json" in summary.artifacts or "summary_markdown" in summary.artifacts


def _case_id(case: dict[str, JsonValue]) -> str:
    case_id = _string(case.get("case_id")) or _string(case.get("id"))
    if case_id:
        return case_id
    namespace = _case_namespace(case)
    if namespace:
        return namespace.strip("/").split("/")[-1]
    workflow_id = _string(case.get("workflow_id"))
    return workflow_id or "unknown-case"


def _case_namespace(case: dict[str, JsonValue]) -> str | None:
    return _string(case.get("namespace")) or _string(case.get("run_namespace"))


def _matrix_evidence_status(cases: tuple[MatrixEvidenceCaseSummary, ...]) -> EvidenceStatus:
    if not cases or all(case.evidence_status == "skipped" for case in cases):
        return "skipped"
    if all(case.evidence_status == "complete" for case in cases):
        return "complete"
    return "incomplete"


def _matrix_equivalence_status(cases: tuple[MatrixEvidenceCaseSummary, ...]) -> EquivalenceStatus:
    if not cases:
        return "incomplete"
    if any(case.equivalence_status == "fail" for case in cases):
        return "fail"
    if all(case.equivalence_status == "pass" for case in cases):
        return "pass"
    return "incomplete"


def _matrix_artifact_summary(paths: MatrixEvidencePaths) -> dict[str, str]:
    artifacts = {
        "output_dir": str(paths.output_dir),
        "summary_json": str(paths.summary_json_path or paths.output_dir / "summary.json"),
        "summary_markdown": str(paths.summary_markdown_path or paths.output_dir / "summary.md"),
    }
    if paths.matrix_run_path is not None:
        artifacts["matrix_run"] = str(paths.matrix_run_path)
    if paths.matrix_summary_path is not None:
        artifacts["matrix_summary"] = str(paths.matrix_summary_path)
    if paths.artifact_root is not None:
        artifacts["artifact_root"] = str(paths.artifact_root)
    return artifacts


def _matrix_notes(cases: tuple[MatrixEvidenceCaseSummary, ...]) -> tuple[str, ...]:
    notes: list[str] = []
    if not cases:
        notes.append("Matrix evidence contained no cases.")
    if any(case.evidence_status == "skipped" for case in cases):
        notes.append("One or more matrix cases had no available generated-model evidence.")
    if any(case.evidence_status == "incomplete" for case in cases):
        notes.append("One or more matrix cases lacked explicit comparable/match/mismatch counts.")
    if any(case.equivalence_status == "fail" for case in cases):
        notes.append("One or more matrix cases reported explicit validation mismatches.")
    return tuple(notes)


def _matrix_summary_markdown(summary: MatrixEvidenceSummary) -> str:
    lines = [
        f"# Modelwright Matrix Evidence: {summary.evidence_id}",
        "",
        f"- Matrix id: `{summary.matrix_id}`",
        f"- Evidence status: `{summary.evidence_status}`",
        f"- Equivalence status: `{summary.equivalence_status}`",
        f"- Cases: `{summary.case_count}`",
        f"- Complete cases: `{summary.complete_count}`",
        f"- Passing cases: `{summary.pass_count}`",
        f"- Failing cases: `{summary.fail_count}`",
        "",
        "## Cases",
        "",
        "| Case | Namespace | Evidence | Equivalence | Comparable | Matches | Mismatches |",
        "| --- | --- | --- | --- | ---: | ---: | ---: |",
    ]
    for case in summary.cases:
        lines.append(
            "| "
            f"`{case.case_id}` | "
            f"`{case.namespace}` | "
            f"`{case.evidence_status}` | "
            f"`{case.equivalence_status}` | "
            f"`{case.comparable_output_count}` | "
            f"`{case.match_count}` | "
            f"`{case.mismatch_count}` |"
        )
    if summary.notes:
        lines.extend(["", "## Notes", ""])
        lines.extend(f"- {note}" for note in summary.notes)
    lines.append("")
    return "\n".join(lines)


def _load_json_object(path: Path) -> dict[str, JsonValue]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"expected JSON object in {path}")
    return data


def _object(value: JsonValue) -> dict[str, JsonValue]:
    return value if isinstance(value, dict) else {}


def _sequence(value: JsonValue) -> list[JsonValue]:
    return value if isinstance(value, list) else []


def _length(value: JsonValue) -> int | None:
    if isinstance(value, dict | list):
        return len(value)
    return None


def _string(value: JsonValue) -> str | None:
    return value if isinstance(value, str) and value else None


def _int(value: JsonValue) -> int | None:
    return value if isinstance(value, int) and not isinstance(value, bool) else None


def _evidence_status(value: JsonValue) -> EvidenceStatus:
    return value if value in {"skipped", "incomplete", "complete"} else "incomplete"  # type: ignore[return-value]


def _equivalence_value(value: JsonValue) -> EquivalenceStatus:
    return value if value in {"pass", "fail", "incomplete"} else "incomplete"  # type: ignore[return-value]


def _stage_diagnostic_count(stages: dict[str, JsonValue], *, key: str = "diagnostic_count") -> int:
    return sum(
        value
        for stage in stages.values()
        if isinstance(stage, dict) and isinstance((value := stage.get(key)), int) and not isinstance(value, bool)
    )


def _diagnostic_count(data: dict[str, JsonValue], *, severity: str | None = None) -> int:
    diagnostics = _sequence(data.get("diagnostics"))
    if severity is None:
        return len(diagnostics)
    return sum(1 for item in diagnostics if isinstance(item, dict) and item.get("severity") == severity)


_COMPARABLE_KEYS = ("comparable_output_count", "comparable_outputs", "total_comparable_outputs")
_MATCH_KEYS = ("match_count", "matches", "matched_outputs", "generated_output_matches")
_MISMATCH_KEYS = ("mismatch_count", "mismatches", "mismatched_outputs")


def _find_count(data: JsonValue, keys: tuple[str, ...]) -> int | None:
    if isinstance(data, dict):
        for key in keys:
            value = data.get(key)
            if isinstance(value, int) and not isinstance(value, bool):
                return value
        for value in data.values():
            found = _find_count(value, keys)
            if found is not None:
                return found
    elif isinstance(data, list):
        for item in data:
            found = _find_count(item, keys)
            if found is not None:
                return found
    return None
