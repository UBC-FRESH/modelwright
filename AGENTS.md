# AGENTS.md

This file is the working contract for AI coding agents in this repository.

## Project Purpose

`sheetforge` exists to research and build a generic workflow for converting spreadsheet workbooks into transparent, version-controlled, standalone Python models.

The goal is not to preserve spreadsheets as the execution environment. The goal is to recover workbook logic, formulas, dependencies, inputs, outputs, and validation examples so that analyst-built spreadsheet models can be migrated into reproducible Python code.

## Current Repo State

This repository is currently a bootstrap skeleton. It contains:

- `README.md`: concise project overview.
- `ROADMAP.md`: lightweight project plan and current next-step tracker.
- `CHANGE_LOG.md`: append-only project narrative.
- `planning/`: focused planning notes and research records.
- `tmp/`: ignored local working area that may contain private notes, source workbooks, scratch experiments, and generated outputs.

There is no established application stack, package manager, test suite, workbook extraction framework, code generator, CLI, or CI contract yet. Do not invent one without clear need or user direction.

Private bootstrap notes may exist under `tmp/`. Treat those files as local context only. Do not copy raw transcripts, private references, unpublished details, or unrelated context into tracked files unless the user explicitly asks for a cleaned public version.

## Source Workbooks And Generated Outputs

Source spreadsheets, local workbook extracts, generated Python clones, validation reports, and large intermediate artifacts should be treated as local working material unless the user explicitly asks to track a specific compact artifact.

Rules:

- Keep `tmp/` ignored.
- Do not commit source workbooks, generated clones, large validation outputs, or private transcripts unless explicitly requested.
- Prefer small, reproducible scripts and documentation over checked-in derived artifacts once the project has a tooling structure.
- Record workbook provenance whenever a source workbook, worksheet, named range, formula, or validation example is interpreted.
- Keep workbook-specific assumptions explicit rather than silently baking them into generic conversion logic.

## Product Vision

The final package and service model is not settled yet. Current direction:

- Analyze spreadsheet structure, formulas, named ranges, worksheets, dependencies, inputs, and outputs.
- Build a dependency graph that can support evaluation, refactoring, validation, and code generation.
- Generate maintainable Python source that can be checked into Git and reviewed like normal software.
- Validate generated Python behavior against source workbook outputs using regression examples.
- Evaluate whether Excel-backed tools such as `xlwings` should be used during extraction or validation while keeping the final generated model independent of Excel.

Do not over-specify implementation details before research and prototypes provide enough evidence.

## Working Principles

- Read `AGENTS.md`, `ROADMAP.md`, and `CHANGE_LOG.md` before making project-shaping changes.
- Preserve the distinction between source workbooks, derived working outputs, generated code, and tracked project metadata.
- Favor reproducible extraction, graphing, code-generation, and validation workflows over one-off manual conversions.
- Use structured parsers, spreadsheet libraries, and graph tooling where available instead of ad hoc text processing.
- Document uncertainty around Excel semantics, unsupported functions, circular references, named ranges, volatile formulas, external links, hidden sheets, macros, array formulas, and workbook-specific assumptions.
- Keep naming conventions explicit once they emerge; do not silently normalize workbook, sheet, range, or generated-symbol names without documenting the mapping.
- Keep changes scoped. This repo is early-stage, so avoid broad framework choices unless they are needed for the immediate task.
- Keep public repo content clean of private, irrelevant, or unpublished references. Prefer sanitized summaries over raw pasted notes.

## Planning Workflow

This repo uses an agent-assisted roadmap and GitHub issue workflow.

Active rules now:

