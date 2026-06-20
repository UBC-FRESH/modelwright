"""Generated Python module contracts."""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

from openpyxl.utils.cell import get_column_letter, range_boundaries

from sheetforge.formulas import FormulaExpression, FormulaExpressionNode


JsonValue = str | int | float | bool | None | list[Any] | dict[str, Any]
DiagnosticSeverity = Literal["info", "warning", "error"]
GeneratedSymbolKind = Literal["input", "intermediate", "output"]


@dataclass(frozen=True)
class GenerationDiagnostic:
    """Generation concern tied to workbook or generated-code provenance."""

    code: str
    message: str
    severity: DiagnosticSeverity = "warning"
    location: str | None = None
    raw_value: JsonValue = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "GenerationDiagnostic":
        return cls(
            code=data["code"],
            message=data["message"],
            severity=data.get("severity", "warning"),
            location=data.get("location"),
            raw_value=data.get("raw_value"),
        )

    def to_dict(self) -> dict[str, JsonValue]:
        return {
            "code": self.code,
            "message": self.message,
            "severity": self.severity,
            "location": self.location,
            "raw_value": self.raw_value,
        }


@dataclass(frozen=True)
class GeneratedSymbol:
    """Generated Python symbol tied back to workbook provenance."""

    cell_ref: str
    symbol_name: str
    kind: GeneratedSymbolKind
    raw_formula: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "GeneratedSymbol":
        return cls(
            cell_ref=data["cell_ref"],
            symbol_name=data["symbol_name"],
            kind=data["kind"],
            raw_formula=data.get("raw_formula"),
        )

    def to_dict(self) -> dict[str, JsonValue]:
        return {
            "cell_ref": self.cell_ref,
            "symbol_name": self.symbol_name,
            "kind": self.kind,
            "raw_formula": self.raw_formula,
        }


@dataclass(frozen=True)
class GeneratedModuleContract:
    """Contract for one generated standalone Python module."""

    workbook_id: str
    module_name: str
    entrypoint: str = "calculate"
    input_refs: tuple[str, ...] = field(default_factory=tuple)
    output_refs: tuple[str, ...] = field(default_factory=tuple)
    symbols: tuple[GeneratedSymbol, ...] = field(default_factory=tuple)
    include_provenance_comments: bool = True

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "GeneratedModuleContract":
        return cls(
            workbook_id=data["workbook_id"],
            module_name=data["module_name"],
            entrypoint=data.get("entrypoint", "calculate"),
            input_refs=tuple(data.get("input_refs", [])),
            output_refs=tuple(data.get("output_refs", [])),
            symbols=tuple(GeneratedSymbol.from_dict(item) for item in data.get("symbols", [])),
            include_provenance_comments=data.get("include_provenance_comments", True),
        )

    def to_dict(self) -> dict[str, JsonValue]:
        return {
            "workbook_id": self.workbook_id,
            "module_name": self.module_name,
            "entrypoint": self.entrypoint,
            "input_refs": list(self.input_refs),
            "output_refs": list(self.output_refs),
            "symbols": [symbol.to_dict() for symbol in self.symbols],
            "include_provenance_comments": self.include_provenance_comments,
        }


@dataclass(frozen=True)
class GenerationResult:
    """Result of generating one Python module."""

    contract: GeneratedModuleContract
    source_code: str = ""
    diagnostics: tuple[GenerationDiagnostic, ...] = field(default_factory=tuple)

    @property
    def generated(self) -> bool:
        return bool(self.source_code) and not any(diagnostic.severity == "error" for diagnostic in self.diagnostics)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "GenerationResult":
        return cls(
            contract=GeneratedModuleContract.from_dict(data["contract"]),
            source_code=data.get("source_code", ""),
            diagnostics=tuple(GenerationDiagnostic.from_dict(item) for item in data.get("diagnostics", [])),
        )

    def to_dict(self) -> dict[str, JsonValue]:
        return {
            "contract": self.contract.to_dict(),
            "source_code": self.source_code,
            "generated": self.generated,
            "diagnostics": [diagnostic.to_dict() for diagnostic in self.diagnostics],
        }


