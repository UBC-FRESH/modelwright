# Contributing To Sheetforge

Sheetforge is pre-release research software for converting spreadsheet workbook logic into transparent Python model artifacts.

The project values reproducible workflow steps, explicit unsupported-semantics diagnostics, and clean separation between tracked source code and private/generated workbook artifacts.

## Development Environment

Use a repo-local virtual environment. Do not rely on a shared user-level environment.

Bootstrap the environment:

```bash
scripts/bootstrap_dev_env.sh
```

This creates `.venv/` and installs the editable package with the `dev` extra:

```bash
.venv/bin/python -m pip install -e '.[dev]'
```

To also restore the public external FABLE benchmark workbooks into canonical ignored paths, run:

```bash
scripts/bootstrap_dev_env.sh --benchmarks
```

Activate it when working interactively:

```bash
source .venv/bin/activate
```

Run checks from the repo root:

```bash
.venv/bin/python -m ruff check .
.venv/bin/python -m pytest
.venv/bin/sphinx-build -b html docs _build/html -W
```

## Workflow

- Read `AGENTS.md`, `ROADMAP.md`, and `CHANGE_LOG.md` before project-shaping changes.
- Keep the active roadmap phase, GitHub issues, branch, changelog, and planning notes synchronized.
- Prefer small package-backed changes with focused tests.
- Keep CLI commands thin wrappers over Python APIs.
- Keep generated outputs and private workbook material out of tracked files.

## Private Workbook And Generated Output Hygiene

Keep private and generated artifacts under ignored `tmp/` subdirectories, such as:

```text
tmp/private-workbooks/
tmp/private-evaluations/
tmp/generated-models/
tmp/logs/
```

Do not commit:

- source workbooks;
- raw workbook extracts;
- generated Python clones of private workbooks;
- full private validation reports;
- raw formulas, values, sheet names, workbook names, or private paths.

Tracked private-evaluation notes must be sanitized and should focus on counts, unsupported feature categories, validation status, stop conditions, and follow-up priorities.

## Documentation

Sphinx docs live under `docs/`.

Build docs locally with warnings as errors:

```bash
.venv/bin/sphinx-build -b html docs _build/html -W
```

The GitHub Pages workflow builds docs on pull requests and deploys on pushes to `main`.

## Release And Deployment

Release work uses the repo-local `.venv` and the same artifact checks used in CI.

Build and inspect release artifacts locally:

```bash
scripts/check_release_artifacts.sh
```

Verify the Sphinx Read the Docs themed docs artifact:

```bash
.venv/bin/sphinx-build -b html docs _build/html -W -v
.venv/bin/python scripts/verify_docs_theme.py _build/html
```

Publication is maintainer-gated:

- build artifacts locally and in CI first;
- rehearse publication through TestPyPI;
- publish to real PyPI only from the release workflow, with a tag such as `v0.1.0a1` and protected environment approval;
- never commit credentials, benchmark workbook binaries, generated models, private reports, or local logs.

See `docs/guides/release-deployment.rst` for the full runbook.

## Pull Requests

Before opening a PR:

- run the local checks;
- update `ROADMAP.md` and `CHANGE_LOG.md`;
- update relevant planning notes;
- close or update the corresponding child issue checklist;
- keep the PR scoped to the active phase branch.

Do not add broad conversion claims or compatibility guarantees until the roadmap phase explicitly calls for them.
