Limitations And Boundaries
==========================

Modelwright is pre-release software. It is suitable for controlled research and package-backed workflow
experiments, not for unsupervised conversion of arbitrary workbooks.

Known limitations include:

- structured table-reference formulas;
- unsupported Excel functions;
- unsupported parser token forms;
- unsupported operators;
- external workbook references;
- volatile functions;
- unresolved named ranges;
- formula cells without cached values;
- full-workbook recalculation oracle failures;
- no broad conversion-plan API yet;
- no release compatibility guarantee.

The project should report unsupported semantics explicitly. It should not silently translate workbook
behavior it does not understand.
