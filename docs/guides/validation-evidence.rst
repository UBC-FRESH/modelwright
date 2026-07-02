Compact Validation Evidence
===========================

Modelwright can package compact validation evidence from generated-model workflow artifacts that
already exist on disk. This is useful when a downstream package or CI job needs a small, sanitized
summary of a generated-model run without copying raw generated source, raw generated output values,
source workbook contents, or full validation reports.

The packaging step is extraction-only. It does not infer a contract, generate Python, execute the
generated model, evaluate a workbook, or rerun a benchmark.

Expected Artifacts
------------------

By default, Modelwright looks under ``tmp/generated-model`` for:

- ``inference-result.json`` from ``modelwright model infer-contract``;
- ``generation-result.json`` from ``modelwright model generate``;
- ``generated-values.json`` from generated-model execution;
- ``validation-scenario.json`` describing declared validation outputs;
- ``evaluation-report.json`` from ``modelwright validation evaluate``.

The default output directory is ``tmp/validation-evidence/generated-model``. The command writes:

- ``summary.json`` for machine-readable automation;
- ``summary.md`` for lightweight human review.

CLI Usage
---------

.. code-block:: bash

   modelwright validation evidence \
     --evidence-id generated-model \
     --artifact-dir tmp/generated-model \
     --output-dir tmp/validation-evidence/generated-model \
     --json

Use ``--scenario`` when the validation scenario JSON lives outside the artifact directory:

.. code-block:: bash

   modelwright validation evidence \
     --artifact-dir tmp/generated-model \
     --scenario tmp/scenarios/baseline.json \
     --output-dir tmp/validation-evidence/baseline

Missing artifacts are skipped by default so optional evidence workflows can run cleanly in
environments where ignored local artifacts have not been restored. Add ``--require-artifacts`` when
the command should fail instead:

.. code-block:: bash

   modelwright validation evidence \
     --artifact-dir tmp/generated-model \
     --require-artifacts

Matrix Evidence
---------------

FreshForge matrix runs can produce one generated-model workflow per case. Modelwright can aggregate
those saved matrix records into a compact matrix-level evidence package:

.. code-block:: bash

   modelwright validation matrix-evidence \
     --evidence-id generated-model-matrix \
     --matrix-run tmp/matrix-run.json \
     --artifact-root tmp/generated-model-matrix \
     --output-dir tmp/validation-evidence/generated-model-matrix \
     --json

The matrix command is also extraction-only. It does not run FreshForge, generate models, execute
generated code, or validate workbooks. It reads a saved FreshForge matrix run or matrix summary and
then looks for per-case generated-model artifacts under ``--artifact-root``. For each case,
Modelwright checks ``<artifact-root>/<case-id>`` and then ``<artifact-root>/<namespace>`` when the
FreshForge namespace is relative.

The output is again compact:

- matrix-level ``summary.json`` and ``summary.md``;
- one sanitized row per matrix case;
- evidence/equivalence status per case;
- comparable, match, and mismatch counts when available.

Use ``--require-evidence`` when every matrix case must have generated-model evidence:

.. code-block:: bash

   modelwright validation matrix-evidence \
     --matrix-summary tmp/matrix-summary.json \
     --artifact-root tmp/generated-model-matrix \
     --require-evidence

Status Rules
------------

``evidence_status`` is conservative:

- ``skipped`` means one or more expected artifacts are missing and missing artifacts were allowed;
- ``incomplete`` means artifacts exist but explicit comparison counts are unavailable;
- ``complete`` means comparison counts are available and support a pass/fail equivalence status.

``equivalence_status`` is even stricter:

- ``pass`` only when comparable output count equals match count and mismatch count is zero;
- ``fail`` when explicit counts show mismatches or missing matches;
- ``incomplete`` when the comparison counts are unavailable.

A successful generated-model execution by itself is not treated as zero-mismatch evidence. The
summary must include explicit comparable-output, match, and mismatch counts from validation evidence.

Python API
----------

.. code-block:: python

   from modelwright import (
       extract_matrix_evidence,
       extract_validation_evidence,
       matrix_evidence_paths,
       validation_evidence_paths,
       write_matrix_evidence,
       write_validation_evidence,
   )

   paths = validation_evidence_paths(
       evidence_id="synthetic-baseline",
       artifact_dir="tmp/generated-model",
       output_dir="tmp/validation-evidence/synthetic-baseline",
   )
   summary = extract_validation_evidence(paths)
   write_validation_evidence(summary, paths)

   matrix_paths = matrix_evidence_paths(
       evidence_id="strategy-matrix",
       matrix_run_path="tmp/matrix-run.json",
       artifact_root="tmp/generated-model-matrix",
       output_dir="tmp/validation-evidence/strategy-matrix",
   )
   matrix_summary = extract_matrix_evidence(matrix_paths)
   write_matrix_evidence(matrix_summary, matrix_paths)

Boundary
--------

Compact evidence is meant for publication, CI summaries, and downstream orchestration. It is not a
replacement for raw local validation artifacts while debugging. Keep raw workbooks, generated source,
generated values, and full validation reports under ignored working directories unless a later roadmap
phase explicitly approves a sanitized tracked artifact.
