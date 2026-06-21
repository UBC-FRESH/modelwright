# Phase 26 Full FABLE Benchmark Validation

Phase 26 validates generated Modelwright Python output against cached workbook oracle values for the
2020 FABLE Calculator benchmark. This phase is intentionally stricter than prior selected-output runs.

## Primary Workbook

Use the official external benchmark workbook materialized under the ignored canonical path:

```text
tmp/private-workbooks/2020_Open_FABLECalculator.xlsx
```

The workbook binary remains untracked. Benchmark provenance and checksums remain tracked under
`benchmarks/fable-calculator/`.

## Full-Validation Contract

The phase should report these scopes separately:

- `formula_universe`: every extracted formula cell in the workbook.
- `translated_formula_universe`: formula cells with translated Modelwright formula expressions.
- `candidate_output_universe`: translated formula cells selected for generated-model output comparison.
- `comparable_output_universe`: candidate outputs with cached workbook values and scalar kinds Modelwright can compare.
- `validated_output_universe`: comparable outputs that were generated, executed, and compared.

Pass language is only allowed when:

- generated Python imports and executes without runtime failure;
- every comparable generated output is present;
- every comparable generated output matches the cached workbook value within declared tolerance;
- every skipped cell has a specific diagnostic category.

If this is not achieved, the closeout must say "blocked" or "partial" and list exact blocker counts and
examples. Do not call selected-output validation "full" validation.

## Iterative Convergence Loop

For each run:

1. Extract workbook facts.
2. Build the dependency graph.
3. Translate formulas.
4. Infer the widest generated-model contract possible.
5. Generate Python.
6. Execute generated Python.
7. Compare outputs to cached workbook values.
8. Classify blockers.
9. Fix Modelwright blockers.
10. Rerun from the earliest affected stage.

Stop only when full comparable-output validation passes, or when remaining blockers are explicitly
classified as accepted source-workbook or scope limitations.

## Evidence: 2026-06-21 Full-Scale Runs

Ignored local artifacts:

- `tmp/logs/p26-full-validation.log`
- `tmp/logs/p26-rerun.log`
- `tmp/p26-fable-full-validation/summary.json`
- `tmp/p26-fable-full-validation/blockers.json`

Observed full-scale status:

- extraction completed for the 2020 FABLE workbook: 54 sheets, 395,482 extracted cells,
  296,976 formula cells;
- dependency graph construction completed with 3,543,800 total edges and zero graph diagnostics;
- formula translation completed for 296,976 of 296,976 formula cells with zero translation
  diagnostics;
- candidate output universe contained 296,976 translated formula cells;
- comparable cached output universe contained 281,741 scalar cached outputs:
  239,943 numeric and 41,798 text outputs;
- 15,235 translated formula cells had blank cached values and were classified as
  `non_comparable_cached_blank`;
- contract inference reached workbook scale: 373,410 generated symbols, 289,951 formula
  expressions, 83,459 input constants, and 281,741 declared outputs;
- the widest generated Python model was generated under ignored `tmp/` and executed with verbose
  progress;
- generated execution completed for the full comparable-output universe;
- validation status is `pass`: 281,741 comparable outputs, 281,741 matches, and 0 mismatches;
- the comparable universe included 239,943 numeric outputs and 41,798 text outputs;
- 15,235 translated formula cells had blank cached values and were classified as
  `non_comparable_cached_blank`; these define a validation-boundary category, not a blocker for
  comparable-output validation.

Resolved during this pass:

- Excel `IF(test, value_if_true)` with an omitted false branch is now generated as a supported
  two-argument form instead of crashing with `ValueError("IF requires three operands")`.
- formula renderability failures are now surfaced as structured generation diagnostics before
  module rendering.
- contract inference expands range dependency sources locally rather than requiring graph-wide
  range-edge explosion.
- missing sparse cells inside referenced ranges are treated as blank generated inputs instead of
  fatal missing dependency cells.
- verbose progress was added for graph construction, contract inference, Python generation, and
  generated-model execution.
- generated models now treat direct blank scalar references as Excel-compatible zero values in
  scalar formulas and VLOOKUP table results, while preserving blanks as explicit non-comparable
  validation-boundary evidence when the cached workbook output itself is blank.
- validation comparison now supports the Phase 26 numeric policy:
  `absolute_difference <= 1e-9` or `relative_difference <= 1e-12`.

Resolved AO29 blocker:

- Static dependency cycles are now recorded as warning diagnostics during contract inference rather
  than fatal generation blockers.
- Generated models now evaluate formula cells lazily, cache runtime values, and raise runtime circular
  dependency errors only when the active execution path re-enters a cell.
- Excel criteria matching now handles bare string criteria case-insensitively while preserving
  numeric-text criteria matches and wildcard handling.
- `SUMIF` and `SUMIFS` now ignore text and blank values in sum ranges, matching the workbook behavior
  needed by the AO29 dependency slice.
- Numeric arithmetic rendering treats blank generated inputs as zero for the tested arithmetic slice.

Targeted AO29 evidence:

- Cached smoke log: `tmp/logs/p26-ao29-lazy-smoke.log`.
- Generated targeted model: `tmp/p26-fable-full-validation/ao29_lazy_model.py`.
- The cached smoke hit the extraction, graph, and expression cache before regenerating the targeted
  model.
- `3_calc_crops!AO29` matched the cached workbook value exactly:
  `27844.896576581647`.
- The immediate upstream probes also matched cached workbook values, including `3_calc_crops!AP29`,
  `3_calc_crops!AT29`, `3_calc_crops!AS29`, `3_calc_crops!AU29`, `3_calc_crops!AV29`,
  `1_calc_human_demand!V32`, `1_calc_human_demand!X32`, and `2_calc_livestock!BD34`.

Current blocker:

- No Phase 26 comparable-output blocker remains.
- P26 release closeout remains: run full local verification, publish `v0.1.0a2`, and verify the
  clean PyPI install claim.

Next convergence target:

1. Run full local verification for the release candidate.
2. Tag and publish `v0.1.0a2` through the existing release workflow.
3. Verify clean install from PyPI.
4. Defer performance, memory, and generated-output architecture refactoring to Phase 27 and the
   `0.1.0a3` release line.

## Logs And Raw Artifacts

Raw artifacts stay ignored under `tmp/p26-fable-full-validation/`.

Use these ignored logs:

- `tmp/logs/p26-full-validation.log`
- `tmp/logs/p26-materialize.log`
- `tmp/logs/p26-rerun.log`

Before long commands, print the matching `tail -f` command.
