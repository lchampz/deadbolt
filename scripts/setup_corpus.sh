#!/usr/bin/env bash
# Prepara os três corpora pinados. Os venvs NÃO são versionados — este script é
# a fonte única de como recriá-los, e recriá-los é necessário sempre que a pasta
# do projeto for movida ou renomeada: o venv grava caminho absoluto no shebang
# dos scripts de console, e um caminho velho quebra com FileNotFoundError que
# nomeia o script em vez do interpretador que sumiu.
set -euo pipefail
cd "$(dirname "$0")/.."

prep() {
  local dir="$1"; shift
  echo "== $dir"
  uv venv --python 3.12 "$dir/.venv" >/dev/null
  uv pip install --python "$dir/.venv/bin/python" -q "$@"
  ( cd "$dir" && .venv/bin/python -m pytest -q 2>&1 | tail -1 )
}

# python-slugify e sua cópia de holdout: pacote NÃO instalado de propósito, para
# que o import venha do diretório de trabalho (o sandbox precisa vencer).
prep corpus/python-slugify         text-unidecode pytest "mutmut==3.7.0"
prep corpus/python-slugify-holdout text-unidecode pytest "mutmut==3.7.0"

# toolz deriva a versão de tags git via setuptools_scm; o corpus é vendorizado
# sem .git, então a versão real vai explícita (PINNED_SHA.txt guarda a tag).
echo "== corpus/toolz-transfer"
uv venv --python 3.12 corpus/toolz-transfer/.venv >/dev/null
SETUPTOOLS_SCM_PRETEND_VERSION=1.1.0 uv pip install \
  --python corpus/toolz-transfer/.venv/bin/python -q -e corpus/toolz-transfer
uv pip install --python corpus/toolz-transfer/.venv/bin/python -q pytest "mutmut==3.7.0"
( cd corpus/toolz-transfer && .venv/bin/python -m pytest -q 2>&1 | tail -1 )

echo
echo "Esperado: 82 passed, 82 passed, 186 passed"
