# Roadmap

This roadmap is the current project plan and issue tracker map for `sheetforge`.

The near-term implementation direction is recorded here. Broader phase rationale is recorded in `planning/long-term-roadmap.md`.

## Phase 0: Governance Bootstrap

GitHub parent issue: #1

- [x] P0.1 Create project overview and agent operating contract. Child issue: #2.
- [x] P0.2 Establish roadmap, changelog, planning area, and ignore rules. Child issue: #3.
- [x] P0.3 Commit bootstrap skeleton and verify clean ignored scratch space. Child issue: #4.
- [x] P0.4 Define strict issue, branch, and PR workflow. Child issue: #30.

Status: complete.

## Phase 1: Research Spreadsheet Tooling

GitHub parent issue: #5

- [x] P1.1 Compare candidate spreadsheet tooling. Child issue: #6.
- [x] P1.2 Run first synthetic workbook prototype. Child issue: #7.
- [x] P1.3 Record first prototype findings and architecture implications. Child issue: #8.

Status: complete.

## Phase 2: Workbook Extraction Contracts

GitHub parent issue: #9

Goal: define and test the minimum intermediate representation for workbook references, formulas, named ranges, dependencies, and diagnostics.

- [x] P2.1 Define workbook IR prototype contract. Child issue: #10.
- [x] P2.2 Emit IR JSON from the synthetic workbook. Child issue: #11.
  - [x] Create ignored prototype IR emitter under `tmp/`.
  - [x] Emit semantic named-range/reference edges.
  - [x] Emit execution cell-dependency edges.
  - [x] Emit diagnostics for missing cached formula values.
  - [x] Verify output against `planning/workbook-ir-contract.md` acceptance criteria.
- [x] P2.3 Record IR prototype findings and refine contract. Child issue: #12.
- [x] P2.4 Close extraction-contract phase with Phase 3 inputs. Child issue: #13.

Merged PR: #31

Status: complete.

## Phase 3: Prototype Python Code Generation

GitHub parent issue: #14

Goal: generate readable Python from the controlled workbook IR without committing to durable package structure too early.

- [x] P3.1 Define generated-code prototype contract. Child issue: #15.
- [x] P3.2 Build ignored generated-code experiment. Child issue: #16.
- [x] P3.3 Compare generated outputs against `formulas` results. Child issue: #17.
- [x] P3.4 Summarize code-generation readiness. Child issue: #18.

Merged PR: #32

Status: complete.

## Phase 4: Regression Validation Against Workbooks

GitHub parent issue: #19

Goal: define and prototype the validation loop that compares generated Python behavior against source workbook outputs.

- [x] P4.1 Define validation scenario and oracle contract. Child issue: #20.
- [x] P4.2 Build ignored validation prototype. Child issue: #21.
- [x] P4.3 Define mismatch diagnostics and tolerance rules. Child issue: #22.
- [x] P4.4 Summarize validation architecture and package inputs. Child issue: #23.

Merged PR: #33

Status: complete.

## Phase 5: Package, API, CLI, And CI Decisions

GitHub parent issue: #24

Active branch: `feature/p5-package-api-cli-ci-decisions`

Merged PR: #40

Goal: introduce durable project tooling only after extraction, code generation, and validation prototypes clarify the required shape.

- [x] P5.1 Choose package, dependency, and test stack. Child issue: #25.
- [x] P5.2 Define public API and CLI boundaries. Child issue: #26.
- [x] P5.3 Define fixture and regression-test strategy. Child issue: #27.
- [x] P5.4 Define CI and documentation verification. Child issue: #28.
- [x] P5.5 Summarize implementation bootstrap plan. Child issue: #29.

Status: complete.

## Phase 6: Initial Package And Validation Core

GitHub parent issue: #34

Active branch: `feature/p6-initial-package-validation-core`

Merged PR: #41

Goal: build the first durable code-bearing slice from the Phase 5 decisions: package skeleton, validation report core, synthetic fixtures, regression tests, and minimal default CI after tests exist.

- [x] P6.1 Add package and test skeleton. Child issue: #38.
- [x] P6.2 Add validation report core objects. Child issue: #37.
- [x] P6.3 Add synthetic fixture builder and expected outputs. Child issue: #35.
- [x] P6.4 Add baseline and mismatch regression tests. Child issue: #36.
- [x] P6.5 Add first default CI workflow. Child issue: #39.

