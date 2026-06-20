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

Active branch: `feature/p14-cli-api-stabilization`

Goal: stabilize the Python API and add thin CLI wrappers only after the internal flow is coherent.

- [x] P14.1 Review and stabilize Python API boundaries. Child issue: #73.
- [ ] P14.2 Add thin CLI command groups. Child issue: #71.
- [ ] P14.3 Document CLI and JSON workflows. Child issue: #78.

Status: active.

## Phase 15: Hardening And Release Prep

GitHub parent issue: #51

Planned branch: `feature/p15-hardening-release-prep`

Goal: add hardening, documentation, release, and quality tooling only where evidence shows it will pay for itself.

- [ ] P15.1 Decide hardening tooling from evidence. Child issue: #77.
- [ ] P15.2 Add release and documentation metadata if needed. Child issue: #76.
- [ ] P15.3 Summarize release readiness and next roadmap. Child issue: #75.

Status: planned backlog.

## Current Next Steps

1. Work P14.2 in child issue #71 on branch `feature/p14-cli-api-stabilization`.
2. Add thin CLI command groups over the reviewed Python APIs.
3. Keep issue #71, parent issue #53, this roadmap, and `CHANGE_LOG.md` synchronized before documenting CLI workflows.
