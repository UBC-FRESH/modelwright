import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType

from sheetforge.extraction import extract_workbook
from sheetforge.formulas import FormulaExpression, FormulaExpressionNode, translate_formula_cell
from sheetforge.generation import (
    GeneratedModuleContract,
    GeneratedSymbol,
    GenerationResult,
    generate_python_module,
    symbol_name_for_cell_ref,
)
from sheetforge.graph import build_dependency_graph
from sheetforge.references import normalize_reference
from tests.fixtures.synthetic_model.build_workbook import build_workbook


def synthetic_generation_inputs(tmp_path: Path) -> tuple[GeneratedModuleContract, dict, dict]:
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
    spec = importlib.util.spec_from_file_location("generated_synthetic_model", path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def formula_expression(source_cell: str, raw_formula: str, root: FormulaExpressionNode) -> FormulaExpression:
    return FormulaExpression(source_cell=source_cell, raw_formula=raw_formula, root=root)


def test_generate_python_module_writes_standalone_synthetic_model(tmp_path: Path) -> None:
    contract, expressions, constants = synthetic_generation_inputs(tmp_path)
    output_path = tmp_path / "generated_model.py"

    result = generate_python_module(
        contract=contract,
        expressions=expressions,
        constants=constants,
        output_path=output_path,
    )

    assert result.generated is True
    assert output_path.exists()
    assert "Source workbook: synthetic_model.xlsx" in result.source_code
    assert "# Calc!B2: =BaseVolume*(1+GrowthRate)" in result.source_code
    assert "def calculate(inputs=None):" in result.source_code
    assert "openpyxl" not in result.source_code
    module = load_module(output_path)
    assert module.calculate() == {"Summary!B2": 70.2, "Summary!B3": "ok"}


def test_generate_python_module_uses_input_overrides(tmp_path: Path) -> None:
    contract, expressions, constants = synthetic_generation_inputs(tmp_path)
    output_path = tmp_path / "generated_model.py"

    result = generate_python_module(
        contract=contract,
        expressions=expressions,
        constants=constants,
        output_path=output_path,
    )
    module = load_module(output_path)

    assert result.generated is True
    assert module.calculate({"Inputs!B2": 10}) == {"Summary!B2": 7.02, "Summary!B3": "low"}


def test_generate_python_module_payload_round_trips_without_writing(tmp_path: Path) -> None:
    contract, expressions, constants = synthetic_generation_inputs(tmp_path)

    result = generate_python_module(contract=contract, expressions=expressions, constants=constants)
    payload = result.to_dict()

    assert result.generated is True
    assert not (tmp_path / "generated_model.py").exists()
    assert json.loads(json.dumps(payload)) == payload
    assert GenerationResult.from_dict(payload) == result


def test_generate_python_module_reports_missing_expression(tmp_path: Path) -> None:
    contract, expressions, constants = synthetic_generation_inputs(tmp_path)
    expressions.pop("Summary!B3")

    result = generate_python_module(contract=contract, expressions=expressions, constants=constants)

    assert result.generated is False
    assert result.source_code == ""
    assert result.diagnostics[0].code == "missing_formula_expression"
    assert result.diagnostics[0].location == "Summary!B3"


def test_generate_python_module_renders_p17_operator_slice(tmp_path: Path) -> None:
    contract = GeneratedModuleContract(
        workbook_id="operators.xlsx",
        module_name="operators",
        input_refs=("Inputs!A1", "Inputs!A2"),
        output_refs=("Calc!B1", "Calc!B2", "Calc!B3", "Calc!B4"),
        symbols=(
            GeneratedSymbol(cell_ref="Inputs!A1", symbol_name="inputs_a1", kind="input"),
            GeneratedSymbol(cell_ref="Inputs!A2", symbol_name="inputs_a2", kind="input"),
            GeneratedSymbol(cell_ref="Calc!B1", symbol_name="calc_b1", kind="output", raw_formula="=FALSE"),
            GeneratedSymbol(cell_ref="Calc!B2", symbol_name="calc_b2", kind="output", raw_formula="=-A1"),
            GeneratedSymbol(cell_ref="Calc!B3", symbol_name="calc_b3", kind="output", raw_formula="=A1^2"),
            GeneratedSymbol(cell_ref="Calc!B4", symbol_name="calc_b4", kind="output", raw_formula='=A2&"y"'),
        ),
    )
    expressions = {
        "Calc!B1": formula_expression("Calc!B1", "=FALSE", FormulaExpressionNode.literal(False)),
        "Calc!B2": formula_expression(
            "Calc!B2",
            "=-A1",
            FormulaExpressionNode.unary("-", FormulaExpressionNode.reference_to(normalize_reference("Inputs!A1"))),
        ),
        "Calc!B3": formula_expression(
            "Calc!B3",
            "=A1^2",
            FormulaExpressionNode.binary(
                "^",
                FormulaExpressionNode.reference_to(normalize_reference("Inputs!A1")),
                FormulaExpressionNode.literal(2),
            ),
        ),
        "Calc!B4": formula_expression(
            "Calc!B4",
            '=A2&"y"',
            FormulaExpressionNode.binary(
                "&",
                FormulaExpressionNode.reference_to(normalize_reference("Inputs!A2")),
                FormulaExpressionNode.literal("y"),
            ),
        ),
    }
    output_path = tmp_path / "generated_operators.py"

    result = generate_python_module(
        contract=contract,
        expressions=expressions,
        constants={"Inputs!A1": 3, "Inputs!A2": "x"},
        output_path=output_path,
    )
    module = load_module(output_path)

    assert result.generated is True
    assert "**" in result.source_code
    assert "str(" in result.source_code
    assert module.calculate() == {
        "Calc!B1": False,
        "Calc!B2": -3,
        "Calc!B3": 9,
        "Calc!B4": "xy",
    }


def test_generate_python_module_renders_criteria_functions(tmp_path: Path) -> None:
    contract = GeneratedModuleContract(
        workbook_id="criteria.xlsx",
        module_name="criteria",
        input_refs=("Data!A1", "Data!A2", "Data!B1", "Data!B2"),
        output_refs=("Calc!B1", "Calc!B2", "Calc!B3", "Calc!B4"),
        symbols=(
            GeneratedSymbol(cell_ref="Data!A1", symbol_name="data_a1", kind="input"),
            GeneratedSymbol(cell_ref="Data!A2", symbol_name="data_a2", kind="input"),
            GeneratedSymbol(cell_ref="Data!B1", symbol_name="data_b1", kind="input"),
            GeneratedSymbol(cell_ref="Data!B2", symbol_name="data_b2", kind="input"),
            GeneratedSymbol(cell_ref="Calc!B1", symbol_name="calc_b1", kind="output", raw_formula="=SUMIF(A1:A2,\">1\")"),
            GeneratedSymbol(cell_ref="Calc!B2", symbol_name="calc_b2", kind="output", raw_formula="=COUNTIF(A1:A2,\">1\")"),
            GeneratedSymbol(
                cell_ref="Calc!B3",
                symbol_name="calc_b3",
                kind="output",
                raw_formula='=SUMIFS(A1:A2,B1:B2,"x")',
            ),
            GeneratedSymbol(
                cell_ref="Calc!B4",
                symbol_name="calc_b4",
                kind="output",
                raw_formula='=COUNTIFS(B1:B2,"x")',
            ),
        ),
    )
    amount_range = normalize_reference("Data!A1:A2")
    label_range = normalize_reference("Data!B1:B2")
    expressions = {
        "Calc!B1": formula_expression(
            "Calc!B1",
            '=SUMIF(A1:A2,">1")',
            FormulaExpressionNode.function_call(
                "SUMIF",
                (
                    FormulaExpressionNode.reference_to(amount_range),
                    FormulaExpressionNode.literal(">1"),
                ),
            ),
        ),
        "Calc!B2": formula_expression(
            "Calc!B2",
            '=COUNTIF(A1:A2,">1")',
            FormulaExpressionNode.function_call(
                "COUNTIF",
                (
                    FormulaExpressionNode.reference_to(amount_range),
                    FormulaExpressionNode.literal(">1"),
                ),
            ),
        ),
        "Calc!B3": formula_expression(
            "Calc!B3",
            '=SUMIFS(A1:A2,B1:B2,"x")',
            FormulaExpressionNode.function_call(
                "SUMIFS",
                (
                    FormulaExpressionNode.reference_to(amount_range),
                    FormulaExpressionNode.reference_to(label_range),
                    FormulaExpressionNode.literal("x"),
                ),
            ),
        ),
        "Calc!B4": formula_expression(
            "Calc!B4",
            '=COUNTIFS(B1:B2,"x")',
            FormulaExpressionNode.function_call(
                "COUNTIFS",
                (
                    FormulaExpressionNode.reference_to(label_range),
                    FormulaExpressionNode.literal("x"),
                ),
            ),
        ),
    }
    output_path = tmp_path / "generated_criteria.py"

    result = generate_python_module(
        contract=contract,
        expressions=expressions,
        constants={"Data!A1": 1, "Data!A2": 4, "Data!B1": "x", "Data!B2": "y"},
        output_path=output_path,
    )
    module = load_module(output_path)

    assert result.generated is True
    assert "_sf_sumif" in result.source_code
    assert module.calculate() == {
        "Calc!B1": 4,
        "Calc!B2": 1,
        "Calc!B3": 1,
        "Calc!B4": 1,
    }


def test_generate_python_module_renders_vlookup(tmp_path: Path) -> None:
    contract = GeneratedModuleContract(
        workbook_id="lookup.xlsx",
        module_name="lookup",
        input_refs=("Lookup!A1", "Lookup!A2", "Lookup!B1", "Lookup!B2"),
        output_refs=("Calc!B1", "Calc!B2"),
        symbols=(
            GeneratedSymbol(cell_ref="Lookup!A1", symbol_name="lookup_a1", kind="input"),
            GeneratedSymbol(cell_ref="Lookup!A2", symbol_name="lookup_a2", kind="input"),
            GeneratedSymbol(cell_ref="Lookup!B1", symbol_name="lookup_b1", kind="input"),
            GeneratedSymbol(cell_ref="Lookup!B2", symbol_name="lookup_b2", kind="input"),
            GeneratedSymbol(
                cell_ref="Calc!B1",
                symbol_name="calc_b1",
                kind="output",
                raw_formula="=VLOOKUP(2,Lookup!A1:B2,2,FALSE)",
            ),
            GeneratedSymbol(
                cell_ref="Calc!B2",
                symbol_name="calc_b2",
                kind="output",
                raw_formula="=VLOOKUP(1.5,Lookup!A1:B2,2,TRUE)",
            ),
        ),
    )
    table_range = normalize_reference("Lookup!A1:B2")
    expressions = {
        "Calc!B1": formula_expression(
            "Calc!B1",
            "=VLOOKUP(2,Lookup!A1:B2,2,FALSE)",
            FormulaExpressionNode.function_call(
                "VLOOKUP",
                (
                    FormulaExpressionNode.literal(2),
                    FormulaExpressionNode.reference_to(table_range),
                    FormulaExpressionNode.literal(2),
                    FormulaExpressionNode.literal(False),
                ),
            ),
        ),
        "Calc!B2": formula_expression(
            "Calc!B2",
            "=VLOOKUP(1.5,Lookup!A1:B2,2,TRUE)",
            FormulaExpressionNode.function_call(
                "VLOOKUP",
                (
                    FormulaExpressionNode.literal(1.5),
                    FormulaExpressionNode.reference_to(table_range),
                    FormulaExpressionNode.literal(2),
                    FormulaExpressionNode.literal(True),
                ),
            ),
        ),
    }
    output_path = tmp_path / "generated_lookup.py"

    result = generate_python_module(
        contract=contract,
        expressions=expressions,
        constants={"Lookup!A1": 1, "Lookup!A2": 2, "Lookup!B1": "one", "Lookup!B2": "two"},
        output_path=output_path,
    )
    module = load_module(output_path)

    assert result.generated is True
    assert "_sf_vlookup" in result.source_code
    assert "((lookup_a1, lookup_b1), (lookup_a2, lookup_b2))" in result.source_code
    assert module.calculate() == {
        "Calc!B1": "two",
        "Calc!B2": "one",
    }
