import importlib.util
import json
import math
import statistics
import sys
from pathlib import Path

import pytest
from typer.testing import CliRunner

from modelwright.cli import app
from modelwright.extraction import extract_workbook
from modelwright.formulas import translate_formula_cell
from modelwright.generation import (
    GeneratedModuleContract,
    GeneratedSymbol,
    generate_python_module,
    symbol_name_for_cell_ref,
)
from modelwright.graph import build_dependency_graph
from modelwright.uncertainty import (
    InputDistribution,
    UncertaintySpec,
    evaluate_draws,
    iter_input_draws,
    run_uncertainty,
    summarize_draws,
    unknown_input_refs,
)
from tests.fixtures.synthetic_model.build_workbook import build_workbook


def build_synthetic_model(tmp_path: Path):
    workbook = extract_workbook(build_workbook(tmp_path / "synthetic_model.xlsx"))
    graph = build_dependency_graph(workbook)
    formula_cells = {cell.cell_ref: cell for cell in workbook.cells if cell.formula is not None}
    expressions = {ref: translate_formula_cell(cell, graph) for ref, cell in formula_cells.items()}
    constants = {
        cell.cell_ref: cell.raw_value
        for cell in workbook.cells
        if cell.formula is None and cell.cell_ref in {"Inputs!B2", "Inputs!B3", "Inputs!B4"}
    }
    formula_order = ("Calc!B2", "Calc!B3", "Calc!B4", "Summary!B2", "Summary!B3")
    contract = GeneratedModuleContract(
        workbook_id=workbook.workbook_id,
        module_name="synthetic_model",
        input_refs=tuple(constants),
        output_refs=("Summary!B2", "Summary!B3"),
        symbols=(
            tuple(
                GeneratedSymbol(cell_ref=ref, symbol_name=symbol_name_for_cell_ref(ref), kind="input")
                for ref in constants
            )
            + tuple(
                GeneratedSymbol(
                    cell_ref=ref,
                    symbol_name=symbol_name_for_cell_ref(ref),
                    kind="output" if ref.startswith("Summary!") else "intermediate",
                    raw_formula=formula_cells[ref].formula.raw_formula if formula_cells[ref].formula else None,
                )
                for ref in formula_order
            )
        ),
    )
    output_path = tmp_path / "generated" / "generated_model.py"
    output_path.parent.mkdir()
    generate_python_module(
        contract=contract,
        expressions=expressions,
        constants=constants,
        output_path=output_path,
    )
    module_spec = importlib.util.spec_from_file_location("generated_uncertainty_model", output_path)
    assert module_spec is not None and module_spec.loader is not None
    module = importlib.util.module_from_spec(module_spec)
    sys.modules[module_spec.name] = module
    module_spec.loader.exec_module(module)
    return contract, module, output_path


def test_distribution_inverse_cdf_families() -> None:
    normal = InputDistribution("Inputs!B2", "normal", {"mean": 10.0, "std": 2.0})
    assert normal.inverse_cdf(0.5) == pytest.approx(10.0)

    uniform = InputDistribution("Inputs!B2", "uniform", {"low": -1.0, "high": 3.0})
    assert uniform.inverse_cdf(0.0) == pytest.approx(-1.0, abs=1e-9)
    assert uniform.inverse_cdf(1.0) == pytest.approx(3.0, abs=1e-9)

    lognormal = InputDistribution("Inputs!B2", "lognormal", {"mean": 0.0, "sigma": 1.0})
    assert lognormal.inverse_cdf(0.5) == pytest.approx(1.0)

    triangular = InputDistribution("Inputs!B2", "triangular", {"low": 0.0, "mode": 2.0, "high": 5.0})
    assert triangular.inverse_cdf((2.0 - 0.0) / (5.0 - 0.0)) == pytest.approx(2.0)

    truncated = InputDistribution(
        "Inputs!B2",
        "truncated_normal",
        {"mean": 0.0, "std": 1.0, "low": -1.0, "high": 1.0},
    )
    for unit in (0.01, 0.25, 0.5, 0.75, 0.99):
        assert -1.0 <= truncated.inverse_cdf(unit) <= 1.0

    constant = InputDistribution("Inputs!B2", "constant", {"value": 7.5})
    assert constant.inverse_cdf(0.3) == 7.5


def test_distribution_validation_rejects_bad_parameters() -> None:
    with pytest.raises(ValueError, match="unsupported distribution family"):
        InputDistribution("Inputs!B2", "cauchy", {"location": 0.0, "scale": 1.0})
    with pytest.raises(ValueError, match="missing parameter"):
        InputDistribution("Inputs!B2", "normal", {"mean": 0.0})
    with pytest.raises(ValueError, match="std"):
        InputDistribution("Inputs!B2", "normal", {"mean": 0.0, "std": 0.0})
    with pytest.raises(ValueError, match="low < high"):
        InputDistribution("Inputs!B2", "uniform", {"low": 2.0, "high": 1.0})
    with pytest.raises(ValueError, match="cell_ref"):
        InputDistribution("B2", "normal", {"mean": 0.0, "std": 1.0})


