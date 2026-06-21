import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType

import pytest

from modelwright.extraction import extract_workbook
from modelwright.formulas import FormulaExpression, FormulaExpressionNode, translate_formula_cell
from modelwright.generation import (
    GeneratedModuleContract,
    GeneratedSymbol,
    GenerationResult,
    generate_python_module,
    infer_generated_module_contract,
    symbol_name_for_cell_ref,
)
from modelwright.graph import DependencyEdge, DependencyGraph, build_dependency_graph
from modelwright.references import normalize_reference
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


def test_infer_generated_module_contract_for_synthetic_outputs(tmp_path: Path) -> None:
    workbook = extract_workbook(build_workbook(tmp_path / "synthetic_model.xlsx"))
    graph = build_dependency_graph(workbook)
    formula_cells = {cell.cell_ref: cell for cell in workbook.cells if cell.formula is not None}
    expressions = {
        cell_ref: translate_formula_cell(cell, graph)
        for cell_ref, cell in formula_cells.items()
    }

    result = infer_generated_module_contract(
        workbook=workbook,
        graph=graph,
        expressions=expressions,
        output_refs=("Summary!B2", "Summary!B3"),
        module_name="synthetic_model",
    )

    assert result.inferred is True
    assert result.diagnostics == ()
    assert result.contract.input_refs == ("Inputs!B2", "Inputs!B3", "Inputs!B4")
    assert result.constants == {"Inputs!B2": 100, "Inputs!B3": 0.08, "Inputs!B4": 0.65}
    assert result.contract.include_provenance_comments is True
    assert tuple(symbol.cell_ref for symbol in result.contract.symbols) == (
        "Inputs!B2",
        "Inputs!B3",
        "Inputs!B4",
        "Calc!B2",
        "Calc!B3",
        "Calc!B4",
        "Summary!B2",
        "Summary!B3",
    )
    assert [symbol.kind for symbol in result.contract.symbols] == [
        "input",
        "input",
        "input",
        "intermediate",
        "intermediate",
        "intermediate",
        "output",
        "output",
    ]


def test_infer_generated_module_contract_disables_large_inline_provenance_comments(tmp_path: Path) -> None:
    workbook = extract_workbook(build_workbook(tmp_path / "synthetic_model.xlsx"))
    graph = build_dependency_graph(workbook)
    formula_cells = {cell.cell_ref: cell for cell in workbook.cells if cell.formula is not None}
    expressions = {
        cell_ref: translate_formula_cell(cell, graph)
        for cell_ref, cell in formula_cells.items()
    }

    result = infer_generated_module_contract(
        workbook=workbook,
        graph=graph,
        expressions=expressions,
        output_refs=("Summary!B2", "Summary!B3"),
        module_name="synthetic_model",
        inline_provenance_comment_limit=2,
    )

    assert result.inferred is True
    assert result.contract.include_provenance_comments is False
    assert any(symbol.raw_formula == "=BaseVolume*(1+GrowthRate)" for symbol in result.contract.symbols)


def test_infer_generated_module_contract_uses_expression_sources_for_large_formula_sets(tmp_path: Path) -> None:
    workbook = extract_workbook(build_workbook(tmp_path / "synthetic_model.xlsx"))
    graph = build_dependency_graph(workbook)
    formula_cells = {cell.cell_ref: cell for cell in workbook.cells if cell.formula is not None}
    expressions = {
        cell_ref: translate_formula_cell(cell, graph)
        for cell_ref, cell in formula_cells.items()
    }

    result = infer_generated_module_contract(
        workbook=workbook,
        graph=graph,
        expressions=expressions,
        output_refs=("Summary!B2", "Summary!B3"),
        module_name="synthetic_model",
        inline_formula_lambda_limit=2,
    )

    assert result.inferred is True
    assert result.contract.formula_storage == "expression_source"


def test_generate_python_module_can_omit_inline_provenance_comments(tmp_path: Path) -> None:
    contract, expressions, constants = synthetic_generation_inputs(tmp_path)
    compact_contract = GeneratedModuleContract(
        workbook_id=contract.workbook_id,
        module_name=contract.module_name,
        entrypoint=contract.entrypoint,
        input_refs=contract.input_refs,
        output_refs=contract.output_refs,
        symbols=contract.symbols,
        include_provenance_comments=False,
    )
    output_path = tmp_path / "generated_compact_model.py"

    result = generate_python_module(
        contract=compact_contract,
        expressions=expressions,
        constants=constants,
        output_path=output_path,
    )
    module = load_module(output_path)

    assert result.generated is True
    assert "# Calc!B2: =BaseVolume*(1+GrowthRate)" not in result.source_code
    assert module.calculate() == {"Summary!B2": 70.2, "Summary!B3": "ok"}


