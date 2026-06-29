FABLE Pyculator Onboarding
==========================

This guide is for HQP joining the Modelwright/FABLE Pyculator pilot. The immediate goal is to help
new testers run the tracked notebook examples, record validation results, and report usability
friction in a consistent place.

The FABLE Pyculator is a workflow name for using Modelwright-generated Python models with FABLE
Calculator workbooks. It is not a separate package and it is not a claim that arbitrary FABLE country
calculators are production-ready.

Start In The Project Dev Environment
------------------------------------

Use the project JupyterHub environment:

.. code-block:: text

   https://fresh01.01101.dev/jupyterhub14/

Log in with your UBC CWL. After login, JupyterLab should open a default Launcher tab.

From that Launcher tab, click **VSCode (code-server)** at the end of the top row of launch buttons.
The JupyterLab interface also works, but VSCode has better built-in support for GitHub
authentication, repository cloning, Python environments, and notebook editing. In JupyterLab, those
steps require more manual shell commands.

Set Up The Repository In VSCode
-------------------------------

In VSCode/code-server:

1. Authenticate VSCode with your GitHub account when prompted.
2. Clone the Modelwright repository from GitHub.
3. Open the cloned repository folder.
4. Open one of the tracked notebooks under ``examples/notebooks/``.
5. Allow VSCode to install the Python and Jupyter extensions if prompted.
6. Create a repository-local virtual environment from the repo root:

   .. code-block:: bash

      python -m venv .venv
      .venv/bin/python -m pip install --upgrade pip
      .venv/bin/python -m pip install -e '.[dev]'

7. Select the ``.venv`` Python interpreter as the notebook kernel.
8. Run the notebook cells live.

If VSCode asks whether it can trust the workspace, approve the repository workspace only if it is the
Modelwright checkout you cloned from the project GitHub repository.

What To Try First
-----------------

Start with the Examples Gallery:

.. code-block:: text

   https://ubc-fresh.github.io/modelwright/examples.html

Then run the tracked notebooks:

- ``examples/notebooks/synthetic-notebook-interface.ipynb``
- ``examples/notebooks/fable-2020-notebook-interface.ipynb``

As you go, write down every point where the workflow assumes too much, hides too much, or makes you
wonder what to do next. Those notes are part of the development process.

Generated Model Artifacts
-------------------------

FABLE Pyculator notebooks wrap Modelwright-generated Python models. When testing a new FABLE
Calculator workbook version, the workbook and generated Python model must come from the same workbook
version.

Modelwright documents the generated-model artifact workflow in :doc:`generated-model-artifacts`.
That guide explains how to create ``contract.json``, ``expressions.json``, and ``constants.json`` with
``modelwright model infer-contract`` before running ``modelwright model generate``.

For FABLE workbooks, the output-ref list is still a project-specific choice. Keep version-specific
workbooks, output-ref lists, inferred JSON files, generated Python models, and validation reports under
ignored ``tmp/`` paths unless a maintainer explicitly approves a tracked artifact.

Where To Leave Notes
--------------------

Use GitHub issues for structured project notes:

- Use the FABLE validation run form when comparing Excel and generated Python outputs.
- Use the usability observation form when something about the interface, notebook, or documentation is
  confusing.
- Use the setup problem form when the dev environment, GitHub authentication, VSCode, ``.venv``, or
  notebook kernel setup blocks progress.

If you want help getting set up, ping Greg in Basecamp and ask for a setup working session. It is also
fine to work through the setup independently and report what was confusing afterward.

Source Workbook Hygiene
-----------------------

Raw FABLE Calculator workbooks, downloaded country calculators, generated Python clones, local logs,
and full validation reports should stay as local working material unless the maintainer explicitly
approves a small sanitized tracked artifact.

Keep local workbook material under ignored ``tmp/`` paths. Do not commit original workbook files to
the Modelwright repository.

Safe tracked material includes small scripts, cleaned notes, sanitized validation summaries, compact
manifest examples, generated Python outputs that have been explicitly approved for tracking, and
documentation.
