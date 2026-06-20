"""Conversion plan records and assembly helpers."""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Literal

from sheetforge.extraction import WorkbookRecord
from sheetforge.formulas import FormulaExpression
from sheetforge.generation import GenerationResult
from sheetforge.graph import DependencyGraph
from sheetforge.validation import ValidationReport


JsonValue = str | int | float | bool | None | list[Any] | dict[str, Any]
BenchmarkRole = Literal[
    "primary_benchmark",
    "stress_benchmark",
    "broken_reference_regression",
    "synthetic_fixture",
    "ad_hoc_private",
]
StageStatus = Literal["pass", "blocked", "not_run"]
ValidationStatus = Literal["pass", "fail", "blocked", "not_run"]
OverallStatus = Literal["complete", "partial", "blocked"]
DiagnosticSeverity = Literal["info", "warning", "error"]
BlockerCategory = Literal[
    "source_workbook_defect",
    "unsupported_formula_semantics",
    "unsupported_reference_semantics",
    "graph_semantics",
    "generation_scope",
    "validation_oracle",
    "missing_cached_values",
    "external_dependency",
    "unknown",
]
BlockerDisposition = Literal["resolved", "blocked_by_design", "deferred", "out_of_scope", "next_target"]


@dataclass(frozen=True)
class ConversionSource:
    """Source workbook identity and benchmark role."""

    workbook_id: str
    file_type: str
    benchmark_role: BenchmarkRole
    source_path: str | None = None
    sanitized: bool = True

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ConversionSource":
        return cls(
            workbook_id=data["workbook_id"],
            file_type=data["file_type"],
            benchmark_role=data["benchmark_role"],
            source_path=data.get("source_path"),
            sanitized=data.get("sanitized", True),
        )

    def to_dict(self) -> dict[str, JsonValue]:
        return {
            "workbook_id": self.workbook_id,
            "file_type": self.file_type,
            "benchmark_role": self.benchmark_role,
            "source_path": self.source_path,
            "sanitized": self.sanitized,
        }


@dataclass(frozen=True)
class WorkflowStatus:
    """Stage-level conversion workflow status."""

    extraction: StageStatus = "not_run"
    dependency_graph: StageStatus = "not_run"
    formula_translation: StageStatus = "not_run"
    generation: StageStatus = "not_run"
    cached_validation: ValidationStatus = "not_run"
    oracle_validation: ValidationStatus = "not_run"
    overall: OverallStatus = "blocked"

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "WorkflowStatus":
        return cls(
            extraction=data.get("extraction", "not_run"),
            dependency_graph=data.get("dependency_graph", "not_run"),
            formula_translation=data.get("formula_translation", "not_run"),
            generation=data.get("generation", "not_run"),
            cached_validation=data.get("cached_validation", "not_run"),
            oracle_validation=data.get("oracle_validation", "not_run"),
            overall=data.get("overall", "blocked"),
        )

    def to_dict(self) -> dict[str, JsonValue]:
        return {
            "extraction": self.extraction,
            "dependency_graph": self.dependency_graph,
            "formula_translation": self.formula_translation,
            "generation": self.generation,
            "cached_validation": self.cached_validation,
            "oracle_validation": self.oracle_validation,
            "overall": self.overall,
        }


