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

## P17 Formula And Operator Scope

A local private-workbook diagnostic aggregation was run under ignored `tmp/` to identify the unsupported formula semantics needed by the current private sample workbook. The tracked scope below includes only sanitized Excel function/operator/token names and counts. It does not include source formulas, workbook names, sheet names, named ranges, values, or paths.

The current P17 goal is broad enough to cover every unsupported function and operator observed in the private sample workbook's first-failure translation diagnostics:

| Category | Item | Count | P17 stance |
| --- | ---: | ---: | --- |
| Function | `SUMIFS` | 89,853 | In scope for P17 translation support. |
| Function | `IFERROR` | 25,674 | In scope for P17 translation support. |
| Function | `AND` | 12,372 | In scope for P17 translation support. |
| Function | `SUMIF` | 5,220 | In scope for P17 translation support. |
| Function | `COUNTIFS` | 1,164 | In scope for P17 translation support. |
| Function | `MIN` | 1,144 | In scope for P17 translation support. |
| Function | `OR` | 858 | In scope for P17 translation support. |
| Function | `SUM` | 724 | In scope for P17 translation support. |
| Function | `AVERAGE` | 307 | In scope for P17 translation support. |
| Function | `CONCATENATE` | 288 | In scope for P17 translation support. |
| Function | `OFFSET` | 165 | In scope for P17 diagnostics and, if feasible, constrained support; volatile/reference-returning semantics make this higher risk than scalar functions. |
| Operator | `^` | 1,898 | In scope for P17 translation support. |
| Operator | `&` | 80 | In scope for P17 translation support. |
| Token | `FALSE` | 24,266 | In scope for P17 boolean literal support. |
| Token | `#REF!` | 306 | In scope for explicit error-reference diagnostics, not silent translation. |
| Token | unary `-` | 135 | In scope for P17 unary operator support. |

These counts are first-failure diagnostics, not a complete proof that the listed items are the only required semantics. The translator stops when it hits the first unsupported construct in a formula, so implementing high-count items may reveal additional unsupported functions, operators, token forms, or reference forms in later passes.

## Full Private Sample Import Scope

To fully import the current private sample workbook, P17 needs more than adding scalar Excel functions. The intended P17 scope is:

- represent structured references distinctly and keep them blocked unless table semantics are modeled;
- support the listed functions where their inputs can be represented by existing scalar/range expression records;
- support the listed operators and boolean literals;
- add explicit diagnostics for `#REF!`, unsupported structured/table semantics, unresolved named ranges, external references, volatile/reference-returning behavior, and missing cached values;
- keep generation blocked for formulas whose dependencies or semantics remain unsupported;
- rerun sanitized private diagnostics after each expansion slice to discover second-order blockers.

This scope is intentionally wide enough to pursue full private-sample import, but P17 should still land it in slices. The project should not claim full workbook equivalence until generated outputs are validated against cached workbook values, `formulas`, Excel-backed validation, or an explicitly documented hybrid oracle.

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

## P17.3 Starting Scope

P17.3 should start with expression-model changes that unlock many of the listed items without touching table semantics:

- boolean literals, especially `FALSE`;
- unary minus;
- `&` string concatenation;
- `^` exponentiation;
- scalar logical functions: `AND`, `OR`;
- scalar error handling: `IFERROR`;
- scalar/range aggregations: `SUM`, `MIN`, `AVERAGE`;
- criteria aggregations: `SUMIF`, `SUMIFS`, `COUNTIFS`;
- text concatenation: `CONCATENATE`;
- explicit diagnostics for `#REF!`;
- constrained `OFFSET` handling or a more specific unsupported diagnostic if safe support is not feasible in P17.

Structured-reference evaluation, external workbook execution, and unconstrained volatile/reference-returning formulas remain blocked until their provenance and validation semantics are explicit.
