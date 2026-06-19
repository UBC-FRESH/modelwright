# CHANGE_LOG.md

This file records completed project work in chronological order.

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
