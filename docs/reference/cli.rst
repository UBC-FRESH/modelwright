CLI Reference
=============

Modelwright exposes a Typer-based CLI:

.. code-block:: bash

   modelwright --help

Workflow groups:

- ``modelwright workbook``: extraction and dependency graph commands;
- ``modelwright model``: generated Python model commands;
- ``modelwright validation``: validation report and evaluation commands;
- ``modelwright conversion``: conversion planning reports.

Workbook Commands
-----------------

.. code-block:: bash

   modelwright workbook extract path/to/workbook.xlsx > tmp/extraction.json
   modelwright workbook graph path/to/workbook.xlsx > tmp/dependency-graph.json

Model Commands
--------------

.. code-block:: bash

   modelwright model infer-contract path/to/workbook.xlsx \
     --module-name generated_model \
     --output-ref "Summary!B2" \
     --output-ref "Summary!B3" \
     --contract tmp/contract.json \
     --expressions tmp/expressions.json \
     --constants tmp/constants.json \
     --verbose \
     > tmp/inference-result.json

   modelwright model generate \
     --contract tmp/contract.json \
     --expressions tmp/expressions.json \
     --constants tmp/constants.json \
     --out tmp/generated_model.py \
     > tmp/generation-result.json

   modelwright model execute \
     --contract tmp/contract.json \
     --model tmp/generated_model.py \
     --inputs tmp/input-overrides.json \
     > tmp/generated-values.json

``infer-contract`` extracts the workbook, builds the dependency graph, translates formulas, and writes
the three JSON inputs consumed by ``model generate``. Output refs may also be supplied with
``--output-refs-file`` as a JSON array of cell refs. See :doc:`../guides/generated-model-artifacts`
for the end-to-end generated-artifact workflow.

Validation Commands
-------------------

.. code-block:: bash

   modelwright validation report \
     --scenario tmp/scenario.json \
     --generated-values tmp/generated-values.json \
     --oracle-values tmp/oracle-values.json \
     > tmp/validation-report.json

   modelwright validation evaluate \
     --contract tmp/contract.json \
     --model tmp/generated_model.py \
     --scenario tmp/scenario.json \
     --workbook-record tmp/extraction.json \
     --oracle-result tmp/oracle-result.json \
     --verbose \
     > tmp/evaluation-report.json

The evaluation command executes the generated Python model, then builds cached-workbook and/or
oracle-backed validation reports when those inputs are supplied. Verbose progress is written to stderr so
stdout remains valid JSON for redirected reports.

Conversion Commands
-------------------

.. code-block:: bash

   modelwright conversion plan path/to/workbook.xlsx \
     --plan-id conversion-plan:example \
     --benchmark-role ad_hoc_private \
     > tmp/conversion-plan.json

The conversion plan command runs workbook extraction, dependency graph construction, and formula
translation, then emits a JSON report with coverage, diagnostics, residual blockers, and next-action
recommendations. It does not generate a full workbook clone or run validation by itself; those stages are
reported as ``not_run`` until explicit generation and validation artifacts are supplied by later workflow
steps.
