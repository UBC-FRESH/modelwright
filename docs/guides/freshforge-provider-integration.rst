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
   python -m pip install "freshforge @ git+https://github.com/UBC-FRESH/freshforge.git@v0.1.0a3"

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

FreshForge run namespaces can isolate repeated runs under a relative artifact
prefix:

.. code-block:: bash

   freshforge run path/to/generated_model_workflow.yaml \
      --workdir /path/to/project \
      --namespace strategy/output-columns \
      --json

With a namespace, FreshForge resolves relative artifact paths under
``workdir / namespace``. Absolute artifact paths remain absolute.

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

Run And Stage Summaries
-----------------------

FreshForge owns the whole-run summary. In ``freshforge run --json`` output, the
top-level ``summary`` object reports the workflow id, run namespace, node
counts, diagnostic counts, artifact counts, and compact node summaries.

Modelwright owns generated-model stage summaries inside each executed node's
full result. Look in ``run.nodes[*].data.summary`` for compact stage facts:

- ``model_infer_contract`` reports whether inference succeeded plus selected
  input, output, symbol, expression, constants, and diagnostic counts.
- ``model_generate`` reports whether Python source was generated plus source
  line/byte counts, contract counts, and diagnostic counts.
- ``model_execute`` reports whether the generated model executed plus declared
  and observed output counts.
- ``validation_evaluate`` reports scenario id, generated-execution counts, and
  cached/oracle validation comparison, match, mismatch, status, and diagnostic
  counts.

The raw JSON artifacts are still written exactly as before. Stage summaries are
small convenience payloads for downstream automation; they are not replacements
for raw inference, generation, execution, or evaluation artifacts.

Validation Failure Semantics
----------------------------

``validation_evaluate`` is fail-fast for explicit validation failure. If the
generated model has error diagnostics, or if an available cached/oracle
validation report has status ``fail``, the FreshForge node returns failed status
with diagnostic ``modelwright.validation_evaluate.failed``. If generated
execution succeeds but no validation report is available, the node may still
succeed while its stage summary records that validation evidence is unavailable.

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
