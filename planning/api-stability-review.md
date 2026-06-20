# API Stability Review

Date: 2026-06-20

## Purpose

Phase 14 starts by reviewing Sheetforge's Python API before adding command-line wrappers. The goal is to make the current API boundaries explicit and avoid turning accidental helpers into public commitments.

Sheetforge is still pre-release. This review stabilizes the package shape enough for a thin CLI, but it does not create a long-term compatibility guarantee.

## Primary Module Boundaries

The package should stay organized by responsibility:

- `sheetforge.extraction`: workbook, sheet, cell, formula, named-range, and extraction diagnostics; `extract_workbook`.
- `sheetforge.graph`: dependency edge and graph records; `build_dependency_graph`.
- `sheetforge.formulas`: formula expression records, translation diagnostics, formula translation, and reference-index construction.
- `sheetforge.generation`: generated-module contracts, generated symbols, generation diagnostics, and Python source generation.
- `sheetforge.validation`: scenario, comparison, diagnostic, and report records; scenario loading; scalar comparison; report assembly.
- `sheetforge.oracles`: oracle request/result/diagnostic records and backend protocol.
- `sheetforge.formulas_oracle`: optional pure-Python `formulas` oracle implementation.
- `sheetforge.oracle_validation`: report assembly from generated outputs and oracle results.

Module-level imports are preferred for implementation code because they make responsibility boundaries explicit.

## Curated Root Facade

The package root `sheetforge` may expose convenience imports for primary records and functions, but it should not export implementation-only aliases or helper functions that are not intended as user entrypoints.

Kept at the root facade:

- primary record objects;
- primary extraction, graph, translation, generation, oracle, and validation functions;
- optional oracle backend class;
- `__version__`.

Removed from the root facade:

- `FormulaReferenceIndex`, because it is an implementation type alias for translation performance;
- `OracleOutputs`, because it is an implementation type alias for oracle result payloads;
- `missing_optional_dependency_diagnostic`, because it is an internal helper for backend implementations;
- `symbol_name_for_cell_ref`, because it is a generation implementation helper rather than a user workflow entrypoint.

These helpers may still be imported from their implementation modules when package internals or tests need them.

## Stable Enough For CLI

The next CLI work should wrap these module APIs without adding new conversion behavior:

- inspect/extract workbook facts with `extract_workbook`;
- build dependency graph facts with `build_dependency_graph`;
- generate Python source with `generate_python_module`;
- load scenarios and build validation reports with `sheetforge.validation`;
- run optional oracle-backed validation through explicit oracle APIs.

The CLI should not hide unsupported workbook semantics. It should surface diagnostics and JSON reports.

## Deferred

Do not add a broad `convert_workbook` API yet. Real workbook evaluation showed that full conversion depends on unresolved choices around structured references, unsupported functions, external references, volatile functions, cached values, and oracle strategy.