Status: complete.

## Phase 7: Validation Scenario And Comparison Core

GitHub parent issue: #42

Merged PR: #79

Goal: turn the Phase 6 validation report records and synthetic fixture JSON into reusable scenario loading and scalar comparison helpers. This phase should not add workbook extraction, code generation, Excel-backed validation, CLI, or broad oracle execution.

- [x] P7.1 Add validation scenario objects and loader. Child issue: #46.
- [x] P7.2 Add scalar comparison helpers. Child issue: #45.
- [x] P7.3 Build validation reports from observed values. Child issue: #44.
- [x] P7.4 Summarize validation-core readiness. Child issue: #43.

Status: complete.

## Phase 8: Workbook Extraction Core

GitHub parent issue: #50

Merged PR: #80

Goal: move the proven `openpyxl` extraction concepts into package code for workbook, worksheet, cell, formula, named-range, and diagnostic records.

- [x] P8.1 Add extraction record objects. Child issue: #58.
- [x] P8.2 Implement `openpyxl` workbook extraction. Child issue: #57.
- [x] P8.3 Add extraction tests and closeout. Child issue: #56.

Status: complete.

## Phase 9: Dependency Graph Core

GitHub parent issue: #49

Merged PR: #81

Goal: build normalized reference and dependency graph behavior on top of extracted workbook records.

- [x] P9.1 Add canonical reference model. Child issue: #55.
- [x] P9.2 Resolve named ranges and dependency edges. Child issue: #62.
- [x] P9.3 Add graph diagnostics and readiness note. Child issue: #60.

Status: complete.

## Phase 10: Formula Translation Core

GitHub parent issue: #48

Merged PR: #82

Goal: translate the first supported Excel formula subset into internal operations ready for generated Python.

- [x] P10.1 Add formula expression model. Child issue: #61.
- [x] P10.2 Translate supported synthetic formula subset. Child issue: #59.
- [x] P10.3 Add unsupported formula diagnostics and closeout. Child issue: #66.

Status: complete.

## Phase 11: Generated Python Model Core

GitHub parent issue: #47

Merged PR: #83

Goal: generate small standalone Python modules from extracted and translated workbook logic.

- [x] P11.1 Define generated module contract. Child issue: #65.
- [x] P11.2 Generate Python from translated workbook logic. Child issue: #64.
- [x] P11.3 Test generated model outputs and closeout. Child issue: #63.

Status: complete.

## Phase 12: Oracle-Backed Validation

GitHub parent issue: #54

Merged PR: #84

Goal: introduce optional source-workbook oracle execution, starting with a pure-Python `formulas`-backed lane before any Excel-backed validation.

- [x] P12.1 Define oracle interface and optional dependency boundary. Child issue: #70.
- [x] P12.2 Add `formulas`-backed oracle for synthetic workbook. Child issue: #69.
- [x] P12.3 Compare generated model against oracle outputs. Child issue: #68.

Status: complete.

## Phase 13: Real Workbook Evaluation Lane

GitHub parent issue: #52

Merged PR: #85

Goal: use private workbooks under ignored `tmp/` to evaluate the pipeline and record sanitized findings without committing source workbooks or private outputs.

- [x] P13.1 Define private workbook evaluation protocol. Child issue: #67.
- [x] P13.2 Run first private workbook evaluation locally. Child issue: #74.
- [x] P13.3 Record sanitized findings and unsupported features. Child issue: #72.

Status: complete.

## Phase 14: CLI And API Stabilization

GitHub parent issue: #53

Merged PR: #86

Goal: stabilize the Python API and add thin CLI wrappers only after the internal flow is coherent.

- [x] P14.1 Review and stabilize Python API boundaries. Child issue: #73.
- [x] P14.2 Add thin CLI command groups. Child issue: #71.
- [x] P14.3 Document CLI and JSON workflows. Child issue: #78.

Status: complete.

## Phase 15: Hardening And Release Prep

GitHub parent issue: #51

Merged PR: #102

Goal: add hardening, documentation, release, and quality tooling only where evidence shows it will pay for itself.

- [x] P15.1 Decide hardening tooling from evidence. Child issue: #77.
- [x] P15.2 Add release and documentation metadata if needed. Child issue: #76.
- [x] P15.3 Summarize release readiness and next roadmap. Child issue: #75.

Status: complete.

## Phase 16: CLI And Documentation Public Surface

