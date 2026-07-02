# Roadmap

This roadmap is the current project plan and issue tracker map for `modelwright`.

The near-term implementation direction is recorded here. Broader phase rationale is recorded in `planning/long-term-roadmap.md`.

## Phase 0: Governance Bootstrap

GitHub parent issue: #1

- [x] P0.1 Create project overview and agent operating contract. Child issue: #2.
- [x] P0.2 Establish roadmap, changelog, planning area, and ignore rules. Child issue: #3.
- [x] P0.3 Commit bootstrap skeleton and verify clean ignored scratch space. Child issue: #4.
- [x] P0.4 Define strict issue, branch, and PR workflow. Child issue: #30.

Status: complete.

## Phase 1: Research Spreadsheet Tooling

GitHub parent issue: #5

- [x] P1.1 Compare candidate spreadsheet tooling. Child issue: #6.
- [x] P1.2 Run first synthetic workbook prototype. Child issue: #7.
- [x] P1.3 Record first prototype findings and architecture implications. Child issue: #8.

Status: complete.

## Phase 2: Workbook Extraction Contracts

GitHub parent issue: #9

Goal: define and test the minimum intermediate representation for workbook references, formulas, named ranges, dependencies, and diagnostics.

- [x] P2.1 Define workbook IR prototype contract. Child issue: #10.
- [x] P2.2 Emit IR JSON from the synthetic workbook. Child issue: #11.
  - [x] Create ignored prototype IR emitter under `tmp/`.
  - [x] Emit semantic named-range/reference edges.
  - [x] Emit execution cell-dependency edges.
  - [x] Emit diagnostics for missing cached formula values.
  - [x] Verify output against `planning/workbook-ir-contract.md` acceptance criteria.
- [x] P2.3 Record IR prototype findings and refine contract. Child issue: #12.
- [x] P2.4 Close extraction-contract phase with Phase 3 inputs. Child issue: #13.

Merged PR: #31

Status: complete.

## Phase 3: Prototype Python Code Generation

GitHub parent issue: #14

Goal: generate readable Python from the controlled workbook IR without committing to durable package structure too early.

- [x] P3.1 Define generated-code prototype contract. Child issue: #15.
- [x] P3.2 Build ignored generated-code experiment. Child issue: #16.
- [x] P3.3 Compare generated outputs against `formulas` results. Child issue: #17.
- [x] P3.4 Summarize code-generation readiness. Child issue: #18.

Merged PR: #32

Status: complete.

## Phase 4: Regression Validation Against Workbooks

GitHub parent issue: #19

Goal: define and prototype the validation loop that compares generated Python behavior against source workbook outputs.

- [x] P4.1 Define validation scenario and oracle contract. Child issue: #20.
- [x] P4.2 Build ignored validation prototype. Child issue: #21.
- [x] P4.3 Define mismatch diagnostics and tolerance rules. Child issue: #22.
- [x] P4.4 Summarize validation architecture and package inputs. Child issue: #23.

Merged PR: #33

Status: complete.

## Phase 5: Package, API, CLI, And CI Decisions

GitHub parent issue: #24

Active branch: `feature/p5-package-api-cli-ci-decisions`

Merged PR: #40

Goal: introduce durable project tooling only after extraction, code generation, and validation prototypes clarify the required shape.

- [x] P5.1 Choose package, dependency, and test stack. Child issue: #25.
- [x] P5.2 Define public API and CLI boundaries. Child issue: #26.
- [x] P5.3 Define fixture and regression-test strategy. Child issue: #27.
- [x] P5.4 Define CI and documentation verification. Child issue: #28.
- [x] P5.5 Summarize implementation bootstrap plan. Child issue: #29.

Status: complete.

## Phase 6: Initial Package And Validation Core

GitHub parent issue: #34

Active branch: `feature/p6-initial-package-validation-core`

Merged PR: #41

Goal: build the first durable code-bearing slice from the Phase 5 decisions: package skeleton, validation report core, synthetic fixtures, regression tests, and minimal default CI after tests exist.

- [x] P6.1 Add package and test skeleton. Child issue: #38.
- [x] P6.2 Add validation report core objects. Child issue: #37.
- [x] P6.3 Add synthetic fixture builder and expected outputs. Child issue: #35.
- [x] P6.4 Add baseline and mismatch regression tests. Child issue: #36.
- [x] P6.5 Add first default CI workflow. Child issue: #39.

Status: complete.

## Phase 7: Validation Scenario And Comparison Core

GitHub parent issue: #42

Merged PR: #79

Goal: turn the Phase 6 validation report records and synthetic fixture JSON into reusable scenario loading and scalar comparison helpers. This phase should not add workbook extraction, code generation, Excel-backed validation, CLI, or broad oracle execution.

- [x] P7.1 Add validation scenario objects and loader. Child issue: #46.
- [x] P7.2 Add scalar comparison helpers. Child issue: #45.
- [x] P7.3 Build validation reports from observed values. Child issue: #44.
- [x] P7.4 Summarize validation-core readiness. Child issue: #43.

Status: complete.

## Phase 8: Workbook Extraction Core

GitHub parent issue: #50

Merged PR: #80

Goal: move the proven `openpyxl` extraction concepts into package code for workbook, worksheet, cell, formula, named-range, and diagnostic records.

- [x] P8.1 Add extraction record objects. Child issue: #58.
- [x] P8.2 Implement `openpyxl` workbook extraction. Child issue: #57.
- [x] P8.3 Add extraction tests and closeout. Child issue: #56.

Status: complete.

## Phase 9: Dependency Graph Core

GitHub parent issue: #49

Merged PR: #81

Goal: build normalized reference and dependency graph behavior on top of extracted workbook records.

- [x] P9.1 Add canonical reference model. Child issue: #55.
- [x] P9.2 Resolve named ranges and dependency edges. Child issue: #62.
- [x] P9.3 Add graph diagnostics and readiness note. Child issue: #60.

Status: complete.

## Phase 10: Formula Translation Core

GitHub parent issue: #48

Merged PR: #82

Goal: translate the first supported Excel formula subset into internal operations ready for generated Python.

- [x] P10.1 Add formula expression model. Child issue: #61.
- [x] P10.2 Translate supported synthetic formula subset. Child issue: #59.
- [x] P10.3 Add unsupported formula diagnostics and closeout. Child issue: #66.

Status: complete.

## Phase 11: Generated Python Model Core

GitHub parent issue: #47

Merged PR: #83

Goal: generate small standalone Python modules from extracted and translated workbook logic.

- [x] P11.1 Define generated module contract. Child issue: #65.
- [x] P11.2 Generate Python from translated workbook logic. Child issue: #64.
- [x] P11.3 Test generated model outputs and closeout. Child issue: #63.

Status: complete.

## Phase 12: Oracle-Backed Validation

GitHub parent issue: #54

Merged PR: #84

Goal: introduce optional source-workbook oracle execution, starting with a pure-Python `formulas`-backed lane before any Excel-backed validation.

- [x] P12.1 Define oracle interface and optional dependency boundary. Child issue: #70.
- [x] P12.2 Add `formulas`-backed oracle for synthetic workbook. Child issue: #69.
- [x] P12.3 Compare generated model against oracle outputs. Child issue: #68.

Status: complete.

## Phase 13: Real Workbook Evaluation Lane

GitHub parent issue: #52

Merged PR: #85

Goal: use private workbooks under ignored `tmp/` to evaluate the pipeline and record sanitized findings without committing source workbooks or private outputs.

- [x] P13.1 Define private workbook evaluation protocol. Child issue: #67.
- [x] P13.2 Run first private workbook evaluation locally. Child issue: #74.
- [x] P13.3 Record sanitized findings and unsupported features. Child issue: #72.

Status: complete.

## Phase 14: CLI And API Stabilization

GitHub parent issue: #53

Merged PR: #86

Goal: stabilize the Python API and add thin CLI wrappers only after the internal flow is coherent.

- [x] P14.1 Review and stabilize Python API boundaries. Child issue: #73.
- [x] P14.2 Add thin CLI command groups. Child issue: #71.
- [x] P14.3 Document CLI and JSON workflows. Child issue: #78.

Status: complete.

## Phase 15: Hardening And Release Prep

GitHub parent issue: #51

Merged PR: #102

Goal: add hardening, documentation, release, and quality tooling only where evidence shows it will pay for itself.

- [x] P15.1 Decide hardening tooling from evidence. Child issue: #77.
- [x] P15.2 Add release and documentation metadata if needed. Child issue: #76.
- [x] P15.3 Summarize release readiness and next roadmap. Child issue: #75.

Status: complete.

## Phase 16: CLI And Documentation Public Surface

GitHub parent issue: #89

Completed branch: `feature/p16-cli-docs-public-surface`

Goal: align Modelwright's CLI feel, command organization, help text, and documentation depth with the other FRESH lab packages `fhops` and `femic`, including full Sphinx documentation published to GitHub Pages from the `main` branch.

- [x] P16.1 Audit `fhops`/`femic` CLI and docs conventions. Child issue: #92.
- [x] P16.2 Refactor CLI toward FRESH Typer/Rich conventions. Child issue: #90.
- [x] P16.3 Add full Sphinx docs and GitHub Pages workflow. Child issue: #93.
- [x] P16.4 Verify CLI/docs surface and closeout. Child issue: #91.

Status: complete.

## Phase 17: Real Workbook Formula Semantics

GitHub parent issue: #88

Completed branch: `feature/p17-real-workbook-formula-semantics`

Merged PR: #109

Goal: expand formula and reference semantics based on real workbook evidence, especially structured references, unsupported functions, parser token forms, operators, external references, volatile functions, named ranges, and cached-value gaps.

- [x] P17.1 Prioritize real-workbook unsupported semantics. Child issue: #97.
- [x] P17.2 Add structured-reference extraction records. Child issue: #95.
- [x] P17.3 Expand formula translation subset. Child issue: #96.
  - [x] Pass 1: boolean literals, unary minus, `^`, `&`, and explicit `#REF!` diagnostics.
  - [x] Pass 2: scalar/range functions, supported table structured references, and unresolved structured-reference fast-fail behavior.
  - [x] Pass 3: criteria functions `SUMIF`, `SUMIFS`, `COUNTIF`, and `COUNTIFS`.
  - [x] Pass 4: lookup function `VLOOKUP` plus table-array structured references.
  - [x] Pass 5: constrained cross-table current-row structured references.
  - [x] Pass 6: constrained static `OFFSET` support.
