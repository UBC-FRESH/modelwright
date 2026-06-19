# ROADMAP.md

This roadmap is the current project plan and next-step tracker for `sheetforge`.

The repository is intentionally lightweight at this stage. Do not add a package layout, dependency manager, test framework, CLI, or CI contract until research and prototypes provide enough evidence for those choices.

## Current Next Steps

- Review `planning/first-prototype-findings.md` and define the minimum tracked intermediate representation for workbook references, formulas, named ranges, and dependencies.
- Decide whether named ranges should remain first-class dependency nodes or normalize immediately to destination cells.
- Use the synthetic prototype findings to plan the first generated-code experiment without adding durable package structure yet.

## Phase 0: Bootstrap Repo Contract

Goal: establish the project skeleton and working conventions.

Tasks:

- Add the project overview, agent contract, roadmap, changelog, planning folder, and ignore rules.
- Keep private bootstrap notes and source workbooks out of tracked files.
- Avoid choosing a Python stack before the first research phase.

Status: complete.

## Phase 1: Research Spreadsheet Tooling

Goal: evaluate existing libraries and decide what they can safely provide.

Topics:

- `openpyxl` for workbook structure, formulas, worksheets, names, and metadata.
- `formulas` and `pycel` for parsing, dependency graphs, and Python evaluation.
- `xlwings` as a possible extraction or validation bridge to Excel, not as a runtime dependency for generated models.
- `networkx` or similar graph tooling for dependency analysis.
- Jinja or standard-library templating options for generated source once generation is justified.

Deliverable: planning notes that record candidate libraries, capabilities, limitations, risks, and first prototype findings.

Status: active.

## Phase 2: Define Workbook Extraction Contracts

Goal: define the minimum intermediate representation needed for workbook conversion.

Expected focus:

- Workbook, worksheet, cell, formula, named range, dependency, input, output, and validation-example concepts.
- Handling of cross-sheet references, external links, hidden sheets, circular references, volatile functions, array formulas, and unsupported Excel functions.
- Provenance fields that trace generated behavior back to source workbook locations.

Status: planned.

## Phase 3: Prototype Python Code Generation

Goal: generate readable Python from extracted workbook logic for a small controlled workbook.

Expected focus:

- Generated module structure.
- Naming and symbol mapping rules.
- Formula translation strategy.
- Separation between generated code and hand-written support code.
- Reviewability and reproducibility of generated output.

Status: planned.

## Phase 4: Regression Validation Against Workbooks

Goal: prove generated Python behavior matches source workbook outputs for representative scenarios.

Expected focus:

- Input scenario definition.
- Workbook recalculation or oracle strategy.
- Numeric tolerance and comparison rules.
- Reporting mismatches with source-cell provenance.

Status: planned.

## Phase 5: Package, API, CLI, And CI Decisions

Goal: introduce durable project tooling only after prototypes clarify the required shape.

Expected focus:

- Python package layout.
- Public API boundaries.
- CLI commands.
- Dependency manager.
- Test framework and fixtures.
- CI checks.
- Documentation structure.

Status: planned.
