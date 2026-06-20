"""Typer-based command-line wrappers for Sheetforge JSON workflows."""

from __future__ import annotations

import json
from collections.abc import Sequence
from pathlib import Path
from typing import Any

import typer
from typer.main import get_command

from sheetforge.extraction import extract_workbook
from sheetforge.formulas import FormulaExpression
from sheetforge.generation import GeneratedModuleContract, generate_python_module
from sheetforge.graph import build_dependency_graph
from sheetforge.validation import build_validation_report, load_validation_scenario


JsonValue = str | int | float | bool | None | list[Any] | dict[str, Any]

app = typer.Typer(
    add_completion=False,
    no_args_is_help=True,
    help="Inspect spreadsheet workbooks and assemble transparent Python-model workflow artifacts.",
)
workbook_app = typer.Typer(
    add_completion=False,
    no_args_is_help=True,
    help="Extract workbook facts and dependency graphs.",
)
model_app = typer.Typer(
    add_completion=False,
    no_args_is_help=True,
    help="Generate standalone Python model artifacts.",
)
validation_app = typer.Typer(
    add_completion=False,
    no_args_is_help=True,
    help="Build validation reports from observed output values.",
)

app.add_typer(workbook_app, name="workbook")
app.add_typer(model_app, name="model")
app.add_typer(validation_app, name="validation")


def main(argv: Sequence[str] | None = None) -> int:
    """Run the Sheetforge CLI with an explicit argv sequence."""

    command = get_command(app)
    command.main(args=list(argv) if argv is not None else None, prog_name="sheetforge", standalone_mode=False)
    return 0


@app.command("extract", hidden=True)
def extract_alias(
    workbook: Path = typer.Argument(..., exists=True, dir_okay=False, readable=True, help="Source workbook path."),
) -> None:
    """Extract workbook facts as JSON."""

    _emit_json(_extract_payload(workbook))


@app.command("graph", hidden=True)
def graph_alias(
    workbook: Path = typer.Argument(..., exists=True, dir_okay=False, readable=True, help="Source workbook path."),
) -> None:
    """Build dependency graph JSON from a workbook."""

    _emit_json(_graph_payload(workbook))


@app.command("generate", hidden=True)
def generate_alias(
    contract: Path = typer.Option(
        ...,
        "--contract",
        exists=True,
        dir_okay=False,
        readable=True,
        help="Generated module contract JSON file.",
    ),
    expressions: Path = typer.Option(
        ...,
        "--expressions",
        exists=True,
        dir_okay=False,
        readable=True,
        help="Formula expressions JSON object.",
    ),
    constants: Path | None = typer.Option(
        None,
        "--constants",
        exists=True,
        dir_okay=False,
        readable=True,
        help="Optional input constants JSON object.",
    ),
    output: Path | None = typer.Option(
        None,
        "--out",
        "--output",
        help="Optional path for generated Python source.",
    ),
) -> None:
    """Generate Python from explicit JSON contracts."""

    _emit_json(_generate_payload(contract=contract, expressions=expressions, constants=constants, output=output))


@app.command("validate-report", hidden=True)
def validate_report_alias(
    scenario: Path = typer.Option(
        ...,
        "--scenario",
        exists=True,
        dir_okay=False,
        readable=True,
        help="Validation scenario JSON file.",
    ),
    generated_values: Path = typer.Option(
        ...,
        "--generated-values",
        exists=True,
        dir_okay=False,
        readable=True,
        help="Generated model output values JSON object.",
    ),
    oracle_values: Path = typer.Option(
        ...,
        "--oracle-values",
        exists=True,
        dir_okay=False,
        readable=True,
        help="Oracle output values JSON object.",
    ),
) -> None:
    """Build validation report JSON."""

    _emit_json(
        _validate_report_payload(
            scenario=scenario,
            generated_values=generated_values,
            oracle_values=oracle_values,
        )
    )


