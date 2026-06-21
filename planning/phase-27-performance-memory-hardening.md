# Phase 27 Performance And Memory Hardening

## Purpose

Phase 27 will make full-workbook generated-model validation practical after Phase 26 establishes the
current correctness boundary for the 2020 FABLE benchmark.

The immediate evidence is that cached extraction and contract inference can now be skipped, but the
generated model still takes substantial time and memory to import, execute, and compare. That cost
needs to be measured before changing architecture.

## Working Hypotheses

These are hypotheses to test, not conclusions:

- Formula cells should not be recomputed repeatedly once `_get(cell_ref)` caches a value.
- Range-heavy formulas may still rebuild and rescan large Python lists many times, especially
  `SUMIF`, `SUMIFS`, `COUNTIF`, and `COUNTIFS`.
- Criteria functions may evaluate and allocate more source range data than needed for excluded rows.
- Importing one very large generated module may create significant parser, bytecode, function-object,
  and symbol-table overhead before `calculate()` starts.
- Pipeline JSON caches may trade CPU time for high memory use because workbook, graph, expression,
  inference, generated-output, and oracle-output records are all materialized as Python objects.
- A small `.xlsx` file can expand to much larger runtime memory because zipped XML, parsed workbook
  records, dependency edges, expression trees, generated Python source, compiled code objects, output
  dictionaries, and validation records are all separate in-memory representations.

## Measurement Plan

Phase 27 should measure before optimizing:

- wall time by pipeline stage;
- generated module import time;
- formula execution time by generated cell or by sheet/block;
- helper time and call counts for `_get`, `_range`, `_table`, criteria functions, lookups, and
  arithmetic/coercion helpers;
- repeated range/table materialization counts;
- peak memory around cache load, generation, import, execution, and comparison.

Raw profiler outputs should stay under ignored `tmp/`. Sanitized conclusions belong in this note or a
successor planning note.

## Baseline Profile: 2026-06-21

Ignored raw artifacts:

- `tmp/p27_profile_generated_model.py`
- `tmp/logs/p27-profile-import-only.log`
- `tmp/logs/p27-profile-full-execution.log`
- `tmp/p27-profile/generated-model-profile.json`
- `tmp/p27-profile/generated_fable_2020_model_profiled.py`

Scope:

- reused the Phase 26 generated source artifact:
  `tmp/p26-fable-full-validation/generated_fable_2020_model.py`;
- did not regenerate extraction, graph, expressions, inference, or source code;
- instrumented a temporary copy of the generated source under ignored `tmp/`;
- measured import-only behavior and full `calculate()` behavior over the 2020 FABLE comparable-output
  universe.

Headline measurements:

- generated source size: 198,767,455 bytes;
- import-only elapsed time: 36.079 seconds in the first run and 34.892 seconds in the full profile;
- maximum RSS after import: about 11,222,896 KiB, or roughly 10.7 GiB;
- full profiled `calculate()` elapsed time: 1,502.321 seconds;
- outputs returned: 281,741;
- formula evaluations: 286,505;
- `_get` calls: 251,517,729;
- `_get` constant hits: 188,153,993;
- `_get` cache hits: 63,077,231;
- `_range` calls: 605,817;
- `_range` addressed cells: 364,236,641;
- `_table` calls: 38,336;
- `_table` addressed cells: 4,141,335.

Helper timing caveat:

- helper timings are cumulative and nested because wrappers time helpers that call other wrapped
  helpers; therefore helper seconds should not be summed or compared directly to wall time;
- call counts and relative ranking are still useful for identifying where runtime work concentrates.

Top helper signals:

- `_sf_sumifs`: 199,343 calls;
- `_sf_value`: 251,715,601 calls;
- `_sf_sum_value`: 356,219 calls;
- `_sf_iferror`: 20,976 calls;
- `_sf_matches_criteria`: 121,247,129 calls;
- `_sf_compare_criteria`: 121,296,032 calls;
- `_sf_criteria_equal`: 121,292,302 calls;
- `_sf_numeric_value`: 242,584,604 calls;
- `_sf_coerce_criteria`: 111,343,168 calls.

Initial conclusion:

