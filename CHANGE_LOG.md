# CHANGE_LOG.md

This file records completed project work in chronological order.

## 2026-07-02

- Activated Phase 38 on `feature/p38-matrix-generated-model-evidence`, created parent issue #243 and
  child issues #244 through #248, and scoped the phase around generic compact generated-model
  evidence aggregation for FreshForge matrix runs.
- Implemented Phase 38 matrix evidence aggregation by adding compact matrix evidence records,
  extraction/writer helpers, a `modelwright validation matrix-evidence` CLI command, public exports,
  and validation-evidence documentation while keeping FABLE semantics and raw artifacts out of
  Modelwright summaries.
- Verified the Phase 38 implementation locally with Ruff, focused evidence/CLI/API tests, full pytest
  (`202` passed and `1` skipped benchmark), warning-clean Sphinx docs, Read the Docs theme
  verification, release artifact checks, and `git diff --check`.
- Updated the optional FreshForge integration dependency now that FreshForge is published on PyPI:
  `modelwright[freshforge]`, `dev`, and `test` install `freshforge>=0.1.0a5,<0.2` while the core
  Modelwright package remains FreshForge-free.
- Released Modelwright `v0.1.0a8` after PR #240 merged to `main`, post-merge Test workflow
  #28559618570 passed, post-merge Docs Pages workflow #28559618583 passed, annotated tag
  `v0.1.0a8` triggered Release workflow #28559646142, and trusted publishing uploaded
  `modelwright==0.1.0a8` to PyPI.
- Created the GitHub prerelease for `v0.1.0a8` and verified PyPI listed both wheel and sdist
  artifacts.
- Smoke-tested a clean PyPI install of `modelwright[notebook]==0.1.0a8`, including import version,
  `modelwright --help`, `modelwright model infer-contract --help`, and
  `modelwright validation evidence --help`.

## 2026-06-22

- Activated Phase 37 on `feature/v0.1.0a8-release`, created parent issue #235 and child issues #236
  through #239, and scoped the release around publishing the generated-model evidence workflow alpha
  after FreshForge `v0.1.0a3`.
- Prepared the `0.1.0a8` release candidate by bumping package/import metadata, provider metadata
  version, version tests, release docs, README alpha line, and FreshForge installation guidance.
- Verified the `0.1.0a8` release candidate locally with Ruff, `195` passing pytest tests and `1`
  skipped benchmark, warning-clean Sphinx docs, Read the Docs theme verification, release artifact
  checks, CLI help, `modelwright model infer-contract --help`, `modelwright validation evidence
  --help`, and FreshForge provider discovery showing Modelwright provider version `0.1.0a8` with
  FreshForge `v0.1.0a3` installed.
- Activated Phase 36 on `feature/p36-compact-validation-evidence`, created child issues #231, #232,
  #229, #230, and #233 under parent issue #221, and scoped the phase around generic compact
  validation-evidence extraction for downstream automation without FABLE-specific path conventions
  or new equivalence claims.
- Added `modelwright.evidence` with generic validation-evidence path and summary records,
  conservative extraction logic, sanitized JSON/Markdown writers, and a `modelwright validation
  evidence` CLI command for packaging existing generated-model workflow artifacts.
- Verified the Phase 36 implementation locally with targeted evidence/CLI/API tests, Ruff, full pytest
  (`195` passed and `1` skipped benchmark), Sphinx warning-as-error docs, Read the Docs theme
  verification, release artifact checks, and `git diff --check`.
- Completed Phase 36 by merging PR #234, confirming post-merge Test run 28548149402 and docs-pages
  run 28548149355 passed, verifying the live validation-evidence guide on GitHub Pages, and closing
  the Phase 36 issue set.
- Activated Phase 35 on `feature/p35-generated-model-workflow-summaries`, created child issues #223
  through #227 under parent issue #220, and scoped the phase around compact Modelwright stage
  summaries plus sharper FreshForge provider diagnostics for generated-model workflows.
- Added compact `ProviderRunResult.data["summary"]` payloads for Modelwright FreshForge
  `model_infer_contract`, `model_generate`, `model_execute`, and `validation_evaluate` nodes so
  downstream tools can inspect counts and status without parsing raw generated artifacts.
- Added Phase 35 provider diagnostics for empty required output/artifact declarations and
  stage-specific generated-model generation, execution, and validation failures; explicit
  validation failures now fail the FreshForge `validation_evaluate` node.
- Completed Phase 35 by merging PR #228, verifying PR Test workflow run 28547298026 and PR
  docs-pages run 28547298025, then confirming post-merge Test run 28547368269 and docs-pages run
  28547368962 passed and deployed GitHub Pages.
- Activated Phase 33 as a maintainer-approved parallel FreshForge provider pilot on
  `feature/p33-modelwright-freshforge-provider`, created parent issue #205 and child issues #206
  through #210, and scoped a plan-only Modelwright provider that FreshForge can discover, validate,
  inspect, and plan without executing Modelwright or adding a GitHub direct-reference dependency.
- Implemented the Phase 33 FreshForge provider pilot by adding `modelwright.freshforge`, a
  `freshforge.providers` entry point, the public-safe
  `examples/freshforge/generated_model_workflow.yaml`, Sphinx provider-integration docs, API
  reference coverage, and tests for metadata, import boundaries, example planning, and diagnostics.
- Verified Phase 33 locally with Ruff, full pytest, Sphinx warning-as-error docs, docs-theme
  verification, FreshForge `providers` / `validate` / `inspect` / `plan` smoke checks after installing
  FreshForge `v0.1.0a1`, release artifact checks, and `git diff --check`.
- Merged Phase 33 PR #211 to `main`, verified post-merge Test and Docs Pages workflows, confirmed
  GitHub Pages deployment, and closed the Phase 33 child and parent issue set.