def test_generate_python_module_can_store_formula_expression_sources(tmp_path: Path) -> None:
    contract, expressions, constants = synthetic_generation_inputs(tmp_path)
    compact_contract = GeneratedModuleContract(
        workbook_id=contract.workbook_id,
        module_name=contract.module_name,
        entrypoint=contract.entrypoint,
        input_refs=contract.input_refs,
        output_refs=contract.output_refs,
        symbols=contract.symbols,
        formula_storage="expression_source",
    )
    output_path = tmp_path / "generated_expression_source_model.py"

    result = generate_python_module(
        contract=compact_contract,
        expressions=expressions,
        constants=constants,
        output_path=output_path,
    )
    module = load_module(output_path)

    assert result.generated is True
    assert "    def _evaluate_formula(cell_ref, formula):" in result.source_code
    assert "compile(formula, f'<modelwright formula {cell_ref}>', 'eval')" in result.source_code
    assert "_formula_code_cache" not in result.source_code
    assert "lambda: _sf_direct_reference" not in result.source_code
    assert module.calculate() == {"Summary!B2": 70.2, "Summary!B3": "ok"}
    assert module.calculate({"Inputs!B2": 10}) == {"Summary!B2": 7.02, "Summary!B3": "low"}


def test_infer_generated_module_contract_ignores_unreached_dependency_diagnostics(tmp_path: Path) -> None:
    workbook = extract_workbook(build_workbook(tmp_path / "synthetic_model.xlsx"))
    graph = build_dependency_graph(workbook)
    graph = DependencyGraph(
        workbook_id=graph.workbook_id,
        edges=graph.edges
        + (
            DependencyEdge(
                source=normalize_reference("Inputs!B2:B3"),
                target=normalize_reference("Inputs!A1"),
                edge_kind="execution",
                raw_reference="Inputs!B2:B3",
            ),
        ),
        diagnostics=graph.diagnostics,
    )
    formula_cells = {cell.cell_ref: cell for cell in workbook.cells if cell.formula is not None}
    expressions = {
        cell_ref: translate_formula_cell(cell, graph)
        for cell_ref, cell in formula_cells.items()
    }

    result = infer_generated_module_contract(
        workbook=workbook,
        graph=graph,
        expressions=expressions,
        output_refs=("Summary!B2", "Summary!B3"),
        module_name="synthetic_model",
    )

    assert result.inferred is True
    assert result.diagnostics == ()


def test_infer_generated_module_contract_treats_missing_dependency_cells_as_blank_inputs(tmp_path: Path) -> None:
    workbook = extract_workbook(build_workbook(tmp_path / "synthetic_model.xlsx"))
    graph = build_dependency_graph(workbook)
    graph = DependencyGraph(
        workbook_id=graph.workbook_id,
        edges=graph.edges
        + (
            DependencyEdge(
                source=normalize_reference("Inputs!Z99"),
                target=normalize_reference("Summary!B2"),
                edge_kind="execution",
                raw_reference="Inputs!Z99",
            ),
        ),
        diagnostics=graph.diagnostics,
    )
    formula_cells = {cell.cell_ref: cell for cell in workbook.cells if cell.formula is not None}
    expressions = {
        cell_ref: translate_formula_cell(cell, graph)
        for cell_ref, cell in formula_cells.items()
    }

    result = infer_generated_module_contract(
        workbook=workbook,
        graph=graph,
        expressions=expressions,
        output_refs=("Summary!B2",),
        module_name="synthetic_model",
    )

    assert result.inferred is True
    assert result.diagnostics == ()
    assert "Inputs!Z99" in result.contract.input_refs
    assert result.constants["Inputs!Z99"] is None


def test_infer_generated_module_contract_expands_range_dependency_sources(tmp_path: Path) -> None:
    workbook = extract_workbook(build_workbook(tmp_path / "synthetic_model.xlsx"))
    graph = build_dependency_graph(workbook)
    graph = DependencyGraph(
        workbook_id=graph.workbook_id,
        edges=graph.edges
        + (
            DependencyEdge(
                source=normalize_reference("Inputs!Z1:Z2"),
                target=normalize_reference("Summary!B2"),
                edge_kind="execution",
                raw_reference="Inputs!Z1:Z2",
            ),
        ),
        diagnostics=graph.diagnostics,
    )
    formula_cells = {cell.cell_ref: cell for cell in workbook.cells if cell.formula is not None}
    expressions = {
        cell_ref: translate_formula_cell(cell, graph)
        for cell_ref, cell in formula_cells.items()
    }

    result = infer_generated_module_contract(
        workbook=workbook,
        graph=graph,
        expressions=expressions,
        output_refs=("Summary!B2",),
        module_name="synthetic_model",
    )

    assert result.inferred is True
    assert result.diagnostics == ()
    assert "Inputs!Z1" in result.contract.input_refs
    assert "Inputs!Z2" in result.contract.input_refs
    assert result.constants["Inputs!Z1"] is None
    assert result.constants["Inputs!Z2"] is None


