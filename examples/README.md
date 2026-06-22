# Modelwright Examples

These examples show how generated Modelwright Python models can be wrapped with analyst-facing
facades and notebook-friendly DataFrame helpers.

- `synthetic/`: a tiny generated-model example based on the tracked synthetic fixture shape.
- `fable_2020/`: a production-size example using a compressed generated Python model converted from
  the public 2020 FABLE Calculator benchmark workbook.

The original FABLE workbook is not tracked here. The tracked FABLE example contains Modelwright's
generated Python output, compressed as `generated_fable_2020_model.py.xz` because the uncompressed
module is larger than ordinary GitHub per-file limits.

## Importing From Local Notebooks

These are source-tree examples. If your notebook file lives under `tmp/notebooks/`, add the repository
root to `sys.path` before importing from `examples`:

```python
from pathlib import Path
import sys

repo_root = Path.cwd().resolve()
while repo_root.name != "sheetforge":
    repo_root = repo_root.parent

sys.path.insert(0, str(repo_root))
```

Then imports such as `from examples.synthetic.notebook_interface import build_facade` will resolve.
