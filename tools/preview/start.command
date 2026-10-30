#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/../.."

# Keep existing environments intact. Use a separate path to select a different
# interpreter, e.g. PROOFREAD_PYTHON=python3.13 PROOFREAD_VENV=backend/.venv-313.
preview_venv="${PROOFREAD_VENV:-backend/.venv}"
preview_python="$preview_venv/bin/python"
supported_python() {
  command -v "$1" >/dev/null 2>&1 && "$1" -c \
    'import sys; sys.exit(not ((3, 11) <= sys.version_info[:2] <= (3, 13)))' >/dev/null 2>&1
}
if [[ -x "$preview_python" ]]; then
  if ! supported_python "$preview_python"; then
    echo "Existing $preview_venv requires a supported Python 3.11–3.13 interpreter; it was preserved." >&2
    echo "Set PROOFREAD_PYTHON to Python 3.11–3.13 and PROOFREAD_VENV to a new environment path." >&2
    exit 1
  fi
  printf 'Using existing preview environment: %s (PROOFREAD_PYTHON selects new environments only).\n' "$preview_venv"
elif [[ -e "$preview_venv" ]]; then
  echo "Existing $preview_venv has no usable Python and was preserved. Set PROOFREAD_VENV to a new path and PROOFREAD_PYTHON to Python 3.11–3.13." >&2
  exit 1
else
  selected_python=""
  if [[ -n "${PROOFREAD_PYTHON:-}" ]]; then
    if supported_python "$PROOFREAD_PYTHON"; then
      selected_python="$PROOFREAD_PYTHON"
    else
      echo "PROOFREAD_PYTHON must name an installed Python 3.11–3.13 interpreter. Newer versions are not validated for this preview." >&2
      exit 1
    fi
  else
    for candidate in python3.13 python3.12 python3.11 python3 \
      /Library/Frameworks/Python.framework/Versions/{3.13,3.12,3.11}/bin/python3 \
      /opt/homebrew/bin/python3.{13,12,11} /usr/local/bin/python3.{13,12,11}; do
      if supported_python "$candidate"; then
        selected_python="$candidate"
        break
      fi
    done
  fi
  if [[ -z "$selected_python" ]]; then
    echo "Install Python 3.11–3.13 and set PROOFREAD_PYTHON to its executable. Newer versions are not validated for this preview." >&2
    exit 1
  fi
  "$selected_python" -m venv "$preview_venv"
fi

dependencies_ready() {
  "$preview_python" -m pip check >/dev/null 2>&1 && "$preview_python" - >/dev/null 2>&1 <<'PY'
from importlib import import_module, metadata
from pathlib import Path
from packaging.requirements import Requirement
for line in Path('backend/requirements.txt').read_text().splitlines():
    if not line.strip() or line.lstrip().startswith('#'):
        continue
    requirement = Requirement(line)
    if requirement.marker is None or requirement.marker.evaluate():
        if metadata.version(requirement.name) not in requirement.specifier:
            raise RuntimeError('Dependency version mismatch')
for module in ('fastapi', 'uvicorn', 'pydantic', 'httpx', 'jwt', 'cryptography'):
    import_module(module)
PY
}
if ! dependencies_ready; then
  echo "Installing or repairing preview dependencies in $preview_venv…"
  if ! "$preview_python" -m pip --version >/dev/null 2>&1; then
    "$preview_python" -m ensurepip --upgrade
  fi
  "$preview_python" -m pip install -r backend/requirements.txt
  if ! dependencies_ready; then
    echo "Preview dependencies remain incomplete; the server was not started. Retry after checking the installation errors." >&2
    exit 1
  fi
fi
printf '%s\n' 'Open http://127.0.0.1:8010 in your browser. Press Control-C to stop.'
exec "$preview_python" tools/preview/server.py
