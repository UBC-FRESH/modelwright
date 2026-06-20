# Phase 21 Full Benchmark Model Materialization And Validation Plan

Date: 2026-06-20

## Purpose

Phase 21 turns clean benchmark conversion evidence into executable generated-model evidence.

Phase 20 proved that Sheetforge can execute and validate a generated model when the generated-model
contract is explicit. It also preserved clean 2020 FABLE benchmark extraction, dependency graphing, and
formula translation evidence. Phase 21 owns the missing bridge: infer and materialize a generated Python
model for selected benchmark outputs, then validate those outputs against cached or oracle values.

## Starting Evidence

Phase 20 closeout evidence:

- synthetic generated-model evaluation passed through the CLI;
- 2020 FABLE extraction completed for 54 sheets, 395,482 extracted cells, and 296,976 formula cells;
- 2020 FABLE dependency graphing completed with 3,543,800 dependency edges and no graph diagnostics;
- 2020 FABLE formula translation completed for 296,976 of 296,976 formulas with no translation diagnostics;
- full 2020 workbook equivalence is not proven because no full generated-model contract or generated model
  has been materialized for that workbook.

## Tasks

### P21.1 Infer Generated-Model Contracts From Dependency Graphs

Goal: infer a `GeneratedModuleContract`, translated expression subset, and input constants for selected
outputs by walking dependency graph edges.

Acceptance criteria:

- define selected-output-to-contract inference inputs;
- traverse dependency graph dependencies required for selected outputs;
- classify unresolved dependencies as explicit input boundaries or blockers;
- preserve workbook provenance for generated symbols;
- add synthetic tests before applying the workflow to the 2020 FABLE benchmark.

### P21.2 Materialize The 2020 FABLE Generated Model

Goal: emit an ignored generated Python model for the selected 2020 FABLE benchmark scope.

Acceptance criteria:

- topologically order generated symbols for the selected benchmark scope;
- write generated model artifacts under ignored `tmp/`;
- run materialization in verbose mode with a tail-able log;
- record generation diagnostics, model size, and runtime constraints.

### P21.3 Validate Selected 2020 FABLE Outputs

Goal: compare selected generated 2020 FABLE outputs against cached workbook values or an explicit oracle.

Acceptance criteria:

- define selected benchmark output scenarios;
- compare generated outputs against cached or oracle values;
- preserve missing cached values and oracle failures as validation blockers;
- write ignored local validation reports and verbose logs.

### P21.4 Rerun Benchmark Convergence Loop

Goal: rerun the benchmark after P21 fixes and classify every remaining blocker.

Acceptance criteria:

- rerun the 2020 FABLE benchmark after contract inference, generation, and validation work;
- classify each remaining blocker as resolved, deferred, out of scope, or next target;
- record what equivalence has and has not been proven;
- open the Phase 21 PR only after verification passes.

## Convergence Rule

Do not accept a planning-only result when a blocker is concrete enough to reproduce. The loop is:

1. run the benchmark workflow with verbose logs;
2. identify the next concrete blocker;
3. implement the smallest package-backed fix or explicitly scope the blocker;
4. rerun the benchmark workflow;
5. repeat until selected benchmark equivalence is proven or remaining limitations are sharply scoped.

## Non-Goals

- Do not claim full workbook equivalence from translation coverage alone.
- Do not treat missing cached values as generated-model failures.
- Do not commit private workbooks, generated models, or bulky local reports.
- Do not create service or UI surfaces in this phase.
