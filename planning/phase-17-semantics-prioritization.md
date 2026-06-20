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

## Iterative Blocker Loop

Phase 17 should explicitly use a blocker-find-resolve-continue loop for the private sample workbook. This is the operating model for P17.3 and P17.4, not an incidental debugging tactic.

Each semantics expansion slice should follow this sequence:

1. Run the private-workbook diagnostic pass under ignored `tmp/`.
2. Record sanitized first-failure counts for unsupported functions, operators, token forms, reference forms, and validation blockers.
3. Select the highest-impact next blocker set that can be implemented with clear synthetic tests and explicit generation behavior.
4. Implement that support or, when support is not safe yet, implement a sharper diagnostic.
5. Rerun focused synthetic tests and the full package verification path.
6. Rerun the private-workbook diagnostic pass.
7. Compare translated formula count, unsupported diagnostic counts, generated subset size, and validation status against the previous run.
8. Record only sanitized findings in tracked planning notes.
9. Repeat until remaining blockers are either resolved or explicitly deferred as structural decisions.

This loop matters because first-failure diagnostics hide downstream blockers. A formula that currently stops at `SUMIFS` may reveal an unsupported operator, token, reference form, or nested function only after `SUMIFS` support is added.

The loop should stop only when one of these conditions is true:

- the selected private-workbook import scope translates and validates against accepted workbook evidence;
- remaining blockers require a larger design phase, such as table semantics, external workbook execution, volatile calculation policy, or validation-oracle architecture;
- the maintainer explicitly narrows the target import scope.

Translation progress is necessary but not sufficient. A slice is not "good to go" for workbook import unless generated outputs can also be validated against cached workbook values, `formulas`, Excel-backed validation, or a documented hybrid oracle.

## Convergence Contract

P17 should converge toward importing the private sample workbook. Convergence means each implementation pass must make measurable progress toward a smaller, clearer blocker set and a larger validated generated subset.

The baseline from the current private diagnostic pass is:

- formula cells: 215,728;
- translated formula cells: 51,274;
- untranslated formula cells: 164,454;
- first-failure unsupported functions: 137,769;
- first-failure unsupported formula tokens: 24,707;
- first-failure unsupported operators: 1,978;
- generated direct-output subset validated against cached workbook values: 10 outputs, 0 mismatches.

Each P17.3 implementation pass must report:

- translated formula count delta;
- unsupported diagnostic count delta by code;
- top remaining unsupported function/operator/token categories;
- newly exposed unsupported categories;
- generated subset size delta, when candidate selection can safely expand;
- validation status for any expanded generated subset.

A pass counts as convergent only if at least one of these is true:

- translated formula count increases;
- a high-count unsupported category is eliminated or materially reduced;
- a generic diagnostic is replaced by a sharper diagnostic that enables a specific next implementation decision;
- generated subset size increases and validates;
- a remaining blocker is explicitly classified as deferred structural work with a reason.

A pass is non-convergent if it only moves failures between generic categories, adds support without improving private diagnostics, or expands generated code without validation evidence.

P17.3 should prioritize work in this order:

1. Low-risk parser/expression unblockers: boolean literals, unary minus, `^`, and `&`.
2. Scalar functions: `AND`, `OR`, `IFERROR`, `MIN`, `SUM`, `AVERAGE`, `CONCATENATE`.
3. Criteria/range functions: `SUMIF`, `SUMIFS`, `COUNTIFS`.
4. Error-reference diagnostics: `#REF!`.
5. `OFFSET`: implement only if a constrained, provenance-safe subset is clear; otherwise emit a sharper unsupported diagnostic.

This order is designed to expose downstream blockers quickly while avoiding premature table, external workbook, or volatile/reference-returning semantics.

P17.4 closeout should not merely summarize work. It should decide one of these outcomes:

- converged for the current target import scope: selected formulas translate and generated outputs validate;
- partially converged: remaining blockers are enumerated, lower in count, and assigned to concrete later phases;
- not converged: progress metrics failed to improve, requiring a scope or architecture decision before more implementation.

## Full Private Sample Import Scope

To fully import the current private sample workbook, P17 needs more than adding scalar Excel functions. The intended P17 scope is:

- represent structured references distinctly and keep them blocked unless table semantics are modeled;
- support the listed functions where their inputs can be represented by existing scalar/range expression records;
- support the listed operators and boolean literals;
- add explicit diagnostics for `#REF!`, unsupported structured/table semantics, unresolved named ranges, external references, volatile/reference-returning behavior, and missing cached values;
- keep generation blocked for formulas whose dependencies or semantics remain unsupported;
- rerun sanitized private diagnostics after each expansion slice to discover second-order blockers;
- compare each rerun against the previous diagnostic pass so progress and newly exposed blockers are explicit.

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

P17.3 should end with a rerun of the sanitized private-workbook diagnostic pass. Its closeout should record:

- translated formula count before and after the slice;
- remaining first-failure diagnostic counts;
- newly exposed blocker categories;
- whether the generated subset can grow;
- whether cached-value validation, `formulas`, Excel-backed validation, or hybrid validation is available for the expanded subset.
