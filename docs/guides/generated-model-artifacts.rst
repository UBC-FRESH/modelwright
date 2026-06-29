Generated Model Artifacts
=========================

Modelwright generated Python models are built in two steps. First, Modelwright infers the JSON
artifacts that describe the selected model boundary. Then ``modelwright model generate`` turns those
JSON artifacts into standalone Python source.

The three generation inputs are:

- ``contract.json``: the generated module contract, including workbook id, module name, input refs,
  output refs, and generated symbol provenance.
- ``expressions.json``: translated formula expressions for the formula cells needed by the selected
  outputs.
- ``constants.json``: literal workbook values used as default generated-model inputs.

These files are derived artifacts. Keep them under ignored local paths such as ``tmp/`` unless a
maintainer explicitly approves a small tracked example.

Infer The Generation Inputs
---------------------------

The user must choose the output refs that define the generated model boundary. Modelwright does not
guess which workbook cells represent the right business outputs for a production workbook.

For a small model, output refs can be supplied directly:

.. code-block:: bash

   modelwright model infer-contract path/to/workbook.xlsx \
     --module-name generated_example_model \
     --output-ref "Summary!B2" \
     --output-ref "Summary!B3" \
     --contract tmp/generated-model/contract.json \
     --expressions tmp/generated-model/expressions.json \
     --constants tmp/generated-model/constants.json \
     --verbose \
     > tmp/generated-model/inference-result.json

For a larger model, keep the output refs in a JSON array:

.. code-block:: json

   [
     "Summary!B2",
     "Summary!B3"
   ]

Then pass that file to the inference command:

.. code-block:: bash

   modelwright model infer-contract path/to/workbook.xlsx \
     --module-name generated_example_model \
     --output-refs-file tmp/generated-model/output_refs.json \
     --contract tmp/generated-model/contract.json \
     --expressions tmp/generated-model/expressions.json \
     --constants tmp/generated-model/constants.json \
     --verbose \
     > tmp/generated-model/inference-result.json

The command extracts the workbook, builds a dependency graph, translates formulas, infers the selected
generated-model contract, writes the three JSON inputs, and emits the full inference result JSON to
stdout. Verbose progress is written to stderr so redirected stdout remains valid JSON.

Generate The Python Model
-------------------------

After inference succeeds, generate the Python source:

.. code-block:: bash

   modelwright model generate \
     --contract tmp/generated-model/contract.json \
     --expressions tmp/generated-model/expressions.json \
     --constants tmp/generated-model/constants.json \
     --out tmp/generated-model/generated_example_model.py \
     > tmp/generated-model/generation-result.json

The generated Python module is also a derived local artifact. For private or production-sized
workbooks, keep it under ignored ``tmp/`` paths unless the project has explicitly decided to track a
sanitized or compressed example.

Execute And Validate
--------------------

Execute the generated model:

.. code-block:: bash

   modelwright model execute \
     --contract tmp/generated-model/contract.json \
     --model tmp/generated-model/generated_example_model.py \
     > tmp/generated-model/generated-values.json

Validation is a separate evidence step. A generated model that imports and executes is not
automatically equivalent to the source workbook. Compare generated outputs against cached workbook
values, an oracle, or another documented validation source before interpreting the numbers as
equivalent:

.. code-block:: bash

   modelwright validation evaluate \
     --contract tmp/generated-model/contract.json \
     --model tmp/generated-model/generated_example_model.py \
     --scenario path/to/scenario.json \
     --workbook path/to/workbook.xlsx \
     --verbose \
     > tmp/generated-model/evaluation-report.json

FABLE Workbook Versions
-----------------------

For a new FABLE Calculator version, keep the workbook, output-ref list, inferred JSON artifacts, and
generated Python model in version-specific ignored directories. For example:

.. code-block:: text

   tmp/private-workbooks/2022_Open_FABLECalculator.xlsx
   tmp/generated-models/fable-2022/output_refs.json
   tmp/generated-models/fable-2022/contract.json
   tmp/generated-models/fable-2022/expressions.json
   tmp/generated-models/fable-2022/constants.json
   tmp/generated-models/fable-2022/generated_fable_2022_model.py

The output-ref list is the important workbook-specific decision. FABLE Pyculator can discover
notebook-facing workbook surfaces, but Modelwright still needs explicit output refs to decide which
calculation boundary to materialize as a generated Python model.
