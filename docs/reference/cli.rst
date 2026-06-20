CLI Reference
=============

Sheetforge exposes a Typer-based CLI:

.. code-block:: bash

   sheetforge --help

Workflow groups:

- ``sheetforge workbook``: extraction and dependency graph commands;
- ``sheetforge model``: generated Python model commands;
- ``sheetforge validation``: validation report commands;
- ``sheetforge conversion``: conversion planning reports.

Workbook Commands
-----------------

.. code-block:: bash

   sheetforge workbook extract path/to/workbook.xlsx > tmp/extraction.json
   sheetforge workbook graph path/to/workbook.xlsx > tmp/dependency-graph.json

Model Commands
--------------

.. code-block:: bash

   sheetforge model generate \
     --contract tmp/contract.json \
     --expressions tmp/expressions.json \
     --constants tmp/constants.json \
     --out tmp/generated_model.py \
     > tmp/generation-result.json

Validation Commands
-------------------

.. code-block:: bash

   sheetforge validation report \
     --scenario tmp/scenario.json \
     --generated-values tmp/generated-values.json \
     --oracle-values tmp/oracle-values.json \
     > tmp/validation-report.json

Conversion Commands
-------------------

.. code-block:: bash

   sheetforge conversion plan path/to/workbook.xlsx \
     --plan-id conversion-plan:example \
     --benchmark-role ad_hoc_private \
     > tmp/conversion-plan.json

The conversion plan command runs workbook extraction, dependency graph construction, and formula
translation, then emits a JSON report with coverage, diagnostics, residual blockers, and next-action
recommendations. It does not generate a full workbook clone or run validation by itself; those stages are
reported as ``not_run`` until explicit generation and validation artifacts are supplied by later workflow
steps.