GitHub parent issue: #89

Completed branch: `feature/p16-cli-docs-public-surface`

Goal: align Sheetforge's CLI feel, command organization, help text, and documentation depth with the other FRESH lab packages `fhops` and `femic`, including full Sphinx documentation published to GitHub Pages from the `main` branch.

- [x] P16.1 Audit `fhops`/`femic` CLI and docs conventions. Child issue: #92.
- [x] P16.2 Refactor CLI toward FRESH Typer/Rich conventions. Child issue: #90.
- [x] P16.3 Add full Sphinx docs and GitHub Pages workflow. Child issue: #93.
- [x] P16.4 Verify CLI/docs surface and closeout. Child issue: #91.

Status: complete.

## Phase 17: Real Workbook Formula Semantics

GitHub parent issue: #88

Active branch: `feature/p17-real-workbook-formula-semantics`

Goal: expand formula and reference semantics based on real workbook evidence, especially structured references, unsupported functions, parser token forms, operators, external references, volatile functions, named ranges, and cached-value gaps.

- [x] P17.1 Prioritize real-workbook unsupported semantics. Child issue: #97.
- [x] P17.2 Add structured-reference extraction records. Child issue: #95.
- [x] P17.3 Expand formula translation subset. Child issue: #96.
  - [x] Pass 1: boolean literals, unary minus, `^`, `&`, and explicit `#REF!` diagnostics.
  - [x] Pass 2: scalar/range functions, supported table structured references, and unresolved structured-reference fast-fail behavior.
  - [x] Pass 3: criteria functions `SUMIF`, `SUMIFS`, `COUNTIF`, and `COUNTIFS`.
  - [x] Pass 4: lookup function `VLOOKUP` plus table-array structured references.
  - [x] Pass 5: constrained cross-table current-row structured references.
  - [x] Pass 6: constrained static `OFFSET` support.
- [x] P17.4 Validate expanded semantics and closeout. Child issue: #94.

Status: complete pending PR.

## Phase 18: Conversion Planning And Pipeline Orchestration

GitHub parent issue: #87

Merged PR: #110

Goal: turn extraction, graphing, translation, generation, and validation pieces into an explicit conversion plan workflow without pretending every workbook can be fully converted.

- [x] P18.1 Define conversion plan JSON contract. Child issue: #101.
- [x] P18.2 Build conversion plan API. Child issue: #99.
  - [x] Track official external FABLE benchmark metadata and add a helper that materializes the untracked workbook files into canonical ignored paths.
- [x] P18.3 Add conversion planning CLI. Child issue: #100.
- [x] P18.4 Test conversion planning workflow and closeout. Child issue: #98.

Status: complete.

## Phase 19: Residual Blocker Resolution For Full Benchmark Import

GitHub parent issue: #103

Active branch: `feature/p19-residual-blocker-resolution`

Open PR: #111

Goal: resolve or explicitly scope the residual blockers exposed by the 2020 FABLE conversion plan before treating validation automation as meaningful evidence.

- [x] P19.1 Resolve or scope unresolved named ranges. Child issue: #107.
- [x] P19.2 Define circular dependency semantics and policy. Child issue: #105.
- [x] P19.3 Resolve deferred workbook dependency and volatile/cache blockers. Child issue: #106.
- [x] P19.4 Rerun 2020 benchmark to convergence and closeout. Child issue: #104.

Status: complete pending PR.

## Phase 20: Automated Validation And Evaluation Reports

GitHub parent issue: TBD

Planned branch: `feature/p20-automated-validation-reports`

Goal: after residual blockers have concrete resolution or scope decisions, make generated-model execution, oracle execution where available, cached-value comparisons, and benchmark evaluation reports repeatable through APIs and CLI commands.

- [ ] P20.1 Add generated model execution API. Child issue: TBD.
- [ ] P20.2 Orchestrate oracle and cached-value validation. Child issue: TBD.
- [ ] P20.3 Add evaluation report CLI and JSON outputs. Child issue: TBD.
- [ ] P20.4 Run repeatable evaluation and closeout. Child issue: TBD.

Status: planned backlog.

## Current Next Steps

1. Open and review the Phase 19 PR from `feature/p19-residual-blocker-resolution` back to `main`.
2. Merge the Phase 19 PR after checks pass.
3. Close parent issue #103 after merge.
4. Activate Phase 20 only after Phase 19 is merged back to `main`.
