# Phase 20 Validation And Evaluation Plan

Date: 2026-06-20

## Purpose

Phase 20 turns the Phase 19 blocker-resolution evidence into repeatable generated-model execution and
validation reporting.

The 2020 FABLE benchmark is no longer blocked by extraction, graph, or translation diagnostics. Phase 20
should therefore stop treating conversion status as a planning report only and start producing repeatable
evidence about generated Python behavior.

## Starting Evidence

Phase 19 final 2020 FABLE conversion-plan evidence:

- formula cells: 296,976;
- translated formula cells: 296,976;
- untranslated formula cells: 0;
- graph diagnostics: empty;
- translation diagnostics: empty;
- structured-reference extraction diagnostics: resolved provenance;
- volatile-function extraction diagnostics: resolved provenance;
- external-link diagnostics: deferred to explicit materialize, mock, or reject policy;
- missing cached formula values: deferred to oracle/cached-validation strategy.

## Tasks

### P20.1 Generated Model Execution API

Goal: execute generated Python modules from explicit contracts and return JSON-serializable observed
outputs and diagnostics.

Acceptance criteria:

- define the smallest package API needed to execute generated Python in tests;
- keep execution separate from workbook extraction;
- support explicit input overrides and output refs;
- add synthetic fixture tests before using benchmark workbooks.

### P20.2 Oracle And Cached-Value Validation Orchestration

Goal: compare generated outputs against cached workbook values and oracle outputs where available.

Acceptance criteria:

- preserve missing cached values as validation limitations, not generation failures;
- preserve oracle failures as explicit validation blockers;
- produce validation reports with clear output counts, mismatches, and blockers.

### P20.3 Evaluation Report CLI And JSON Outputs

Goal: expose the repeatable evaluation workflow through thin CLI commands and JSON reports.

Acceptance criteria:

- add CLI wrappers over package APIs only;
- emit JSON suitable for ignored local benchmark reports;
- keep verbose progress logging available for long workbook runs.

### P20.4 Repeatable Evaluation Closeout

Goal: run the synthetic and 2020 FABLE evaluation workflows and record what is proven.

Acceptance criteria:

- run synthetic evaluation end to end;
- run 2020 FABLE evaluation with verbose logging;
- write ignored local reports under `tmp/`;
- record what is proven, what remains unproven, and Phase 21 inputs.

## Non-Goals

- Do not claim full workbook equivalence before generated outputs are compared against usable oracle or
  cached workbook values.
- Do not silently ignore external dependencies or missing cached values.
- Do not create broad service or UI surfaces in this phase.
