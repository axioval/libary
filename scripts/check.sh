#!/usr/bin/env bash
set -euo pipefail
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"
export PATH="$HOME/.local/bin:$PATH"
# Resolve a copied project against an empty cache and require an exact lock match.
ROOT="$repo_root" PYTHONPATH="$repo_root/vendor/schema/scripts" python3 -c \
  'import os; from pathlib import Path; from mcs_archive import _fresh_resolve_dependency_lock; _fresh_resolve_dependency_lock(Path(os.environ["ROOT"]))'
python3 -m unittest discover -s tests -v
python3 scripts/validate.py