def test_infer_generated_module_contract_deduplicates_cycle_diagnostics(tmp_path: Path) -> None:
    workbook = extract_workbook(build_workbook(tmp_path / "synthetic_model.xlsx"))
    graph = build_dependency_graph(workbook)
    graph = DependencyGraph(
        workbook_id=graph.workbook_id,
        edges=graph.edges
        + (
            DependencyEdge(
                source=normalize_reference("Summary!B2"),
                target=normalize_reference("Summary!B3"),
                edge_kind="execution",
                raw_reference="Summary!B2",
            ),
            DependencyEdge(
                source=normalize_reference("Summary!B3"),
                target=normalize_reference("Summary!B2"),
                edge_kind="execution",
                raw_reference="Summary!B3",
            ),
        ),
        diagnostics=graph.diagnostics,
    )
    formula_cells = {cell.cell_ref: cell for cell in workbook.cells if cell.formula is not None}
    expressions = {
        cell_ref: translate_formula_cell(cell, graph)
        for cell_ref, cell in formula_cells.items()
    }

    result = infer_generated_module_contract(
        workbook=workbook,
        graph=graph,
        expressions=expressions,
        output_refs=("Summary!B2", "Summary!B3"),
        module_name="synthetic_model",
    )

    assert result.inferred is True
    assert [(diagnostic.code, diagnostic.severity, diagnostic.location) for diagnostic in result.diagnostics] == [
        ("static_circular_dependency", "warning", "Summary!B2")
    ]


def test_inferred_generated_module_runs_synthetic_model(tmp_path: Path) -> None:
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
    output_path = tmp_path / "generated_model.py"

    generation = generate_python_module(
        contract=inference.contract,
        expressions=inference.expressions,
        constants=inference.constants,
        output_path=output_path,
    )
    module = load_module(output_path)

    assert generation.generated is True
    assert "    _output_refs = (" in generation.source_code
    assert "    return {cell_ref: _get(cell_ref) for cell_ref in _output_refs}" in generation.source_code
    assert module.calculate() == {"Summary!B2": 70.2, "Summary!B3": "ok"}
    assert module.calculate({"Inputs!B2": 10}) == {"Summary!B2": 7.02, "Summary!B3": "low"}


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
        input_refs=("Data!A1", "Data!A2", "Data!B1", "Data!B2", "Data!C1", "Data!C2", "Data!D1", "Data!D2"),
        output_refs=(
            "Calc!B1",
            "Calc!B2",
            "Calc!B3",
            "Calc!B4",
            "Calc!B5",
            "Calc!B6",
            "Calc!B7",
            "Calc!B8",
            "Calc!B9",
        ),
        symbols=(
            GeneratedSymbol(cell_ref="Data!A1", symbol_name="data_a1", kind="input"),
            GeneratedSymbol(cell_ref="Data!A2", symbol_name="data_a2", kind="input"),
            GeneratedSymbol(cell_ref="Data!B1", symbol_name="data_b1", kind="input"),
            GeneratedSymbol(cell_ref="Data!B2", symbol_name="data_b2", kind="input"),
            GeneratedSymbol(cell_ref="Data!C1", symbol_name="data_c1", kind="input"),
            GeneratedSymbol(cell_ref="Data!C2", symbol_name="data_c2", kind="input"),
            GeneratedSymbol(cell_ref="Data!D1", symbol_name="data_d1", kind="input"),
            GeneratedSymbol(cell_ref="Data!D2", symbol_name="data_d2", kind="input"),
            GeneratedSymbol(cell_ref="Calc!B1", symbol_name="calc_b1", kind="output", raw_formula="=SUMIF(A1:A2,\">1\")"),
            GeneratedSymbol(cell_ref="Calc!B2", symbol_name="calc_b2", kind="output", raw_formula="=COUNTIF(A1:A2,\">1\")"),
            GeneratedSymbol(
                cell_ref="Calc!B3",
                symbol_name="calc_b3",
                kind="output",
                raw_formula='=SUMIFS(A1:A2,B1:B2,"Corn")',
            ),
            GeneratedSymbol(
                cell_ref="Calc!B4",
                symbol_name="calc_b4",
                kind="output",
                raw_formula='=COUNTIFS(B1:B2,"Corn")',
            ),
            GeneratedSymbol(
                cell_ref="Calc!B5",
                symbol_name="calc_b5",
                kind="output",
                raw_formula='=SUMIFS(A1:A2,A1:A2,"4")',
            ),
            GeneratedSymbol(
                cell_ref="Calc!B6",
                symbol_name="calc_b6",
                kind="output",
                raw_formula='=COUNTIFS(B1:B2,"c*")',
            ),
            GeneratedSymbol(
                cell_ref="Calc!B7",
                symbol_name="calc_b7",
                kind="output",
                raw_formula='=COUNTIFS(C1:C2,"2010")',
            ),
            GeneratedSymbol(
                cell_ref="Calc!B8",
                symbol_name="calc_b8",
                kind="output",
                raw_formula='=SUMIFS(D1:D2,B1:B2,"Corn")',
            ),
            GeneratedSymbol(
                cell_ref="Calc!B9",
                symbol_name="calc_b9",
                kind="output",
                raw_formula="=COUNTIFS(C1:C2,2010)",
            ),
        ),
    )
    amount_range = normalize_reference("Data!A1:A2")
    label_range = normalize_reference("Data!B1:B2")
    year_text_range = normalize_reference("Data!C1:C2")
    mixed_sum_range = normalize_reference("Data!D1:D2")
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
            '=SUMIFS(A1:A2,B1:B2,"Corn")',
            FormulaExpressionNode.function_call(
                "SUMIFS",
                (
                    FormulaExpressionNode.reference_to(amount_range),
                    FormulaExpressionNode.reference_to(label_range),
                    FormulaExpressionNode.literal("Corn"),
                ),
            ),
        ),
        "Calc!B4": formula_expression(
            "Calc!B4",
            '=COUNTIFS(B1:B2,"Corn")',
            FormulaExpressionNode.function_call(
                "COUNTIFS",
                (
                    FormulaExpressionNode.reference_to(label_range),
                    FormulaExpressionNode.literal("Corn"),
                ),
            ),
        ),
        "Calc!B5": formula_expression(
            "Calc!B5",
            '=SUMIFS(A1:A2,A1:A2,"4")',
            FormulaExpressionNode.function_call(
                "SUMIFS",
                (
                    FormulaExpressionNode.reference_to(amount_range),
                    FormulaExpressionNode.reference_to(amount_range),
                    FormulaExpressionNode.literal("4"),
                ),
            ),
        ),
        "Calc!B6": formula_expression(
            "Calc!B6",
            '=COUNTIFS(B1:B2,"c*")',
            FormulaExpressionNode.function_call(
                "COUNTIFS",
                (
                    FormulaExpressionNode.reference_to(label_range),
                    FormulaExpressionNode.literal("c*"),
                ),
            ),
        ),
        "Calc!B7": formula_expression(
            "Calc!B7",
            '=COUNTIFS(C1:C2,"2010")',
            FormulaExpressionNode.function_call(
                "COUNTIFS",
                (
                    FormulaExpressionNode.reference_to(year_text_range),
                    FormulaExpressionNode.literal("2010"),
                ),
            ),
        ),
        "Calc!B8": formula_expression(
            "Calc!B8",
            '=SUMIFS(D1:D2,B1:B2,"Corn")',
            FormulaExpressionNode.function_call(
                "SUMIFS",
                (
                    FormulaExpressionNode.reference_to(mixed_sum_range),
                    FormulaExpressionNode.reference_to(label_range),
                    FormulaExpressionNode.literal("Corn"),
                ),
            ),
        ),
        "Calc!B9": formula_expression(
            "Calc!B9",
            "=COUNTIFS(C1:C2,2010)",
            FormulaExpressionNode.function_call(
                "COUNTIFS",
                (
                    FormulaExpressionNode.reference_to(year_text_range),
                    FormulaExpressionNode.literal(2010),
                ),
            ),
        ),
    }
    output_path = tmp_path / "generated_criteria.py"

    result = generate_python_module(
        contract=contract,
        expressions=expressions,
        constants={
            "Data!A1": 1,
            "Data!A2": 4,
            "Data!B1": "corn",
            "Data!B2": "Corn",
            "Data!C1": "2010",
            "Data!C2": "2000",
            "Data!D1": "ignored",
            "Data!D2": 4,
        },
        output_path=output_path,
    )
    module = load_module(output_path)

    assert result.generated is True
    assert "_sf_sumif" in result.source_code
    assert "_sf_criteria_matcher" in result.source_code
    assert "class _SfRangeView" in result.source_code
    assert "_range_cache = {}" in result.source_code
    assert module.calculate() == {
        "Calc!B1": 4,
        "Calc!B2": 1,
        "Calc!B3": 5,
        "Calc!B4": 2,
        "Calc!B5": 4,
        "Calc!B6": 1,
        "Calc!B7": 1,
        "Calc!B8": 4,
        "Calc!B9": 1,
    }


