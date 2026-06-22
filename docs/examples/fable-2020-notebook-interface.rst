2020 FABLE Notebook Interface
=============================

This production-size example uses Modelwright's generated Python output from the public 2020 FABLE
Calculator benchmark workbook. The original workbook is not tracked in this repository. The generated
Python model is tracked as ``examples/fable_2020/generated_fable_2020_model.py.xz`` and decompressed
into ignored ``tmp/`` working space before import.

The example wraps three validated ``SCENARIOS selection`` outputs, renders them as DataFrames, and
keeps the validation boundary explicit: the source Phase 26 full-validation report recorded 281,741
comparable cached outputs, 281,741 matches, and 0 mismatches.

Run it from the repository root:

.. code-block:: bash

   python examples/fable_2020/notebook_interface.py

Source
------

.. literalinclude:: ../../examples/fable_2020/notebook_interface.py
   :language: python
