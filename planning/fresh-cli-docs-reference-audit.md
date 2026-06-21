# FRESH CLI And Docs Reference Audit

Date: 2026-06-20

## Purpose

This note records the local reference packages Modelwright should use for CLI feel and Sphinx documentation scope.

Reference repos inspected:

- `/home/gep/projects/fhops`
- `/home/gep/projects/femic`

## CLI Pattern

Both packages expose a public console script through `pyproject.toml` and route it to a Typer application:

- `fhops = "fhops.cli.main:app"`
- `femic = "femic.cli.main:app"`

Observed style:

- Typer command apps rather than bare `argparse`;
- grouped subcommands for workflow areas;
- `no_args_is_help=True` and completion disabled where appropriate;
- `rich.console.Console` for human-oriented output;
- explicit path arguments and options;
- output file options named like `--out`, `--out-json`, `--out-csv`, or domain-specific variants;
- `typer.BadParameter` and `typer.Exit` for user-facing failures;
- docstrings and help text that double as CLI/API reference material.

Modelwright's current argparse CLI is acceptable as a thin first wrapper, but it should be migrated toward this Typer/Rich style before the CLI becomes the primary public interface.

## Documentation Pattern

Both packages use Sphinx with curated narrative pages plus generated API reference.

Common pieces:

- `docs/conf.py`;
- `docs/index.rst`;
- `docs/requirements.txt`;
- `sphinx.ext.autodoc`;
- `sphinx.ext.autosummary`;
- `sphinx.ext.napoleon`;
- `sphinx.ext.viewcode`;
- warning-clean local build command: `sphinx-build -b html docs _build/html -W`.

FEMIC also has a GitHub Pages workflow:

- builds docs on pull requests and pushes to `main`;
- uploads the built `_build/html` artifact;
- deploys to GitHub Pages only on non-PR `main` builds.

Modelwright should follow that GitHub Pages model rather than Read the Docs for the next docs milestone.

## Modelwright Implications

Phase 16 should add:

- a Typer/Rich CLI refactor with the same general interaction style;
- curated docs pages for overview, quickstart, CLI, workflow boundaries, private workbook handling, validation, limitations, and API reference;
- GitHub Pages workflow triggered by pull requests and pushes to `main`;
- docs verification in CI with warnings as errors.

The docs should remain honest: Modelwright is still pre-release and does not yet perform full workbook conversion.
