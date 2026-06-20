# Long-Term Roadmap

Date: 2026-06-20

## Purpose

This note records the current planning horizon beyond the active Phase 7 work.

The sequence is intentionally staged. Sheetforge should move from scenario/report mechanics to extraction, dependency analysis, formula translation, generated Python, oracle-backed validation, private workbook evaluation, API/CLI stabilization, and then hardening. The project should not jump directly to a broad conversion pipeline before the intermediate contracts are proven.

## Direction Of Travel

The major path is:

```text
scenario/report core
  -> workbook extraction
  -> dependency graph
  -> formula translation
  -> generated Python
  -> oracle-backed validation
  -> private workbook evaluation
  -> API/CLI stabilization
  -> hardening and release prep
```

Each phase should produce package-backed behavior, tests, and documentation before the next phase relies on it.

## Phase 7: Validation Scenario And Comparison Core

Goal: turn the Phase 6 validation report records and synthetic fixture JSON into reusable scenario loading and scalar comparison helpers.

Boundaries:

- load validation scenario JSON;
- preserve source workbook path, generated model path, oracle backend, outputs, inputs, and comparison defaults;
- compare observed generated/oracle scalar values;
- produce `ValidationReport` objects;
- do not execute workbooks, generated models, formulas, Excel, or CLI commands.

## Phase 8: Workbook Extraction Core

Goal: move the proven `openpyxl` extraction concepts into package code.

Expected outputs:

- workbook, sheet, cell, formula, named-range, and extraction diagnostic records;
- `openpyxl`-backed extraction of the synthetic workbook fixture;
- diagnostics for missing cached formula values and unsupported workbook features;
- tests that verify extracted facts without committing generated workbook artifacts.

## Phase 9: Dependency Graph Core

Goal: build normalized reference and dependency graph behavior on top of extracted workbook records.

Expected outputs:

- canonical workbook, sheet, cell, range, and named-reference handling;
- named-range resolution;
- semantic and execution dependency edges;
- diagnostics for unresolved references, ambiguous named ranges, circular references, and external links.

Do not add `networkx` unless simple local structures become insufficient.

## Phase 10: Formula Translation Core

Goal: translate the first supported Excel formula subset into internal operations ready for generated Python.

Initial supported subset:

- scalar references;
- workbook-level named ranges already resolved by the dependency layer;
- arithmetic;
- `ROUND`;
- `IF`;
- comparison with `>`.

Unsupported functions and formula forms should produce diagnostics, not silent behavior.

## Phase 11: Generated Python Model Core

Goal: generate small standalone Python modules from extracted and translated workbook logic.

Expected outputs:

- generation result object;
- generated module contract;
- generated provenance comments;
- `calculate()` output contract;
- tests that execute generated modules from temporary directories and verify synthetic baseline outputs.

Generated Python remains an output artifact, not a tracked source artifact, unless explicitly approved.

## Phase 12: Oracle-Backed Validation

Goal: introduce optional source-workbook oracle execution.

Expected outputs:

- oracle interface;
- optional dependency boundary for pure-Python validation;
- `formulas`-backed oracle for the synthetic workbook;
- generated model versus oracle comparison using validation reports.

Excel-backed validation remains separate and optional. It should not enter default CI.

## Phase 13: Real Workbook Evaluation Lane

Goal: evaluate the pipeline against private workbooks under ignored `tmp/`.

Expected outputs:

- private workbook evaluation protocol;
- local-only extraction/generation/validation runs;
- sanitized findings;
- unsupported Excel semantics list;
- decision on whether any sanitized fixture should be created later.

Private workbooks, raw formulas, business meaning, raw values, generated clones, and full validation outputs should not be tracked.

## Phase 14: CLI And API Stabilization

Goal: stabilize the Python API and add thin CLI wrappers only after the internal flow is coherent.

Expected outputs:

- reviewed public/provisional API boundaries;
- thin command groups such as `inspect`, `emit-ir`, `generate`, `validate`, and `report` if they are still justified;
- JSON-first CLI output for automation;
- README workflow examples.

CLI commands must call the Python API rather than reimplementing core logic.

## Phase 15: Hardening And Release Prep

Goal: add quality, documentation, release, and packaging improvements only where evidence shows they will pay for themselves.

Candidate work:

- linting, formatting, type checking, coverage, or pre-commit if useful;
- richer docs or release metadata;
- packaging/release readiness;
- next roadmap horizon after unsupported workbook semantics are better understood.

Avoid tooling churn without demonstrated pain.

## Planning Discipline

These future phases are backlog lanes, not permission to work around the active phase.

Rules:

- Keep one active parent phase and feature branch unless explicitly approved otherwise.
- Treat future-phase issues as placeholders until activated.
- Refine future child issues when evidence changes, but keep roadmap and GitHub synchronized.
- Prefer small package-backed increments over broad rewrites.
- Preserve the distinction between tracked fixtures and ignored private/generated workbook artifacts.