- [x] P17.4 Validate expanded semantics and closeout. Child issue: #94.

Status: complete.

## Phase 18: Conversion Planning And Pipeline Orchestration

GitHub parent issue: #87

Merged PR: #110

Goal: turn extraction, graphing, translation, generation, and validation pieces into an explicit conversion plan workflow without pretending every workbook can be fully converted.

- [x] P18.1 Define conversion plan JSON contract. Child issue: #101.
- [x] P18.2 Build conversion plan API. Child issue: #99.
  - [x] Track official external FABLE benchmark metadata and add a helper that materializes the untracked workbook files into canonical ignored paths.
- [x] P18.3 Add conversion planning CLI. Child issue: #100.
- [x] P18.4 Test conversion planning workflow and closeout. Child issue: #98.

Status: complete.

## Phase 19: Residual Blocker Resolution For Full Benchmark Import

GitHub parent issue: #103

Completed branch: `feature/p19-residual-blocker-resolution`

Merged PR: #111

Goal: resolve or explicitly scope the residual blockers exposed by the 2020 FABLE conversion plan before treating validation automation as meaningful evidence.

- [x] P19.1 Resolve or scope unresolved named ranges. Child issue: #107.
- [x] P19.2 Define circular dependency semantics and policy. Child issue: #105.
- [x] P19.3 Resolve deferred workbook dependency and volatile/cache blockers. Child issue: #106.
- [x] P19.4 Rerun 2020 benchmark to convergence and closeout. Child issue: #104.

Status: complete.

## Phase 20: Automated Validation And Evaluation Reports

GitHub parent issue: #112

Completed branch: `feature/p20-automated-validation-reports`

Merged PR: #117

Goal: after residual blockers have concrete resolution or scope decisions, make generated-model execution, oracle execution where available, cached-value comparisons, and benchmark evaluation reports repeatable through APIs and CLI commands.

- [x] P20.1 Add generated model execution API. Child issue: #113.
- [x] P20.2 Orchestrate oracle and cached-value validation. Child issue: #114.
- [x] P20.3 Add evaluation report CLI and JSON outputs. Child issue: #115.
- [x] P20.4 Run repeatable evaluation and closeout. Child issue: #116.

Status: complete.

Closeout evidence:

- Synthetic generated-model evaluation passed end to end through the CLI with generated outputs
  `Summary!B2 = 70.2` and `Summary!B3 = "ok"` and no cached-validation mismatches.
- The 2020 FABLE benchmark rerun completed extraction, dependency graphing, and formula translation:
  54 sheets, 395,482 extracted cells, 296,976 formula cells, 296,976 translated formulas,
  3,543,800 dependency edges, no graph diagnostics, and no translation diagnostics.
- Full 2020 workbook equivalence is not proven yet because Modelwright does not yet infer and
  materialize a full generated-model contract with topologically ordered symbols and selected
  validation outputs for that workbook.

Ignored local evidence:

- `tmp/p20-synthetic-evaluation/summary.json`
- `tmp/p20-fable-2020-evaluation/closeout-summary.json`
- `tmp/logs/p20-synthetic-evaluation.log`
- `tmp/logs/p20-fable-2020-evaluation.log`
- `tmp/logs/p20-fable-2020-evaluation-closeout.log`

## Phase 21: Full Benchmark Model Materialization And Validation

GitHub parent issue: #118

Completed branch: `feature/p21-full-benchmark-model-validation`

Merged PR: #123

Goal: turn the clean 2020 FABLE extraction, graph, and translation evidence into an executable generated
Python benchmark model, then validate selected benchmark outputs and keep iterating on concrete blockers
until generated-model equivalence is either proven or sharply scoped.

- [x] P21.1 Infer generated-model contracts from dependency graphs and selected outputs. Child issue: #122.
- [x] P21.2 Materialize the 2020 FABLE generated model with topologically ordered symbols. Child issue: #121.
- [x] P21.3 Validate selected 2020 FABLE outputs against cached or oracle values. Child issue: #120.
- [x] P21.4 Rerun the blocker-find-resolve-continue loop until the benchmark result converges. Child issue: #119.

Status: complete.

Closeout evidence:

- The selected 2020 FABLE benchmark scope uses ten cached outputs from `SCENARIOS definition`.
- Extraction covered 54 sheets, 395,482 cells, and 296,976 formula cells.
- Dependency graphing produced 3,543,800 edges with no graph diagnostics.
- Formula translation covered 296,976 of 296,976 formulas with no translation diagnostics.
- Contract inference produced 20 symbols, 10 input constants, and 10 selected outputs with no diagnostics.
- Generated Python materialization produced a 207-line standalone model with no generation diagnostics.
- Generated execution returned all ten selected outputs.
- Cached workbook validation passed with ten comparisons, zero mismatches, and zero diagnostics.

Equivalence boundary:

- Proven: selected-output equivalence for the ten declared `SCENARIOS definition` outputs against cached
  workbook values.
- Not proven: full-workbook generated-model materialization, full-workbook generated-output equivalence,
  oracle-backed recalculation equivalence, and external workbook dependency behavior.

Ignored local evidence:

- `tmp/p21-fable-2020-materialization/summary.json`
- `tmp/p21-fable-2020-validation/summary.json`
- `tmp/p21-convergence-closeout/summary.json`
- `tmp/logs/p21-fable-2020-materialization-rerun.log`
- `tmp/logs/p21-fable-2020-validation.log`
- `tmp/logs/p21-convergence-closeout.log`

## Phase 22: PyPI Publication And Deployment Workflow

GitHub parent issue: #124

Active branch: `feature/p22-pypi-publication-deployment`

Goal: establish a professional deployment and publication workflow before any real PyPI release. This phase should make release metadata, artifact builds, TestPyPI rehearsal, documentation deployment checks, and maintainer publication gates explicit and reproducible.

- [x] P22.1 Decide alpha release target, license, and publication policy. Child issue: #127.
  - [x] Recommend `0.1.0a1` as the first external alpha version line.
  - [x] Define staged publication policy: local artifacts, TestPyPI rehearsal, then gated real PyPI.
  - [x] Define benchmark evidence boundary for alpha release claims.
  - [x] Confirm maintainer-approved MIT license before package metadata changes or real PyPI publication.
- [x] P22.2 Harden package metadata and artifact build checks. Child issue: #125.
  - [x] Add MIT license file and package metadata.
  - [x] Set package and import version to `0.1.0a1`.
  - [x] Add local release artifact check script.
  - [x] Verify sdist/wheel metadata, artifact contents, clean wheel install, package import, and installed CLI smoke test.
- [x] P22.3 Add release automation for GitHub, TestPyPI, and PyPI gates. Child issue: #129.
  - [x] Add CI release artifact build validation.
  - [x] Add manually gated TestPyPI and tag/protected-environment gated PyPI publication workflow skeleton.
  - [x] Verify GitHub Pages serves the built Sphinx Read the Docs themed artifact, not a fallback Jekyll/minima site.
- [x] P22.4 Document deployment runbook and developer release onboarding. Child issue: #128.
  - [x] Add Sphinx release and deployment runbook.
  - [x] Mirror release onboarding essentials in `CONTRIBUTING.md`.
  - [x] Verify docs build and local Read the Docs themed artifact.
- [x] P22.5 Rehearse release artifacts and close publication readiness. Child issue: #126.
  - [x] Run full local verification with verbose logs.
  - [x] Build sdist and wheel from a clean isolated build environment.
  - [x] Run artifact inspection and clean install smoke tests.
  - [x] Document TestPyPI rehearsal blocker: release workflow and trusted-publishing environments must be available after merge.
  - [x] Verify the published GitHub Pages site is the Sphinx Read the Docs themed documentation artifact.
  - [x] Record real PyPI alpha publication as deferred until TestPyPI rehearsal and maintainer approval pass.

Publication gates:

- Local sdist/wheel builds must pass metadata checks and clean install smoke tests.
- CI must validate release artifacts before any publication workflow can publish them.
- TestPyPI publication must be rehearsed or blocked with a concrete documented reason.
- Real PyPI publication must be protected by a maintainer-controlled gate.
- The first published alpha version must use canonical Python packaging syntax such as `0.1.0a1` or `1.0.0a1`.
- The project license must be selected explicitly by the maintainer before real PyPI publication.

Merged PR: #130

Status: complete.

## Phase 23: Modelwright Rebrand Before Publication

GitHub parent issue: #131

Active branch: `feature/p23-modelwright-rebrand`

Goal: complete the pre-publication rename from Sheetforge to Modelwright across the GitHub repository,
Python package, CLI, documentation, tests, and release workflow before resuming TestPyPI or PyPI
publication. There are no external users yet, so this phase should not add compatibility aliases.

- [x] P23.1 Define Modelwright rebrand scope. Child issue: #133.
  - [x] Rename the GitHub repository from `UBC-FRESH/sheetforge` to `UBC-FRESH/modelwright`.
  - [x] Record `modelwright` as the public package name.
  - [x] Record `modelwright` as the only CLI command.
  - [x] Record `modelwright` as the only Python import package.
  - [x] Record the no-alias policy for the old name.
- [x] P23.2 Rename package import CLI and metadata. Child issue: #135.
  - [x] Move `src/sheetforge` to `src/modelwright`.
  - [x] Update imports, tests, generated-code helpers, and optional dependency messages.
  - [x] Rename the console script from `sheetforge` to `modelwright`.
  - [x] Update package metadata, URLs, release artifact checks, and workflow smoke tests.
  - [x] Rename JSON fields and CLI options that embed the old project name.
- [x] P23.3 Update Modelwright docs planning and release text. Child issue: #134.
  - [x] Update README, CONTRIBUTING, AGENTS, Sphinx docs, and release guidance.
  - [x] Update planning notes that describe current product identity or commands.
  - [x] Preserve historical release-blocker provenance without carrying the old package name forward as the target.
  - [x] Update GitHub Pages references to `https://ubc-fresh.github.io/modelwright/`.
- [x] P23.4 Verify Modelwright release readiness. Child issue: #132.
  - [x] Rebuild the repo-local development environment.
  - [x] Run ruff in logged mode.
  - [x] Run pytest in verbose logged mode.
  - [x] Build Sphinx docs in logged mode and verify the Read the Docs theme.
  - [x] Run local release artifact checks and installed CLI smoke tests for `modelwright`.
  - [x] Record closeout evidence and next publication steps.

