# Codegen Comparison Findings

Date: 2026-06-19

## Question

Does the generated Python prototype agree with `formulas` on the controlled workbook outputs?

## Prototype Setup

Ignored scratch files under `tmp/`:

- `tmp/prototype_compare_generated_vs_formulas.py`: comparison script.
- `tmp/generated_model.py`: generated Python model from P3.2.
- `tmp/synthetic_model.xlsx`: source workbook fixture.
- `tmp/prototype_compare_output.json`: comparison output.
- `tmp/prototype-venv/`: local environment with `formulas`.

Commands used:

```bash
tmp/prototype-venv/bin/python -m py_compile tmp/prototype_compare_generated_vs_formulas.py
tmp/prototype-venv/bin/python tmp/prototype_compare_generated_vs_formulas.py
```

## Verified Output

The comparison passed with no mismatches:

```json
{
  "Summary!B2": {
    "generated": 70.2,
    "formulas": 70.2
  },
  "Summary!B3": {
    "generated": "ok",
    "formulas": "ok"
  }
}
```

## Findings

- The generated Python prototype agrees with `formulas` for the controlled workbook outputs.
- The comparison script can report per-cell generated values, `formulas` values, match status, and mismatches.
- For this fixture, exact equality was sufficient for both numeric and text outputs.
- The result supports moving to P3.4 to summarize code-generation readiness.

## Limits

- This does not validate against Excel itself.
- This covers only two output cells and the narrow formula subset in the synthetic workbook.
- Future validation needs numeric tolerances, richer mismatch diagnostics, and scenario/input variation.
- The comparison still depends on ignored scratch artifacts rather than durable package code.

## Next Step

P3.4 should summarize Phase 3 results and define Phase 4 validation inputs, especially:

- which generated-code behavior is ready to carry forward;
- which formula and reference limits remain;
- what a validation scenario contract should include;
- when an Excel-backed oracle such as `xlwings` might become necessary.
