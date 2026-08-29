PY ?= .venv/bin/python
SET ?= dev

.PHONY: help setup sanity ground-truth test predict eval report all clean

help:
	@grep -E '^[a-z-]+:.*?##' $(MAKEFILE_LIST) | sed 's/:.*##/\t/'

setup:            ## cria .venv e prepara os dois corpora pinados
	uv venv --python 3.12 .venv
	bash scripts/setup_corpus.sh

ground-truth:     ## regera o ground truth de mutação — para VERIFICAR, não emendar (METRIC.md R5)
	PY=$(PY) bash scripts/regen_ground_truth.sh

test:             ## testes da própria métrica — se quebrarem, todo results/ perde validade
	$(PY) -m pytest tests/ -q

sanity:           ## controles do harness: piso trivial, fabricada errada, aleatório, oráculo
	$(PY) eval/run.py --sanity --set dev
	$(PY) eval/run.py --sanity --set holdout

predict:          ## roda um estágio (STAGE=baseline|s4|s5|s6 SET=dev|holdout)
	PYTHONPATH=src $(PY) -m deadzone.predict --stage $(STAGE) --set $(SET)

eval:             ## pontua um arquivo de predições (PRED=results/x.pred.json)
	$(PY) eval/run.py --predictions $(PRED) --save

report:           ## tabela final: pisos + todos os estágios medidos
	$(PY) eval/report.py

all: test sanity report ## caminho de reprodução sem chave de API
