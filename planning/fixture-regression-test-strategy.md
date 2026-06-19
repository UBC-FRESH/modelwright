# Fixture And Regression-Test Strategy

Date: 2026-06-19

## Purpose

This note defines the first fixture and regression-test strategy for Sheetforge.

The decision is intentionally limited to test assets and regression shape. It does not add the package skeleton, pytest configuration, CI, CLI, or durable implementation code yet.

## Fixture Principles

Tracked fixtures should be compact, synthetic, source-like, and reproducible.

Rules:

- Prefer a tracked fixture builder for generated `.xlsx` files.
- Keep generated workbooks, generated models, emitted IR JSON, and validation reports in pytest temporary directories.
- Commit small scenario and expected-output JSON files when they are stable enough to serve as contracts.
- Do not commit private workbooks, client workbooks, bulky generated artifacts, local Excel caches, or prototype outputs from `tmp/`.
- Every fixture should state what workbook behavior it covers and what it intentionally does not cover.

## First Fixture Set

Use a tracked synthetic fixture family under `tests/fixtures/` once the package and test skeleton are introduced.

Recommended shape:

```text
tests/
  fixtures/
    synthetic_model/
      README.md
      build_workbook.py
      baseline_scenario.json
      baseline_expected_outputs.json
      numeric_mismatch_scenario.json
      text_mismatch_scenario.json
```

`build_workbook.py` should create the controlled workbook previously prototyped under `tmp/synthetic_model.xlsx`. Tests should call the builder and write the workbook into a pytest temporary directory instead of tracking the generated `.xlsx` file.

The synthetic fixture should cover the known first formula subset:

- workbook-level named ranges resolved to single cells;
- scalar cell references across worksheets;
- arithmetic expressions;
- `ROUND`;
- `IF`;
- comparison with `>`;
- one numeric output cell;
- one text output cell.

Do not expand this first fixture to cover unsupported Excel features. Add separate focused fixtures later for hidden sheets, circular references, volatile formulas, array formulas, external links, errors, blanks, booleans, and workbook-specific edge cases.

## Expected Outputs

The first baseline expected outputs should be:

```json
{
  "scenario_id": "synthetic_model_baseline",
  "outputs": {
    "Summary!B2": {
      "kind": "number",
      "value": 70.2,
      "tolerance": 1e-9
    },
    "Summary!B3": {
      "kind": "text",
      "value": "ok"
    }
  }
}
```

Numeric comparisons should use absolute tolerance only in the first durable tests. Use `1e-9` as the default numeric tolerance and allow per-output overrides.

Text and boolean comparisons should be exact. Blank and error outputs should remain explicitly unsupported until their normalization rules are implemented.

## First Regression Tests

The first package-backed tests should cover validation report behavior before broad extraction or code-generation behavior.

Recommended first tests:

- baseline scenario passes with `status: "pass"` and no mismatches;
- numeric mismatch scenario fails with `numeric_mismatch`, generated value, oracle value, tolerance, and difference;
- text mismatch scenario fails with `text_mismatch`, generated value, and oracle value;
- missing generated output scenario fails with `missing_generated_output`;
- unsupported input override scenario produces `unsupported_input_override` until input mutation is implemented.

This keeps regression coverage close to the Phase 4 validation prototype and avoids pretending that the full spreadsheet conversion pipeline is durable before it exists.

## Private And Source Workbook Handling

Private or real source workbooks should stay under ignored `tmp/` unless the maintainer explicitly chooses a sanitized fixture for tracking.

When a private workbook is used for local regression exploration:

- keep the workbook path under `tmp/`;
- keep generated extracts, generated Python, and validation reports under `tmp/`;
- record only sanitized findings in tracked planning notes;
- avoid copying workbook formulas, values, names, sheet labels, business meaning, or raw validation output into tracked files unless cleared by the maintainer;
- document assumptions and unsupported workbook behavior at a high level.

If a real workbook later needs to become a tracked fixture, first create a separate issue to sanitize it and define what provenance can be public.

## Implementation Timing

Do not create `tests/`, `tests/fixtures/`, or pytest configuration in this task.

P5.5 should use this strategy with `planning/package-dependency-test-stack-decision.md` and `planning/api-cli-boundary-decision.md` to decide the first implementation bootstrap. The likely first code-bearing slice remains:

1. add `src/sheetforge` and `tests`;
2. add minimal validation report and comparison objects;
3. add synthetic fixture builder and baseline expected outputs;
4. add one passing baseline validation test;
5. add one intentional mismatch test.

## Open Questions

- Whether generated `.xlsx` fixtures should ever be tracked directly for cross-tool reproducibility checks.
- Whether `formulas` should be an optional test extra immediately or deferred until validation code lands.
- How many mismatch scenarios are worth adding before extraction and code generation are package-backed.
