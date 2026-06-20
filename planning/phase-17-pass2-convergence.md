# Phase 17 Pass 2 Convergence

Date: 2026-06-20

## Scope

This pass implemented the second P17.3 semantics slice:

- scalar logical functions: `AND`, `OR`;
- scalar error handling: `IFERROR`;
- scalar and range aggregations: `SUM`, `MIN`, `MAX`, `AVERAGE`;
- text concatenation function: `CONCATENATE`;
- generated Python helpers for flattening range arguments, averaging values, and lazy `IFERROR` evaluation;
- extraction records for worksheet table metadata;
- dependency-graph resolution for supported structured references:
  - table whole-column references such as `Table[Column]`;
  - table current-row references such as `Table[[#This Row],[Column]]`;
  - implicit current-row references such as `[@Column]` when the target cell is inside a known table;
- a fast-fail translation path for unresolved structured references so large workbooks do not scan all graph edges for each unsupported reference.

It also expanded the tracked supported-semantics fixture harness under `tests/fixtures/supported_semantics/` so the clean-checkout fixture now covers the currently supported operators, scalar functions, range aggregations, and supported structured-reference forms.

## Verification

Local verification passed:

- `.venv/bin/python -m ruff check .`;
- `.venv/bin/python -m pytest`;
- `.venv/bin/sphinx-build -b html docs _build/html -W`;
- `git diff --check`.

The full pytest suite had 91 passing tests after this pass.

## Private Diagnostic Delta

Pass 1 private diagnostic pass:

- formula cells: 215,728;
- translated formula cells: 52,972;
- first-failure unsupported functions: 162,450;
- first-failure unsupported error references: 306;
- first-failure unsupported structured references: not yet exposed as a major translation blocker.

An intermediate simple-function pass without table resolution was non-convergent:

- translated formula cells dropped to 3,931;
- true structured-reference failures dominated translation diagnostics;
- unresolved structured references caused a severe translation slowdown late in the private workbook pass.

The completed pass 2 private diagnostic pass:

- formula cells: 215,728;
- translated formula cells: 72,437;
- first-failure unsupported functions: 137,177;
- first-failure unsupported structured references: 5,808;
- first-failure unsupported error references: 306;
- generated direct-output subset validated against cached workbook values: 10 outputs, 0 mismatches;
- `formulas` oracle validation remained blocked by oracle calculation failure.

Net movement from pass 1 to completed pass 2:

- translated formulas increased by 19,465;
- first-failure unsupported functions decreased by 25,273;
- supported structured-reference forms were converted into ordinary cell/range references for graphing and translation;
- unresolved structured references now fail fast with a sharp diagnostic instead of causing an O(graph-size) scan for each formula.

## Remaining Blockers

The largest remaining first-failure category is unsupported functions. Sanitized private diagnostics after pass 2 show that criteria and lookup functions are now the next high-impact implementation set:

- `SUMIFS`;
- `VLOOKUP`;
- `COUNTIFS`;
- `COUNTIF`;
- `SUMIF`.

Remaining structured-reference failures are lower count and should be inspected as a separate sub-pass. The current supported table-reference implementation is intentionally constrained to current-row and whole-column references that can be mapped to explicit cells or ranges using extracted table metadata.

`#REF!` remains an explicit unsupported error-reference diagnostic. That is preferable to silent translation because source-workbook error semantics need a validation policy before generated code should reproduce them.

## Convergence Assessment

This pass is convergent under the Phase 17 convergence contract because it:

- materially increased translated formula count;
- reduced unsupported function first failures;
- replaced many structured-reference blockers with explicit table-backed cell/range dependencies;
- expanded generated Python support while keeping cached-value validation green for the generated direct-output subset;
- identified and fixed a private-workbook performance trap in unresolved structured-reference translation.

This pass does not prove full private-workbook equivalence. It proves the next layer of blockers. P17.3 should continue with criteria and lookup functions, then rerun the same private diagnostic loop.

## Next Pass Direction

The next P17.3 implementation pass should target:

1. Criteria functions: `SUMIF`, `SUMIFS`, `COUNTIF`, `COUNTIFS`.
2. Lookup function: `VLOOKUP`.
3. Sanitized inspection of the remaining structured-reference forms after criteria/lookup support lands.

Each new supported function must be added to the tracked supported-semantics fixture before the private workbook pass is considered convergent.
