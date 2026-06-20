"""Formula expression records.

These records describe translated formula structure; they do not translate
Excel formula text themselves.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

from sheetforge.references import WorkbookReference


JsonValue = str | int | float | bool | None | list[Any] | dict[str, Any]
ExpressionKind = Literal["literal", "reference", "binary", "comparison", "function_call"]
DiagnosticSeverity = Literal["info", "warning", "error"]


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
