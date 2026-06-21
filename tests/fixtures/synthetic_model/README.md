# Synthetic Model Fixture

This fixture is a compact synthetic workbook used for Modelwright package tests.

It covers:

- three worksheets: `Inputs`, `Calc`, and `Summary`;
- workbook-level named ranges: `BaseVolume` and `GrowthRate`;
- scalar cross-sheet references;
- arithmetic formulas;
- `ROUND`;
- `IF`;
- comparison with `>`;
- numeric output `Summary!B2`;
- text output `Summary!B3`.

It does not cover hidden sheets, circular references, volatile formulas, array formulas, external links, macros, errors, blanks, booleans, or workbook-specific business semantics.

Use `build_workbook.py` to create the `.xlsx` file in a pytest temporary directory. Do not commit generated `.xlsx` files, generated reports, or local scratch outputs from this fixture.
