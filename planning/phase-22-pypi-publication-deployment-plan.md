# Phase 22 PyPI Publication And Deployment Plan

Date: 2026-06-21

## Purpose

Phase 22 prepares Sheetforge for professional package publication and deployment. The phase is about release infrastructure, release evidence, and maintainer-controlled gates. It should not publish to real PyPI until the package metadata, artifacts, documentation deployment, and TestPyPI rehearsal have been verified.

GitHub parent issue: #124

Active branch: `feature/p22-pypi-publication-deployment`

## Task Map

- P22.1: Decide alpha release target, license, and publication policy. Child issue: #127.
- P22.2: Harden package metadata and artifact build checks. Child issue: #125.
- P22.3: Add release automation for GitHub, TestPyPI, and PyPI gates. Child issue: #129.
- P22.4: Document deployment runbook and developer release onboarding. Child issue: #128.
- P22.5: Rehearse release artifacts and close publication readiness. Child issue: #126.

## Release Policy Questions

P22.1 must resolve these before real PyPI publication:

- Whether the first external alpha should be `0.1.0a1`, `1.0.0a1`, or another canonical PEP 440 version.
- Which license the maintainer approves for tracked source, docs, examples, and future package artifacts.
- Whether alpha publication means TestPyPI only, real PyPI, GitHub release only, or a staged sequence.
- Which benchmark evidence is required before the release is described as a working alpha rather than a packaging rehearsal.

## Package Artifact Gates

P22.2 should add repeatable checks for:

- source distribution and wheel builds;
- metadata validation with `twine check`;
- clean editable and non-editable install smoke tests;
- package import and CLI smoke tests from an installed artifact;
- artifact inspection to ensure ignored local material stays out of distributions.

Artifacts must not include `tmp/`, benchmark workbook binaries, generated models, raw evaluation reports, local logs, credentials, or private notes.

## Deployment Automation Gates

P22.3 should keep publication controlled:

- CI may build and validate artifacts on pull requests.
- TestPyPI publication should require an explicit maintainer trigger or protected environment approval.
- Real PyPI publication should require a tag, protected environment, or manual approval.
- Trusted publishing is preferred over storing API tokens when feasible.
- Real PyPI publication must not run from ordinary branch pushes.

GitHub Pages deployment also belongs in this gate. The current source configuration uses `sphinx_rtd_theme`; the deployed site must be checked so GitHub Pages serves the built Sphinx artifact rather than a fallback Jekyll/minima page.

## Documentation Gates

P22.4 should document:

- repo-root `.venv` development setup;
- build, test, quality, and docs commands;
- package artifact build commands;
- TestPyPI rehearsal;
- real PyPI publication gates;
- GitHub release and tag process;
- post-release verification;
- yanking or rollback guidance if a broken alpha is published.

## Closeout Evidence

P22.5 should record:

- full local verification logs;
- artifact build logs;
- metadata check results;
- clean install smoke-test results;
- TestPyPI rehearsal result or blocker;
- GitHub Pages RTD-theme verification result;
- final recommendation on whether real PyPI alpha publication should proceed.
