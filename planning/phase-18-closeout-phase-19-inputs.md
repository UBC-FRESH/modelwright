# Phase 18 Closeout And Phase 19 Inputs

Date: 2026-06-20

## Scope Closed

Phase 18 turned the prior extraction, dependency graph, formula translation, generation, and validation
pieces into an explicit conversion-planning surface.

Completed pieces:

- conversion-plan contract in `planning/conversion-plan-contract.md`;
- package records and `build_conversion_plan`;
- public external FABLE Calculator benchmark metadata, checksums, and canonical ignored local paths;
- `scripts/materialize_fable_benchmarks.py` plus `scripts/bootstrap_dev_env.sh --benchmarks`;
- `sheetforge conversion plan` CLI;
- residual-blocker classification for extraction, named ranges, formula extraction, graphing,
  translation, generation, cached validation, and oracle validation diagnostics;
- Read the Docs Sphinx theme configuration aligned with the other FRESH lab packages.

The conversion plan remains a status report, not a generated workbook clone or proof of equivalence.

## Closeout Workflow Evidence

The closeout workflow was run with stdout and stderr redirected to:

```text
tmp/logs/p18-closeout-classified-plan-verification.log
```

Local ignored plan outputs:

```text
tmp/conversion-plans/p18-synthetic-conversion-plan.json
tmp/conversion-plans/p18-fable-2020-conversion-plan.json
```

The synthetic fixture conversion plan reported:

- workflow status: extraction, dependency graph, and formula translation passed;
- formula cells: 5;
- translated formula cells: 5;
- translation coverage: 1.0;
- generation, cached validation, and oracle validation: not run;
- residual blocker: 5 missing cached formula values from the generated fixture workbook.

The 2020 FABLE primary benchmark conversion plan reported:

- workflow status: extraction, dependency graph, and formula translation passed;
- overall status: partial;
- sheets: 54;
- cells: 395,482;
- formula cells: 296,976;
- translated formula cells: 296,976;
- untranslated formula cells: 0;
- translation coverage: 1.0;
- named ranges: 128;
- dependency edges: 3,543,800;
- semantic edges: 1,771,900;
- execution edges: 1,771,900.

Sanitized 2020 diagnostic summary:

- workbook extraction: 1 unsupported external link;
- named ranges: 6 unresolved named ranges;
- formula extraction: 15,235 missing cached formula values;
- formula extraction: 1,748,603 structured-reference diagnostics kept visible at extraction level;
- formula extraction: 474 volatile-function diagnostics;
- graph: 1 circular dependency;
- formula translation: no diagnostics.

The 2020 residual-blocker classification now reports:

- `unsupported_external_link`: `external_dependency`, deferred;
- `unresolved_named_range`: `unsupported_reference_semantics`, next target;
- `missing_cached_formula_value`: `missing_cached_values`, deferred;
- `unsupported_structured_reference`: `unsupported_reference_semantics`, deferred;
- `unsupported_volatile_function`: `unsupported_formula_semantics`, deferred;
- `circular_dependency`: `graph_semantics`, next target.

The generated recommendations are:

- resolve named-range semantics or document why unresolved ranges are out of conversion scope;
- define graph semantics or reporting policy for the circular dependency.

## Verification

Targeted closeout verification passed:

- conversion-plan and CLI tests;
- focused Ruff checks;
- synthetic and 2020 conversion-plan CLI runs;
- Sphinx docs build with warnings treated as errors;
- `git diff --check`.

Full repository verification should be run before the Phase 18 PR is opened.

## Phase 19 Inputs

Phase 19 should resolve or explicitly scope the residual blockers exposed by conversion planning before
automating validation reports. Automated validation is not credible if it only packages unresolved
named-range, circular dependency, external link, volatile-function, structured-reference, or cached-value
blockers into nicer JSON.

Highest-priority inputs:

- unresolved named-range resolution or explicit out-of-scope classification;
- circular dependency semantics and generated-model policy;
- external workbook dependency policy;
- volatile-function policy beyond currently constrained static translations;
- structured-reference extraction diagnostic policy so supported table references are not counted as
  unresolved conversion blockers;
- cached-value validation policy tied to generated output selection;
- native verbose progress output for long-running conversion-plan and evaluation commands so workbook
  runs can be monitored without waiting for final JSON output;
- persisted local logs under `tmp/logs/` for every real-workbook benchmark pass;
- repeated 2020 FABLE primary benchmark run as the Phase 19 acceptance target.

Phase 19 should treat the 2020 benchmark as the primary convergence target, the 2019 benchmark as a
broken-reference regression case, and the 2021 benchmark as a later stress benchmark.

Generated-model execution, oracle orchestration, cached-value comparison, and evaluation report CLI work
should move to Phase 20 unless a narrow slice is needed to prove a Phase 19 blocker resolution.
