# Phase 17 Pass 5 Convergence

Date: 2026-06-20

## Scope

This pass implemented the fifth P17.3 semantics slice:

- constrained cross-table current-row structured-reference resolution;
- row-offset mapping from a formula's containing table to the referenced table;
- support only when both source and target tables have the same data-row count;
- tracked synthetic fixture coverage for generated-model behavior using this structured-reference form.

The pass deliberately does not add general table joins, implicit relational semantics, dynamic table lookup, or broad structured-reference interpretation. It converts only the observed equal-height current-row pattern into explicit cell dependencies.

## Verification

Focused local verification passed before the full-suite run:

- `.venv/bin/python -m pytest tests/test_dependency_graph.py tests/test_supported_semantics_fixture.py tests/test_formula_translation.py`;
- `.venv/bin/python -m ruff check src/modelwright/graph.py tests/test_dependency_graph.py tests/fixtures/supported_semantics/build_workbook.py tests/test_supported_semantics_fixture.py`.

The private diagnostic pass was run with very-verbose output redirected to an ignored local log:

- `tmp/private-evaluations/eval-001/p17-pass5-cross-table-current-row-run.log`.

Ignored local sanitized and raw report snapshots were preserved under `tmp/private-evaluations/eval-001/`.

## Private Diagnostic Delta

Pass 4 private diagnostic pass:

- formula cells: 215,728;
- translated formula cells: 209,394;
- first-failure unsupported functions: 220;
- first-failure unsupported structured references: 5,808;
- first-failure unsupported error references: 306;
- generated direct-output subset validated against cached workbook values: 10 outputs, 0 mismatches;
- `formulas` oracle validation remained blocked by oracle calculation failure.

Completed pass 5 private diagnostic pass:

- formula cells: 215,728;
- translated formula cells: 215,202;
- first-failure unsupported functions: 220;
- first-failure unsupported structured references: 0;
- first-failure unsupported error references: 306;
- generated direct-output subset validated against cached workbook values: 10 outputs, 0 mismatches;
- `formulas` oracle validation remained blocked by oracle calculation failure.

Net movement from pass 4 to pass 5:

- translated formulas increased by 5,808;
- structured-reference first-failure blockers decreased from 5,808 to 0;
- cached generated validation remained green for the selected direct-output subset;
- residual first-failure blockers narrowed to `OFFSET` and explicit error references.

## Remaining Blockers

Sanitized remaining first-failure categories after pass 5:

- unsupported functions: 220, attributed to `OFFSET` from the remaining-function diagnostic;
- unsupported error references: 306;
- validation oracle: `formulas` still reports oracle calculation failure.

`OFFSET` remains the only unsupported function first-failure category in the private diagnostic pass. It should receive either constrained, provenance-safe support or a deliberately sharper deferred diagnostic. Explicit `#REF!` references are already identified and should not be translated into silent generated behavior.

## Convergence Assessment

This pass is convergent under the Phase 17 convergence contract because it:

- materially increased translated formula count;
- eliminated remaining structured-reference first failures in the private diagnostic pass;
- added tracked fixture coverage for the supported structured-reference shape;
- kept generated cached-value validation passing for the selected private direct-output subset;
- narrowed the residual blocker set enough for a clear P17.3 closeout decision.

This pass still does not prove full private-workbook equivalence. It proves that the structured-reference blocker layer has been resolved for the current private diagnostic pass and exposes the next residual layer: `OFFSET`, explicit error references, and the validation-oracle blocker.

## Next Pass Direction

Recommended next action: decide whether P17.3 should add constrained `OFFSET` support or close P17.3 with `OFFSET` explicitly deferred to a later validation/planning phase.

Before implementing `OFFSET`, inspect whether the remaining uses can be reduced to static reference construction with literal row and column offsets. If the references depend on dynamic height, width, volatile behavior, or unsupported structured-reference composition, keep `OFFSET` blocked with a sharper diagnostic rather than generating uncertain Python semantics.
