"""Workbook reference normalization records and helpers."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Literal

from openpyxl.utils.cell import range_boundaries


JsonValue = str | int | float | bool | None | list[Any] | dict[str, Any]
ReferenceKind = Literal["cell", "range", "named_range", "structured", "external", "unresolved"]

_CELL_RE = re.compile(r"^\$?[A-Za-z]{1,3}\$?\d+$")
_SHEET_AND_COORD_RE = re.compile(r"^(?P<sheet>'[^']+'|[^!]+)!(?P<coord>.+)$")
_NAME_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_.]*$")
_EXTERNAL_WORKBOOK_RE = re.compile(r"\[[^\]]+\.(?:xlsx|xlsm|xlsb|xls|csv)\]", re.IGNORECASE)


@dataclass(frozen=True)
class WorkbookReference:
    """Canonical representation of one workbook reference token."""

    kind: ReferenceKind
    original: str
    normalized: str
    workbook: str | None = None
    sheet: str | None = None
    start_cell: str | None = None
    end_cell: str | None = None
    name: str | None = None
    diagnostic_code: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "WorkbookReference":
        return cls(
            kind=data["kind"],
            original=data["original"],
            normalized=data["normalized"],
            workbook=data.get("workbook"),
            sheet=data.get("sheet"),
            start_cell=data.get("start_cell"),
            end_cell=data.get("end_cell"),
            name=data.get("name"),
            diagnostic_code=data.get("diagnostic_code"),
        )

    def to_dict(self) -> dict[str, JsonValue]:
        return {
            "kind": self.kind,
            "original": self.original,
            "normalized": self.normalized,
            "workbook": self.workbook,
            "sheet": self.sheet,
            "start_cell": self.start_cell,
            "end_cell": self.end_cell,
            "name": self.name,
            "diagnostic_code": self.diagnostic_code,
        }


def normalize_reference(reference: str, *, current_sheet: str | None = None) -> WorkbookReference:
    """Normalize one workbook formula reference token."""

    original = reference
    reference = reference.strip()
    if not reference:
        return _unresolved(original, "empty_reference")

    if _is_external_reference(reference):
        return WorkbookReference(
            kind="external",
            original=original,
            normalized=reference,
            workbook=_external_workbook(reference),
            diagnostic_code="external_reference",
        )

    if _is_structured_reference(reference):
        return WorkbookReference(
            kind="structured",
            original=original,
            normalized=reference,
            diagnostic_code="unsupported_structured_reference",
        )

    sheet_name, coordinate = _split_sheet_and_coordinate(reference)
    if sheet_name is None:
        if _is_named_range(reference):
            return WorkbookReference(
                kind="named_range",
                original=original,
                normalized=reference,
                name=reference,
            )
        sheet_name = current_sheet
        coordinate = reference

    if sheet_name is not None and _is_cell_or_range(coordinate):
        return _cell_or_range_reference(
            original=original,
            sheet_name=sheet_name,
            coordinate=coordinate,
        )

    return _unresolved(original, "unresolved_reference")


def normalize_cell_reference(reference: str, *, current_sheet: str | None = None) -> WorkbookReference:
    """Normalize a token expected to identify one cell."""

    normalized = normalize_reference(reference, current_sheet=current_sheet)
    if normalized.kind == "cell":
        return normalized
    return _unresolved(reference, "not_a_cell_reference")


def _cell_or_range_reference(*, original: str, sheet_name: str, coordinate: str) -> WorkbookReference:
    clean_coordinate = coordinate.replace("$", "")
    try:
        min_col, min_row, max_col, max_row = range_boundaries(clean_coordinate)
    except ValueError:
        return _unresolved(original, "unresolved_reference")

    start_cell = f"{_column_name(min_col)}{min_row}"
    end_cell = f"{_column_name(max_col)}{max_row}"
    if start_cell == end_cell:
        return WorkbookReference(
            kind="cell",
            original=original,
            normalized=f"{sheet_name}!{start_cell}",
            sheet=sheet_name,
            start_cell=start_cell,
            end_cell=end_cell,
        )

    return WorkbookReference(
        kind="range",
        original=original,
        normalized=f"{sheet_name}!{start_cell}:{end_cell}",
        sheet=sheet_name,
        start_cell=start_cell,
        end_cell=end_cell,
    )


def _split_sheet_and_coordinate(reference: str) -> tuple[str | None, str]:
    match = _SHEET_AND_COORD_RE.match(reference)
    if not match:
        return None, reference
    return _unquote_sheet(match.group("sheet")), match.group("coord")


def _unquote_sheet(sheet_name: str) -> str:
    if sheet_name.startswith("'") and sheet_name.endswith("'"):
        return sheet_name[1:-1].replace("''", "'")
    return sheet_name


def _is_cell_or_range(coordinate: str) -> bool:
    clean_coordinate = coordinate.replace("$", "")
    if _CELL_RE.match(clean_coordinate):
        return True
    try:
        range_boundaries(clean_coordinate)
    except ValueError:
        return False
    return ":" in clean_coordinate


def _is_named_range(reference: str) -> bool:
    return bool(_NAME_RE.match(reference)) and not _CELL_RE.match(reference)


def _is_external_reference(reference: str) -> bool:
    return bool(_EXTERNAL_WORKBOOK_RE.search(reference)) or _looks_like_external_reference(reference)


def _is_structured_reference(reference: str) -> bool:
    return "[" in reference and "]" in reference


def _looks_like_external_reference(reference: str) -> bool:
    return "[" in reference and "]" in reference and "!" in reference


def _external_workbook(reference: str) -> str | None:
    match = re.search(r"\[([^\]]+)\]", reference)
    if match:
        return match.group(1)
    return None


def _unresolved(original: str, diagnostic_code: str) -> WorkbookReference:
    return WorkbookReference(
        kind="unresolved",
        original=original,
        normalized=original.strip(),
        diagnostic_code=diagnostic_code,
    )


def _column_name(index: int) -> str:
    name = ""
    while index:
        index, remainder = divmod(index - 1, 26)
        name = chr(65 + remainder) + name
    return name
