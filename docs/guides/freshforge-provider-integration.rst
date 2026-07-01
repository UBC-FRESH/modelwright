FreshForge Provider Integration
===============================

Purpose
-------

Modelwright exposes a FreshForge provider for workbook conversion workflow
stages. FreshForge owns declarative graph validation, provider discovery,
inspection, deterministic non-executing planning, and serial local scheduling.
Modelwright still owns actual extraction, graphing, generated-model
materialization, execution, and validation through its Python APIs and
``modelwright`` CLI.

The provider is intentionally workbook-neutral. Concrete workflow documents
belong to the project or package that owns the workbook, output-ref list,
validation scenario, and artifact policy.

Install
-------

FreshForge is currently consumed from its GitHub release rather than as a
Modelwright package dependency. For development, install Modelwright normally
and then install FreshForge into the same environment:

.. code-block:: bash

   python -m pip install -e .[dev]
   python -m pip install "freshforge @ git+https://github.com/UBC-FRESH/freshforge.git@v0.1.0a2"

Modelwright registers a ``freshforge.providers`` entry point, but it does not
add a GitHub direct-reference dependency in ``pyproject.toml``. This keeps
Modelwright's published package metadata PyPI-safe while FreshForge is still
early and moving.

Provider Discovery
------------------

When both packages are installed in the same environment, FreshForge can
discover provider id ``modelwright``:

.. code-block:: bash

   freshforge providers

The provider references currently exposed for workflow declarations are:

- ``modelwright.workbook_extract``
- ``modelwright.workbook_graph``
- ``modelwright.model_infer_contract``
- ``modelwright.model_generate``
- ``modelwright.model_execute``
- ``modelwright.validation_evaluate``
- ``modelwright.conversion_plan``

Generic Workflow Example
------------------------

The public-safe provider example workflow lives at:

.. code-block:: text

   examples/freshforge/generated_model_workflow.yaml

Validate and plan it with:

.. code-block:: bash

   freshforge validate examples/freshforge/generated_model_workflow.yaml
   freshforge inspect examples/freshforge/generated_model_workflow.yaml
   freshforge plan examples/freshforge/generated_model_workflow.yaml

When a workflow declares real public-safe paths and the required artifacts
exist, executable generated-model stages can also be run with:

.. code-block:: bash

   freshforge run path/to/generated_model_workflow.yaml --workdir /path/to/project --json

The graph declares this order:

1. extract workbook facts;
2. build the dependency graph;
3. infer the generated-model contract from selected output refs;
4. generate the standalone Python model;
5. execute the generated model;
6. evaluate generated outputs against a validation scenario;
7. summarize the conversion boundary.

Relationship To Modelwright Execution
-------------------------------------

FreshForge graph planning is not Modelwright execution. Planning validates and
orders the graph. FreshForge ``run`` then calls Modelwright provider
``run_node`` hooks for supported nodes. Those hooks use Modelwright Python APIs
and write the same JSON artifacts as commands such as:

.. code-block:: bash

   modelwright model infer-contract path/to/workbook.xlsx ...
   modelwright model generate ...
   modelwright model execute ...
   modelwright validation evaluate ...

The executable provider currently supports ``model_infer_contract``,
``model_generate``, ``model_execute``, and ``validation_evaluate``. It does not
shell out to the CLI. Workbook extraction and graph construction remain
Modelwright internals of contract inference unless a workflow deliberately uses
those stages for planning context.

FABLE Pyculator Boundary
------------------------

FABLE-specific output-ref discovery belongs in FABLE Pyculator, not
Modelwright. Modelwright can infer and generate a model once a caller provides
explicit output refs. FABLE Pyculator knows the FABLE workbook output tables,
headline series, and column-flavour tags that can help construct those output
refs for FABLE Calculator versions.

Boundaries
----------

The Modelwright provider remains bounded. It does not:

- implement FreshForge scheduling;
- call the Modelwright CLI via subprocess;
- choose workbook output refs;
- cache or checkpoint workflow stages; or
- claim full-workbook conversion or validation equivalence.

API
---

Use :func:`modelwright.freshforge.provider_factory` when a caller needs
explicit registry control. Concrete workflow assembly belongs to the project
that owns the workbook and validation contract.
