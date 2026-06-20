# Phase 12 Closeout And Phase 13 Inputs

Date: 2026-06-20

## What Phase 12 Added

Phase 12 added the first durable oracle-backed validation path:

- oracle request, result, diagnostic, and backend protocol records;
- optional `formulas` dependency metadata;
- a `formulas`-backed workbook oracle for synthetic workbook outputs;
- JSON-scalar normalization for `formulas` result values;
- a validation-report bridge that compares generated model outputs with oracle outputs.

## Current Limits

The `formulas` oracle is intentionally narrow:

- it supports the controlled synthetic workbook baseline;
- it maps requested `Sheet!Cell` outputs to `formulas` workbook result keys;
- it normalizes only scalar JSON-compatible output values;
- it does not support scenario input overrides yet;
- it does not validate against Excel itself;
- it does not cover private workbooks, external links, macros, array formulas, volatile functions, circular references, or workbook-specific assumptions.

These limits should stay visible in diagnostics rather than being silently treated as successful validation.

## CI Boundary

Default CI may run the synthetic `formulas` oracle regression because the workbook is generated in a temporary directory from tracked fixture code.

Default CI should not require Excel, `xlwings`, private source workbooks, local `tmp/` artifacts, or generated validation reports from private models.

## Phase 13 Inputs

Phase 13 should use ignored private workbooks under `tmp/` to evaluate the pipeline locally and record sanitized findings only.

The first private workbook evaluation protocol should record:

- source workbook provenance without committing the workbook;
- which sheets, formulas, names, and outputs were inspected;
- unsupported workbook semantics and oracle failures;
- whether `formulas` can calculate the selected outputs;
- whether generated Python agrees with the oracle for selected scenarios;
- what must change before private-workbook findings can influence public package behavior.
