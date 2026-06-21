#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN="${PYTHON:-python3}"
VENV_DIR="${VENV_DIR:-"$ROOT_DIR/.venv"}"
MATERIALIZE_BENCHMARKS=0

usage() {
  cat <<EOF
Usage: scripts/bootstrap_dev_env.sh [--benchmarks]

Creates or updates a repo-local .venv and installs Modelwright in editable
development mode with the [dev] extra.

Options:
  --benchmarks  Also materialize the public FABLE benchmark workbooks into
                tmp/private-workbooks/ after installing dependencies.
  -h, --help    Show this help.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --benchmarks)
      MATERIALIZE_BENCHMARKS=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [[ ! -d "$VENV_DIR" ]]; then
  "$PYTHON_BIN" -m venv "$VENV_DIR"
fi

"$VENV_DIR/bin/python" -m pip install --upgrade pip
rm -rf "$ROOT_DIR/src/sheetforge.egg-info"
if "$VENV_DIR/bin/python" -m pip show sheetforge >/dev/null 2>&1; then
  echo "Removing stale pre-rebrand sheetforge editable install."
  "$VENV_DIR/bin/python" -m pip uninstall -y sheetforge
fi
"$VENV_DIR/bin/python" -m pip install -e "${ROOT_DIR}[dev]"

if [[ "$MATERIALIZE_BENCHMARKS" -eq 1 ]]; then
  "$VENV_DIR/bin/python" "$ROOT_DIR/scripts/materialize_fable_benchmarks.py"
fi

cat <<EOF
Modelwright development environment is ready.

Python: $VENV_DIR/bin/python

Run checks with:
  $VENV_DIR/bin/python -m ruff check .
  $VENV_DIR/bin/python -m pytest
  $VENV_DIR/bin/sphinx-build -b html docs _build/html -W

Materialize public FABLE benchmarks with:
  scripts/bootstrap_dev_env.sh --benchmarks

Activate manually with:
  source "$VENV_DIR/bin/activate"
EOF
