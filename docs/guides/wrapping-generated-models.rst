Wrapping Generated Models
=========================

Generated Modelwright modules are calculation artifacts. They expose a small Python boundary, usually
``calculate(inputs=None) -> dict``, where keys are workbook cell references such as ``"Summary!B2"``.
That boundary is useful for validation and automation, but it is not a comfortable analyst interface
by itself.

The ``modelwright.wrappers`` module provides lightweight template primitives for building custom
facades around generated models. A facade can name meaningful inputs, define rectangular table views,
bundle reports, and preserve provenance back to the original workbook references.

Boundary
--------

Wrapper facades do not edit generated source code. They pass scenario input overrides to the generated
model and structure the returned values.

They also do not recreate a spreadsheet UI. Formatting, merged cells, hidden rows, formulas-as-visual
objects, and Excel editing remain outside this alpha API.

Minimal Example
---------------

Assume a generated model module has a ``calculate`` function:

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

Define a wrapper facade:

.. code-block:: python

   from modelwright.wrappers import ModelFacade, cell, report, table

   facade = ModelFacade(
       generated_model,
       cells=[
           cell("Inputs!B2", name="base", label="Base volume", role="input", unit="t"),
           cell("Inputs!B3", name="growth", label="Growth rate", role="input", unit="fraction"),
           cell("Summary!B2", name="projected", label="Projected volume", role="output", unit="t"),
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
           report("summary", cells=["base", "projected"], tables=["summary_grid"]),
       ],
   )

Run a scenario:

.. code-block:: python

   scenario = facade.scenario(inputs={"Inputs!B2": 50}).with_input("Inputs!B3", 0.2)
   outputs = facade.calculate(scenario)

Inspect a declared cell:

.. code-block:: python

   projected = facade.inspect("Summary!B2", scenario)
   assert projected.value == 60.0
   assert projected.cell_ref == "Summary!B2"

Read a table payload:

.. code-block:: python

   table_payload = facade.table("summary_grid", scenario).to_dict()

   assert table_payload["rows"] == ["volume", "status"]
   assert table_payload["columns"] == ["primary", "secondary"]
   assert table_payload["values"] == [[60.0, 100], ["ok", 55]]

Build a report payload:

.. code-block:: python

   summary = facade.report("summary", scenario)
   assert summary["cells"]["base"]["value"] == 50
   assert summary["tables"]["summary_grid"]["values"][0][0] == 60.0

Scenario Inputs
---------------

``Scenario`` objects are copy-on-write input override sets:

.. code-block:: python

   baseline = facade.scenario(inputs={"Inputs!B2": 100})
   high_growth = baseline.with_input("Inputs!B3", 0.25)

   assert baseline.inputs == {"Inputs!B2": 100}
   assert high_growth.inputs == {"Inputs!B2": 100, "Inputs!B3": 0.25}

Mutation means changing scenario inputs, not editing generated model code.

Table Declarations
------------------

The first table API is intentionally rectangular and explicit. A declaration such as
``sheet="Summary", range_ref="B2:C3"`` expands to row-major cell refs:

.. code-block:: python

   [["Summary!B2", "Summary!C2"], ["Summary!B3", "Summary!C3"]]

If row or column labels are supplied, their counts must match the range shape. When labels are omitted,
the wrapper uses workbook row numbers and column letters as stable fallback labels.

Alpha Limits
------------

The wrapper API is provisional. It is intended to make custom generated-model facades easier to write,
not to promise complete automatic workbook semantic recovery.

Current non-goals:

- full spreadsheet UI recreation;
- Excel-backed execution;
- automatic interpretation of all workbook layouts;
- visual formatting or workbook editing;
- stable public API compatibility before real wrapper use cases harden the design.
