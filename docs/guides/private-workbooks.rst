Private Workbooks
=================

Private source workbooks, raw extracts, generated clones, logs, and validation reports are local working
artifacts. They should remain under ignored ``tmp/`` paths unless the maintainer explicitly approves a
small sanitized tracked artifact.

Official External Benchmarks
----------------------------

Some real workbooks are public benchmark inputs but still should not be committed as binary files. For
those cases, Modelwright tracks benchmark metadata, source URLs, expected filenames, roles, and checksums
under ``benchmarks/`` while keeping the downloaded workbooks under ignored ``tmp/`` paths.

The FABLE Calculator benchmark set is tracked this way:

.. code-block:: text

   benchmarks/fable-calculator/

The workbook files are restored locally under ``tmp/private-workbooks/`` and verified with the tracked
checksum file.

Materialize the files from the tracked benchmark manifest:

.. code-block:: bash

   scripts/bootstrap_dev_env.sh --benchmarks

If the Dropbox folder ZIP has already been downloaded manually, use:

.. code-block:: bash

   .venv/bin/python scripts/materialize_fable_benchmarks.py --from-zip path/to/downloaded-folder.zip

The helper identifies workbook payloads by checksum and writes the standard filenames expected by the
benchmark scaffolding.

Recommended local layout:

.. code-block:: text

   tmp/
     private-workbooks/
     private-evaluations/
     generated-models/
     logs/

Tracked documentation may summarize private evaluation findings only after removing workbook names,
worksheet names, formulas, values, business meaning, and raw output payloads.

Safe tracked notes should focus on:

- sanitized counts;
- unsupported feature categories;
- runtime and stop conditions;
- validation status;
- follow-up implementation priorities.

Unsafe tracked content includes:

- raw workbook files;
- raw formulas;
- raw cell values;
- private paths;
- generated Python clones of private workbooks;
- full validation reports from private workbooks.