Merged PR: #136

Status: complete.

## Phase 24: TestPyPI Publication Rehearsal

GitHub parent issue: #137

Active branch: `feature/p24-testpypi-rehearsal`

Goal: rehearse publication of `modelwright==0.1.0a1` to TestPyPI, then verify clean installation,
import, and CLI behavior from TestPyPI before any real PyPI release.

- [x] P24.1 Confirm TestPyPI target and credentials. Child issue: #141.
  - [x] Check whether `modelwright` exists on TestPyPI.
  - [x] Confirm local token file shape without printing token values.
  - [x] Record whether the rehearsal will use token upload, trusted publishing, or a documented blocker.
- [x] P24.2 Build and upload TestPyPI artifacts. Child issue: #139.
  - [x] Run local release artifact check with verbose log.
  - [x] Upload the checked artifacts to TestPyPI without exposing credentials.
  - [x] Preserve upload logs under ignored `tmp/logs/`.
  - [x] Record success or exact blocker.
- [x] P24.3 Verify clean TestPyPI install. Child issue: #140.
  - [x] Install `modelwright==0.1.0a1` from TestPyPI into a clean ignored virtual environment.
  - [x] Verify import version.
  - [x] Verify `modelwright --help`.
  - [x] Verify old `sheetforge` import/CLI is absent.
  - [x] Record pass/blocker evidence.
- [x] P24.4 Record publication readiness decision. Child issue: #138.
  - [x] Update roadmap current next steps.
  - [x] Update changelog and planning note with sanitized evidence.
  - [x] State whether real PyPI alpha publication is ready or still blocked.
  - [x] Keep private token details out of tracked files.

Merged PR: #142

Status: complete.

## Phase 25: Real PyPI Alpha Publication

GitHub parent issue: #143

Goal: publish `modelwright==0.1.0a1` to real PyPI after successful TestPyPI rehearsal and maintainer
approval, then verify clean installation, import, and CLI behavior from PyPI.

- [x] P25.1 Confirm PyPI target and release tag readiness.
  - [x] Confirm `modelwright` returned `404` from real PyPI before publication.
  - [x] Confirm local working tree was clean on `main`.
  - [x] Confirm release tag `v0.1.0a1` did not already exist.
- [x] P25.2 Build and publish real PyPI artifacts.
  - [x] Run fresh local release artifact check with verbose log.
  - [x] Create annotated tag `v0.1.0a1`.
  - [x] Push tag and watch GitHub Actions `Release` workflow.
  - [x] Verify trusted-publishing `publish-pypi` job passed.
- [x] P25.3 Verify real PyPI install.
  - [x] Confirm PyPI JSON lists `modelwright` version `0.1.0a1`.
  - [x] Install `modelwright==0.1.0a1` from real PyPI into a clean ignored virtual environment.
  - [x] Verify import version.
  - [x] Verify `modelwright --help`.
  - [x] Verify old `sheetforge` import/CLI is absent.
- [x] P25.4 Record release closeout.
  - [x] Update roadmap, changelog, and planning note with sanitized evidence.
  - [x] Keep token values out of tracked files.
  - [x] State next release path.

Status: active pending closeout PR.

## Phase 26: Full FABLE Benchmark Validation

GitHub parent issue: #144

Active branch: `feature/p26-full-fable-validation`

Goal: validate generated Modelwright Python output against cached workbook oracle values for the full
2020 FABLE benchmark scope, not only selected outputs. The phase must end with either a full
comparable-output pass statement or a precise blocker taxonomy.

- [x] P26.1 Define full FABLE validation contract. Child issue: #150.
  - [x] Define primary workbook and canonical local path.
  - [x] Define generated output universe and comparable-output universe.
  - [x] Define pass/fail/blocker language.
  - [x] Define required raw and sanitized artifacts.
- [x] P26.2 Run verbose FABLE extraction graph translation. Child issue: #149.
  - [x] Materialize or verify the 2020 FABLE workbook at the canonical ignored path.
  - [x] Extract workbook records with verbose progress.
  - [x] Build dependency graph with verbose progress.
  - [x] Translate formulas with verbose progress.
  - [x] Persist ignored raw artifacts and summary counts.
- [x] P26.3 Generate and execute widest FABLE Python model. Child issue: #148.
  - [x] Infer the widest generated-model contract possible from the full output universe.
  - [x] Generate standalone Python under ignored `tmp/`.
  - [x] Execute generated model with verbose progress.
  - [x] Record generation and execution blockers.
  - [x] Resolve or explicitly scope cyclic workbook dependency semantics before generation. Implementation issue: #151.
- [x] P26.4 Compare generated outputs to cached oracle values. Child issue: #147.
  - [x] Build cached workbook oracle values for comparable outputs.
  - [x] Compare generated outputs with declared tolerance.
  - [x] Persist raw validation report under ignored `tmp/`.
  - [x] Record mismatch counts and samples in sanitized summary.
- [x] P26.5 Resolve FABLE full-validation blockers to convergence. Child issue: #146.
  - [x] Classify each blocker as extraction, graph, translation, generation, execution, comparison, performance, or source-workbook limitation.
  - [x] Fix Modelwright blockers in priority order.
  - [x] Rerun verbose validation after each fix.
  - [x] Stop only when validation passes or remaining blockers are explicitly non-Modelwright/accepted.
- [x] P26.6 Record full FABLE validation evidence. Child issue: #145.
  - [x] Update roadmap with exact pass/blocker statement.
  - [x] Update changelog and planning note with sanitized counts.
  - [x] Keep raw workbooks, generated models, and raw reports ignored.
  - [x] State release implications for the next alpha.
- [x] P26.7 Publish `v0.1.0a2` after full FABLE validation. Child issue: #153.
  - [x] Confirm P26 full validation status is `pass` with zero comparable-output mismatches.
  - [x] Record sanitized validation evidence and release claim boundaries.
  - [x] Run full local verification and release artifact checks.
  - [x] Tag `v0.1.0a2` and publish matching GitHub and PyPI releases through the existing release workflow.
  - [x] Verify clean install from PyPI.
  - [x] Defer P27 performance, memory, and generated-output architecture refactoring to the `0.1.0a3` release line.

Full comparable-output validation evidence:

- Status: `pass`.
- Comparable cached output universe: 281,741 formula outputs.
- Matches: 281,741.
- Mismatches: 0.
- Numeric comparable outputs: 239,943.
- Text comparable outputs: 41,798.
- Non-comparable cached blank formula outputs: 15,235, recorded as validation-boundary evidence rather than blockers.
- Raw local evidence remains ignored under `tmp/p26-fable-full-validation/` and `tmp/logs/p26-full-validation.log`.

Release evidence:

- Annotated tag: `v0.1.0a2`.
- GitHub release: `modelwright 0.1.0a2`.
- PyPI package: `modelwright==0.1.0a2`.
- Clean PyPI install verified in ignored `tmp/pypi-install/modelwright-0.1.0a2/.venv`.
- Import verified `modelwright.__version__ == "0.1.0a2"`.
- CLI smoke verified `modelwright --help`.

Status: complete.

## Phase 27: Generated Runtime Performance And Memory Hardening

GitHub parent issue: #152

Active branch: `feature/p27-performance-memory-hardening`

Status: complete.

Goal: make full-workbook generated-model validation practical by profiling and reducing generated
runtime, cache-load, and memory costs exposed by the 2020 FABLE benchmark. This phase should start
after Phase 26 records a clear correctness pass/blocker statement, because performance work must not
hide validation defects.

Planning note: `planning/phase-27-performance-memory-hardening.md`.

- [x] P27.1 Profile generated-model runtime hotspots. Child issue: #155.
  - [x] Add high-frequency timing around generated helper functions, formula execution, range/table materialization, and criteria functions.
  - [x] Determine whether runtime is dominated by repeated formula evaluation, repeated range scans, Python import/code-object overhead, output materialization, or cache loading.
  - [x] Record profiler output and sanitized conclusions under `planning/`.
- [x] P27.2 Reduce repeated range and criteria work. Child issue: #159.
  - [x] Cache reusable range/table views where Excel semantics allow.
  - [x] Avoid rebuilding large Python lists for every `SUMIF`, `SUMIFS`, `COUNTIF`, and `COUNTIFS` call.
  - [x] Preserve lazy `IF`/`IFERROR`/`IFNA` branch behavior and runtime circular-dependency detection.
- [x] P27.3 Reduce generated module size and import overhead. Child issue: #158.
  - [x] Disable inline formula provenance comments for large generated modules and verify full FABLE correctness is unchanged.
  - [x] Compact generated output maps while preserving `calculate(inputs=None) -> dict`.
  - [x] Use expression-source formula storage for large generated modules to reduce lambda/code-object import pressure.
  - [x] Keep `calculate(inputs=None) -> dict` behavior stable unless a later public API phase intentionally changes it.
  - [x] Measure import time and generated-code object memory before and after each change.
- [x] P27.4 Reduce pipeline cache and validation memory footprint. Child issue: #157.
  - [x] Measure workbook, graph, expression, inference, generated-module, and output-map memory costs separately.
  - [x] Evaluate streaming, SQLite/shelve-style local caches, compact record encoding, or selective loading for validation.
  - [x] Explain why runtime memory can be much larger than the original workbook file size.
  - [x] Decide whether the slim oracle validation artifact should become tracked package/CLI behavior in P27 or feed the compact runtime IR backend.
- [x] P27.5 Evaluate multicore and sharded execution options. Child issue: #156.
  - Status: complete.
  - [x] Evaluate parallel formula rendering and validation comparison where records are independent; do not productionize because measured serial costs are already small.
  - [x] Evaluate sharded generated-output execution across separate worker processes; do not productionize naive output sharding because broad dependency closures duplicate work and memory.
  - [x] Reprofile contract inference before parallelizing it, and fix measured serial bottlenecks first.
  - [x] Add production inference fixes for ordered membership tracking and cached range-dependency expansion.
  - [x] Decide whether further parallel contract inference remains warranted after the serial fixes.
  - [x] Document CPU, memory, process startup, serialization, and determinism tradeoffs for high-core-count hosts.
- [x] P27.6 Rerun FABLE validation with performance evidence. Child issue: #160.
  - Status: complete.
  - [x] Always run verbose with stdout piped to `tmp/logs/` and print the tail command first.
  - [x] Record runtime, peak memory, cache-hit behavior, and correctness comparison results.
  - [x] Confirm performance changes do not regress Phase 26 correctness evidence.

