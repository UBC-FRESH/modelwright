from __future__ import annotations

import importlib.util
import json
import os
import sys
from pathlib import Path
from types import ModuleType

import pytest

from modelwright.notebooks import outputs_frame, report_frames, table_frame
from modelwright.wrappers import ModelFacade, cell, report, table


FABLE_ARTIFACT_DIR = Path("tmp/p26-fable-full-validation")
FABLE_MODEL_PATH = FABLE_ARTIFACT_DIR / "generated_fable_2020_model.py"
FABLE_SUMMARY_PATH = FABLE_ARTIFACT_DIR / "summary.json"
FABLE_SCENARIO_OUTPUTS = {
    "SCENARIOS selection!D20": 2.146115426018433,
    "SCENARIOS selection!D21": 1.8982220554032356,
    "SCENARIOS selection!D22": 1.462761288724012,
}


def load_module(path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location("generated_fable_2020_model_for_wrapper_test", path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@pytest.mark.benchmark
def test_model_facade_wraps_2020_fable_benchmark_model_outputs() -> None:
    if os.environ.get("MODELWRIGHT_RUN_FABLE_BENCHMARKS") != "1":
        pytest.skip("set MODELWRIGHT_RUN_FABLE_BENCHMARKS=1 to run local FABLE benchmark facade tests")
    if not FABLE_MODEL_PATH.exists() or not FABLE_SUMMARY_PATH.exists():
        pytest.skip("materialize local P26 FABLE validation artifacts before running this benchmark test")

    summary = json.loads(FABLE_SUMMARY_PATH.read_text())
    assert summary["status"] == "pass"
    assert summary["validated_output_universe"]["matches"] == 281741
    assert summary["validated_output_universe"]["mismatches"] == 0

    module = load_module(FABLE_MODEL_PATH)
    facade = ModelFacade(
        module,
        cells=[
            cell("SCENARIOS selection!D20", name="scenario_metric_1", role="output"),
            cell("SCENARIOS selection!D21", name="scenario_metric_2", role="output"),
            cell("SCENARIOS selection!D22", name="scenario_metric_3", role="output"),
        ],
        tables=[
            table(
                "scenario_selection_slice",
                sheet="SCENARIOS selection",
                range_ref="D20:D22",
                row_labels=["d20", "d21", "d22"],
                column_labels=["value"],
            )
        ],
        reports=[
            report(
                "scenario_selection",
                cells=["scenario_metric_1", "scenario_metric_2", "scenario_metric_3"],
                tables=["scenario_selection_slice"],
            )
        ],
    )

    values = facade.calculate()

    for cell_ref, expected in FABLE_SCENARIO_OUTPUTS.items():
        assert values[cell_ref] == pytest.approx(expected)
        assert facade.inspect(cell_ref).value == pytest.approx(expected)
    table_values = facade.table("scenario_selection_slice").to_dict()["values"]
    assert table_values[0][0] == pytest.approx(FABLE_SCENARIO_OUTPUTS["SCENARIOS selection!D20"])
    assert table_values[1][0] == pytest.approx(FABLE_SCENARIO_OUTPUTS["SCENARIOS selection!D21"])
    assert table_values[2][0] == pytest.approx(FABLE_SCENARIO_OUTPUTS["SCENARIOS selection!D22"])

    report_payload = facade.report("scenario_selection")
    assert report_payload["cells"]["scenario_metric_1"]["value"] == pytest.approx(
        FABLE_SCENARIO_OUTPUTS["SCENARIOS selection!D20"]
    )
    assert report_payload["tables"]["scenario_selection_slice"]["values"][2][0] == pytest.approx(
        FABLE_SCENARIO_OUTPUTS["SCENARIOS selection!D22"]
    )

    output_rows = outputs_frame(facade).set_index("cell_ref")
    assert output_rows.loc["SCENARIOS selection!D20", "value"] == pytest.approx(
        FABLE_SCENARIO_OUTPUTS["SCENARIOS selection!D20"]
    )

    table_rows = table_frame(facade, "scenario_selection_slice")
    assert table_rows.loc["d21", "value"] == pytest.approx(FABLE_SCENARIO_OUTPUTS["SCENARIOS selection!D21"])
    assert table_rows.attrs["cell_refs"] == [
        ["SCENARIOS selection!D20"],
        ["SCENARIOS selection!D21"],
        ["SCENARIOS selection!D22"],
    ]

    frames = report_frames(facade, "scenario_selection")
    assert frames["cells"].set_index("name").loc["scenario_metric_3", "value"] == pytest.approx(
        FABLE_SCENARIO_OUTPUTS["SCENARIOS selection!D22"]
    )
    assert frames["tables"]["scenario_selection_slice"].loc["d20", "value"] == pytest.approx(
        FABLE_SCENARIO_OUTPUTS["SCENARIOS selection!D20"]
    )