- Activated Phase 32 on `feature/p32-fable-pyculator-pilot`, created GitHub parent issue #191 and child issues #192 through #197, and scoped the next `0.1.0a7` alpha around FABLE Pyculator HQP onboarding, structured tester issue forms, a validation pilot protocol, and a scenario/output manifest seed format before deeper country-calculator compatibility work.
- Completed the first Phase 32 onboarding and pilot-infrastructure slice by adding a public FABLE Pyculator onboarding guide for the project JupyterHub/code-server workflow, GitHub issue forms for validation runs, usability observations, and setup problems, a planning protocol for Abdulateef's validation checks plus Gloria and Camilla's usability feedback, and a tracked JSON scenario/output manifest seed for sanitized FABLE validation evidence.
- Added the P32.5 generated-model artifact materialization fix from first-user feedback: `modelwright model infer-contract` now writes the `contract.json`, `expressions.json`, and `constants.json` inputs required by `modelwright model generate` from a workbook plus explicit selected output refs, with Sphinx docs explaining the artifact boundary, FABLE version-pairing expectations, and validation caveats.
- Added a P32.5 generated runtime semantic fix for Excel-style `VLOOKUP` miss handling: generated
  models now propagate bare lookup misses as `#N/A` values while `IFNA` and `IFERROR` still return
  their fallbacks. This unblocked the FABLE Pyculator 2021 full comparable-output validation run.
- Merged P32.5 PR #202, verified post-merge Test and Docs Pages workflows on `main`, confirmed the generated-model artifact guide deployed to GitHub Pages, and closed generated-model materialization issue #201 while leaving broader P32.5 pilot-feedback tracking open.
- Prepared the `0.1.0a7` release candidate by closing the concrete first-user P32.5 feedback loop,
  folding in the Phase 33/34 FreshForge provider planning and execution evidence, bumping
  package/import/provider metadata and release docs, and preserving the alpha boundary around
  selected-output generated-model materialization rather than arbitrary full-workbook conversion.
- Verified the `0.1.0a7` release candidate locally with Ruff, `180` passing pytest tests and `1`
  skipped benchmark, warning-clean Sphinx docs, Read the Docs theme verification, release artifact
  checks, `modelwright --help`, `modelwright model infer-contract --help`, and FreshForge provider
  discovery showing Modelwright provider version `0.1.0a7` with FreshForge `0.1.0a2` installed.
- Published `modelwright==0.1.0a7` to PyPI from annotated tag `v0.1.0a7`, created the matching
  GitHub prerelease, verified PyPI JSON lists the wheel and sdist artifacts, confirmed a clean
  ignored PyPI install of `modelwright[notebook]==0.1.0a7` imports `modelwright 0.1.0a7`, imports
  pandas, and runs `modelwright --help`, and verified the post-merge Test and Docs Pages workflows
  passed for the release PR.
