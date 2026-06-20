# Phase 17 Closeout And Phase 18 Inputs

Date: 2026-06-20

## Scope Closed

Phase 17 expanded real-workbook formula semantics through an explicit blocker-find-resolve-rerun loop. The implemented slices were:

- boolean literals, unary minus, exponentiation, text concatenation, and explicit error-reference diagnostics;
- scalar functions including logical, error-handling, aggregation, and text concatenation forms;
- table-backed structured references for supported current-row, whole-column, whole-table, and data-body forms;
- criteria functions `SUMIF`, `SUMIFS`, `COUNTIF`, and `COUNTIFS`;
- lookup function `VLOOKUP`, including table-array structured references;
- constrained cross-table current-row structured references;
- constrained static `OFFSET` references.

The phase intentionally did not claim general Excel equivalence. It translated only semantics that could be represented with explicit provenance and tested generated Python behavior.

## Verification

Final local verification passed:

- `.venv/bin/python -m pytest`;
- `.venv/bin/python -m ruff check .`;
- `.venv/bin/sphinx-build -b html docs _build/html -W`;
- `git diff --check`.

The final test suite had 97 passing tests.

The final private diagnostic pass was run with very-verbose output redirected to ignored local logs and reports under `tmp/private-evaluations/eval-001/`.

## Final Sanitized Private Diagnostics

Final P17 private diagnostic counts:

- formula cells: 215,728;
- translated formula cells: 215,422;
- untranslated formula cells: 306;
- unsupported-function first failures: 0;
- unsupported structured-reference first failures: 0;
- explicit unsupported error references: 306;
- generated direct-output candidates: 10;
- selected generated outputs: 10;
- selected input dependencies: 13;
- cached generated validation: 10 outputs, 0 mismatches;
- `formulas` oracle validation: blocked by oracle calculation failure.

Other sanitized diagnostics still visible in the workbook evaluation:

- unresolved named ranges: 6;
- missing cached formula values: 15,560;
- volatile-function extraction diagnostics: 308;
- graph diagnostics: 1 circular dependency.

These are not all P17 translation blockers. They are important inputs for conversion planning, residual-risk reporting, and validation strategy.

## Residual Blocker Classification

Resolved in P17:

- unsupported functions observed as first-failure translation blockers;
- unsupported operator and token forms observed in the private diagnostic loop;
- structured-reference first-failure translation blockers;
- unresolved structured-reference translation performance traps.

Blocked by design:

- 306 formulas with explicit error references. Sheetforge should not silently turn workbook `#REF!` formulas into normal generated Python behavior. A conversion plan should classify these as repair, exclusion, error-preserving generated behavior, or out-of-scope workbook damage.

Deferred to structural design phases:

- circular dependency handling;
- unresolved named-range policy beyond currently supported workbook-level destinations;
- missing cached-value policy for validation examples;
- volatile-function risk reporting beyond the constrained static `OFFSET` translation subset;
- full-workbook oracle strategy after the pure-Python `formulas` oracle failed to calculate this private workbook.

## Convergence Decision

Phase 17 converged for formula-semantics expansion: repeated implementation passes reduced unsupported-function, unsupported-operator, unsupported-token, and structured-reference first-failure translation categories to zero in the private diagnostic pass.

Phase 17 did not prove full private-workbook equivalence. The generated subset still validates only against cached workbook values for selected direct outputs, and the pure-Python oracle remains blocked. The remaining 306 untranslated formulas are explicit error-reference formulas, which should be handled by conversion planning and residual reporting rather than by pretending the workbook has valid references.

## Phase 18 Inputs

Phase 18 should shift from adding formula semantics to building a conversion plan workflow.

The conversion plan should report:

- total formula, translated formula, and untranslated formula counts;
- translated formula coverage percentage;
- residual blocker categories and counts;
- whether each residual category is resolved, blocked by design, deferred, or out of target scope;
- generated-output subset selection and validation status;
- source-workbook diagnostics that affect conversion risk;
- oracle availability and reason when no full oracle is available.

For this private workbook, the first conversion-plan acceptance target should be a sanitized report that says:

- formula translation coverage is 215,422 of 215,728 formulas;
- all observed unsupported function and structured-reference first-failure categories are resolved;
- 306 explicit error-reference formulas remain blocked by design;
- cached generated validation passes for the selected direct-output subset;
- full oracle validation is unavailable through the current pure-Python backend.

Phase 18 should avoid adding more formula semantics unless the conversion plan exposes a concrete, newly prioritized blocker. The next project risk is no longer "unknown formula support"; it is making conversion status, residual blockers, generated outputs, and validation evidence repeatable and visible.
