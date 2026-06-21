# Long-Term Roadmap

Date: 2026-06-20

## Purpose

This note records the current planning horizon beyond the active Phase 7 work.

The sequence is intentionally staged. Modelwright should move from scenario/report mechanics to extraction, dependency analysis, formula translation, generated Python, oracle-backed validation, private workbook evaluation, API/CLI stabilization, and then hardening. The project should not jump directly to a broad conversion pipeline before the intermediate contracts are proven.

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
  -> CLI/docs public surface alignment
  -> real workbook semantics expansion
  -> conversion planning
  -> automated validation reports
  -> alpha publication and deployment workflow
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

## Phase 16: CLI And Documentation Public Surface

Goal: bring Modelwright's public CLI and docs surface into the same family as the other FRESH lab software packages.

Reference models:

- `fhops`: Typer/Rich CLI with grouped command surfaces, explicit output paths, curated Sphinx guide/reference/API pages, warning-clean docs builds, and a practical workflow tone.
- `femic`: Typer/Rich CLI, Sphinx docs with guides/sample-models/reference sections, and a GitHub Pages workflow that builds on pull requests and deploys on pushes to `main`.

Expected outputs:

- CLI conventions audit against local `~/projects/fhops` and `~/projects/femic` checkouts;
- Modelwright CLI refactor plan and implementation using the same Typer/Rich feel where it is justified;
- full Sphinx docs skeleton with curated guide, CLI reference, API reference, workflow, limitations, and private-data handling pages;
- GitHub Actions docs workflow that runs `sphinx-build -b html docs _build/html -W` and deploys to GitHub Pages on `main`;
- README links and local docs build instructions.

The CLI should still call Python APIs rather than reimplementing core logic. The docs should be honest about partial conversion and unsupported spreadsheet semantics.

## Phase 17: Real Workbook Formula Semantics

Goal: expand formula and reference semantics based on real workbook evidence.

Expected focus:

- structured table-reference formulas;
- unsupported functions from private evaluation findings;
- parser token forms and operators that currently produce diagnostics;
- external references, volatile functions, unresolved named ranges, and cached-value gaps;
- synthetic coverage for newly supported semantics without committing private workbook data.

Phase 17 should improve explicit support or explicit diagnostics. It should not claim full workbook equivalence.

## Phase 18: Conversion Planning And Pipeline Orchestration

Goal: define a conversion plan workflow that explains what can be converted, what cannot be converted, and how generated outputs should be validated.

Expected outputs:

- conversion plan JSON contract;
- API that composes extraction, graphing, translation, generation diagnostics, and validation targets;
- CLI command for plan/report output;
- tests that prove partial-conversion behavior is explicit.

The conversion plan should make unsupported cells visible rather than hiding them behind a broad `convert` command.

## Phase 19: Residual Blocker Resolution For Full Benchmark Import

Goal: resolve or explicitly scope the residual blockers exposed by the 2020 FABLE conversion plan before treating validation automation as proof that the system works.

Expected outputs:

- named-range resolution or explicit out-of-scope classification;
- circular dependency semantics and generated-model policy;
- workbook dependency, volatile-function, structured-reference diagnostic, and cached-value policies;
- repeated 2020 FABLE conversion-plan run showing no unowned residual blocker categories.

This phase is about convergence. Validation automation should not become a polished report over unresolved structural blockers.

## Phase 20: Automated Validation And Evaluation Reports

Goal: make generated-model execution, oracle execution where available, cached-value comparisons, and private evaluation reports repeatable after residual blockers have concrete owners or scope decisions.

Expected outputs:

- generated model execution API;
- oracle/cached-value validation orchestration;
- evaluation report CLI and JSON outputs;
- sanitized private-evaluation summary workflow.

Excel-backed validation remains optional and should not enter default CI unless it has a controlled, documented environment.

Closeout result:

- synthetic generated-model evaluation is proven end to end through the CLI;
- 2020 FABLE extraction, dependency graphing, and formula translation remain clean;
- full 2020 FABLE workbook equivalence remains unproven until a generated-model contract can be inferred,
  topologically ordered, materialized, and validated against selected benchmark outputs.

## Phase 21: Full Benchmark Model Materialization And Validation

Goal: turn clean benchmark conversion evidence into an executable generated Python model and validate
selected outputs until the blocker-find-resolve-rerun loop converges.

Expected outputs:

- generated-model contract inference from dependency graphs and selected outputs;
- topological symbol ordering for large generated modules;
- a materialized 2020 FABLE generated model under ignored local artifacts;
- selected 2020 FABLE output validation against cached values or an explicit oracle;
- explicit residual blocker list if full equivalence still cannot be claimed.

This phase is the next convergence gate. It should not accept a planning-only result if a concrete blocker
can be reproduced, fixed, and rerun within the phase.

## Phase 22: PyPI Publication And Deployment Workflow

Goal: establish a professional deployment and publication workflow before any real PyPI release.

Expected outputs:

- explicit alpha release target and publication policy;
- maintainer-approved project license before real PyPI publication;
- hardened package metadata, project URLs, classifiers, and version handling;
- local sdist/wheel build checks, artifact inspection, and clean install smoke tests;
- CI release artifact validation;
- maintainer-gated TestPyPI and real PyPI publication workflows;
- GitHub release/tag policy;
- deployment runbook for maintainers and contributor-facing release onboarding docs;
- GitHub Pages verification that the published site is the Sphinx Read the Docs themed artifact rather than a fallback Jekyll/minima site.

Publication should remain gated. The project can be ready for a TestPyPI/internal alpha before it is ready for real PyPI. The first published alpha should use canonical Python packaging syntax such as `0.1.0a1` or `1.0.0a1`, and the decision between those version lines should be explicit.

## Planning Discipline

These future phases are backlog lanes, not permission to work around the active phase.

Rules:

- Keep one active parent phase and feature branch unless explicitly approved otherwise.
- Treat future-phase issues as placeholders until activated.
- Refine future child issues when evidence changes, but keep roadmap and GitHub synchronized.
- Prefer small package-backed increments over broad rewrites.
- Preserve the distinction between tracked fixtures and ignored private/generated workbook artifacts.
