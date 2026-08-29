#!/usr/bin/env bash
# Espelha o vault Obsidian (o raciocínio, em português) para docs/ no repo.
# Convenção herdada do projeto anterior: o documento final para o juiz vive no
# repo (README, METRIC, CHANGELOG, REPRODUCTION, em inglês); aqui vive o porquê.
set -euo pipefail
cd "$(dirname "$0")/.."
VAULT="${VAULT:-$HOME/Documents/documentacao/obsidian/deadzone}"
[ -d "$VAULT" ] || { echo "vault não encontrado: $VAULT" >&2; exit 1; }
mkdir -p docs
rsync -a --delete --exclude '.git' --exclude '.obsidian' --exclude '.gitignore' --exclude 'trajectories' \
      "$VAULT"/ docs/
echo "sincronizado de $VAULT:"
ls docs/*.md | sed 's|^|  |'
