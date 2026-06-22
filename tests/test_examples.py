from __future__ import annotations

import importlib.util
import json
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


def test_fable_scenario_output_manifest_seed_is_valid() -> None:
    manifest_path = ROOT / "examples/fable_2020/scenario_output_manifest.example.json"
    payload = json.loads(manifest_path.read_text())

    assert payload["schema_name"] == "modelwright-fable-pyculator-scenario-output-manifest"
    assert payload["schema_version"] == 1
    assert payload["workbook"]["local_workbook_path"].startswith("tmp/")
    assert payload["scenario"]["changed_inputs"]
    assert payload["outputs"][0]["comparison_status"] == "match"
    assert payload["run"]["status"] == "pass"


def notebook(path: str) -> dict:
    return json.loads((ROOT / path).read_text())


def source_text(cell: dict) -> str:
    source = cell.get("source", "")
    if isinstance(source, list):
        return "".join(source)
    return source


def output_text(cell: dict) -> str:
    chunks: list[str] = []
    for output in cell.get("outputs", []):
        if "text" in output:
            text = output["text"]
            chunks.append("".join(text) if isinstance(text, list) else text)
        data = output.get("data", {})
        text_plain = data.get("text/plain")
        if text_plain is not None:
            chunks.append("".join(text_plain) if isinstance(text_plain, list) else text_plain)
    return "\n".join(chunks)


def test_literate_notebooks_have_expected_structure() -> None:
    for notebook_path in [
        "examples/notebooks/synthetic-notebook-interface.ipynb",
        "examples/notebooks/fable-2020-notebook-interface.ipynb",
    ]:
        payload = notebook(notebook_path)
        cells = payload["cells"]

        assert payload["nbformat"] == 4
        assert payload["metadata"]["kernelspec"]["name"] == "python3"
        assert cells[0]["cell_type"] == "markdown"
        assert source_text(cells[0]).startswith("# ")
        assert sum(cell["cell_type"] == "markdown" for cell in cells) >= 5
        assert sum(cell["cell_type"] == "code" for cell in cells) >= 5

        for index, cell in enumerate(cells):
            if cell["cell_type"] == "code":
                assert index > 0
                assert cells[index - 1]["cell_type"] == "markdown"
                assert cell.get("outputs"), f"{notebook_path} code cell {index} has no stored output"


def test_synthetic_notebook_outputs_are_known_valid() -> None:
    payload = notebook("examples/notebooks/synthetic-notebook-interface.ipynb")
    outputs = "\n".join(output_text(cell) for cell in payload["cells"] if cell["cell_type"] == "code")

    assert "Declared inputs: ['base', 'growth']" in outputs
    assert "projected  Summary!B2  132.0" in outputs
    assert "volume   132.0        240" in outputs
    assert "projected          110.0          132.0            22.0            0.2" in outputs


def test_synthetic_notebook_code_cells_execute() -> None:
    payload = notebook("examples/notebooks/synthetic-notebook-interface.ipynb")
    namespace: dict[str, object] = {}
    for cell in payload["cells"]:
        if cell["cell_type"] == "code":
            exec(source_text(cell), namespace)

    comparison = namespace["compare_scenarios_frame"](
        namespace["facade"],
        namespace["baseline"],
        namespace["shock"],
    ).set_index("name")
    assert comparison.loc["projected", "scenario_value"] == 132.0
    assert comparison.loc["projected", "absolute_change"] == pytest.approx(22.0)


def test_fable_notebook_static_outputs_preserve_validation_boundary() -> None:
    payload = notebook("examples/notebooks/fable-2020-notebook-interface.ipynb")
    text = "\n".join(source_text(cell) + "\n" + output_text(cell) for cell in payload["cells"])

    assert "generated_fable_2020_model.py.xz" in text
    assert "281,741 comparable cached outputs" in text
    assert "SCENARIOS selection!D20': 2.146115426018433" in text
    assert "scenario_metric_3  SCENARIOS selection!D22  1.462761" in text
    assert "range_ref': 'D20:D22'" in text