@dataclass(frozen=True)
class CoverageSummary:
    """Workbook coverage counts for conversion planning."""

    sheets: int
    cells: int
    value_cells: int
    formula_cells: int
    translated_formula_cells: int
    untranslated_formula_cells: int
    translation_coverage: float
    named_ranges: int
    dependency_edges: int
    semantic_edges: int
    execution_edges: int

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CoverageSummary":
        return cls(
            sheets=data["sheets"],
            cells=data["cells"],
            value_cells=data["value_cells"],
            formula_cells=data["formula_cells"],
            translated_formula_cells=data["translated_formula_cells"],
            untranslated_formula_cells=data["untranslated_formula_cells"],
            translation_coverage=data["translation_coverage"],
            named_ranges=data["named_ranges"],
            dependency_edges=data["dependency_edges"],
            semantic_edges=data["semantic_edges"],
            execution_edges=data["execution_edges"],
        )

    def to_dict(self) -> dict[str, JsonValue]:
        return {
            "sheets": self.sheets,
            "cells": self.cells,
            "value_cells": self.value_cells,
            "formula_cells": self.formula_cells,
            "translated_formula_cells": self.translated_formula_cells,
            "untranslated_formula_cells": self.untranslated_formula_cells,
            "translation_coverage": self.translation_coverage,
            "named_ranges": self.named_ranges,
            "dependency_edges": self.dependency_edges,
            "semantic_edges": self.semantic_edges,
            "execution_edges": self.execution_edges,
        }


@dataclass(frozen=True)
class DiagnosticSummary:
    """Diagnostic counts by workflow stage."""

    workbook_extraction: dict[str, int] = field(default_factory=dict)
    named_ranges: dict[str, int] = field(default_factory=dict)
    formula_extraction: dict[str, int] = field(default_factory=dict)
    graph: dict[str, int] = field(default_factory=dict)
    translation: dict[str, int] = field(default_factory=dict)
    generation: dict[str, int] = field(default_factory=dict)
    cached_validation: dict[str, int] = field(default_factory=dict)
    oracle_validation: dict[str, int] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DiagnosticSummary":
        return cls(
            workbook_extraction=dict(data.get("workbook_extraction", {})),
            named_ranges=dict(data.get("named_ranges", {})),
            formula_extraction=dict(data.get("formula_extraction", {})),
            graph=dict(data.get("graph", {})),
            translation=dict(data.get("translation", {})),
            generation=dict(data.get("generation", {})),
            cached_validation=dict(data.get("cached_validation", {})),
            oracle_validation=dict(data.get("oracle_validation", {})),
        )

    def to_dict(self) -> dict[str, JsonValue]:
        return {
            "workbook_extraction": self.workbook_extraction,
            "named_ranges": self.named_ranges,
            "formula_extraction": self.formula_extraction,
            "graph": self.graph,
            "translation": self.translation,
            "generation": self.generation,
            "cached_validation": self.cached_validation,
            "oracle_validation": self.oracle_validation,
        }


@dataclass(frozen=True)
class ResidualBlocker:
    """Classified residual blocker for conversion planning."""

    blocker_id: str
    category: BlockerCategory
    diagnostic_code: str
    item: str
    count: int
    severity: DiagnosticSeverity
    disposition: BlockerDisposition
    next_action: str
    provenance: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ResidualBlocker":
        return cls(
            blocker_id=data["blocker_id"],
            category=data["category"],
            diagnostic_code=data["diagnostic_code"],
            item=data["item"],
            count=data["count"],
            severity=data.get("severity", "warning"),
            disposition=data["disposition"],
            next_action=data["next_action"],
            provenance=data["provenance"],
        )

    def to_dict(self) -> dict[str, JsonValue]:
        return {
            "blocker_id": self.blocker_id,
            "category": self.category,
            "diagnostic_code": self.diagnostic_code,
            "item": self.item,
            "count": self.count,
            "severity": self.severity,
            "disposition": self.disposition,
            "next_action": self.next_action,
            "provenance": self.provenance,
        }