- the first optimization target should be repeated range and criteria work, not parallel execution;
- P27.2 should focus on reducing repeated `_range` materialization and `SUMIFS` criteria scans while
  preserving lazy evaluation and runtime circular-dependency behavior;
- import/source size remains a major problem at roughly 35 seconds and 10.7 GiB before calculation,
  but generated execution spends about 25 minutes in the current source backend, so P27.2 comes before
  P27.3 unless new evidence contradicts this baseline;
- `_get` appears to cache formula results as intended, but range and criteria helpers still repeatedly
  ask for very large numbers of constants and cached formula values.

## P27.2 Range And Criteria Optimization Evidence

Implemented changes:

- generated `_range(...)` calls now return cached `_SfRangeView` objects keyed by sheet and bounds;
- `_SfRangeView` materializes eager values or lazy callable values only when needed, and caches those
  materializations after reuse rather than permanently storing every unique range on first touch;
- `SUMIF`, `SUMIFS`, `COUNTIF`, and `COUNTIFS` now build criteria matcher callables once per criteria
  argument instead of reparsing operator/wildcard criteria for every row;
- generated `_sf_numeric_value` now uses a bounded `lru_cache` to reduce repeated numeric coercion of
  common criteria values.

Focused tests:

- `tests/test_python_generation.py::test_generate_python_module_renders_criteria_functions`
- `tests/test_python_generation.py::test_generate_python_module_skips_excluded_sumifs_sum_cells`
- `tests/test_python_generation.py::test_generate_python_module_reuses_range_views_without_changing_results`

Ignored raw artifacts:

- `tmp/logs/p27-range-cache-focused-tests.log`
- `tmp/logs/p27-range-cache-regenerate-model.log`
- `tmp/logs/p27-range-cache-profile-full-execution.log`
- `tmp/logs/p27-criteria-matcher-focused-tests.log`
- `tmp/logs/p27-criteria-matcher-regenerate-model.log`
- `tmp/logs/p27-criteria-matcher-profile-full-execution.log`
- `tmp/logs/p27-optimized-full-validation.log`

Measured performance:

- P26 proof-run generated execution baseline: 1,469.944 seconds;
- P27.1 profiled generated execution baseline: 1,502.321 seconds;
- range-view profiled generated execution: 696.610 seconds;
- range-view plus criteria-matcher profiled generated execution: 379.177 seconds;
- optimized uninstrumented full-validation generated execution: 183.463 seconds;
- optimized full-validation total elapsed time with cache loading, generation, execution, and
  comparison: 424.417 seconds.

Correctness evidence:

- full cached 2020 FABLE validation still passed;
- comparable outputs: 281,741;
- matches: 281,741;
- mismatches: 0.

Remaining measured bottleneck:

- generated source import remains roughly 35 seconds and about 10.7 GiB maximum RSS before
  calculation;
- generated source size remains about 198.8 MB;
- P27.3 should therefore address generated module size and import overhead next.

## P27.3 Compact Provenance Evidence

Implemented change:

- inferred generated-module contracts now disable inline formula provenance comments by default once
  the reachable formula count exceeds 50,000 cells;
- small/debug models still keep inline comments by default;
- callers can force comments with `inline_provenance_comment_limit=None`;
- raw formula provenance remains on each `GeneratedSymbol`, so the information is not discarded from
  the contract layer.

Why this was the first size slice:

- the P26/P27 FABLE generated source had 289,951 provenance comment lines;
- those comments accounted for about 66,471,192 bytes of source;
- removing them is low risk because generated runtime behavior never reads comments.

Measured source-size breakdown before the change:

- total generated source: 198,769,198 bytes and 945,428 lines;
- preamble/runtime helper source: about 10,027 bytes and 319 lines;
- constants source: 3,502,940 bytes and 83,462 lines;
- formula source: 178,211,932 bytes and 579,904 lines, including provenance comments;
- output dictionary source: 17,044,299 bytes and 281,743 lines.

Measured compact-provenance result:

- compact generated source: 132,298,006 bytes;
- source-size reduction: about 66.5 MB;
- import-only elapsed time: 34.328 seconds;
- maximum RSS after import: 11,096,124 KiB, or about 10.6 GiB;
- compact-source generated execution: 169.982 seconds;
- compact-source cached compare loop elapsed time, including cache loads and comparison:
  380.879 seconds.

