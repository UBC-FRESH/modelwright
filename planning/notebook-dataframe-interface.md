# Notebook DataFrame Interface

Phase 30 adds a notebook-facing interaction layer on top of `modelwright.wrappers`.

The product boundary is deliberately narrow: analysts should be able to use a live Python kernel to
inspect declared model structure, change scenario inputs, recalculate, render declared tables as
`pandas.DataFrame` objects, and compare baseline-vs-scenario outputs without treating raw
`Sheet!A1` dictionaries or generated source as the normal interface.

## Layering Decision

The intended stack is:

```text
generated model -> ModelFacade -> notebook/DataFrame helpers
```

`ModelFacade` remains the lower-level semantic adapter around generated `calculate(inputs=None) ->
dict[str, object]` models. Phase 30 should not move pandas into the core wrapper path. The notebook
layer should consume public wrapper declarations and views:

- `ModelFacade.inputs()`
- `ModelFacade.outputs()`
- `ModelFacade.scenario(...)`
- `ModelFacade.calculate(...)`
- `ModelFacade.inspect(...)`
- `ModelFacade.table(...)`
- `ModelFacade.report(...)`

## Module Boundary

The preferred initial module is `modelwright.notebooks`.

Rationale:

- The release claim is notebook-facing workflow, not only generic tabular conversion.
- The module can host DataFrame helpers now and still leave room for later notebook-specific display
  affordances if evidence justifies them.
- The lower-level `modelwright.wrappers` API can stay independent of pandas and Jupyter assumptions.

The initial implementation should provide pure helper functions rather than adding methods directly
to `ModelFacade`. That keeps optional dependency handling local to the notebook adapter and avoids
turning wrapper facades into a broad display surface too early.

## Optional Dependency Policy

Add a `notebook` optional extra that installs pandas:

```toml
[project.optional-dependencies]
notebook = [
  "pandas>=2"
]
```

The `modelwright.notebooks` module should import pandas lazily from helper calls, not at package
import time. If pandas is missing, raise a clear notebook-layer exception that tells users to install
`modelwright[notebook]`.

Pandas should not become a core package dependency during this phase.

## Initial Helper Sketch

Candidate module-level helpers:

```python
from modelwright.notebooks import (
    compare_scenarios_frame,
    inputs_frame,
    outputs_frame,
    report_frames,
    scenario_frame,
    table_frame,
)
```

Expected behavior:

- `inputs_frame(facade, scenario=None)` returns one row per declared input.
- `outputs_frame(facade, scenario=None)` returns one row per declared output.
- `scenario_frame(scenario)` returns one row per scenario input override.
- `table_frame(facade, "name", scenario=None)` returns a DataFrame whose visible index and columns
  use declared row and column labels while cell references remain available as metadata columns or
  attrs.
- `report_frames(facade, "name", scenario=None)` returns a mapping that contains cell and table
  DataFrames for a declared report bundle.
- `compare_scenarios_frame(facade, baseline, scenario, cells=None)` returns a tidy comparison
  DataFrame for declared outputs by default, or for an explicit cell-name/ref selection.

## Comparison Columns

Scenario comparison should include these fields where practical:

- `name`
- `label`
- `cell_ref`
- `baseline_value`
- `scenario_value`
- `absolute_change`
- `percent_change`
- `unit`
- `role`
- `description`

Percent change should only be populated for numeric values with a non-zero numeric baseline.
Textual, missing, or zero-baseline comparisons should remain explicit rather than raising.

## Non-Goals

Phase 30 must not claim:

- full spreadsheet UI;
- dashboard server;
- widget framework;
- automatic recovery of workbook semantic names or table meanings;
- stable public API compatibility;
- compact runtime IR production readiness;
- Excel-backed recalculation equivalence.

## Verification Plan

Always-on tests should cover the tracked synthetic generated-model workflow and prove that DataFrame
helpers do not change generated calculation behavior.

Opt-in benchmark coverage may extend the existing FABLE wrapper test pattern behind
`MODELWRIGHT_RUN_FABLE_BENCHMARKS=1`. Generated FABLE models, raw validation outputs, and source
workbooks must remain under ignored `tmp/`.

## Implementation Result

The first implementation uses `modelwright.notebooks` and exposes these helpers:

- `inputs_frame(facade, scenario=None)`
- `outputs_frame(facade, scenario=None)`
- `scenario_frame(scenario)`
- `table_frame(facade, name, scenario=None)`
- `report_frames(facade, name, scenario=None)`
- `compare_scenarios_frame(facade, baseline, scenario, cells=None)`

Tables display with declared row and column labels. Workbook provenance stays attached through
`DataFrame.attrs`, including sheet, range, and cell references.

The implementation delegates value resolution through the facade cache path where available. This is
important for large generated models: notebook display helpers should not accidentally trigger
multiple full generated-model recalculations when they are formatting already-calculated results.

Verification completed:

- `scripts/bootstrap_dev_env.sh`
- `.venv/bin/python -m ruff check .`
- `.venv/bin/python -m pytest -vv`
- `.venv/bin/sphinx-build -b html docs _build/html -W`
- `.venv/bin/python scripts/verify_docs_theme.py _build/html`
- `MODELWRIGHT_RUN_FABLE_BENCHMARKS=1 .venv/bin/python -m pytest -vv tests/test_fable_wrapper_benchmark.py`

The opt-in FABLE notebook wrapper benchmark passed in 149.67 seconds using ignored local artifacts
under `tmp/p26-fable-full-validation/`.

## Examples Gallery

The P30 release adds a tracked `examples/` directory and Sphinx Examples Gallery:

- `examples/synthetic/notebook_interface.py` is a tiny runnable example using a generated-model-shaped
  `calculate(inputs=None)` function, `ModelFacade`, and notebook DataFrame helpers.
- `examples/fable_2020/notebook_interface.py` is a production-size wrapper example over the generated
  2020 FABLE benchmark model.
- `examples/fable_2020/generated_fable_2020_model.py.xz` tracks the generated Python output in
  compressed form. The uncompressed module is about 117 MiB, which is above ordinary GitHub per-file
  limits, so the example script decompresses it into ignored `tmp/examples/fable_2020/` before import.

The original FABLE workbook remains untracked.