@dataclass(frozen=True)
class GenerationSummary:
    """Generated model summary for conversion planning."""

    generated: bool = False
    generated_model_path: str | None = None
    selected_outputs: int = 0
    selected_input_dependencies: int = 0
    selection_strategy: str = "not_run"
    full_workbook_model: bool = False

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "GenerationSummary":
        return cls(
            generated=data.get("generated", False),
            generated_model_path=data.get("generated_model_path"),
            selected_outputs=data.get("selected_outputs", 0),
            selected_input_dependencies=data.get("selected_input_dependencies", 0),
            selection_strategy=data.get("selection_strategy", "not_run"),
            full_workbook_model=data.get("full_workbook_model", False),
        )

    def to_dict(self) -> dict[str, JsonValue]:
        return {
            "generated": self.generated,
            "generated_model_path": self.generated_model_path,
            "selected_outputs": self.selected_outputs,
            "selected_input_dependencies": self.selected_input_dependencies,
            "selection_strategy": self.selection_strategy,
            "full_workbook_model": self.full_workbook_model,
        }


@dataclass(frozen=True)
class ValidationSummary:
    """Validation summary for generated outputs."""

    cached_validation_status: ValidationStatus = "not_run"
    cached_outputs: int = 0
    cached_mismatches: int = 0
    oracle_backend: str | None = None
    oracle_status: ValidationStatus = "not_run"
    oracle_mismatches: int = 0
    oracle_blockers: tuple[str, ...] = field(default_factory=tuple)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ValidationSummary":
        return cls(
            cached_validation_status=data.get("cached_validation_status", "not_run"),
            cached_outputs=data.get("cached_outputs", 0),
            cached_mismatches=data.get("cached_mismatches", 0),
            oracle_backend=data.get("oracle_backend"),
            oracle_status=data.get("oracle_status", "not_run"),
            oracle_mismatches=data.get("oracle_mismatches", 0),
            oracle_blockers=tuple(data.get("oracle_blockers", [])),
        )

    def to_dict(self) -> dict[str, JsonValue]:
        return {
            "cached_validation_status": self.cached_validation_status,
            "cached_outputs": self.cached_outputs,
            "cached_mismatches": self.cached_mismatches,
            "oracle_backend": self.oracle_backend,
            "oracle_status": self.oracle_status,
            "oracle_mismatches": self.oracle_mismatches,
            "oracle_blockers": list(self.oracle_blockers),
        }


@dataclass(frozen=True)
class PlanRecommendation:
    """Recommended next action from a conversion plan."""

    priority: int
    action: str
    rationale: str
    target_issue: int | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PlanRecommendation":
        return cls(
            priority=data["priority"],
            action=data["action"],
            rationale=data["rationale"],
            target_issue=data.get("target_issue"),
        )

    def to_dict(self) -> dict[str, JsonValue]:
        return {
            "priority": self.priority,
            "action": self.action,
            "rationale": self.rationale,
            "target_issue": self.target_issue,
        }


@dataclass(frozen=True)
class PrivacyReview:
    """Privacy flags for local or tracked conversion plans."""

    contains_source_path: bool = False
    contains_sheet_names: bool = False
    contains_named_ranges: bool = False
    contains_raw_formulas: bool = False
    contains_raw_cell_values: bool = False
    contains_generated_source: bool = False

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "PrivacyReview":
        return cls(
            contains_source_path=data.get("contains_source_path", False),
            contains_sheet_names=data.get("contains_sheet_names", False),
            contains_named_ranges=data.get("contains_named_ranges", False),
            contains_raw_formulas=data.get("contains_raw_formulas", False),
            contains_raw_cell_values=data.get("contains_raw_cell_values", False),
            contains_generated_source=data.get("contains_generated_source", False),
        )

    def to_dict(self) -> dict[str, JsonValue]:
        return {
            "contains_source_path": self.contains_source_path,
            "contains_sheet_names": self.contains_sheet_names,
            "contains_named_ranges": self.contains_named_ranges,
            "contains_raw_formulas": self.contains_raw_formulas,
            "contains_raw_cell_values": self.contains_raw_cell_values,
            "contains_generated_source": self.contains_generated_source,
        }


