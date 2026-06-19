# Codegen Prototype Findings

Date: 2026-06-19

## Question

Can the prototype IR drive readable standalone Python generation for the controlled synthetic workbook?

## Prototype Setup

Ignored scratch files under `tmp/`:

- `tmp/prototype_codegen.py`: generator script.
- `tmp/prototype_ir_output.json`: input IR from Phase 2.
- `tmp/generated_model.py`: generated Python model.
- `tmp/prototype_codegen_output.json`: generation summary.

Commands used:

```bash
python3 -m py_compile tmp/prototype_codegen.py
python3 tmp/prototype_codegen.py
python3 tmp/generated_model.py
```

An additional assertion check imported `tmp/generated_model.py` and verified its `calculate()` output.

## Verified Output

The generator emitted:

- constants for required value cells: `Inputs!B2`, `Inputs!B3`, and `Inputs!B4`;
- formula functions in execution dependency order:
  - `calc_b2()`;
  - `calc_b3()`;
  - `calc_b4()`;
  - `summary_b2()`;
  - `summary_b3()`;
- `calculate()` returning `Summary!B2` and `Summary!B3`;
- provenance comments with source formulas and semantic dependencies;
- named-range resolution comments for `BaseVolume` and `GrowthRate`.

The generated model produced:

```json
{
  "Summary!B2": 70.2,
  "Summary!B3": "ok"
}
```

## Findings

The first code-generation contract is practical for the controlled workbook:

- Execution edges from the IR are sufficient to order formula functions.
- Semantic edges are useful as generated comments without affecting calculation.
- Named ranges can remain visible in comments while resolved cell constants drive execution.
- The supported subset can be translated with simple logic for arithmetic, scalar references, `ROUND`, `IF`, and `>`.
- The generated module is readable enough for manual inspection.

No package layout, CLI, dependency manager, test framework, or CI was needed.

## Limits

The prototype translator is intentionally narrow:

- it is not a general Excel formula parser;
- it only handles the formula subset present in `tmp/synthetic_model.xlsx`;
- it assumes scalar execution references;
- it does not handle operator precedence beyond Python-compatible formula text;
- it does not support multi-cell ranges, external links, array formulas, circular dependencies, or unsupported functions.

## Next Step

P3.3 should compare the generated model outputs against the `formulas` calculation results already observed for the same workbook. That comparison should remain under ignored `tmp/` and should record whether generated Python and `formulas` agree on the controlled outputs.