- Activated Phase 31 on `feature/p31-literate-notebook-examples`, created GitHub parent issue #183 and child issues #187, #185, #186, #184, #188, and #189, and scoped the next `0.1.0a6` alpha around actual known-valid literate `.ipynb` notebook files for the synthetic and generated 2020 FABLE examples, plus matching Sphinx Examples Gallery documentation and validation.
- Completed P31.1 through P31.5 by adding real literate Jupyter notebooks under `examples/notebooks/` for the synthetic and generated 2020 FABLE notebook-interface workflows; each notebook includes headings, explanatory markdown, code cells, and stored outputs; Sphinx Examples Gallery pages now link to downloadable `.ipynb` files; and default tests validate notebook JSON, Python kernel metadata, markdown-before-code structure, stored outputs, synthetic notebook execution, and static FABLE notebook validation-boundary output without running the expensive generated FABLE model in default pytest.
- Prepared the `0.1.0a6` release candidate by bumping package/import metadata and release docs, passing repo-local bootstrap, Ruff, default `pytest -vv` with `167` passed and `1` benchmark skip, Sphinx warning-as-error docs with notebook downloads copied, Read the Docs theme verification, and `scripts/check_release_artifacts.sh`; the artifact checker built a roughly `56K` wheel and `2.2M` sdist, included the tracked literate notebooks in the sdist, installed the wheel into a clean ignored environment, imported `modelwright 0.1.0a6`, and smoke-tested the CLI.
- Published `modelwright==0.1.0a6` to PyPI from annotated tag `v0.1.0a6`, created the matching GitHub prerelease, verified PyPI JSON lists the wheel and sdist artifacts, confirmed a clean ignored PyPI install of `modelwright[notebook]==0.1.0a6` imports `modelwright 0.1.0a6`, imports pandas, exposes `modelwright.notebooks.inputs_frame`, confirms the old import is absent, and runs `modelwright --help`, and verified the live GitHub Pages docs serve the Examples Gallery, both notebook example pages, both downloadable `.ipynb` files with `Using project: modelwright` stored output, and `0.1.0a6` release-deployment content.
- Activated Phase 30 on `feature/p30-notebook-dataframe-interface`, created GitHub parent issue #174 and child issues #175, #178, #176, #177, #179, and #180, and scoped the next `0.1.0a5` alpha around an optional pandas-backed notebook/DataFrame layer over `modelwright.wrappers` for live-kernel inspection, scenario mutation, table rendering, and baseline-vs-scenario comparison workflows.
- Completed P30.1 through P30.5 by adding `modelwright.notebooks` with lazy pandas-backed DataFrame helpers for declared inputs, outputs, scenarios, tables, reports, and baseline-vs-scenario comparisons; added a `notebook` optional extra with `pandas>=2` while keeping pandas out of core dependencies; documented the notebook workflow in Sphinx; added always-on synthetic notebook tests plus real generated synthetic model coverage; and extended the opt-in FABLE wrapper benchmark so `MODELWRIGHT_RUN_FABLE_BENCHMARKS=1 .venv/bin/python -m pytest -vv tests/test_fable_wrapper_benchmark.py` passed in 149.67 seconds against ignored local 2020 FABLE artifacts while preserving the existing `281,741` matches and `0` mismatches evidence boundary.
- Added P30.6 release examples scope with a tracked `examples/` directory, a tiny synthetic notebook-interface example, a production-size 2020 FABLE notebook-interface example backed by compressed generated Python output rather than the original workbook, Sphinx Examples Gallery pages linked from the docs index, and lightweight tests that verify example integrity without running the expensive FABLE generated-model calculation in default pytest.
- Prepared the `0.1.0a5` release candidate by bumping package/import metadata and release docs, passing repo-local bootstrap, Ruff, default `pytest -vv` with `163` passed and `1` benchmark skip, Sphinx warning-as-error docs, Read the Docs theme verification, and `scripts/check_release_artifacts.sh`; the artifact checker built a roughly `56K` wheel and `2.2M` sdist, included the compressed FABLE generated-model example in the sdist, installed the wheel into a clean ignored environment, imported `modelwright 0.1.0a5`, and smoke-tested the CLI.
- Published `modelwright==0.1.0a5` to PyPI from annotated tag `v0.1.0a5`, created the matching GitHub prerelease, verified PyPI JSON lists `0.1.0a5` with the `notebook` optional extra, confirmed a clean ignored PyPI install of `modelwright[notebook]==0.1.0a5` imports `modelwright 0.1.0a5`, imports pandas, exposes `modelwright.notebooks.inputs_frame`, and runs `modelwright --help`, and verified the live GitHub Pages docs serve the Examples Gallery, notebook-interface guide, and `0.1.0a5` release-deployment content.
- Activated Phase 29 on `feature/p29-model-wrapper-templates`, created GitHub parent issue #167 and child issues #171, #170, #169, #168, and #172, and scoped initial wrapper-template facades for generated Python models with `0.1.0a4` publication as the final phase closeout task.
- Closed P29.1 by expanding `planning/model-wrapper-template-facades.md` into a concrete initial wrapper API contract covering generated-model boundaries, facade records, declaration helpers, table semantics, scenario mutation, report payloads, provenance preservation, error handling, and alpha API limits.
- Completed P29.2 by adding the initial `modelwright.wrappers` module with `ModelFacade`, `Scenario`, cell/table/report declarations, table and report view payloads, wrapper declaration/execution errors, public package exports, and focused tests for scenario overrides, rectangular table reporting, duplicate declarations, report references, and generated-model error wrapping.
- Completed P29.3 by adding Sphinx documentation for custom generated-model wrapper facades, including examples for facade declarations, scenario input overrides, inspection, rectangular table views, report payloads, and explicit alpha limitations; added `modelwright.wrappers` to the API reference.
- Completed P29.4 by adding an integration-style wrapper test that builds the tracked synthetic workbook, generates a real Modelwright Python module, wraps it with `ModelFacade`, and verifies facade calculations, inspection, tables, and reports preserve generated-model semantics under input overrides; also added an opt-in benchmark-gated wrapper test against the ignored generated 2020 FABLE model, where `MODELWRIGHT_RUN_FABLE_BENCHMARKS=1 .venv/bin/python -m pytest -vv tests/test_fable_wrapper_benchmark.py` passed in 148.96 seconds while wrapping `SCENARIOS selection!D20:D22` from the P26 full-validation report that recorded `281,741` matches and `0` mismatches.
- Prepared the `0.1.0a4` release candidate by bumping package/import metadata and release docs, tightening docs-theme verification to avoid false positives from ordinary `minimal` words, and passing local release checks: Ruff, default `pytest -vv` with `156` passed and `1` benchmark skip, Sphinx warning-as-error docs, Read the Docs theme verification, and `scripts/check_release_artifacts.sh` with clean artifact build, twine check, artifact privacy inspection, clean wheel install, `modelwright 0.1.0a4` import, and CLI smoke test.
- Published `modelwright==0.1.0a4` to PyPI from annotated tag `v0.1.0a4`, created the matching GitHub prerelease, verified PyPI JSON lists the release, confirmed a clean ignored PyPI install imports version `0.1.0a4` and runs `modelwright --help`, and verified the live GitHub Pages release documentation serves the Read the Docs themed `0.1.0a4` wrapper-facade content.

## 2026-06-21