@dataclass(frozen=True)
class ConversionPlan:
    """Inspectable plan for partial or complete workbook conversion."""

    plan_id: str
    created_at: str
    sheetforge_commit: str
    source: ConversionSource
    workflow_status: WorkflowStatus
    coverage: CoverageSummary
    diagnostic_summary: DiagnosticSummary
    residual_blockers: tuple[ResidualBlocker, ...] = field(default_factory=tuple)
    generation: GenerationSummary = field(default_factory=GenerationSummary)
    validation: ValidationSummary = field(default_factory=ValidationSummary)
    recommendations: tuple[PlanRecommendation, ...] = field(default_factory=tuple)
    privacy_review: PrivacyReview = field(default_factory=PrivacyReview)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ConversionPlan":
        return cls(
            plan_id=data["plan_id"],
            created_at=data["created_at"],
            sheetforge_commit=data["sheetforge_commit"],
            source=ConversionSource.from_dict(data["source"]),
            workflow_status=WorkflowStatus.from_dict(data["workflow_status"]),
            coverage=CoverageSummary.from_dict(data["coverage"]),
            diagnostic_summary=DiagnosticSummary.from_dict(data["diagnostic_summary"]),
            residual_blockers=tuple(
                ResidualBlocker.from_dict(item) for item in data.get("residual_blockers", [])
            ),
            generation=GenerationSummary.from_dict(data.get("generation", {})),
            validation=ValidationSummary.from_dict(data.get("validation", {})),
            recommendations=tuple(
                PlanRecommendation.from_dict(item) for item in data.get("recommendations", [])
            ),
            privacy_review=PrivacyReview.from_dict(data.get("privacy_review", {})),
        )

    def to_dict(self) -> dict[str, JsonValue]:
        return {
            "plan_id": self.plan_id,
            "created_at": self.created_at,
            "sheetforge_commit": self.sheetforge_commit,
            "source": self.source.to_dict(),
            "workflow_status": self.workflow_status.to_dict(),
            "coverage": self.coverage.to_dict(),
            "diagnostic_summary": self.diagnostic_summary.to_dict(),
            "residual_blockers": [blocker.to_dict() for blocker in self.residual_blockers],
            "generation": self.generation.to_dict(),
            "validation": self.validation.to_dict(),
            "recommendations": [recommendation.to_dict() for recommendation in self.recommendations],
            "privacy_review": self.privacy_review.to_dict(),
        }


