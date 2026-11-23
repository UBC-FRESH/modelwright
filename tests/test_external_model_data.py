import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType

import pytest
from typer.testing import CliRunner

from modelwright.cli import app
from modelwright.extraction import extract_workbook
from modelwright.formulas import translate_formula_cell
from modelwright.generation import (
    GeneratedModuleContract,
    GeneratedSymbol,
    build_external_model_data,
    generate_python_module,
    infer_generated_module_contract,
    symbol_name_for_cell_ref,
    write_external_model_data,
)
from modelwright.graph import build_dependency_graph
from tests.fixtures.synthetic_model.build_workbook import build_workbook


def synthetic_inputs(tmp_path: Path):
    workbook = extract_workbook(build_workbook(tmp_path / "synthetic_model.xlsx"))
    graph = build_dependency_graph(workbook)
    formula_cells = {cell.cell_ref: cell for cell in workbook.cells if cell.formula is not None}
    expressions = {
        cell_ref: translate_formula_cell(cell, graph)
        for cell_ref, cell in formula_cells.items()
    }
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
                GeneratedSymbol(
                    cell_ref=cell_ref,
                    symbol_name=symbol_name_for_cell_ref(cell_ref),
                    kind="input",
                )
                for cell_ref in constants
            )
            + tuple(
                GeneratedSymbol(
                    cell_ref=cell_ref,
                    symbol_name=symbol_name_for_cell_ref(cell_ref),
                    kind="output" if cell_ref.startswith("Summary!") else "intermediate",
                    raw_formula=formula_cells[cell_ref].formula.raw_formula if formula_cells[cell_ref].formula else None,
                )
                for cell_ref in formula_order
            )
        ),
    )
    return contract, expressions, constants