- Activated Phase 22 on `feature/p22-pypi-publication-deployment`, created GitHub parent issue #124 and child issues #125 through #129, and scoped PyPI/TestPyPI publication, release artifact checks, maintainer gates, deployment docs, and GitHub Pages Read the Docs theme verification.
- Drafted the P22.1 alpha release policy: recommend `0.1.0a1`, require local artifact checks and TestPyPI rehearsal before real PyPI, preserve benchmark-claim limits, and keep license selection gated on explicit maintainer approval.
- Approved MIT licensing and the `0.1.0a1` alpha release target, then started P22.2 package metadata and artifact-check hardening.
- Completed P22.2 package metadata hardening with an MIT `LICENSE`, `0.1.0a1` package/import version, release metadata, local artifact checker, clean sdist/wheel metadata checks, artifact privacy inspection, clean wheel install smoke test, and full local ruff/pytest/docs verification.
- Started P22.3 release automation by adding a gated GitHub Actions release workflow and a Sphinx Read the Docs theme artifact verifier for documentation deployment checks.
- Added the P22.4 release and deployment runbook to the Sphinx docs and contributor onboarding notes.
- Recorded P22.5 local release-readiness evidence: ruff, pytest, docs, local RTD theme verification, sdist/wheel build, `twine check`, artifact privacy inspection, and clean wheel install smoke test pass; TestPyPI, real PyPI, and deployed Pages verification remain gated after merge.
- Merged Phase 22 PR #130, verified post-merge CI and release-artifact checks passed, confirmed the live GitHub Pages site serves the Sphinx Read the Docs themed artifact, and closed the Phase 22 publication/deployment workflow setup.
- Attempted the pre-rebrand TestPyPI `0.1.0a1` upload with the ignored local TestPyPI token; artifacts passed local checks, but TestPyPI rejected the upload with `403 Forbidden` while the old TestPyPI project name returned `404`, so the next release operation is to complete the Modelwright rebrand and rehearse publication under the new package name.
- Activated Phase 23 on `feature/p23-modelwright-rebrand`, renamed the GitHub repository to `UBC-FRESH/modelwright`, and scoped a full pre-publication rebrand with no old-name compatibility aliases.
- Completed the local Modelwright rebrand across package metadata, import package, CLI command, generated-code/runtime labels, release workflow artifacts, docs, tests, and planning notes; hardened bootstrap and release checks to remove stale pre-rebrand metadata and reject old package paths or console scripts.
- Verified Phase 23 locally with repo-local bootstrap, ruff, 129 pytest tests, Sphinx warning-as-error docs build, Read the Docs theme verification, and a clean sdist/wheel release artifact check for `modelwright`.
- Merged Phase 23 PR #136, closed the rebrand phase, confirmed post-merge CI and release-artifact checks passed, and verified the live renamed GitHub Pages site at `https://ubc-fresh.github.io/modelwright/` serves the Sphinx Read the Docs themed Modelwright docs.
- Activated Phase 24 on `feature/p24-testpypi-rehearsal`, created GitHub parent issue #137 and child issues #141, #139, #140, and #138, and scoped TestPyPI target checks, artifact upload, clean install verification, and real-PyPI readiness decision evidence for `modelwright==0.1.0a1`.
- Completed the TestPyPI rehearsal for `modelwright==0.1.0a1`: token upload was rejected with `403 Forbidden`, GitHub Actions trusted publishing succeeded, TestPyPI published the package, and a clean ignored virtual environment installed from TestPyPI, imported `modelwright`, ran `modelwright --help`, and confirmed old `sheetforge` import/CLI surfaces were absent.
- Published `modelwright==0.1.0a1` to real PyPI from annotated tag `v0.1.0a1` using the GitHub Actions `Release` workflow and trusted publishing; verified PyPI JSON lists the release and a clean ignored virtual environment installed from PyPI, imported `modelwright`, ran `modelwright --help`, and confirmed old `sheetforge` import/CLI surfaces were absent.
- Activated Phase 26 full FABLE benchmark validation on `feature/p26-full-fable-validation`, defined the full cached-output validation contract, ran verbose full-scale 2020 FABLE extraction/graph/translation/inference passes, and recorded that extraction, graphing, and translation are clean at full scale while generated-model materialization is blocked by cyclic workbook dependencies in contract inference.
- Added verbose progress hooks for graph construction, contract inference, Python generation, and generated-model runtime execution; added generation support for Excel's two-argument `IF(test, value_if_true)` form; added boolean validation comparison support; and hardened contract inference around range dependencies, sparse blank cells, renderability diagnostics, and de-duplicated cycle diagnostics.
- Resolved the targeted FABLE `3_calc_crops!AO29` semantic mismatch by switching generated models to lazy runtime evaluation for static-cycle tolerance, fixing Excel-style case-insensitive and numeric-text criteria matching, ignoring text/blank `SUMIF(S)` sum values, and verifying a cached AO29 smoke run that matched `27844.896576581647` exactly with matching upstream probes.
- Achieved the Phase 26 full comparable-output validation pass for the 2020 FABLE Calculator benchmark: the generated Modelwright Python model matched 281,741 of 281,741 comparable cached workbook outputs with zero mismatches, while 15,235 cached blank formula outputs were recorded as non-comparable validation-boundary evidence rather than blockers.
- Prepared the `0.1.0a2` release candidate with updated package/import version, release-boundary documentation, repeatable release artifact cleanup, local Ruff, 145-test pytest, Sphinx warning-as-error docs, Read the Docs theme verification, and clean sdist/wheel artifact checks.
- Published `modelwright==0.1.0a2` to PyPI from annotated tag `v0.1.0a2`, created the matching GitHub release, verified PyPI JSON lists the release, and confirmed a clean ignored PyPI install imports version `0.1.0a2` and runs `modelwright --help`.
- Activated Phase 27 on `feature/p27-performance-memory-hardening`, created GitHub child issues #155 through #160 under parent issue #152, and scoped the phase around measured profiling evidence before any performance, memory, parallelism, or generated-output architecture changes.
- Completed the P27.1 baseline profile against the Phase 26 generated FABLE model: import takes about 35 seconds and 10.7 GiB maximum RSS before calculation, full profiled execution takes about 1,502 seconds, and the dominant runtime signals are repeated range/criteria work including 605,817 `_range` calls, 364,236,641 addressed range cells, 199,343 `_sf_sumifs` calls, and 121,247,129 criteria-match calls.
- Completed P27.2 range and criteria optimization by adding generated range views, reused range materialization, precompiled criteria matchers, and cached numeric coercion; optimized full FABLE validation still passed with 281,741 of 281,741 comparable outputs matching, while generated execution dropped from the P26 baseline of 1,469.944 seconds to 183.463 seconds.
- Completed the first P27.3 generated-size slice by disabling inline formula provenance comments for large generated modules: the 2020 FABLE generated source dropped from about 198.8 MB to 132.3 MB and still matched 281,741 of 281,741 comparable outputs, while import time and memory remained roughly 34 seconds and 10.6 GiB, leaving formula/output source layout as the next import-overhead target.
- Added P27.3 generated output-map compaction so large modules return `{cell_ref: _get(cell_ref) for cell_ref in _output_refs}` instead of repeating every output reference twice; combined compact source size dropped to about 124.1 MB, full 2020 FABLE comparison still matched 281,741 of 281,741 outputs, and import remained roughly 34 seconds and 10.2 GiB.
- Closed P27.3 by adding expression-source formula storage for large generated modules: compact-lambda cold import measured 34.370 seconds and 10,518,600 KiB RSS, while expression-source cold import measured 4.898 seconds and 1,381,648 KiB RSS; direct expression-source import plus `calculate()` returned 281,741 outputs in 151.616 seconds with 1,380,728 KiB RSS, and full cached FABLE comparison still matched 281,741 of 281,741 outputs.
- Started P27.4 memory-stage profiling and identified graph/inference residency as the dominant remaining full-process memory source: graph hydration holds about 10,182,548 KiB RSS for 3,543,800 edges, inference hydration pushes current RSS to about 11,850,248 KiB, while generated execution and comparison add comparatively little and still produce 281,741 matches with zero mismatches.
- Prototyped a P27.4 slim-oracle validation path under ignored local artifacts: a 23.66 MB oracle file plus the expression-source generated model reran the full 281,741-output FABLE comparison with zero mismatches, dropping recurring validation peak RSS from about 12,981,284 KiB in the all-in-one debug process to about 1,564,740 KiB.
- Closed P27.4 by deciding not to add a separate public slim-oracle CLI/API contract before the compact runtime IR backend; the slim validation prototype is retained as benchmark-artifact evidence for future runtime IR design.
- Activated P27.5 to evaluate multicore and sharded execution options only where the P27 measurements still justify them, with caution around duplicating large graph/inference memory or breaking generated-model lazy evaluation semantics.
- Added P27.5 production inference fixes after profiling the real bottleneck: ordered membership tracking and non-eager range-dependency expansion caching reduced uncached full 2020 FABLE contract inference from 224.001 seconds after the first fix to 46.237 seconds after the range-cache fix, while preserving 373,410 inferred symbols, 289,951 expressions, 83,459 constants/inputs, and 1,808 static-cycle diagnostics.
- Closed P27.5 with a no-new-parallelism decision for this phase: formula rendering and scalar comparison were too small to shard, naive generated-output sharding duplicated broad dependency work and memory, and the remaining costs are better assigned to full P27.6 validation evidence plus compact runtime IR and benchmark-artifact design.
- Activated P27.6 to rerun the full 2020 FABLE validation with current P27 production changes, verbose logs, refreshed inference, cache-hit behavior, runtime measurements, memory observations, and full comparable-output correctness evidence.
- Completed P27.6 full-validation evidence: refreshed-inference validation passed with 281,741 of 281,741 comparable outputs matching, current generated source measured 122,318,322 bytes, inference took 46.645 seconds, generation took 10.219 seconds, generated execution took 154.477 seconds, total elapsed time was 419.672 seconds, and a timed cache-hit validation rerun also passed with 13,224,896 KiB maximum RSS while showing inference cache load took 47.978 seconds versus 46.645 seconds to recompute.
- Activated Phase 28 on `feature/p28-v0.1.0a3-release`, created GitHub parent issue #162 and child issues #165, #164, and #163, and bumped package/import metadata plus release docs toward the `0.1.0a3` alpha release that packages the Phase 27 performance and memory hardening evidence.
- Completed P28.2 local release verification for `0.1.0a3`: Ruff, `git diff --check`, 150-test pytest, Sphinx warning-as-error docs build, Read the Docs theme verification, and `scripts/check_release_artifacts.sh` passed; the artifact checker built and inspected sdist/wheel contents, ran `twine check`, installed the wheel into a clean ignored environment, imported `modelwright 0.1.0a3`, and smoke-tested the CLI.
- Published `modelwright==0.1.0a3` to PyPI from annotated tag `v0.1.0a3`, created the matching GitHub prerelease, verified PyPI JSON lists the release, confirmed a clean ignored PyPI install imports version `0.1.0a3` and runs `modelwright --help`, and verified the live GitHub Pages release documentation serves the Read the Docs themed `0.1.0a3` content.

