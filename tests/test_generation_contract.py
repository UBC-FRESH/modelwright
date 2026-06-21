import json

from modelwright.generation import (
    GeneratedModuleContract,
    GeneratedSymbol,
    GenerationDiagnostic,
    GenerationResult,
    symbol_name_for_cell_ref,
)


def test_symbol_name_for_cell_ref_builds_python_identifier() -> None:
    assert symbol_name_for_cell_ref("Summary!B2") == "summary_b2"
    assert symbol_name_for_cell_ref("'Input Data'!$B$2") == "input_data_b_2"
    assert symbol_name_for_cell_ref("123!A1") == "cell_123_a1"


def test_generated_module_contract_serializes_provenance() -> None:
    contract = GeneratedModuleContract(
        workbook_id="synthetic_model.xlsx",
        module_name="synthetic_model",
        entrypoint="calculate",
        input_refs=("Inputs!B2", "Inputs!B3", "Inputs!B4"),
        output_refs=("Summary!B2", "Summary!B3"),
        symbols=(
            GeneratedSymbol(
                cell_ref="Summary!B2",
                symbol_name="summary_b2",
                kind="output",
                raw_formula="=Calc!B4",
            ),
            GeneratedSymbol(
                cell_ref="Summary!B3",
                symbol_name="summary_b3",
                kind="output",
                raw_formula='=IF(B2>50,"ok","low")',
            ),
        ),
    )

    payload = contract.to_dict()

    assert payload["module_name"] == "synthetic_model"
    assert payload["entrypoint"] == "calculate"
    assert payload["output_refs"] == ["Summary!B2", "Summary!B3"]
    assert payload["include_provenance_comments"] is True
    assert payload["symbols"][0] == {
        "cell_ref": "Summary!B2",
        "symbol_name": "summary_b2",
        "kind": "output",
        "raw_formula": "=Calc!B4",
    }
    assert GeneratedModuleContract.from_dict(payload) == contract
    json.dumps(payload)


def test_generation_result_reports_success_and_errors() -> None:
    contract = GeneratedModuleContract(
        workbook_id="synthetic_model.xlsx",
        module_name="synthetic_model",
        output_refs=("Summary!B2",),
    )
    success = GenerationResult(
        contract=contract,
        source_code="def calculate():\n    return {'Summary!B2': 70.2}\n",
    )
    failure = GenerationResult(
        contract=contract,
        diagnostics=(
            GenerationDiagnostic(
                code="unsupported_formula",
                message="formula could not be generated",
                severity="error",
                location="Summary!B2",
                raw_value="=XLOOKUP(...)",
            ),
        ),
    )

    assert success.generated is True
    assert success.to_dict()["generated"] is True
    assert failure.generated is False
    assert failure.to_dict()["diagnostics"] == [
        {
            "code": "unsupported_formula",
            "message": "formula could not be generated",
            "severity": "error",
            "location": "Summary!B2",
            "raw_value": "=XLOOKUP(...)",
        }
    ]
    assert GenerationResult.from_dict(success.to_dict()) == success
    assert GenerationResult.from_dict(failure.to_dict()) == failure
