"""Dependency graph records built from extracted workbook facts."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

from openpyxl.utils.cell import range_boundaries

from sheetforge.extraction import CellRecord, TableRecord, WorkbookRecord
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
    diagnostics: tuple[str, ...] = field(default_factory=tuple)

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
            diagnostics=tuple(data.get("diagnostics", [])),
        )

    def to_dict(self) -> dict[str, JsonValue]:
        return {
            "workbook_id": self.workbook_id,
            "edges": [edge.to_dict() for edge in self.edges],
            "diagnostics": list(self.diagnostics),
        }


def build_dependency_graph(workbook: WorkbookRecord) -> DependencyGraph:
    """Build semantic and execution dependency edges from extracted formulas."""

    named_ranges = _named_range_destinations(workbook)
    tables = {table.name: table for table in workbook.tables}
    edges: list[DependencyEdge] = []
    diagnostics: list[str] = []

    for cell in workbook.cells:
        if cell.formula is None:
            continue

        target = _target_reference(cell)
        current_sheet = target.sheet
        for raw_reference in cell.formula.raw_references:
            source = normalize_reference(raw_reference, current_sheet=current_sheet)
            execution_edges = _execution_edges_for(source, target, raw_reference, named_ranges, tables)
            diagnostic_code = source.diagnostic_code
            if source.kind == "structured" and all(edge.diagnostic_code is None for edge in execution_edges):
                diagnostic_code = None
            edges.append(
                DependencyEdge(
                    source=source,
                    target=target,
                    edge_kind="semantic",
                    raw_reference=raw_reference,
                    diagnostic_code=diagnostic_code,
                )
            )
            edges.extend(execution_edges)

    diagnostics.extend(_diagnostic_codes(edges))
    diagnostics.extend(_circular_dependency_codes(edges))
    return DependencyGraph(workbook_id=workbook.workbook_id, edges=tuple(edges), diagnostics=tuple(dict.fromkeys(diagnostics)))


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
    tables: dict[str, TableRecord],
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

    if source.kind == "range":
        return tuple(
            DependencyEdge(
                source=range_cell,
                target=target,
                edge_kind="execution",
                raw_reference=raw_reference,
                resolved_from=source,
            )
            for range_cell in _expand_range_reference(source)
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

    if source.kind == "structured":
        resolved = _resolve_structured_reference(source, target, tables)
        if resolved is not None:
            return (
                DependencyEdge(
                    source=resolved,
                    target=target,
                    edge_kind="execution",
                    raw_reference=raw_reference,
                    resolved_from=source,
                ),
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


def _resolve_structured_reference(
    source: WorkbookReference,
    target: WorkbookReference,
    tables: dict[str, TableRecord],
) -> WorkbookReference | None:
    parsed = _parse_structured_reference(source.original)
    if parsed is None or parsed.column is None:
        return None

    table = tables.get(parsed.table_name) if parsed.table_name is not None else _table_containing_target(target, tables)
    if table is None:
        return None

    try:
        min_col, min_row, _max_col, max_row = range_boundaries(table.ref)
    except ValueError:
        return None

    try:
        column_offset = table.columns.index(parsed.column)
    except ValueError:
        return None

    column_name = _column_name(min_col + column_offset)
    data_start_row = min_row + 1
    if parsed.current_row:
        if target.sheet != table.sheet or target.start_cell is None:
            return None
        try:
            _target_col, target_row, _target_max_col, _target_max_row = range_boundaries(target.start_cell)
        except ValueError:
            return None
        if target_row < data_start_row or target_row > max_row:
            return None
        return normalize_reference(f"{table.sheet}!{column_name}{target_row}")

    return normalize_reference(f"{table.sheet}!{column_name}{data_start_row}:{column_name}{max_row}")


@dataclass(frozen=True)
class _StructuredReferenceParts:
    table_name: str | None
    column: str | None
    current_row: bool


def _parse_structured_reference(reference: str) -> _StructuredReferenceParts | None:
    if "[" not in reference or "]" not in reference:
        return None

    table_name = reference.split("[", 1)[0] or None
    bracketed_parts = _bracketed_parts(reference)
    current_row = any(part == "#This Row" or part.startswith("@") for part in bracketed_parts)
    if reference.startswith("[@"):
        current_row = True

    column = next(
        (
            _clean_structured_selector(part)
            for part in reversed(bracketed_parts)
            if not part.startswith("#")
        ),
        None,
    )
    return _StructuredReferenceParts(
        table_name=table_name,
        column=column,
        current_row=current_row,
    )


def _bracketed_parts(reference: str) -> tuple[str, ...]:
    parts: list[str] = []
    current: list[str] = []
    depth = 0
    for character in reference:
        if character == "[":
            if depth > 0:
                current.append(character)
            depth += 1
            continue
        if character == "]":
            depth -= 1
            if depth == 0:
                part = "".join(current)
                current = []
                if part.startswith("[") and part.endswith("]"):
                    parts.extend(_bracketed_parts(part))
                elif part:
                    parts.append(part)
                continue
            current.append(character)
            continue
        if depth > 0:
            current.append(character)
    return tuple(parts)


def _clean_structured_selector(selector: str) -> str:
    return selector.removeprefix("@").replace("''", "'")


def _table_containing_target(target: WorkbookReference, tables: dict[str, TableRecord]) -> TableRecord | None:
    if target.sheet is None or target.start_cell is None:
        return None

    try:
        target_col, target_row, _target_max_col, _target_max_row = range_boundaries(target.start_cell)
    except ValueError:
        return None

    for table in tables.values():
        if table.sheet != target.sheet:
            continue
        try:
            min_col, min_row, max_col, max_row = range_boundaries(table.ref)
        except ValueError:
            continue
        if min_col <= target_col <= max_col and min_row <= target_row <= max_row:
            return table
    return None


def _expand_range_reference(source: WorkbookReference) -> tuple[WorkbookReference, ...]:
    if source.sheet is None or source.start_cell is None or source.end_cell is None:
        return ()

    min_col, min_row, max_col, max_row = range_boundaries(f"{source.start_cell}:{source.end_cell}")
    return tuple(
        normalize_reference(f"{source.sheet}!{_column_name(column)}{row}")
        for row in range(min_row, max_row + 1)
        for column in range(min_col, max_col + 1)
    )


def _diagnostic_codes(edges: list[DependencyEdge]) -> tuple[str, ...]:
    return tuple(edge.diagnostic_code for edge in edges if edge.diagnostic_code is not None)


def _circular_dependency_codes(edges: list[DependencyEdge]) -> tuple[str, ...]:
    execution_pairs = {
        (edge.source.normalized, edge.target.normalized)
        for edge in edges
        if edge.edge_kind == "execution" and edge.source.kind == "cell" and edge.target.kind == "cell"
    }
    if any((target, source) in execution_pairs for source, target in execution_pairs):
        return ("circular_dependency",)
    return ()


def _column_name(index: int) -> str:
    name = ""
    while index:
        index, remainder = divmod(index - 1, 26)
        name = chr(65 + remainder) + name
    return name
