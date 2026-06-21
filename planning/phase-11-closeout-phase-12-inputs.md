# Phase 11 Closeout And Phase 12 Inputs

Date: 2026-06-20

## Purpose

This note closes the Phase 11 generated Python model core and defines inputs for Phase 12 oracle-backed validation.

Phase 11 added generated module contracts and a first standalone Python generator for the controlled synthetic workbook. It did not add oracle execution, CLI commands, package-level generated artifact storage, or a generalized optimizer for generated code.

## Generated Model Core Now Supports

Tracked package code now supports:

- `GeneratedModuleContract` records for generated module shape, entrypoint, inputs, outputs, symbols, and provenance-comment policy;
- `GeneratedSymbol` records tying generated Python symbols back to workbook cell references and raw formulas;
- `GenerationResult` records with generated source, diagnostics, and generated status;
- stable Python symbol naming from canonical workbook cell references;
- `generate_python_module(...)` for producing standalone Python source;
- optional writing to caller-provided output paths;
- provenance comments for generated workbook cells and raw formulas;
- generated `calculate(inputs=None)` functions returning `{cell_ref: value}` output mappings;
- caller input overrides while preserving generated defaults from workbook constants.

The generated synthetic model tests confirm:

- generated files are written only to pytest temporary directories;
- generated source has no runtime dependency on Excel, source workbooks, `openpyxl`, or Modelwright;
- generated `calculate()` returns `Summary!B2 == 70.2` and `Summary!B3 == "ok"` for the baseline;
- generated `calculate({"Inputs!B2": 10})` returns a changed output and status from the same standalone module;
- no generated Python model artifact is tracked in Git.

## Still Deferred

The generated model core does not yet:

- infer output cells automatically;
- infer input cells automatically;
- compute a topological order beyond caller-provided symbol ordering;
- package generated modules;
- optimize repeated expressions;
- generate multiple modules;
- generate type annotations for model inputs and outputs;
- expose a CLI for generation;
- compare generated outputs against source workbook oracle outputs.

These behaviors belong in oracle-backed validation, API/CLI stabilization, and later hardening phases.

## Phase 12 Oracle-Backed Validation Inputs

Phase 12 should consume:

- the synthetic workbook fixture builder;
- generated standalone Python module output from Phase 11;
- existing validation scenarios and expected output records;
- optional oracle dependencies, starting with a pure-Python `formulas` backend;
- `build_validation_report` for comparing generated and oracle output mappings.

Phase 12 should add:

- an oracle interface boundary;
- an optional dependency boundary for `formulas`;
- a `formulas`-backed oracle for the controlled synthetic workbook;
- tests that compare generated standalone model outputs against oracle-calculated workbook outputs;
- explicit handling for unavailable optional oracle dependencies.

## Suggested Phase 12 Acceptance Checks

For the synthetic workbook, Phase 12 should:

- build the source workbook in a temporary directory;
- generate and execute the standalone Python model in a temporary directory;
- evaluate the same workbook outputs through the oracle backend;
- compare outputs with the existing validation report builder;
- confirm the baseline validation report passes.

Oracle-backed validation should remain optional and should not require Excel in the default path.
