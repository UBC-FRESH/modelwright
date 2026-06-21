Validation
==========

Validation is the evidence layer for generated model behavior.

Current validation support is deliberately narrow:

- scenarios identify expected output cells and comparison rules;
- generated values and oracle values are supplied as JSON mappings;
- reports compare scalar outputs and preserve mismatch diagnostics;
- optional oracle execution is available through the Python API for supported ``formulas`` workbooks.

Example report assembly:

.. code-block:: bash

   modelwright validation report \
     --scenario tests/fixtures/synthetic_model/baseline_scenario.json \
     --generated-values tmp/generated-values.json \
     --oracle-values tmp/oracle-values.json \
     > tmp/validation-report.json

Oracle Limits
-------------

The pure-Python ``formulas`` oracle is useful for controlled workbooks, but it is not a universal Excel
replacement. Real workbook evaluation has already shown structured-reference syntax that blocks this
oracle. Cached workbook values can be useful evidence, but they are not the same as independent
recalculation.
