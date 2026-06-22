Notebook Interface
==================

The wrapper facade API gives generated models analyst-facing names, tables, reports, and scenarios.
The ``modelwright.notebooks`` module adds the next layer: pandas-backed helpers that display those
facade views naturally in a live Jupyter kernel.

Install the optional notebook dependency when using these helpers:

.. code-block:: bash

   python -m pip install 'modelwright[notebook]'

The core package and ``modelwright.wrappers`` do not require pandas.

When using the tracked source-tree examples from a notebook stored under ``tmp/notebooks/``, add the
repository root to ``sys.path`` before importing from ``examples``:

.. code-block:: python

   from pathlib import Path
   import sys

   repo_root = Path.cwd().resolve()
   while repo_root.name != "sheetforge":
       repo_root = repo_root.parent

   sys.path.insert(0, str(repo_root))

Boundary
--------

Notebook helpers do not edit generated source code and do not recreate a spreadsheet UI. They convert
declared wrapper views into DataFrames so an analyst can inspect model structure, change scenario
inputs, recalculate, and compare results without manually reading raw ``Sheet!A1`` dictionaries.

Minimal Example
---------------

Assume a generated model module exposes ``calculate(inputs=None)``:

.. code-block:: python

   def calculate(inputs=None):
       inputs = inputs or {}
       base = inputs.get("Inputs!B2", 100)
       growth = inputs.get("Inputs!B3", 0.1)
       return {
           "Summary!B2": base * (1 + growth),
           "Summary!C2": base * 2,
           "Summary!B3": "ok",
           "Summary!C3": base + 5,
       }

Declare a facade around the generated model:

.. code-block:: python

   from modelwright.wrappers import ModelFacade, cell, report, table

   facade = ModelFacade(
       generated_model,
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

Render declared inputs and outputs:

.. code-block:: python

   from modelwright.notebooks import inputs_frame, outputs_frame

   scenario = facade.scenario(name="shock", inputs={"Inputs!B2": 50}).with_input("Inputs!B3", 0.2)

   inputs_frame(facade, scenario)
   outputs_frame(facade, scenario)

In Jupyter, those calls display tidy DataFrames with names, labels, cell references, roles, units,
values, and value-presence flags.

Render Tables
-------------

Declared rectangular tables become DataFrames whose visible row and column labels come from the
wrapper declaration:

.. code-block:: python

   from modelwright.notebooks import table_frame

   summary = table_frame(facade, "summary_grid", scenario)
   summary

Workbook provenance stays attached to the DataFrame:

.. code-block:: python

   summary.attrs["sheet"]
   summary.attrs["range_ref"]
   summary.attrs["cell_refs"]

Render Reports
--------------

Reports return a small mapping with a cell DataFrame and named table DataFrames:

.. code-block:: python

   from modelwright.notebooks import report_frames

   frames = report_frames(facade, "summary", scenario)
   frames["cells"]
   frames["tables"]["summary_grid"]

Compare Scenarios
-----------------

Scenario comparison is the core notebook loop:

.. code-block:: python

   from modelwright.notebooks import compare_scenarios_frame

   baseline = facade.scenario(name="baseline", inputs={"Inputs!B2": 100, "Inputs!B3": 0.1})
   shock = baseline.with_input("Inputs!B2", 120)

   compare_scenarios_frame(facade, baseline, shock)

The comparison DataFrame includes declared name, label, cell reference, baseline value, scenario
value, absolute change, percent change where numeric and meaningful, unit, role, and description.
Text comparisons and zero-baseline percent changes remain explicit rather than raising.

Scenario Inputs
---------------

Use ``scenario_frame`` to inspect the exact overrides being sent to the generated model:

.. code-block:: python

   from modelwright.notebooks import scenario_frame

   scenario_frame(shock)

Alpha Limits
------------

The notebook helpers are provisional. They are intended to make wrapped generated models usable in a
live Python kernel, not to promise a complete end-user application.

Current non-goals:

- full spreadsheet UI recreation;
- dashboard server or widget framework;
- automatic recovery of workbook semantic names or table meanings;
- visual formatting or workbook editing;
- Excel-backed recalculation equivalence;
- stable public API compatibility before real notebook workflows harden the design.
