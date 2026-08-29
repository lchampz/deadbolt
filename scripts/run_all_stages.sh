#!/usr/bin/env bash
# Grava os quatro estágios nos dois conjuntos e imprime a tabela final.
#
# Exige DEADZONE_MODE=live e credencial no ambiente do PROCESSO (não do seu
# terminal interativo). Cada chamada é gravada em recordings/; rodar de novo
# depois disso é replay a custo zero.
#
#   DEADZONE_MODE=live bash scripts/run_all_stages.sh
set -euo pipefail
cd "$(dirname "$0")/.."
PY="${PY:-.venv/bin/python}"
export PYTHONPATH="${PYTHONPATH:-}:$PWD/src"

for stage in baseline s4 s5 s6; do
  for set_name in dev holdout; do
    echo "=== $stage / $set_name"
    "$PY" -m deadzone.predict --stage "$stage" --set "$set_name"
    "$PY" eval/run.py --predictions "results/$stage-$set_name.pred.json" --save
    echo
  done
done

"$PY" scripts/export_trajectories.py
"$PY" scripts/refresh_submission_table.py
"$PY" eval/report.py
