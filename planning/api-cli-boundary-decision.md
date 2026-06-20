# API And CLI Boundary Decision

Date: 2026-06-19

## Purpose

This note defines the first public API and CLI boundaries for Sheetforge.

The decision is intentionally conservative: Phase 5 should prepare a small Python package API first, and defer CLI implementation until package responsibilities and fixtures are stable.

## Responsibility Boundaries

Keep these responsibilities separate:

- workbook extraction and IR construction;
- dependency/reference utilities;
- code generation;
- validation scenarios and oracle backends;
- diagnostics and validation report objects.

Do not create one monolithic conversion function that hides extraction, generation, and validation behavior.

## Initial Python API Shape

The first durable package should expose small, explicit functions or classes around the proven prototype steps.

Candidate module layout:

```text
sheetforge/
  __init__.py
  ir.py
  extract.py
  generate.py
  validate.py
  diagnostics.py
```

Candidate entrypoints:

- `extract_workbook(path) -> WorkbookRecord`
- `generate_python_model(ir, output_path) -> GenerationResult`
- `load_validation_scenario(path) -> ValidationScenario`
- `validate_generated_model(scenario) -> ValidationReport`

The exact dataclass names can be finalized during implementation, but the API should keep workbook path, generated model path, scenario path, oracle backend, and output cells explicit.

## Data Objects

The first durable API should prefer typed Python objects for internal use and JSON-serializable dictionaries at boundaries.

Likely objects:

- `WorkbookRecord`
- `SheetRecord`
- `CellRecord`
- `FormulaRecord`
- `DependencyEdge`
- `Diagnostic`
- `GenerationResult`
- `ValidationScenario`
- `ValidationReport`
- `ComparisonResult`

These should remain simple dataclasses or equivalent lightweight structures at first.

## Dependency Boundaries

Default package behavior may depend on:

- `openpyxl` for extraction.

Validation oracle support should be optional:

- `formulas` belongs behind a validation/oracle boundary.
- `xlwings` belongs behind a separate Excel-backed optional boundary, not default runtime behavior.

Code generation should rely on the standard library unless a concrete need appears.

## CLI Boundary

Do not implement a CLI in the first durable package slice.

Phase 16 established the grouped Typer surface:

```text
sheetforge workbook extract
sheetforge workbook graph
sheetforge model generate
sheetforge validation report
```

CLI commands should be thin wrappers over the Python API. They should not reimplement extraction, generation, or validation logic.

Default CLI output should eventually support JSON for automation. Human-readable formatting can come later.

## First Implementation Boundary

The first implementation bootstrap should focus on:

- package skeleton;
- core data objects;
- validation report/comparison structures;
- fixture-backed tests for one baseline validation path and one intentional mismatch.

It should not implement all candidate entrypoints at once.

Recommended first durable slice:

1. Add `src/sheetforge` and `tests`.
2. Add minimal validation data/report objects.
3. Add a fixture-backed validation test for the synthetic baseline.
4. Add one intentional mismatch test.

Extraction and code generation can be brought in after the validation/report shape is stable, unless P5.5 decides otherwise.

## Non-Goals

- No CLI implementation in Phase 5 unless explicitly approved later.
- No public stability guarantee yet.
- No Excel-backed validation in default API.
- No broad conversion pipeline API yet.
- No hidden dependence on ignored `tmp/` artifacts.
