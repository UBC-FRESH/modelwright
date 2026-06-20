"""Typer-based command-line wrappers for Sheetforge JSON workflows."""

from __future__ import annotations

import json
from collections.abc import Sequence
from pathlib import Path
from typing import Any, cast

import typer
from typer.main import get_command

from sheetforge.conversion import BenchmarkRole, build_conversion_plan
from sheetforge.evaluation import evaluate_generated_model
from sheetforge.execution import execute_generated_model
from sheetforge.extraction import WorkbookRecord, extract_workbook
from sheetforge.formulas import FormulaExpression, build_formula_reference_index, translate_formula_cell
from sheetforge.generation import GeneratedModuleContract, generate_python_module
from sheetforge.graph import build_dependency_graph
from sheetforge.oracles import OracleResult
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
conversion_app = typer.Typer(
    add_completion=False,
    no_args_is_help=True,
    help="Assemble conversion planning reports.",
)

app.add_typer(workbook_app, name="workbook")
app.add_typer(model_app, name="model")
app.add_typer(validation_app, name="validation")
app.add_typer(conversion_app, name="conversion")


def main(argv: Sequence[str] | None = None) -> int:
    """Run the Sheetforge CLI with an explicit argv sequence."""

    command = get_command(app)
    command.main(args=list(argv) if argv is not None else None, prog_name="sheetforge", standalone_mode=False)
    return 0


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
        help="Optional path for generated Python source.",
    ),
) -> None:
    """Generate Python from explicit JSON contracts."""

    _emit_json(_generate_payload(contract=contract, expressions=expressions, constants=constants, output=output))


@model_app.command("execute")
def model_execute(
    contract: Path = typer.Option(
        ...,
        "--contract",
        exists=True,
        dir_okay=False,
        readable=True,
        help="Generated module contract JSON file.",
    ),
    model: Path = typer.Option(
        ...,
        "--model",
        exists=True,
        dir_okay=False,
        readable=True,
        help="Generated Python model file.",
    ),
    inputs: Path | None = typer.Option(
        None,
        "--inputs",
        exists=True,
        dir_okay=False,
        readable=True,
        help="Optional generated model input overrides JSON object.",
    ),
) -> None:
    """Execute generated Python model JSON outputs."""

    _emit_json(_execute_payload(contract=contract, model=model, inputs=inputs))


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


@validation_app.command("evaluate")
def validation_evaluate(
    contract: Path = typer.Option(
        ...,
        "--contract",
        exists=True,
        dir_okay=False,
        readable=True,
        help="Generated module contract JSON file.",
    ),
    model: Path = typer.Option(
        ...,
        "--model",
        exists=True,
        dir_okay=False,
        readable=True,
        help="Generated Python model file.",
    ),
    scenario: Path = typer.Option(
        ...,
        "--scenario",
        exists=True,
        dir_okay=False,
        readable=True,
        help="Validation scenario JSON file.",
    ),
    workbook: Path | None = typer.Option(
        None,
        "--workbook",
        exists=True,
        dir_okay=False,
        readable=True,
        help="Optional source workbook path used for cached workbook validation.",
    ),
    workbook_record: Path | None = typer.Option(
        None,
        "--workbook-record",
        exists=True,
        dir_okay=False,
        readable=True,
        help="Optional extracted WorkbookRecord JSON used for cached workbook validation.",
    ),
    oracle_result: Path | None = typer.Option(
        None,
        "--oracle-result",
        exists=True,
        dir_okay=False,
        readable=True,
        help="Optional OracleResult JSON used for oracle-backed validation.",
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        help="Print progress messages to stderr while keeping stdout as JSON.",
    ),
) -> None:
    """Execute generated model and build available validation reports."""

    _emit_json(
        _evaluate_payload(
            contract=contract,
            model=model,
            scenario=scenario,
            workbook=workbook,
            workbook_record=workbook_record,
            oracle_result=oracle_result,
            verbose=verbose,
        )
    )


