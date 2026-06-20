Workflow Boundaries
===================

Sheetforge is organized as separate workflow stages. The separation is deliberate: each stage emits
inspectable records before another stage depends on them.

Workbook Extraction
-------------------

``sheetforge.extraction`` reads workbook structure with ``openpyxl`` and emits records for sheets,
cells, formulas, named ranges, and extraction diagnostics.

Dependency Graphing
-------------------

``sheetforge.graph`` turns extracted formula references into semantic and execution dependency edges.
It preserves provenance so unsupported or unresolved references remain visible.

Formula Translation
-------------------

``sheetforge.formulas`` translates a narrow supported formula subset into expression records. Unsupported
functions, token forms, and operators produce diagnostics rather than silent generated behavior.

Python Generation
-----------------

``sheetforge.generation`` writes standalone Python modules from explicit generated-module contracts and
translated expression records. Generated modules are local artifacts and should normally stay under
ignored paths such as ``tmp/``.

Validation
----------

``sheetforge.validation`` builds reports from already-observed generated and oracle values.
``sheetforge.formulas_oracle`` provides an optional pure-Python oracle boundary for workbooks supported
by the ``formulas`` package.

No One-Step Conversion Yet
--------------------------

Sheetforge does not yet expose a broad ``convert workbook`` command. Real workbook evaluation showed
that conversion plans must first explain which formulas were translated, which cells were unsupported,
which outputs were generated, and which oracle was used for validation.
