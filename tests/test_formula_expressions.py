import json

from sheetforge.formulas import (
    FormulaExpression,
    FormulaExpressionNode,
    FormulaTranslationDiagnostic,
)
from sheetforge.references import normalize_reference


def test_formula_expression_represents_binary_reference_expression() -> None:
    base_volume = FormulaExpressionNode.reference_to(normalize_reference("Inputs!B2"))
    growth_rate = FormulaExpressionNode.reference_to(normalize_reference("Inputs!B3"))
    expression = FormulaExpression(
        source_cell="Calc!B2",
        raw_formula="=BaseVolume*(1+GrowthRate)",
        root=FormulaExpressionNode.binary(
            "*",
            base_volume,
            FormulaExpressionNode.binary(
                "+",
                FormulaExpressionNode.literal(1),
                growth_rate,
            ),
        ),
    )

    payload = expression.to_dict()

    assert payload["source_cell"] == "Calc!B2"
    assert payload["raw_formula"] == "=BaseVolume*(1+GrowthRate)"
    assert payload["translated"] is True
    assert payload["root"]["kind"] == "binary"
    assert payload["root"]["operator"] == "*"
    assert payload["root"]["operands"][0]["reference"]["normalized"] == "Inputs!B2"
    json.dumps(payload)


def test_formula_expression_represents_function_and_comparison() -> None:
    expression = FormulaExpression(
        source_cell="Summary!B3",
        raw_formula='=IF(B2>50,"ok","low")',
        root=FormulaExpressionNode.function_call(
            "if",
            (
                FormulaExpressionNode.comparison(
                    ">",
                    FormulaExpressionNode.reference_to(normalize_reference("Summary!B2")),
                    FormulaExpressionNode.literal(50),
                ),
                FormulaExpressionNode.literal("ok"),
                FormulaExpressionNode.literal("low"),
            ),
        ),
    )

    payload = expression.to_dict()

    assert payload["root"]["kind"] == "function_call"
    assert payload["root"]["function_name"] == "IF"
    assert payload["root"]["operands"][0]["kind"] == "comparison"
    assert payload["root"]["operands"][1]["value"] == "ok"
    assert FormulaExpression.from_dict(payload) == expression


def test_formula_expression_records_translation_diagnostics() -> None:
    expression = FormulaExpression(
        source_cell="Calc!B9",
        raw_formula="=XLOOKUP(A1,B:B,C:C)",
        diagnostics=(
            FormulaTranslationDiagnostic(
                code="unsupported_function",
                message="function XLOOKUP is not supported",
                severity="error",
                location="Calc!B9",
                raw_value="XLOOKUP",
            ),
        ),
    )

    payload = expression.to_dict()

    assert expression.translated is False
    assert payload["translated"] is False
    assert payload["root"] is None
    assert payload["diagnostics"] == [
        {
            "code": "unsupported_function",
            "message": "function XLOOKUP is not supported",
            "severity": "error",
            "location": "Calc!B9",
            "raw_value": "XLOOKUP",
        }
    ]
    assert FormulaExpression.from_dict(payload) == expression
