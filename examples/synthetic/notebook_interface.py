"""Tiny notebook-interface example for a generated Modelwright model."""

from __future__ import annotations

from modelwright.notebooks import compare_scenarios_frame, outputs_frame, table_frame
from modelwright.wrappers import ModelFacade, cell, report, table


def calculate(inputs=None):
    """Small stand-in for generated Modelwright Python output."""

    inputs = inputs or {}
    base = inputs.get("Inputs!B2", 100)
    growth = inputs.get("Inputs!B3", 0.1)
    return {
        "Summary!B2": base * (1 + growth),
        "Summary!C2": base * 2,
        "Summary!B3": "ok",
        "Summary!C3": base + 5,
    }


def build_facade() -> ModelFacade:
    return ModelFacade(
        calculate,
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
        reports=[
            report("summary", cells=["base", "projected", "status"], tables=["summary_grid"]),
        ],
    )


def run_example():
    facade = build_facade()
    baseline = facade.scenario(name="baseline", inputs={"Inputs!B2": 100, "Inputs!B3": 0.1})
    shock = baseline.with_input("Inputs!B2", 120)
    return {
        "outputs": outputs_frame(facade, shock),
        "summary_grid": table_frame(facade, "summary_grid", shock),
        "comparison": compare_scenarios_frame(facade, baseline, shock),
    }


if __name__ == "__main__":
    frames = run_example()
    for name, frame in frames.items():
        print(f"\n{name}")
        print(frame)
