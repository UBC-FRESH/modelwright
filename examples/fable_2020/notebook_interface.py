"""Notebook-interface example for the generated 2020 FABLE benchmark model."""

from __future__ import annotations

import importlib.util
import lzma
import shutil
import sys
from pathlib import Path
from types import ModuleType

from modelwright.notebooks import outputs_frame, report_frames, table_frame
from modelwright.wrappers import ModelFacade, cell, report, table


EXAMPLE_DIR = Path(__file__).resolve().parent
ARCHIVE_PATH = EXAMPLE_DIR / "generated_fable_2020_model.py.xz"
WORK_DIR = Path("tmp/examples/fable_2020")
MODEL_PATH = WORK_DIR / "generated_fable_2020_model.py"

FABLE_SCENARIO_OUTPUTS = {
    "SCENARIOS selection!D20": 2.146115426018433,
    "SCENARIOS selection!D21": 1.8982220554032356,
    "SCENARIOS selection!D22": 1.462761288724012,
}


def materialize_generated_model() -> Path:
    """Decompress the tracked generated model into ignored local working space."""

    WORK_DIR.mkdir(parents=True, exist_ok=True)
    if not MODEL_PATH.exists():
        with lzma.open(ARCHIVE_PATH, "rb") as source:
            with MODEL_PATH.open("wb") as target:
                shutil.copyfileobj(source, target)
    return MODEL_PATH


def load_generated_model(path: Path | None = None) -> ModuleType:
    model_path = path or materialize_generated_model()
    spec = importlib.util.spec_from_file_location("modelwright_example_fable_2020", model_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load generated model from {model_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def build_facade(module: ModuleType | None = None) -> ModelFacade:
    generated_model = module or load_generated_model()
    return ModelFacade(
        generated_model,
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


def run_example():
    facade = build_facade()
    values = facade.calculate()
    for cell_ref, expected in FABLE_SCENARIO_OUTPUTS.items():
        observed = values[cell_ref]
        if observed != expected:
            raise RuntimeError(f"{cell_ref} expected {expected!r}, observed {observed!r}")
    return {
        "outputs": outputs_frame(facade),
        "scenario_selection_slice": table_frame(facade, "scenario_selection_slice"),
        "report": report_frames(facade, "scenario_selection"),
    }


if __name__ == "__main__":
    frames = run_example()
    print(frames["outputs"])
    print(frames["scenario_selection_slice"])