def test_generate_python_module_treats_blank_arithmetic_operands_as_zero(tmp_path: Path) -> None:
    contract = GeneratedModuleContract(
        workbook_id="blank-arithmetic.xlsx",
        module_name="blank_arithmetic",
        input_refs=("Data!A1",),
        output_refs=("Calc!B1",),
        symbols=(
            GeneratedSymbol(cell_ref="Data!A1", symbol_name="data_a1", kind="input"),
            GeneratedSymbol(
                cell_ref="Calc!B1",
                symbol_name="calc_b1",
                kind="output",
                raw_formula="=Data!A1+Data!B1",
            ),
        ),
    )
    expressions = {
        "Calc!B1": formula_expression(
            "Calc!B1",
            "=Data!A1+Data!B1",
            FormulaExpressionNode.binary(
                "+",
                FormulaExpressionNode.reference_to(normalize_reference("Data!A1")),
                FormulaExpressionNode.reference_to(normalize_reference("Data!B1")),
            ),
        ),
    }
    output_path = tmp_path / "generated_blank_arithmetic.py"

    result = generate_python_module(
        contract=contract,
        expressions=expressions,
        constants={"Data!A1": 3},
        output_path=output_path,
    )
    module = load_module(output_path)

    assert result.generated is True
    assert module.calculate() == {"Calc!B1": 3}


