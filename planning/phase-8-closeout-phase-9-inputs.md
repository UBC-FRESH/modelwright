# Phase 8 Closeout And Phase 9 Inputs

Date: 2026-06-20

## Purpose

This note closes the Phase 8 workbook extraction core and defines the inputs needed for Phase 9 dependency graph work.

Phase 8 moved extraction records and the first `openpyxl` workbook extractor into package code. It did not add dependency graph construction, generated-code behavior, oracle-backed validation, a CLI, or persisted extracted JSON outputs.

## Extraction Core Now Supports

Tracked package code now supports:

- `WorkbookRecord`, `SheetRecord`, `CellRecord`, `FormulaRecord`, `NamedRangeRecord`, and `ExtractionDiagnostic`;
- JSON-serializable `to_dict` and `from_dict` boundaries for extraction records;
- `extract_workbook(path)` using `openpyxl`;
- workbook id and source path provenance;
- worksheet names, visibility states, and workbook order;
- non-empty value and formula cells with canonical `Sheet!A1` cell references;
- formula text, token values, raw range operands, observed function names, and formula-local diagnostics;
- workbook-level defined names with raw definitions, scope, resolved destinations where `openpyxl` provides them, and unresolved-name diagnostics;
- missing cached formula value diagnostics;
- unsupported volatile function diagnostics for the initial volatile function set;
- basic unsupported external-link and macro diagnostics where `openpyxl` exposes those facts;
- JSON-safe scalar normalization for extracted cell and cached values.

The synthetic workbook extraction tests confirm:

- three expected sheets: `Inputs`, `Calc`, and `Summary`;
- two resolved named ranges: `BaseVolume` and `GrowthRate`;
- 22 non-empty cells;
- five formula cells;
- raw formula references and functions for the controlled formulas;
- five missing cached formula value warnings;
- no tracked workbook binaries or generated extraction artifacts.

## Still Deferred

The extraction core does not yet:

- build dependency edges;
- normalize formula references into graph-ready canonical references;
- resolve sheet-relative formula references;
- resolve named ranges inside formula references;
- expand multi-cell ranges;
- distinguish semantic dependency edges from execution dependency edges;
- detect circular references;
- inspect array formulas beyond future diagnostics;
- interpret charts, pivot tables, tables, conditional formatting, styles, macros, or workbook calculation settings;
- classify workbook inputs and outputs;
- write extraction reports to disk.

These behaviors should be handled by the graph, formula translation, reporting, and CLI phases rather than folded into raw workbook extraction.

## Phase 9 Graph Inputs

Phase 9 should build on the extraction records without reparsing workbook files.

Minimum graph inputs now available:

- `WorkbookRecord.sheets` for sheet ordering and valid sheet names;
- `WorkbookRecord.cells` for candidate source and target cells;
- `CellRecord.cell_ref` as the target reference for formula cells;
- `FormulaRecord.raw_references` as the unresolved source reference list;
- `NamedRangeRecord.destinations` for name-to-cell resolution;
- `ExtractionDiagnostic` records that should flow through graph diagnostics.

Phase 9 should add:

- a canonical reference model for workbook, sheet, cell, range, named range, unresolved reference, and external reference cases;
- sheet-relative reference resolution, such as `B2` in `Calc!B3` becoming `Calc!B2`;
- explicit sheet reference preservation, such as `Inputs!B4`;
- named-range resolution, such as `BaseVolume` becoming `Inputs!B2`;
- semantic edges that preserve workbook author references;
- execution edges that represent actual upstream cell dependencies;
- diagnostics for unresolved, ambiguous, external, circular, and unsupported range cases.

## Suggested Phase 9 Acceptance Checks

For the synthetic workbook, Phase 9 should recover these execution dependencies:

```text
Inputs!B2 -> Calc!B2
Inputs!B3 -> Calc!B2
Inputs!B4 -> Calc!B3
Calc!B2 -> Calc!B3
Calc!B3 -> Calc!B4
Calc!B4 -> Summary!B2
Summary!B2 -> Summary!B3
```

It should also preserve semantic references for named ranges and raw formula references so later code generation can explain where resolved dependencies came from.
