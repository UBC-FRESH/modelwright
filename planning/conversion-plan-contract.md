 # Conversion Plan Contract

Date: 2026-06-20

## Purpose

This note defines the Phase 18 conversion plan contract.

The conversion plan is not the generated Python model. It is the inspectable decision record that explains what Sheetforge can currently do with a workbook:

- what source workbook was inspected;
- which benchmark role the workbook plays;
- how much workbook logic was extracted, graphed, translated, generated, and validated;
- which cells or formulas remain unsupported;
- which residual blockers are defects, semantics gaps, validation gaps, or deferred structural work;
- what the next action should be.

The goal is to stop treating conversion as a binary "works or does not work" result. Real workbooks need partial-conversion reporting with provenance.

## Contract Status

This is a Phase 18 planning contract, not a stable public schema.

Implementation should keep the first package records JSON-serializable and close to this shape, but field names may still change before a release.

## Benchmark Roles

Each conversion plan should classify the source workbook's local evaluation role.

Allowed benchmark roles:

- `primary_benchmark`: the current main private workbook used to ratchet development forward.
- `stress_benchmark`: a larger or more complex workbook used after the primary benchmark is stable.
- `broken_reference_regression`: a workbook known to contain explicit broken source references, used to verify diagnostics rather than conversion coverage.
- `synthetic_fixture`: a tracked workbook fixture built for deterministic tests.
- `ad_hoc_private`: a local workbook evaluated for exploration but not yet selected as a benchmark.

Current private benchmark policy:

- 2020 workbook: `primary_benchmark`.
- 2021 workbook: `stress_benchmark`.
- 2019 workbook: `broken_reference_regression`.

Tracked public docs and planning notes should avoid raw private workbook names where possible. Official external benchmarks may be named in tracked files when the repository tracks only metadata, source URLs, and checksums rather than workbook binaries. Local ignored reports may include filenames.

## Top-Level Shape

Prototype JSON shape:

```json
{
  "plan_id": "private-2020-baseline",
  "created_at": "2026-06-20T00:00:00Z",
  "sheetforge_commit": "unknown",
  "source": {},
  "workflow_status": {},
  "coverage": {},
  "diagnostic_summary": {},
  "residual_blockers": [],
  "generation": {},
  "validation": {},
  "recommendations": [],
  "privacy_review": {}
}
```

## Records

### ConversionPlan

Fields:

- `plan_id`: stable local identifier for this plan.
- `created_at`: ISO timestamp when the plan was created.
- `sheetforge_commit`: Git commit used for the evaluation.
- `source`: `ConversionSource`.
- `workflow_status`: `WorkflowStatus`.
- `coverage`: `CoverageSummary`.
- `diagnostic_summary`: `DiagnosticSummary`.
- `residual_blockers`: list of `ResidualBlocker`.
- `generation`: `GenerationSummary`.
- `validation`: `ValidationSummary`.
- `recommendations`: list of `PlanRecommendation`.
- `privacy_review`: `PrivacyReview`.

### ConversionSource

Fields:

- `workbook_id`: local workbook identifier or sanitized label.
- `file_type`: workbook suffix, such as `.xlsx`.
- `benchmark_role`: one benchmark role from this contract.
- `source_path`: optional local path; allowed only in ignored local reports.
- `sanitized`: boolean indicating whether private identifiers were removed.

Rules:

- Tracked planning notes should use sanitized labels and counts.
- Ignored local reports may include local paths to make reruns practical.

### WorkflowStatus

Fields:

- `extraction`: `pass`, `blocked`, or `not_run`.
- `dependency_graph`: `pass`, `blocked`, or `not_run`.
- `formula_translation`: `pass`, `blocked`, or `not_run`.
- `generation`: `pass`, `blocked`, or `not_run`.
- `cached_validation`: `pass`, `fail`, `blocked`, or `not_run`.
- `oracle_validation`: `pass`, `fail`, `blocked`, or `not_run`.
- `overall`: `complete`, `partial`, or `blocked`.

Rules:

- `overall` is `complete` only when all target formulas needed by the declared conversion scope are translated, generated, and validated.
- `overall` is `partial` when Sheetforge can produce useful generated output but still has residual blockers.
- `overall` is `blocked` when no generated output can be produced or a required early stage fails.

### CoverageSummary

Fields:

- `sheets`: integer.
- `cells`: integer.
- `value_cells`: integer.
- `formula_cells`: integer.
- `translated_formula_cells`: integer.
- `untranslated_formula_cells`: integer.
- `translation_coverage`: number between 0 and 1.
- `named_ranges`: integer.
- `dependency_edges`: integer.
- `semantic_edges`: integer.
- `execution_edges`: integer.

Rules:

- Counts should come from package records, not ad hoc spreadsheet scans when possible.
- `translation_coverage` is `translated_formula_cells / formula_cells`.

### DiagnosticSummary

Fields:

- `workbook_extraction`: map of diagnostic code to count.
- `named_ranges`: map of diagnostic code to count.
- `formula_extraction`: map of diagnostic code to count.
- `graph`: map of diagnostic code to count.
- `translation`: map of diagnostic code to count.
- `generation`: map of diagnostic code to count.
- `oracle`: map of diagnostic code to count.
- `cached_validation`: map of diagnostic code to count.
- `formulas_validation`: map of diagnostic code to count.

Rules:

- Diagnostic codes should remain stable enough for comparison across runs.
- The plan may include additional `ResidualBlocker` records for diagnostics that require classification.

### ResidualBlocker

Fields:

