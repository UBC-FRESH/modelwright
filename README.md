# Modelwright

`modelwright` is an early-stage project for turning spreadsheet workbooks into transparent, version-controlled, standalone Python models.

The intended direction is a generic workflow that can inspect workbook structure, extract formulas and dependencies, generate maintainable Python source, and validate the generated model against the original workbook outputs.

This repository is currently an early implementation skeleton. It defines minimal Python package and test scaffolding plus initial validation, extraction, graph, generation, oracle records, and thin JSON command-line wrappers, but does not yet provide a release stability guarantee, catalog schema, or full workbook conversion.

## Current Focus

- Build the first package-backed validation/report, workbook extraction, generation, and CLI cores.
- Keep extraction, code generation, validation, diagnostics, and reporting responsibilities separate.
- Avoid committing private notes, source workbooks, generated clones, or large artifacts while the project shape is still being established.

## Python API Boundary

The durable API is organized by module responsibility:

- `modelwright.extraction`: workbook extraction records and `extract_workbook`.
- `modelwright.graph`: dependency graph records and `build_dependency_graph`.
- `modelwright.formulas`: formula expression records, translation helpers, and reference-index helpers.
- `modelwright.generation`: generated-module records and `generate_python_module`.
- `modelwright.validation`: validation scenarios, scalar comparisons, and report records.
- `modelwright.oracles`, `modelwright.formulas_oracle`, and `modelwright.oracle_validation`: oracle request/result records, optional `formulas` oracle execution, and oracle-backed report assembly.

The package root `modelwright` exposes a curated convenience facade for those records and functions. Module-level imports remain preferred for implementation work because this project is still pre-release.

## Command-Line Interface

Bootstrap the repo-local virtual environment before using the console script:

```bash
scripts/bootstrap_dev_env.sh
```

The current CLI prints JSON to stdout and stays close to the Python APIs:

```bash
modelwright workbook extract path/to/workbook.xlsx > tmp/extraction.json
modelwright workbook graph path/to/workbook.xlsx > tmp/dependency-graph.json
modelwright conversion plan path/to/workbook.xlsx > tmp/conversion-plan.json
modelwright model generate --contract tmp/contract.json --expressions tmp/expressions.json --constants tmp/constants.json --out tmp/generated_model.py > tmp/generation-result.json
modelwright validation report --scenario tests/fixtures/synthetic_model/baseline_scenario.json --generated-values tmp/generated-values.json --oracle-values tmp/oracle-values.json > tmp/validation-report.json
```

These commands do not provide a one-step workbook converter. `conversion plan` reports extraction, graphing, formula-translation, and residual-blocker status; `model generate` expects explicit generated-module and formula-expression JSON inputs; and `validation report` compares already-observed generated/oracle values. See `planning/cli-json-workflows.md` for JSON examples and workflow boundaries.

## Local Development

Bootstrap a repo-local virtual environment:

```bash
scripts/bootstrap_dev_env.sh
```

This installs Modelwright with the `dev` extra:

```bash
.venv/bin/python -m pip install -e '.[dev]'
```

Run lint checks:

```bash
.venv/bin/python -m ruff check .
```

Run tests:

```bash
.venv/bin/python -m pytest
```

Build docs locally:

```bash
.venv/bin/sphinx-build -b html docs _build/html -W
.venv/bin/python scripts/verify_docs_theme.py _build/html
```

Restore the public external FABLE benchmark workbooks into ignored local paths:

```bash
scripts/bootstrap_dev_env.sh --benchmarks
```

`modelwright` is pre-release. The current alpha line is `0.1.0a8`; alpha releases must not be described as full-workbook conversion guarantees.

Check release artifacts locally:

```bash
scripts/check_release_artifacts.sh
```

Release checks write build outputs under ignored `tmp/release-checks/`.

See `docs/guides/release-deployment.rst` for the release and deployment runbook.

## Repository Conventions

- `AGENTS.md` is the working contract for AI coding agents.
- `CONTRIBUTING.md` is the contributor onboarding and development workflow guide.
- `ROADMAP.md` is the current plan and next-step tracker.
- `CHANGE_LOG.md` is the append-only project narrative.
- `planning/` contains focused design notes and research records that are too detailed for the roadmap.
- `benchmarks/` contains tracked metadata for official external benchmarks; large workbook binaries remain untracked and are restored locally under `tmp/`.
- `src/modelwright/` contains the importable Python package.
- `tests/` contains package-backed tests and tracked synthetic fixture helpers.
- `tmp/` is ignored local working space for private notes, source workbooks, experiments, and generated scratch outputs.