def test_spec_round_trip_and_hashes(tmp_path: Path) -> None:
    spec = UncertaintySpec(
        distributions=(
            InputDistribution("Inputs!B2", "normal", {"mean": 100.0, "std": 10.0}),
            InputDistribution("Inputs!B4", "uniform", {"low": 0.5, "high": 0.8}),
        ),
        draws=50,
        seed=11,
        design="latin_hypercube",
        output_refs=("Summary!B2",),
        percentiles=(5.0, 50.0, 95.0),
        histogram_bins=10,
    )
    path = spec.save(tmp_path / "spec.json")
    loaded = UncertaintySpec.load(path)
    assert loaded.to_dict() == spec.to_dict()
    assert loaded.sha256 == spec.sha256
    assert json.loads(path.read_text(encoding="utf-8"))["draws"] == 50


def test_spec_validation_rejects_duplicates_and_bad_percentiles() -> None:
    distribution = InputDistribution("Inputs!B2", "normal", {"mean": 0.0, "std": 1.0})
    with pytest.raises(ValueError, match="duplicate"):
        UncertaintySpec(distributions=(distribution, distribution))
    with pytest.raises(ValueError, match="sorted"):
        UncertaintySpec(distributions=(distribution,), percentiles=(50.0, 5.0))
    with pytest.raises(ValueError, match="design"):
        UncertaintySpec(distributions=(distribution,), design="sobol")


def test_input_draws_are_seeded_and_lhs_stratified() -> None:
    spec = UncertaintySpec(
        distributions=(InputDistribution("Inputs!B2", "normal", {"mean": 0.0, "std": 1.0}),),
        draws=100,
        seed=42,
        design="latin_hypercube",
    )
    first = list(iter_input_draws(spec))
    second = list(iter_input_draws(spec))
    assert [draw[1] for draw in first] == [draw[1] for draw in second]

    units = [statistics.NormalDist().cdf(value) for _, values in first for value in values.values()]
    strata = sorted(math.floor(unit * spec.draws) for unit in units)
    assert strata == list(range(spec.draws))


def test_run_uncertainty_on_synthetic_model_estimates_expected_value(tmp_path: Path) -> None:
    _, module, _ = build_synthetic_model(tmp_path)
    spec = UncertaintySpec(
        distributions=(InputDistribution("Inputs!B2", "normal", {"mean": 100.0, "std": 10.0}),),
        draws=4000,
        seed=7,
        output_refs=("Summary!B2",),
    )

    result = run_uncertainty(module.calculate, spec)

    summary = result["outputs"][0]
    assert summary["cell_ref"] == "Summary!B2"
    assert summary["count"] == 4000
    assert summary["numeric_count"] == 4000
    assert summary["error_count"] == 0
    assert summary["mean"] == pytest.approx(70.2, abs=5 * summary["standard_error"] + 0.01)
    assert summary["percentiles"]["p5"] < summary["percentiles"]["p50"] < summary["percentiles"]["p95"]
    assert summary["percentiles"]["p50"] == pytest.approx(70.2, abs=1.0)
    assert summary["percentiles"]["p5"] == pytest.approx(58.65, abs=1.5)
    assert summary["percentiles"]["p95"] == pytest.approx(81.75, abs=1.5)
    assert summary["coefficient_of_variation"] == pytest.approx(7.02 / 70.2, rel=0.1)
    assert sum(summary["histogram"]["counts"]) == 4000
    assert result["provenance"]["seed"] == 7
    assert result["provenance"]["draws"] == 4000

    repeated = run_uncertainty(module.calculate, spec)
    assert repeated["outputs"] == result["outputs"]


def test_include_samples_and_output_selection(tmp_path: Path) -> None:
    _, module, _ = build_synthetic_model(tmp_path)
    spec = UncertaintySpec(
        distributions=(InputDistribution("Inputs!B2", "constant", {"value": 100.0}),),
        draws=2,
        output_refs=("Summary!B2",),
    )

    result = run_uncertainty(module.calculate, spec, include_samples=True)

    assert [sample["values"] for sample in result["samples"]] == [
        {"Summary!B2": 70.2},
        {"Summary!B2": 70.2},
    ]


