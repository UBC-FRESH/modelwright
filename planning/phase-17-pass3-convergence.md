# Phase 17 Pass 3 Convergence

Date: 2026-06-20

## Scope

This pass implemented the third P17.3 semantics slice:

- criteria functions: `SUMIF`, `SUMIFS`, `COUNTIF`, and `COUNTIFS`;
- generated Python helpers for criteria matching, including equality, inequality, numeric comparisons, booleans, and simple wildcard matching;
- tracked supported-semantics fixture coverage for single-criteria sums/counts and multi-criteria sums/counts.

The implementation keeps criteria behavior inside generated standalone Python modules. Generated models do not depend on the Sheetforge runtime to evaluate supported criteria functions.

## Verification

Local verification passed:

- `.venv/bin/python -m ruff check .`;
- `.venv/bin/python -m pytest`;
- `.venv/bin/sphinx-build -b html docs _build/html -W`;
- `git diff --check`.

The full pytest suite had 92 passing tests after this pass.

## Private Diagnostic Delta

Pass 2 private diagnostic pass:

- formula cells: 215,728;
- translated formula cells: 72,437;
- first-failure unsupported functions: 137,177;
- first-failure unsupported structured references: 5,808;
- first-failure unsupported error references: 306;
- generated direct-output subset validated against cached workbook values: 10 outputs, 0 mismatches.

Pass 3 private diagnostic pass:

- formula cells: 215,728;
- translated formula cells: 185,128;
- first-failure unsupported functions: 24,486;
- first-failure unsupported structured references: 5,808;
- first-failure unsupported error references: 306;
- generated direct-output subset validated against cached workbook values: 10 outputs, 0 mismatches;
- `formulas` oracle validation remained blocked by oracle calculation failure.

Net movement from pass 2 to pass 3:

- translated formulas increased by 112,691;
- first-failure unsupported functions decreased by 112,691;
- structured-reference and error-reference first failures were unchanged;
- cached generated validation remained green for the selected direct-output subset.

## Remaining Function Blockers

Sanitized remaining function first-failure counts after pass 3:

| Function | Count | P17 stance |
| --- | ---: | --- |
| `VLOOKUP` | 24,266 | Next P17.3 implementation pass. |
| `OFFSET` | 220 | Defer unless a constrained, provenance-safe subset is clear; otherwise sharpen diagnostics. |

`VLOOKUP` is now the dominant remaining formula-function blocker. `OFFSET` remains risky because it is volatile/reference-returning and can depend on dynamic ranges that are harder to prove from static extraction alone.

## Convergence Assessment

This pass is convergent under the Phase 17 convergence contract because it:

- materially increased translated formula count;
- eliminated all observed criteria-function first failures from the private workbook's first-failure diagnostics;
- reduced the unsupported-function blocker set to `VLOOKUP` and `OFFSET`;
- expanded tracked synthetic coverage for the newly supported criteria semantics;
- kept generated cached-value validation passing for the selected private direct-output subset.

This pass does not prove full private-workbook equivalence. It exposes the next layer: lookup semantics, remaining structured-reference forms, explicit error references, and the validation-oracle blocker.

## Next Pass Direction

The next P17.3 implementation pass should target `VLOOKUP`.

Minimum expectations:

- support exact-match lookup over explicit ranges and resolved table ranges;
- decide whether approximate-match lookup is safe enough for P17 or should receive a specific unsupported diagnostic;
- add tracked supported-semantics fixture coverage for supported `VLOOKUP` forms;
- rerun the private workbook convergence loop and compare translated count, remaining diagnostics, generated subset, and validation status.
