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
