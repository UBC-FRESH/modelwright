# CI And Documentation Verification Decision

Date: 2026-06-19

## Purpose

This note defines the first CI and documentation verification boundary for Sheetforge.

The decision is intentionally conservative. It identifies what should become routine once package files exist, but it does not add GitHub Actions, pytest configuration, documentation tooling, or workflow files in this task.

## Default Verification Principles

Default checks should be deterministic, local-first, and runnable from a clean checkout.

Rules:

- Keep default verification free of private workbooks and ignored `tmp/` contents.
- Keep default verification free of Excel, GUI automation, network access, external services, and platform-specific assumptions.
- Prefer generated synthetic fixtures over tracked binary workbook files unless a tracked workbook is explicitly justified.
- Keep generated IR, generated Python models, validation reports, and temporary workbooks in test temporary directories.
- Document every project command that CI runs so maintainers can reproduce failures locally.
- Add optional checks only behind explicit dependency extras or manually triggered workflows.

## Routine Local Checks

Once the package skeleton exists, the first routine local verification command should be:

```bash
python -m pytest
```

Before tests exist, there is no project-specific command to run.

When `pyproject.toml` is introduced, it should define enough metadata for an editable install and pytest run:

```bash
python -m pip install -e ".[test]"
python -m pytest
```

The exact optional extra name can be finalized during implementation, but `test` is the preferred first name if the project needs pytest outside the default dependency set.

Do not add formatting, linting, coverage, type checking, property-based tests, or snapshot tools to the first CI boundary unless a concrete implementation need appears.

## First CI Boundary

The first GitHub Actions workflow should run only after the repository has:

- `pyproject.toml`;
- `src/sheetforge`;
- `tests`;
- at least one package-backed pytest test.

Recommended first workflow:

- trigger on pull requests and pushes to `main`;
- use Ubuntu only;
- use one current Python version first;
- install the package in editable mode with the test extra;
- run `python -m pytest`;
- avoid cache complexity until dependency install time becomes a problem.

Do not add a CI matrix until there is enough behavior to justify cross-version or cross-platform coverage.

## Documentation Verification

Documentation verification should remain lightweight at first.

Recommended first checks:

- ensure `README.md`, `AGENTS.md`, `ROADMAP.md`, and `CHANGE_LOG.md` exist;
- ensure roadmap task state and changelog entries are manually reviewed in PRs;
- ensure new planning notes are linked from `ROADMAP.md`, `CHANGE_LOG.md`, or another planning note when they govern active work.

Do not add a documentation site, Markdown linter, link checker, spell checker, or generated docs build yet.

If documentation drift becomes frequent, add a small repository script later to check required files and planning-note links. Do not introduce that script before there is evidence it saves work.

## Optional And Manual Checks

Some checks are valuable but should stay outside default CI.

Use optional or manual workflows for:

- Excel-backed validation with `xlwings`;
- tests requiring local Excel on Windows or macOS;
- large private workbook regression packs;
- network-dependent dependency research;
- benchmarks or scale tests;
- compatibility checks against multiple formula engines.

These checks should document required environment variables, local paths, workbook provenance, and expected artifacts before they are introduced.

## Failure Reporting Expectations

CI failures should be actionable.

For the first validation-oriented tests, assertion messages and report objects should include:

- scenario id;
- output cell reference;
- generated value;
- oracle value;
- diagnostic code;
- tolerance or comparison mode.

Avoid committing large generated reports only to explain failures. Generate reports in temporary output directories and print or assert the compact mismatch details needed to debug the failure.

## P5.5 Inputs

The implementation bootstrap plan should carry forward these decisions:

- no CI workflow until package skeleton and pytest tests exist;
- default CI should run `python -m pytest` only at first;
- default CI should not require Excel, network access, private workbooks, or ignored `tmp/`;
- docs verification should start as PR review discipline rather than tooling;
- optional Excel/private-workbook validation belongs behind explicitly scoped manual workflows later.
