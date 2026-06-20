# Phase 17 Semantics Prioritization

Date: 2026-06-20

## Purpose

This note completes P17.1 by ranking the real-workbook formula and reference semantics exposed by sanitized private evaluation findings. It does not copy private formulas, workbook names, sheet names, named ranges, values, paths, or raw diagnostic payloads into tracked files.

Primary inputs:

- `planning/private-workbook-eval-001-findings.md`;
- `planning/phase-16-closeout-phase-17-inputs.md`;
- existing extraction, reference, graph, and formula diagnostics in `src/sheetforge/`.

## Ranked Semantics Gaps

1. Structured table references.

   These blocked the `formulas` oracle on the private workbook and are not currently represented as a first-class reference kind. They should be recorded explicitly before Sheetforge tries to translate them. This is the next implementation slice.

2. Unsupported Excel functions.

   Private evaluation showed this as the largest translation gap by count. Function support should be expanded only after the parser/reference layer can distinguish ordinary cell/range references from structured references and other unsupported forms.

3. Unsupported formula token forms.

   Token gaps are the next parser-level blocker after structured references. They should be grouped by sanitized diagnostic category before implementation so the project does not add one-off parser behavior.

4. Unsupported operators.

   Operators are lower count than function and token gaps, but they can affect dependency extraction and translation correctness. Add focused synthetic fixtures before supporting new operators.

5. External workbook references.

   Sheetforge already records external references as unsupported dependency sources. Phase 17 should preserve that behavior and avoid translation until multi-workbook provenance and validation policy are clearer.

6. Volatile functions.

   Extraction diagnostics already identify known volatile functions. Keep them visible as validation-risk diagnostics rather than translating them casually.

7. Unresolved named ranges.

   Named-range resolution already exists for supported workbook-level names. Phase 17 should not broaden this until structured references and table-like name forms are separated from ordinary named ranges.

8. Formula cells without cached values.

   Missing cached values are already extraction diagnostics. This remains a validation-evidence issue and should feed Phase 19 automated evaluation/reporting work.

## Next Implementation Slice

P17.2 should add structured-reference extraction records and diagnostics.

The goal is not full structured-reference calculation. The goal is to make structured references explicit, countable, and safe:

- detect table-style structured reference tokens or formulas during extraction/reference parsing;
- preserve the raw reference text only in local/private outputs, not tracked private findings;
- add a reference kind or diagnostic that distinguishes structured references from generic unresolved references;
- ensure dependency graph diagnostics identify structured-reference dependencies without pretending they are executable cell dependencies;
- add synthetic fixtures with non-private table formulas;
- keep generation blocked for formulas that depend on structured references until translation semantics are implemented.

## Acceptance Criteria For P17.2

- Synthetic workbook fixture contains at least one structured-reference formula.
- Extraction or reference parsing emits an explicit structured-reference diagnostic or record.
- Dependency graph output preserves provenance and marks structured-reference dependencies unsupported.
- Formula translation fails with a structured-reference diagnostic rather than a generic token failure where practical.
- Existing external-reference, volatile-function, named-range, and missing-cache diagnostics continue to pass.

## Deferred Work

Do not implement these in P17.2 unless they are required to represent structured references safely:

- full Excel table object modeling;
- structured-reference evaluation;
- automatic conversion of table references into cell ranges;
- broad new Excel function support;
- external workbook execution;
- volatile function calculation;
- cache-value validation policy.

Those belong in later P17 tasks or Phase 19 validation/report orchestration.