## 2026-06-20

- Added validation report core objects for comparison records, diagnostics, report status, mismatch extraction, and JSON-serializable boundaries.
- Added the tracked synthetic fixture builder, baseline scenario JSON, expected output JSON, and tests that generate the workbook in a pytest temporary directory.
- Added baseline and intentional numeric mismatch regression tests using the synthetic fixture assets and validation report core.
- Added the first default GitHub Actions workflow for editable install and `python -m pytest`.
- Opened Phase 6 PR #41 from `feature/p6-initial-package-validation-core` back to `main`.
- Merged Phase 6 PR #41, closed parent issue #34, and activated Phase 7 on `feature/p7-validation-scenario-comparison-core`.
- Expanded the roadmap and GitHub issue backlog through Phase 15, with the long-term sequence recorded in `planning/long-term-roadmap.md`.
- Added validation scenario objects and a JSON loader for fixture-backed validation scenario files.
- Added scalar comparison helpers for numeric tolerance, exact text, missing outputs, and unsupported output diagnostics.
- Added a validation report builder that compares scenario outputs from observed generated and oracle value mappings.
- Closed the Phase 7 validation-core planning loop by recording Phase 8 extraction inputs in `planning/phase-7-closeout-phase-8-inputs.md`.
- Opened Phase 7 PR #79 from `feature/p7-validation-scenario-comparison-core` back to `main`.
- Merged Phase 7 PR #79, closed parent issue #42, and activated Phase 8 on `feature/p8-workbook-extraction-core`.
- Added extraction record objects for workbooks, sheets, cells, formulas, named ranges, and extraction diagnostics.
- Added `openpyxl` workbook extraction for sheets, non-empty cells, formulas, named ranges, and initial extraction diagnostics.
- Closed the Phase 8 extraction-core planning loop by recording Phase 9 dependency graph inputs in `planning/phase-8-closeout-phase-9-inputs.md`.
- Opened Phase 8 PR #80 from `feature/p8-workbook-extraction-core` back to `main`.
- Merged Phase 8 PR #80, closed parent issue #50, and activated Phase 9 on `feature/p9-dependency-graph-core`.
- Added a canonical workbook reference model and normalization helpers for cells, ranges, named ranges, external references, and unresolved references.
- Added dependency graph records and graph building from extracted formula references, including named-range resolution and semantic/execution edges.
- Added dependency graph diagnostics coverage for ranges, external references, and simple circular dependencies.
- Closed the Phase 9 dependency-graph planning loop by recording Phase 10 formula translation inputs in `planning/phase-9-closeout-phase-10-inputs.md`.
- Opened Phase 9 PR #81 from `feature/p9-dependency-graph-core` back to `main`.
- Merged Phase 9 PR #81, closed parent issue #49, and activated Phase 10 on `feature/p10-formula-translation-core`.
- Added formula expression records for literals, references, binary arithmetic, comparisons, function calls, and translation diagnostics.
- Added formula translation for the supported synthetic workbook subset, including references, named ranges, arithmetic, `ROUND`, `IF`, and `>`.
- Added formula translation diagnostics coverage for unsupported functions and unsupported operators.
- Closed the Phase 10 formula-translation planning loop by recording Phase 11 generated-model inputs in `planning/phase-10-closeout-phase-11-inputs.md`.
- Opened Phase 10 PR #82 from `feature/p10-formula-translation-core` back to `main`.
- Merged Phase 10 PR #82, closed parent issue #48, and activated Phase 11 on `feature/p11-generated-python-model-core`.
- Added generated Python module contract records, generation result records, generated symbol provenance, and cell-reference symbol naming.
- Added standalone Python module generation from translated workbook logic, with provenance comments and generated-output tests using temporary files.
- Closed the Phase 11 generated-model planning loop by recording Phase 12 oracle-backed validation inputs in `planning/phase-11-closeout-phase-12-inputs.md`.
- Opened Phase 11 PR #83 from `feature/p11-generated-python-model-core` back to `main`.
- Merged Phase 11 PR #83, closed parent issue #47, and activated Phase 12 on `feature/p12-oracle-backed-validation`.
- Added oracle interface records and the optional `formulas` dependency boundary for oracle-backed validation.
- Added a `formulas`-backed oracle for synthetic workbook outputs with JSON scalar normalization and unsupported-input diagnostics.
- Added oracle-backed validation report assembly for generated synthetic model outputs and recorded Phase 13 private-workbook evaluation inputs.
- Opened Phase 12 PR #84 from `feature/p12-oracle-backed-validation` back to `main`.
- Merged Phase 12 PR #84 and closed parent issue #54.
- Activated Phase 13 on `feature/p13-real-workbook-evaluation-lane`.
- Defined the private workbook evaluation protocol for ignored local inputs, sanitized tracked notes, local commands, and stop conditions.
- Ran the first private workbook evaluation locally under ignored `tmp/`, added a generic unresolved defined-name extraction fix, and recorded package extraction runtime as the first private-workbook blocker.
- Extended private-workbook evaluation support with sparse populated-cell extraction, verbose extraction progress hooks, indexed formula-reference lookup, and generated-subset validation against cached workbook outputs.
- Recorded sanitized `eval-001` findings, including generated-subset validation results and the structured-reference blocker for the pure-Python oracle.
- Opened Phase 13 PR #85 from `feature/p13-real-workbook-evaluation-lane` back to `main`.
- Merged Phase 13 PR #85 and closed parent issue #52.
- Activated Phase 14 on `feature/p14-cli-api-stabilization`.
- Reviewed Python API boundaries, documented stable/provisional entrypoints, and narrowed the package-root facade to primary workflow records and functions.
- Added thin JSON CLI command groups for extraction, dependency graph building, generated Python module creation, and validation report assembly.
- Documented the CLI JSON workflows, command expectations, and stabilization decisions.
- Opened Phase 14 PR #86 from `feature/p14-cli-api-stabilization` back to `main`.
- Merged Phase 14 PR #86 and closed parent issue #53.
- Activated Phase 15 on `feature/p15-hardening-release-prep`.
- Decided the Phase 15 hardening tooling boundary: keep `pytest`, add at most a lightweight lint lane next, and defer formatter, type checker, coverage threshold, and pre-commit hooks.
- Added a minimal Ruff quality extra, CI quality job, local quality-check documentation, and release metadata deferral note.
- Summarized release readiness, unsupported workbook semantics, and the next roadmap horizon through Phases 16-19 with mirrored GitHub issues.
- Revised the next roadmap horizon so Phase 16 prioritizes FRESH-style Typer/Rich CLI alignment and full Sphinx GitHub Pages documentation modeled on local `fhops` and `femic` repositories.
- Merged Phase 15 PR #102 and closed parent issue #51.
- Activated Phase 16 on `feature/p16-cli-docs-public-surface`.
- Recorded Modelwright-specific Phase 16 CLI and Sphinx documentation acceptance criteria from the local `fhops` and `femic` reference packages.
- Refactored the CLI to a tight Typer/Rich command surface with grouped `workbook`, `model`, and `validation` workflows.
- Added full Sphinx documentation with curated guide/reference pages and a GitHub Pages workflow that builds on pull requests and deploys on pushes to `main`.
- Added repo-root `.venv` bootstrap tooling plus contributor and developer-onboarding documentation for repeatable local setup.
- Verified the Phase 16 CLI/docs surface locally and recorded Phase 17 real-workbook formula-semantics inputs.
- Opened Phase 16 PR #108 from `feature/p16-cli-docs-public-surface` back to `main`, verified PR checks for tests, quality, and docs build, and confirmed the post-merge `main` docs Pages deployment succeeded.
- Merged Phase 16 PR #108, closed parent issue #89, and activated Phase 17 on `feature/p17-real-workbook-formula-semantics`.
- Prioritized Phase 17 real-workbook semantics gaps and selected structured-reference extraction diagnostics as the next implementation slice.
- Added first-class structured-reference diagnostics across reference normalization, workbook extraction, dependency graphing, and formula translation blocking.
- Expanded Phase 17 planning with the sanitized private-workbook formula-function, operator, and token scope needed for full sample-workbook import.
- Codified the Phase 17 blocker-find-resolve-rerun loop for private-workbook formula semantics and validation evidence.
- Added explicit Phase 17 convergence metrics, pass/fail rules, and implementation priority order for private-workbook import progress.
- Added P17.3 pass-one support for boolean literals, unary minus, `^`, `&`, and `#REF!` diagnostics, plus a tracked supported-semantics fixture harness and sanitized convergence note.
- Added P17.3 pass-two support for scalar/range functions, supported table structured references, table metadata extraction, unresolved structured-reference fast-fail behavior, and expanded supported-semantics fixture coverage; the sanitized private pass increased translated formulas to 72,437 and kept cached generated validation at 10 outputs with 0 mismatches.
- Added P17.3 pass-three support for `SUMIF`, `SUMIFS`, `COUNTIF`, and `COUNTIFS`; the sanitized private pass increased translated formulas to 185,128 and reduced remaining unsupported-function first failures to `VLOOKUP` and `OFFSET`.
- Added P17.3 pass-four support for `VLOOKUP` and table-array structured references; the sanitized private pass increased translated formulas to 209,394 and left `OFFSET`, remaining structured references, explicit error references, and oracle calculation failure as residual blockers.
- Added P17.3 pass-five support for constrained cross-table current-row structured references; the sanitized private pass increased translated formulas to 215,202, cleared structured-reference first failures, and left `OFFSET`, explicit error references, and oracle calculation failure as residual blockers.
- Added P17.3 pass-six support for constrained static `OFFSET` translation; the sanitized private pass increased translated formulas to 215,422, cleared unsupported-function first failures, and left explicit error references plus oracle calculation failure as residual blockers for closeout.
- Closed Phase 17 with sanitized final diagnostics, classified explicit error references and oracle calculation failure as residual blockers, and recorded Phase 18 conversion-planning inputs.
- Shifted the primary private benchmark direction to the 2020 workbook after cross-version inspection showed the 2019 workbook contains explicit broken references; the 2020 baseline translated 296,319 of 296,976 formulas and exposed `_XLFN.IFNA` as the next formula-semantics blocker.
- Merged Phase 17 PR #109, closed parent issue #88, and activated Phase 18 on `feature/p18-conversion-planning-pipeline`.
- Defined the Phase 18 conversion plan contract for partial-conversion reporting, residual blocker classification, benchmark roles, generation summaries, validation summaries, and privacy review boundaries.
- Added `_XLFN.IFNA` normalization and generated `IFNA` semantics; the 2020 private benchmark now translates 296,976 of 296,976 formulas with no translation diagnostics while cached generated subset validation remains at 10 outputs with 0 mismatches.
- Added package conversion-plan records and `build_conversion_plan` for P18.2, including coverage summaries, diagnostic summaries, residual blocker classification, generation summaries, validation summaries, recommendations, API docs, and focused tests.
- Promoted the public FABLE Calculator workbooks to official external benchmark status by tracking the source URL, local placement instructions, roles, and checksums while keeping workbook binaries untracked under ignored `tmp/`.
- Added a benchmark materialization helper that downloads or consumes a local Dropbox ZIP/directory, verifies the public FABLE workbook payloads by checksum, and writes them to canonical ignored paths.
- Added a `dev` dependency extra and linked benchmark materialization into the repo-local bootstrap ritual through `scripts/bootstrap_dev_env.sh --benchmarks`.
- Added the P18.3 `modelwright conversion plan` CLI command for JSON conversion-plan reports over extraction, dependency graphing, and formula translation.
- Standardized the Sphinx documentation build on the Read the Docs theme used by the other FRESH lab packages.
- Expanded conversion-plan residual-blocker classification across extraction, named ranges, formula extraction, graphing, validation, and generation diagnostics.
- Closed Phase 18 with synthetic and 2020 FABLE conversion-plan workflow evidence and recorded Phase 19 validation automation inputs.
- Re-scoped Phase 19 around residual blocker resolution for the 2020 FABLE benchmark and moved broad validation/evaluation automation to Phase 20.
- Resolved P19.1 named-range blockers by supporting table-column structured-reference defined names and classifying remaining `#REF!` defined-name diagnostics as source workbook defects.
- Marked the unreferenced `ProductList` defined-name `#REF!` defect as stale workbook metadata rather than an active conversion blocker.
- Resolved the P19.2 circular dependency blocker by aligning dependency-graph execution edges with constrained static `OFFSET` semantics; the 2020 FABLE conversion plan now reports empty graph diagnostics and 296,976 of 296,976 formulas translated.
- Resolved P19.3 residual policy classification so supported structured-reference and volatile-function extraction diagnostics are treated as provenance, while external dependencies and missing cached values have explicit deferred validation/conversion owners.
- Closed Phase 19 with a final verbose 2020 FABLE conversion-plan rerun showing empty graph and translation diagnostics, 296,976 of 296,976 formulas translated, and all remaining residual blockers resolved, out of scope, or assigned to Phase 20 validation/generation owners.
- Merged Phase 19 PR #111, closed parent issue #103, and activated Phase 20 on `feature/p20-automated-validation-reports`.
- Created the Phase 20 validation/evaluation plan and mirrored the phase/task structure into GitHub issues #112 through #116.
- Added the P20.1 generated-model execution API with structured execution diagnostics, JSON-serializable observed outputs, package facade exports, API docs, and synthetic tests.
- Added P20.2 validation orchestration over generated outputs, cached workbook values, and optional oracle results, preserving missing cached values and oracle failures as explicit validation evidence.
- Added P20.3 CLI commands for generated model execution and validation evaluation JSON reports, with verbose progress on stderr and documented workflow boundaries.
- Closed P20.4 by running a verbose synthetic generated-model evaluation through the CLI and a verbose 2020 FABLE benchmark boundary run, proving synthetic generated-model validation and preserving the 2020 benchmark's clean extraction, graph, and translation status while explicitly deferring full workbook equivalence to Phase 21 generated-model materialization and validation.
- Merged Phase 20 PR #117, closed parent issue #112, and activated Phase 21 on `feature/p21-full-benchmark-model-validation` with parent issue #118 and child issues #119 through #122.
- Added P21.1 generated-model contract inference from workbook records, dependency graphs, translated expressions, and selected output refs, with synthetic tests proving inferred contracts generate and execute the controlled fixture model.
- Closed P21.2 by materializing a selected 2020 FABLE generated Python model under ignored local artifacts, using ten cached benchmark outputs, 20 inferred symbols, 10 input constants, no inference/generation diagnostics, and a successful generated-model execution smoke test.
- Closed P21.3 by validating the selected 2020 FABLE generated model through the public CLI against cached workbook values, with ten passing comparisons, zero mismatches, and zero validation diagnostics.
- Closed P21.4 by recording the convergence boundary: selected-output equivalence is proven for ten cached 2020 FABLE `SCENARIOS definition` outputs, while full-workbook equivalence, oracle-backed recalculation equivalence, and external dependency behavior remain unproven next targets.

