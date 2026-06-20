# Hardening Tooling Decision

Date: 2026-06-20

## Purpose

Phase 15 starts by deciding which hardening tools are justified by current project evidence. The goal is to improve reliability without adding process weight before the package surface is stable.

## Current Evidence

- The package has a small but real implementation surface: 11 source modules under `src/sheetforge/`.
- The test suite has 74 tests covering extraction records, `openpyxl` extraction, references, graphing, formula translation, generated Python, validation reports, CLI wrappers, and optional `formulas` oracle behavior.
- Default CI runs editable install plus `python -m pytest` on Python 3.12.
- The repo has no formatter, linter, type checker, coverage threshold, or pre-commit hook yet.
- The codebase is still pre-release and the workbook conversion boundary is still changing.

## Decision Summary

Keep `python -m pytest` as the required gate.

Add one lightweight linting lane next, preferably `ruff check`, because it can catch unused imports, syntax issues, obvious mistakes, and style hazards with low configuration overhead.

Defer mandatory formatting, type checking, coverage thresholds, and pre-commit hooks.

## Tool Decisions

### Linting

Decision: add a small lint gate next.

Rationale:

- The package now has enough modules that import hygiene and simple static checks pay for themselves.
- `ruff` is fast and can be introduced with a narrow default configuration.
- A lint gate should run in CI only if it can be replicated locally with one documented command.

Initial scope:

```bash
python -m ruff check .
```

This should be added as a test extra or dedicated quality extra in the next task if the dependency boundary is acceptable.

### Formatting

Decision: defer mandatory formatting.

Rationale:

- The current code style is coherent enough.
- Adding an autoformatter now would create broad mechanical churn without addressing a current defect.
- If `ruff check` proves useful, `ruff format` can be reconsidered later as the least disruptive formatter option.

### Type Checking

Decision: defer static type checking.

Rationale:

- The current APIs are heavily JSON-boundary oriented and use third-party workbook libraries where type coverage may be incomplete.
- Strict typing would require decisions around public schemas, protocol boundaries, and optional dependencies that are still moving.
- A type checker should be introduced only after the conversion pipeline boundaries settle further.

### Coverage

Decision: defer coverage thresholds.

Rationale:

- The suite already exercises the main package paths, and missing coverage is better handled by targeted tests around discovered workbook behavior.
- A numeric coverage threshold could incentivize low-value tests before unsupported spreadsheet semantics are better understood.
- Coverage reporting may become useful later for release readiness, but should not block development yet.

### Pre-Commit

Decision: defer pre-commit hooks.

Rationale:

- The repo has few contributors and a strict roadmap/PR workflow.
- CI plus explicit local commands are enough for the current project size.
- Hooks become worthwhile when multiple local checks are mandatory and contributors need a consistent before-push path.

## Recommended Next Change

P15.2 should add release/documentation metadata only if it is genuinely needed, and may include a minimal quality extra plus CI lint command if the dependency boundary stays small.

Do not add a broad hardening stack in one commit.
