# Phase 3 Closeout And Phase 4 Inputs

Date: 2026-06-19

## Purpose

This note closes the Phase 3 code-generation prototype work and defines inputs for Phase 4 regression validation.

Phase 3 proved that the controlled Modelwright IR can drive readable generated Python for the synthetic workbook and that the generated outputs match `formulas` for the controlled output cells.

## What Worked

- Execution dependency edges were sufficient to order generated formula functions.
- Semantic dependency edges were useful as provenance comments without affecting calculation.
- Named ranges could remain visible in generated comments while resolved source cells drove execution.
- A narrow formula subset was enough for the first generated model: arithmetic, scalar references, resolved workbook-level named ranges, `ROUND`, `IF`, and `>`.
- The generated module was readable and runnable as plain Python.
- Generated outputs matched `formulas` for the controlled workbook outputs:
  - `Summary!B2 = 70.2`;
  - `Summary!B3 = "ok"`.

## Support-Code Needs

The next durable implementation will need explicit support layers before this becomes more than a scratch prototype:

- formula translation with clear supported/unsupported syntax boundaries;
- dependency graph utilities for topological ordering, cycle diagnostics, and source/target queries;
- IR validation before generation;
- provenance-aware generated-code naming and comments;
- diagnostic objects for generation blockers and warnings;
- comparison/mismatch reporting reusable by validation workflows;
- fixture and scenario handling for repeated validation cases.

Do not add package layout, CLI, dependency manager, test framework, or CI until Phase 4 clarifies the validation contract.

## Remaining Limits

The current generated-code prototype does not support:

- general Excel formula parsing;
- multi-cell ranges;
- sheet-local named ranges;
- external workbook links;
- array formulas;
- volatile functions;
- circular dependencies;
- broad operator/function coverage;
- scenario/input variation;
- direct Excel-backed validation.

These limits should become explicit validation cases or diagnostics rather than implicit assumptions.

## Phase 4 Validation Inputs

Phase 4 should define a validation loop with:

- a source workbook path;
- a generated model path or generated callable;
- named output cells to compare;
- optional scenario inputs;
- an oracle backend, initially `formulas`;
- numeric tolerance rules;
- exact comparison rules for text and boolean outputs;
- mismatch records with cell provenance and both observed values.

The first validation scenario can remain the synthetic workbook:

```text
Workbook: tmp/synthetic_model.xlsx
Generated model: tmp/generated_model.py
Outputs:
  Summary!B2 -> expected 70.2
  Summary!B3 -> expected "ok"
Oracle: formulas
```

## Oracle Strategy

Use `formulas` as the first pure-Python oracle because it already calculated the synthetic workbook without Excel.

Use Excel-backed validation, likely through `xlwings`, only when:

- `formulas` disagrees with known Excel behavior;
- a workbook uses functions or workbook features outside pure-Python evaluator coverage;
- cached workbook values are missing or untrusted and Excel is available as the source of truth.

Excel-backed validation should remain optional and platform-aware because it requires a live Excel runtime.

## Phase 4 Entry Criteria

Phase 4 can start when:

- Phase 3 child issues are closed;
- the Phase 3 branch has a PR back to `main`;
- the Phase 3 PR is merged or the maintainer explicitly allows parallel work.

The first Phase 4 task should be P4.1: define validation scenario and oracle contract.
