from __future__ import annotations

import importlib.util
import lzma
from pathlib import Path
from types import ModuleType

import pytest


ROOT = Path(__file__).resolve().parents[1]


def load_example(path: Path, module_name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_synthetic_notebook_example_runs() -> None:
    module = load_example(ROOT / "examples/synthetic/notebook_interface.py", "synthetic_notebook_example")

    frames = module.run_example()

    assert frames["outputs"].set_index("name").loc["projected", "value"] == 132.0
    assert frames["summary_grid"].loc["volume", "primary"] == 132.0
    assert frames["comparison"].set_index("name").loc["projected", "absolute_change"] == pytest.approx(22.0)


def test_fable_generated_model_archive_is_tracked_and_readable() -> None:
    archive_path = ROOT / "examples/fable_2020/generated_fable_2020_model.py.xz"

    assert archive_path.exists()
    assert archive_path.stat().st_size < 10_000_000
    with lzma.open(archive_path, "rb") as archive:
        prefix = archive.read(128)

    assert b"Generated Modelwright model" in prefix
