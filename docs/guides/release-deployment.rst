Release And Deployment
======================

Sheetforge releases are maintainer-controlled. A release is not ready because the version changed;
it is ready only when package artifacts, documentation, benchmark claims, and publication gates have
all been checked.

Current Alpha Target
--------------------

The first planned alpha is ``0.1.0a1`` with Git tag ``v0.1.0a1``.

The alpha may claim selected-output benchmark validation for the current declared FABLE scope. It must
not claim full-workbook conversion, full-workbook equivalence, Excel-backed recalculation equivalence,
or stable public API compatibility.

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
into a clean virtual environment, imports Sheetforge, and smoke-tests the installed CLI.

Documentation Deployment Gate
-----------------------------

The docs workflow builds Sphinx documentation and uploads the built HTML artifact to GitHub Pages.
The build must pass ``scripts/verify_docs_theme.py`` so the uploaded artifact uses the Sphinx Read the
Docs theme rather than a fallback Jekyll/minima site.

After a release PR merges to ``main``, verify the published GitHub Pages site from the workflow
deployment result. The deployed page should show the Read the Docs side navigation and should not look
like a plain Jekyll project page.

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

   python -m pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ sheetforge==0.1.0a1
   python -c "import sheetforge; print(sheetforge.__version__)"
   sheetforge --help

Real PyPI Publication
---------------------

Real PyPI publication requires maintainer approval and the protected ``pypi`` environment.

Expected sequence:

1. Confirm ``CHANGE_LOG.md`` and release notes describe the actual alpha boundary.
2. Confirm local and CI release artifact checks pass.
3. Confirm TestPyPI rehearsal passes or document the exact blocker.
4. Create the annotated tag, for example ``v0.1.0a1``.
5. Run the ``Release`` workflow or push the tag, then approve the protected PyPI environment.
6. Verify the package page, wheel install, import, CLI help, docs deployment, and GitHub release notes.

Rollback And Yanking
--------------------

If a broken alpha reaches PyPI, do not reuse the same version. PyPI artifacts are immutable.

Use one of these responses:

- yank the broken release on PyPI if installation should be discouraged but historical availability is
  still useful;
- publish a new alpha such as ``0.1.0a2`` after fixing the issue;
- update release notes and roadmap entries with the failure mode and mitigation.

Private Data Rules
------------------

Release artifacts must not include source workbooks, generated workbook clones, private evaluation
reports, local logs, credentials, or ignored ``tmp/`` material.