def test_generate_python_module_treats_direct_blank_reference_as_zero(tmp_path: Path) -> None:
    contract = GeneratedModuleContract(
        workbook_id="blank-reference.xlsx",
        module_name="blank_reference",
        input_refs=("Data!B1",),
        output_refs=("Calc!A1",),
        symbols=(
            GeneratedSymbol(cell_ref="Data!B1", symbol_name="data_b1", kind="input"),
            GeneratedSymbol(
                cell_ref="Calc!A1",
                symbol_name="calc_a1",
                kind="output",
                raw_formula="=Data!B1",
            ),
        ),
    )
    expressions = {
        "Calc!A1": formula_expression(
            "Calc!A1",
            "=Data!B1",
            FormulaExpressionNode.reference_to(normalize_reference("Data!B1")),
        ),
    }
    output_path = tmp_path / "generated_blank_reference.py"

    result = generate_python_module(
        contract=contract,
        expressions=expressions,
        constants={"Data!B1": None},
        output_path=output_path,
    )
    module = load_module(output_path)

    assert result.generated is True
    assert module.calculate() == {"Calc!A1": 0}


def test_generate_python_module_treats_blank_scalar_references_as_zero_in_functions(tmp_path: Path) -> None:
    contract = GeneratedModuleContract(
        workbook_id="blank-function-references.xlsx",
        module_name="blank_function_references",
        input_refs=("Data!A1", "Data!B1", "Lookup!A1", "Lookup!B1"),
        output_refs=("Calc!A1", "Calc!A2", "Calc!A3"),
        symbols=(
            GeneratedSymbol(cell_ref="Data!A1", symbol_name="data_a1", kind="input"),
            GeneratedSymbol(cell_ref="Data!B1", symbol_name="data_b1", kind="input"),
            GeneratedSymbol(cell_ref="Lookup!A1", symbol_name="lookup_a1", kind="input"),
            GeneratedSymbol(cell_ref="Lookup!B1", symbol_name="lookup_b1", kind="input"),
            GeneratedSymbol(
                cell_ref="Calc!A1",
                symbol_name="calc_a1",
                kind="output",
                raw_formula='=IF(Data!A1<>"NA",Data!A1,0)',
            ),
            GeneratedSymbol(
                cell_ref="Calc!A2",
                symbol_name="calc_a2",
                kind="output",
                raw_formula="=IFERROR(Data!B1,0)",
            ),
            GeneratedSymbol(
                cell_ref="Calc!A3",
                symbol_name="calc_a3",
                kind="output",
                raw_formula='=VLOOKUP("x",Lookup!A1:B1,2,FALSE)',
            ),
        ),
    )
    lookup_range = normalize_reference("Lookup!A1:B1")
    expressions = {
        "Calc!A1": formula_expression(
            "Calc!A1",
            '=IF(Data!A1<>"NA",Data!A1,0)',
            FormulaExpressionNode.function_call(
                "IF",
                (
                    FormulaExpressionNode.comparison(
                        "<>",
                        FormulaExpressionNode.reference_to(normalize_reference("Data!A1")),
                        FormulaExpressionNode.literal("NA"),
                    ),
                    FormulaExpressionNode.reference_to(normalize_reference("Data!A1")),
                    FormulaExpressionNode.literal(0),
                ),
            ),
        ),
        "Calc!A2": formula_expression(
            "Calc!A2",
            "=IFERROR(Data!B1,0)",
            FormulaExpressionNode.function_call(
                "IFERROR",
                (
                    FormulaExpressionNode.reference_to(normalize_reference("Data!B1")),
                    FormulaExpressionNode.literal(0),
                ),
            ),
        ),
        "Calc!A3": formula_expression(
            "Calc!A3",
            '=VLOOKUP("x",Lookup!A1:B1,2,FALSE)',
            FormulaExpressionNode.function_call(
                "VLOOKUP",
                (
                    FormulaExpressionNode.literal("x"),
                    FormulaExpressionNode.reference_to(lookup_range),
                    FormulaExpressionNode.literal(2),
                    FormulaExpressionNode.literal(False),
                ),
            ),
        ),
    }
    output_path = tmp_path / "generated_blank_function_references.py"

    result = generate_python_module(
        contract=contract,
        expressions=expressions,
        constants={"Data!A1": None, "Data!B1": None, "Lookup!A1": "x", "Lookup!B1": None},
        output_path=output_path,
    )
    module = load_module(output_path)

    assert result.generated is True
    assert module.calculate() == {"Calc!A1": 0, "Calc!A2": 0, "Calc!A3": 0}