@workbook_app.command("extract")
def workbook_extract(
    workbook: Path = typer.Argument(..., exists=True, dir_okay=False, readable=True, help="Source workbook path."),
) -> None:
    """Extract workbook facts as JSON."""

    _emit_json(_extract_payload(workbook))


@workbook_app.command("graph")
def workbook_graph(
    workbook: Path = typer.Argument(..., exists=True, dir_okay=False, readable=True, help="Source workbook path."),
) -> None:
    """Build dependency graph JSON from a workbook."""

    _emit_json(_graph_payload(workbook))


@model_app.command("generate")
def model_generate(
    contract: Path = typer.Option(
        ...,
        "--contract",
        exists=True,
        dir_okay=False,
        readable=True,
        help="Generated module contract JSON file.",
    ),
    expressions: Path = typer.Option(
        ...,
        "--expressions",
        exists=True,
        dir_okay=False,
        readable=True,
        help="Formula expressions JSON object.",
    ),
    constants: Path | None = typer.Option(
        None,
        "--constants",
        exists=True,
        dir_okay=False,
        readable=True,
        help="Optional input constants JSON object.",
    ),
    output: Path | None = typer.Option(
        None,
        "--out",
        "--output",
        help="Optional path for generated Python source.",
    ),
) -> None:
    """Generate Python from explicit JSON contracts."""

    _emit_json(_generate_payload(contract=contract, expressions=expressions, constants=constants, output=output))


@validation_app.command("report")
def validation_report(
    scenario: Path = typer.Option(
        ...,
        "--scenario",
        exists=True,
        dir_okay=False,
        readable=True,
        help="Validation scenario JSON file.",
    ),
    generated_values: Path = typer.Option(
        ...,
        "--generated-values",
        exists=True,
        dir_okay=False,
        readable=True,
        help="Generated model output values JSON object.",
    ),
    oracle_values: Path = typer.Option(
        ...,
        "--oracle-values",
        exists=True,
        dir_okay=False,
        readable=True,
        help="Oracle output values JSON object.",
    ),
) -> None:
    """Build validation report JSON."""

    _emit_json(
        _validate_report_payload(
            scenario=scenario,
            generated_values=generated_values,
            oracle_values=oracle_values,
        )
    )


def _extract_payload(workbook: Path) -> dict[str, JsonValue]:
    return extract_workbook(workbook).to_dict()


def _graph_payload(workbook: Path) -> dict[str, JsonValue]:
    workbook_record = extract_workbook(workbook)
    graph = build_dependency_graph(workbook_record)
    return graph.to_dict()


def _generate_payload(
    *,
    contract: Path,
    expressions: Path,
    constants: Path | None,
    output: Path | None,
) -> dict[str, JsonValue]:
    module_contract = GeneratedModuleContract.from_dict(_load_object(contract))
    formula_expressions = {
        cell_ref: FormulaExpression.from_dict(expression)
        for cell_ref, expression in _load_object(expressions).items()
    }
    result = generate_python_module(
        contract=module_contract,
        expressions=formula_expressions,
        constants=_load_object(constants) if constants else {},
        output_path=output,
    )
    return result.to_dict()


def _validate_report_payload(
    *,
    scenario: Path,
    generated_values: Path,
    oracle_values: Path,
) -> dict[str, JsonValue]:
    report = build_validation_report(
        scenario=load_validation_scenario(scenario),
        generated_values=_load_object(generated_values),
        oracle_values=_load_object(oracle_values),
    )
    return report.to_dict()


def _emit_json(payload: dict[str, JsonValue]) -> None:
    typer.echo(json.dumps(payload, indent=2, sort_keys=True))


def _load_object(path: str | Path) -> dict[str, JsonValue]:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except OSError as error:
        raise typer.BadParameter(f"could not read JSON file {path}: {error}") from error
    except json.JSONDecodeError as error:
        raise typer.BadParameter(f"could not parse JSON file {path}: {error}") from error

    if not isinstance(data, dict):
        raise typer.BadParameter(f"expected JSON object in {path}")
    return data


if __name__ == "__main__":
    app()