Acceptance criteria:

- Performance claims are backed by logged timings and memory observations, not guesses.
- The phase states whether formulas are being recomputed unnecessarily or whether the cost is dominated
  by range scans, generated-module import, cache materialization, output materialization, or another
  measured source.
- Any optimization keeps full FABLE validation correctness evidence at least as good as before.

## Phase 28: Publish Modelwright 0.1.0a3

GitHub parent issue: #162

Active branch: `feature/p28-v0.1.0a3-release`

Status: complete.

Goal: publish `modelwright==0.1.0a3` as the alpha release that records Phase 27 performance and
memory hardening after full 2020 FABLE comparable-output validation remained green.

- [x] P28.1 Update `0.1.0a3` release metadata and notes. Child issue: #165.
  - Status: complete.
  - [x] Bump package and import version to `0.1.0a3`.
  - [x] Update release deployment docs and current alpha target text.
  - [x] Record P27 performance/correctness release boundary in roadmap/changelog.
  - [x] Avoid overstating public API stability or universal workbook conversion claims.
- [x] P28.2 Verify local release artifacts for `0.1.0a3`. Child issue: #164.
  - [x] Run Ruff, pytest, Sphinx docs, docs theme verification, and `git diff --check`.
  - [x] Run `scripts/check_release_artifacts.sh`.
  - [x] Confirm artifacts contain no private workbooks, generated clones, logs, or ignored `tmp/` material.
  - [x] Record local verification evidence in roadmap/changelog and issue comments.
- [x] P28.3 Publish and verify `0.1.0a3`. Child issue: #163.
  - [x] Open and merge the release PR to `main`.
  - [x] Create annotated tag `v0.1.0a3` after merge.
  - [x] Publish through the gated GitHub Actions release workflow after maintainer approval.
  - [x] Verify PyPI JSON lists `0.1.0a3`.
  - [x] Install from PyPI into a clean ignored environment, import `modelwright`, verify `__version__`, and run `modelwright --help`.
  - [x] Verify GitHub release and docs deployment.

Release result:

- Annotated tag: `v0.1.0a3`.
- GitHub release: `modelwright 0.1.0a3`.
- PyPI package: `modelwright==0.1.0a3`.
- Clean PyPI install verified in ignored `tmp/pypi-install/modelwright-0.1.0a3/.venv`.
- Import verified `modelwright.__version__ == "0.1.0a3"`.
- CLI help smoke test passed.
- GitHub Pages release documentation verified live with the Read the Docs theme.

Release claim boundary:

- May claim full comparable-output validation for the 2020 FABLE benchmark remains green.
- May claim measured generated-runtime performance and import/source-size improvements from P27.
- Must not claim stable public API, universal workbook conversion, Excel-backed recalculation
  equivalence, or compact runtime IR production readiness.

## Current Next Steps

## Phase 29: Model Wrapper Templates And Analyst-Facing Facades

GitHub parent issue: #167

Completed branch: `feature/p29-model-wrapper-templates`

Status: complete.

Goal: explore and implement an initial `modelwright` module that helps users build custom wrapper
facades around generated Python models, bridging the gap between raw generated cell-address APIs and
usable analyst-facing workbook structures.

Planning note: `planning/model-wrapper-template-facades.md`.

Motivation: generated Python code from a spreadsheet workbook can be validated and version controlled,
but a raw `Sheet!A1` output dictionary is not a humane analyst interface. This phase should restore
enough workbook, sheet, table, row, column, cell, scenario, and report structure around generated
models to support inspection, mutation, execution, and reporting without reintroducing spreadsheet
files as the execution environment.

- [x] P29.1 Define wrapper facade contract. Child issue: #171.
  - Status: complete.
  - [x] Define the problem boundary between raw generated models and analyst-usable facades.
  - [x] Specify workbook, sheet, table, row, column, cell, and scenario concepts.
  - [x] Decide what metadata must come from extraction/generation versus user-authored wrapper declarations.
  - [x] Define inspection, mutation, execution, and reporting API sketches.
  - [x] Record non-goals: no full spreadsheet UI, no Excel dependency, no stable public API guarantee yet.
- [x] P29.2 Implement initial wrapper template module. Child issue: #170.
  - Status: complete.
  - [x] Add an initial `modelwright` wrapper/template module.
  - [x] Provide workbook/sheet/table/cell facade primitives around generated `calculate(inputs=None) -> dict` models.
  - [x] Support user-authored labels and rectangular table declarations.
  - [x] Support input mutation and output reporting without mutating generated source.
  - [x] Add focused synthetic tests.
- [x] P29.3 Document custom wrapper workflow. Child issue: #169.
  - Status: complete.
  - [x] Add Sphinx docs explaining why raw generated models need facades.
  - [x] Show a minimal custom wrapper around a generated synthetic model.
  - [x] Document inspection, mutation, execution, and reporting examples.
  - [x] Document limitations and alpha API stability boundary.
  - [x] Keep examples free of private workbook content.
- [x] P29.4 Validate wrapper workflow against benchmarks. Child issue: #168.
  - Status: complete.
  - [x] Verify wrapper primitives against tracked synthetic fixture outputs.
  - [x] Use FABLE-derived public/extracted metadata where practical without committing private/generated artifacts.
  - [x] Add an opt-in benchmark-gated wrapper test against the local generated 2020 FABLE model.
  - [x] Confirm wrapper behavior does not change generated-model calculation semantics.
  - [x] Run full local verification.
  - [x] Record evidence in roadmap/changelog and issue comments.
- [x] P29.5 Publish `modelwright==0.1.0a4`. Child issue: #172.
  - Status: complete.
  - [x] Bump package/import version and release docs to `0.1.0a4`.
  - [x] Run local release artifact checks.
  - [x] Open and merge release PR to `main`.
  - [x] Create annotated tag `v0.1.0a4`.
  - [x] Publish through the gated release workflow after maintainer approval.
  - [x] Verify PyPI JSON, clean PyPI install, import version, CLI help, GitHub release, and docs deployment.

Release boundary:

- May claim an initial wrapper-template API for custom generated-model facades if tests/docs support it.
- Must not claim a full spreadsheet UI, automatic workbook semantic recovery, stable public API
  compatibility, or compact runtime IR production readiness.

Release evidence:

- PR #173 merged to `main`.
- Annotated tag: `v0.1.0a4`.
- GitHub release: `modelwright 0.1.0a4`.
- PyPI package: `modelwright==0.1.0a4`.
- Clean PyPI install verified in ignored `tmp/pypi-install/modelwright-0.1.0a4-rerun/.venv`.
- Import verified `modelwright.__version__ == "0.1.0a4"`.
- CLI help verified from the clean PyPI install.
- GitHub Pages release docs verified with Read the Docs themed markup and `0.1.0a4` content.

## Current Next Steps

## Phase 30: Notebook Interface And DataFrame Display Layer

GitHub parent issue: #174

Active branch: `feature/p30-notebook-dataframe-interface`

Status: complete.

Goal: add an optional notebook-facing layer on top of `modelwright.wrappers` that exposes wrapped
generated models as Jupyter-friendly, pandas-backed analyst workflows. This phase should support a
live-kernel loop where analysts can inspect declared inputs, outputs, and tables; mutate scenarios;
recalculate; render declared tables as DataFrames; and compare baseline-vs-scenario results without
using raw generated source or `Sheet!A1` dictionaries as the common path.

Planning note: `planning/notebook-dataframe-interface.md`.

Release target: `modelwright==0.1.0a5`.

- [x] P30.1 Define notebook adapter contract. Child issue: #175.
  - Status: complete.
  - [x] Decide the module boundary for notebook-facing helpers.
  - [x] Define the relationship to `ModelFacade` without making pandas a core wrapper dependency.
  - [x] Decide the optional dependency policy for `pandas`.
  - [x] Define helper API sketches for inputs, outputs, tables, reports, scenarios, and comparisons.
  - [x] Define non-goals: no full spreadsheet UI, no dashboard server, no automatic workbook semantic
        naming, no widget framework unless explicitly scoped, and no stable public API guarantee yet.
- [x] P30.2 Implement DataFrame view helpers. Child issue: #178.
  - Status: complete.
  - [x] Add the selected notebook/DataFrame module.
  - [x] Add a lazy pandas import and clear missing-dependency error.
  - [x] Convert declared inputs and outputs to tidy DataFrames.
  - [x] Convert declared table views to DataFrames preserving row labels, column labels, values,
        cell refs, and provenance where practical.
  - [x] Convert report bundles to DataFrame payloads without changing `ModelFacade` calculation behavior.
  - [x] Add focused synthetic tests.
- [x] P30.3 Implement scenario comparison helpers. Child issue: #176.
  - Status: complete.
  - [x] Define scenario comparison inputs and output columns.
  - [x] Include declared name, label, cell ref, baseline value, scenario value, absolute change,
        percent change where numeric, unit, role, and provenance/drilldown metadata where practical.
  - [x] Preserve generated-model execution errors as wrapper/notebook-layer errors.
  - [x] Add synthetic tests for numeric, text, missing, and zero-baseline comparison behavior.
  - [x] Keep raw cell refs available without making them the primary notebook-facing interaction.
- [x] P30.4 Add notebook-oriented docs. Child issue: #177.
  - Status: complete.
  - [x] Add `docs/guides/notebook-interface.rst`.
  - [x] Show loading a generated model and wrapping it with `ModelFacade`.
  - [x] Show declared inputs, outputs, tables, and reports.
  - [x] Show DataFrame rendering helpers.
  - [x] Show scenario mutation and scenario comparison.
  - [x] Document alpha limits and non-goals clearly.
  - [x] Add the guide to the docs index.
- [x] P30.5 Validate synthetic and FABLE notebook workflows. Child issue: #179.
  - Status: complete.
  - [x] Add always-on synthetic tests for DataFrame conversion and scenario comparison.
  - [x] Confirm the notebook layer does not change generated-model calculation behavior.
  - [x] Add or extend an opt-in FABLE benchmark-gated test with `MODELWRIGHT_RUN_FABLE_BENCHMARKS=1`
        if local artifacts support it.
  - [x] Keep generated FABLE models and raw reports under ignored `tmp/`.
  - [x] Run full local verification and record evidence in roadmap, changelog, and issue comments.
