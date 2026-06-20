# Phase 19 Residual Blocker Resolution Plan

Date: 2026-06-20

## Purpose

Phase 19 is the convergence phase for the residual blockers exposed by the 2020 FABLE conversion plan.
The goal is not to make nicer reports around unresolved problems. The goal is to remove, resolve, or
explicitly scope every blocker that prevents the benchmark import from being a serious conversion target.

## Starting Evidence

The Phase 18 closeout conversion plan for the 2020 FABLE primary benchmark reported:

- formula cells: 296,976;
- translated formula cells: 296,976;
- untranslated formula cells: 0;
- translation coverage: 1.0;
- translation diagnostics: none;
- overall status: partial because generation and validation are not yet fully automated.

Residual blocker categories:

- `unsupported_external_link`: `external_dependency`, deferred;
- `unresolved_named_range`: `unsupported_reference_semantics`, next target;
- `missing_cached_formula_value`: `missing_cached_values`, deferred;
- `unsupported_structured_reference`: `unsupported_reference_semantics`, deferred;
- `unsupported_volatile_function`: `unsupported_formula_semantics`, deferred;
- `circular_dependency`: `graph_semantics`, next target.

## Phase 19 Tasks

### P19.1 Resolve Or Scope Unresolved Named Ranges

Goal: eliminate ambiguous named-range blocker status.

Acceptance criteria:

- inspect the 6 unresolved named-range diagnostics from the 2020 benchmark;
- distinguish unsupported syntax, workbook defects, hidden/external scope, and safe out-of-scope names;
- implement resolver support where the workbook semantics are clear and generic;
- otherwise classify each unresolved name as out-of-scope or source/workbook dependency with provenance;
- rerun the 2020 conversion plan and show no unclassified named-range blockers.

Status: complete.

Result:

- inspected the 6 unresolved named-range diagnostics from the 2020 benchmark;
- identified 5 table-column structured-reference defined names that openpyxl did not expose through
  `defined_name.destinations`;
- added generic extraction support that resolves those table-column defined names to concrete cell ranges;
- preserved range dependencies in graph/index behavior so formula translation sees the range, not only
  the first expanded cell;
- classified the remaining named-range diagnostic as `named_range_source_error`, a source workbook
  `#REF!` defined-name defect;
- verified the `ProductList` defined-name defect is not referenced by worksheet formulas, data
  validations, or any other raw XLSX XML package entry outside the defined-name declaration itself;
- marked that stale defined-name defect as out of scope for conversion blocker resolution.

P19.1 rerun evidence:

- 2020 named-range diagnostics changed from `unresolved_named_range: 6` to `named_range_source_error: 1`;
- the remaining `named_range_source_error` is stale workbook metadata, not an active calculation blocker;
- formula cells remained 296,976;
- translated formula cells remained 296,976;
- translation diagnostics remained empty;
- no unclassified named-range blockers remain.

Local ignored evidence:

```text
tmp/logs/p19-named-range-inspection.log
tmp/logs/p19-named-range-targeted-verification.log
tmp/logs/p19-named-range-2020-rerun.log
tmp/conversion-plans/p19-named-range-fable-2020.json
```

### P19.2 Define Circular Dependency Semantics And Policy

Goal: stop treating circularity as a vague graph warning.

Acceptance criteria:

- inspect the 2020 circular dependency diagnostic;
- determine whether it affects selected/generated outputs;
- decide whether Sheetforge should support fixed-point/iterative calculation, preserve a blocking
  diagnostic, or explicitly exclude the cycle from generated scope;
- update graph or conversion-plan policy so circular dependencies become actionable;
- rerun the 2020 conversion plan and show circular dependency status is resolved, scoped, or retained as
  a deliberate blocker.

Status: complete.

Result:

- inspected the 2020 circular dependency diagnostic with verbose local logging;
- found that the reported two-cell cycles were not evidence of a workbook iterative-calculation model;
- traced the cycle shape to formulas that use constrained static `OFFSET(...,-1,0)` references against
  current-row table structured references;
- determined that formula translation already resolves those cases as previous-row concrete cell
  references, while the dependency graph was still using the raw current-row base reference as the
  execution dependency;
