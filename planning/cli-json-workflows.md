# CLI JSON Workflows

Date: 2026-06-20

## Purpose

Phase 14 adds the first command-line boundary after the Python APIs have a coherent shape. The CLI is intentionally thin: it calls existing package functions and writes JSON to stdout for automation.

The CLI does not introduce a one-step workbook converter. It exposes the current workflow pieces so extraction, graphing, generation, and validation reports can be scripted and inspected separately.

## Commands

Bootstrap the repo-local virtual environment before using the console script:

```bash
scripts/bootstrap_dev_env.sh
```

Extract workbook facts:

```bash
sheetforge workbook extract tmp/private-workbooks/example.xlsx > tmp/extraction.json
```

This command calls `sheetforge.extraction.extract_workbook` and writes the `WorkbookRecord` JSON payload.

Build dependency graph facts directly from a workbook:

```bash
sheetforge workbook graph tmp/private-workbooks/example.xlsx > tmp/dependency-graph.json
```

This command calls `extract_workbook`, then `sheetforge.graph.build_dependency_graph`, and writes the `DependencyGraph` JSON payload.

Generate Python source from explicit JSON inputs:

```bash
sheetforge model generate \
  --contract tmp/contract.json \
  --expressions tmp/expressions.json \
  --constants tmp/constants.json \
  --out tmp/generated_model.py \
  > tmp/generation-result.json
```

This command calls `sheetforge.generation.generate_python_module`. The contract JSON must match `GeneratedModuleContract.to_dict()`. The expressions JSON must be an object keyed by cell reference where each value matches `FormulaExpression.to_dict()`. Constants are optional and must be a JSON object keyed by input cell reference.

Execute a generated Python model from explicit JSON inputs:

```bash
sheetforge model execute \
  --contract tmp/contract.json \
  --model tmp/generated_model.py \
  --inputs tmp/input-overrides.json \
  > tmp/generated-values.json
```

This command calls `sheetforge.execution.execute_generated_model`. The inputs file is optional and must be
a JSON object keyed by input cell reference. The command returns a `GeneratedExecutionResult` payload with
declared output values and execution diagnostics.

Build a validation report from already-observed generated and oracle values:

```bash
sheetforge validation report \
  --scenario tests/fixtures/synthetic_model/baseline_scenario.json \
  --generated-values tmp/generated-values.json \
  --oracle-values tmp/oracle-values.json \
  > tmp/validation-report.json
```

This command calls `load_validation_scenario`, then `build_validation_report`. It does not execute Excel, `formulas`, or generated Python by itself.

Execute a generated model and assemble available validation reports:

```bash
sheetforge validation evaluate \
  --contract tmp/contract.json \
  --model tmp/generated_model.py \
  --scenario tests/fixtures/synthetic_model/baseline_scenario.json \
  --workbook-record tmp/extraction.json \
  --oracle-result tmp/oracle-result.json \
  --verbose \
  > tmp/evaluation-report.json
```

This command calls `sheetforge.evaluation.evaluate_generated_model`. Cached-workbook validation is
included when either `--workbook-record` or `--workbook` is supplied. Oracle-backed validation is included
when `--oracle-result` is supplied. Verbose progress messages go to stderr; stdout remains JSON.

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

- The public CLI command groups are workflow-oriented: `workbook`, `model`, and `validation`.
- All successful command payloads are JSON printed to stdout.
- Generated Python source is written only when `sheetforge model generate --out` is provided.
- The CLI does not duplicate extraction, graphing, generation, or validation logic.
- The CLI does not run the optional oracle interface yet; oracle execution remains a Python API boundary, and `validation evaluate` accepts already-materialized oracle-result JSON.
- The CLI does not translate every formula in a workbook or infer a generated module contract. Those steps still require explicit Python API usage and project-specific decisions.
- Private workbooks and bulky outputs should remain under ignored `tmp/` paths.

## Open Follow-Up

Future phases may add command options for progress logging, oracle execution, conversion planning, and private-evaluation automation. Those should be added only after the corresponding Python APIs have stable boundaries and tests.
