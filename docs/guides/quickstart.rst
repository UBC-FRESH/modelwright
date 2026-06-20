Quickstart
==========

Bootstrap a repo-local virtual environment:

.. code-block:: bash

   scripts/bootstrap_dev_env.sh

The script creates ``.venv/`` under the repository root and installs Sheetforge with the test,
quality, oracle, and documentation dependencies through the ``dev`` extra.

To also materialize public FABLE benchmark workbooks into ``tmp/private-workbooks/``:

.. code-block:: bash

   scripts/bootstrap_dev_env.sh --benchmarks

Activate the environment manually when useful:

.. code-block:: bash

   source .venv/bin/activate

Run the standard local checks:

.. code-block:: bash

   .venv/bin/python -m ruff check .
   .venv/bin/python -m pytest
   .venv/bin/sphinx-build -b html docs _build/html -W

CLI Shape
---------

The public CLI uses workflow groups:

.. code-block:: bash

   sheetforge workbook extract path/to/workbook.xlsx > tmp/extraction.json
   sheetforge workbook graph path/to/workbook.xlsx > tmp/dependency-graph.json
   sheetforge conversion plan path/to/workbook.xlsx > tmp/conversion-plan.json
   sheetforge model generate --contract tmp/contract.json --expressions tmp/expressions.json --out tmp/generated_model.py
   sheetforge validation report --scenario tmp/scenario.json --generated-values tmp/generated-values.json --oracle-values tmp/oracle-values.json
