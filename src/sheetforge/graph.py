"""Dependency graph records built from extracted workbook facts."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

from sheetforge.extraction import CellRecord, WorkbookRecord
from sheetforge.references import WorkbookReference, normalize_reference


JsonValue = str | int | float | bool | None | list[Any] | dict[str, Any]
EdgeKind = Literal["semantic", "execution"]


@dataclass(frozen=True)
class DependencyEdge:
    """One dependency edge from an upstream source to a formula cell target."""

    source: WorkbookReference
    target: WorkbookReference
    edge_kind: EdgeKind
    raw_reference: str
    resolved_from: WorkbookReference | None = None
    diagnostic_code: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DependencyEdge":
        resolved_from_data = data.get("resolved_from")
        return cls(
            source=WorkbookReference.from_dict(data["source"]),
            target=WorkbookReference.from_dict(data["target"]),
            edge_kind=data["edge_kind"],
            raw_reference=data["raw_reference"],
            resolved_from=WorkbookReference.from_dict(resolved_from_data) if resolved_from_data is not None else None,
            diagnostic_code=data.get("diagnostic_code"),
        )

    def to_dict(self) -> dict[str, JsonValue]:
        return {
            "source": self.source.to_dict(),
            "target": self.target.to_dict(),
            "edge_kind": self.edge_kind,
            "raw_reference": self.raw_reference,
            "resolved_from": self.resolved_from.to_dict() if self.resolved_from is not None else None,
            "diagnostic_code": self.diagnostic_code,
        }


@dataclass(frozen=True)
class DependencyGraph:
    """Dependency edges for one workbook extraction."""

    workbook_id: str
    edges: tuple[DependencyEdge, ...] = field(default_factory=tuple)

    @property
    def semantic_edges(self) -> tuple[DependencyEdge, ...]:
        return tuple(edge for edge in self.edges if edge.edge_kind == "semantic")

    @property
    def execution_edges(self) -> tuple[DependencyEdge, ...]:
        return tuple(edge for edge in self.edges if edge.edge_kind == "execution")

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DependencyGraph":
        return cls(
            workbook_id=data["workbook_id"],
            edges=tuple(DependencyEdge.from_dict(edge) for edge in data.get("edges", [])),
        )

    def to_dict(self) -> dict[str, JsonValue]:
        return {
            "workbook_id": self.workbook_id,
            "edges": [edge.to_dict() for edge in self.edges],
        }


def build_dependency_graph(workbook: WorkbookRecord) -> DependencyGraph:
    """Build semantic and execution dependency edges from extracted formulas."""

    named_ranges = _named_range_destinations(workbook)
    edges: list[DependencyEdge] = []

    for cell in workbook.cells:
        if cell.formula is None:
            continue

        target = _target_reference(cell)
        current_sheet = target.sheet
        for raw_reference in cell.formula.raw_references:
            source = normalize_reference(raw_reference, current_sheet=current_sheet)
            edges.append(
                DependencyEdge(
                    source=source,
                    target=target,
                    edge_kind="semantic",
                    raw_reference=raw_reference,
                    diagnostic_code=source.diagnostic_code,
                )
            )
            edges.extend(_execution_edges_for(source, target, raw_reference, named_ranges))

    return DependencyGraph(workbook_id=workbook.workbook_id, edges=tuple(edges))


def _named_range_destinations(workbook: WorkbookRecord) -> dict[str, tuple[WorkbookReference, ...]]:
    return {
        named_range.name: tuple(
            reference
            for destination in named_range.destinations
            if (reference := normalize_reference(destination)).kind == "cell"
        )
        for named_range in workbook.named_ranges
    }


def _target_reference(cell: CellRecord) -> WorkbookReference:
    target = normalize_reference(cell.cell_ref)
    if target.kind != "cell":
        raise ValueError(f"formula cell target is not a cell reference: {cell.cell_ref}")
    return target


def _execution_edges_for(
    source: WorkbookReference,
    target: WorkbookReference,
    raw_reference: str,
    named_ranges: dict[str, tuple[WorkbookReference, ...]],
) -> tuple[DependencyEdge, ...]:
    if source.kind == "cell":
        return (
            DependencyEdge(
                source=source,
                target=target,
                edge_kind="execution",
                raw_reference=raw_reference,
            ),
        )

    if source.kind == "named_range" and source.name in named_ranges:
        return tuple(
            DependencyEdge(
                source=destination,
                target=target,
                edge_kind="execution",
                raw_reference=raw_reference,
                resolved_from=source,
            )
            for destination in named_ranges[source.name]
        )

    return (
        DependencyEdge(
            source=source,
            target=target,
            edge_kind="execution",
            raw_reference=raw_reference,
            diagnostic_code=source.diagnostic_code or f"unsupported_{source.kind}_dependency",
        ),
    )
