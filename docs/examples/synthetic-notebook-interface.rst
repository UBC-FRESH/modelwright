Synthetic Notebook Interface
============================

This tiny example uses a small generated-model-shaped ``calculate(inputs=None)`` function, wraps it
with ``ModelFacade``, and renders outputs, a declared table, and a baseline-vs-scenario comparison as
DataFrames.

Run it from the repository root:

.. code-block:: bash

   python examples/synthetic/notebook_interface.py

Source
------

.. literalinclude:: ../../examples/synthetic/notebook_interface.py
   :language: python