Correctness evidence:

- compact-source 2020 FABLE validation still passed;
- comparable outputs: 281,741;
- matches: 281,741;
- mismatches: 0.

Conclusion:

- inline provenance comments were a real source-size problem and should stay disabled for large
  generated modules;
- comment removal alone does not materially solve import time or memory use;
- constants are only about 3.5 MB of the generated source, so extracting constants from Python source
  would not be the next highest-leverage source-size fix by itself;
- the remaining P27.3 work should focus on formula and output source layout, code-object count, module
  chunking, or the planned compact runtime IR backend rather than spending more effort on comments.

## P27.3 Compact Output Map Evidence

Implemented change:

- generated modules now build their public output dictionary from a single `_output_refs` tuple and a
  dict comprehension;
- this replaces the previous generated return literal that repeated each output cell reference twice;
- public behavior remains `calculate(inputs=None) -> dict[str, value]`;
- Python dict insertion order preserves the selected output order from `_output_refs`.

Measured compact-provenance plus compact-output-map result:

- generated source: 124,057,682 bytes;
- generation elapsed time from cached inference: 9.009 seconds;
- import-only elapsed time: 34.093 seconds;
- maximum RSS after import: 10,658,776 KiB, or about 10.2 GiB;
- generated execution: 169.040 seconds;
- cached compare loop elapsed time, including cache loads, generation, execution, and comparison:
  390.196 seconds.

Correctness evidence:

- compact-output-map 2020 FABLE validation still passed;
- comparable outputs: 281,741;
- matches: 281,741;
- mismatches: 0.

Conclusion:

- output-map compaction removed another roughly 8.2 MB beyond compact provenance;
- the combined P27.3 source-size reduction is about 74.7 MB, from 198.8 MB to 124.1 MB;
- import time and memory still remain near the previous baseline, so source text bytes alone are not
  the dominant import/RSS driver;
- the remaining P27.3 target is the formula function/lambda structure and generated code-object
  volume, which probably requires chunking, indexed runtime data, or a compact runtime IR backend.

## P27.3 Expression-Source Formula Storage Evidence

Implemented change:

- generated-module contracts now include `formula_storage`, with `lambdas` retained for small/debug
  models and `expression_source` selected by inferred large contracts;
- expression-source generated modules store rendered formula expressions as strings rather than as
  one lambda function per formula cell;
- formula expressions are compiled and evaluated lazily when `_get(cell_ref)` reaches the cell;
- compiled expression code is not retained because `_get()` already caches computed formula values;
- the public generated API remains `calculate(inputs=None) -> dict[str, value]`.

Cold import comparison against compact-lambda source:

- compact lambda source: 124,057,782 bytes;
- compact lambda cold import: 34.370 seconds;
- compact lambda RSS after cold import: 10,518,600 KiB;
- expression-source source: 122,318,322 bytes;
- expression-source cold import: 4.898 seconds;
- expression-source RSS after cold import: 1,381,648 KiB.

Generated-model-only execution profile:

- direct expression-source import plus `calculate()` elapsed time: 151.616 seconds;
- direct expression-source `calculate()` elapsed time after import: 146.717 seconds;
- outputs returned: 281,741;
- RSS after direct generated-model execution: 1,380,728 KiB.

Correctness evidence:

- full cached 2020 FABLE comparison with expression-source storage still passed;
- comparable outputs: 281,741;
- matches: 281,741;
- mismatches: 0;
- full cached compare process RSS reached 13,100,240 KiB, but that process also held workbook,
  graph, expression, inference, generated-output, and oracle comparison structures in memory.

Conclusion:

- the import/RSS bottleneck was primarily generated lambda/code-object pressure, not raw source text
  length alone;
- expression-source storage is a practical bridge for large source-backend models;
- pipeline/cache memory is now clearly separate from generated-model import memory and belongs in
  P27.4;
- direct generated-model RSS is still much larger than the original workbook, but it is no longer in
  the 10 GiB import range.

## Formula Template And Vectorization Direction

