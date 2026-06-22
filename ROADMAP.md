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

Active branch: `feature/p29-model-wrapper-templates`

Status: active.

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
- [ ] P29.5 Publish `modelwright==0.1.0a4`. Child issue: #172.
  - [x] Bump package/import version and release docs to `0.1.0a4`.
  - [x] Run local release artifact checks.
  - [ ] Open and merge release PR to `main`.
  - [ ] Create annotated tag `v0.1.0a4`.
  - [ ] Publish through the gated release workflow after maintainer approval.
  - [ ] Verify PyPI JSON, clean PyPI install, import version, CLI help, GitHub release, and docs deployment.

Release boundary:

- May claim an initial wrapper-template API for custom generated-model facades if tests/docs support it.
- Must not claim a full spreadsheet UI, automatic workbook semantic recovery, stable public API
  compatibility, or compact runtime IR production readiness.

## Current Next Steps

1. Open the Phase 29 PR from `feature/p29-model-wrapper-templates` to `main`.
2. Wait for CI to pass and merge the PR.
3. Create annotated tag `v0.1.0a4` from `main`.
4. Publish through the gated release workflow and verify PyPI, GitHub release, and docs deployment.