def build_conversion_plan(
    *,
    plan_id: str,
    workbook: WorkbookRecord,
    graph: DependencyGraph,
    expressions: Mapping[str, FormulaExpression],
    benchmark_role: BenchmarkRole,
    sheetforge_commit: str = "unknown",
    generation_result: GenerationResult | None = None,
    cached_validation_report: ValidationReport | None = None,
    oracle_validation_report: ValidationReport | None = None,
    oracle_blockers: tuple[str, ...] = (),
    generated_model_path: str | None = None,
    include_source_path: bool = False,
    full_workbook_model: bool = False,
) -> ConversionPlan:
    """Build a JSON-serializable conversion plan from workflow records."""

    formula_cells = tuple(cell for cell in workbook.cells if cell.formula is not None)
    translated_formula_cells = sum(1 for expression in expressions.values() if expression.translated)
    untranslated_formula_cells = len(formula_cells) - translated_formula_cells
    translation_coverage = translated_formula_cells / len(formula_cells) if formula_cells else 1.0
    diagnostic_summary = _diagnostic_summary(
        workbook=workbook,
        graph=graph,
        expressions=expressions,
        generation_result=generation_result,
        cached_validation_report=cached_validation_report,
        oracle_validation_report=oracle_validation_report,
        oracle_blockers=oracle_blockers,
    )
    generation_summary = _generation_summary(
        generation_result=generation_result,
        generated_model_path=generated_model_path,
        full_workbook_model=full_workbook_model,
    )
    validation_summary = _validation_summary(
        cached_validation_report=cached_validation_report,
        oracle_validation_report=oracle_validation_report,
        oracle_blockers=oracle_blockers,
    )
    residual_blockers = _residual_blockers(diagnostic_summary)
    workflow_status = _workflow_status(
        translated_formula_cells=translated_formula_cells,
        formula_cells=len(formula_cells),
        generation_summary=generation_summary,
        validation_summary=validation_summary,
        residual_blockers=residual_blockers,
        full_workbook_model=full_workbook_model,
    )
    source_path = workbook.source_path if include_source_path else None
    return ConversionPlan(
        plan_id=plan_id,
        created_at=datetime.now(UTC).isoformat(),
        sheetforge_commit=sheetforge_commit,
        source=ConversionSource(
            workbook_id=workbook.workbook_id,
            file_type=_file_type(workbook.source_path),
            benchmark_role=benchmark_role,
            source_path=source_path,
            sanitized=not include_source_path,
        ),
        workflow_status=workflow_status,
        coverage=CoverageSummary(
            sheets=len(workbook.sheets),
            cells=len(workbook.cells),
            value_cells=len(workbook.cells) - len(formula_cells),
            formula_cells=len(formula_cells),
            translated_formula_cells=translated_formula_cells,
            untranslated_formula_cells=untranslated_formula_cells,
            translation_coverage=translation_coverage,
            named_ranges=len(workbook.named_ranges),
            dependency_edges=len(graph.edges),
            semantic_edges=len(graph.semantic_edges),
            execution_edges=len(graph.execution_edges),
        ),
        diagnostic_summary=diagnostic_summary,
        residual_blockers=residual_blockers,
        generation=generation_summary,
        validation=validation_summary,
        recommendations=_recommendations(residual_blockers, validation_summary),
        privacy_review=PrivacyReview(contains_source_path=include_source_path),
    )


def _diagnostic_summary(
    *,
    workbook: WorkbookRecord,
    graph: DependencyGraph,
    expressions: Mapping[str, FormulaExpression],
    generation_result: GenerationResult | None,
    cached_validation_report: ValidationReport | None,
    oracle_validation_report: ValidationReport | None,
    oracle_blockers: tuple[str, ...],
) -> DiagnosticSummary:
    return DiagnosticSummary(
        workbook_extraction=_counter_dict(diagnostic.code for diagnostic in workbook.diagnostics),
        named_ranges=_counter_dict(
            diagnostic.code
            for named_range in workbook.named_ranges
            for diagnostic in named_range.diagnostics
        ),
        formula_extraction=_counter_dict(
            diagnostic.code
            for cell in workbook.cells
            if cell.formula is not None
            for diagnostic in cell.formula.diagnostics
        ),
        graph=_counter_dict(graph.diagnostics),
        translation=_counter_dict(
            diagnostic.code
            for expression in expressions.values()
            for diagnostic in expression.diagnostics
        ),
        generation=_counter_dict(
            diagnostic.code for diagnostic in generation_result.diagnostics
        )
        if generation_result is not None
        else {},
        cached_validation=_validation_diagnostic_counts(cached_validation_report),
        oracle_validation=_counter_dict(oracle_blockers)
        if oracle_blockers
        else _validation_diagnostic_counts(oracle_validation_report),
    )


def _generation_summary(
    *,
    generation_result: GenerationResult | None,
    generated_model_path: str | None,
    full_workbook_model: bool,
) -> GenerationSummary:
    if generation_result is None:
        return GenerationSummary()
    return GenerationSummary(
        generated=generation_result.generated,
        generated_model_path=generated_model_path,
        selected_outputs=len(generation_result.contract.output_refs),
        selected_input_dependencies=len(generation_result.contract.input_refs),
        selection_strategy="contract_outputs",
        full_workbook_model=full_workbook_model,
    )


