CLI Reference
=============

Sheetforge exposes a Typer-based CLI:

.. code-block:: bash

   sheetforge --help

Workflow groups:

- ``sheetforge workbook``: extraction and dependency graph commands;
- ``sheetforge model``: generated Python model commands;
- ``sheetforge validation``: validation report commands.

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
