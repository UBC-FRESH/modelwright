import importlib.util
import sys
from pathlib import Path
from types import ModuleType

import pytest

from modelwright.extraction import extract_workbook
from modelwright.formulas import translate_formula_cell
from modelwright.generation import generate_python_module, infer_generated_module_contract
from modelwright.graph import build_dependency_graph
from modelwright.wrappers import (
    ModelFacade,
    Scenario,
    WrapperDeclarationError,
    WrapperExecutionError,
    cell,
    report,
    table,
)
from tests.fixtures.synthetic_model.build_workbook import build_workbook


def generated_model(inputs=None):
    inputs = inputs or {}
    base = inputs.get("Inputs!B2", 100)
    growth = inputs.get("Inputs!B3", 0.1)
    return {
        "Summary!B2": base * (1 + growth),
        "Summary!C2": base * 2,
        "Summary!B3": "ok",
        "Summary!C3": base + 5,
    }


def load_module(path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location("wrapped_generated_synthetic_model", path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def build_generated_synthetic_model(tmp_path: Path) -> ModuleType:
    workbook = extract_workbook(build_workbook(tmp_path / "synthetic_model.xlsx"))
    graph = build_dependency_graph(workbook)
    formula_cells = {cell.cell_ref: cell for cell in workbook.cells if cell.formula is not None}
    expressions = {
        cell_ref: translate_formula_cell(cell, graph)
        for cell_ref, cell in formula_cells.items()
    }
    inference = infer_generated_module_contract(
        workbook=workbook,
        graph=graph,
        expressions=expressions,
        output_refs=("Summary!B2", "Summary!B3"),
        module_name="synthetic_model",
    )
    output_path = tmp_path / "generated_synthetic_model.py"

    generation = generate_python_module(
        contract=inference.contract,
        expressions=inference.expressions,
        constants=inference.constants,
        output_path=output_path,
    )

    assert generation.generated is True
    return load_module(output_path)


def test_model_facade_wraps_generated_model_with_scenario_tables_and_reports() -> None:
    facade = ModelFacade(
        generated_model,
        cells=[
            cell("Inputs!B2", name="base", label="Base volume", role="input", unit="t"),
            cell("Inputs!B3", name="growth", label="Growth rate", role="input", unit="fraction"),
            cell("Summary!B2", name="projected", label="Projected volume", role="output", unit="t"),
        ],
        tables=[
            table(
                "summary_grid",
                sheet="Summary",
                range_ref="B2:C3",
                row_labels=["volume", "status"],
                column_labels=["primary", "secondary"],
            )
        ],
        reports=[report("summary", cells=["base", "projected"], tables=["summary_grid"])],
    )

    scenario = facade.scenario(inputs={"Inputs!B2": 50}).with_input("Inputs!B3", 0.2)

    assert facade.inputs()["base"].cell_ref == "Inputs!B2"
    assert facade.outputs()["projected"].cell_ref == "Summary!B2"
    assert facade.calculate(scenario) == {
        "Summary!B2": 60.0,
        "Summary!C2": 100,
        "Summary!B3": "ok",
        "Summary!C3": 55,
    }

    input_view = facade.inspect("Inputs!B2", scenario)
    assert input_view.to_dict() == {
        "cell_ref": "Inputs!B2",
        "name": "base",
        "label": "Base volume",
        "role": "input",
        "unit": "t",
        "description": None,
        "value": 50,
        "has_value": True,
    }

    table_view = facade.table("summary_grid", scenario)
    assert table_view.to_dict() == {
        "name": "summary_grid",
        "sheet": "Summary",
        "range_ref": "B2:C3",
        "rows": ["volume", "status"],
        "columns": ["primary", "secondary"],
        "cell_refs": [["Summary!B2", "Summary!C2"], ["Summary!B3", "Summary!C3"]],
        "values": [[60.0, 100], ["ok", 55]],
        "label": None,
        "description": None,
    }

    report_payload = facade.report("summary", scenario)
    assert report_payload["cells"]["base"]["value"] == 50
    assert report_payload["cells"]["projected"]["value"] == 60.0
    assert report_payload["tables"]["summary_grid"]["values"] == [[60.0, 100], ["ok", 55]]


def test_model_facade_preserves_real_generated_synthetic_model_semantics(tmp_path: Path) -> None:
    module = build_generated_synthetic_model(tmp_path)
    facade = ModelFacade(
        module,
        cells=[
            cell("Inputs!B2", name="base", label="Base volume", role="input"),
            cell("Inputs!B3", name="growth", label="Growth rate", role="input"),
            cell("Inputs!B4", name="harvest_share", label="Harvest share", role="input"),
            cell("Summary!B2", name="harvest", label="Rounded harvest", role="output"),
            cell("Summary!B3", name="status", label="Status", role="output"),
        ],
        tables=[
            table(
                "summary",
                sheet="Summary",
                range_ref="B2:B3",
                row_labels=["harvest", "status"],
                column_labels=["value"],
            )
        ],
        reports=[report("default", cells=["base", "harvest", "status"], tables=["summary"])],
    )

    assert facade.calculate() == module.calculate()

    scenario = facade.scenario(name="low-volume", inputs={"Inputs!B2": 10})
    generated_values = module.calculate(scenario.inputs)

    assert facade.calculate(scenario) == generated_values
    assert generated_values == {"Summary!B2": 7.02, "Summary!B3": "low"}
    assert facade.inspect("Summary!B2", scenario).value == generated_values["Summary!B2"]
    assert facade.table("summary", scenario).to_dict()["values"] == [[7.02], ["low"]]

    report_payload = facade.report("default", scenario)
    assert report_payload["cells"]["base"]["value"] == 10
    assert report_payload["cells"]["harvest"]["value"] == generated_values["Summary!B2"]
    assert report_payload["tables"]["summary"]["values"] == [[7.02], ["low"]]


def test_scenario_is_copy_on_write_and_normalizes_input_refs() -> None:
    original = Scenario.from_inputs(inputs={"Inputs!B2": 10})
    updated = original.with_input("Inputs!B3", 0.25)

    assert original.inputs == {"Inputs!B2": 10}
    assert updated.inputs == {"Inputs!B2": 10, "Inputs!B3": 0.25}


def test_table_declaration_validates_label_shape() -> None:
    with pytest.raises(WrapperDeclarationError, match="row labels"):
        table("bad_rows", sheet="Summary", range_ref="A1:A2", row_labels=["only one"])

    with pytest.raises(WrapperDeclarationError, match="column labels"):
        table("bad_columns", sheet="Summary", range_ref="A1:B1", column_labels=["only one"])


def test_facade_validates_duplicate_names_and_report_references() -> None:
    with pytest.raises(WrapperDeclarationError, match="duplicate cell declaration"):
        ModelFacade(
            generated_model,
            cells=[
                cell("Inputs!B2", name="base"),
                cell("Inputs!B3", name="base"),
            ],
        )

    with pytest.raises(WrapperDeclarationError, match="unknown table"):
        ModelFacade(generated_model, reports=[report("bad", tables=["missing"])])


def test_facade_wraps_generated_model_execution_errors() -> None:
    def broken_model(inputs=None):
        raise RuntimeError("boom")

    facade = ModelFacade(broken_model)

    with pytest.raises(WrapperExecutionError, match="calculation failed"):
        facade.calculate()
