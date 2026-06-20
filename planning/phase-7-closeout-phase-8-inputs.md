# Phase 7 Closeout And Phase 8 Inputs

Date: 2026-06-20

## Purpose

This note closes the Phase 7 validation scenario and comparison-core work and defines the validation inputs needed by Phase 8 workbook extraction.

Phase 7 moved the validation prototype concepts into package code without adding workbook extraction, generated-model execution, oracle execution, CLI commands, or Excel-backed validation.

## Validation Core Now Supports

Tracked package code now supports:

- loading JSON validation scenarios into typed records;
- preserving explicit scenario provenance for source workbook path, generated model path, oracle backend, input declarations, output declarations, and comparison rules;
- comparing observed numeric outputs with absolute tolerance and per-output overrides;
- comparing observed text outputs with exact matching;
- reporting missing generated outputs and missing oracle outputs;
- reporting unsupported output kinds through diagnostics rather than silent success;
- building a JSON-serializable validation report from a scenario plus already-observed generated and oracle value mappings;
- exposing report status, all comparisons, mismatches, and run-level diagnostics through stable record objects.

The current implementation is intentionally scalar and fixture-backed. It can validate values once another layer has already produced generated and oracle output mappings.

## Still Deferred

The validation core does not yet:

- read source workbooks;
- mutate scenario inputs into a workbook or generated model;
- execute generated Python models;
- execute `formulas`, Excel, or any other oracle backend;
- normalize Excel error values, blanks, booleans, dates, percentages, arrays, or ranges beyond the current declared scalar kinds;
- resolve workbook, worksheet, or named-range references;
- infer outputs from workbook structure;
- provide a CLI or persisted report file writer.

Those behaviors belong in later extraction, graph, generation, oracle, and CLI phases.

## Phase 8 Extraction Inputs

Phase 8 should produce workbook extraction records that validation and later generation can rely on:

- workbook-level metadata and diagnostics;
- worksheet records with explicit sheet names and visibility where available;
- cell records for constants, formulas, blanks, and unsupported values;
- formula records that preserve the original formula text and source cell reference;
- named-range records with workbook or worksheet scope;
- extraction diagnostics for unsupported workbook features, external links, macros, volatile formulas, array formulas, circular references, and ambiguous names.

Extraction should keep every workbook reference explicit enough for later scenario output declarations such as `Summary!B2` to be matched back to extracted cells.

## Phase 8 Test Inputs

Recommended first tests:

- extract the controlled synthetic workbook from a pytest temporary path;
- confirm the expected sheets, formulas, constants, and named ranges are present;
- confirm extraction records are JSON-serializable at package boundaries;
- confirm unsupported or absent features produce empty diagnostics rather than omitted diagnostic fields;
- avoid committing generated workbook binaries or large extracted JSON outputs.

## Phase 9 And Later Handoff

The Phase 8 extraction records should leave enough information for Phase 9 to build dependency edges without reparsing workbook files.

Later validation phases should be able to combine:

- extracted workbook outputs and formula provenance;
- generated-model output mappings;
- oracle output mappings;
- `ValidationScenario` declarations;
- `build_validation_report`.

The next durable gap is workbook extraction, not broader validation orchestration.
