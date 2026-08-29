PY ?= .venv/bin/python
SET ?= dev

.PHONY: help setup sanity ground-truth predict eval report all clean

help:
	@grep -E '^[a-z-]+:.*?##' $(MAKEFILE_LIST) | sed 's/:.*##/\t/'

setup:            ## cria .venv e prepara os dois corpora pinados
	uv venv --python 3.12 .venv
	bash scripts/setup_corpus.sh

ground-truth:     ## regera o ground truth de mutação (destrói o congelamento — ver METRIC.md R5)
	cd corpus/python-slugify && .venv/bin/mutmut run
	cd corpus/python-slugify-holdout && .venv/bin/mutmut run
	$(PY) eval/build_ground_truth.py python-slugify
	$(PY) eval/build_ground_truth.py python-slugify-holdout

sanity:           ## controles do harness: piso trivial, fabricada errada, aleatório, oráculo
	$(PY) eval/run.py --sanity --set dev
	$(PY) eval/run.py --sanity --set holdout

predict:          ## roda um estágio (STAGE=baseline|s4|s5|s6 SET=dev|holdout)
	PYTHONPATH=src $(PY) -m deadzone.predict --stage $(STAGE) --set $(SET)

eval:             ## pontua um arquivo de predições (PRED=results/x.pred.json)
	$(PY) eval/run.py --predictions $(PRED) --save

report:           ## tabela final: pisos + todos os estágios medidos
	$(PY) eval/report.py

all: sanity report ## caminho de reprodução sem chave de API