def _validation_summary(
    *,
    cached_validation_report: ValidationReport | None,
    oracle_validation_report: ValidationReport | None,
    oracle_blockers: tuple[str, ...],
) -> ValidationSummary:
    oracle_backend = oracle_validation_report.oracle_backend if oracle_validation_report is not None else None
    return ValidationSummary(
        cached_validation_status=_report_status(cached_validation_report),
        cached_outputs=len(cached_validation_report.comparisons) if cached_validation_report is not None else 0,
        cached_mismatches=len(cached_validation_report.mismatches) if cached_validation_report is not None else 0,
        oracle_backend=oracle_backend,
        oracle_status="blocked" if oracle_blockers else _report_status(oracle_validation_report),
        oracle_mismatches=len(oracle_validation_report.mismatches) if oracle_validation_report is not None else 0,
        oracle_blockers=oracle_blockers,
    )


def _workflow_status(
    *,
    translated_formula_cells: int,
    formula_cells: int,
    generation_summary: GenerationSummary,
    validation_summary: ValidationSummary,
    residual_blockers: tuple[ResidualBlocker, ...],
    full_workbook_model: bool,
) -> WorkflowStatus:
    formula_translation: StageStatus = "pass" if translated_formula_cells else "blocked"
    generation: StageStatus = "pass" if generation_summary.generated else "not_run"
    if not translated_formula_cells:
        overall: OverallStatus = "blocked"
    elif full_workbook_model and not residual_blockers and validation_summary.oracle_status == "pass":
        overall = "complete"
    else:
        overall = "partial"
    return WorkflowStatus(
        extraction="pass",
        dependency_graph="pass",
        formula_translation=formula_translation,
        generation=generation,
        cached_validation=validation_summary.cached_validation_status,
        oracle_validation=validation_summary.oracle_status,
        overall=overall,
    )


def _residual_blockers(diagnostics: DiagnosticSummary) -> tuple[ResidualBlocker, ...]:
    blockers: list[ResidualBlocker] = []
    for code, count in sorted(diagnostics.workbook_extraction.items()):
        blockers.append(
            _diagnostic_blocker(
                prefix="extraction",
                index=len(blockers) + 1,
                code=code,
                count=count,
                category=_extraction_blocker_category(code),
                disposition=_extraction_blocker_disposition(code),
                next_action=_extraction_next_action(code),
                provenance="extraction",
            )
        )
    for code, count in sorted(diagnostics.named_ranges.items()):
        blockers.append(
            _diagnostic_blocker(
                prefix="named-range",
                index=len(blockers) + 1,
                code=code,
                count=count,
                category=_named_range_blocker_category(code),
                disposition=_named_range_blocker_disposition(code),
                next_action=_named_range_next_action(code),
                provenance="extraction",
            )
        )
    for code, count in sorted(diagnostics.formula_extraction.items()):
        blockers.append(
            _diagnostic_blocker(
                prefix="formula-extraction",
                index=len(blockers) + 1,
                code=code,
                count=count,
                category=_formula_extraction_blocker_category(code),
                disposition=_formula_extraction_blocker_disposition(code, diagnostics),
                next_action=_formula_extraction_next_action(code, diagnostics),
                provenance="extraction",
            )
        )
    for code, count in sorted(diagnostics.graph.items()):
        blockers.append(
            _diagnostic_blocker(
                prefix="graph",
                index=len(blockers) + 1,
                code=code,
                count=count,
                category=_graph_blocker_category(code),
                disposition=_graph_blocker_disposition(code),
                next_action=_graph_next_action(code),
                provenance="graph",
            )
        )
    for code, count in sorted(diagnostics.translation.items()):
        blockers.append(
            _diagnostic_blocker(
                prefix="translation",
                index=len(blockers) + 1,
                code=code,
                count=count,
                category=_translation_blocker_category(code),
                disposition=_translation_blocker_disposition(code),
                next_action=_translation_next_action(code),
                provenance="translation",
            )
        )
    for code, count in sorted(diagnostics.generation.items()):
        blockers.append(
            _diagnostic_blocker(
                prefix="generation",
                index=len(blockers) + 1,
                code=code,
                count=count,
                category="generation_scope",
                disposition="next_target",
                next_action="Refine generated-model scope or code generation support for this diagnostic.",
                provenance="generation",
            )
        )
    for code, count in sorted(diagnostics.cached_validation.items()):
        blockers.append(
            _diagnostic_blocker(
                prefix="cached-validation",
                index=len(blockers) + 1,
                code=code,
                count=count,
                category="missing_cached_values" if "missing" in code else "unknown",
                disposition="deferred",
                next_action="Record cached-value limitation and select validation examples that can be compared.",
                provenance="validation",
            )
        )
    for code, count in sorted(diagnostics.oracle_validation.items()):
        blockers.append(
            _diagnostic_blocker(
                prefix="oracle-validation",
                index=len(blockers) + 1,
                code=code,
                count=count,
                category="validation_oracle",
                disposition="deferred",
                next_action="Record oracle limitation and select a validation strategy.",
                provenance="validation",
            )
        )
    return tuple(blockers)


