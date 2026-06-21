# Phase 22 Alpha Release Policy

Date: 2026-06-21

## Purpose

This note records the P22.1 release policy decision for Sheetforge's first package publication workflow.

GitHub task issue: #127

## Version Target

Decision: use `0.1.0a1` for the first external alpha.

Rationale:

- Sheetforge has a real package, CLI, docs, CI, and benchmark validation evidence.
- The current proven benchmark claim is selected-output equivalence for a declared 2020 FABLE output slice.
- Full-workbook generated-model materialization, full-workbook equivalence, oracle-backed recalculation equivalence, and external dependency behavior are not yet proven.
- `1.0.0a1` would signal a stronger public-API and product-completeness posture than the evidence supports.
- The sibling FRESH package `femic` already uses an alpha version line in the `0.1.xa1` range.

The canonical version string should use Python packaging syntax: `0.1.0a1`.

## License

Decision: use MIT for consistency with the sibling FRESH package `fhops`.

Status: approved by the maintainer on 2026-06-21.

Rationale:

- `fhops` uses MIT and includes a tracked `LICENSE` file.
- `femic` does not expose a shallow license file in the local checkout inspected during this task.
- License choice is a maintainer/legal decision and should not be silently inferred from project style.

P22.2 may replace `license = { text = "TBD" }` with MIT package metadata and a tracked `LICENSE` file.

## Publication Sequence

The release process should be staged:

1. Build local source distribution and wheel artifacts from a clean tree.
2. Run metadata checks, including README rendering where feasible.
3. Inspect artifacts to verify that ignored local files are absent.
4. Run editable and non-editable install smoke tests from a clean virtual environment.
5. Publish to TestPyPI using a maintainer-controlled workflow.
6. Install from TestPyPI and run import, CLI, and selected smoke tests.
7. Publish to real PyPI only after maintainer approval through a protected gate.

Real PyPI publication must not run from ordinary branch pushes.

## GitHub Releases And Tags

Recommended policy:

- Use annotated release tags such as `v0.1.0a1`.
- Generate GitHub release notes from the changelog and the Phase 22 closeout summary.
- Attach or link package artifact verification evidence, but rely on PyPI/TestPyPI for package distribution.
- Keep benchmark workbook binaries, generated models, local logs, private reports, and credentials out of release artifacts.

## Benchmark Claim Boundary

The first alpha may claim:

- extraction, graphing, and formula translation are clean for the current 2020 FABLE benchmark scope;
- selected-output generated-model equivalence is proven for ten cached `SCENARIOS definition` outputs;
- the CLI and Python APIs support explicit staged conversion planning, generation, and validation workflows.

The first alpha must not claim:

- full-workbook conversion;
- full-workbook generated-output equivalence;
- Excel-backed oracle recalculation equivalence;
- general support for arbitrary private workbooks;
- stable public API compatibility.

## P22.1 Closeout

P22.1 is complete. P22.2 owns package metadata changes, local artifact checks, and clean install smoke tests.
