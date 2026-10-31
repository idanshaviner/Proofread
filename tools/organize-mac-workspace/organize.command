#!/bin/bash
set -euo pipefail
helper_dir="$(cd "$(dirname "$0")" && pwd)"
python3 "$helper_dir/organize.py" "${1:-$HOME/Documents}"