def symbol_name_for_cell_ref(cell_ref: str) -> str:
    """Build a stable Python identifier from a canonical workbook cell ref."""

    symbol = re.sub(r"[^0-9A-Za-z_]+", "_", cell_ref).strip("_").lower()
    if not symbol:
        return "cell"
    if symbol[0].isdigit():
        return f"cell_{symbol}"
    return symbol


def generate_python_module(
    *,
    contract: GeneratedModuleContract,
    expressions: Mapping[str, FormulaExpression],
    constants: Mapping[str, JsonValue] | None = None,
    output_path: str | Path | None = None,
) -> GenerationResult:
    """Generate standalone Python source from translated formula expressions."""

    constants = constants or {}
    diagnostics = _generation_diagnostics(contract, expressions)
    if any(diagnostic.severity == "error" for diagnostic in diagnostics):
        return GenerationResult(contract=contract, diagnostics=tuple(diagnostics))

    source_code = _render_module(contract=contract, expressions=expressions, constants=constants)
    if output_path is not None:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(source_code, encoding="utf-8")

    return GenerationResult(contract=contract, source_code=source_code, diagnostics=tuple(diagnostics))


def _generation_diagnostics(
    contract: GeneratedModuleContract,
    expressions: Mapping[str, FormulaExpression],
) -> list[GenerationDiagnostic]:
    diagnostics: list[GenerationDiagnostic] = []
    for symbol in contract.symbols:
        if symbol.kind == "input":
            continue

        expression = expressions.get(symbol.cell_ref)
        if expression is None:
            diagnostics.append(
                GenerationDiagnostic(
                    code="missing_formula_expression",
                    message="generated symbol has no translated formula expression",
                    severity="error",
                    location=symbol.cell_ref,
                    raw_value=symbol.raw_formula,
                )
            )
            continue

        if not expression.translated:
            diagnostics.append(
                GenerationDiagnostic(
                    code="unsupported_formula",
                    message="formula expression could not be generated",
                    severity="error",
                    location=symbol.cell_ref,
                    raw_value=expression.raw_formula,
                )
            )
    return diagnostics


def _render_module(
    *,
    contract: GeneratedModuleContract,
    expressions: Mapping[str, FormulaExpression],
    constants: Mapping[str, JsonValue],
) -> str:
    lines = [
        '"""Generated Sheetforge model.',
        "",
        f"Source workbook: {contract.workbook_id}",
        '"""',
        "",
        "",
        "def _sf_flatten(values):",
        "    for value in values:",
        "        if isinstance(value, (list, tuple)):",
        "            yield from _sf_flatten(value)",
        "        else:",
        "            yield value",
        "",
        "",
        "def _sf_average(values):",
        "    values = list(values)",
        "    return sum(values) / len(values)",
        "",
        "",
        "def _sf_iferror(value_fn, fallback):",
        "    try:",
        "        return value_fn()",
        "    except Exception:",
        "        return fallback",
        "",
        "",
        f"def {contract.entrypoint}(inputs=None):",
        "    inputs = {} if inputs is None else dict(inputs)",
    ]

    for symbol in contract.symbols:
        if contract.include_provenance_comments:
            lines.append(f"    # {symbol.cell_ref}" + (f": {symbol.raw_formula}" if symbol.raw_formula else ""))

        if symbol.kind == "input":
            default_value = constants.get(symbol.cell_ref)
            lines.append(
                f"    {symbol.symbol_name} = inputs.get({symbol.cell_ref!r}, {default_value!r})"
            )
            continue

        expression = expressions[symbol.cell_ref]
        lines.append(f"    {symbol.symbol_name} = {_render_expression(expression.root)}")

    lines.append("    return {")
    for output_ref in contract.output_refs:
        lines.append(f"        {output_ref!r}: {symbol_name_for_cell_ref(output_ref)},")
    lines.append("    }")
    lines.append("")
    return "\n".join(lines)


