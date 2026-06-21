# Phase 20 Validation And Evaluation Plan

Date: 2026-06-20

## Purpose

Phase 20 turns the Phase 19 blocker-resolution evidence into repeatable generated-model execution and
validation reporting.

The 2020 FABLE benchmark is no longer blocked by extraction, graph, or translation diagnostics. Phase 20
should therefore stop treating conversion status as a planning report only and start producing repeatable
evidence about generated Python behavior.

## Starting Evidence

Phase 19 final 2020 FABLE conversion-plan evidence:

- formula cells: 296,976;
- translated formula cells: 296,976;
- untranslated formula cells: 0;
- graph diagnostics: empty;
- translation diagnostics: empty;
- structured-reference extraction diagnostics: resolved provenance;
- volatile-function extraction diagnostics: resolved provenance;
- external-link diagnostics: deferred to explicit materialize, mock, or reject policy;
- missing cached formula values: deferred to oracle/cached-validation strategy.

## Tasks

### P20.1 Generated Model Execution API

Goal: execute generated Python modules from explicit contracts and return JSON-serializable observed
outputs and diagnostics.

Acceptance criteria:

- define the smallest package API needed to execute generated Python in tests;
- keep execution separate from workbook extraction;
- support explicit input overrides and output refs;
- add synthetic fixture tests before using benchmark workbooks.

Status: complete.

Result:

- added `modelwright.execution` with `ExecutionDiagnostic`, `GeneratedExecutionResult`, and
  `execute_generated_model`;
- kept execution tied to explicit `GeneratedModuleContract` objects and generated Python module paths;
- isolated generated-model execution from workbook extraction;
- returned JSON-serializable output values and execution diagnostics;
- added synthetic tests for default execution, input overrides, payload round-trip, missing generated
  model files, and missing declared outputs.

### P20.2 Oracle And Cached-Value Validation Orchestration

Goal: compare generated outputs against cached workbook values and oracle outputs where available.

Acceptance criteria:

- preserve missing cached values as validation limitations, not generation failures;
- preserve oracle failures as explicit validation blockers;
- produce validation reports with clear output counts, mismatches, and blockers.

Status: complete.

Result:

- added `modelwright.evaluation` with `ValidationEvaluationResult` and `evaluate_generated_model`;
- orchestrated generated-model execution, cached workbook values from `WorkbookRecord`, and optional
  oracle results;
- kept missing cached values visible as validation diagnostics and missing-oracle-output comparisons;
- preserved oracle diagnostics from `OracleResult` in oracle-backed validation reports;
- added JSON round-trip support for validation reports used by evaluation results;
- added focused synthetic tests for cached validation success, missing cached values, oracle blockers, and
  evaluation-result payload round-trip.

### P20.3 Evaluation Report CLI And JSON Outputs

Goal: expose the repeatable evaluation workflow through thin CLI commands and JSON reports.

Acceptance criteria:

- add CLI wrappers over package APIs only;
- emit JSON suitable for ignored local benchmark reports;
- keep verbose progress logging available for long workbook runs.

Status: complete.

Result:

- added `modelwright model execute` for `execute_generated_model`;
- added `modelwright validation evaluate` for `evaluate_generated_model`;
- allowed cached validation from either source workbook extraction or existing `WorkbookRecord` JSON;
- allowed oracle-backed validation from already-materialized `OracleResult` JSON;
- kept verbose progress on stderr so stdout remains JSON;
- documented CLI workflow boundaries and added focused CLI tests.

### P20.4 Repeatable Evaluation Closeout

Goal: run the synthetic and 2020 FABLE evaluation workflows and record what is proven.

Acceptance criteria:

- run synthetic evaluation end to end;
- run 2020 FABLE evaluation with verbose logging;
- write ignored local reports under `tmp/`;
- record what is proven, what remains unproven, and Phase 21 inputs.

Status: complete.

Local evidence:

- `tmp/p20-synthetic-evaluation/summary.json`;
- `tmp/p20-synthetic-evaluation/evaluation-result.json`;
- `tmp/p20-synthetic-evaluation/generated_model.py`;
- `tmp/p20-fable-2020-evaluation/conversion-plan.json`;
- `tmp/p20-fable-2020-evaluation/closeout-summary.json`;
- `tmp/logs/p20-synthetic-evaluation.log`;
- `tmp/logs/p20-fable-2020-evaluation.log`;
- `tmp/logs/p20-fable-2020-evaluation-closeout.log`.

Result:

- synthetic generated-model generation, execution, and validation ran end to end through the CLI;
- synthetic generated outputs were `Summary!B2 = 70.2` and `Summary!B3 = "ok"`;
- synthetic cached validation status was `pass` with no mismatches;
- 2020 FABLE extraction completed for 54 sheets, 395,482 extracted cells, and 296,976 formula cells;
- 2020 FABLE dependency graphing completed with 3,543,800 dependency edges and no graph diagnostics;
- 2020 FABLE formula translation completed for 296,976 of 296,976 formulas with no translation
  diagnostics.

What this proves:

- the generated-model execution API and CLI can execute a generated Python module from an explicit
  contract;
- the validation evaluation API and CLI can compare generated outputs against cached workbook values when
  the generated-model boundary is explicit;
- the 2020 FABLE benchmark remains clean through extraction, graphing, and translation.

What this does not prove:

- full 2020 FABLE workbook equivalence is not proven;
- no full 2020 FABLE generated Python model was materialized in Phase 20;
- no selected 2020 FABLE output set was validated against cached or oracle values in Phase 20.

Phase 21 inputs:

- infer generated-model contracts from dependency graphs and selected outputs;
- choose benchmark validation outputs and required input boundaries;
- topologically order generated symbols for large workbooks;
- materialize a full 2020 FABLE generated model before claiming workbook equivalence;
- compare selected benchmark outputs against cached or oracle values and continue the
  blocker-find-resolve-rerun loop until convergence.

## Non-Goals

- Do not claim full workbook equivalence before generated outputs are compared against usable oracle or
  cached workbook values.
- Do not silently ignore external dependencies or missing cached values.
- Do not create broad service or UI surfaces in this phase.