def test_evaluate_draws_records_or_raises_errors() -> None:
    spec = UncertaintySpec(
        distributions=(InputDistribution("Inputs!B2", "constant", {"value": 1.0}),),
        draws=3,
    )

    def failing_calculate(inputs=None, **kwargs):
        raise ValueError("boom")

    results = evaluate_draws(failing_calculate, spec)
    assert len(results) == 3
    assert all(result.error == "ValueError: boom" for result in results)
    summaries = summarize_draws(results, spec)
    assert summaries == ()

    with pytest.raises(ValueError, match="boom"):
        evaluate_draws(failing_calculate, spec, stop_on_error=True)


def test_unknown_input_refs() -> None:
    spec = UncertaintySpec(
        distributions=(
            InputDistribution("Inputs!B2", "normal", {"mean": 0.0, "std": 1.0}),
            InputDistribution("Inputs!Z99", "normal", {"mean": 0.0, "std": 1.0}),
        )
    )
    assert unknown_input_refs(spec, ["Inputs!B2"]) == ("Inputs!Z99",)


def test_uncertainty_with_external_input_data(tmp_path: Path) -> None:
    workbook = extract_workbook(build_workbook(tmp_path / "synthetic_model.xlsx"))
    graph = build_dependency_graph(workbook)
    expressions = {
        cell.cell_ref: translate_formula_cell(cell, graph)
        for cell in workbook.cells
        if cell.formula is not None
    }
    constants = {
        cell.cell_ref: cell.raw_value
        for cell in workbook.cells
        if cell.formula is None and cell.cell_ref in {"Inputs!B2", "Inputs!B3", "Inputs!B4"}
    }
    contract = GeneratedModuleContract(
        workbook_id=workbook.workbook_id,
        module_name="synthetic_model",
        input_refs=tuple(constants),
        output_refs=("Summary!B2",),
        symbols=(
            tuple(
                GeneratedSymbol(cell_ref=ref, symbol_name=symbol_name_for_cell_ref(ref), kind="input")
                for ref in constants
            )
            + tuple(
                GeneratedSymbol(
                    cell_ref=ref,
                    symbol_name=symbol_name_for_cell_ref(ref),
                    kind="output" if ref.startswith("Summary!") else "intermediate",
                    raw_formula=expressions[ref].raw_formula,
                )
                for ref in ("Calc!B2", "Calc!B3", "Calc!B4", "Summary!B2")
            )
        ),
    )
    output_path = tmp_path / "external" / "generated_model.py"
    output_path.parent.mkdir()
    generate_python_module(
        contract=contract,
        expressions={ref: expressions[ref] for ref in ("Calc!B2", "Calc!B3", "Calc!B4", "Summary!B2")},
        constants=constants,
        output_path=output_path,
        external_data=True,
    )
    module_spec = importlib.util.spec_from_file_location("generated_external_uncertainty", output_path)
    assert module_spec is not None and module_spec.loader is not None
    module = importlib.util.module_from_spec(module_spec)
    sys.modules[module_spec.name] = module
    module_spec.loader.exec_module(module)

    spec = UncertaintySpec(
        distributions=(InputDistribution("Inputs!B2", "constant", {"value": 200.0}),),
        draws=1,
        output_refs=("Summary!B2",),
    )
    result = run_uncertainty(
        module.calculate,
        spec,
        calculate_kwargs={"data_dir": output_path.parent / "model_data"},
    )

    assert result["outputs"][0]["mean"] == pytest.approx(140.4)


def test_uncertainty_cli_run(tmp_path: Path) -> None:
    contract, _module, model_path = build_synthetic_model(tmp_path)
    contract_path = tmp_path / "contract.json"
    contract_path.write_text(json.dumps(contract.to_dict()), encoding="utf-8")
    spec = UncertaintySpec(
        distributions=(InputDistribution("Inputs!B2", "constant", {"value": 100.0}),),
        draws=2,
        output_refs=("Summary!B2",),
    )
    spec_path = spec.save(tmp_path / "spec.json")

    result = CliRunner().invoke(
        app,
        [
            "uncertainty",
            "run",
            "--model",
            str(model_path),
            "--spec",
            str(spec_path),
            "--contract",
            str(contract_path),
        ],
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["outputs"][0]["cell_ref"] == "Summary!B2"
    assert payload["outputs"][0]["mean"] == pytest.approx(70.2)

    unknown_spec = UncertaintySpec(
        distributions=(InputDistribution("Inputs!Z99", "constant", {"value": 1.0}),),
        draws=1,
    )
    unknown_path = unknown_spec.save(tmp_path / "unknown_spec.json")
    failed = CliRunner().invoke(
        app,
        [
            "uncertainty",
            "run",
            "--model",
            str(model_path),
            "--spec",
            str(unknown_path),
            "--contract",
            str(contract_path),
        ],
    )
    assert failed.exit_code == 2