def _render_expression(node: FormulaExpressionNode | None) -> str:
    if node is None:
        raise ValueError("cannot render missing formula expression root")

    if node.kind == "literal":
        return repr(node.value)
    if node.kind == "reference":
        if node.reference is None:
            raise ValueError("cannot render reference expression without reference")
        if node.reference.kind == "range":
            return _render_range_reference(node.reference)
        return symbol_name_for_cell_ref(node.reference.normalized)
    if node.kind == "unary":
        (operand,) = node.operands
        if node.operator == "-":
            return f"(-{_render_expression(operand)})"
        raise ValueError(f"unsupported unary operator: {node.operator}")
    if node.kind == "binary":
        left, right = node.operands
        if node.operator == "^":
            return f"({_render_expression(left)} ** {_render_expression(right)})"
        if node.operator == "&":
            return f"(str({_render_expression(left)}) + str({_render_expression(right)}))"
        return f"({_render_expression(left)} {node.operator} {_render_expression(right)})"
    if node.kind == "comparison":
        left, right = node.operands
        operator = _python_comparison_operator(node.operator)
        return f"({_render_expression(left)} {operator} {_render_expression(right)})"
    if node.kind == "function_call":
        return _render_function_call(node)

    raise ValueError(f"unsupported expression kind: {node.kind}")


def _render_function_call(node: FormulaExpressionNode) -> str:
    if node.function_name == "ROUND":
        if len(node.operands) != 2:
            raise ValueError("ROUND requires two operands")
        return f"round({_render_expression(node.operands[0])}, {_render_expression(node.operands[1])})"
    if node.function_name == "IF":
        if len(node.operands) != 3:
            raise ValueError("IF requires three operands")
        condition, true_value, false_value = node.operands
        return f"({_render_expression(true_value)} if {_render_expression(condition)} else {_render_expression(false_value)})"
    if node.function_name == "IFERROR":
        if len(node.operands) != 2:
            raise ValueError("IFERROR requires two operands")
        value, fallback = node.operands
        return f"_sf_iferror(lambda: {_render_expression(value)}, {_render_expression(fallback)})"
    if node.function_name == "AND":
        return f"all(_sf_flatten({_render_argument_tuple(node.operands)}))"
    if node.function_name == "OR":
        return f"any(_sf_flatten({_render_argument_tuple(node.operands)}))"
    if node.function_name == "SUM":
        return f"sum(_sf_flatten({_render_argument_tuple(node.operands)}))"
    if node.function_name == "MIN":
        return f"min(_sf_flatten({_render_argument_tuple(node.operands)}))"
    if node.function_name == "MAX":
        return f"max(_sf_flatten({_render_argument_tuple(node.operands)}))"
    if node.function_name == "AVERAGE":
        return f"_sf_average(_sf_flatten({_render_argument_tuple(node.operands)}))"
    if node.function_name == "CONCATENATE":
        return f"''.join(str(value) for value in _sf_flatten({_render_argument_tuple(node.operands)}))"
    raise ValueError(f"unsupported function call: {node.function_name}")


def _render_argument_tuple(operands: tuple[FormulaExpressionNode, ...]) -> str:
    rendered = ", ".join(_render_expression(operand) for operand in operands)
    if len(operands) == 1:
        rendered = f"{rendered},"
    return f"({rendered})"


def _render_range_reference(reference) -> str:
    if reference.sheet is None or reference.start_cell is None or reference.end_cell is None:
        raise ValueError(f"cannot render incomplete range reference: {reference.normalized}")

    min_col, min_row, max_col, max_row = range_boundaries(f"{reference.start_cell}:{reference.end_cell}")
    rendered_cells = [
        symbol_name_for_cell_ref(f"{reference.sheet}!{get_column_letter(column)}{row}")
        for row in range(min_row, max_row + 1)
        for column in range(min_col, max_col + 1)
    ]
    return f"({', '.join(rendered_cells)}{',' if len(rendered_cells) == 1 else ''})"


def _python_comparison_operator(operator: str | None) -> str:
    if operator == "=":
        return "=="
    if operator == "<>":
        return "!="
    if operator is None:
        raise ValueError("missing comparison operator")
    return operator
