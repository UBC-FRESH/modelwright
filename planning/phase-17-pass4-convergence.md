# Phase 17 Pass 4 Convergence

Date: 2026-06-20

## Scope

This pass implemented the fourth P17.3 semantics slice:

- `VLOOKUP` translation and generated standalone Python support;
- exact-match lookup with `FALSE` or equivalent range-lookup values;
- approximate-match lookup with `TRUE` or omitted range-lookup values;
- row-preserving table-array rendering for VLOOKUP ranges;
- structured-reference resolution for table data-body and whole-table references:
  - `Table[]`;
  - `Table[#Data]`;
  - `Table[#All]`.

The first VLOOKUP attempt exposed that most private-workbook VLOOKUP calls used table structured references as table arrays. The completed pass therefore includes table-array structured-reference support rather than only explicit cell-range VLOOKUP support.

## Verification

Local verification passed:

- `.venv/bin/python -m ruff check .`;
- `.venv/bin/python -m pytest`;
- `.venv/bin/sphinx-build -b html docs _build/html -W`;
- `git diff --check`.

The full pytest suite had 94 passing tests after this pass.

## Private Diagnostic Delta

Pass 3 private diagnostic pass:

- formula cells: 215,728;
- translated formula cells: 185,128;
- first-failure unsupported functions: 24,486;
- first-failure unsupported structured references: 5,808;
- first-failure unsupported error references: 306;
- generated direct-output subset validated against cached workbook values: 10 outputs, 0 mismatches.

Completed pass 4 private diagnostic pass:

- formula cells: 215,728;
- translated formula cells: 209,394;
- first-failure unsupported functions: 220;
- first-failure unsupported structured references: 5,808;
- first-failure unsupported error references: 306;
- generated direct-output subset validated against cached workbook values: 10 outputs, 0 mismatches;
- `formulas` oracle validation remained blocked by oracle calculation failure.

Net movement from pass 3 to pass 4:

- translated formulas increased by 24,266;
- first-failure unsupported functions decreased by 24,266;
- `VLOOKUP` is no longer a first-failure function blocker;
- structured-reference and error-reference first failures returned to their prior baseline after table-array references were resolved;
- cached generated validation remained green for the selected direct-output subset.

## Remaining Blockers

Sanitized remaining first-failure categories after pass 4:

- unsupported functions: 220, attributed to `OFFSET` from the prior remaining-function diagnostic;
- unsupported structured references: 5,808;
- unsupported error references: 306;
- validation oracle: `formulas` still reports oracle calculation failure.

`OFFSET` should not be translated casually. It is volatile/reference-returning and can describe dynamic ranges whose provenance and validation policy should be explicit before generated code reproduces them.

## Convergence Assessment

This pass is convergent under the Phase 17 convergence contract because it:

- materially increased translated formula count;
- eliminated the dominant remaining `VLOOKUP` function blocker;
- expanded structured-reference support for whole-table and table data-body references that are required by real workbook VLOOKUP formulas;
- expanded tracked synthetic fixture coverage for explicit-range and table-backed VLOOKUP forms;
- kept generated cached-value validation passing for the selected private direct-output subset.

This pass still does not prove full private-workbook equivalence. The next decision is whether to address `OFFSET` in P17.3, inspect the remaining structured references, or close P17.3 and move to P17.4 validation closeout with explicit residual blockers.

## Next Pass Direction

Recommended next action: inspect remaining structured-reference shapes and `OFFSET` usage before adding more translation behavior.

Possible outcomes:

- add a constrained `OFFSET` implementation if all remaining uses are static and provenance-safe;
- leave `OFFSET` as a sharper deferred diagnostic if it depends on dynamic references;
- resolve additional structured-reference forms if they are table metadata forms rather than calculation semantics;
- proceed to P17.4 closeout if remaining blockers are structural and should move to later phases.
