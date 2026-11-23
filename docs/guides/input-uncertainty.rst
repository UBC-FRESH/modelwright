Input Uncertainty Modelling
===========================

Modelwright can summarize expected values and output distributions for **independent uncertain input
variates** in a generated model. The implementation is a small, dependency-free reference layer built
on the generated model's existing ``calculate(inputs=...)`` entrypoint:

- a JSON distribution specification keyed by input cell reference;
- inverse-CDF sampling, using either plain random draws or Latin-hypercube stratification;
- evaluation of every draw through the generated model;
- per-output summaries: expected value (mean), median, standard deviation, standard error,
  coefficient of variation, percentiles, and histogram counts.

It does **not** model correlations between inputs, run Sobol or variance-based global sensitivity
analysis, or provide production-scale parallel execution. Those are explicit follow-up boundaries.

Distribution Specification
--------------------------

Write a specification as JSON. Parameters are validated when the specification is loaded.

.. code-block:: json

   {
     "draws": 2000,
     "seed": 17,
     "design": "latin_hypercube",
     "distributions": [
       {
         "cell_ref": "1_data_demand!EX26",
         "family": "truncated_normal",
         "parameters": {"mean": 2020.0, "std": 10.0, "low": 2000.0, "high": 2040.0}
       },
       {
         "cell_ref": "2_calc_livestock!C42",
         "family": "uniform",
         "parameters": {"low": 0.8, "high": 1.2}
       }
     ],
     "output_refs": ["GHG!AE18", "FOOD!B12"],
     "percentiles": [5, 25, 50, 75, 95],
     "histogram_bins": 20
   }

Supported families:

.. list-table::
   :header-rows: 1

   * - Family
     - Parameters
   * - ``normal``
     - ``mean``, ``std`` (``std > 0``)
   * - ``truncated_normal``
     - ``mean``, ``std``, ``low``, ``high`` (``low < high``)
   * - ``uniform``
     - ``low``, ``high`` (``low < high``)
   * - ``lognormal``
     - ``mean``, ``sigma`` (parameters of the underlying normal)
   * - ``triangular``
     - ``low``, ``mode``, ``high`` (``low <= mode <= high``)
   * - ``constant``
     - ``value``

``output_refs`` is optional; when omitted, the summaries cover every output returned by the model.
``design`` is ``random`` (default) or ``latin_hypercube``. All draws are seeded and reproducible.

Python API
----------

.. code-block:: python

   import importlib.util

   from modelwright.uncertainty import InputDistribution, UncertaintySpec, run_uncertainty

   spec = UncertaintySpec(
       distributions=(
           InputDistribution("Inputs!B2", "normal", {"mean": 100.0, "std": 10.0}),
       ),
       draws=2000,
       seed=7,
       output_refs=("Summary!B2",),
   )

   module_spec = importlib.util.spec_from_file_location("generated_model", "tmp/generated_model.py")
   module = importlib.util.module_from_spec(module_spec)
   module_spec.loader.exec_module(module)

   result = run_uncertainty(module.calculate, spec)
   summary = result["outputs"][0]
   print(summary["mean"], summary["percentiles"]["p5"], summary["percentiles"]["p95"])

When the generated model was produced in external input-data mode, pass the data directory through:

.. code-block:: python

   result = run_uncertainty(
       module.calculate,
       spec,
       calculate_kwargs={"data_dir": "tmp/generated-model/model_data"},
   )

CLI
---

.. code-block:: bash

   modelwright uncertainty run \
     --model tmp/generated-model/generated_model.py \
     --spec tmp/uncertainty/spec.json \
     --contract tmp/generated-model/contract.json \
     --out tmp/uncertainty/result.json

Pass ``--include-samples`` to keep per-draw output values, ``--stop-on-error`` to abort on the first
failed draw, and omit ``--out`` to print the result JSON to standard output. When ``--contract`` is
supplied, distribution cell refs are validated against the contract's declared ``input_refs``. For a
loader-based generated model, pass ``--data-dir`` to point at its external input-data directory.

Interpreting Results
--------------------

Each output summary contains:

- ``mean`` (expected value) and ``median``;
- ``standard_deviation``, ``standard_error`` (Monte Carlo error on the mean), and
  ``coefficient_of_variation``;
- ``minimum``, ``maximum``, and requested ``percentiles`` (default 5, 25, 50, 75, 95);
- histogram ``edges`` and ``counts``;
- ``numeric_count``, ``non_numeric_count``, and ``error_count`` so failed or non-numeric draws are
  visible rather than silently dropped.

The standard error is the right convergence check: increasing ``draws`` shrinks it approximately with
``1 / sqrt(draws)``. Latin-hypercube sampling usually reduces error for the same number of draws, but
it does not eliminate it.

Runtime
-------

The reference runner is serial. A full FABLE model run is on the order of 100 seconds, so hundreds of
draws are a batch job rather than an interactive loop. For larger studies, slice the model to the
required outputs or use the downstream reduced evaluator, and run multiple processes with separate
seeds. The provenance block records the seed, draw count, design, and specification hash so results
can be reproduced.

Relationship To Distribution-Algebra Tools
------------------------------------------

Sampling works with any generated model because it treats ``calculate()`` as a black box. Tools such
as PaCal instead propagate distributions through analytic expressions, which is attractive for small
formulas but cannot execute a generated workbook model with lookups, conditionals, and Excel error
semantics. Use sampling for model-wide uncertainty and keep distribution-algebra tools for small
side-calculations or cross-checks.
