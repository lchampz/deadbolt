#!/usr/bin/env bash
# Prepara os dois corpora. Ambos são cópias vendorizadas e pinadas de
# python-slugify @ 7b6d5d96 (MIT) — ver corpus/*/PINNED_SHA.txt e LICENSE.
set -euo pipefail
cd "$(dirname "$0")/.."

for c in corpus/python-slugify corpus/python-slugify-holdout; do
  echo "== $c"
  uv venv --python 3.12 "$c/.venv" >/dev/null
  uv pip install --python "$c/.venv/bin/python" -q text-unidecode pytest "mutmut==3.7.0"
  ( cd "$c" && .venv/bin/python -m pytest -q | tail -1 )
done