- [x] P30.6 Add examples gallery. Child issue: #181.
  - Status: complete.
  - [x] Add an `examples/` directory with a tiny synthetic notebook-interface example.
  - [x] Add a production-size 2020 FABLE generated-model example without tracking the original workbook.
  - [x] Keep the original FABLE workbook and raw local validation reports out of tracked files.
  - [x] Avoid ordinary Git blobs larger than GitHub/PyPI practical limits.
  - [x] Add Sphinx Examples Gallery pages linked from the docs index.
  - [x] Add lightweight tests for example integrity without running expensive production-size FABLE
        calculation in default pytest.
- [x] P30.7 Publish `modelwright==0.1.0a5`. Child issue: #180.
  - Status: complete.
  - [x] Confirm P30 notebook/DataFrame scope and evidence are complete.
  - [x] Bump package/import version and release docs to `0.1.0a5`.
  - [x] Run local release checks, including Ruff, pytest, Sphinx docs, docs theme verification, and
        release artifact checks.
  - [x] Open and merge the P30 PR to `main`.
  - [x] Create annotated tag `v0.1.0a5`.
  - [x] Publish through the gated release workflow after maintainer approval.
  - [x] Verify PyPI JSON, clean PyPI install, import version, CLI help, GitHub release, and docs deployment.

Acceptance boundary:

- May claim initial Jupyter/DataFrame-facing helpers for wrapped generated models.
- May claim optional pandas-backed display helpers.
- May claim scenario mutation and comparison as notebook-native workflows.
- May claim synthetic and opt-in FABLE evidence that notebook helpers do not change calculation behavior.
- Must not claim a full spreadsheet UI, dashboard application, widget framework, automatic workbook
  semantic recovery, stable public API compatibility, or compact runtime IR production readiness.

Implementation evidence:

- Added `modelwright.notebooks` with lazy pandas-backed helpers:
  `inputs_frame`, `outputs_frame`, `scenario_frame`, `table_frame`, `report_frames`, and
  `compare_scenarios_frame`.
- Added the `notebook` optional extra with `pandas>=2`, while keeping pandas out of core dependencies.
- Added always-on synthetic notebook tests, including real generated synthetic model coverage and
  missing-pandas dependency behavior.
- Extended the opt-in FABLE wrapper benchmark to validate notebook DataFrame helpers over the ignored
  generated 2020 FABLE model.
- Added `examples/` with a tracked synthetic notebook-interface example and a production-size FABLE
  notebook-interface example. The FABLE generated Python output is tracked as a compressed
  `generated_fable_2020_model.py.xz` artifact because the uncompressed module is larger than ordinary
  GitHub per-file limits.

Verification evidence:

- `scripts/bootstrap_dev_env.sh` passed and installed the updated `dev` extra.
- `.venv/bin/python -m ruff check .` passed.
- `.venv/bin/python -m pytest -vv` passed with `161` passed and `1` skipped benchmark.
- `.venv/bin/sphinx-build -b html docs _build/html -W` passed.
- `.venv/bin/python scripts/verify_docs_theme.py _build/html` passed.
- `MODELWRIGHT_RUN_FABLE_BENCHMARKS=1 .venv/bin/python -m pytest -vv tests/test_fable_wrapper_benchmark.py`
  passed in `149.67` seconds, using ignored local FABLE artifacts under `tmp/p26-fable-full-validation/`.
- `scripts/check_release_artifacts.sh` passed for `0.1.0a5`; the clean wheel install imported
  `modelwright 0.1.0a5` and the artifact inspection found no forbidden private workbook, ignored
  `tmp/`, or source workbook content.
- Release artifacts from the local check were about `56K` for the wheel and `2.2M` for the sdist. The
  sdist includes the compressed FABLE generated-model example; the wheel remains package-code only.

Release result:

- PR #182 merged to `main`.
- Annotated tag: `v0.1.0a5`.
- GitHub release: `modelwright 0.1.0a5`.
- PyPI package: `modelwright==0.1.0a5`.
- Clean PyPI install verified in ignored `tmp/pypi-install/modelwright-0.1.0a5/.venv` with
  `modelwright[notebook]==0.1.0a5`.
- Import verified `modelwright.__version__ == "0.1.0a5"`.
- Notebook extra verified by importing pandas and `modelwright.notebooks.inputs_frame`.
- CLI help verified from the clean PyPI install.
- GitHub Pages release docs verified with Read the Docs themed Examples Gallery, notebook-interface
  guide, and `0.1.0a5` release-deployment content.

## Current Next Steps

## Phase 31: Literate Notebook Examples Gallery

GitHub parent issue: #183

Active branch: `feature/p31-literate-notebook-examples`

Status: complete.

Goal: substantially enhance the examples seed from Phase 30 with actual known-valid Jupyter
notebook files and matching Sphinx gallery documentation. The notebooks should follow a literate
programming style: headings and subheadings, explanatory markdown before code, code cells, stored
outputs, and enough context that motivated new users can understand the workflow without reading
package internals first.

Release target: `modelwright==0.1.0a6`.

- [x] P31.1 Define literate notebook example contract. Child issue: #187.
  - Status: complete.
  - [x] Decide notebook file placement and naming.
  - [x] Define required markdown/code/output structure.
  - [x] Define how notebooks import repo examples from source checkouts and installed packages.
  - [x] Define validation strategy for notebook JSON, markdown/code alternation, expected outputs, and
        expensive FABLE execution boundaries.
  - [x] Record non-goals and release boundary in roadmap/planning docs.
- [x] P31.2 Add synthetic `.ipynb` notebook example. Child issue: #185.
  - Status: complete.
  - [x] Add a real `.ipynb` file with headings, explanatory markdown, code cells, and stored outputs.
  - [x] Show import setup, facade construction, scenario creation, input/output frames, table frame,
        and scenario comparison.
  - [x] Keep the notebook fast enough for default validation.
  - [x] Add tests that verify the notebook is valid and its expected outputs stay synchronized.
- [x] P31.3 Add 2020 FABLE `.ipynb` notebook example. Child issue: #186.
  - Status: complete.
  - [x] Add a real `.ipynb` file with headings, explanatory markdown, code cells, and stored outputs.
  - [x] Explain the compressed generated-model artifact and why the original workbook is not tracked.
  - [x] Show facade construction, calculation, output frames, table frame, report frames, and
        validation-boundary context.
  - [x] Avoid running the expensive FABLE generated-model calculation in default pytest; keep full
        execution opt-in.
  - [x] Keep raw workbooks and generated decompressed models ignored under `tmp/`.
- [x] P31.4 Integrate notebooks into examples gallery docs. Child issue: #184.
  - Status: complete.
  - [x] Add notebook download/open links to the examples gallery pages.
  - [x] Explain the intended workflow for opening notebooks from a source checkout.
  - [x] Keep generated workbook binaries and raw validation reports out of docs.
  - [x] Verify Sphinx docs build warning-free.
- [x] P31.5 Validate notebook examples and docs. Child issue: #188.
  - Status: complete.
  - [x] Validate notebook JSON structure and metadata.
  - [x] Validate literate structure: headings, explanatory markdown before code, code cells, and stored
        outputs.
  - [x] Execute or otherwise verify the synthetic notebook in default tests.
  - [x] Keep production-size FABLE execution opt-in but verify static stored outputs and provenance in
        default tests.
  - [x] Run Ruff, pytest, Sphinx docs, and docs theme verification.
  - [x] Record evidence in roadmap, changelog, and issue comments.
- [x] P31.6 Publish `modelwright==0.1.0a6`. Child issue: #189.
  - Status: complete.
  - [x] Confirm P31 notebook example scope and evidence are complete.
  - [x] Bump package/import version and release docs to `0.1.0a6`.
  - [x] Run local release checks, including Ruff, pytest, Sphinx docs, docs theme verification, and
        release artifact checks.
  - [x] Open and merge the P31 PR to `main`.
  - [x] Create annotated tag `v0.1.0a6`.
  - [x] Publish through the gated release workflow after maintainer approval.
  - [x] Verify PyPI JSON, clean PyPI install, import version, CLI help, GitHub release, and docs deployment.

Acceptance boundary:

- May claim tracked, known-valid literate notebook examples for synthetic and generated 2020 FABLE
  notebook/DataFrame workflows.
- May claim Sphinx Examples Gallery pages that link to actual `.ipynb` notebooks.
- Must not claim a full spreadsheet UI, automatic workbook semantic recovery, stable public API
  compatibility, or Excel-backed recalculation equivalence.

Implementation evidence:

- Added `examples/notebooks/synthetic-notebook-interface.ipynb` with literate markdown, code cells,
  and stored outputs for the synthetic notebook/DataFrame workflow.
- Added `examples/notebooks/fable-2020-notebook-interface.ipynb` with literate markdown, code cells,
  and stored outputs for the generated 2020 FABLE wrapper workflow.
- Added notebook download links to the Sphinx Examples Gallery pages.
- Added default tests that parse notebook JSON, verify Python 3 kernel metadata, validate markdown
  before code, require stored outputs, execute the synthetic notebook code cells, and verify the FABLE
  notebook's stored validation-boundary output without running the expensive generated model.

Verification evidence:

- `scripts/bootstrap_dev_env.sh` passed and installed the `0.1.0a6` editable package.
- `.venv/bin/python -m ruff check .` passed.
- `.venv/bin/python -m pytest -vv` passed with `167` passed and `1` skipped benchmark.
- `.venv/bin/sphinx-build -b html docs _build/html -W` passed and copied the notebook downloads.
- `.venv/bin/python scripts/verify_docs_theme.py _build/html` passed.
- `scripts/check_release_artifacts.sh` passed for `0.1.0a6`; the clean wheel install imported
  `modelwright 0.1.0a6` and the artifact inspection included the tracked notebook files in the sdist
  without including source workbooks, ignored `tmp/`, or private validation material.
- Local release artifacts were about `56K` for the wheel and `2.2M` for the sdist.

Release result:

- PR #190 merged to `main`.
- Annotated tag: `v0.1.0a6`.
- GitHub release: `modelwright 0.1.0a6`.
- PyPI package: `modelwright==0.1.0a6`.
- Clean PyPI install verified in ignored `tmp/pypi-install/modelwright-0.1.0a6/.venv` with
  `modelwright[notebook]==0.1.0a6`.
