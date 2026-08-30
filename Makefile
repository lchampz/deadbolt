PY ?= .venv/bin/python
SET ?= dev

.PHONY: help setup sanity ground-truth test predict eval report report-testgen verify testgen submission-table run-all check-creds all clean

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
	$(PY) eval/run.py --sanity --set transfer

predict:          ## roda um estágio (STAGE=baseline|s4|s5|s6 SET=dev|holdout)
	PYTHONPATH=src $(PY) -m deadbolt.predict --stage $(STAGE) --set $(SET)

eval:             ## pontua um arquivo de predições (PRED=results/x.pred.json)
	$(PY) eval/run.py --predictions $(PRED) --save

submission-table: ## reescreve a tabela dentro de SUBMISSION.md a partir de report.py
	$(PY) scripts/refresh_submission_table.py

check-creds:      ## separa "chave inválida" de "saldo zerado" usando endpoints gratuitos
	$(PY) scripts/check_credentials.py

run-all:          ## grava os 4 estágios nos 2 conjuntos e refaz a tabela (exige DEADBOLT_MODE=live)
	bash scripts/run_all_stages.sh

report-testgen:   ## tabela do Deadbolt — antes/depois, ablação e camada 2
	$(PY) eval/report_testgen.py

verify:           ## roda o mutmut do zero sobre os testes gerados (SET=dev SUF=)
	$(PY) eval/verify_mutmut.py $(SET) T3 $(SUF)

testgen:          ## gera testes num estágio (STAGE=B|T1|T2|T3 SET=dev|holdout|transfer)
	PYTHONPATH=src $(PY) -m deadbolt.testgen --stage $(STAGE) --set $(SET)

report:           ## tabela final: pisos + todos os estágios medidos
	$(PY) eval/report.py

all: test sanity report report-testgen ## caminho de reprodução sem chave de API
