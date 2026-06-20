# CLI JSON Workflows

Date: 2026-06-20

## Purpose

Phase 14 adds the first command-line boundary after the Python APIs have a coherent shape. The CLI is intentionally thin: it calls existing package functions and writes JSON to stdout for automation.

The CLI does not introduce a one-step workbook converter. It exposes the current workflow pieces so extraction, graphing, generation, and validation reports can be scripted and inspected separately.

## Commands

Install the package in editable mode before using the console script:

```bash
python -m pip install -e ".[test]"
```

Extract workbook facts:

```bash
sheetforge extract tmp/private-workbooks/example.xlsx > tmp/extraction.json
```

This command calls `sheetforge.extraction.extract_workbook` and writes the `WorkbookRecord` JSON payload.

Build dependency graph facts directly from a workbook:

```bash
sheetforge graph tmp/private-workbooks/example.xlsx > tmp/dependency-graph.json
```

This command calls `extract_workbook`, then `sheetforge.graph.build_dependency_graph`, and writes the `DependencyGraph` JSON payload.

Generate Python source from explicit JSON inputs:

```bash
sheetforge generate \
  --contract tmp/contract.json \
  --expressions tmp/expressions.json \
  --constants tmp/constants.json \
  --output tmp/generated_model.py \
  > tmp/generation-result.json
```

This command calls `sheetforge.generation.generate_python_module`. The contract JSON must match `GeneratedModuleContract.to_dict()`. The expressions JSON must be an object keyed by cell reference where each value matches `FormulaExpression.to_dict()`. Constants are optional and must be a JSON object keyed by input cell reference.

Build a validation report from already-observed generated and oracle values:

```bash
sheetforge validate-report \
  --scenario tests/fixtures/synthetic_model/baseline_scenario.json \
  --generated-values tmp/generated-values.json \
  --oracle-values tmp/oracle-values.json \
  > tmp/validation-report.json
```

This command calls `load_validation_scenario`, then `build_validation_report`. It does not execute Excel, `formulas`, or generated Python by itself.

## JSON Examples

Minimal generated module contract shape:

```json
{
  "workbook_id": "synthetic_model.xlsx",
  "module_name": "synthetic_model",
  "entrypoint": "calculate",
  "input_refs": ["Inputs!B2"],
  "output_refs": ["Summary!B2"],
  "symbols": [
    {
      "cell_ref": "Inputs!B2",
      "symbol_name": "inputs_b2",
      "kind": "input",
      "raw_formula": null
    },
    {
      "cell_ref": "Summary!B2",
      "symbol_name": "summary_b2",
      "kind": "output",
      "raw_formula": "=Inputs!B2+1"
    }
  ],
  "include_provenance_comments": true
}
```

Minimal generated/oracle values shape for validation-report input:

```json
{
  "Summary!B2": 101,
  "Summary!B3": "ok"
}
```

## Stabilization Decisions

- The CLI command names are workflow-oriented: `extract`, `graph`, `generate`, and `validate-report`.
- All successful command payloads are JSON printed to stdout.
- Generated Python source is written only when `sheetforge generate --output` is provided.
- The CLI does not duplicate extraction, graphing, generation, or validation logic.
- The CLI does not run the optional oracle interface yet; oracle execution remains a Python API boundary until the backend behavior is better proven against real workbooks.
- The CLI does not translate every formula in a workbook or infer a generated module contract. Those steps still require explicit Python API usage and project-specific decisions.
- Private workbooks and bulky outputs should remain under ignored `tmp/` paths.

## Open Follow-Up

Future phases may add command options for progress logging, oracle execution, conversion planning, and private-evaluation automation. Those should be added only after the corresponding Python APIs have stable boundaries and tests.
