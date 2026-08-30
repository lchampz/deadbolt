#!/usr/bin/env bash
# Regera o ground truth de mutação dos dois corpora e reconstrói os JSON.
#
# ATENÇÃO (R5, METRIC.md): isto SOBRESCREVE artefatos congelados. Reproduz do
# corpus pinado, então o resultado deve bater bit a bit. Rode para VERIFICAR,
# não para emendar. Divergência aqui é um achado, não um detalhe.
set -euo pipefail
cd "$(dirname "$0")/.."

PY="${PY:-.venv/bin/python}"
command -v "$PY" >/dev/null 2>&1 || PY="$(command -v python3 || command -v python)"

for c in python-slugify python-slugify-holdout; do
  echo "== mutmut run: $c"
  # via módulo, não via script de console — shebang guarda caminho absoluto
  if [ -x "corpus/$c/.venv/bin/python" ]; then
    MUTPY="$PWD/corpus/$c/.venv/bin/python"
  else
    MUTPY="$PY"
  fi
  ( cd "corpus/$c" && "$MUTPY" -m mutmut run 2>&1 | tr '\r' '\n' | tail -1 )
  "$PY" eval/build_ground_truth.py "$c"
done

echo
echo "Esperado — qualquer divergência invalida os números de results/:"
echo "  python-slugify         216 mutantes | 170 killed | 46 survived | 0.213"
echo "  python-slugify-holdout 288 mutantes | 189 killed | 99 survived | 0.3438"
echo "  ambos: parse_errors 0, line_mismatches 0"
