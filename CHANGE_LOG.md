# CHANGE_LOG.md

This file records completed project work in chronological order.

## 2026-06-20

- Added validation report core objects for comparison records, diagnostics, report status, mismatch extraction, and JSON-serializable boundaries.
- Added the tracked synthetic fixture builder, baseline scenario JSON, expected output JSON, and tests that generate the workbook in a pytest temporary directory.
- Added baseline and intentional numeric mismatch regression tests using the synthetic fixture assets and validation report core.
- Added the first default GitHub Actions workflow for editable install and `python -m pytest`.
- Opened Phase 6 PR #41 from `feature/p6-initial-package-validation-core` back to `main`.
- Merged Phase 6 PR #41, closed parent issue #34, and activated Phase 7 on `feature/p7-validation-scenario-comparison-core`.
- Expanded the roadmap and GitHub issue backlog through Phase 15, with the long-term sequence recorded in `planning/long-term-roadmap.md`.
- Added validation scenario objects and a JSON loader for fixture-backed validation scenario files.
- Added scalar comparison helpers for numeric tolerance, exact text, missing outputs, and unsupported output diagnostics.
- Added a validation report builder that compares scenario outputs from observed generated and oracle value mappings.
- Closed the Phase 7 validation-core planning loop by recording Phase 8 extraction inputs in `planning/phase-7-closeout-phase-8-inputs.md`.
- Opened Phase 7 PR #79 from `feature/p7-validation-scenario-comparison-core` back to `main`.
- Merged Phase 7 PR #79, closed parent issue #42, and activated Phase 8 on `feature/p8-workbook-extraction-core`.
- Added extraction record objects for workbooks, sheets, cells, formulas, named ranges, and extraction diagnostics.
- Added `openpyxl` workbook extraction for sheets, non-empty cells, formulas, named ranges, and initial extraction diagnostics.
- Closed the Phase 8 extraction-core planning loop by recording Phase 9 dependency graph inputs in `planning/phase-8-closeout-phase-9-inputs.md`.
- Opened Phase 8 PR #80 from `feature/p8-workbook-extraction-core` back to `main`.

## 2026-06-19

- Bootstrapped the repository with a lightweight project overview, agent working contract, roadmap, changelog, planning directory, and ignore rules.
- Established `tmp/` as ignored local working space for private notes, source workbooks, scratch experiments, and generated outputs.
- Documented that no Python package, CLI, dependency manager, test framework, or CI contract exists yet.
- Added the first Phase 1 research note comparing workbook extraction, formula evaluation, dependency graph, code-generation, and Excel-backed validation options.
- Ran the first ignored synthetic workbook prototype with `openpyxl`, `formulas`, and `networkx`, then recorded findings in `planning/first-prototype-findings.md`.
- Defined the first prototype workbook IR contract in `planning/workbook-ir-contract.md`.
- Reorganized `ROADMAP.md` into phase/task structure, mirrored phases and tasks into GitHub issues #1 through #30, closed completed Phase 0 and Phase 1 issues, and activated Phase 2 on `feature/p2-workbook-extraction-contracts`.
- Built an ignored IR emitter prototype for the synthetic workbook, verified the emitted JSON against the IR contract, and recorded findings in `planning/ir-prototype-findings.md`.
- Closed the Phase 2 extraction-contract planning loop by recording Phase 3 code-generation inputs in `planning/phase-2-closeout-phase-3-inputs.md`.
- Opened Phase 2 PR #31 from `feature/p2-workbook-extraction-contracts` back to `main`.
- Merged Phase 2 PR #31, closed parent issue #9, and activated Phase 3 on `feature/p3-code-generation-prototype`.
- Defined the Phase 3 generated-code prototype contract in `planning/generated-code-prototype-contract.md`.
- Built an ignored generated-code prototype from the IR, verified it computes `Summary!B2 = 70.2` and `Summary!B3 = "ok"`, and recorded findings in `planning/codegen-prototype-findings.md`.
- Compared the ignored generated model against `formulas`, confirmed both controlled outputs match, and recorded findings in `planning/codegen-comparison-findings.md`.
- Closed the Phase 3 generated-code planning loop by recording Phase 4 validation inputs in `planning/phase-3-closeout-phase-4-inputs.md`.
- Opened Phase 3 PR #32 from `feature/p3-code-generation-prototype` back to `main`.
- Merged Phase 3 PR #32, closed parent issue #14, and activated Phase 4 on `feature/p4-regression-validation`.
- Defined the Phase 4 validation scenario and oracle contract in `planning/validation-scenario-oracle-contract.md`.
- Built an ignored validation prototype, verified the baseline scenario passes with no mismatches, and recorded findings in `planning/validation-prototype-findings.md`.
- Defined validation mismatch diagnostics and tolerance rules in `planning/mismatch-diagnostics-tolerance-rules.md`.
- Closed the Phase 4 validation planning loop by recording Phase 5 package/API/CLI inputs in `planning/phase-4-closeout-phase-5-inputs.md`.
- Opened Phase 4 PR #33 from `feature/p4-regression-validation` back to `main`.
- Merged Phase 4 PR #33, closed parent issue #19, and activated Phase 5 on `feature/p5-package-api-cli-ci-decisions`.
- Chose the initial package, dependency, and test stack in `planning/package-dependency-test-stack-decision.md`.
- Defined initial Python API and deferred CLI boundaries in `planning/api-cli-boundary-decision.md`.
- Defined the initial fixture and regression-test strategy in `planning/fixture-regression-test-strategy.md`.
- Defined the first CI and documentation verification boundary in `planning/ci-docs-verification-decision.md`.
- Summarized the Phase 5 implementation bootstrap plan in `planning/implementation-bootstrap-plan.md` and created the planned Phase 6 issue sequence.
- Opened Phase 5 PR #40 from `feature/p5-package-api-cli-ci-decisions` back to `main`.
- Merged Phase 5 PR #40, closed parent issue #24, and activated Phase 6 on `feature/p6-initial-package-validation-core`.
- Added the initial package and test skeleton with `pyproject.toml`, `src/sheetforge`, `tests`, and documented local test commands.
