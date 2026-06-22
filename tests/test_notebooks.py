from __future__ import annotations

import builtins
import importlib
from pathlib import Path

import pytest

from modelwright.notebooks import (
    NotebookDependencyError,
    compare_scenarios_frame,
    inputs_frame,
    outputs_frame,
    report_frames,
    scenario_frame,
    table_frame,
)
from modelwright.wrappers import ModelFacade, cell, report, table
from tests.test_wrappers import build_generated_synthetic_model


def generated_model(inputs=None):
    inputs = inputs or {}
    base = inputs.get("Inputs!B2", 100)
    growth = inputs.get("Inputs!B3", 0.1)
    return {
        "Summary!B2": base * (1 + growth),
        "Summary!C2": base * 2,
        "Summary!B3": "ok",
        "Summary!C3": base + 5,
    }


def notebook_facade(generated=generated_model) -> ModelFacade:
    return ModelFacade(
        generated,
        cells=[
            cell("Inputs!B2", name="base", label="Base volume", role="input", unit="t"),
            cell("Inputs!B3", name="growth", label="Growth rate", role="input", unit="fraction"),
            cell("Summary!B2", name="projected", label="Projected volume", role="output", unit="t"),
            cell("Summary!B3", name="status", label="Status", role="output"),
        ],
        tables=[
            table(
                "summary_grid",
                sheet="Summary",
                range_ref="B2:C3",
                row_labels=["volume", "status"],
                column_labels=["primary", "secondary"],
            )
        ],
        reports=[report("summary", cells=["base", "projected", "status"], tables=["summary_grid"])],
    )


def test_notebook_frames_expose_declared_inputs_outputs_tables_and_reports() -> None:
    facade = notebook_facade()
    scenario = facade.scenario(name="shock", inputs={"Inputs!B2": 50}).with_input("Inputs!B3", 0.2)

    input_rows = inputs_frame(facade, scenario)
    assert input_rows.to_dict("records") == [
        {
            "name": "base",
            "label": "Base volume",
            "cell_ref": "Inputs!B2",
            "role": "input",
            "unit": "t",
            "description": None,
            "value": 50,
            "has_value": True,
        },
        {
            "name": "growth",
            "label": "Growth rate",
            "cell_ref": "Inputs!B3",
            "role": "input",
            "unit": "fraction",
            "description": None,
            "value": 0.2,
            "has_value": True,
        },
    ]

    output_rows = outputs_frame(facade, scenario)
    assert output_rows[["name", "cell_ref", "value", "has_value"]].to_dict("records") == [
        {"name": "projected", "cell_ref": "Summary!B2", "value": 60.0, "has_value": True},
        {"name": "status", "cell_ref": "Summary!B3", "value": "ok", "has_value": True},
    ]

    scenario_rows = scenario_frame(scenario)
    assert scenario_rows.to_dict("records") == [
        {"scenario": "shock", "cell_ref": "Inputs!B2", "value": 50},
        {"scenario": "shock", "cell_ref": "Inputs!B3", "value": 0.2},
    ]

    summary_grid = table_frame(facade, "summary_grid", scenario)
    assert list(summary_grid.index) == ["volume", "status"]
    assert list(summary_grid.columns) == ["primary", "secondary"]
    assert summary_grid.loc["volume", "primary"] == 60.0
    assert summary_grid.loc["status", "secondary"] == 55
    assert summary_grid.attrs["sheet"] == "Summary"
    assert summary_grid.attrs["range_ref"] == "B2:C3"
    assert summary_grid.attrs["cell_refs"] == [["Summary!B2", "Summary!C2"], ["Summary!B3", "Summary!C3"]]

    frames = report_frames(facade, "summary", scenario)
    assert frames["name"] == "summary"
    assert frames["cells"][["name", "value"]].to_dict("records") == [
        {"name": "base", "value": 50},
        {"name": "projected", "value": 60.0},
        {"name": "status", "value": "ok"},
    ]
    assert frames["tables"]["summary_grid"].loc["volume", "secondary"] == 100


def test_compare_scenarios_frame_handles_numeric_text_and_zero_baseline() -> None:
    def comparison_model(inputs=None):
        inputs = inputs or {}
        base = inputs.get("Inputs!B2", 100)
        multiplier = inputs.get("Inputs!B3", 1)
        return {
            "Summary!B2": base * multiplier,
            "Summary!B3": "ok" if multiplier == 1 else "changed",
            "Summary!B4": base - 100,
        }

    facade = ModelFacade(
        comparison_model,
        cells=[
            cell("Inputs!B2", name="base", role="input"),
            cell("Inputs!B3", name="multiplier", role="input"),
            cell("Summary!B2", name="projected", label="Projected volume", role="output", unit="t"),
            cell("Summary!B3", name="status", label="Status", role="output"),
            cell("Summary!B4", name="delta", label="Delta", role="output"),
        ],
    )

    baseline = facade.scenario(name="baseline", inputs={"Inputs!B2": 100, "Inputs!B3": 1})
    shock = baseline.with_input("Inputs!B3", 1.2)
    comparison = compare_scenarios_frame(facade, baseline, shock)

    projected = comparison.set_index("name").loc["projected"]
    assert projected["baseline_value"] == 100
    assert projected["scenario_value"] == 120
    assert projected["absolute_change"] == 20
    assert projected["percent_change"] == pytest.approx(0.2)

    status = comparison.set_index("name").loc["status"]
    assert status["baseline_value"] == "ok"
    assert status["scenario_value"] == "changed"
    assert status["absolute_change"] is None
    assert status["percent_change"] is None

    delta = comparison.set_index("name").loc["delta"]
    assert delta["baseline_value"] == 0
    assert delta["scenario_value"] == 0
    assert delta["absolute_change"] == 0
    assert delta["percent_change"] is None


def test_notebook_helpers_preserve_real_generated_synthetic_model_semantics(tmp_path: Path) -> None:
    module = build_generated_synthetic_model(tmp_path)
    facade = ModelFacade(
        module,
        cells=[
            cell("Inputs!B2", name="base", label="Base volume", role="input"),
            cell("Summary!B2", name="harvest", label="Rounded harvest", role="output"),
            cell("Summary!B3", name="status", label="Status", role="output"),
        ],
        tables=[
            table(
                "summary",
                sheet="Summary",
                range_ref="B2:B3",
                row_labels=["harvest", "status"],
                column_labels=["value"],
            )
        ],
    )
    scenario = facade.scenario(name="low-volume", inputs={"Inputs!B2": 10})

    assert facade.calculate(scenario) == module.calculate(scenario.inputs)
    assert outputs_frame(facade, scenario).set_index("name").loc["harvest", "value"] == 7.02
    assert table_frame(facade, "summary", scenario).loc["status", "value"] == "low"


def test_modelwright_import_does_not_require_pandas(monkeypatch: pytest.MonkeyPatch) -> None:
    real_import = builtins.__import__

    def guarded_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "pandas":
            raise ModuleNotFoundError("No module named 'pandas'")
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", guarded_import)
    module = importlib.reload(importlib.import_module("modelwright"))

    assert "inputs_frame" in module.__all__


def test_notebook_helpers_report_missing_pandas(monkeypatch: pytest.MonkeyPatch) -> None:
    real_import = builtins.__import__

    def guarded_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "pandas":
            raise ModuleNotFoundError("No module named 'pandas'")
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", guarded_import)

    with pytest.raises(NotebookDependencyError, match=r"modelwright\[notebook\]"):
        scenario_frame(notebook_facade().scenario())
