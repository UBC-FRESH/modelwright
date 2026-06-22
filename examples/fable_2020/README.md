# 2020 FABLE Generated Model Example

This directory contains a compressed generated Python model produced by Modelwright from the public
2020 FABLE Calculator benchmark workbook.

The original workbook is not tracked in this repository. The generated model is tracked as
`generated_fable_2020_model.py.xz` because the uncompressed Python module is about 117 MiB, which is
larger than ordinary GitHub per-file limits. The example script decompresses it into ignored `tmp/`
working space before importing it.

The generated model preserves the P26 full-validation evidence boundary:

- comparable cached outputs: 281,741;
- matches: 281,741;
- mismatches: 0.

Run from the repository root:

```bash
python examples/fable_2020/notebook_interface.py
```