def _diagnostic_blocker(
    *,
    prefix: str,
    index: int,
    code: str,
    count: int,
    category: BlockerCategory,
    disposition: BlockerDisposition,
    next_action: str,
    provenance: str,
) -> ResidualBlocker:
    return ResidualBlocker(
        blocker_id=f"{prefix}-{index:03d}",
        category=category,
        diagnostic_code=code,
        item=code,
        count=count,
        severity="warning",
        disposition=disposition,
        next_action=next_action,
        provenance=provenance,
    )


def _recommendations(
    residual_blockers: tuple[ResidualBlocker, ...],
    validation_summary: ValidationSummary,
) -> tuple[PlanRecommendation, ...]:
    recommendations: list[PlanRecommendation] = []
    for blocker in residual_blockers:
        if blocker.disposition == "next_target":
            recommendations.append(
                PlanRecommendation(
                    priority=len(recommendations) + 1,
                    action=blocker.next_action,
                    rationale=f"{blocker.count} item(s) remain blocked by {blocker.diagnostic_code}.",
                )
            )
    if validation_summary.oracle_status == "blocked":
        recommendations.append(
            PlanRecommendation(
                priority=len(recommendations) + 1,
                action="Choose full-workbook validation oracle strategy.",
                rationale="Cached-value subset validation is useful but does not prove workbook equivalence.",
            )
        )
    return tuple(recommendations)


def _validation_diagnostic_counts(report: ValidationReport | None) -> dict[str, int]:
    if report is None:
        return {}
    return _counter_dict(
        comparison.diagnostic_code
        for comparison in report.comparisons
        if comparison.diagnostic_code is not None
    )


def _report_status(report: ValidationReport | None) -> ValidationStatus:
    if report is None:
        return "not_run"
    return report.status


def _counter_dict(values) -> dict[str, int]:
    return dict(Counter(value for value in values if value))


def _file_type(source_path: str) -> str:
    if "." not in source_path:
        return ""
    return f".{source_path.rsplit('.', 1)[1].lower()}"


def _extraction_blocker_category(code: str) -> BlockerCategory:
    if "external" in code:
        return "external_dependency"
    return "unknown"


def _extraction_blocker_disposition(code: str) -> BlockerDisposition:
    if "external" in code:
        return "deferred"
    return "next_target"


def _extraction_next_action(code: str) -> str:
    if "external" in code:
        return "Require explicit external workbook materialization, mock inputs, or rejection policy; do not inline external dependencies silently."
    return "Classify this workbook-extraction diagnostic before claiming conversion readiness."


def _graph_blocker_category(code: str) -> BlockerCategory:
    if "external" in code:
        return "external_dependency"
    return "graph_semantics"


def _graph_blocker_disposition(code: str) -> BlockerDisposition:
    if "external" in code:
        return "deferred"
    return "next_target"


