# Mismatch Diagnostics And Tolerance Rules

Date: 2026-06-19

## Purpose

This note defines comparison behavior and mismatch diagnostics for Modelwright validation reports.

The goal is to make validation failures stable, explainable, and tied back to workbook output cells before any durable validation API or test framework is introduced.

## Comparison Result Shape

Each output comparison should produce one record:

- `scenario_id`: validation scenario identifier.
- `cell_ref`: output cell being compared, such as `Summary!B2`.
- `kind`: declared output kind: `number`, `text`, `boolean`, `blank`, or `error`.
- `generated`: generated-model value after normalization.
- `oracle`: oracle value after normalization.
- `matches`: boolean comparison result.
- `tolerance`: numeric tolerance used, or `null`.
- `difference`: numeric absolute difference when available, or `null`.
- `diagnostic_code`: stable code, or `null` when values match.
- `message`: concise explanation.
- `oracle_backend`: backend used, initially `formulas`.

Validation reports should include:

- `status`: `pass` when all comparisons match, otherwise `fail`;
- `comparisons`: all comparison records;
- `mismatches`: comparison records where `matches` is false;
- `diagnostics`: run-level warnings or errors that are not tied to one output value.

## Numeric Rules

Numeric comparisons use absolute tolerance first.

Rules:

- Use per-output `tolerance` when present.
- Otherwise use scenario `default_numeric_tolerance`.
- Default numeric tolerance is `1e-9`.
- Normalize integers and floats to Python numeric values before comparison.
- `matches` is true when `abs(generated - oracle) <= tolerance`.
- Record `difference` as `abs(generated - oracle)`.
- If either value cannot be interpreted as numeric, record `numeric_type_mismatch`.

Future work may add relative tolerance, but do not add it to the first validation prototype.

## Text Rules

Text comparisons are exact.

Rules:

- Normalize both values to Python strings only when the declared kind is `text` and both values are already string-like.
- Do not trim whitespace.
- Do not fold case.
- Do not normalize Unicode beyond whatever the oracle and generated model already return.
- Record `text_mismatch` when values differ.

## Boolean Rules

Boolean comparisons are exact.

Rules:

- Compare Python `True`/`False` values directly.
- Do not treat `1` and `True` as equivalent in validation reports.
- Record `boolean_mismatch` when boolean values differ.
- Record `boolean_type_mismatch` when one or both values are not booleans.

## Blank And Error Rules

Blank and error handling should be explicit.

Rules:

- Blank values should normalize to `null` in JSON reports.
- Declared `blank` outputs match only when both generated and oracle values are blank/null.
- Excel-style error values should eventually normalize to an explicit object such as `{"error": "#DIV/0!"}`.
- Until error normalization exists, record unsupported or unequal error outputs as mismatches.

## Missing Output Rules

Missing outputs are mismatches unless the validation run cannot proceed at all.

Rules:

- Missing generated output records `missing_generated_output`.
- Missing oracle output records `missing_oracle_output`.
- If both are missing, record `missing_generated_and_oracle_output`.
- Include the missing `cell_ref` and scenario id in the comparison record.

## Exception Rules

Exceptions should be captured as diagnostics.

Rules:

- Generated-model import or execution failures record `generated_exception`.
- Oracle load or calculation failures record `oracle_exception`.
- Scenario parsing failures record `invalid_scenario`.
- Unsupported oracle backend records `unsupported_oracle_backend`.
- Unsupported output kind records `unsupported_output_kind`.

If a run-level exception prevents all output comparisons, the report should still include `status: "fail"` and a run-level diagnostic when possible.

## Diagnostic Codes

Initial comparison diagnostic codes:

- `numeric_mismatch`
- `numeric_type_mismatch`
- `text_mismatch`
- `boolean_mismatch`
- `boolean_type_mismatch`
- `blank_mismatch`
- `error_mismatch`
- `missing_generated_output`
- `missing_oracle_output`
- `missing_generated_and_oracle_output`
- `unsupported_output_kind`

Initial run-level diagnostic codes:

- `generated_exception`
- `oracle_exception`
- `invalid_scenario`
- `unsupported_oracle_backend`
- `unsupported_input_override`

## Provenance Requirements

Every mismatch must include enough provenance to act on it:

- scenario id;
- output cell reference;
- oracle backend;
- generated value;
- oracle value;
- diagnostic code;
- message.

Future durable implementations should also include source workbook path, generated model path, and optionally formula/source-cell provenance from the IR.

## P4.4 Inputs

The Phase 4 closeout should carry forward:

- validation scenario shape from `planning/validation-scenario-oracle-contract.md`;
- validation prototype findings from `planning/validation-prototype-findings.md`;
- mismatch and tolerance rules from this note;
- recommendation to keep validation implementation deferred until package/API decisions in Phase 5.
