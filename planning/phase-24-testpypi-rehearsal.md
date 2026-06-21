# Phase 24 TestPyPI Rehearsal

Phase 24 rehearses publication of `modelwright==0.1.0a1` to TestPyPI before any real PyPI release.

## Scope

This phase should prove or precisely block:

- TestPyPI target state for the `modelwright` package name;
- local release artifacts for the current package;
- upload authentication without exposing token material;
- clean installation from TestPyPI;
- import and CLI smoke tests from the published artifact;
- absence of old pre-rebrand `sheetforge` import or CLI surface in a clean install.

## Private Data Rules

- Token values stay in ignored local files only.
- Logs may show package names, HTTP status codes, and command status.
- Logs must not include PyPI or TestPyPI token values.
- Tracked notes should describe token type only at a sanitized level.

## Local Logs

Use these ignored logs:

- `tmp/logs/p24-testpypi-target.log`
- `tmp/logs/p24-release-artifact-check.log`
- `tmp/logs/p24-testpypi-upload.log`
- `tmp/logs/p24-testpypi-install.log`

Before long commands, print the matching `tail -f` command so progress is visible.

## Local Closeout Evidence

Completed on 2026-06-21:

- Initial TestPyPI JSON check returned `404` for `modelwright`.
- Local token metadata was checked without printing token values.
- Local release artifact check passed using `RELEASE_CHECK_DIR=tmp/release-checks/p24-testpypi`.
- Direct local token upload failed with `403 Forbidden`.
- GitHub Actions `Release` workflow with `publish_target=testpypi` succeeded through trusted publishing.
- Follow-up TestPyPI JSON check returned `200` and listed version `0.1.0a1`.
- Clean install from TestPyPI passed from ignored virtual environment `tmp/testpypi-install/modelwright-0.1.0a1`.
- Clean install verification imported `modelwright`, confirmed version `0.1.0a1`, ran `modelwright --help`, and confirmed old `sheetforge` import/CLI surfaces were absent.

Ignored local evidence:

- `tmp/logs/p24-testpypi-target.log`
- `tmp/logs/p24-release-artifact-check.log`
- `tmp/logs/p24-testpypi-upload.log`
- `tmp/logs/p24-testpypi-install.log`

GitHub Actions evidence:

- `Release` workflow run `27891940796`: passed for `publish_target=testpypi`.

## Real PyPI Readiness

Phase 24 proves the package can publish and install through TestPyPI using trusted publishing.

Real PyPI remains gated on:

- configuring the real PyPI trusted publisher for owner `UBC-FRESH`, repository `modelwright`,
  workflow `release.yml`, and environment `pypi`;
- maintainer approval to create and push annotated tag `v0.1.0a1`;
- post-publication verification from real PyPI.