def test_generate_python_module_renders_vlookup(tmp_path: Path) -> None:
    contract = GeneratedModuleContract(
        workbook_id="lookup.xlsx",
        module_name="lookup",
        input_refs=("Lookup!A1", "Lookup!A2", "Lookup!B1", "Lookup!B2", "Lookup!C1", "Lookup!D1"),
        output_refs=("Calc!B1", "Calc!B2", "Calc!B3"),
        symbols=(
            GeneratedSymbol(cell_ref="Lookup!A1", symbol_name="lookup_a1", kind="input"),
            GeneratedSymbol(cell_ref="Lookup!A2", symbol_name="lookup_a2", kind="input"),
            GeneratedSymbol(cell_ref="Lookup!B1", symbol_name="lookup_b1", kind="input"),
            GeneratedSymbol(cell_ref="Lookup!B2", symbol_name="lookup_b2", kind="input"),
            GeneratedSymbol(cell_ref="Lookup!C1", symbol_name="lookup_c1", kind="input"),
            GeneratedSymbol(cell_ref="Lookup!D1", symbol_name="lookup_d1", kind="input"),
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
            GeneratedSymbol(
                cell_ref="Calc!B3",
                symbol_name="calc_b3",
                kind="output",
                raw_formula='=VLOOKUP("X",Lookup!C1:D1,2,FALSE)',
            ),
        ),
    )
    table_range = normalize_reference("Lookup!A1:B2")
    string_table_range = normalize_reference("Lookup!C1:D1")
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
        "Calc!B3": formula_expression(
            "Calc!B3",
            '=VLOOKUP("X",Lookup!C1:D1,2,FALSE)',
            FormulaExpressionNode.function_call(
                "VLOOKUP",
                (
                    FormulaExpressionNode.literal("X"),
                    FormulaExpressionNode.reference_to(string_table_range),
                    FormulaExpressionNode.literal(2),
                    FormulaExpressionNode.literal(False),
                ),
            ),
        ),
    }
    output_path = tmp_path / "generated_lookup.py"

    result = generate_python_module(
        contract=contract,
        expressions=expressions,
        constants={
            "Lookup!A1": 1,
            "Lookup!A2": 2,
            "Lookup!B1": "one",
            "Lookup!B2": "two",
            "Lookup!C1": "x",
            "Lookup!D1": "string-one",
        },
        output_path=output_path,
    )
    module = load_module(output_path)

    assert result.generated is True
    assert "_sf_vlookup" in result.source_code
    assert "_table('Lookup', 1, 1, 2, 2)" in result.source_code
    assert module.calculate() == {
        "Calc!B1": "two",
        "Calc!B2": "one",
        "Calc!B3": "string-one",
    }


def test_generate_python_module_renders_ifna_for_lookup_errors(tmp_path: Path) -> None:
    contract = GeneratedModuleContract(
        workbook_id="ifna.xlsx",
        module_name="ifna",
        input_refs=("Lookup!A1", "Lookup!B1"),
        output_refs=("Calc!B1", "Calc!B2"),
        symbols=(
            GeneratedSymbol(cell_ref="Lookup!A1", symbol_name="lookup_a1", kind="input"),
            GeneratedSymbol(cell_ref="Lookup!B1", symbol_name="lookup_b1", kind="input"),
            GeneratedSymbol(cell_ref="Calc!B1", symbol_name="calc_b1", kind="output", raw_formula="=IFNA(VLOOKUP(...),\"missing\")"),
            GeneratedSymbol(cell_ref="Calc!B2", symbol_name="calc_b2", kind="output", raw_formula="=IFNA(A1,\"missing\")"),
        ),
    )
    table_range = normalize_reference("Lookup!A1:B1")
    expressions = {
        "Calc!B1": formula_expression(
            "Calc!B1",
            '=IFNA(VLOOKUP(9,Lookup!A1:B1,2,FALSE),"missing")',
            FormulaExpressionNode.function_call(
                "IFNA",
                (
                    FormulaExpressionNode.function_call(
                        "VLOOKUP",
                        (
                            FormulaExpressionNode.literal(9),
                            FormulaExpressionNode.reference_to(table_range),
                            FormulaExpressionNode.literal(2),
                            FormulaExpressionNode.literal(False),
                        ),
                    ),
                    FormulaExpressionNode.literal("missing"),
                ),
            ),
        ),
        "Calc!B2": formula_expression(
            "Calc!B2",
            '=IFNA(A1,"missing")',
            FormulaExpressionNode.function_call(
                "IFNA",
                (
                    FormulaExpressionNode.reference_to(normalize_reference("Lookup!A1")),
                    FormulaExpressionNode.literal("missing"),
                ),
            ),
        ),
    }
    output_path = tmp_path / "generated_ifna.py"

    result = generate_python_module(
        contract=contract,
        expressions=expressions,
        constants={"Lookup!A1": 1, "Lookup!B1": "one"},
        output_path=output_path,
    )
    module = load_module(output_path)

    assert result.generated is True
    assert "_sf_ifna" in result.source_code
    assert module.calculate() == {
        "Calc!B1": "missing",
        "Calc!B2": 1,
    }