- Import verified `modelwright.__version__ == "0.1.0a6"`.
- Notebook extra verified by importing pandas and `modelwright.notebooks.inputs_frame`.
- CLI help verified from the clean PyPI install.
- GitHub Pages docs verified with the Examples Gallery, both notebook example pages, both downloadable
  `.ipynb` files, and `0.1.0a6` release-deployment content.

## Current Next Steps

Phase 34 is complete on `main`: Modelwright's FreshForge provider can execute
supported generated-model workflow stages using Modelwright Python APIs and the
FreshForge serial local runner.

Phase 32 is complete: `modelwright==0.1.0a7` is published to PyPI and GitHub as the generated-model
workflow orchestration alpha.

Phase 35 is complete on `main`: Modelwright's FreshForge provider now emits compact stage
summaries and sharper diagnostics for generated-model workflows, using FreshForge Phase 7
namespaces and whole-run summaries where useful.

Phase 36 is complete on `main`: Modelwright now packages generic compact validation-evidence
summaries for downstream automation without copying raw generated source, generated values,
workbooks, or full validation reports.

Phase 38 is active on `feature/p38-matrix-generated-model-evidence`: Modelwright will aggregate
compact generated-model evidence across FreshForge matrix runs so downstream packages can summarize
repeated validation cases without parsing raw artifacts or encoding domain-specific semantics.

## Phase 33: FreshForge Provider Pilot For Modelwright Workflows

GitHub parent issue: #205

Active branch: `feature/p33-modelwright-freshforge-provider`.

Status: complete.

Goal: add a plan-only FreshForge provider for Modelwright workflow stages so FreshForge can discover,
validate, inspect, and plan workbook-to-generated-model workflows without executing Modelwright
commands, reading declared artifacts, or adding a GitHub direct-reference FreshForge dependency to
published package metadata.

- [x] P33.1 Add FreshForge provider package boundary. Child issue: #206.
  - Status: complete.
  - [x] Add `modelwright.freshforge` provider factory module.
  - [x] Keep FreshForge imports lazy and optional.
  - [x] Add `freshforge.providers` entry point for Modelwright.
  - [x] Preserve PyPI-safe package metadata without a GitHub direct-reference FreshForge dependency.
  - [x] Test provider factory and normal import boundary.
- [x] P33.2 Add plan-only Modelwright provider node vocabulary. Child issue: #207.
  - Status: complete.
  - [x] Define provider id `modelwright`.
  - [x] Expose plan-only node types for workbook extraction, graphing, contract inference,
        generation, execution, validation evaluation, and conversion planning.
  - [x] Validate required inputs, outputs, parameters, and artifacts declared by provider metadata.
  - [x] Confirm provider metadata serializes deterministically.
- [x] P33.3 Add public-safe generated-model workflow example. Child issue: #208.
  - Status: complete.
  - [x] Add `examples/freshforge/generated_model_workflow.yaml`.
  - [x] Use public-safe synthetic paths only.
  - [x] Declare the Modelwright CLI-stage artifact flow without running commands.
  - [x] Test that the example validates and plans when FreshForge is installed.
- [x] P33.4 Add docs and tests for provider discovery/planning. Child issue: #209.
  - Status: complete.
  - [x] Add Sphinx docs for the Modelwright FreshForge provider.
  - [x] Link the guide from the docs index and relevant workflow docs.
  - [x] Document FreshForge planning versus Modelwright CLI execution.
  - [x] Document why FABLE-specific output-ref discovery belongs in FABLE Pyculator.
  - [x] Add tests for provider discovery, example planning, metadata, and diagnostics.
- [ ] P33.5 Verify, PR, and close Phase 33. Child issue: #210.
  - Status: complete.
  - [x] Run Ruff, pytest, Sphinx docs, docs theme verification, release artifact checks, and
        `git diff --check`.
  - [x] Smoke-test FreshForge `providers`, `validate`, `inspect`, and `plan` after installing
        FreshForge separately.
  - [x] Update roadmap and changelog evidence.
  - [x] Open PR from `feature/p33-modelwright-freshforge-provider` to `main`.
  - [x] Merge only after CI passes and close the parent issue after merge.

Acceptance boundary:

- May claim Modelwright exposes a plan-only FreshForge provider for workflow graph validation,
  inspection, and planning.
- Must not claim FreshForge executes Modelwright nodes, materializes artifacts, caches stages,
  checkpoints runs, or replaces Modelwright CLI/API execution.
- Must keep FABLE-specific output-ref discovery out of Modelwright.
- Must keep normal `import modelwright` from importing FreshForge eagerly.

Implementation evidence:

- Added `modelwright.freshforge` with a lazy, non-executing provider factory and provider id
  `modelwright`.
- Added a PyPI-safe `freshforge.providers` entry point without adding a FreshForge package dependency.
- Added plan-only node types for extraction, graphing, contract inference, generation, execution,
  validation evaluation, and conversion planning.
- Added `examples/freshforge/generated_model_workflow.yaml` as a public-safe plan-only workflow.
- Added `docs/guides/freshforge-provider-integration.rst`, linked it from the docs index, workflow
  boundary guide, and API reference.
- Added `tests/test_freshforge_integration.py` covering metadata, entry-point declaration, import
  boundary, example planning, and provider diagnostics.

Verification evidence:

- `.venv/bin/python -m ruff check .` passed.
- `.venv/bin/python -m pytest tests/test_freshforge_integration.py -q` passed with `6` tests after
  installing FreshForge from `v0.1.0a1`.
- `.venv/bin/python -m pytest` passed with `179` passed and `1` skipped benchmark.
- `.venv/bin/sphinx-build -b html docs _build/html -W` passed.
- `.venv/bin/python scripts/verify_docs_theme.py _build/html` passed.
- FreshForge smoke checks passed: `freshforge providers --json`, `freshforge validate
  examples/freshforge/generated_model_workflow.yaml --json`, `freshforge inspect
  examples/freshforge/generated_model_workflow.yaml --json`, and `freshforge plan
  examples/freshforge/generated_model_workflow.yaml --json`.
- `scripts/check_release_artifacts.sh` passed; the clean wheel install imported `modelwright
  0.1.0a6`, and artifact inspection included `modelwright/freshforge.py` plus entry-point metadata.
- `git diff --check` passed.

Closeout evidence:

- Phase 33 child issues #206, #207, #208, and #209 are closed.
- Phase 33 PR #211 merged to `main` with merge commit `193f3c6`.
- Post-merge `Test` workflow passed on `main`, including quality, pytest, and release-artifact jobs.
- Post-merge `docs-pages` workflow passed on `main`, including Sphinx build, Read the Docs theme
  artifact verification, artifact upload, and GitHub Pages deployment.

## Phase 34: Executable FreshForge Provider For Generated-Model Workflows

GitHub parent issue: #213

Active branch: `feature/p34-freshforge-executable-provider`.

Status: complete.

Goal: make Modelwright's FreshForge provider executable for the generated-model workflow while
keeping normal `import modelwright` FreshForge-free and preserving PyPI-safe package metadata.

- [x] P34.1 Update provider execution contract and workflow artifact requirements. Child issue:
      #214.
  - [x] Make `model_infer_contract` executable from an explicit workbook path and output refs.
  - [x] Require concrete artifact paths on executable generation, execution, and evaluation nodes.
  - [x] Keep FABLE-specific output-ref discovery outside Modelwright.
- [x] P34.2 Implement executable generated-model nodes with Python APIs. Child issue: #215.
  - [x] Add `run_node(...)` support to `modelwright.freshforge`.
  - [x] Use Modelwright Python payload helpers instead of CLI subprocesses.
  - [x] Write inference, generation, execution, and evaluation JSON artifacts.
- [x] P34.3 Add synthetic workflow run tests and CLI compatibility checks. Child issue: #216.
  - [x] Add a FreshForge run test over the synthetic workbook fixture.
  - [x] Confirm the generated model executes and cached validation passes.
  - [x] Preserve the normal import boundary that avoids eager FreshForge imports.
- [x] P34.4 Update docs, roadmap, changelog, and examples. Child issue: #217.
  - [x] Update the public FreshForge example workflow artifact declarations.
  - [x] Update FreshForge provider docs and workflow-boundary docs.
  - [x] Record Phase 34 evidence in the roadmap and changelog.
- [x] P34.5 Verify, PR, deploy docs, and close phase. Child issue: #218.
  - [x] Run full local verification.
  - [x] Open PR and verify CI/docs.
  - [x] Confirm post-merge docs deployment.

Acceptance boundary:

- May claim Modelwright's FreshForge provider can execute supported generated-model workflow stages
  through Python APIs.
- Must not claim FreshForge chooses workbook output refs, executes shell commands, caches stages, or
  validates arbitrary workbook equivalence.
- Must keep normal `import modelwright` from importing FreshForge eagerly.

Implementation evidence:

- Updated `modelwright.freshforge` with `run_node(...)` support.
- Updated `examples/freshforge/generated_model_workflow.yaml` with executable artifact paths.
- Added synthetic FreshForge run coverage for infer, generate, execute, and validation-evaluate.
- Updated Sphinx docs for FreshForge planning versus run behavior.

Verification evidence:

- `.venv/bin/python -m ruff check .` passed.
- `.venv/bin/python -m pytest` passed with 180 tests and 1 skipped benchmark.
- `.venv/bin/sphinx-build -b html docs _build/html -W` passed.
- `.venv/bin/python scripts/verify_docs_theme.py _build/html` passed.
- `scripts/check_release_artifacts.sh` passed.
- `git diff --check` passed.

Closeout evidence:

- Phase 34 PR #219 merged to `main`.
- PR checks passed for quality, pytest, docs build, and release artifacts.
- Post-merge docs workflow passed and deployed the updated FreshForge provider docs.

## Phase 35: Generated-Model Workflow Summaries And Provider Diagnostics

GitHub parent issue: #220

Active branch: `feature/p35-generated-model-workflow-summaries`.

Status: complete.

Goal: improve machine-readable summaries and diagnostics for Modelwright generated-model workflows
used through FreshForge and downstream tools.

- [x] P35.1 Define generated-model stage summary contract. Child issue: #224.
  - [x] Add compact stage summaries under `ProviderRunResult.data["summary"]`.
  - [x] Summarize inference, generation, execution, and validation-evaluation stages.