- Keep the current plan in `ROADMAP.md`.
- Keep the immediate edge of work in the `Current Next Steps` section of `ROADMAP.md`.
- Record completed deliverables in `CHANGE_LOG.md` with dated bullets.
- Use `planning/` for focused notes, investigations, and contracts that are too detailed for the roadmap.
- Before non-trivial work, update or confirm the roadmap entry that governs it.
- Use GitHub issues with `gh` in tandem with the roadmap:
  - roadmap phases map to GitHub parent issues;
  - roadmap tasks map to child issues linked from the parent issue body;
  - substantial subtasks may map to third-level implementation issues linked from the task issue body;
  - lightweight subtasks stay as checklists inside the task issue body;
  - do not use more than three issue levels: phase, task, and implementation subtask;
  - record issue numbers beside roadmap phases and tasks once created.

## Strict Development Workflow

Use this workflow for active development from the first phase boundary onward:

- One active roadmap phase should generally correspond to one GitHub parent issue and one feature branch.
- Create or activate the GitHub parent issue before starting a roadmap phase.
- Create the feature branch from current `main` for that parent issue.
- Create child issues for roadmap tasks under the parent issue.
- Document task subtasks as checklist steps inside the child issue body unless they are large enough to deserve third-level implementation issues.
- Work child issues one at a time where practical, usually in roadmap order.
- Before closing a child issue, update every issue-body checklist item to checked, or rewrite the issue body to make explicitly clear which items were superseded or are not applicable.
- Close each child issue only after its repo changes, documentation, issue-body checklist, and verification for that task are complete.
- Keep `ROADMAP.md`, `CHANGE_LOG.md`, and issue comments synchronized as task state changes.
- Open a PR from the phase branch back to `main` when the parent issue's child issues are complete or explicitly deferred.
- Close the parent issue only after the PR has merged back to `main`.
- Do not start a new active parent issue and branch until the current parent issue is closed, unless the maintainer explicitly approves a parallel lane.

Existing bootstrap-created parent issues for future phases are planning placeholders. Treat them as inactive backlog lanes until their phase is explicitly activated.

Planned later, once the repo has enough structure to justify them:

- GitHub issue hygiene rules, labels, milestones, and release tracking.
- CI, linting, formatting, tests, and pre-commit rules.
- Documentation build checks.
- Package, Python API, or command-line tooling contracts.
- Workbook extraction, dependency graph, generated-code, and validation schemas.
- Commit granularity rules tied to roadmap tasks.

## Expected Deliverables Over Time

The expected project phases are:

1. Bootstrap: establish the repo contract, roadmap, changelog, and planning structure.
2. Research: evaluate workbook parsing, formula parsing, calculation, dependency graph, and Excel-backed validation options.
3. Extraction contracts: define the minimum workbook model needed to represent sheets, cells, formulas, named ranges, dependencies, inputs, and outputs.
4. Code generation: prototype generated Python modules from extracted workbook logic.
5. Validation: compare generated model outputs against source workbook outputs across representative input scenarios.
6. Packaging: decide on package layout, API, CLI, dependency manager, test framework, and CI after prototypes establish the right shape.

Use these phases as orientation, not as permission to add large systems prematurely.

## Tooling And Verification

At the time this contract was written, there are no project-specific commands to run.

When adding tooling:

- Document required commands in `README.md` or a dedicated planning note.
- Add the smallest useful verification path for the change.
- Prefer commands that can be rerun from a clean checkout with source workbooks restored under `tmp/`.
- Do not require absolute machine-specific paths outside this repository unless unavoidable; if unavoidable, document them clearly.

## Git Hygiene

- Treat existing uncommitted changes as user work unless you made them.
- Do not revert user changes without explicit instruction.
- Avoid committing generated, bulky, private, or environment-specific files.
- Keep `.gitignore` aligned with data handling rules, especially for `tmp/`, source workbooks, and generated-output directories.

## Documentation Standards

Documentation should be practical and provenance-oriented:

- Say what was inspected, where it came from, and how it was interpreted.
- Include exact local paths for workbook sources or scratch outputs only when useful and safe.
- Include commands used for repeatable inspection steps.
- Capture assumptions, known gaps, and follow-up questions.
- Avoid presenting generated code or recovered workbook meaning as authoritative until it has been validated against source workbook behavior.
