# Release And Documentation Metadata Decision

Date: 2026-06-20

## Purpose

P15.2 decides which release, documentation, and quality metadata should exist before the project has a stable conversion workflow.

## Added Now

- Added a `quality` optional dependency extra for `ruff`.
- Added minimal Ruff configuration in `pyproject.toml`.
- Added a CI `quality` job that runs `python -m ruff check .`.
- Documented local quality commands in `README.md`.
- Documented that the project remains pre-release and has no compatibility guarantee yet.

## Deferred

- No package publishing workflow.
- No release artifact build workflow.
- No changelog automation.
- No versioning policy beyond the existing `0.0.0` skeleton version.
- No license choice beyond the existing `TBD` metadata.
- No documentation site, API docs build, Markdown linter, link checker, or spell checker.
- No formatter, type checker, coverage threshold, or pre-commit hook.

## Rationale

The repo now has enough Python surface area for a lint command to pay for itself, but the product boundary is still pre-release. Publishing metadata and release automation would imply maturity that the workbook conversion workflow has not earned yet.

The right next release-readiness step is to summarize what is usable, what remains unsupported, and which decisions block a real user-facing release.