- updated graph execution semantics so constrained static three-argument `OFFSET` calls record the
  shifted execution source cell and preserve the concrete base cell for formula translation;
- kept simple direct circular references as graph diagnostics;
- added synthetic regression coverage proving previous-row `OFFSET` patterns do not produce false
  circular dependency diagnostics;
- reran the 2020 FABLE primary benchmark conversion plan with verbose progress logging.

P19.2 rerun evidence:

- graph diagnostics changed from `circular_dependency: 1` to empty;
- formula cells remained 296,976;
- translated formula cells remained 296,976;
- untranslated formula cells remained 0;
- translation diagnostics remained empty;
- conversion-plan workflow is now blocked only by generation/validation not being run and the remaining
  P19.3 policy/provenance blockers.

Local ignored evidence:

```text
tmp/logs/p19-circular-inspection.log
tmp/logs/p19-static-offset-targeted-tests.log
tmp/logs/p19-static-offset-2020-conversion-plan.log
tmp/conversion-plans/p19-static-offset-fable-2020.json
```

### P19.3 Resolve Deferred Workbook Dependency And Volatile/Cache Blockers

Goal: give each deferred blocker an implementation or policy owner.

Acceptance criteria:

- external link policy: document whether to inline, mock, reject, or require external workbook inputs;
- volatile-function policy: distinguish already-supported constrained static forms from unsupported
  dynamic/volatile semantics;
- structured-reference extraction diagnostic policy: prevent supported table references from appearing
  as unresolved conversion blockers while preserving provenance for unsupported forms;
- cached-value policy: define when missing cached values block validation, when they are irrelevant, and
  when a recalculation oracle is required;
- update conversion-plan classification to avoid treating deferred policy items as hand-waved success.

Status: complete.

Policy decisions:

- External dependencies are not silently inlined. A workbook with external links requires explicit
  external workbook materialization, mock inputs, or rejection policy before full conversion or validation.
- Missing cached formula values are not generation blockers. They are validation evidence blockers unless
  a recalculation oracle is available or the selected validation outputs have usable cached values.
- Structured-reference extraction diagnostics are provenance once graphing and translation have resolved
  those references. They should stay visible in diagnostic summaries but should not be treated as active
  conversion blockers when graph and translation diagnostics are clean.
- Volatile-function extraction diagnostics are risk provenance once formula translation is clean. For the
  2020 benchmark, the remaining volatile diagnostics are not active formula-semantics blockers; they are
  retained for validation-risk review.
- Source workbook `named_range_source_error` remains out of scope when unreferenced by formulas or
  validation rules.

P19.3 rerun evidence:

- graph diagnostics: empty;
- translation diagnostics: empty;
- formula cells: 296,976;
- translated formula cells: 296,976;
- untranslated formula cells: 0;
- `unsupported_structured_reference`: disposition `resolved`, extraction provenance only;
- `unsupported_volatile_function`: disposition `resolved`, validation-risk provenance only;
- `unsupported_external_link`: disposition `deferred`, owned by explicit external-dependency policy;
- `missing_cached_formula_value`: disposition `deferred`, owned by oracle/cached-validation strategy.

Local ignored evidence:

```text
tmp/logs/p19-policy-targeted-tests.log
tmp/logs/p19-policy-2020-conversion-plan.log
tmp/conversion-plans/p19-policy-fable-2020.json
```

### P19.4 Rerun 2020 Benchmark To Convergence And Closeout

Goal: prove that Phase 19 resolved the residual-blocker layer enough to move to automated validation.

Acceptance criteria:

- run the 2020 FABLE conversion plan with verbose logging to `tmp/logs/`;
- produce ignored local JSON reports under `tmp/conversion-plans/`;
- show every residual blocker is resolved, scoped out with provenance, or explicitly retained as a real
  blocker with a named next phase;
- update `ROADMAP.md`, `CHANGE_LOG.md`, this planning note, and GitHub issues;
- only then activate Phase 20 validation/evaluation automation.

## Non-Goals

- Do not build broad validation report polish before blocker ownership is explicit.
- Do not claim full workbook equivalence from translation coverage alone.
- Do not silently generate Python behavior for external links, volatile semantics, circular references, or
  unavailable cached/oracle values.
