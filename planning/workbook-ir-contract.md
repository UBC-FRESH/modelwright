# Workbook IR Contract

Date: 2026-06-19

## Purpose

This note defines the minimum intermediate representation (IR) for the next Modelwright prototype.

The IR should sit between raw workbook extraction and generated Python:

```text
workbook file
  -> extraction facts from openpyxl/formulas
  -> Modelwright IR
  -> dependency graph and diagnostics
  -> generated Python prototype
```

This is a prototype contract, not a committed public API or package schema.

## Design Decisions

- Use workbook/sheet/cell provenance as the backbone of the IR.
- Preserve named ranges as first-class records so analyst intent is not lost.
- Also resolve named ranges to destination references for dependency graph analysis.
- Store raw formulas and token-derived references separately from normalized dependency edges.
- Represent ambiguity and unsupported workbook features as diagnostics, not silent omissions.
- Keep the IR JSON-serializable for scratch prototypes and review.

## Minimum Records

### WorkbookRecord

Represents one source workbook.

Fields:

- `workbook_id`: stable local identifier for this extraction run, initially the workbook filename.
- `source_path`: local path used during extraction.
- `sheets`: list of `SheetRecord`.
- `named_ranges`: list of `NamedRangeRecord`.
- `cells`: list of `CellRecord`.
- `dependencies`: list of `DependencyEdge`.
- `diagnostics`: list of `DiagnosticRecord`.

### SheetRecord

Represents one worksheet.

Fields:

- `sheet_id`: canonical sheet name.
- `title`: original sheet title.
- `state`: worksheet visibility/state when available.
- `index`: workbook sheet order.

### CellRef

Canonical reference to a single cell.

Shape:

```text
SheetName!A1
```

Rules:

- Preserve original sheet spelling.
- Use A1 coordinates.
- Remove `$` absolute-reference markers in canonical refs.
- Do not include workbook filename for same-workbook references in the first prototype.
- Add workbook qualification later when external links or multi-workbook extraction are implemented.

### NamedRangeRecord

Represents workbook-defined names and their destinations.

Fields:

- `name`: original defined name.
- `scope`: workbook-level or sheet-local scope if available.
- `raw_definition`: original definition text.
- `destinations`: normalized destination refs when resolvable.
- `status`: `resolved`, `partially_resolved`, or `unresolved`.

Decision:

Named ranges remain first-class records. Dependency extraction may emit both:

- an edge from the named range to the formula cell for intent/provenance; and
- resolved edges from destination cells to the formula cell for graph execution.

### CellRecord

Represents one non-empty source cell.

Fields:

- `cell_ref`: canonical `CellRef`.
- `kind`: `value`, `formula`, or `blank`.
- `raw_value`: value or formula string as extracted.
- `cached_value`: cached value when available.
- `data_type`: source library data type.
- `formula`: `FormulaRecord` when `kind` is `formula`.

Rules:

- Do not treat missing cached formula values as errors.
- Do not infer semantic input/output roles from position or labels yet.

### FormulaRecord

Represents one formula cell.

Fields:

- `raw_formula`: original formula string, including leading `=`.
- `tokens`: token list from the extractor.
- `raw_references`: references as they appear in tokens.
- `normalized_references`: resolved references where possible.
- `functions`: function names observed in tokens.
- `diagnostics`: formula-local diagnostics.

Rules:

- Token extraction is not the same as full Excel parsing.
- Sheet-relative references must resolve against the formula cell's sheet.
- Named ranges must resolve through `NamedRangeRecord` when possible.

### DependencyEdge

Represents a directed dependency.

Fields:

- `source_ref`: upstream cell, named range, or unresolved reference.
- `target_ref`: formula cell that depends on the source.
- `source_kind`: `cell`, `named_range`, `range`, `external`, or `unresolved`.
- `edge_kind`: `semantic` or `execution`.
- `raw_reference`: original token text that produced the edge.
- `diagnostics`: edge-local diagnostics.

Rules:

- `semantic` edges preserve workbook author intent, such as `BaseVolume -> Calc!B2`.
- `execution` edges point from resolved cell dependencies to formula cells, such as `Inputs!B2 -> Calc!B2`.
- Graph ordering should use `execution` edges only in the first prototype.

### DiagnosticRecord

Represents an extraction or interpretation concern.

Fields:

- `severity`: `info`, `warning`, or `error`.
- `code`: stable diagnostic code.
- `message`: short human-readable message.
- `location`: workbook, sheet, cell, named range, or dependency edge location.
- `raw_value`: optional raw source text.

Initial diagnostic codes:

- `missing_cached_formula_value`
- `unresolved_reference`
- `unsupported_external_link`
- `unsupported_volatile_function`
- `unsupported_array_formula`
- `circular_dependency`
- `ambiguous_named_range`

## First Prototype Acceptance Criteria

The next ignored prototype should emit JSON for `tmp/synthetic_model.xlsx` with:

- one `WorkbookRecord`;
- three `SheetRecord` entries;
- two resolved `NamedRangeRecord` entries;
- `CellRecord` entries for all non-empty cells;
- `FormulaRecord` entries for `Calc!B2`, `Calc!B3`, `Calc!B4`, `Summary!B2`, and `Summary!B3`;
- semantic edges for named ranges and raw references;
- execution edges matching the normalized dependency chain from `planning/first-prototype-findings.md`;
- warnings for missing cached formula values.

## Non-Goals

- No package layout yet.
- No public API yet.
- No committed JSON schema yet.
- No CLI yet.
- No code generation yet.
- No attempt to cover external links, multi-cell ranges, array formulas, VBA, or circular references beyond diagnostics.

## Next Step

Create an ignored prototype script under `tmp/` that emits this IR as JSON for the existing synthetic workbook, then record findings in a tracked planning note.