- [x] P35.2 Add provider diagnostics and failure semantics. Child issue: #223.
  - [x] Reject empty required artifact path strings and empty required outputs.
  - [x] Emit stage-specific diagnostics for generation, execution, and validation failures.
  - [x] Treat explicit validation failure as FreshForge node failure.
- [x] P35.3 Add FreshForge namespace and summary integration tests. Child issue: #225.
  - [x] Run the synthetic generated-model workflow with a FreshForge run namespace.
  - [x] Assert namespaced artifacts, FreshForge run summaries, and Modelwright stage summaries.
- [x] P35.4 Update docs, roadmap, changelog, and examples. Child issue: #226.
  - [x] Update FreshForge provider docs with namespace and stage-summary guidance.
  - [x] Update downstream planning note and changelog.
- [x] P35.5 Verify, PR, deploy docs, and close phase. Child issue: #227.
  - [x] Run full local verification.
  - [x] Open PR and verify CI/docs.
  - [x] Confirm post-merge docs deployment.

Dependency note: this phase should consume FreshForge Phase 7 run namespaces/summaries where useful
and provide the stage-level generated-model summaries needed by FABLE Pyculator Phase 18 output-ref
strategy comparisons.

Acceptance boundary:

- May expose clearer generated-model workflow status, artifact, and diagnostic summaries.
- Must not add FABLE output-table discovery, scenario-bundle semantics, or FreshForge orchestration
  policy beyond provider-owned generated-model execution details.

Implementation evidence:

- Added compact provider stage summaries for `model_infer_contract`, `model_generate`,
  `model_execute`, and `validation_evaluate` under `ProviderRunResult.data["summary"]`.
- Added validation diagnostics for empty required output and artifact declarations.
- Added stage-specific failure diagnostics for generated-model generation, execution, and validation
  failures while preserving generic unexpected-exception diagnostics.
- Added fail-fast validation semantics when cached/oracle validation reports explicitly fail.
- Added namespaced FreshForge synthetic workflow tests that assert FreshForge run summaries and
  Modelwright stage summaries together.

Local verification:

- `.venv/bin/python -m ruff check .` passed.
- `.venv/bin/python -m pytest` passed with 184 tests and 1 skipped benchmark.
- `.venv/bin/sphinx-build -b html docs _build/html -W` passed.
- `.venv/bin/python scripts/verify_docs_theme.py _build/html` passed.
- `scripts/check_release_artifacts.sh` passed.
- `git diff --check` passed.
- FreshForge smoke checks passed: `freshforge providers --json`, `freshforge validate
  examples/freshforge/generated_model_workflow.yaml --json`, and `freshforge plan
  examples/freshforge/generated_model_workflow.yaml --json`.

Closeout evidence:

- Phase 35 PR #228 merged to `main`.
- PR Test workflow run 28547298026 passed quality, pytest, and release-artifact jobs.
- PR docs-pages workflow run 28547298025 passed.
- Post-merge Test workflow run 28547368269 passed quality, pytest, and release-artifact jobs.
- Post-merge docs-pages workflow run 28547368962 passed and deployed GitHub Pages.

## Phase 36: Compact Validation Evidence Extraction For Downstream Automation

GitHub parent issue: #221

Active branch: `main` after PR #234.

Status: complete.

Goal: expose compact generated-model validation evidence that downstream packages can record in
docs, planning notes, and optional CI workflows without tracking raw validation reports.

- [x] P36.1 Define generic validation-evidence schema and paths. Child issue: #231.
  - [x] Add generic evidence identity and default path conventions.
  - [x] Add `ValidationEvidencePaths` and `ValidationEvidenceSummary`.
  - [x] Keep FABLE-specific workbook-version wording out of Modelwright.
- [x] P36.2 Add evidence extraction and conservative equivalence status logic. Child issue: #232.
  - [x] Summarize inference, generation, generated values, validation scenario, and evaluation
        artifacts.
  - [x] Mark missing artifacts as skipped unless required.
  - [x] Mark evidence incomplete when explicit comparison counts are absent.
  - [x] Mark equivalence pass only with explicit comparable/match/mismatch zero-mismatch evidence.
- [x] P36.3 Add writer and CLI packaging command. Child issue: #229.
  - [x] Write compact `summary.json` and `summary.md` files.
  - [x] Add `modelwright validation evidence`.
  - [x] Support evidence id, artifact/output dirs, scenario path, require-artifacts, and JSON output
        flags.
- [x] P36.4 Update docs, roadmap, changelog, and downstream guidance. Child issue: #230.
  - [x] Add API and CLI documentation.
  - [x] Add validation-evidence guide and cross-link generated-model workflow docs.
  - [x] Update the Phase 35/36 downstream planning note.
- [x] P36.5 Verify, PR, deploy docs, and close phase. Child issue: #233.
  - [x] Run full local verification.
  - [x] Open PR from `feature/p36-compact-validation-evidence` to `main`.
  - [x] Merge only after CI passes.
  - [x] Confirm post-merge Test and Docs Pages workflows pass.
  - [x] Close Phase 36 child issues and parent #221.

Dependency note: this phase follows Phase 35 because compact evidence should be derived from stable
stage summaries and diagnostics. FABLE Pyculator Phase 20 should consume this generic evidence rather
than duplicating raw Modelwright validation-report parsing.

Acceptance boundary:

- May summarize validation evidence for downstream publication and CI gates.
- Must not declare arbitrary workbook equivalence or absorb FABLE-specific output selection logic.

Implementation evidence:

- Added `modelwright.evidence` with generic validation-evidence path and summary records.
- Added conservative extraction rules for existing inference, generation, generated-values,
  validation-scenario, and evaluation artifacts.
- Added sanitized `summary.json` and `summary.md` writers that report counts and statuses without
  copying raw generated source, raw generated output values, workbook contents, or full comparison
  rows.
- Added `modelwright validation evidence` with evidence id, artifact/output directory, scenario,
  require-artifacts, and JSON output options.
- Added Sphinx guide, CLI reference, API reference, and generated-model workflow cross-links.

Local verification:

- `.venv/bin/python -m pytest tests/test_evidence.py tests/test_cli.py tests/test_public_api.py -q`
  passed with 28 tests.
- `.venv/bin/python -m ruff check .` passed.
- `.venv/bin/python -m pytest` passed with 195 tests and 1 skipped benchmark.
- `.venv/bin/sphinx-build -b html docs _build/html -W` passed.
- `.venv/bin/python scripts/verify_docs_theme.py _build/html` passed.
- `scripts/check_release_artifacts.sh` passed; artifact inspection included `modelwright/evidence.py`,
  and the clean wheel install imported `modelwright 0.1.0a7` and smoke-tested the CLI.
- `git diff --check` passed.
- Phase 36 PR #234 merged to `main` with merge commit `06814c5`.
- PR Test workflow passed quality, pytest, and release-artifact jobs after the CI help-rendering test
  fix.
- PR docs-pages workflow passed.
- Post-merge Test workflow run 28548149402 passed quality, pytest, and release-artifact jobs.
- Post-merge docs-pages workflow run 28548149355 passed and deployed GitHub Pages.
- Live docs smoke check verified
  `https://ubc-fresh.github.io/modelwright/guides/validation-evidence.html`.

## Phase 37: v0.1.0a8 Generated-Model Evidence Workflow Alpha Release

GitHub parent issue: #235

Release branch: `feature/v0.1.0a8-release`.

Status: complete after PR #240, tag `v0.1.0a8`, PyPI publication, GitHub prerelease, and
clean PyPI install smoke tests.

Goal: publish `modelwright==0.1.0a8` to GitHub and PyPI as the generated-model evidence workflow
alpha release.

- [x] P37.1 Bump Modelwright version and release metadata. Child issue: #236.
  - [x] Bump package and import metadata to `0.1.0a8`.
  - [x] Update provider metadata version and version tests.
- [x] P37.2 Update Modelwright release docs and FreshForge guidance. Child issue: #237.
  - [x] Update release deployment docs for the `0.1.0a8` alpha boundary.
  - [x] Update FreshForge guidance to `v0.1.0a3`.
- [x] P37.3 Verify Modelwright release artifacts and smoke tests. Child issue: #238.
  - [x] Run local quality, tests, docs, docs theme, and release artifact checks.
  - [x] Smoke-test CLI and evidence commands.
- [x] P37.4 Tag, publish PyPI/GitHub release, and close phase. Child issue: #239.
  - [x] Open and merge release PR after CI passes.
  - [x] Create annotated tag `v0.1.0a8`.
  - [x] Publish to PyPI through trusted publishing.
  - [x] Create GitHub prerelease and verify clean PyPI install.

Acceptance boundary:

- May claim generated-model FreshForge provider stage summaries, improved provider diagnostics,
  namespace-aware FreshForge integration, and generic compact validation-evidence extraction.
- Must not claim FABLE-specific output discovery, arbitrary full-workbook conversion, production
  readiness, or stable public API compatibility.

Local verification:

- `.venv/bin/python -m ruff check .` passed.
- `.venv/bin/python -m pytest` passed with 195 tests and 1 skipped benchmark.
- `.venv/bin/sphinx-build -b html docs _build/html -W` passed.
- `.venv/bin/python scripts/verify_docs_theme.py _build/html` passed.
- `scripts/check_release_artifacts.sh` passed; the clean wheel install imported
  `modelwright 0.1.0a8` and smoke-tested the CLI.
- `.venv/bin/modelwright --help` passed.
- `.venv/bin/modelwright model infer-contract --help` passed.
- `.venv/bin/modelwright validation evidence --help` passed.
- After installing FreshForge `v0.1.0a3`, `.venv/bin/freshforge providers --json` reported the
  Modelwright provider version as `0.1.0a8`.
- `git diff --check` passed.

Release evidence:

- PR #240 merged to `main`.
- Post-merge Test workflow run #28559618570 passed.
- Post-merge Docs Pages workflow run #28559618583 passed and deployed.
- Annotated tag `v0.1.0a8` was pushed.
- Release workflow run #28559646142 built artifacts and published `modelwright==0.1.0a8` to PyPI.
- PyPI listed both `modelwright-0.1.0a8-py3-none-any.whl` and `modelwright-0.1.0a8.tar.gz`.
- GitHub prerelease `v0.1.0a8` was created.
- Clean PyPI install of `modelwright[notebook]==0.1.0a8` imported version `0.1.0a8` and
  smoke-tested `modelwright --help`, `modelwright model infer-contract --help`, and
  `modelwright validation evidence --help`.

