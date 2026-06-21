# Phase 22 Release Readiness Closeout

Date: 2026-06-21

## Scope

This note records the local closeout evidence for Phase 22 PyPI publication and deployment workflow work.

GitHub parent issue: #124

Active branch: `feature/p22-pypi-publication-deployment`

## Completed Locally

- First alpha version set to `0.1.0a1`.
- Release tag policy set to `v0.1.0a1`.
- MIT license approved and tracked in `LICENSE`.
- Package metadata includes project URLs, classifiers, keywords, release dependency extra, and SPDX-style license metadata.
- Release artifact checker added at `scripts/check_release_artifacts.sh`.
- Sphinx Read the Docs theme verifier added at `scripts/verify_docs_theme.py`.
- CI release artifact validation added to `.github/workflows/test.yml`.
- Gated release workflow added at `.github/workflows/release.yml`.
- Docs Pages workflow now verifies the built RTD-themed artifact before upload.
- Release runbook added at `docs/guides/release-deployment.rst`.

## Local Verification

Verbose logs are ignored local evidence under `tmp/logs/`.

- `tmp/logs/p22-ruff.log`: `ruff check .` passed.
- `tmp/logs/p22-pytest.log`: `pytest -vv` passed with 129 tests.
- `tmp/logs/p22-docs.log`: Sphinx warning-as-error docs build passed and local RTD theme verification passed.
- `tmp/logs/p22-release-artifact-check.log`: sdist/wheel build passed, `twine check` passed, artifact inspection found no forbidden private/generated files, clean wheel install passed, package import returned `0.1.0a1`, and installed CLI help smoke test passed.

The final release-artifact rehearsal used:

```bash
RELEASE_CHECK_DIR=tmp/release-checks/ci PYTHON=.venv/bin/python scripts/check_release_artifacts.sh
```

## Publication State

Ready locally:

- package metadata;
- local artifact builds;
- artifact metadata checks;
- artifact privacy inspection;
- clean install smoke tests;
- local Sphinx RTD-themed artifact verification.

Not yet complete:

- TestPyPI publication rehearsal;
- real PyPI publication;
- deployed GitHub Pages RTD-theme verification.

## TestPyPI Blocker

TestPyPI rehearsal was attempted after Phase 22 merge using the ignored local token file at
`tmp/pypi-secrets`.

Result:

- the local release artifact check passed before upload;
- the token labelled `test-pypi:` was confirmed to be a TestPyPI token without printing its value;
- `twine upload` to `https://test.pypi.org/legacy/` failed with `403 Forbidden`;
- `https://test.pypi.org/pypi/sheetforge/json` returned `404`, so the `sheetforge` project does not currently exist on TestPyPI.

Interpretation:

The provided TestPyPI token cannot currently create or upload the `sheetforge` project. The likely
resolution is to use an account-scoped TestPyPI token for the first upload, or manually create/claim the
project on TestPyPI and then use a project-scoped token for `sheetforge`.

Required next steps:

- configure the `testpypi` GitHub environment and trusted publishing relationship;
- run the `Release` workflow manually with `publish_target = testpypi`;
- install `sheetforge==0.1.0a1` from TestPyPI in a clean environment and run import/CLI smoke tests.

## Real PyPI State

Real PyPI publication is deferred.

Required next steps before real PyPI:

- TestPyPI rehearsal passes;
- `pypi` GitHub environment and trusted publishing relationship are configured;
- maintainer approves publication;
- annotated tag `v0.1.0a1` is created;
- release workflow publishes from the protected environment;
- post-release package install, CLI, docs, and GitHub release checks pass.

## GitHub Pages State

Local docs artifact verification passed. Post-merge deployed Pages verification also passed.

The live site at `https://ubc-fresh.github.io/sheetforge/` contains the expected Sphinx Read the Docs markers:

- `_static/css/theme.css`;
- `wy-nav-side`;
- `sphinx_rtd_theme`.

The live site did not contain `minima` or `jekyll-theme` markers during the post-merge check.
