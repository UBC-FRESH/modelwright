# Private Workbook Evaluation Findings: eval-001

Date: 2026-06-20

## Scope

This note records sanitized findings from the first private workbook evaluation. Raw workbook files, source paths, worksheet names, named ranges, formulas, cell values, generated Python, logs, and full reports remain under ignored `tmp/`.

The source was a private `.xlsx` workbook evaluated locally as `eval-001`.

## What Ran

The local evaluation exercised the current Modelwright pipeline against the private workbook:

- workbook extraction;
- dependency graph construction;
- formula translation with indexed dependency lookup;
- generated Python model creation for a narrow translated subset;
- generated model execution;
- comparison against cached workbook output values;
- attempted `formulas` oracle execution.

## Sanitized Counts

The workbook-scale facts from the sanitized local summary were:

- sheets: 24;
- extracted cells: 270,205;
- value cells: 54,477;
- formula cells: 215,728;
- named ranges: 6;
- dependency edges: 2,636,538;
- translated formula cells: 51,274;
- selected generated outputs: 10;
- selected scalar input dependencies: 3.

## Validation Result

The generated model subset validated successfully against cached workbook values:

- generated subset: 10 direct-output formulas;
- comparison oracle: cached values saved in the workbook;
- mismatches: 0;
- status: pass.

This proves that Modelwright can extract this private workbook, build a dependency graph, translate a limited formula subset, generate Python for a direct-output subset, run that generated Python, and match cached workbook values for the selected outputs.

It does not prove full workbook equivalence.

## Oracle Limitation

The pure-Python `formulas` oracle could not calculate the private workbook. The blocker was an Excel structured-reference formula form used by table-like workbook constructs. In plain language: the oracle library encountered a table-reference formula syntax that it does not parse, so it could not be used as a full recalculation oracle for this workbook.

The current validation evidence therefore comes from cached workbook values, not from an independent recalculation of the workbook.

## Unsupported Feature Categories

The evaluation exposed these sanitized unsupported or incomplete categories:

- structured table-reference formulas block the current `formulas` oracle;
- many formula functions are outside Modelwright's current translator subset;
- some formula token forms are outside the current parser;
- some operators are outside the current parser;
- external workbook references are present at scale;
- volatile functions are present;
- some named ranges are unresolved by the current extraction model;
- some formula cells lack cached values.

The largest translator gaps by count were:

- unsupported functions: 137,769;
- unsupported formula tokens: 24,707;
- unsupported operators: 1,978.

## Implications

Phase 13 should not claim full private workbook conversion or full spreadsheet equivalence.

The useful result is narrower and still important: the pipeline can handle real workbook scale for extraction, graphing, and formula-translation diagnostics, and it can generate and validate a small direct-output subset.

The next implementation priorities should be evidence-driven:

- add support for structured references or record them as first-class unsupported references;
- expand formula function coverage based on observed unsupported-function categories;
- improve parser coverage for unsupported token and operator forms;
- decide whether cached values, `formulas`, Excel-backed validation, or a hybrid should be the validation oracle for real workbooks;
- make private evaluation reporting a repeatable local command once the API is stable enough.