## Phase 32: FABLE Pyculator Onboarding And Validation Pilot

GitHub parent issue: #191

Active branch: `main` after PR #202.

Status: complete.

Goal: turn the current Modelwright humane-interface prototype into a structured onboarding and
validation pilot for Abdulateef, Gloria, and Camilla. The phase should make setup repeatable, make
tester feedback easy to capture, and define an initial FABLE-P validation protocol before deeper
FABLE Calculator compatibility work begins.

Release target: `modelwright==0.1.0a7`.

- [x] P32.1 Add FABLE Pyculator HQP onboarding guide. Child issue: #192.
  - Status: complete.
  - [x] Document JupyterHub login with UBC CWL.
  - [x] Document opening VSCode/code-server from JupyterLab.
  - [x] Document GitHub authentication and cloning the Modelwright repo.
  - [x] Document creating a repo-local `.venv` and selecting it as the notebook kernel.
  - [x] Document running the tracked notebook examples.
  - [x] Include Basecamp setup-help invitation and source-workbook hygiene.
  - [x] Link the guide from the Sphinx docs index.
- [x] P32.2 Add structured tester GitHub issue templates. Child issue: #193.
  - Status: complete.
  - [x] Add FABLE validation run issue form.
  - [x] Add usability observation issue form.
  - [x] Add setup problem issue form.
  - [x] Leave blank issues enabled.
  - [x] Validate issue-template YAML syntax.
- [x] P32.3 Define FABLE-P validation pilot protocol. Child issue: #194.
  - Status: complete.
  - [x] Define workbook provenance and local artifact rules.
  - [x] Define scenario parameter-change recording expectations.
  - [x] Define Excel-vs-generated-Python output comparison expectations.
  - [x] Define sanitized tracked finding boundaries.
  - [x] Keep raw workbooks and raw validation reports ignored under `tmp/`.
- [x] P32.4 Add scenario/output manifest seed format. Child issue: #195.
  - Status: complete.
  - [x] Define workbook identifier and provenance summary fields.
  - [x] Define scenario name and changed input fields.
  - [x] Define key output metric fields.
  - [x] Define Excel value, Python value, comparison status, and notes fields.
  - [x] Keep this as a seed format, not a full validation framework.
- [x] P32.5 Improve notebook examples from first-user friction. Child issue: #196.
  - Status: complete.
  - [x] Triage Gloria/Camilla usability observations. Deferred until concrete observations are filed.
  - [x] Triage Abdulateef validation-run friction.
  - [x] Close generated-model artifact materialization documentation/tooling gap. Implementation issue: #201.
  - [x] Fix generated `VLOOKUP` `#N/A` error-value propagation uncovered by the 2021 FABLE
        validation run. Implementation issue: #203.
  - [x] Apply only focused notebook/docs/API-polish changes justified by pilot feedback.
  - [x] Keep unrelated converter compatibility work out of this phase.
- [x] P32.6 Publish `modelwright==0.1.0a7`. Child issue: #197.
  - Status: complete.
  - [x] Confirm P32 onboarding/protocol/template scope and evidence are complete.
  - [x] Bump package/import version and release docs to `0.1.0a7`.
  - [x] Run local release checks, including Ruff, pytest, Sphinx docs, docs theme verification, and
        release artifact checks.
  - [x] Open and merge the P32 PR to `main`.
  - [x] Create annotated tag `v0.1.0a7`.
  - [x] Publish through the gated release workflow after maintainer approval.
  - [x] Verify PyPI JSON, clean PyPI install, import version, CLI help, GitHub release, and docs deployment.

Acceptance boundary:

- May claim a documented onboarding and validation pilot workflow for FABLE Pyculator testers.
- May claim structured validation and usability feedback can be captured through GitHub issues and
  manifest seeds.
- Must not claim arbitrary FABLE country calculator support, production FABLE-P Canada readiness,
  stable public API compatibility, or a full scenario automation framework.

Implementation evidence:

- Added `docs/guides/fable-pyculator-onboarding.rst` and linked it from the Sphinx guide index.
- Added GitHub issue forms for FABLE validation runs, setup problems, and usability observations.
- Added `planning/phase-32-fable-pyculator-onboarding-validation-pilot.md` with local artifact rules,
  validation protocol, usability protocol, and manifest-seed intent.
- Added `examples/fable_2020/scenario_output_manifest.example.json` as a sanitized seed for recording
  scenario inputs and selected Excel-vs-Python output comparisons.
- Updated `MANIFEST.in` so JSON example artifacts are included in source distributions.
- Added `modelwright model infer-contract` to materialize `contract.json`, `expressions.json`, and
  `constants.json` from a source workbook plus explicit selected output refs, and documented the
  generated-model artifact workflow for FABLE Pyculator testers.
- PR #202 merged the generated-model artifact materialization slice to `main`, and issue #201 is
  closed.
- Added generated runtime semantics for `VLOOKUP` misses as `#N/A` error values, while preserving
  `IFNA` and `IFERROR` fallback behavior. This closes the generic Modelwright blocker uncovered by
  the FABLE Pyculator 2021 validation run.
- Added plan-only and executable FreshForge provider integration after the first-user feedback loop,
  allowing FreshForge to validate, plan, and execute supported Modelwright generated-model workflow
  stages when FreshForge is installed separately.

Verification evidence:

- `.venv/bin/python -m pytest -vv tests/test_examples.py` passed with `7` tests.
- `.venv/bin/python -m ruff check .` passed.
- `.venv/bin/python -m pytest` passed with `172` passed and `1` skipped benchmark.
- `.venv/bin/sphinx-build -b html docs _build/html -W` passed and included the FABLE Pyculator
  onboarding guide and generated-model artifact guide.
- `.venv/bin/python scripts/verify_docs_theme.py _build/html` passed.
- `scripts/check_release_artifacts.sh` passed; the clean wheel install imported `modelwright 0.1.0a6`
  and smoke-tested the CLI.
- Post-merge `Test` workflow passed on `main` for commit `f865ec9`.
- Post-merge `docs-pages` workflow passed and deployed the generated-model artifact guide at
  `https://ubc-fresh.github.io/modelwright/guides/generated-model-artifacts.html`.
- Phase 33 PR #211 merged the plan-only FreshForge provider and deployed provider-integration docs.
- Phase 34 PR #219 merged the executable FreshForge provider for generated-model workflows and
  deployed updated provider-integration docs.
- `ruby -e 'require "yaml"; ...'` parsed all GitHub issue-template YAML files successfully.
- `.venv/bin/python` parsed `examples/fable_2020/scenario_output_manifest.example.json` as valid JSON.
- `git diff --check` passed.
- `.venv/bin/python -m ruff check .` passed for the `0.1.0a7` release candidate.
- `.venv/bin/python -m pytest` passed with `180` passed and `1` skipped benchmark.
- `.venv/bin/sphinx-build -b html docs _build/html -W` passed.
- `.venv/bin/python scripts/verify_docs_theme.py _build/html` passed.
- `scripts/check_release_artifacts.sh` passed; the clean wheel install imported `modelwright 0.1.0a7`
  and smoke-tested the CLI.
- `.venv/bin/modelwright --help` and `.venv/bin/modelwright model infer-contract --help` passed.
- `.venv/bin/freshforge providers --json` reported the Modelwright provider version as `0.1.0a7`
  after installing FreshForge `0.1.0a2`.
- Phase 32 release PR #222 merged to `main` at `878c0ad`.
- Post-merge `Test` workflow run #28540307396 passed.
- Post-merge `docs-pages` workflow run #28540307391 passed and deployed.
- Annotated tag `v0.1.0a7` was pushed.
- Tag-triggered `Release` workflow run #28540356638 built artifacts and published to PyPI.
- GitHub prerelease `modelwright 0.1.0a7` was created with the workflow-built wheel and sdist
  attached.
- PyPI JSON listed `modelwright-0.1.0a7-py3-none-any.whl` and `modelwright-0.1.0a7.tar.gz`.
- Clean PyPI install verified `modelwright[notebook]==0.1.0a7`, imported `modelwright 0.1.0a7`,
  imported pandas, and ran `modelwright --help`.

## Phase 38: Matrix Generated-Model Evidence Aggregation

GitHub parent issue: #243.

Active branch: `feature/p38-matrix-generated-model-evidence`.

Status: implemented locally; PR pending.

Goal: aggregate compact generated-model evidence across FreshForge matrix runs without rerunning
FreshForge, Modelwright generation, or validation.

- [x] P38.1 Define matrix evidence aggregation records. Child issue: #244.
- [x] P38.2 Add aggregation API and compact writers. Child issue: #245.
- [x] P38.3 Add CLI command for matrix evidence packaging. Child issue: #246.
- [x] P38.4 Update docs, examples, and tests. Child issue: #247.
- [ ] P38.5 Verify, PR, deploy docs, and close phase. Child issue: #248.

Dependency note: this phase follows FreshForge `v0.1.0a5` and Modelwright Phase 36. It provides the
generic matrix evidence backend that FABLE Pyculator Phase 25 should consume.

Acceptance boundary:

- May summarize matrix-level generated-model validation evidence from compact FreshForge/Modelwright
  artifacts.
- Must not run FreshForge matrices, generate models, validate workbooks, or infer domain semantics.
- Must not copy raw generated source, raw generated values, source workbooks, or full validation
  reports into compact summaries.

Implementation evidence:

- Added `MatrixEvidencePaths`, `MatrixEvidenceCaseSummary`, and `MatrixEvidenceSummary`.
- Added matrix evidence extraction and writers that read FreshForge matrix JSON and optional per-case
  generated-model artifacts or compact validation summaries.
- Added `modelwright validation matrix-evidence` with matrix run/summary input, artifact root,
  output directory, required-evidence, and JSON options.
- Updated validation-evidence docs, CLI reference, public exports, and tests.

Local verification:

- `.venv/bin/python -m ruff check .` passed.
- `.venv/bin/python -m pytest tests/test_evidence.py tests/test_cli.py tests/test_public_api.py -q`
  passed with 35 tests.
- `.venv/bin/python -m pytest` passed with 202 tests and 1 skipped benchmark.
- `.venv/bin/sphinx-build -q -b html docs _build/html -W` passed.
- `.venv/bin/python scripts/verify_docs_theme.py _build/html` passed.
- `scripts/check_release_artifacts.sh` passed.
- `git diff --check` passed.