The next architectural improvement should stop representing every cell formula as a unique formula
body when spreadsheet structure proves otherwise.

Likely path:

- normalize formulas into relative-reference templates, similar in spirit to R1C1 form;
- group contiguous ranges, table columns, and rectangular regions that share the same template;
- measure how much of the 2020 FABLE formula universe collapses into repeated templates;
- compile one kernel per template and apply it over indexed cells, table columns, or rectangular
  regions;
- evaluate whether those kernels should run over plain Python arrays first, then NumPy, pandas, or
  another array/table representation only if measurements justify the dependency.

This is distinct from expression-source storage:

- expression-source storage reduces Python import/code-object pressure while preserving the current
  cell-by-cell lazy evaluator;
- template/vectorized evaluation changes the intermediate representation and execution model;
- template/vectorized work should be planned as a follow-on architecture slice after P27 records the
  current performance boundary.

## P27.4 Memory Stage Profile: First Pass

Ignored raw artifacts:

- `tmp/p27_memory_stage_profile.py`
- `tmp/logs/p27-memory-stage-profile.log`
- `tmp/p27-profile/memory-stage-profile.json`

Scope:

- loaded the cached 2020 FABLE workbook, graph, expressions, and inference artifacts in one process;
- measured current RSS from `/proc/self/status`;
- measured peak RSS from `resource.getrusage`;
- generated and executed the expression-source source backend;
- built oracle values and comparison reports in the same process.

Stage measurements:

- start: 35,192 KiB current RSS;
- workbook JSON loaded: 1,908,292 KiB current RSS and 2,567,828 KiB peak RSS;
- workbook record hydrated: 2,309,580 KiB current RSS;
- graph JSON loaded: 8,462,292 KiB current RSS and 10,776,312 KiB peak RSS;
- graph record hydrated: 10,182,548 KiB current RSS for 3,543,800 edges;
- graph JSON deleted: 10,154,872 KiB current RSS;
- expressions JSON loaded: 10,177,380 KiB current RSS and 11,612,668 KiB peak RSS;
- expressions hydrated: 10,184,888 KiB current RSS for 296,976 expressions;
- output universe built: 10,193,080 KiB current RSS for 281,741 comparable outputs;
- inference JSON loaded: 11,114,632 KiB current RSS;
- inference hydrated: 11,850,248 KiB current RSS for 373,410 symbols, 289,951 expressions, and
  83,459 constants;
- inference JSON deleted: 11,850,264 KiB current RSS;
- generation done: 12,025,068 KiB current RSS and 12,139,032 KiB peak RSS;
- generation result deleted: 11,905,616 KiB current RSS;
- generated execution done: 12,670,648 KiB current RSS and 12,981,284 KiB peak RSS;
- oracle values built: 12,670,648 KiB current RSS;
- comparison done: 12,670,648 KiB current RSS with 281,741 matches and 0 mismatches;
- validation outputs deleted: 12,435,240 KiB current RSS.

Conclusions:

- the graph cache/object model is the largest confirmed resident memory source;
- the full dependency graph has 3,543,800 Python edge records, and hydrating it keeps the process near
  10 GiB even after raw graph JSON is deleted;
- inference loading adds a second large expression/symbol/constant representation and pushes current
  RSS to about 11.85 GiB;
- generation, generated execution, oracle-value construction, and comparison are not the dominant
  remaining memory costs in the full-process validation path;
- Python does not return most allocated memory to the OS after validation objects are deleted, so
  long-lived all-in-one debug processes exaggerate steady RSS after high-water stages.

Next P27.4 target:

- avoid keeping the full graph and inference/expression duplicates resident during generated-model
  execution and validation;
- evaluate a validation path that loads only the inference artifact plus cached workbook scalar values,
  or serializes generated execution and comparison into separate short-lived processes;
- evaluate compact graph/inference stores before hydrating millions of edges into Python objects.

## P27.4 Slim Oracle Validation Prototype

Ignored raw artifacts:

- `tmp/p27_slim_validation_profile.py`
- `tmp/logs/p27-slim-oracle-build.log`
- `tmp/logs/p27-slim-validation-profile.log`
- `tmp/p27-profile/slim-fable-2020-oracle.json`
- `tmp/p27-profile/slim-oracle-build-profile.json`
- `tmp/p27-profile/slim-validation-profile.json`