## 2026-06-19

- Bootstrapped the repository with a lightweight project overview, agent working contract, roadmap, changelog, planning directory, and ignore rules.
- Established `tmp/` as ignored local working space for private notes, source workbooks, scratch experiments, and generated outputs.
- Documented that no Python package, CLI, dependency manager, test framework, or CI contract exists yet.
- Added the first Phase 1 research note comparing workbook extraction, formula evaluation, dependency graph, code-generation, and Excel-backed validation options.
- Ran the first ignored synthetic workbook prototype with `openpyxl`, `formulas`, and `networkx`, then recorded findings in `planning/first-prototype-findings.md`.
- Defined the first prototype workbook IR contract in `planning/workbook-ir-contract.md`.
- Reorganized `ROADMAP.md` into phase/task structure, mirrored phases and tasks into GitHub issues #1 through #30, closed completed Phase 0 and Phase 1 issues, and activated Phase 2 on `feature/p2-workbook-extraction-contracts`.
- Built an ignored IR emitter prototype for the synthetic workbook, verified the emitted JSON against the IR contract, and recorded findings in `planning/ir-prototype-findings.md`.
- Closed the Phase 2 extraction-contract planning loop by recording Phase 3 code-generation inputs in `planning/phase-2-closeout-phase-3-inputs.md`.
- Opened Phase 2 PR #31 from `feature/p2-workbook-extraction-contracts` back to `main`.
- Merged Phase 2 PR #31, closed parent issue #9, and activated Phase 3 on `feature/p3-code-generation-prototype`.
- Defined the Phase 3 generated-code prototype contract in `planning/generated-code-prototype-contract.md`.
- Built an ignored generated-code prototype from the IR, verified it computes `Summary!B2 = 70.2` and `Summary!B3 = "ok"`, and recorded findings in `planning/codegen-prototype-findings.md`.
- Compared the ignored generated model against `formulas`, confirmed both controlled outputs match, and recorded findings in `planning/codegen-comparison-findings.md`.
- Closed the Phase 3 generated-code planning loop by recording Phase 4 validation inputs in `planning/phase-3-closeout-phase-4-inputs.md`.
- Opened Phase 3 PR #32 from `feature/p3-code-generation-prototype` back to `main`.
- Merged Phase 3 PR #32, closed parent issue #14, and activated Phase 4 on `feature/p4-regression-validation`.
- Defined the Phase 4 validation scenario and oracle contract in `planning/validation-scenario-oracle-contract.md`.
- Built an ignored validation prototype, verified the baseline scenario passes with no mismatches, and recorded findings in `planning/validation-prototype-findings.md`.
- Defined validation mismatch diagnostics and tolerance rules in `planning/mismatch-diagnostics-tolerance-rules.md`.
- Closed the Phase 4 validation planning loop by recording Phase 5 package/API/CLI inputs in `planning/phase-4-closeout-phase-5-inputs.md`.
- Opened Phase 4 PR #33 from `feature/p4-regression-validation` back to `main`.
- Merged Phase 4 PR #33, closed parent issue #19, and activated Phase 5 on `feature/p5-package-api-cli-ci-decisions`.
- Chose the initial package, dependency, and test stack in `planning/package-dependency-test-stack-decision.md`.
- Defined initial Python API and deferred CLI boundaries in `planning/api-cli-boundary-decision.md`.
- Defined the initial fixture and regression-test strategy in `planning/fixture-regression-test-strategy.md`.
- Defined the first CI and documentation verification boundary in `planning/ci-docs-verification-decision.md`.
- Summarized the Phase 5 implementation bootstrap plan in `planning/implementation-bootstrap-plan.md` and created the planned Phase 6 issue sequence.
- Opened Phase 5 PR #40 from `feature/p5-package-api-cli-ci-decisions` back to `main`.
- Merged Phase 5 PR #40, closed parent issue #24, and activated Phase 6 on `feature/p6-initial-package-validation-core`.
- Added the initial package and test skeleton with `pyproject.toml`, `src/modelwright`, `tests`, and documented local test commands.
- Activated Phase 34 on `feature/p34-freshforge-executable-provider` with parent issue #213 and
  child issues #214 through #218 for executable FreshForge provider contracts, generated-model node
  execution, synthetic run tests, docs, and closeout.
- Updated `modelwright.freshforge` so supported generated-model workflow nodes can execute through
  Modelwright Python APIs when FreshForge's serial local runner is installed, while preserving the
  normal import boundary and PyPI-safe dependency metadata.
- Added synthetic FreshForge run coverage proving `model_infer_contract`, `model_generate`,
  `model_execute`, and `validation_evaluate` can materialize JSON/model artifacts and pass cached
  validation for the controlled workbook fixture.
- Verified Phase 34 locally with Ruff, full pytest, warning-clean Sphinx docs, Read the Docs theme
  verification, release-artifact checks, and `git diff --check`.
- Merged Phase 34 PR #219, verified PR checks and post-merge docs deployment, and closed the Phase
  34 issue set.
- Created Modelwright parent issues #220 and #221 and recorded planned roadmap phases for generated
  workflow summaries/provider diagnostics and compact validation evidence extraction needed by the
  downstream CLEWs-C2020 FreshForge/FABLE Pyculator automation lane.
- Added `planning/phase-35-36-downstream-automation-chain.md` and expanded the Phase 35/36 roadmap
  entries to record their dependency on FreshForge Phase 7 and their downstream role in FABLE
  Pyculator output-ref strategy comparisons and opt-in benchmark evidence workflows.
