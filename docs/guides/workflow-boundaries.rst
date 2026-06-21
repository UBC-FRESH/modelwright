Workflow Boundaries
===================

Modelwright is organized as separate workflow stages. The separation is deliberate: each stage emits
inspectable records before another stage depends on them.

Workbook Extraction
-------------------

``modelwright.extraction`` reads workbook structure with ``openpyxl`` and emits records for sheets,
cells, formulas, named ranges, and extraction diagnostics.

Dependency Graphing
-------------------

``modelwright.graph`` turns extracted formula references into semantic and execution dependency edges.
It preserves provenance so unsupported or unresolved references remain visible.

Formula Translation
-------------------

``modelwright.formulas`` translates a narrow supported formula subset into expression records. Unsupported
functions, token forms, and operators produce diagnostics rather than silent generated behavior.

Python Generation
-----------------

``modelwright.generation`` writes standalone Python modules from explicit generated-module contracts and
translated expression records. Generated modules are local artifacts and should normally stay under
ignored paths such as ``tmp/``.

Conversion Planning
-------------------

``modelwright.conversion`` summarizes extraction, graphing, formula translation, generation, validation,
and residual blockers into an inspectable conversion plan. A conversion plan can report partial success
without claiming that a full workbook clone or equivalence proof exists.

The CLI wrapper is:

.. code-block:: bash

   modelwright conversion plan path/to/workbook.xlsx > tmp/conversion-plan.json

This command runs extraction, dependency graphing, and formula translation. It leaves generation and
validation as explicit later workflow steps and reports those stages as ``not_run``.

Validation
----------

``modelwright.validation`` builds reports from already-observed generated and oracle values.
``modelwright.formulas_oracle`` provides an optional pure-Python oracle boundary for workbooks supported
by the ``formulas`` package.

No One-Step Conversion Yet
--------------------------

Modelwright does not yet expose a broad ``convert workbook`` command. Real workbook evaluation showed
that conversion plans must first explain which formulas were translated, which cells were unsupported,
which outputs were generated, and which oracle was used for validation.