def test_generate_python_module_renders_if_with_omitted_false_branch(tmp_path: Path) -> None:
    contract = GeneratedModuleContract(
        workbook_id="if.xlsx",
        module_name="if_optional_false",
        input_refs=("Inputs!A1",),
        output_refs=("Calc!B1",),
        symbols=(
            GeneratedSymbol(cell_ref="Inputs!A1", symbol_name="inputs_a1", kind="input"),
            GeneratedSymbol(cell_ref="Calc!B1", symbol_name="calc_b1", kind="output", raw_formula='=IF(A1>0,"yes")'),
        ),
    )
    expressions = {
        "Calc!B1": formula_expression(
            "Calc!B1",
            '=IF(A1>0,"yes")',
            FormulaExpressionNode.function_call(
                "IF",
                (
                    FormulaExpressionNode.comparison(
                        ">",
                        FormulaExpressionNode.reference_to(normalize_reference("Inputs!A1")),
                        FormulaExpressionNode.literal(0),
                    ),
                    FormulaExpressionNode.literal("yes"),
                ),
            ),
        ),
    }
    output_path = tmp_path / "generated_if_optional_false.py"

    result = generate_python_module(
        contract=contract,
        expressions=expressions,
        constants={"Inputs!A1": 0},
        output_path=output_path,
    )
    module = load_module(output_path)

    assert result.generated is True
    assert module.calculate({"Inputs!A1": 1}) == {"Calc!B1": "yes"}
    assert module.calculate({"Inputs!A1": 0}) == {"Calc!B1": False}


def test_generate_python_module_renders_case_insensitive_text_equality(tmp_path: Path) -> None:
    contract = GeneratedModuleContract(
        workbook_id="text-comparison.xlsx",
        module_name="text_comparison",
        input_refs=("Inputs!A1",),
        output_refs=("Calc!B1", "Calc!B2"),
        symbols=(
            GeneratedSymbol(cell_ref="Inputs!A1", symbol_name="inputs_a1", kind="input"),
            GeneratedSymbol(
                cell_ref="Calc!B1",
                symbol_name="calc_b1",
                kind="output",
                raw_formula='=IF(A1="EatLancetAverage",1,0)',
            ),
            GeneratedSymbol(
                cell_ref="Calc!B2",
                symbol_name="calc_b2",
                kind="output",
                raw_formula='=IF(A1<>"EatLancetAverage",1,0)',
            ),
        ),
    )
    expressions = {
        "Calc!B1": formula_expression(
            "Calc!B1",
            '=IF(A1="EatLancetAverage",1,0)',
            FormulaExpressionNode.function_call(
                "IF",
                (
                    FormulaExpressionNode.comparison(
                        "=",
                        FormulaExpressionNode.reference_to(normalize_reference("Inputs!A1")),
                        FormulaExpressionNode.literal("EatLancetAverage"),
                    ),
                    FormulaExpressionNode.literal(1),
                    FormulaExpressionNode.literal(0),
                ),
            ),
        ),
        "Calc!B2": formula_expression(
            "Calc!B2",
            '=IF(A1<>"EatLancetAverage",1,0)',
            FormulaExpressionNode.function_call(
                "IF",
                (
                    FormulaExpressionNode.comparison(
                        "<>",
                        FormulaExpressionNode.reference_to(normalize_reference("Inputs!A1")),
                        FormulaExpressionNode.literal("EatLancetAverage"),
                    ),
                    FormulaExpressionNode.literal(1),
                    FormulaExpressionNode.literal(0),
                ),
            ),
        ),
    }
    output_path = tmp_path / "generated_text_comparison.py"

    result = generate_python_module(
        contract=contract,
        expressions=expressions,
        constants={"Inputs!A1": "EATLancetAverage"},
        output_path=output_path,
    )
    module = load_module(output_path)

    assert result.generated is True
    assert module.calculate() == {"Calc!B1": 1, "Calc!B2": 0}


def test_generate_python_module_skips_unselected_if_cycle_branch(tmp_path: Path) -> None:
    contract = GeneratedModuleContract(
        workbook_id="lazy_if.xlsx",
        module_name="lazy_if",
        input_refs=("Inputs!A1",),
        output_refs=("Calc!B1",),
        symbols=(
            GeneratedSymbol(cell_ref="Inputs!A1", symbol_name="inputs_a1", kind="input"),
            GeneratedSymbol(cell_ref="Calc!B1", symbol_name="calc_b1", kind="output", raw_formula="=IF(A1>0,C1,7)"),
            GeneratedSymbol(cell_ref="Calc!C1", symbol_name="calc_c1", kind="intermediate", raw_formula="=B1+1"),
        ),
    )
    expressions = {
        "Calc!B1": formula_expression(
            "Calc!B1",
            "=IF(A1>0,C1,7)",
            FormulaExpressionNode.function_call(
                "IF",
                (
                    FormulaExpressionNode.comparison(
                        ">",
                        FormulaExpressionNode.reference_to(normalize_reference("Inputs!A1")),
                        FormulaExpressionNode.literal(0),
                    ),
                    FormulaExpressionNode.reference_to(normalize_reference("Calc!C1")),
                    FormulaExpressionNode.literal(7),
                ),
            ),
        ),
        "Calc!C1": formula_expression(
            "Calc!C1",
            "=B1+1",
            FormulaExpressionNode.binary(
                "+",
                FormulaExpressionNode.reference_to(normalize_reference("Calc!B1")),
                FormulaExpressionNode.literal(1),
            ),
        ),
    }
    output_path = tmp_path / "generated_lazy_if.py"

    result = generate_python_module(
        contract=contract,
        expressions=expressions,
        constants={"Inputs!A1": 0},
        output_path=output_path,
    )
    module = load_module(output_path)

    assert result.generated is True
    assert module.calculate() == {"Calc!B1": 7}
    with pytest.raises(RuntimeError, match="Calc!B1 -> Calc!C1 -> Calc!B1"):
        module.calculate({"Inputs!A1": 1})


