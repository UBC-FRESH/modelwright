# Generated-Code Prototype Contract

Date: 2026-06-19

## Purpose

This note defines the first Modelwright generated-code experiment for Phase 3.

The experiment should prove whether the prototype IR can drive readable Python generation for the controlled synthetic workbook. It is not a public API, package layout, CLI, or durable source tree.

## Inputs

The ignored code-generation experiment should consume:

- `tmp/prototype_ir_output.json`: prototype IR emitted during Phase 2;
- `planning/workbook-ir-contract.md`: IR field contract;
- `planning/phase-2-closeout-phase-3-inputs.md`: supported subset and blocking diagnostics.

The generator should fail clearly if `tmp/prototype_ir_output.json` is missing or stale enough that required fields are absent.

## Outputs

The experiment should write ignored generated files under `tmp/`, for example:

- `tmp/generated_model.py`: generated Python model for the synthetic workbook;
- `tmp/prototype_codegen_output.json`: optional generation summary and diagnostics.

No generated Python should be committed in Phase 3 unless the maintainer explicitly asks for a tracked fixture or example.

## Generated Module Shape

The generated module should be simple and inspectable:

- a module docstring naming the source workbook and warning that the file is generated;
- constants for literal input cells that are needed by formulas;
- one function per formula cell, using stable Python names derived from cell references;
- a final `calculate()` function that returns the workbook outputs needed for verification.

For the synthetic workbook, the minimum generated functions are:

```text
calc_b2()
calc_b3()
calc_b4()
summary_b2()
summary_b3()
calculate()
```

The prototype may inline literal cell values as constants rather than creating functions for every value cell.

## Naming And Provenance

Generated Python names should be deterministic:

- lowercase sheet names;
- lowercase cell coordinates;
- non-alphanumeric characters converted to underscores;
- cell references represented as `sheet_cell`, such as `summary_b2`.

Every generated formula function should include a short provenance comment:

```python
# Source: Summary!B2 = Calc!B4
```

Named ranges should be preserved in comments when they were part of the source formula:

```python
# Source: Calc!B2 = BaseVolume*(1+GrowthRate)
# Resolved: BaseVolume -> Inputs!B2, GrowthRate -> Inputs!B3
```

## Dependency Ordering

The generator should use only `execution` dependency edges for calculation order.

Rules:

- formula functions should be emitted in topological order when possible;
- semantic edges are for comments, traceability, and diagnostics only;
- duplicate semantic/execution meaning should not create duplicate calculations;
- unresolved, external, circular, or unsupported dependency edges should block generation.

## Supported Formula Subset

The first experiment should support only the formulas present in `tmp/synthetic_model.xlsx`:

- arithmetic with `+`, `*`, and parentheses;
- same-sheet scalar references;
- cross-sheet scalar references;
- workbook-level named ranges already resolved by IR;
- `ROUND(value, digits)`;
- `IF(condition, true_value, false_value)`;
- `>` comparisons;
- numeric and string literals.

The generated Python should rely only on the Python standard library.

## Diagnostics

Generation should stop on:

- missing required IR fields;
- unresolved references;
- external workbook links;
- circular execution dependencies;
- unsupported functions;
- unsupported operators;
- multi-cell ranges used where a scalar is required.

Generation may continue with warnings for:

- missing cached formula values;
- semantic named-range edges that also have resolved execution edges;
- unused value cells.

Warnings should be recorded in the optional generation summary if that summary is emitted.

## Acceptance Criteria

P3.2 should be considered successful when the ignored generated model:

- is created under `tmp/`;
- is readable enough to inspect manually;
- runs with `python`;
- computes `Summary!B2` as `70.2`;
- computes `Summary!B3` as `"ok"`;
- keeps all generated files ignored;
- requires no package layout, CLI, dependency manager, test framework, or CI setup.

## Non-Goals

- No tracked package source tree.
- No public API.
- No command-line interface.
- No broad Excel formula parser.
- No support for formulas outside the first synthetic workbook subset.
- No committed generated model output.
