Private Workbooks
=================

Private source workbooks, raw extracts, generated clones, logs, and validation reports are local working
artifacts. They should remain under ignored ``tmp/`` paths unless the maintainer explicitly approves a
small sanitized tracked artifact.

Recommended local layout:

.. code-block:: text

   tmp/
     private-workbooks/
     private-evaluations/
     generated-models/
     logs/

Tracked documentation may summarize private evaluation findings only after removing workbook names,
worksheet names, formulas, values, business meaning, and raw output payloads.

Safe tracked notes should focus on:

- sanitized counts;
- unsupported feature categories;
- runtime and stop conditions;
- validation status;
- follow-up implementation priorities.

Unsafe tracked content includes:

- raw workbook files;
- raw formulas;
- raw cell values;
- private paths;
- generated Python clones of private workbooks;
- full validation reports from private workbooks.
