#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON:-python3}"
VENV_DIR="${VENV_DIR:-"$ROOT_DIR/.venv"}"

if [[ ! -d "$VENV_DIR" ]]; then
  "$PYTHON_BIN" -m venv "$VENV_DIR"
fi

"$VENV_DIR/bin/python" -m pip install --upgrade pip
"$VENV_DIR/bin/python" -m pip install -e "${ROOT_DIR}[test,quality,docs]"

cat <<EOF
Sheetforge development environment is ready.

Python: $VENV_DIR/bin/python

Run checks with:
  $VENV_DIR/bin/python -m ruff check .
  $VENV_DIR/bin/python -m pytest
  $VENV_DIR/bin/sphinx-build -b html docs _build/html -W

Activate manually with:
  source "$VENV_DIR/bin/activate"
EOF
