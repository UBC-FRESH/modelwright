# Spreadsheet Tooling Research

Date: 2026-06-19

## Question

Which existing Python tools should Modelwright evaluate first for a generic spreadsheet-to-Python migration workflow?

The target workflow is:

```text
workbook
  -> extracted workbook model
  -> dependency graph
  -> generated Python source
  -> regression validation against workbook outputs
```

The final generated model should run without Excel.

## Candidate Tools

### openpyxl

Best initial role: workbook extraction baseline.

Use it to read `.xlsx`/`.xlsm` structure, worksheets, cells, formulas, named ranges, workbook metadata, and cached values. It should not be treated as a calculation engine: its own documentation says it never evaluates formulas, though it can preserve, parse, and tokenize formulas.

Fit:

- Strong for workbook inspection and source extraction.
- Useful for preserving source-cell provenance.
- Useful for detecting formulas, array formulas, and data-table formula structures.

Risks:

- Formula parsing is limited.
- Cached formula values depend on the workbook having been recalculated and saved elsewhere.
- It cannot validate generated model behavior by itself.

### formulas

Best initial role: first serious evaluation and intermediate-model candidate.

`formulas` parses and compiles Excel formula expressions, can compile workbooks to Python, can execute without the Excel COM server, and exposes CLI workflows for calculation, JSON model export, workbook testing, and serving models.

Fit:

- Closest match to Modelwright's early need for formula parsing, dependency extraction, workbook execution, and inspectable model artifacts.
- Its JSON export may be useful as a temporary intermediate representation during early prototypes.
- Its built-in workbook testing and comparison features are worth evaluating before inventing a validation harness.

Risks:

- Function coverage and behavior must be tested against representative workbooks.
- Its internal model may not match the maintainable generated-source shape Modelwright eventually wants.
- License and dependency implications need review before adopting it as a core runtime dependency.

### pycel

Best initial role: comparison point for graph-based compilation.

`pycel` translates Excel spreadsheets into executable Python code that can run independently of Excel. Its code is graph-based, uses caching and lazy evaluation, and can export/analyze graphs. The current PyPI release is `1.0b30`, released on 2021-10-13, and the package is GPLv3.

Fit:

- Directly aligned with spreadsheet-to-Python compilation.
- Useful source of ideas for graph structure, lazy evaluation, cache behavior, and generated-code ergonomics.

Risks:

- Published release age and beta status increase adoption risk.
- GPLv3 may be incompatible with some future Modelwright distribution goals.
- README notes that supported Excel functions were driven by the author's own workbook needs, and VBA must be reimplemented manually.

### xlcalculator

Best initial role: secondary formula-evaluation comparison.

`xlcalculator` reads Excel workbooks, translates supported formulas to Python, and evaluates them without Excel.

Fit:

- Worth including in the evaluation matrix because it is explicitly focused on Excel formula translation and evaluation.
- MIT license may be attractive if its coverage and maintenance are adequate.

Risks:

- Function coverage and maintenance status need verification during hands-on testing.
- It appears less directly focused on generated maintainable source than Modelwright's long-term goal.

### xlwings

Best initial role: optional Excel-backed oracle for validation.

`xlwings` is a bridge between Python and a live Excel runtime. The open-source package requires local Excel and Python on Windows or macOS. It can automate Excel, interact with workbooks, and trigger recalculation of open books.

Fit:

- Useful for extraction or validation when the source workbook relies on Excel behavior that pure-Python evaluators do not reproduce yet.
- Useful as an oracle to compare generated Python outputs against recalculated workbook outputs.

Risks:

- Not viable as a dependency for the final generated Python model.
- Requires platform-specific Excel availability.
- Harder to run in Linux CI or headless environments.

### networkx

Best initial role: dependency graph representation and analysis.

NetworkX is a general Python package for graph creation, manipulation, and analysis. It is a reasonable first choice for prototypes that need topological ordering, cycle detection, subgraph extraction, dependency queries, and graph diagnostics.

Fit:

- Good for workbook dependency graph prototypes.
- Keeps graph logic explicit instead of hidden inside one spreadsheet evaluator.

Risks:

- May not be the right long-term graph runtime if generated models need very high performance.
- Should remain a prototype dependency until actual workbook scale is known.

### Jinja

Best initial role: optional code-generation templating.

Jinja is a Python templating engine that renders text from structured data. It is a reasonable candidate for generated Python files once Modelwright has a stable intermediate model.

Fit:

- Good for readable source templates.
- Keeps generated-code layout explicit and reviewable.

Risks:

- Premature before the intermediate representation is stable.
- For early prototypes, simple standard-library string assembly may be enough.

## Recommended First Prototype Path

Start with a research prototype, not a package scaffold:

1. Create one small synthetic workbook under ignored `tmp/` with:
   - multiple sheets;
   - constants;
   - cross-sheet formulas;
   - named ranges;
   - a few lookup/math functions;
   - one intentionally unsupported or risky feature if useful.
2. Use `openpyxl` to extract workbook structure, formula strings, named ranges, cached values, sheet metadata, and source-cell provenance.
3. Use `formulas` to parse and calculate the same workbook, and inspect whether its model can expose enough dependency and formula information for Modelwright's needs.
4. Compare `pycel` and `xlcalculator` against the same workbook only after the `openpyxl` plus `formulas` path is understood.
5. Defer `xlwings` until a validation oracle is needed or until pure-Python evaluators diverge from Excel on important behavior.
6. Do not introduce a durable package layout, CLI, dependency manager, or CI until the prototype identifies the minimum stable interfaces.

## Early Acceptance Criteria

The first prototype should answer:

- Can we inventory workbook sheets, cells, formulas, named ranges, and cached values with stable provenance?
- Can we build or extract a dependency graph that supports topological ordering and cycle detection?
- Can we evaluate selected output cells without Excel?
- Can we identify unsupported functions or features clearly enough for diagnostics?
- Can we sketch what generated Python should look like for a tiny workbook?

## References Checked

- openpyxl documentation, including workbook support and formula notes: https://openpyxl.readthedocs.io/
- formulas documentation: https://formulas.readthedocs.io/
- pycel GitHub repository and PyPI record: https://github.com/dgorissen/pycel and https://pypi.org/project/pycel/
- xlcalculator GitHub repository: https://github.com/bradbase/xlcalculator
- xlwings documentation and product overview: https://docs.xlwings.org/ and https://www.xlwings.org/
- NetworkX documentation: https://networkx.org/documentation/stable/
- Jinja documentation: https://jinja.palletsprojects.com/
