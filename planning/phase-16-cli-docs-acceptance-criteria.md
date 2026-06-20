# Phase 16 CLI And Docs Acceptance Criteria

Date: 2026-06-20

## Purpose

This note turns the `fhops`/`femic` reference audit into concrete acceptance criteria for Sheetforge's Phase 16 public surface work.

## Reference Baseline

Sheetforge should use these local packages as style and implementation references:

- `/home/gep/projects/fhops`
- `/home/gep/projects/femic`

The relevant patterns are recorded in `planning/fresh-cli-docs-reference-audit.md`.

## CLI Acceptance Criteria

P16.2 should leave Sheetforge with a CLI that feels like a FRESH lab package:

- console script remains `sheetforge`;
- public entrypoint is a Typer app rather than bare `argparse`;
- command groups are workflow-oriented and discoverable;
- no-argument invocation shows help;
- shell completion is disabled unless there is a reason to support it;
- human-facing output can use Rich where useful;
- automation output remains JSON-first for extraction, graphing, generation, validation, and future planning/report commands;
- command options use FRESH-style naming such as `--out`, `--out-json`, and explicit path arguments;
- user errors use Typer-style parameter errors and exits instead of raw tracebacks;
- every command stays a thin wrapper over package APIs.

These JSON automation capabilities must not regress:

- workbook extraction;
- dependency graph building;
- generated Python module creation;
- validation report assembly.

## Documentation Acceptance Criteria

P16.3 should add full Sphinx documentation modeled on `fhops` and `femic`:

- `docs/conf.py`;
- `docs/index.rst`;
- `docs/requirements.txt`;
- curated guide pages, not only generated API pages;
- CLI reference page;
- API reference page using autodoc/autosummary;
- workflow boundaries page explaining extraction, graphing, formula translation, generation, validation, and private workbook handling;
- limitations page covering unsupported spreadsheet semantics and pre-release status;
- local build command documented as `.venv/bin/sphinx-build -b html docs _build/html -W`.

The docs should be warning-clean before Phase 16 closeout.

## GitHub Pages Acceptance Criteria

P16.3 should add a GitHub Pages workflow modeled on FEMIC:

- trigger on pull requests to `main`;
- trigger on pushes to `main`;
- build docs with warnings as errors;
- upload the built `_build/html` artifact;
- deploy to GitHub Pages only for non-PR `main` builds;
- keep regular package/test CI separate from docs publishing.

## Closeout Acceptance Criteria

P16.4 should verify:

- `sheetforge --help`;
- representative command help output for each command group;
- JSON command behavior for existing synthetic workflows;
- `scripts/bootstrap_dev_env.sh`;
- `.venv/bin/python -m ruff check .`;
- `.venv/bin/python -m pytest`;
- `.venv/bin/sphinx-build -b html docs _build/html -W`;
- GitHub Actions quality, test, and docs checks on the Phase 16 PR.
