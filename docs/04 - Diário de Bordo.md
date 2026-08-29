# Diário de Bordo

> R2 — output cru, colado literal. "Os testes passaram" não é evidência;
> `82 passed in 0.04s` é.

## 2026-08-29 — Sessão 1

### 13:10 · contexto reconstruído

Repo `~/Documents/dev/deadzone` continha só o plano. Vault vazio. Descoberto o
projeto anterior (Apura) e o commit de pivô `80e6e23 chore: archive Apura before
pivot` (29/08 00:20). Ver [[02 - Herança do Apura]].

Ambiente: Python 3.11–3.14 disponíveis, `uv 0.11.19`, `docker 28.2.2`, rede OK.
**Nenhuma chave de LLM no ambiente** → [[05 - Decisões Abertas]] D1.

### 16:15 · S0 — seleção de repositório → ✅ confirmada

```
================ python-semver ================
ERROR: usage: python -m pytest [options] [file_or_dir] [...]
python -m pytest: error: unrecognized arguments: --no-cov-on-fail --cov=semver --cov-report=term-missing
================ cachetools ================
312 passed in 4.33s
real 4.65
================ python-slugify ================
82 passed in 0.04s
real 0.37
================ toolz ================
186 passed in 0.57s
real 0.93
```

Padrões proibidos nos testes:
```
cachetools:      7 ocorrências de datetime.now (test_ttl, test_tlru, test_func)
python-slugify:  (nenhuma)
toolz:           3 ocorrências de os.environ (test_dicttoolz)
```

Escolhido: `python-slugify @ 7b6d5d96c1995e6dccb39a19a13ba78d7d0a3ee4`.

### 16:20 · S1 — ground truth de mutação → ✅ confirmada

Módulos declarados **antes** de rodar: `slugify/slugify.py`, `slugify/special.py`.

```
216/216  🎉 170 🫥 0  ⏰ 0  🤔 0  🙁 46  🔇 0  🧙 0
156.48 mutations/second
.venv/bin/mutmut run  7.18s user 2.95s system 341% cpu 2.964 total
```

Fração de sobreviventes **0.213** — anotada antes de ler o conteúdo dos
sobreviventes, como manda o guardrail do S1.

Ground truth estruturado:
```
{ "mutants": 216, "parsed": 216, "parse_errors": 0, "line_mismatches": 0,
  "killed": 170, "survived": 46, "survivor_fraction": 0.213 }
linhas com sobrevivente: 17
linhas só com mortos:    49
```

`line_mismatches: 0` nos 216 é o número que sustenta todos os outros — ver
[[06 - Hot Takes e Falhas]] § "O offset silencioso".

Holdout `slugify/__main__.py`, mutado na mesma sessão, **não lido**:
```
{ "mutants": 288, "parsed": 288, "parse_errors": 0, "line_mismatches": 0,
  "killed": 189, "survived": 99, "survivor_fraction": 0.3438 }
linhas com sobrevivente: 30
```

### 16:35 · S2 — schema, métrica e harness → ✅ confirmada

Harness rodou **antes** de existir solução, com predição fabricada errada.

```
label                      set         prec     rec      F1    near   noise mut-rec    evid    type  #pred   #lin
-----------------------------------------------------------------------------------------------------------------
C1-prevê-tudo              dev        0.070   1.000   0.130   0.193   0.738   1.000   0.000   1.000      2    244
C2-fabricada-errada        dev        0.000   0.000   0.000   0.000   1.000   0.000   0.667   0.667      3      9
C3-aleatório-mesmo-orçamento dev      0.118   0.118   0.118   0.176   0.706   0.087   0.941   1.000     17     17
C4-oráculo                 dev        1.000   1.000   1.000   0.000   0.000   1.000   1.000   1.000     17     17
SANIDADE: OK — harness discrimina

C1-prevê-tudo              holdout    0.306   1.000   0.469   0.245   0.449   1.000   0.000   1.000      1     98
C2-fabricada-errada        holdout    0.000   0.000   0.000   0.000   1.000   0.000   0.333   0.667      3      7
C3-aleatório-mesmo-orçamento holdout  0.233   0.233   0.233   0.233   0.533   0.232   0.733   1.000     30     30
C4-oráculo                 holdout    1.000   1.000   1.000   0.000   0.000   1.000   1.000   1.000     30     30
SANIDADE: OK — harness discrimina
```

**Achado que mudou o formato do relatório:** no holdout, prever o arquivo
inteiro dá **F1 0.469**. O piso trivial não é zero. `eval/report.py` passou a
imprimir o piso em toda tabela, sempre. Ver [[06 - Hot Takes e Falhas]].

### 17:00 · código dos estágios escrito, não medido

`src/deadzone/llm.py` (record/replay, replay falha alto sem gravação),
`src/deadzone/predict.py` (baseline → s4 → s5 → s6), `prompts/` versionados,
`Dockerfile`, `README.md`, `REPRODUCTION.md`, `CHANGELOG.md`, `METRIC.md`.

S3 em diante **bloqueado por [[05 - Decisões Abertas]] D1**, não por código.

### 17:30 · S7 antecipado — reprodução verificada, não presumida

O plano põe o container no S7, depois das iterações. Antecipei porque o gatilho
de abort nº3 diz que solução boa sem reprodução perde para solução estreita e
reproduzível — e porque a parte reprodutível já estava pronta.

```
$ docker run --rm --network none deadzone
python -m pytest tests/ -q
....................                                                     [100%]
20 passed in 0.04s
...
SANIDADE: OK — harness discrimina
```

Regeneração do ground truth dentro do container, sem rede:

```
== mutmut run: python-slugify
{ "mutants": 216, "parsed": 216, "parse_errors": 0, "line_mismatches": 0,
  "killed": 170, "survived": 46, "survivor_fraction": 0.213 }
== mutmut run: python-slugify-holdout
{ "mutants": 288, "parsed": 288, "parse_errors": 0, "line_mismatches": 0,
  "killed": 189, "survived": 99, "survivor_fraction": 0.3438 }
```

Bate exato. Os artefatos congelados são **reproduzíveis a partir da fonte**, não
só commitados. Path B também verificado em clone limpo com zero dependências.

### 18:00 · pipeline provado em replay, antes de qualquer chamada real

`tests/test_pipeline_replay.py` planta gravações sintéticas nas chaves exatas
que o pipeline vai procurar e roda os quatro estágios de ponta a ponta.

```
34 passed in 0.08s
```

O que os testes fecham, e por quê cada um existe:

- replay sem gravação **quebra** e não degrada para chamada de rede (R2)
- resposta não parseável **quebra** em vez de virar lista vazia silenciosa
- a chave de API nunca entra numa gravação — testado com chave falsa no ambiente
- o gate do S5 descarta âncora inventada: 2 predições entram, 1 sai
- `reconcile` funde sobreposto e não funde tipos diferentes
- os 4 estágios recuperam precisão 1.000 / recall 1.000 quando alimentados com
  o oráculo — ou seja, **nenhum estágio perde predição no caminho**

Este último é o que importa: se o S6 medir mal depois, o erro vai estar no
modelo ou no prompt, não na tubulação. A tubulação já foi isolada.
