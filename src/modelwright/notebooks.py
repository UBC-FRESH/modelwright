"""Notebook-friendly DataFrame helpers for wrapped generated models."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from numbers import Real
from typing import TYPE_CHECKING, Any

from modelwright.references import normalize_cell_reference
from modelwright.wrappers import CellRef, ModelFacade, Scenario, WrapperDeclarationError

if TYPE_CHECKING:
    import pandas as pd


class NotebookDependencyError(RuntimeError):
    """Raised when notebook helpers need an optional dependency that is not installed."""


def inputs_frame(facade: ModelFacade, scenario: Scenario | None = None) -> "pd.DataFrame":
    """Return declared facade inputs as a tidy pandas DataFrame."""

    values = _values_for(facade, scenario)
    return _cell_frame(facade.inputs().values(), values)


def outputs_frame(facade: ModelFacade, scenario: Scenario | None = None) -> "pd.DataFrame":
    """Return declared facade outputs as a tidy pandas DataFrame."""

    values = _values_for(facade, scenario)
    return _cell_frame(facade.outputs().values(), values)


def scenario_frame(scenario: Scenario) -> "pd.DataFrame":
    """Return scenario input overrides as a tidy pandas DataFrame."""

    pd = _load_pandas()
    return pd.DataFrame(
        [
            {
                "scenario": scenario.name,
                "cell_ref": cell_ref,
                "value": value,
            }
            for cell_ref, value in scenario.inputs.items()
        ],
        columns=["scenario", "cell_ref", "value"],
    )


def table_frame(facade: ModelFacade, name: str, scenario: Scenario | None = None) -> "pd.DataFrame":
    """Return a declared facade table as a pandas DataFrame."""

    pd = _load_pandas()
    table = facade.table(name, scenario=scenario)
    frame = pd.DataFrame(table.values, index=list(table.rows), columns=list(table.columns))
    frame.index.name = "row"
    frame.attrs.update(
        {
            "name": table.name,
            "label": table.label,
            "description": table.description,
            "sheet": table.sheet,
            "range_ref": table.range_ref,
            "cell_refs": [list(row) for row in table.cell_refs],
        }
    )
    return frame


def report_frames(facade: ModelFacade, name: str, scenario: Scenario | None = None) -> dict[str, Any]:
    """Return DataFrame payloads for a declared facade report."""

    report = facade.reports.get(name)
    if report is None:
        raise WrapperDeclarationError(f"unknown report declaration {name!r}")

    values = _values_for(facade, scenario)
    cells = [facade.cells[cell_name] for cell_name in report.cells]
    return {
        "name": report.name,
        "label": report.label,
        "description": report.description,
        "cells": _cell_frame(cells, values),
        "tables": {
            table_name: table_frame(facade, table_name, scenario=scenario)
            for table_name in report.tables
        },
    }


def compare_scenarios_frame(
    facade: ModelFacade,
    baseline: Scenario,
    scenario: Scenario,
    *,
    cells: Iterable[str] | None = None,
) -> "pd.DataFrame":
    """Compare declared output cells between two scenarios as a tidy DataFrame."""

    baseline_values = _values_for(facade, baseline)
    scenario_values = _values_for(facade, scenario)
    declarations = _comparison_cells(facade, cells)

    rows = []
    for declaration in declarations:
        baseline_value = baseline_values.get(declaration.cell_ref)
        scenario_value = scenario_values.get(declaration.cell_ref)
        absolute_change = _absolute_change(baseline_value, scenario_value)
        rows.append(
            {
                "name": declaration.name,
                "label": declaration.label,
                "cell_ref": declaration.cell_ref,
                "baseline_value": baseline_value,
                "scenario_value": scenario_value,
                "absolute_change": absolute_change,
                "percent_change": _percent_change(baseline_value, absolute_change),
                "unit": declaration.unit,
                "role": declaration.role,
                "description": declaration.description,
            }
        )

    pd = _load_pandas()
    return pd.DataFrame(
        rows,
        columns=[
            "name",
            "label",
            "cell_ref",
            "baseline_value",
            "scenario_value",
            "absolute_change",
            "percent_change",
            "unit",
            "role",
            "description",
        ],
        dtype=object,
    )


def _cell_frame(cells: Iterable[CellRef], values: Mapping[str, object]) -> "pd.DataFrame":
    pd = _load_pandas()
    return pd.DataFrame(
        [
            {
                "name": declaration.name,
                "label": declaration.label,
                "cell_ref": declaration.cell_ref,
                "role": declaration.role,
                "unit": declaration.unit,
                "description": declaration.description,
                "value": values.get(declaration.cell_ref),
                "has_value": declaration.cell_ref in values,
            }
            for declaration in cells
        ],
        columns=[
            "name",
            "label",
            "cell_ref",
            "role",
            "unit",
            "description",
            "value",
            "has_value",
        ],
    )


def _comparison_cells(facade: ModelFacade, cells: Iterable[str] | None) -> list[CellRef]:
    declarations_by_name = facade.cells
    if cells is None:
        return list(facade.outputs().values())

    declarations = []
    for selector in cells:
        declaration = declarations_by_name.get(selector)
        if declaration is not None:
            declarations.append(declaration)
            continue

        normalized = _normalize_cell_ref(selector)
        for candidate in declarations_by_name.values():
            if candidate.cell_ref == normalized:
                declarations.append(candidate)
                break
        else:
            declarations.append(CellRef(cell_ref=normalized, name=normalized))
    return declarations


def _values_for(facade: ModelFacade, scenario: Scenario | None) -> dict[str, object]:
    facade_values_for = getattr(facade, "_values_for", None)
    if callable(facade_values_for):
        return dict(facade_values_for(scenario))

    active_scenario = scenario or facade.scenario()
    values = facade.calculate(active_scenario)
    return {**active_scenario.inputs, **values}


def _normalize_cell_ref(cell_ref: str) -> str:
    normalized = normalize_cell_reference(cell_ref)
    if normalized.kind != "cell" or normalized.sheet is None:
        raise WrapperDeclarationError(f"expected a full cell reference like 'Sheet!A1', got {cell_ref!r}")
    return normalized.normalized


def _absolute_change(baseline_value: object, scenario_value: object) -> float | int | None:
    if _is_number(baseline_value) and _is_number(scenario_value):
        return scenario_value - baseline_value
    return None


def _percent_change(baseline_value: object, absolute_change: object) -> float | None:
    if _is_number(baseline_value) and baseline_value != 0 and _is_number(absolute_change):
        return absolute_change / baseline_value
    return None


def _is_number(value: object) -> bool:
    return isinstance(value, Real) and not isinstance(value, bool)


def _load_pandas() -> Any:
    try:
        import pandas as pd
    except ImportError as error:
        raise NotebookDependencyError(
            "Install modelwright[notebook] to use pandas-backed notebook helpers."
        ) from error
    return pd


__all__ = [
    "NotebookDependencyError",
    "compare_scenarios_frame",
    "inputs_frame",
    "outputs_frame",
    "report_frames",
    "scenario_frame",
    "table_frame",
]
