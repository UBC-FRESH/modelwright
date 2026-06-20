# Sheetforge

`sheetforge` is an early-stage project for turning spreadsheet workbooks into transparent, version-controlled, standalone Python models.

The intended direction is a generic workflow that can inspect workbook structure, extract formulas and dependencies, generate maintainable Python source, and validate the generated model against the original workbook outputs.

This repository is currently an early implementation skeleton. It defines minimal Python package and test scaffolding plus initial validation, extraction, graph, generation, oracle records, and thin JSON command-line wrappers, but does not yet provide a release stability guarantee, catalog schema, or full workbook conversion.

## Current Focus

- Build the first package-backed validation/report, workbook extraction, generation, and CLI cores.
- Keep extraction, code generation, validation, diagnostics, and reporting responsibilities separate.
- Avoid committing private notes, source workbooks, generated clones, or large artifacts while the project shape is still being established.

## Python API Boundary

The durable API is organized by module responsibility:

- `sheetforge.extraction`: workbook extraction records and `extract_workbook`.
- `sheetforge.graph`: dependency graph records and `build_dependency_graph`.
- `sheetforge.formulas`: formula expression records, translation helpers, and reference-index helpers.
- `sheetforge.generation`: generated-module records and `generate_python_module`.
- `sheetforge.validation`: validation scenarios, scalar comparisons, and report records.
- `sheetforge.oracles`, `sheetforge.formulas_oracle`, and `sheetforge.oracle_validation`: oracle request/result records, optional `formulas` oracle execution, and oracle-backed report assembly.

The package root `sheetforge` exposes a curated convenience facade for those records and functions. Module-level imports remain preferred for implementation work because this project is still pre-release.

## Command-Line Interface

Install the package locally before using the console script:

```bash
python -m pip install -e ".[test]"
```

The current CLI prints JSON to stdout and stays close to the Python APIs:

```bash
sheetforge workbook extract path/to/workbook.xlsx > tmp/extraction.json
sheetforge workbook graph path/to/workbook.xlsx > tmp/dependency-graph.json
sheetforge model generate --contract tmp/contract.json --expressions tmp/expressions.json --constants tmp/constants.json --out tmp/generated_model.py > tmp/generation-result.json
sheetforge validation report --scenario tests/fixtures/synthetic_model/baseline_scenario.json --generated-values tmp/generated-values.json --oracle-values tmp/oracle-values.json > tmp/validation-report.json
```

The earlier top-level commands `extract`, `graph`, `generate`, and `validate-report` remain available as JSON automation aliases. These commands do not provide a one-step workbook converter. `model generate` expects explicit generated-module and formula-expression JSON inputs, and `validation report` compares already-observed generated/oracle values. See `planning/cli-json-workflows.md` for JSON examples and workflow boundaries.

## Local Development

Install the package with test dependencies:

```bash
python -m pip install -e ".[test]"
```

Install the lightweight quality-check extra when working on code changes:

```bash
python -m pip install -e ".[quality]"
```

Run lint checks:

```bash
python -m ruff check .
```

Run tests:

```bash
python -m pytest
```

`sheetforge` is pre-release. The package metadata is sufficient for local editable installs and CI, but publishing metadata, release artifacts, and compatibility guarantees are intentionally deferred until the conversion workflow is more proven.

## Repository Conventions

- `AGENTS.md` is the working contract for AI coding agents.
- `ROADMAP.md` is the current plan and next-step tracker.
- `CHANGE_LOG.md` is the append-only project narrative.
- `planning/` contains focused design notes and research records that are too detailed for the roadmap.
- `src/sheetforge/` contains the importable Python package.
- `tests/` contains package-backed tests and tracked synthetic fixture helpers.
- `tmp/` is ignored local working space for private notes, source workbooks, experiments, and generated scratch outputs.
