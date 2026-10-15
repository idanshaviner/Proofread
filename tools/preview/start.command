#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/../.."
if [[ ! -x backend/.venv/bin/python ]]; then
  python3 -m venv backend/.venv
  backend/.venv/bin/python -m pip install -r backend/requirements.txt
fi
printf '%s\n' 'Open http://127.0.0.1:8010 in your browser. Press Control-C to stop.'
exec backend/.venv/bin/python tools/preview/server.py