- `blocker_id`: stable identifier inside the plan.
- `category`: one of `source_workbook_defect`, `unsupported_formula_semantics`, `unsupported_reference_semantics`, `graph_semantics`, `generation_scope`, `validation_oracle`, `missing_cached_values`, `external_dependency`, or `unknown`.
- `diagnostic_code`: related diagnostic code when available.
- `item`: sanitized function, token, reference kind, or feature name.
- `count`: count of affected formulas, cells, references, or diagnostics.
- `severity`: `info`, `warning`, or `error`.
- `disposition`: one of `resolved`, `blocked_by_design`, `deferred`, `out_of_scope`, or `next_target`.
- `next_action`: short action statement.
- `provenance`: source stage such as `extraction`, `graph`, `translation`, `generation`, or `validation`.

Rules:

- A blocker with `disposition=next_target` should be actionable enough to become a task or subtask issue.
- Source workbook defects should not be treated as Sheetforge semantics gaps.
- Validation oracle failures should be separated from formula translation failures.
- Extraction, named-range, graph, cached-value, volatile-function, structured-reference, and external-link diagnostics should remain visible as residual blockers even when formula translation coverage is complete.

### GenerationSummary

Fields:

- `generated`: boolean.
- `generated_model_path`: optional local ignored path.
- `selected_outputs`: integer.
- `selected_input_dependencies`: integer.
- `selection_strategy`: short label, such as `direct_outputs_with_constant_dependencies`.
- `full_workbook_model`: boolean.

Rules:

- `full_workbook_model` must be false for the current private evaluation lane.
- Generated subset success must not be described as full workbook import.

### ValidationSummary

Fields:

- `cached_validation_status`: `pass`, `fail`, `blocked`, or `not_run`.
- `cached_outputs`: integer.
- `cached_mismatches`: integer.
- `oracle_backend`: backend name, such as `formulas`.
- `oracle_status`: `pass`, `fail`, `blocked`, or `not_run`.
- `oracle_mismatches`: integer.
- `oracle_blockers`: list of diagnostic codes.

Rules:

- Cached-value validation is useful evidence but not a recalculation oracle.
- If the source workbook oracle cannot run, the plan should say that explicitly.

### PlanRecommendation

Fields:

- `priority`: integer, lower means sooner.
- `action`: short action title.
- `rationale`: short explanation.
- `target_issue`: optional GitHub issue number when known.

Examples:

- Add `IFNA` semantics for `_XLFN.IFNA`.
- Build conversion-plan API.
- Keep 2019 explicit error references blocked by design.
- Investigate pure-Python oracle limitation or introduce optional Excel-backed oracle.

### PrivacyReview

Fields:

- `contains_source_path`: boolean.
- `contains_sheet_names`: boolean.
- `contains_named_ranges`: boolean.
- `contains_raw_formulas`: boolean.
- `contains_raw_cell_values`: boolean.
- `contains_generated_source`: boolean.

Rules:

- Tracked conversion-plan examples must have all fields false unless the source is a synthetic fixture.
- Ignored local reports may include private details needed for local reruns, but sanitized tracked notes must not.

## Partial-Conversion Semantics

Sheetforge should use precise language:

- `extracted`: workbook facts were loaded into package records.
- `graphed`: dependency graph records were built.
- `translated`: formula text was converted into Sheetforge expression records.
- `generated_subset`: a selected subset was emitted as Python and executed.
- `validated_subset`: generated subset outputs matched cached or oracle values.
- `full_model_generated`: all formulas in the declared conversion scope were emitted.
- `full_workbook_equivalent`: generated model was validated against an accepted oracle for the declared outputs and scenarios.

Do not say "fully imports" unless `full_model_generated` and the declared validation requirements both pass.

## Current Benchmark Examples

### 2020 Primary Benchmark

Sanitized Phase 18 baseline after the `_XLFN.IFNA` ratchet:

- benchmark role: `primary_benchmark`;
- formula cells: 296,976;
- translated formula cells: 296,976;
- untranslated formula cells: 0;
- translation coverage: 1.0;
- residual translation blocker: none;
- residual translation blocker count: 0;
- structured-reference first failures: 0;
- explicit error-reference first failures: 0;
- cached validation subset: 10 outputs, 0 mismatches;
- oracle validation: blocked.

Prior blocker resolved during Phase 18 activation:

```json
{
  "blocker_id": "translation-001",
  "category": "unsupported_formula_semantics",
  "diagnostic_code": "unsupported_function",
  "item": "_XLFN.IFNA",
  "count": 657,
  "severity": "warning",
  "disposition": "resolved",
  "next_action": "No further formula-translation action needed for this blocker.",
  "provenance": "translation"
}
```

The next 2020 benchmark target is no longer formula translation coverage. It is conversion-plan reporting, full generated-model scope, and stronger validation evidence.

### 2019 Broken-Reference Regression

Sanitized Phase 17 closeout:

- benchmark role: `broken_reference_regression`;
- formula cells: 215,728;
- translated formula cells: 215,422;
- untranslated formula cells: 306;
- residual translation blocker: explicit error references;
- explicit error-reference count: 306;
- cached validation subset: 10 outputs, 0 mismatches;
- oracle validation: blocked.

Recommended blocker record:

```json
{
  "blocker_id": "source-defect-001",
  "category": "source_workbook_defect",
  "diagnostic_code": "unsupported_error_reference",
  "item": "#REF!",
  "count": 306,
  "severity": "warning",
  "disposition": "blocked_by_design",
  "next_action": "Report explicit source error references; do not silently generate normal Python behavior.",
  "provenance": "translation"
}
```

## P18.1 Acceptance Criteria

P18.1 is complete when:

- this contract identifies the top-level plan shape;
- residual blocker classification is explicit;
- partial-conversion language is defined;
- current private benchmark roles are documented;
- P18.2 has enough detail to implement package records and tests without reading private workbook files.
