# First Prototype Findings

Date: 2026-06-19

## Question

Can Modelwright's first prototype path use `openpyxl` for extraction and `formulas` for calculation/model inspection without creating a committed package scaffold?

## Prototype Setup

Ignored scratch files under `tmp/`:

- `tmp/prototype-venv/`: isolated local virtual environment.
- `tmp/prototype_openpyxl_formulas.py`: scratch script that creates and inspects the fixture.
- `tmp/synthetic_model.xlsx`: generated synthetic workbook.
- `tmp/prototype_openpyxl_formulas_output.json`: captured prototype output.

The synthetic workbook contains:

- three sheets: `Inputs`, `Calc`, and `Summary`;
- scalar constants;
- formulas using named ranges;
- cross-sheet references;
- `ROUND` and `IF`;
- one numeric output and one text status output.

The command used was:

```bash
tmp/prototype-venv/bin/python tmp/prototype_openpyxl_formulas.py
```

## Findings

`openpyxl` is a good extraction baseline:

- It reported workbook sheets, non-empty cells, values, formulas, data types, defined names, and formula tokens.
- It preserved source-cell provenance naturally through sheet names and cell coordinates.
- It exposed named ranges `BaseVolume` and `GrowthRate` with destinations on `Inputs!B2` and `Inputs!B3`.
- Formula cells created by `openpyxl` had `null` cached values when reloaded with `data_only=True`, confirming that cached formula values cannot be treated as a reliable validation source unless the workbook has been recalculated and saved elsewhere.

A small custom graph layer is still needed:

- Raw formula tokens identify references such as `BaseVolume`, `GrowthRate`, `B2`, `Inputs!B4`, and `Calc!B4`.
- Sheet-relative cell references and named ranges must be resolved into canonical workbook references before dependency analysis.
- For the synthetic workbook, a simple normalized graph produced the expected chain:

```text
Inputs!B2 -> Calc!B2
Inputs!B3 -> Calc!B2
Inputs!B4 -> Calc!B3
Calc!B2 -> Calc!B3
Calc!B3 -> Calc!B4
Calc!B4 -> Summary!B2
Summary!B2 -> Summary!B3
```

`formulas` is promising for early calculation and model inspection:

- It loaded and calculated the synthetic workbook without Excel.
- It calculated `Summary!B2` as `70.2` and `Summary!B3` as `ok`.
- It exposed workbook outputs with fully-qualified keys such as `'[synthetic_model.xlsx]SUMMARY'!B2`.
- It exposed a dispatcher graph through `model.dsp.dmap`, with data nodes, formula/function nodes, and edges.

Important gap:

- `formulas` graph nodes are useful but not yet in the canonical provenance shape Modelwright likely needs. The graph includes intermediate formula-expression nodes, so Modelwright still needs its own normalized workbook reference model even if `formulas` is used for parsing or evaluation.

## Implications

The recommended architecture for the next prototype is:

1. Keep `openpyxl` as the primary workbook extractor.
2. Define a small internal reference model for workbook, sheet, cell, named range, formula, and dependency references.
3. Use `openpyxl` formula tokens for initial dependency extraction, with explicit normalization of named ranges and sheet-relative references.
4. Use `formulas` as the first calculation oracle for pure-Python validation and as a comparison source for dependency behavior.
5. Defer durable package layout, CLI, CI, and dependency manager choices until the internal extraction contract is clearer.

## Next Questions

- What is the smallest tracked intermediate representation for workbook references and formulas?
- Should named ranges be normalized to their destination cells immediately, or preserved as first-class dependency nodes with destination metadata?
- How should Modelwright represent formula-expression nodes versus cell-output nodes?
- What diagnostics should be emitted for unsupported references, external links, volatile functions, circular dependencies, array formulas, and macros?
- Should the next prototype generate a tiny Python function/module for this synthetic workbook, or first formalize the extracted workbook model?
