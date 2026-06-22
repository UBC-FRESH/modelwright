#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON:-"$ROOT_DIR/.venv/bin/python"}"
RUN_ID="$(date -u +%Y%m%dT%H%M%SZ)"
RUN_DIR="${RELEASE_CHECK_DIR:-"$ROOT_DIR/tmp/release-checks/$RUN_ID"}"
DIST_DIR="$RUN_DIR/dist"
INSTALL_DIR="$RUN_DIR/install-$RUN_ID"

if [[ ! -x "$PYTHON_BIN" ]]; then
  if command -v "$PYTHON_BIN" >/dev/null 2>&1; then
    PYTHON_BIN="$(command -v "$PYTHON_BIN")"
  else
    echo "Python executable not found: $PYTHON_BIN" >&2
    echo "Run scripts/bootstrap_dev_env.sh first or set PYTHON=/path/to/python." >&2
    exit 2
  fi
fi

mkdir -p "$RUN_DIR"

echo "[release-check] run directory: $RUN_DIR"
echo "[release-check] removing stale build outputs"
rm -rf "$ROOT_DIR/build"
rm -rf "$ROOT_DIR/src/sheetforge.egg-info"
rm -rf "$DIST_DIR"
rm -rf "$INSTALL_DIR"
mkdir -p "$DIST_DIR" "$INSTALL_DIR"
echo "[release-check] building sdist and wheel"
"$PYTHON_BIN" -m build --sdist --wheel --outdir "$DIST_DIR" "$ROOT_DIR"

echo "[release-check] running twine metadata check"
"$PYTHON_BIN" -m twine check "$DIST_DIR"/*

echo "[release-check] inspecting artifact contents"
"$PYTHON_BIN" - "$DIST_DIR" <<'PY'
from __future__ import annotations

import sys
import tarfile
import zipfile
from pathlib import Path

dist_dir = Path(sys.argv[1])
forbidden_parts = {
    ".venv",
    "_build",
    "tmp",
    "private-workbooks",
    "private-evaluations",
    "release-checks",
    "sheetforge",
}
forbidden_suffixes = {
    ".xls",
    ".xlsb",
    ".xlsm",
    ".xlsx",
}

def names_for(path: Path) -> list[str]:
    if path.suffix == ".whl":
        with zipfile.ZipFile(path) as archive:
            return archive.namelist()
    if path.name.endswith(".tar.gz"):
        with tarfile.open(path) as archive:
            return archive.getnames()
    raise RuntimeError(f"unsupported artifact type: {path}")

errors: list[str] = []
for artifact in sorted(dist_dir.iterdir()):
    names = names_for(artifact)
    for name in names:
        parts = set(Path(name).parts)
        suffix = Path(name).suffix.lower()
        if parts & forbidden_parts:
            errors.append(f"{artifact.name}: forbidden path in artifact: {name}")
        if suffix in forbidden_suffixes:
            errors.append(f"{artifact.name}: workbook file in artifact: {name}")
    print(f"[release-check] inspected {artifact.name}: {len(names)} entries")

if errors:
    for error in errors:
        print(error, file=sys.stderr)
    raise SystemExit(1)
PY

echo "[release-check] creating clean install environment"
"$PYTHON_BIN" -m venv "$INSTALL_DIR/.venv"
"$INSTALL_DIR/.venv/bin/python" -m pip install --upgrade pip
"$INSTALL_DIR/.venv/bin/python" -m pip install "$DIST_DIR"/*.whl

echo "[release-check] running installed package smoke tests"
"$INSTALL_DIR/.venv/bin/python" - <<'PY'
from __future__ import annotations

import modelwright
import importlib.util

assert modelwright.__version__ == "0.1.0a3", modelwright.__version__
assert importlib.util.find_spec("sheetforge") is None
print(f"[release-check] imported modelwright {modelwright.__version__}")
PY
if [[ -e "$INSTALL_DIR/.venv/bin/sheetforge" ]]; then
  echo "[release-check] unexpected old sheetforge console script" >&2
  exit 1
fi
"$INSTALL_DIR/.venv/bin/modelwright" --help >/dev/null

echo "[release-check] release artifact checks passed"
