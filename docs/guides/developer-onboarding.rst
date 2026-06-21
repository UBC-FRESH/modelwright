Developer Onboarding
====================

Use a repository-local virtual environment for Modelwright development. This keeps package dependencies,
console scripts, Sphinx, and quality tools tied to the checkout being edited.

Bootstrap
---------

From the repository root:

.. code-block:: bash

   scripts/bootstrap_dev_env.sh

This creates ``.venv/`` and installs Modelwright with the ``dev`` extra:

.. code-block:: bash

   .venv/bin/python -m pip install -e '.[dev]'

The editable install handles code and development dependencies only. It does not download external
workbook assets as an install side effect.

To also restore the public FABLE benchmark workbooks into canonical ignored paths, run:

.. code-block:: bash

   scripts/bootstrap_dev_env.sh --benchmarks

Activate manually when needed:

.. code-block:: bash

   source .venv/bin/activate

Best Practices
--------------

- Use ``.venv/bin/python`` and ``.venv/bin/sphinx-build`` in local commands.
- Keep ``.venv/`` untracked.
- Run checks before committing:

  .. code-block:: bash

     .venv/bin/python -m ruff check .
     .venv/bin/python -m pytest
     .venv/bin/sphinx-build -b html docs _build/html -W

- Store private workbooks and generated outputs under ignored ``tmp/`` paths.
- Do not commit raw workbook files, generated clones, private logs, or full private validation reports.
- Update ``ROADMAP.md`` and ``CHANGE_LOG.md`` with each completed task.

Where To Look
-------------

- ``README.md``: quick project overview and common commands.
- ``CONTRIBUTING.md``: contributor workflow and data hygiene.
- ``AGENTS.md``: working contract for AI-assisted development.
- ``ROADMAP.md``: active phase and next task.
- ``planning/``: detailed design notes and implementation decisions.
