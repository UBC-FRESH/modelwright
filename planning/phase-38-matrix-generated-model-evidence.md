# Phase 38: Matrix Generated-Model Evidence Aggregation

Phase 38 adds generic compact evidence aggregation for FreshForge matrix runs of generated-model
workflows.

The motivating downstream workflow is FABLE Pyculator output-ref strategy and scenario-bundle
matrices, but the Modelwright implementation must remain domain-neutral. Modelwright should only
understand generated-model workflow evidence: case identifiers, run status, compact diagnostics,
artifact directories, comparison counts, and conservative equivalence status.

## Intended Inputs

- FreshForge matrix run JSON or matrix summary JSON.
- Optional per-case Modelwright compact validation-evidence directories.
- Optional artifact root containing per-case generated-model workflow artifacts.

## Intended Outputs

- A compact matrix `summary.json`.
- A compact matrix `summary.md`.
- Per-case status rows with evidence status, equivalence status, comparison counts, diagnostic
  counts, and sanitized artifact references.

## Boundaries

- Do not run FreshForge matrices.
- Do not rerun Modelwright inference, generation, execution, or validation.
- Do not add FABLE output-ref strategy, workbook-version, or scenario semantics.
- Do not copy raw generated source, generated values, source workbook contents, or full validation
  reports into summaries.

## Downstream Dependency

FABLE Pyculator Phase 25 should consume this generic aggregation layer for a FABLE-facing 2021
benchmark matrix evidence cookbook. FreshForge Phase 13 should wait until this and other downstream
work expose concrete generic run/matrix ergonomics gaps.
