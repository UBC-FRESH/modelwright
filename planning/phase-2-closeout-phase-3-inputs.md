# Phase 2 Closeout And Phase 3 Inputs

Date: 2026-06-19

## Purpose

This note closes the Phase 2 extraction-contract work and defines the inputs for Phase 3 code-generation prototyping.

Phase 2 established that a small Sheetforge-owned IR is needed between raw workbook extraction and generated Python. The IR can represent the controlled synthetic workbook well enough to support the first generated-code experiment.

## Extraction Contract Decisions

Sheetforge should keep its own normalized IR instead of treating either `openpyxl` or `formulas` as the project model.

Confirmed decisions:

- Use source workbook provenance as the backbone: workbook, sheet, and cell references.
- Preserve named ranges as first-class records and semantic dependency edges.
- Also emit resolved execution edges from source cells to formula cells for graph ordering.
- Keep raw formula strings, token lists, raw references, normalized references, and observed function names in formula records.
- Represent missing cached formula values and unsupported workbook features as diagnostics.
- Keep the IR JSON-serializable during prototype work.

The first generated-code prototype should consume execution edges for ordering and semantic edges for comments, diagnostics, and traceability.

## Phase 3 Prototype Inputs

The Phase 3 generated-code experiment should use:

- ignored source workbook: `tmp/synthetic_model.xlsx`;
- ignored IR output: `tmp/prototype_ir_output.json`;
- tracked contracts/findings:
  - `planning/workbook-ir-contract.md`;
  - `planning/ir-prototype-findings.md`.

Minimum IR fields needed by code generation:

- `cells[].cell_ref`;
- `cells[].kind`;
- `cells[].raw_value`;
- `cells[].formula.raw_formula`;
- `cells[].formula.raw_references`;
- `cells[].formula.normalized_references`;
- `cells[].formula.functions`;
- `dependencies[]` filtered to `edge_kind == "execution"`;
- `diagnostics[]` and formula-local diagnostics.

Useful but non-blocking IR fields:

- named range records for comments and provenance;
- semantic dependency edges for preserving workbook author intent;
- token lists for diagnostics and later parser work.

## First Supported Formula Subset

The first generated-code experiment should support only the formulas already present in the synthetic workbook:

- arithmetic with `+`, `*`, and parentheses;
- cell references on the same sheet;
- cross-sheet cell references;
- workbook-level named ranges resolved to single cells;
- `ROUND(value, digits)`;
- `IF(condition, true_value, false_value)`;
- comparison with `>`.

Everything else should produce an explicit diagnostic or be left out of scope for the first generated-code experiment.

## Blocking Diagnostics For Code Generation

The first code-generation experiment should stop on:

- unresolved references;
- external workbook links;
- multi-cell ranges used where a scalar is required;
- circular dependencies;
- unsupported array formulas;
- formulas containing unsupported functions or operators.

It may continue with warnings for:

- missing cached formula values;
- semantic named-range edges that also have resolved execution edges;
- cosmetic worksheet metadata that is irrelevant to code generation.

## Phase 3 Workflow Recommendation

Keep the first code-generation experiment under ignored `tmp/`.

Do not add a package layout, dependency manager, public API, CLI, or CI in Phase 3 unless the generated-code prototype proves that tracked source structure is necessary. The durable deliverable for Phase 3 should remain a tracked planning note plus roadmap/changelog/issue updates, not a permanent package scaffold.

## Phase 3 Entry Criteria

Phase 3 can start when:

- Phase 2 child issues are closed;
- the Phase 2 branch has a PR back to `main`;
- the Phase 2 PR is merged or the maintainer explicitly allows Phase 3 to start in parallel.

The first Phase 3 task should be P3.1: define the generated-code prototype contract.
