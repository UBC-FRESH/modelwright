# Phase 32 FABLE Pyculator Onboarding And Validation Pilot

Date: 2026-06-22

## Purpose

Phase 32 turns the current Modelwright humane-interface prototype into a structured pilot workflow
for new HQP testers. The pilot should make setup repeatable, make tester feedback easy to capture,
and define an initial validation protocol before deeper FABLE Calculator compatibility work begins.

FABLE Pyculator is a workflow name for FABLE Calculator models converted or wrapped through
Modelwright. It is not a package rename and it is not a production-readiness claim.

## Roles

- Abdulateef focuses on validation runs across multiple FABLE country calculators.
- Gloria and Camilla focus on usability, interface clarity, notebook workflow, and setup friction.
- Greg triages feedback, keeps the public repository clean, and decides which local artifacts can be
  converted into sanitized tracked material.

## Local Artifact Rules

Raw country calculators, downloaded workbooks, generated Python clones, local logs, and full
validation reports stay under ignored `tmp/` paths unless the maintainer explicitly approves a small
sanitized tracked artifact.

Tracked content may include:

- onboarding documentation;
- issue-template structure;
- sanitized validation summaries;
- compact scenario/output manifest examples;
- package or notebook improvements;
- generated Python outputs only when explicitly approved.

Tracked content must not include:

- original FABLE workbook files;
- raw workbook extracts;
- raw validation reports;
- private local paths;
- unpublished workbook details that have not been sanitized.

## Validation Pilot Protocol

For each country calculator validation run:

1. Record calculator provenance in sanitized form: source, country identifier if public, version/date,
   and download date.
2. Store the workbook and raw working files under ignored `tmp/`.
3. Choose four or five scenario variants by changing parameters on the scenario selection sheet.
4. Record the changed parameters or cell references, old values, and new values.
5. Capture selected Excel outputs for key metrics such as GHG emissions or other agreed headline
   outputs.
6. Convert or run the corresponding generated Python workflow through Modelwright.
7. Apply the same input changes in Python.
8. Compare selected outputs and record exact matches, mismatches, blockers, or uncertainty.
9. File a sanitized GitHub issue using the FABLE validation run form.

Do not force a validation run through unclear workbook semantics. If the workflow blocks on external
links, unsupported formulas, macros, volatile behavior, or ambiguous scenario controls, record the
blocker instead.

## Usability Pilot Protocol

For each usability pass:

1. Start from the FABLE Pyculator onboarding guide.
2. Log in to the project JupyterHub and open VSCode/code-server.
3. Authenticate to GitHub, clone Modelwright, create `.venv`, select the notebook kernel, and run one
   tracked notebook.
4. Record every point where setup, naming, notebook text, scenario mutation, DataFrame output,
   provenance, or validation expectations are unclear.
5. File each distinct observation as a GitHub issue using the usability or setup form.

Usability notes are not side comments. They are pilot evidence that should drive P32.5 refinements.

## Scenario Manifest Seed

The seed manifest under `examples/fable_2020/` is a documentation artifact, not a complete validation
framework. Its purpose is to show the minimum structured fields needed to turn manual validation notes
into repeatable evidence later.

Future work may promote the seed into a typed schema or CLI workflow after pilot feedback proves which
fields are actually useful.