Prototype shape:

- build a compact ignored oracle file containing only comparable output refs, output kinds, and cached
  workbook values;
- run generated-model import, generated-model calculation, and scalar comparison in a fresh process
  using only the generated model and slim oracle file;
- avoid workbook, graph, expression, and inference hydration in the recurring validation process.

One-time slim oracle build:

- inference contract output refs loaded: 281,741 refs;
- workbook record hydrated: 395,482 cells;
- slim oracle file size: 23,660,000 bytes;
- current RSS at completion after cleanup: 227,820 KiB;
- peak RSS during build: 3,596,580 KiB.

Recurring slim validation run:

- slim oracle loaded: 281,741 outputs and 281,741 oracle values;
- current RSS after slim oracle load: 191,724 KiB;
- generated model import elapsed time: 4.868 seconds;
- current RSS after generated model import: 1,179,464 KiB;
- generated execution elapsed time: 144.778 seconds;
- current RSS after generated execution: 1,178,988 KiB;
- comparison elapsed time: 1.446 seconds;
- comparison result: 281,741 matches and 0 mismatches;
- current RSS after comparison: 1,301,192 KiB;
- peak RSS for the slim validation process: 1,564,740 KiB;
- current RSS at process end: 1,048,104 KiB.

Conclusion:

- the recurring validation path does not need to hydrate workbook records, graph records, translated
  expressions, or inference records once the generated model and slim oracle exist;
- selective loading via a compact oracle artifact reduces the full validation process from roughly
  12.98 GiB peak RSS to roughly 1.56 GiB peak RSS for the same 281,741-output comparison;
- durable validation tooling should promote this idea into a first-class generated-output oracle or
  benchmark-output artifact rather than relying on ad hoc full-pipeline debug scripts.

## Optimization Directions

Prefer targeted changes supported by measurements:

- cache immutable range/table views where inputs and constants make reuse safe;
- stream or index criteria-function ranges instead of building fresh nested lists for every call;
- pre-index common lookup/criteria columns if the generated workbook repeatedly queries the same table;
- split very large generated modules or move formula definitions into compact data structures if import
  time or code-object memory dominates;
- replace large JSON cache reloads with a local structured store if object materialization dominates;
- compare outputs incrementally if keeping all generated outputs and oracle outputs resident is wasteful.

## Parallelization Directions

The benchmark host may have many cores and enough memory to support parallel experiments. Phase 27
should test that directly rather than assuming a single-process pipeline is acceptable.

Likely good candidates:

- contract inference partitioned by selected output refs or dependency-closure shards, with a
  deterministic merge step for symbols, constants, expressions, selected outputs, and diagnostics;
- formula translation partitioned by formula cell, because each translation is mostly independent once
  extraction and graph metadata are available;
- generated-source rendering partitioned into module chunks or formula-definition blocks;
- validation comparison partitioned by output refs after generated values and oracle values exist.

Harder candidates:

- generated formula execution inside one workbook model, because `_get(cell_ref)` uses shared caches,
  active evaluation stacks, and lazy dependency discovery;
- criteria/range-heavy formulas that share large table scans, because naive multiprocessing may duplicate
  memory and serialization work rather than reducing runtime;
- runtime circular-dependency detection across worker boundaries.

Parallel execution experiments should record:

- worker count;
- wall time versus CPU time;
- peak resident memory;
- serialization and process-startup overhead;
- deterministic output ordering;
- correctness comparison against the serial result.

The first parallel target should be contract inference. It was already observed as an expensive stage,
and its output can be cached and compared deterministically. Generated execution should be profiled
before parallelizing; if it is dominated by repeated range scans, indexing or memoization may beat
process-level parallelism.

## Guardrails

- Do not use cached workbook values to mask generated-model calculation errors.
- Do not sacrifice lazy branch semantics or runtime cycle detection.
- Keep verbose logging and tailable logs for all long benchmark runs.
- Treat performance regressions and correctness regressions separately in reports.
- Phase 27 should not close unless it states what was measured, what changed, what improved, and what
  remains expensive.