@conversion_app.command("plan")
def conversion_plan(
    workbook: Path = typer.Argument(..., exists=True, dir_okay=False, readable=True, help="Source workbook path."),
    plan_id: str | None = typer.Option(
        None,
        "--plan-id",
        help="Stable plan identifier. Defaults to conversion-plan:<workbook filename>.",
    ),
    benchmark_role: str = typer.Option(
        "ad_hoc_private",
        "--benchmark-role",
        help="Benchmark role for the source workbook.",
    ),
    sheetforge_commit: str = typer.Option(
        "unknown",
        "--sheetforge-commit",
        help="Sheetforge commit identifier to record in the plan.",
    ),
    include_source_path: bool = typer.Option(
        False,
        "--include-source-path",
        help="Include the local workbook path in JSON output. Off by default for safer sharing.",
    ),
) -> None:
    """Build a conversion plan from workbook extraction, graphing, and translation."""

    _emit_json(
        _conversion_plan_payload(
            workbook=workbook,
            plan_id=plan_id,
            benchmark_role=_parse_benchmark_role(benchmark_role),
            sheetforge_commit=sheetforge_commit,
            include_source_path=include_source_path,
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


def _execute_payload(
    *,
    contract: Path,
    model: Path,
    inputs: Path | None,
) -> dict[str, JsonValue]:
    result = execute_generated_model(
        contract=GeneratedModuleContract.from_dict(_load_object(contract)),
        module_path=model,
        inputs=_load_object(inputs) if inputs else {},
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


def _evaluate_payload(
    *,
    contract: Path,
    model: Path,
    scenario: Path,
    workbook: Path | None,
    workbook_record: Path | None,
    oracle_result: Path | None,
    verbose: bool,
) -> dict[str, JsonValue]:
    if workbook is not None and workbook_record is not None:
        raise typer.BadParameter("use --workbook or --workbook-record, not both")

    def progress(message: str) -> None:
        if verbose:
            typer.echo(message, err=True)

    progress("load contract")
    module_contract = GeneratedModuleContract.from_dict(_load_object(contract))
    progress("load scenario")
    validation_scenario = load_validation_scenario(scenario)

    extracted_workbook = None
    if workbook is not None:
        progress("extract workbook start")
        extracted_workbook = extract_workbook(workbook, progress=progress if verbose else None)
        progress("extract workbook done")
    elif workbook_record is not None:
        progress("load workbook record")
        extracted_workbook = WorkbookRecord.from_dict(_load_object(workbook_record))

    loaded_oracle_result = None
    if oracle_result is not None:
        progress("load oracle result")
        loaded_oracle_result = OracleResult.from_dict(_load_object(oracle_result))

    progress("evaluate generated model")
    result = evaluate_generated_model(
        contract=module_contract,
        module_path=model,
        scenario=validation_scenario,
        workbook=extracted_workbook,
        oracle_result=loaded_oracle_result,
    )
    progress("evaluate generated model done")
    return result.to_dict()


def _conversion_plan_payload(
    *,
    workbook: Path,
    plan_id: str | None,
    benchmark_role: BenchmarkRole,
    sheetforge_commit: str,
    include_source_path: bool,
) -> dict[str, JsonValue]:
    workbook_record = extract_workbook(workbook)
    graph = build_dependency_graph(workbook_record)
    reference_index = build_formula_reference_index(graph)
    expressions = {
        cell.cell_ref: translate_formula_cell(cell, graph, reference_index)
        for cell in workbook_record.cells
        if cell.formula is not None
    }
    plan = build_conversion_plan(
        plan_id=plan_id or f"conversion-plan:{workbook.name}",
        workbook=workbook_record,
        graph=graph,
        expressions=expressions,
        benchmark_role=benchmark_role,
        sheetforge_commit=sheetforge_commit,
        include_source_path=include_source_path,
    )
    return plan.to_dict()


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


def _parse_benchmark_role(value: str) -> BenchmarkRole:
    supported: tuple[BenchmarkRole, ...] = (
        "primary_benchmark",
        "stress_benchmark",
        "broken_reference_regression",
        "synthetic_fixture",
        "ad_hoc_private",
    )
    if value not in supported:
        supported_values = ", ".join(supported)
        raise typer.BadParameter(f"unsupported benchmark role {value!r}; expected one of: {supported_values}")
    return cast(BenchmarkRole, value)


if __name__ == "__main__":
    app()
