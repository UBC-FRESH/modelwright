# Typer CLI Refactor

Date: 2026-06-20

## Purpose

P16.2 refactors Sheetforge's first CLI from a minimal `argparse` wrapper into a FRESH-style Typer command surface.

The change follows the Phase 16 acceptance criteria in `planning/phase-16-cli-docs-acceptance-criteria.md`.

## Implemented Shape

The console script now points at a Typer app:

```toml
[project.scripts]
sheetforge = "sheetforge.cli:app"
```

Public workflow groups:

- `sheetforge workbook extract`
- `sheetforge workbook graph`
- `sheetforge model generate`
- `sheetforge validation report`

## Behavior Preserved

- Successful command payloads remain JSON on stdout.
- `model generate --out` writes generated Python source.
- Commands remain thin wrappers over package APIs.
- JSON input files are still validated as JSON objects.
- Extraction, graph, generation, and validation-report automation paths remain covered by tests.

## Dependency Boundary

Typer and Rich are now runtime dependencies because the public CLI depends on them:

- `typer>=0.9`
- `rich>=13`

This matches the CLI style used by the local `fhops` and `femic` reference packages.

## Deferred

- No one-step workbook conversion command.
- No oracle execution command.
- No private-evaluation automation command.
- No additional human-readable report rendering beyond Typer/Rich help output.

Those should wait for the corresponding Python APIs and Sphinx docs to settle.
