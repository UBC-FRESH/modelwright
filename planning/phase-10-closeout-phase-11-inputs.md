# Phase 10 Closeout And Phase 11 Inputs

Date: 2026-06-20

## Purpose

This note closes the Phase 10 formula translation core and defines inputs for Phase 11 generated Python model work.

Phase 10 added expression records and the first supported formula translator for the controlled synthetic workbook subset. It did not generate Python code, execute translated expressions, persist translated expression reports, or add a CLI.

## Formula Translation Core Now Supports

Tracked package code now supports:

- formula expression records for literals, references, binary arithmetic, comparisons, and function calls;
- formula-level provenance through source cell reference and raw formula text;
- formula translation diagnostics with severity, location, and raw source value;
- translation from `CellRecord` formula facts plus `DependencyGraph` edges;
- dependency-backed reference resolution, including named ranges resolved to upstream cells;
- arithmetic translation for the synthetic subset;
- comparison translation for `>`;
- supported function-call translation for `ROUND` and `IF`;
- explicit error diagnostics for unsupported functions and unsupported operators.

The synthetic workbook tests confirm translation for:

- `=BaseVolume*(1+GrowthRate)`;
- `=B2*Inputs!B4`;
- `=ROUND(B3,2)`;
- `=Calc!B4`;
- `=IF(B2>50,"ok","low")`.

## Still Deferred

The formula translation core does not yet:

- evaluate formula expressions;
- generate Python source;
- infer calculation order;
- translate broader Excel semantics such as dates, errors, arrays, lookup functions, aggregation beyond the tested subset, boolean functions, or text functions;
- preserve every Excel operator precedence nuance beyond the current supported subset;
- normalize locale-specific formula syntax;
- translate external workbook references;
- provide a CLI or persisted translation report.

Unsupported formulas should continue to fail closed with diagnostics rather than being partially translated.

## Phase 11 Generated Model Inputs

Phase 11 should consume:

- `WorkbookRecord` for workbook and cell provenance;
- `DependencyGraph.execution_edges` for dependency order;
- `FormulaExpression` records for translated formula logic;
- `FormulaTranslationDiagnostic` records for formulas that cannot be generated;
- validation fixture outputs for the synthetic workbook.

Phase 11 should add:

- a generated module contract;
- a small generation result record;
- Python source generation for the translated synthetic model;
- generated function names or symbol names derived from canonical cell references;
- provenance comments that tie generated code back to workbook cells and raw formulas;
- tests that execute generated code from a temporary directory and compare baseline outputs.

## Suggested Phase 11 Acceptance Checks

For the synthetic workbook, generated Python should compute:

- `Summary!B2 == 70.2`;
- `Summary!B3 == "ok"`.

Generated code should remain standalone Python and should not depend on Excel, `openpyxl`, or source workbook files at runtime.
