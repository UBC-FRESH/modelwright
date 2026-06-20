# Phase 9 Closeout And Phase 10 Inputs

Date: 2026-06-20

## Purpose

This note closes the Phase 9 dependency graph core and defines inputs for Phase 10 formula translation.

Phase 9 added canonical workbook references and dependency graph construction on top of extracted workbook records. It did not add formula expression translation, generated Python code, oracle execution, CLI behavior, or persisted graph reports.

## Graph Core Now Supports

Tracked package code now supports:

- `WorkbookReference` records for cells, ranges, named ranges, external references, and unresolved references;
- reference normalization for sheet-relative cells, explicit sheet references, quoted sheet names, ranges, named ranges, and external references;
- `DependencyEdge` records with source, target, edge kind, raw reference provenance, and optional `resolved_from`;
- `DependencyGraph` records with semantic edges, execution edges, and graph-level diagnostic codes;
- graph building from `WorkbookRecord` formula cells without reparsing workbook files;
- workbook-level named-range resolution into execution edges;
- semantic edges that preserve raw workbook references such as `BaseVolume`;
- execution edges that point to actual upstream cells such as `Inputs!B2`;
- range expansion for execution edges;
- initial diagnostics for external references, unsupported dependency kinds, and simple two-cell circular dependencies.

The synthetic workbook graph tests confirm the expected execution dependency chain:

```text
Inputs!B2 -> Calc!B2
Inputs!B3 -> Calc!B2
Calc!B2 -> Calc!B3
Inputs!B4 -> Calc!B3
Calc!B3 -> Calc!B4
Calc!B4 -> Summary!B2
Summary!B2 -> Summary!B3
```

## Still Deferred

The graph core does not yet:

- parse formula expressions into operations;
- validate whether functions are supported by code generation;
- preserve Excel operator precedence beyond token provenance;
- build a topological evaluation order;
- detect circular dependencies beyond direct two-cell cycles;
- handle multi-workbook references beyond diagnostics;
- distinguish sheet-local named ranges from workbook-level names beyond existing scope metadata;
- diagnose ambiguous named ranges;
- attach rich diagnostic records to graph outputs;
- write graph reports to disk.

Those behaviors belong in formula translation, generation, validation, and later reporting phases.

## Phase 10 Formula Translation Inputs

Phase 10 should consume:

- `CellRecord.formula.raw_formula` for source formula text;
- `FormulaRecord.tokens` and `FormulaRecord.functions` for the first translation pass;
- `FormulaRecord.raw_references` for provenance;
- `DependencyGraph.execution_edges` for upstream cell inputs;
- `DependencyGraph.semantic_edges` and `DependencyEdge.resolved_from` for explanation and traceability;
- graph diagnostics that identify references or dependency kinds that translation should not silently ignore.

Phase 10 should add:

- an internal formula expression model;
- translation for the controlled synthetic subset: arithmetic, comparisons, `ROUND`, and `IF`;
- explicit unsupported-function diagnostics;
- translation tests tied to extracted cells and graph edges;
- a clear boundary between formula translation and Python code generation.

## Suggested Phase 10 Acceptance Checks

For the synthetic workbook, Phase 10 should translate:

- `=BaseVolume*(1+GrowthRate)` into a multiplication expression with two resolved upstream inputs;
- `=B2*Inputs!B4` into a multiplication expression using sheet-relative and explicit-sheet references;
- `=ROUND(B3,2)` into a supported round operation;
- `=Calc!B4` into a direct reference expression;
- `=IF(B2>50,"ok","low")` into a conditional expression with comparison and text literals.

Translation should fail closed with diagnostics for formulas outside the supported subset.