def _graph_next_action(code: str) -> str:
    if "external" in code:
        return "Require explicit external workbook materialization, mock inputs, or rejection policy before full conversion."
    return "Define graph semantics or reporting policy for this workbook structure."


def _named_range_blocker_category(code: str) -> BlockerCategory:
    if code == "named_range_source_error":
        return "source_workbook_defect"
    if "named_range" in code or "defined_name" in code:
        return "unsupported_reference_semantics"
    return "unknown"


def _named_range_blocker_disposition(code: str) -> BlockerDisposition:
    if code == "named_range_source_error":
        return "out_of_scope"
    if "unresolved" in code:
        return "next_target"
    return "deferred"


def _named_range_next_action(code: str) -> str:
    if code == "named_range_source_error":
        return "Ignore stale source workbook defined-name errors unless referenced by formulas or validation rules."
    if "unresolved" in code:
        return "Resolve named-range semantics or document why the range is out of conversion scope."
    return "Classify this named-range diagnostic before claiming conversion readiness."


def _formula_extraction_blocker_category(code: str) -> BlockerCategory:
    if "external" in code:
        return "external_dependency"
    if code == "missing_cached_formula_value":
        return "missing_cached_values"
    if "structured_reference" in code:
        return "unsupported_reference_semantics"
    if "volatile" in code:
        return "unsupported_formula_semantics"
    return "unknown"


def _formula_extraction_blocker_disposition(
    code: str,
    diagnostics: DiagnosticSummary,
) -> BlockerDisposition:
    if code == "missing_cached_formula_value":
        return "deferred"
    if "external" in code:
        return "deferred"
    if "structured_reference" in code:
        if not _has_unresolved_reference_diagnostics(diagnostics):
            return "resolved"
        return "deferred"
    if "volatile" in code:
        if not diagnostics.translation:
            return "resolved"
        return "deferred"
    return "next_target"


def _formula_extraction_next_action(
    code: str,
    diagnostics: DiagnosticSummary,
) -> str:
    if code == "missing_cached_formula_value":
        return "Not a generation blocker; use a recalculation oracle or select validation outputs with available cached values."
    if "external" in code:
        return "Require explicit external workbook materialization, mock inputs, or rejection policy; do not inline external dependencies silently."
    if "structured_reference" in code:
        if not _has_unresolved_reference_diagnostics(diagnostics):
            return "No conversion action required; extraction diagnostic is provenance for structured references already resolved by graph and translation."
        return "Keep structured-reference diagnostics visible and separate them from translation failures."
    if "volatile" in code:
        if not diagnostics.translation:
            return "No formula-semantics action required while translation is clean; retain volatile-function provenance for validation risk review."
        return "Record volatile formula risk and define deterministic handling where conversion needs it."
    return "Classify this formula-extraction diagnostic before claiming conversion readiness."


def _has_unresolved_reference_diagnostics(diagnostics: DiagnosticSummary) -> bool:
    reference_codes = tuple(diagnostics.graph) + tuple(diagnostics.translation)
    return any("structured_reference" in code or "reference" in code for code in reference_codes)


def _translation_blocker_category(code: str) -> BlockerCategory:
    if code == "unsupported_error_reference":
        return "source_workbook_defect"
    if "structured_reference" in code or "reference" in code:
        return "unsupported_reference_semantics"
    if code.startswith("unsupported_function") or code.startswith("unsupported_"):
        return "unsupported_formula_semantics"
    return "unknown"


def _translation_blocker_disposition(code: str) -> BlockerDisposition:
    if code == "unsupported_error_reference":
        return "blocked_by_design"
    return "next_target"


def _translation_next_action(code: str) -> str:
    if code == "unsupported_error_reference":
        return "Report explicit source error references; do not silently generate normal Python behavior."
    return "Implement support or a sharper diagnostic for this translation blocker."
