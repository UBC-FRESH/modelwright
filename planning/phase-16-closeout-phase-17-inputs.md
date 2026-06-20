# Phase 16 Closeout And Phase 17 Inputs

Date: 2026-06-20

## Phase 16 Verification

Phase 16 aligned the public CLI and documentation surface with the FRESH lab package style used by `fhops` and `femic`.

Local verification completed on branch `feature/p16-cli-docs-public-surface`:

- `scripts/bootstrap_dev_env.sh`;
- `.venv/bin/python -m ruff check .`;
- `.venv/bin/python -m pytest`;
- `.venv/bin/sphinx-build -b html docs _build/html -W`;
- `.venv/bin/sheetforge --help`;
- `.venv/bin/sheetforge workbook --help`;
- `.venv/bin/sheetforge model generate --help`;
- `git diff --check`.

The CLI JSON smoke path also exercised:

- `sheetforge workbook extract`;
- `sheetforge workbook graph`;
- `sheetforge model generate`;
- `sheetforge validation report`.

The smoke run used ignored synthetic artifacts under `tmp/p16-cli-smoke/` and confirmed JSON payloads for extraction, graphing, generation, and validation.

GitHub Actions verification is expected to run on the Phase 16 pull request before merge.

## Phase 17 Starting Point

Phase 17 should return to spreadsheet semantics and use sanitized real-workbook evidence from `planning/private-workbook-eval-001-findings.md` as the primary input.

The highest-priority gaps are:

- structured table-reference formulas, which blocked the pure-Python `formulas` oracle on the private workbook;
- unsupported Excel functions, especially the high-count categories from private evaluation diagnostics;
- unsupported parser token forms;
- unsupported operators;
- external workbook references;
- volatile functions;
- unresolved named ranges;
- formula cells without cached values;
- deciding how cached workbook values, `formulas`, Excel-backed validation, or a hybrid should be represented as validation evidence.

## Recommended Phase 17 Task Order

1. Prioritize the unsupported semantics from private evaluation diagnostics without copying private formulas, values, sheet names, workbook names, or paths into tracked files.
2. Add first-class extraction or diagnostic records for structured references, even before full translation support exists.
3. Expand formula translation only where the parser and validation evidence can support it.
4. Validate expanded semantics against synthetic fixtures and sanitized private-workbook evaluation summaries.

Phase 17 should not claim full workbook equivalence. It should make more real workbook behavior explicit, diagnosable, and testable.
