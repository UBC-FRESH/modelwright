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
