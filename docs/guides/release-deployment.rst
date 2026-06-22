Release And Deployment
======================

Modelwright releases are maintainer-controlled. A release is not ready because the version changed;
it is ready only when package artifacts, documentation, benchmark claims, and publication gates have
all been checked.

Current Alpha Target
--------------------

The current alpha target is ``0.1.0a4`` with Git tag ``v0.1.0a4``.

The alpha may claim full comparable-output validation for the 2020 FABLE Calculator benchmark:
281,741 comparable cached workbook outputs, 281,741 matches, and zero mismatches. It may also claim
the measured Phase 27 generated-runtime and generated-source-size improvements recorded in
``planning/phase-27-performance-memory-hardening.md`` and the initial ``modelwright.wrappers``
facade helpers for building analyst-facing wrappers around generated models. It must not claim
full-workbook conversion, a full spreadsheet UI, Excel-backed recalculation equivalence, compact
runtime IR production readiness, or stable public API compatibility.

Local Release Checks
--------------------

Start from a clean checkout and bootstrap the repo-local development environment:

.. code-block:: bash

   scripts/bootstrap_dev_env.sh

Run the normal local checks:

.. code-block:: bash

   .venv/bin/python -m ruff check .
   .venv/bin/python -m pytest -vv
   .venv/bin/sphinx-build -b html docs _build/html -W -v
   .venv/bin/python scripts/verify_docs_theme.py _build/html

Build and inspect package artifacts:

.. code-block:: bash

   scripts/check_release_artifacts.sh

The artifact checker writes outputs under ignored ``tmp/release-checks/``. It builds an sdist and
wheel, runs ``twine check``, inspects artifact contents for private/generated files, installs the wheel
into a clean virtual environment, imports Modelwright, and smoke-tests the installed CLI.

Documentation Deployment Gate
-----------------------------

The docs workflow builds Sphinx documentation and uploads the built HTML artifact to GitHub Pages.
The build must pass ``scripts/verify_docs_theme.py`` so the uploaded artifact uses the Sphinx Read the
Docs theme rather than a non-Sphinx fallback site.

After a release PR merges to ``main``, verify the published GitHub Pages site from the workflow
deployment result. The deployed page should show the Read the Docs side navigation and should not look
like a plain project page.

TestPyPI Rehearsal
------------------

Use the ``Release`` GitHub Actions workflow with ``publish_target`` set to ``testpypi``.

Requirements:

- the ``testpypi`` environment must be configured by the maintainer;
- trusted publishing is preferred;
- no API tokens should be committed to the repository;
- the workflow must build artifacts before publishing them.

After TestPyPI publication, install the package from TestPyPI in a clean environment and run at least:

.. code-block:: bash

   python -m pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ modelwright==0.1.0a4
   python -c "import modelwright; print(modelwright.__version__)"
   modelwright --help

Real PyPI Publication
---------------------

Real PyPI publication requires maintainer approval and the protected ``pypi`` environment.

Expected sequence:

1. Confirm ``CHANGE_LOG.md`` and release notes describe the actual alpha boundary.
2. Confirm local and CI release artifact checks pass.
3. Confirm TestPyPI rehearsal passes or document the exact blocker.
4. Create the annotated tag, for example ``v0.1.0a4``.
5. Run the ``Release`` workflow or push the tag, then approve the protected PyPI environment.
6. Verify the package page, wheel install, import, CLI help, docs deployment, and GitHub release notes.

Rollback And Yanking
--------------------

If a broken alpha reaches PyPI, do not reuse the same version. PyPI artifacts are immutable.

Use one of these responses:

- yank the broken release on PyPI if installation should be discouraged but historical availability is
  still useful;
- publish a new alpha such as ``0.1.0a5`` after fixing the issue;
- update release notes and roadmap entries with the failure mode and mitigation.

Private Data Rules
------------------

Release artifacts must not include source workbooks, generated workbook clones, private evaluation
reports, local logs, credentials, or ignored ``tmp/`` material.
