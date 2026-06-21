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
