# Phase 25 Real PyPI Publication

Phase 25 published `modelwright==0.1.0a1` to real PyPI after the Phase 24 TestPyPI rehearsal and
maintainer green light.

## Local Logs

Ignored local evidence:

- `tmp/logs/p25-pypi-target.log`
- `tmp/logs/p25-release-artifact-check.log`
- `tmp/logs/p25-pypi-install.log`

## Publication Evidence

Completed on 2026-06-21:

- Pre-publication PyPI JSON check returned `404` for `modelwright`.
- Local release artifact check passed with:

```bash
RELEASE_CHECK_DIR=tmp/release-checks/p25-pypi PYTHON=.venv/bin/python scripts/check_release_artifacts.sh
```

- Annotated tag `v0.1.0a1` was created on `main` commit `74eb21e`.
- Tag `v0.1.0a1` was pushed to GitHub.
- GitHub Actions `Release` workflow run `27894035356` passed.
- `publish-pypi` job passed through trusted publishing.
- Post-publication PyPI JSON check returned `200` and listed version `0.1.0a1`.
- Clean install from real PyPI passed from ignored virtual environment `tmp/pypi-install/modelwright-0.1.0a1`.
- Clean install verification imported `modelwright`, confirmed version `0.1.0a1`, ran `modelwright --help`,
  and confirmed old `sheetforge` import/CLI surfaces were absent.

## Release Boundary

This is an alpha release. It does not claim full-workbook conversion, full-workbook equivalence, stable
API compatibility, or Excel-backed recalculation equivalence.

Future fixes should use a new version such as `0.1.0a2`. Do not reuse `0.1.0a1`.
