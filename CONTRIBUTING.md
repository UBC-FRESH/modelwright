# Contributing To Sheetforge

Sheetforge is pre-release research software for converting spreadsheet workbook logic into transparent Python model artifacts.

The project values reproducible workflow steps, explicit unsupported-semantics diagnostics, and clean separation between tracked source code and private/generated workbook artifacts.

## Development Environment

Use a repo-local virtual environment. Do not rely on a shared user-level environment.

Bootstrap the environment:

```bash
scripts/bootstrap_dev_env.sh
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

## Pull Requests

Before opening a PR:

- run the local checks;
- update `ROADMAP.md` and `CHANGE_LOG.md`;
- update relevant planning notes;
- close or update the corresponding child issue checklist;
- keep the PR scoped to the active phase branch.

Do not add broad conversion claims, compatibility guarantees, release automation, or publishing metadata until the roadmap phase explicitly calls for them.
