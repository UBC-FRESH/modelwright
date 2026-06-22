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

Use it from a notebook stored under ``tmp/notebooks/``:

.. code-block:: python

   from pathlib import Path
   import sys

   repo_root = Path.cwd().resolve()
   while repo_root.name != "sheetforge":
       repo_root = repo_root.parent

   sys.path.insert(0, str(repo_root))

   from examples.fable_2020.notebook_interface import build_facade
   from modelwright.notebooks import outputs_frame, report_frames, table_frame

   facade = build_facade()
   facade.calculate()

   outputs_frame(facade)

Source
------

.. literalinclude:: ../../examples/fable_2020/notebook_interface.py
   :language: python
