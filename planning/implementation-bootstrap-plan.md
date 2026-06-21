# Implementation Bootstrap Plan

Date: 2026-06-19

## Purpose

This note summarizes the Phase 5 decisions and defines the first real implementation phase for Modelwright.

The next phase should be the first code-bearing phase. It should introduce only enough package, fixture, validation, test, and CI structure to make the proven validation/report path durable.

## Phase 5 Decisions Carried Forward

Package and test stack:

- use a `src/modelwright` package layout;
- use `pyproject.toml` with `setuptools`;
- use `pytest`;
- use tracked fixtures under `tests/fixtures`;
- keep generated workbooks, generated models, IR JSON, and validation reports in temporary directories;
- keep default runtime dependencies conservative, starting with `openpyxl` when extraction code is added.

API boundary:

- keep extraction, IR, generation, validation, diagnostics, and reporting responsibilities separate;
- start with small typed objects and JSON-serializable boundary representations;
- do not add a CLI in the first durable code slice;
- keep `formulas` and `xlwings` behind optional validation/oracle boundaries.

Fixture and regression strategy:

- start with a synthetic fixture builder rather than tracked private workbooks;
- cover the controlled formula subset already used in prototypes;
- add expected baseline outputs for `Summary!B2 = 70.2` and `Summary!B3 = "ok"`;
- add at least one intentional mismatch test before treating validation reports as durable.

CI and documentation verification:

- do not add CI until package-backed pytest tests exist;
- first default CI should run only editable install plus `python -m pytest`;
- default CI should not require Excel, network-dependent checks, private workbooks, or ignored `tmp/`;
- keep documentation verification manual until there is evidence tooling would save work.

## Next Phase

Next roadmap phase:

```text
Phase 6: Initial Package And Validation Core
GitHub parent issue: #34
Planned branch: feature/p6-initial-package-validation-core
```

Goal: build the first durable code-bearing slice from the Phase 5 decisions.

Planned child tasks:

- P6.1 Add package and test skeleton. Child issue: #38.
- P6.2 Add validation report core objects. Child issue: #37.
- P6.3 Add synthetic fixture builder and expected outputs. Child issue: #35.
- P6.4 Add baseline and mismatch regression tests. Child issue: #36.
- P6.5 Add first default CI workflow. Child issue: #39.

Do not activate Phase 6 until the Phase 5 PR has merged and parent issue #24 is closed.

## Branch And PR Sequence

Recommended sequence:

1. Finish and merge the Phase 5 PR from `feature/p5-package-api-cli-ci-decisions` to `main`.
2. Close Phase 5 parent issue #24 after the PR merges.
3. Switch to updated `main`.
4. Activate Phase 6 parent issue #34.
5. Create `feature/p6-initial-package-validation-core` from `main`.
6. Work P6 child issues one at a time in roadmap order.
7. Open a Phase 6 PR back to `main` after child issues are complete or explicitly deferred.

## First Implementation Slice

The first code-bearing slice should avoid broad spreadsheet conversion.

Start with:

- package metadata;
- importable package skeleton;
- validation comparison/report dataclasses or equivalent lightweight structures;
- JSON-friendly report serialization;
- synthetic fixture builder;
- baseline and intentional mismatch tests.

Defer:

- CLI;
- complete workbook extraction;
- generated-code pipeline integration;
- Excel-backed validation;
- broad formula support;
- multi-platform CI;
- linting, formatting, coverage, typing, docs site, and release automation.

## Acceptance Criteria For Phase 6

Phase 6 should be considered complete when:

- the repository has a minimal package skeleton;
- `python -m pytest` runs package-backed tests locally;
- the synthetic validation/report baseline is covered;
- at least one intentional mismatch is covered with stable diagnostics;
- generated artifacts are not tracked;
- default CI runs the same basic pytest command without Excel or private data;
- roadmap, changelog, issues, and PR state are synchronized.
