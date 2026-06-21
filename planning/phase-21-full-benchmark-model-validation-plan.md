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

Status: complete.

Result:

- added `GeneratedContractInferenceResult`;
- added `infer_generated_module_contract`;
- inferred generated-model contracts from a workbook record, dependency graph, translated expressions,
  selected output refs, module name, and optional explicit input refs;
- walked execution dependency edges recursively so formula dependencies are ordered before dependent formula
  cells;
- classified missing cells, circular dependencies, diagnostic dependency edges, and non-cell dependency
  sources as generation diagnostics;
- preserved constants for inferred input cells and raw formula provenance for generated symbols;
- added synthetic tests proving the inferred contract generates and executes the same controlled model that
  was previously hand-declared.

### P21.2 Materialize The 2020 FABLE Generated Model

Goal: emit an ignored generated Python model for the selected 2020 FABLE benchmark scope.

Acceptance criteria:

- topologically order generated symbols for the selected benchmark scope;
- write generated model artifacts under ignored `tmp/`;
- run materialization in verbose mode with a tail-able log;
- record generation diagnostics, model size, and runtime constraints.

Status: complete.

Local evidence:

- `tmp/p21-fable-2020-materialization/generated_model.py`;
- `tmp/p21-fable-2020-materialization/contract-inference.json`;
- `tmp/p21-fable-2020-materialization/generation-result.json`;
- `tmp/p21-fable-2020-materialization/summary.json`;
- `tmp/logs/p21-fable-2020-materialization-rerun.log`.

Result:

- selected the ten cached benchmark outputs previously used for the 2020 IFNA evaluation:
  `SCENARIOS definition!J29`, `K29`, `L29`, `M29`, `N29`, `O29`, `S29`, `T29`, `U29`, and `V29`;
- reran 2020 FABLE extraction, graphing, and translation with verbose progress;
- translated 296,976 of 296,976 formulas with zero translation diagnostics;
- built a selected-output generated-model contract with 20 symbols, 10 input constants, and 10 outputs;
- generated a 207-line Python model under ignored `tmp/`;
- executed the generated model as a smoke test and observed ten outputs with no generation diagnostics.

Implementation note:

- tightened generated-contract inference so unsupported dependency edges outside the selected-output
  dependency closure do not block selected-output materialization;
- kept unsupported dependency edges inside the selected-output closure as explicit generation diagnostics.

### P21.3 Validate Selected 2020 FABLE Outputs

Goal: compare selected generated 2020 FABLE outputs against cached workbook values or an explicit oracle.

Acceptance criteria:

- define selected benchmark output scenarios;
- compare generated outputs against cached or oracle values;
- preserve missing cached values and oracle failures as validation blockers;
- write ignored local validation reports and verbose logs.

Status: complete.

Local evidence:

- `tmp/p21-fable-2020-validation/validation-scenario.json`;
- `tmp/p21-fable-2020-validation/evaluation-result.json`;
- `tmp/p21-fable-2020-validation/summary.json`;
- `tmp/logs/p21-fable-2020-validation.log`.

Result:

- wrote a validation scenario for the same ten selected 2020 FABLE outputs materialized in P21.2;
- ran `sheetforge validation evaluate` through the public CLI with `--workbook` and `--verbose`;
- re-extracted the 2020 source workbook to obtain cached workbook values;
- executed the generated model successfully with zero execution diagnostics;
- compared ten generated outputs against cached workbook values;
- cached-workbook validation status was `pass`;
- mismatches were empty;
- validation diagnostics were empty.

### P21.4 Rerun Benchmark Convergence Loop

Goal: rerun the benchmark after P21 fixes and classify every remaining blocker.

Acceptance criteria:

- rerun the 2020 FABLE benchmark after contract inference, generation, and validation work;
- classify each remaining blocker as resolved, deferred, out of scope, or next target;
- record what equivalence has and has not been proven;
- open the Phase 21 PR only after verification passes.

Status: complete.

Local evidence:

- `tmp/p21-convergence-closeout/summary.json`;
- `tmp/logs/p21-convergence-closeout.log`.

Result:

- summarized the post-P21 benchmark evidence from materialization and validation artifacts;
- confirmed selected-output extraction, graphing, translation, contract inference, generation, execution,
  and cached validation are complete for the selected 2020 FABLE scope;
- classified residual blockers from the Phase 20 closeout:
  - `unsupported_structured_reference`: resolved for the selected scope;
  - `unsupported_volatile_function`: resolved for the selected scope;
  - `missing_cached_formula_value`: deferred but avoided for the selected scope by choosing cached outputs;
  - `named_range_source_error`: out of scope because it is an unreferenced source workbook defect;
  - `unsupported_external_link`: deferred to explicit external dependency policy.

Proven:

- selected-output equivalence for the ten declared `SCENARIOS definition` outputs against cached workbook
  values.

Not proven:

- full-workbook generated-model materialization;
- full-workbook generated-output equivalence;
- oracle-backed recalculation equivalence;
- external workbook dependency behavior.

Next targets:

- expand selected-output coverage beyond the initial ten cached scenario-definition outputs;
- define policy and tooling for external workbook dependencies;
- add generated-model scope selection heuristics so users can choose meaningful output sets;
- add cached-value availability reporting for candidate output selection.

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