def load_module(path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location("generated_external_model", path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_build_external_model_data_writes_manifest_and_sheet_csv(tmp_path: Path) -> None:
    contract, _, constants = synthetic_inputs(tmp_path)

    files = build_external_model_data(contract, constants)

    manifest = json.loads(files["manifest.json"])
    assert manifest["format"] == "modelwright-input-data"
    assert manifest["version"] == 1
    assert manifest["workbook_id"] == contract.workbook_id
    assert manifest["input_ref_count"] == len(constants)
    assert manifest["sheets"] == [
        {
            "sheet": "Inputs",
            "file": "000_Inputs.csv",
            "cell_count": 3,
            "sha256": manifest["sheets"][0]["sha256"],
        }
    ]
    csv_text = files["000_Inputs.csv"]
    assert csv_text.splitlines()[0] == "cell_ref,kind,value"
    assert "Inputs!B2,number,100" in csv_text
    assert "Inputs!B4,number,0.65" in csv_text


def test_external_data_mode_matches_embedded_outputs_and_is_editable(tmp_path: Path) -> None:
    contract, expressions, constants = synthetic_inputs(tmp_path)

    embedded_path = tmp_path / "embedded" / "generated_model.py"
    embedded_path.parent.mkdir()
    generate_python_module(
        contract=contract,
        expressions=expressions,
        constants=constants,
        output_path=embedded_path,
    )
    embedded = load_module(embedded_path)

    external_path = tmp_path / "external" / "generated_model.py"
    external_path.parent.mkdir()
    generate_python_module(
        contract=contract,
        expressions=expressions,
        constants=constants,
        output_path=external_path,
        external_data=True,
    )
    data_dir = external_path.parent / "model_data"
    assert (data_dir / "manifest.json").is_file()
    external = load_module(external_path)

    assert external.calculate() == embedded.calculate()

    csv_path = data_dir / "000_Inputs.csv"
    csv_text = csv_path.read_text(encoding="utf-8")
    csv_path.write_text(csv_text.replace("Inputs!B2,number,100", "Inputs!B2,number,200"), encoding="utf-8")
    edited = external.calculate()
    assert edited["Summary!B2"] == pytest.approx(140.4)
    assert edited["Summary!B2"] != embedded.calculate()["Summary!B2"]

    overridden = external.calculate(inputs={"Inputs!B2": 100})
    assert overridden["Summary!B2"] == embedded.calculate()["Summary!B2"]


def test_external_data_mode_reports_missing_data_dir(tmp_path: Path) -> None:
    contract, expressions, constants = synthetic_inputs(tmp_path)
    external_path = tmp_path / "generated_model.py"
    generate_python_module(
        contract=contract,
        expressions=expressions,
        constants=constants,
        output_path=external_path,
        external_data=True,
    )
    module = load_module(external_path)

    with pytest.raises(FileNotFoundError, match="external model data not found"):
        module.calculate(data_dir=tmp_path / "missing")


def test_write_external_model_data_returns_written_paths(tmp_path: Path) -> None:
    contract, _, constants = synthetic_inputs(tmp_path)

    directory, written = write_external_model_data(contract, constants, tmp_path / "model_data")

    assert directory == tmp_path / "model_data"
    assert {path.name for path in written} == {"manifest.json", "000_Inputs.csv"}


def test_model_generate_cli_external_data(tmp_path: Path) -> None:
    contract, expressions, constants = synthetic_inputs(tmp_path)
    contract_path = tmp_path / "contract.json"
    expressions_path = tmp_path / "expressions.json"
    constants_path = tmp_path / "constants.json"
    contract_path.write_text(json.dumps(contract.to_dict()), encoding="utf-8")
    expressions_path.write_text(
        json.dumps({ref: expression.to_dict() for ref, expression in expressions.items()}),
        encoding="utf-8",
    )
    constants_path.write_text(json.dumps(constants), encoding="utf-8")
    output_path = tmp_path / "out" / "generated_model.py"

    result = CliRunner().invoke(
        app,
        [
            "model",
            "generate",
            "--contract",
            str(contract_path),
            "--expressions",
            str(expressions_path),
            "--constants",
            str(constants_path),
            "--out",
            str(output_path),
            "--external-data",
        ],
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["data_dir"] == str(tmp_path / "out" / "model_data")
    assert (tmp_path / "out" / "model_data" / "manifest.json").is_file()


def test_external_data_round_trips_text_boolean_and_blank_values(tmp_path: Path) -> None:
    cell_refs = ("Inputs!A1", "Inputs!B1", "Inputs!C1", "Inputs!D1")
    contract = GeneratedModuleContract(
        workbook_id="synthetic",
        module_name="scalar_types",
        input_refs=cell_refs,
        output_refs=(),
        symbols=tuple(
            GeneratedSymbol(cell_ref=ref, symbol_name=symbol_name_for_cell_ref(ref), kind="input")
            for ref in cell_refs
        ),
    )
    constants = {
        "Inputs!A1": "hello, world",
        "Inputs!B1": True,
        "Inputs!C1": None,
        "Inputs!D1": 1.5,
    }
    output_path = tmp_path / "scalar_types.py"
    generate_python_module(
        contract=contract,
        expressions={},
        constants=constants,
        output_path=output_path,
        external_data=True,
    )

    module = load_module(output_path)
    loaded, manifest = module._load_model_data()
    assert loaded == constants
    assert manifest["input_ref_count"] == 4


def test_manifest_checksums_match_csv_contents(tmp_path: Path) -> None:
    contract, _, constants = synthetic_inputs(tmp_path)

    files = build_external_model_data(contract, constants)
    manifest = json.loads(files["manifest.json"])
    for sheet in manifest["sheets"]:
        content = files[sheet["file"]]
        digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
        assert sheet["sha256"] == digest


def test_generation_with_inference_api_can_write_external_data(tmp_path: Path) -> None:
    workbook = extract_workbook(build_workbook(tmp_path / "synthetic_model.xlsx"))
    graph = build_dependency_graph(workbook)
    expressions = {
        cell.cell_ref: translate_formula_cell(cell, graph)
        for cell in workbook.cells
        if cell.formula is not None
    }
    inference = infer_generated_module_contract(
        workbook=workbook,
        graph=graph,
        expressions=expressions,
        output_refs=["Summary!B2", "Summary!B3"],
        module_name="synthetic_model",
    )
    output_path = tmp_path / "generated" / "generated_model.py"

    result = generate_python_module(
        contract=inference.contract,
        expressions=inference.expressions,
        constants=inference.constants,
        output_path=output_path,
        external_data=True,
    )

    assert result.generated
    assert (output_path.parent / "model_data" / "manifest.json").is_file()
