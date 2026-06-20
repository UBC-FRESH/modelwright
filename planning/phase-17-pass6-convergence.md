# Phase 17 Pass 6 Convergence

Date: 2026-06-20

## Scope

This pass implemented the sixth P17.3 semantics slice:

- constrained static `OFFSET` translation;
- support only for the three-argument form `OFFSET(reference, rows, columns)`;
- support only when the base reference resolves to one concrete cell;
- support only when row and column offsets are static integers;
- translation to a concrete shifted cell reference rather than a generated runtime `OFFSET` function.

This is intentionally narrower than full Excel `OFFSET`. It does not support dynamic offsets, height/width arguments, range-returning `OFFSET`, volatile runtime behavior, or references that cannot be resolved during extraction and translation.

## Verification

Focused local verification passed before the private diagnostic run:

- `.venv/bin/python -m pytest tests/test_formula_translation.py tests/test_supported_semantics_fixture.py`.

The private diagnostic pass was run with very-verbose output redirected to an ignored local log:

- `tmp/private-evaluations/eval-001/p17-pass6-static-offset-run.log`.

Ignored local sanitized and raw report snapshots were preserved under `tmp/private-evaluations/eval-001/`.

## Private Diagnostic Delta

Pass 5 private diagnostic pass:

- formula cells: 215,728;
- translated formula cells: 215,202;
- first-failure unsupported functions: 220;
- first-failure unsupported structured references: 0;
- first-failure unsupported error references: 306;
- generated direct-output subset validated against cached workbook values: 10 outputs, 0 mismatches;
- `formulas` oracle validation remained blocked by oracle calculation failure.

Completed pass 6 private diagnostic pass:

- formula cells: 215,728;
- translated formula cells: 215,422;
- first-failure unsupported functions: 0;
- first-failure unsupported structured references: 0;
- first-failure unsupported error references: 306;
- generated direct-output subset validated against cached workbook values: 10 outputs, 0 mismatches;
- `formulas` oracle validation remained blocked by oracle calculation failure.

Net movement from pass 5 to pass 6:

- translated formulas increased by 220;
- unsupported-function first-failure blockers decreased from 220 to 0;
- cached generated validation remained green for the selected direct-output subset;
- residual formula-translation blockers narrowed to explicit error references.

The workbook extraction diagnostics still record volatile-function appearances because the source workbook uses `OFFSET`. That extraction diagnostic remains useful provenance. The translation layer now supports only the observed static, reference-resolved subset.

## Remaining Blockers

Sanitized remaining first-failure categories after pass 6:

- unsupported error references: 306;
- validation oracle: `formulas` still reports oracle calculation failure.

The explicit error references are not a missing Excel function or parser feature. They represent workbook formulas containing `#REF!` references, and Sheetforge should not silently generate normal Python behavior for them. They should remain sharp diagnostics until a higher-level conversion plan can decide whether to exclude, repair, or model them as errors.

## Convergence Assessment

This pass is convergent under the Phase 17 convergence contract because it:

- cleared the unsupported-function first-failure category in the private diagnostic pass;
- added tracked fixture coverage for the supported static `OFFSET` shape;
- kept generated cached-value validation passing for the selected private direct-output subset;
- narrowed P17.3 from semantics expansion into closeout and validation decisions.

This pass still does not prove full private-workbook equivalence. It proves that the current private diagnostic pass no longer exposes ordinary unsupported function or structured-reference first failures. The remaining work is to close out Phase 17 honestly: document explicit error references, record the oracle limitation, and decide the next phase boundary for conversion planning and repeatable validation.

## Next Phase Direction

Recommended next action: close P17.3 and move to P17.4 validation closeout.

P17.4 should:

- rerun the full default verification path;
- record the final P17 translated-formula count and residual diagnostics;
- decide whether explicit error references remain blocked by design;
- document that the pure-Python `formulas` oracle is still not a usable full-workbook oracle for this private workbook;
- prepare Phase 18 inputs for conversion planning and residual-blocker reporting.
