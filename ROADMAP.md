# Roadmap

This roadmap is the current project plan and issue tracker map for `sheetforge`.

The repository is intentionally lightweight at this stage. Do not add a package layout, dependency manager, test framework, CLI, or CI contract until research and prototypes provide enough evidence for those choices.

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

Active branch: `feature/p2-workbook-extraction-contracts`

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

Status: ready for PR.

## Phase 3: Prototype Python Code Generation

GitHub parent issue: #14

Goal: generate readable Python from the controlled workbook IR without committing to durable package structure too early.

- [ ] P3.1 Define generated-code prototype contract. Child issue: #15.
- [ ] P3.2 Build ignored generated-code experiment. Child issue: #16.
- [ ] P3.3 Compare generated outputs against `formulas` results. Child issue: #17.
- [ ] P3.4 Summarize code-generation readiness. Child issue: #18.

Status: planned.

## Phase 4: Regression Validation Against Workbooks

GitHub parent issue: #19

Goal: define and prototype the validation loop that compares generated Python behavior against source workbook outputs.

- [ ] P4.1 Define validation scenario and oracle contract. Child issue: #20.
- [ ] P4.2 Build ignored validation prototype. Child issue: #21.
- [ ] P4.3 Define mismatch diagnostics and tolerance rules. Child issue: #22.
- [ ] P4.4 Summarize validation architecture and package inputs. Child issue: #23.

Status: planned.

## Phase 5: Package, API, CLI, And CI Decisions

GitHub parent issue: #24

Goal: introduce durable project tooling only after extraction, code generation, and validation prototypes clarify the required shape.

- [ ] P5.1 Choose package, dependency, and test stack. Child issue: #25.
- [ ] P5.2 Define public API and CLI boundaries. Child issue: #26.
- [ ] P5.3 Define fixture and regression-test strategy. Child issue: #27.
- [ ] P5.4 Define CI and documentation verification. Child issue: #28.
- [ ] P5.5 Summarize implementation bootstrap plan. Child issue: #29.

Status: planned.

## Current Next Steps

1. Open a PR from `feature/p2-workbook-extraction-contracts` back to `main` for Phase 2.
2. Merge the Phase 2 PR after review.
3. Close parent issue #9 only after the Phase 2 PR has merged.
4. Activate Phase 3 issue #14 and branch only after Phase 2 is closed, unless the maintainer explicitly approves parallel work.
