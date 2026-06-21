# Phase 23 Modelwright Rebrand Plan

Phase 23 renames the pre-release project from Sheetforge to Modelwright before any package publication.

## Scope

The rebrand is intentionally complete across the public development surface:

- GitHub repository: `UBC-FRESH/modelwright`.
- PyPI/TestPyPI package name: `modelwright`.
- Python import package: `modelwright`.
- CLI command: `modelwright`.
- Sphinx project title and user-facing documentation: Modelwright.
- Release artifact checks, installed smoke tests, and docs deployment references: Modelwright.

There are no external users and no published artifacts under the old name. The old import package and
old CLI command should not be retained as compatibility aliases.

## Compatibility Policy

Do not add:

- `sheetforge` console script aliases;
- `src/sheetforge` import shims;
- old JSON metadata fields in newly emitted records;
- documentation that tells users to install or run the old package name.

Historical notes may mention the old name only where needed to explain provenance, such as the blocked
pre-rebrand TestPyPI upload attempt.

## Verification

The phase is complete only after the repository passes:

```bash
scripts/bootstrap_dev_env.sh
.venv/bin/python -m ruff check .
.venv/bin/python -m pytest -vv
.venv/bin/sphinx-build -b html docs _build/html -W
.venv/bin/python scripts/verify_docs_theme.py _build/html
RELEASE_CHECK_DIR=tmp/release-checks/modelwright PYTHON=.venv/bin/python scripts/check_release_artifacts.sh
```

Longer commands should write logs under `tmp/logs/`, and the tail command should be shared before they
start so progress is visible.

## Local Closeout Evidence

Completed on 2026-06-21:

- GitHub repository renamed to `UBC-FRESH/modelwright`.
- Source package moved to `src/modelwright`.
- Package metadata renamed to `modelwright`.
- Console script renamed to `modelwright`; the old console script is not retained.
- Conversion-plan commit field and CLI option renamed to `modelwright_commit` and `--modelwright-commit`.
- Sphinx docs and package reference docs now use `modelwright` imports and commands.
- Bootstrap removes stale pre-rebrand `sheetforge` editable installs and `src/sheetforge.egg-info`.
- Release artifact checks remove stale build outputs, reject old `sheetforge` artifact paths, verify the old import package is absent, and verify the old console script is absent.

Ignored local verification logs:

- `tmp/logs/p23-bootstrap.log`
- `tmp/logs/p23-ruff.log`
- `tmp/logs/p23-pytest.log`
- `tmp/logs/p23-docs.log`
- `tmp/logs/p23-docs-theme.log`
- `tmp/logs/p23-release-artifact-check.log`

Verification results:

- `scripts/bootstrap_dev_env.sh`: passed.
- `.venv/bin/python -m ruff check .`: passed.
- `.venv/bin/python -m pytest -vv`: 129 passed.
- `.venv/bin/sphinx-build -b html docs _build/html -W -v`: passed.
- `.venv/bin/python scripts/verify_docs_theme.py _build/html`: passed.
- `RELEASE_CHECK_DIR=tmp/release-checks/modelwright-final PYTHON=.venv/bin/python scripts/check_release_artifacts.sh`: passed.
- PR #136 post-merge `Test` workflow: passed.
- PR #136 post-merge `docs-pages` workflow: passed and deployed.
- Live site `https://ubc-fresh.github.io/modelwright/`: contains `Modelwright`, `_static/css/theme.css`,
  `wy-nav-side`, and `sphinx_rtd_theme`; does not contain `minima` or `jekyll-theme`.
