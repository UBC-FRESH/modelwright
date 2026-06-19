# Validation Prototype Findings

Date: 2026-06-19

## Question

Can Sheetforge run a validation scenario that compares generated Python outputs against a workbook oracle and reports mismatches in a reusable shape?

## Prototype Setup

Ignored scratch files under `tmp/`:

- `tmp/validation_scenario.json`: baseline scenario definition.
- `tmp/prototype_validate.py`: validation runner.
- `tmp/generated_model.py`: generated Python model from Phase 3.
- `tmp/synthetic_model.xlsx`: source workbook fixture.
- `tmp/prototype_validation_report.json`: validation report.
- `tmp/prototype-venv/`: local environment with `formulas`.

Commands used:

```bash
tmp/prototype-venv/bin/python -m py_compile tmp/prototype_validate.py
tmp/prototype-venv/bin/python tmp/prototype_validate.py
```

## Verified Output

The validation prototype passed with no mismatches.

Comparison records:

```json
[
  {
    "cell_ref": "Summary!B2",
    "kind": "number",
    "generated": 70.2,
    "oracle": 70.2,
    "matches": true,
    "tolerance": 1e-9,
    "difference": 0.0
  },
  {
    "cell_ref": "Summary!B3",
    "kind": "text",
    "generated": "ok",
    "oracle": "ok",
    "matches": true
  }
]
```

## Findings

- The validation scenario shape from `planning/validation-scenario-oracle-contract.md` is practical for the baseline synthetic workbook.
- The runner can execute the generated Python model and calculate the source workbook through the `formulas` oracle.
- Numeric comparison with absolute tolerance works for `Summary!B2`.
- Exact text comparison works for `Summary!B3`.
- The report shape includes `status`, `comparisons`, `mismatches`, and `diagnostics`.
- No package layout, public API, CLI, test framework, or CI was needed.

## Limits

- The prototype supports only the `formulas` oracle.
- Scenario input overrides are rejected rather than applied.
- Excel-backed validation is still deferred.
- Numeric tolerance behavior has only been exercised on an exact match.
- Error values, missing outputs, booleans, and intentional mismatches still need explicit handling notes.

## Next Step

P4.3 should define mismatch diagnostics and tolerance rules in more detail, including:

- numeric tolerance defaults and per-output overrides;
- exact comparison behavior for text and booleans;
- missing generated or oracle outputs;
- oracle errors and generated-model exceptions;
- stable mismatch record fields for future implementation.