def test_generate_python_module_skips_excluded_sumifs_sum_cells(tmp_path: Path) -> None:
    contract = GeneratedModuleContract(
        workbook_id="lazy_sumifs.xlsx",
        module_name="lazy_sumifs",
        input_refs=("Data!A1", "Data!B1", "Data!B2"),
        output_refs=("Calc!C1",),
        symbols=(
            GeneratedSymbol(cell_ref="Data!A1", symbol_name="data_a1", kind="input"),
            GeneratedSymbol(cell_ref="Data!B1", symbol_name="data_b1", kind="input"),
            GeneratedSymbol(cell_ref="Data!B2", symbol_name="data_b2", kind="input"),
            GeneratedSymbol(cell_ref="Data!A2", symbol_name="data_a2", kind="intermediate", raw_formula="=A2+1"),
            GeneratedSymbol(cell_ref="Calc!C1", symbol_name="calc_c1", kind="output", raw_formula='=SUMIFS(A1:A2,B1:B2,"x")'),
        ),
    )
    amount_range = normalize_reference("Data!A1:A2")
    label_range = normalize_reference("Data!B1:B2")
    expressions = {
        "Data!A2": formula_expression(
            "Data!A2",
            "=A2+1",
            FormulaExpressionNode.binary(
                "+",
                FormulaExpressionNode.reference_to(normalize_reference("Data!A2")),
                FormulaExpressionNode.literal(1),
            ),
        ),
        "Calc!C1": formula_expression(
            "Calc!C1",
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
    }
    output_path = tmp_path / "generated_lazy_sumifs.py"

    result = generate_python_module(
        contract=contract,
        expressions=expressions,
        constants={"Data!A1": 5, "Data!B1": "x", "Data!B2": "y"},
        output_path=output_path,
    )
    module = load_module(output_path)

    assert result.generated is True
    assert module.calculate() == {"Calc!C1": 5}
    with pytest.raises(RuntimeError, match="Data!A2 -> Data!A2"):
        module.calculate({"Data!B1": "skip", "Data!B2": "x"})


def test_generate_python_module_reuses_range_views_without_changing_results(tmp_path: Path) -> None:
    contract = GeneratedModuleContract(
        workbook_id="range-cache.xlsx",
        module_name="range_cache",
        input_refs=("Data!A1", "Data!A2", "Data!B1", "Data!B2"),
        output_refs=("Calc!C1", "Calc!C2", "Calc!C3"),
        symbols=(
            GeneratedSymbol(cell_ref="Data!A1", symbol_name="data_a1", kind="input"),
            GeneratedSymbol(cell_ref="Data!A2", symbol_name="data_a2", kind="input"),
            GeneratedSymbol(cell_ref="Data!B1", symbol_name="data_b1", kind="input"),
            GeneratedSymbol(cell_ref="Data!B2", symbol_name="data_b2", kind="input"),
            GeneratedSymbol(cell_ref="Calc!C1", symbol_name="calc_c1", kind="output", raw_formula='=SUMIFS(A1:A2,B1:B2,"x")'),
            GeneratedSymbol(cell_ref="Calc!C2", symbol_name="calc_c2", kind="output", raw_formula='=SUMIFS(A1:A2,B1:B2,"y")'),
            GeneratedSymbol(cell_ref="Calc!C3", symbol_name="calc_c3", kind="output", raw_formula='=COUNTIFS(B1:B2,"x")'),
        ),
    )
    amount_range = normalize_reference("Data!A1:A2")
    label_range = normalize_reference("Data!B1:B2")
    expressions = {
        "Calc!C1": formula_expression(
            "Calc!C1",
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
        "Calc!C2": formula_expression(
            "Calc!C2",
            '=SUMIFS(A1:A2,B1:B2,"y")',
            FormulaExpressionNode.function_call(
                "SUMIFS",
                (
                    FormulaExpressionNode.reference_to(amount_range),
                    FormulaExpressionNode.reference_to(label_range),
                    FormulaExpressionNode.literal("y"),
                ),
            ),
        ),
        "Calc!C3": formula_expression(
            "Calc!C3",
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
    output_path = tmp_path / "generated_range_cache.py"

    result = generate_python_module(
        contract=contract,
        expressions=expressions,
        constants={"Data!A1": 2, "Data!A2": 5, "Data!B1": "x", "Data!B2": "y"},
        output_path=output_path,
    )
    module = load_module(output_path)

    assert result.generated is True
    assert "_range_cache.get(key)" in result.source_code
    assert "def values(self):" in result.source_code
    assert "def lazy_values(self):" in result.source_code
    assert module.calculate() == {"Calc!C1": 2, "Calc!C2": 5, "Calc!C3": 1}
