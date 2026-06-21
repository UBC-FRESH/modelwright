# Private Workbook Evaluation Protocol

Date: 2026-06-20

## Purpose

Phase 13 uses private source workbooks to test whether Modelwright's extraction, graph, generation, oracle, and validation path can handle real workbook structure.

The evaluation lane is local by default. It should improve the public package without committing private workbooks, raw workbook facts, private generated clones, or full validation reports.

## Local File Boundaries

Keep private and derived files under ignored `tmp/`.

Suggested layout:

```text
tmp/private-workbooks/
tmp/private-evaluations/<evaluation-id>/
```

Use an anonymized `evaluation-id` in tracked notes. Do not use customer, project, file, worksheet, or model names as public identifiers unless the maintainer explicitly approves them.

Allowed local-only files include:

- source workbooks;
- workbook extracts;
- generated Python clones;
- oracle calculation outputs;
- validation reports;
- raw diagnostics;
- private notes and transcripts.

Before committing any Phase 13 work, run `git status --short` and confirm no private workbook, generated clone, private extract, raw report, or private note is tracked.

## Sanitized Public Notes

Tracked findings should be written as sanitized planning notes only after private details have been removed.

Allowed public details by default:

- anonymized evaluation id;
- workbook file type, such as `.xlsx` or `.xlsm`;
- high-level sheet, formula, named-range, and output counts;
- categories of unsupported features;
- package-level diagnostics using generic locations when needed;
- whether extraction, graph building, formula translation, code generation, oracle evaluation, and validation reached pass/fail/blocked states;
- follow-up package tasks stated without private workbook semantics.

Do not include by default:

- source workbook files;
- exact workbook filenames;
- worksheet names;
- named ranges;
- raw formulas;
- raw cell values;
- generated Python clones;
- full dependency graphs;
- full validation reports;
- business meaning inferred from the workbook;
- private paths outside `tmp/`.

If a specific raw detail is needed in a tracked note, ask the maintainer first and record why the detail is safe to publish.

## Evaluation Steps

For each private workbook evaluation:

1. Place the workbook under `tmp/private-workbooks/`.
2. Assign an anonymized `evaluation-id`.
3. Create a local working directory under `tmp/private-evaluations/<evaluation-id>/`.
4. Record private provenance locally: source path, workbook type, timestamp, and any known workbook dependencies.
5. Run extraction into a local artifact.
6. Record extraction blockers and unsupported workbook features.
7. Select a small set of output cells or named outputs for validation.
8. Try the `formulas` oracle where appropriate.
9. Generate Python only for the supported subset.
10. Compare generated outputs with oracle outputs when both are available.
11. Write raw reports under the ignored evaluation directory.
12. Convert the result into a sanitized tracked finding only if it is useful for package planning.

## Local Command Expectations

There is no committed private-workbook runner yet. Until one exists, local evaluation commands should be recorded in the private evaluation directory and summarized in sanitized notes.

Default public verification should remain:

```bash
python -m pytest
git diff --check
git status --short
```

Private evaluation commands must not become default CI requirements. Default CI must not depend on Excel, `xlwings`, private workbooks, ignored `tmp/` artifacts, or machine-specific absolute paths.

## Report Expectations

Raw local reports should include:

- evaluation id;
- source workbook local path;
- command used;
- package commit hash;
- selected outputs;
- extraction, graph, generation, oracle, and validation status;
- diagnostics with original private locations.

Sanitized tracked findings should include:

- evaluation id;
- package commit hash;
- feature categories encountered;
- which pipeline stages passed, failed, or were blocked;
- unsupported feature categories;
- next package tasks.

## Stop Conditions

Stop evaluation and record a blocker instead of forcing conversion when:

- workbook semantics are unclear;
- source workbook links external files that are unavailable;
- formulas or Excel behavior is not reproducible;
- macros, volatile functions, circular references, array formulas, or data tables materially affect selected outputs;
- a diagnostic would require publishing private workbook details to explain.
