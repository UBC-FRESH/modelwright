# Phase 17 Pass 1 Convergence

Date: 2026-06-20

## Scope

This pass implemented the first low-risk P17.3 parser/expression slice:

- boolean literals: `TRUE` and `FALSE`;
- unary minus;
- exponentiation operator: `^`;
- string concatenation operator: `&`;
- explicit `#REF!` error-reference diagnostics.

It also added a tracked supported-semantics fixture harness under `tests/fixtures/supported_semantics/`. That fixture is intentionally separate from private workbooks and should grow whenever Sheetforge adds support for new functions, operators, token forms, or reference forms.

## Verification

Local verification passed:

- `.venv/bin/python -m ruff check .`;
- `.venv/bin/python -m pytest`;
- `.venv/bin/sphinx-build -b html docs _build/html -W`;
- `git diff --check`.

The full pytest suite had 85 passing tests after this pass.

## Private Diagnostic Delta

Baseline private diagnostic pass:

- formula cells: 215,728;
- translated formula cells: 51,274;
- untranslated formula cells: 164,454;
- first-failure unsupported functions: 137,769;
- first-failure unsupported formula tokens: 24,707;
- first-failure unsupported operators: 1,978.

Pass 1 private diagnostic pass:

- formula cells: 215,728;
- translated formula cells: 52,972;
- untranslated formula cells: 162,756;
- first-failure unsupported functions: 162,450;
- first-failure unsupported error references: 306;
- first-failure unsupported formula tokens: 0;
- first-failure unsupported operators: 0.

Net movement:

- translated formulas increased by 1,698;
- unsupported operator first failures dropped from 1,978 to 0;
- unsupported formula-token first failures dropped from 24,707 to 0;
- `#REF!` moved from generic unsupported token diagnostics to explicit `unsupported_error_reference` diagnostics;
- unsupported function first failures increased because previously hidden downstream function blockers became visible.

## Newly Exposed Function Blockers

The pass exposed additional first-failure function categories that were hidden behind earlier token/operator blockers:

- `VLOOKUP`;
- `MAX`.

The current top function blockers remain sanitized function names and counts only in ignored local outputs. No private formulas, sheet names, workbook names, named ranges, values, or paths were copied into tracked files.

## Convergence Assessment

This pass is convergent under the Phase 17 convergence contract because it:

- increased translated formula count;
- eliminated first-failure unsupported operator diagnostics;
- eliminated generic first-failure unsupported formula-token diagnostics;
- replaced `#REF!` generic token failure with a sharper diagnostic;
- expanded tracked synthetic coverage for all currently supported semantics.

Generated private-workbook subset growth was not attempted in this pass. The next implementation pass should target high-count function blockers and then rerun candidate generation and validation to test whether the generated subset can expand.

## Next Pass Direction

The next P17.3 pass should start with scalar and lookup/function blockers now visible in first-failure diagnostics:

- `SUMIFS`;
- `IFERROR`;
- `VLOOKUP`;
- `AND`;
- `SUMIF`;
- `COUNTIFS`;
- `MIN`;
- `OR`;
- `SUM`;
- `AVERAGE`;
- `CONCATENATE`;
- `OFFSET`;
- `MAX`.

`OFFSET` should still be treated cautiously because it is volatile/reference-returning. If constrained support is not feasible, it should receive a sharper unsupported diagnostic.
