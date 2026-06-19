# Phase 4 Closeout And Phase 5 Inputs

Date: 2026-06-19

## Purpose

This note closes the Phase 4 regression-validation prototype work and defines inputs for Phase 5 package, API, CLI, test, and CI decisions.

Phase 4 proved that a validation scenario can run a generated Python model, calculate the same workbook through a `formulas` oracle, compare outputs, and emit a structured report with comparison and mismatch records.

## Validation Findings

Confirmed:

- The validation scenario contract is practical for the controlled synthetic workbook.
- `formulas` works as the first pure-Python oracle.
- Generated-model outputs can be normalized and compared to oracle outputs.
- Numeric outputs can use absolute tolerance with per-output overrides.
- Text outputs can use exact comparison.
- Validation reports should include `status`, `comparisons`, `mismatches`, and `diagnostics`.
- Mismatch records should include scenario id, output cell provenance, generated value, oracle value, diagnostic code, and message.

Still deferred:

- Excel-backed validation with `xlwings`.
- Scenario input mutation.
- Error-value normalization.
- Boolean and blank-output fixtures.
- Intentional mismatch fixture coverage.
- Durable package/API/test/CI implementation.

## Minimum Future Fixtures

Phase 5 should decide whether these fixtures become tracked test assets:

- synthetic baseline workbook;
- baseline IR output or a reproducible generator for it;
- generated model output or a reproducible generator for it;
- expected validation scenario definition;
- expected validation report for a passing run;
- intentional numeric mismatch scenario;
- intentional text mismatch scenario;
- missing generated output scenario;
- missing oracle output scenario;
- numeric tolerance boundary scenario.

Do not commit bulky or private source workbooks as fixtures.

## Phase 5 Package Inputs

Phase 5 should decide whether to introduce a real package layout.

If introduced, the package should separate:

- workbook extraction and IR construction;
- dependency/reference utilities;
- code generation;
- validation scenarios and oracle backends;
- diagnostics and report objects.

The package should not expose internal scratch assumptions from `tmp/`.

## Phase 5 API Inputs

Potential first public or semi-public APIs:

- load or build workbook IR;
- generate Python from IR;
- load validation scenario;
- run validation scenario;
- return structured validation report.

The API should keep workbook paths, generated model paths, scenario definitions, and oracle selection explicit.

## Phase 5 CLI Inputs

A CLI is useful only after the package boundaries are clear.

Potential commands:

- inspect workbook;
- emit IR;
- generate model;
- validate generated model;
- summarize validation report.

CLI output should be structured enough to support automation, likely JSON by default for prototype commands.

## Phase 5 Test And CI Inputs

Phase 5 should choose:

- test framework;
- fixture location;
- whether generated artifacts are checked in or regenerated during tests;
- default validation commands;
- CI scope.

Default CI should avoid Excel-backed validation. Excel-backed validation should be optional and explicitly marked because it requires a live Excel runtime.

## Phase 5 Recommendation

Introduce a minimal tracked package only if Phase 5 also introduces focused tests.

Recommended first durable slice:

- tracked synthetic fixture or fixture builder;
- minimal source modules for IR, code generation, and validation report structures;
- tests covering the baseline validation path and one intentional mismatch;
- no CLI until the Python API shape is stable.

Keep `xlwings` and Excel-backed validation out of the default dependency set.
