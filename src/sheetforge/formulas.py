"""Formula expression records.

These records describe translated formula structure; they do not translate
Excel formula text themselves.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

from openpyxl.formula.tokenizer import Tokenizer

from sheetforge.extraction import CellRecord
from sheetforge.graph import DependencyGraph
from sheetforge.references import WorkbookReference
from sheetforge.references import normalize_reference


JsonValue = str | int | float | bool | None | list[Any] | dict[str, Any]
ExpressionKind = Literal["literal", "reference", "unary", "binary", "comparison", "function_call"]
DiagnosticSeverity = Literal["info", "warning", "error"]
FormulaReferenceIndex = dict[tuple[str, str], WorkbookReference]
SUPPORTED_FUNCTIONS = frozenset(
    {
        "AND",
        "AVERAGE",
        "CONCATENATE",
        "COUNTIF",
        "COUNTIFS",
        "IF",
        "IFERROR",
        "MAX",
        "MIN",
        "OR",
        "ROUND",
        "SUM",
        "SUMIF",
        "SUMIFS",
        "VLOOKUP",
    }
)
SUPPORTED_OPERATORS = frozenset({"+", "-", "*", "/", "^", "&", ">", ">=", "<", "<=", "=", "<>", "(", ")", ","})


@dataclass(frozen=True)
class FormulaTranslationDiagnostic:
    """Formula translation concern tied to source formula provenance."""

    code: str
    message: str
    severity: DiagnosticSeverity = "warning"
    location: str | None = None
    raw_value: JsonValue = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "FormulaTranslationDiagnostic":
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
class FormulaExpressionNode:
    """One node in a translated formula expression tree."""

    kind: ExpressionKind
    value: JsonValue = None
    reference: WorkbookReference | None = None
    operator: str | None = None
    function_name: str | None = None
    operands: tuple["FormulaExpressionNode", ...] = field(default_factory=tuple)

    @classmethod
    def literal(cls, value: JsonValue) -> "FormulaExpressionNode":
        return cls(kind="literal", value=value)

    @classmethod
    def reference_to(cls, reference: WorkbookReference) -> "FormulaExpressionNode":
        return cls(kind="reference", reference=reference)

    @classmethod
    def unary(
        cls,
        operator: str,
        operand: "FormulaExpressionNode",
    ) -> "FormulaExpressionNode":
        return cls(kind="unary", operator=operator, operands=(operand,))

    @classmethod
    def binary(
        cls,
        operator: str,
        left: "FormulaExpressionNode",
        right: "FormulaExpressionNode",
    ) -> "FormulaExpressionNode":
        return cls(kind="binary", operator=operator, operands=(left, right))

    @classmethod
    def comparison(
        cls,
        operator: str,
        left: "FormulaExpressionNode",
        right: "FormulaExpressionNode",
    ) -> "FormulaExpressionNode":
        return cls(kind="comparison", operator=operator, operands=(left, right))

    @classmethod
    def function_call(
        cls,
        function_name: str,
        operands: tuple["FormulaExpressionNode", ...],
    ) -> "FormulaExpressionNode":
        return cls(kind="function_call", function_name=function_name.upper(), operands=operands)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "FormulaExpressionNode":
        reference_data = data.get("reference")
        return cls(
            kind=data["kind"],
            value=data.get("value"),
            reference=WorkbookReference.from_dict(reference_data) if reference_data is not None else None,
            operator=data.get("operator"),
            function_name=data.get("function_name"),
            operands=tuple(cls.from_dict(item) for item in data.get("operands", [])),
        )

    def to_dict(self) -> dict[str, JsonValue]:
        return {
            "kind": self.kind,
            "value": self.value,
            "reference": self.reference.to_dict() if self.reference is not None else None,
            "operator": self.operator,
            "function_name": self.function_name,
            "operands": [operand.to_dict() for operand in self.operands],
        }


@dataclass(frozen=True)
class FormulaExpression:
    """Translated expression for one source formula cell."""

    source_cell: str
    raw_formula: str
    root: FormulaExpressionNode | None = None
    diagnostics: tuple[FormulaTranslationDiagnostic, ...] = field(default_factory=tuple)

    @property
    def translated(self) -> bool:
        return self.root is not None and not any(diagnostic.severity == "error" for diagnostic in self.diagnostics)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "FormulaExpression":
        root_data = data.get("root")
        return cls(
            source_cell=data["source_cell"],
            raw_formula=data["raw_formula"],
            root=FormulaExpressionNode.from_dict(root_data) if root_data is not None else None,
            diagnostics=tuple(
                FormulaTranslationDiagnostic.from_dict(item) for item in data.get("diagnostics", [])
            ),
        )

    def to_dict(self) -> dict[str, JsonValue]:
        return {
            "source_cell": self.source_cell,
            "raw_formula": self.raw_formula,
            "root": self.root.to_dict() if self.root is not None else None,
            "translated": self.translated,
            "diagnostics": [diagnostic.to_dict() for diagnostic in self.diagnostics],
        }


def translate_formula_cell(
    cell: CellRecord,
    graph: DependencyGraph,
    reference_index: FormulaReferenceIndex | None = None,
) -> FormulaExpression:
    """Translate one supported formula cell into an expression tree."""

    if cell.formula is None:
        return FormulaExpression(
            source_cell=cell.cell_ref,
            raw_formula=str(cell.raw_value),
            diagnostics=(
                FormulaTranslationDiagnostic(
                    code="not_a_formula_cell",
                    message="cell does not contain a formula record",
                    severity="error",
                    location=cell.cell_ref,
                    raw_value=cell.raw_value,
                ),
            ),
        )

    raw_formula = cell.formula.raw_formula
    try:
        tokens = _formula_tokens(raw_formula)
        parser = _FormulaParser(
            tokens=tokens,
            cell=cell,
            graph=graph,
            reference_index=reference_index,
        )
        root = parser.parse()
    except FormulaTranslationError as error:
        return FormulaExpression(
            source_cell=cell.cell_ref,
            raw_formula=raw_formula,
            diagnostics=(
                FormulaTranslationDiagnostic(
                    code=error.code,
                    message=error.message,
                    severity="error",
                    location=cell.cell_ref,
                    raw_value=error.raw_value,
                ),
            ),
        )

    return FormulaExpression(source_cell=cell.cell_ref, raw_formula=raw_formula, root=root)


def build_formula_reference_index(graph: DependencyGraph) -> FormulaReferenceIndex:
    """Build fast lookup for formula raw references by target cell."""

    index: FormulaReferenceIndex = {}
    for edge in graph.execution_edges:
        index.setdefault((edge.target.normalized, edge.raw_reference), edge.source)
    return index


@dataclass(frozen=True)
class _FormulaToken:
    kind: str
    value: str


class FormulaTranslationError(Exception):
    def __init__(self, code: str, message: str, raw_value: JsonValue = None) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.raw_value = raw_value


class _FormulaParser:
    def __init__(
        self,
        *,
        tokens: tuple[_FormulaToken, ...],
        cell: CellRecord,
        graph: DependencyGraph,
        reference_index: FormulaReferenceIndex | None,
    ) -> None:
        self.tokens = tokens
        self.cell = cell
        self.graph = graph
        self.reference_index = reference_index
        self.index = 0

    def parse(self) -> FormulaExpressionNode:
        expression = self._parse_comparison()
        if self._peek() is not None:
            token = self._peek()
            raise FormulaTranslationError("unexpected_formula_token", "unexpected token after expression", token.value)
        return expression

    def _parse_comparison(self) -> FormulaExpressionNode:
        left = self._parse_concatenation()
        token = self._peek()
        if token is not None and token.value in {">", ">=", "<", "<=", "=", "<>"}:
            self._advance()
            right = self._parse_concatenation()
            return FormulaExpressionNode.comparison(token.value, left, right)
        return left

    def _parse_concatenation(self) -> FormulaExpressionNode:
        expression = self._parse_additive()
        while (token := self._peek()) is not None and token.value == "&":
            self._advance()
            expression = FormulaExpressionNode.binary(token.value, expression, self._parse_additive())
        return expression

    def _parse_additive(self) -> FormulaExpressionNode:
        expression = self._parse_multiplicative()
        while (token := self._peek()) is not None and token.value in {"+", "-"}:
            self._advance()
            expression = FormulaExpressionNode.binary(token.value, expression, self._parse_multiplicative())
        return expression

    def _parse_multiplicative(self) -> FormulaExpressionNode:
        expression = self._parse_exponent()
        while (token := self._peek()) is not None and token.value in {"*", "/"}:
            self._advance()
            expression = FormulaExpressionNode.binary(token.value, expression, self._parse_exponent())
        return expression

    def _parse_exponent(self) -> FormulaExpressionNode:
        expression = self._parse_unary()
        while (token := self._peek()) is not None and token.value == "^":
            self._advance()
            expression = FormulaExpressionNode.binary(token.value, expression, self._parse_unary())
        return expression

    def _parse_unary(self) -> FormulaExpressionNode:
        token = self._peek()
        if token is not None and token.kind == "operator" and token.value in {"+", "-"}:
            self._advance()
            operand = self._parse_unary()
            if token.value == "+":
                return operand
            return FormulaExpressionNode.unary(token.value, operand)
        return self._parse_primary()

    def _parse_primary(self) -> FormulaExpressionNode:
        token = self._advance()
        if token.kind == "number":
            return FormulaExpressionNode.literal(_number_value(token.value))
        if token.kind == "text":
            return FormulaExpressionNode.literal(token.value)
        if token.kind == "logical":
            return FormulaExpressionNode.literal(token.value == "TRUE")
        if token.kind == "reference":
            return FormulaExpressionNode.reference_to(self._resolved_reference(token.value))
        if token.kind == "identifier":
            return self._parse_function_call(token.value)
        if token.value == "(":
            expression = self._parse_comparison()
            self._expect(")")
            return expression
        raise FormulaTranslationError("unsupported_formula_token", "unsupported formula token", token.value)

    def _parse_function_call(self, function_name: str) -> FormulaExpressionNode:
        self._expect("(")
        function_name = function_name.upper()
        if function_name not in SUPPORTED_FUNCTIONS:
            raise FormulaTranslationError(
                "unsupported_function",
                f"function {function_name} is not supported",
                function_name,
            )

        arguments: list[FormulaExpressionNode] = []
        if (token := self._peek()) is not None and token.value == ")":
            self._advance()
            return FormulaExpressionNode.function_call(function_name, tuple(arguments))

        while True:
            arguments.append(self._parse_comparison())
            token = self._peek()
            if token is not None and token.value == ",":
                self._advance()
                continue
            self._expect(")")
            return FormulaExpressionNode.function_call(function_name, tuple(arguments))

    def _resolved_reference(self, raw_reference: str) -> WorkbookReference:
        semantic_reference = normalize_reference(raw_reference, current_sheet=_sheet_name(self.cell.cell_ref))
        if semantic_reference.kind == "range":
            return semantic_reference

        if self.reference_index is not None:
            source = self.reference_index.get((self.cell.cell_ref, raw_reference))
            if source is not None:
                if source.kind == "structured":
                    raise FormulaTranslationError(
                        "unsupported_structured_reference",
                        "structured references are not supported",
                        raw_reference,
                    )
                return source

        for edge in self.graph.execution_edges:
            if edge.target.normalized == self.cell.cell_ref and edge.raw_reference == raw_reference:
                if edge.source.kind == "structured":
                    raise FormulaTranslationError(
                        "unsupported_structured_reference",
                        "structured references are not supported",
                        raw_reference,
                    )
                return edge.source

        if semantic_reference.kind == "structured":
            raise FormulaTranslationError(
                "unsupported_structured_reference",
                "structured references are not supported",
                raw_reference,
            )
        if semantic_reference.kind == "named_range":
            raise FormulaTranslationError("unresolved_named_range", "named range could not be resolved", raw_reference)
        return semantic_reference

    def _peek(self) -> _FormulaToken | None:
        if self.index >= len(self.tokens):
            return None
        return self.tokens[self.index]

    def _advance(self) -> _FormulaToken:
        token = self._peek()
        if token is None:
            raise FormulaTranslationError("unexpected_formula_end", "formula ended unexpectedly")
        self.index += 1
        return token

    def _expect(self, value: str) -> None:
        token = self._advance()
        if token.value != value:
            raise FormulaTranslationError("unexpected_formula_token", f"expected {value}", token.value)


def _formula_tokens(raw_formula: str) -> tuple[_FormulaToken, ...]:
    tokens: list[_FormulaToken] = []
    for token in Tokenizer(raw_formula).items:
        if token.type == "WHITE-SPACE":
            continue
        if token.type == "FUNC" and token.subtype == "OPEN":
            tokens.append(_FormulaToken("identifier", token.value[:-1]))
            tokens.append(_FormulaToken("operator", "("))
            continue
        if token.type == "FUNC" and token.subtype == "CLOSE":
            tokens.append(_FormulaToken("operator", ")"))
            continue
        if token.type == "PAREN":
            tokens.append(_FormulaToken("operator", token.value))
            continue
        if token.type == "SEP":
            tokens.append(_FormulaToken("operator", token.value))
            continue
        if token.type == "OPERAND" and token.subtype == "NUMBER":
            tokens.append(_FormulaToken("number", token.value))
            continue
        if token.type == "OPERAND" and token.subtype == "TEXT":
            tokens.append(_FormulaToken("text", token.value.strip('"')))
            continue
        if token.type == "OPERAND" and token.subtype == "LOGICAL":
            tokens.append(_FormulaToken("logical", token.value.upper()))
            continue
        if token.type == "OPERAND" and token.subtype == "ERROR":
            raise FormulaTranslationError(
                "unsupported_error_reference",
                "formula contains an unsupported error reference",
                token.value,
            )
        if token.type == "OPERAND" and token.subtype == "RANGE":
            tokens.append(_FormulaToken("reference", token.value))
            continue
        if token.type.startswith("OPERATOR"):
            if token.value not in SUPPORTED_OPERATORS:
                raise FormulaTranslationError("unsupported_operator", "formula operator is not supported", token.value)
            tokens.append(_FormulaToken("operator", token.value))
            continue
        raise FormulaTranslationError("unsupported_formula_token", "unsupported formula token", token.value)
    return tuple(tokens)


def _number_value(raw_value: str) -> int | float:
    value = float(raw_value)
    if value.is_integer():
        return int(value)
    return value


def _sheet_name(cell_ref: str) -> str:
    return cell_ref.split("!", 1)[0]
