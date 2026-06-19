# Validation Scenario And Oracle Contract

Date: 2026-06-19

## Purpose

This note defines the first validation scenario and oracle contract for Phase 4.

The goal is to compare generated Python model outputs against an independent workbook oracle in a repeatable way, while still keeping implementation under ignored `tmp/` until the validation shape is proven.

## Validation Scenario Shape

A validation scenario should be JSON-serializable and contain:

- `scenario_id`: stable identifier for the scenario.
- `description`: short human-readable purpose.
- `source_workbook`: path to the workbook being used as the oracle source.
- `generated_model`: path to the generated Python model or module.
- `oracle`: oracle backend configuration.
- `inputs`: optional future input overrides.
- `outputs`: output cells to compare.
- `comparison`: default comparison rules.

Prototype example:

```json
{
  "scenario_id": "synthetic_model_baseline",
  "description": "Baseline validation for the controlled synthetic workbook.",
  "source_workbook": "tmp/synthetic_model.xlsx",
  "generated_model": "tmp/generated_model.py",
  "oracle": {
    "backend": "formulas"
  },
  "inputs": [],
  "outputs": [
    {
      "cell_ref": "Summary!B2",
      "kind": "number",
      "tolerance": 1e-9
    },
    {
      "cell_ref": "Summary!B3",
      "kind": "text"
    }
  ],
  "comparison": {
    "default_numeric_tolerance": 1e-9,
    "text": "exact",
    "boolean": "exact"
  }
}
```

## Oracle Strategy

Use `formulas` as the first validation oracle.

Reasons:

- It runs without Excel.
- It already calculated the synthetic workbook during earlier prototypes.
- It is suitable for routine pure-Python validation experiments in this repo.

The oracle result should be normalized into plain Python scalars before comparison.

## Excel-Backed Validation

Excel-backed validation, likely through `xlwings`, should be optional and introduced only when needed.

Use an Excel-backed oracle when:

- `formulas` disagrees with known Excel behavior;
- a workbook uses unsupported formulas or workbook features;
- volatile functions or cached values make pure-Python validation insufficient;
- a real Excel workbook must be treated as the source of truth.

Do not make Excel or `xlwings` a default requirement for Phase 4 prototypes.

## Input Scenarios

The first scenario has no input overrides.

Future scenarios should represent input changes explicitly with:

- `cell_ref`: target input cell;
- `value`: replacement scalar value;
- `kind`: number, text, boolean, blank, or error;
- `source`: why the input value is being tested.

The validation prototype should not invent scenario mutation logic until a workbook fixture needs it.

## Comparison Rules

Numeric values:

- compare with absolute tolerance;
- default tolerance: `1e-9`;
- record both generated and oracle values when mismatched.

Text values:

- exact comparison.

Boolean values:

- exact comparison.

Missing or error values:

- record as mismatches unless both sides normalize to the same explicit error representation.

## Mismatch Record Shape

Each output comparison should produce a record with:

- `cell_ref`;
- `kind`;
- `generated`;
- `oracle`;
- `matches`;
- `tolerance`;
- `difference` for numeric values when possible;
- `message`;
- `scenario_id`;
- `oracle_backend`.

The validation run should also report:

- `status`: `pass` or `fail`;
- `comparisons`: all comparison records;
- `mismatches`: failed comparison records;
- `diagnostics`: non-comparison warnings or errors.

## P4.2 Acceptance Criteria

The ignored validation prototype should:

- load the baseline scenario;
- run `tmp/generated_model.py`;
- calculate `tmp/synthetic_model.xlsx` with `formulas`;
- compare `Summary!B2` numerically with tolerance `1e-9`;
- compare `Summary!B3` exactly as text;
- emit an ignored JSON validation report under `tmp/`;
- pass with no mismatches;
- avoid package layout, CLI, dependency manager, test framework, and CI.

## Non-Goals

- No tracked validation schema yet.
- No public validation API.
- No Excel-backed oracle in the first prototype.
- No scenario input mutation in the first prototype.
- No durable test framework or CI integration yet.
