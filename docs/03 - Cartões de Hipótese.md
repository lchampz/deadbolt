# Cartões de Hipótese

> R1 — o critério de saída é escrito **antes** de rodar. Um cartão fechado não se
> reabre. Veredito em três valores: **confirmada / morta / inconclusiva**
> (inconclusiva = morta).
>
> Adaptação do harness: o plano previa "Claude pensa → Cursor executa → Claude
> revisa". Nesta sessão Claude ocupa os três papéis. A mitigação é R2 levada ao
> pé da letra: **todo veredito cita output cru** colado em [[04 - Diário de Bordo]],
> nunca prosa. Registrado como risco em [[06 - Hot Takes e Falhas]].

---

## S0 — Seleção de repositório ✅ CONFIRMADA

```
HIPÓTESE:    existe lib Python pura, entre os candidatos, cuja suíte fica verde
             de primeira em < 30s
CONFIRMA SE: suíte verde sem intervenção manual E tempo < 30s
MORRE SE:    qualquer teste falha no clone limpo · tempo >= 30s · aparece
             requests/urllib/socket/datetime.now/sqlite3 nos testes · precisa env var
TIMEBOX:     15 min por candidato, 2 candidatos
FALLBACK:    próximo candidato; esgotados os 4 → reavaliar abordagem
ARTEFATO:    repo pinado (SHA) + corpus vendorizado
```

**Desvio declarado:** rodei os 4 candidatos em paralelo em vez de 2 sequenciais.
Não altera o critério nem a ordem de preferência — só o relógio. Registrado.

### Veredito por candidato

| # | Candidato | Resultado | Veredito |
|---|---|---|---|
| 1 | `python-semver` | `error: unrecognized arguments: --no-cov-on-fail --cov=semver` | **morta** — `.pytest.ini` exige `pytest-cov`; instalar seria passo manual fora do comando pré-registrado |
| 2 | `cachetools` | `312 passed in 4.33s` | **morta** — 7 usos de `datetime.now` em `test_ttl/test_tlru/test_func`; está na lista de morte |
| 3 | `python-slugify` | `82 passed in 0.04s` | ✅ **confirmada** — zero padrões proibidos |
| 4 | `toolz` | `186 passed in 0.57s` | não avaliado (3 já confirmou) |

**Guardrail aplicado.** `cachetools` era o candidato mais atraente (312 testes,
5 módulos). Matei mesmo assim: `datetime.now` estava na lista escrita **antes**.
Manter seria exatamente o "ajustar o critério depois de ver o resultado" que R1
existe para impedir — e o custo real seria mutante flaky em `TTLCache`.

**Artefato:** `corpus/python-slugify/` @ `7b6d5d96c1995e6dccb39a19a13ba78d7d0a3ee4`
(2026-01-07), licença MIT, `PINNED_SHA.txt` commitado.

---

## S1 — Ground truth de mutação ✅ CONFIRMADA

```
HIPÓTESE:    mutmut roda nos módulos escolhidos e produz fração de sobreviventes
             entre 5% e 30%
CONFIRMA SE: 40 <= total de mutantes <= 400 E 5% <= sobreviventes <= 30%
             E execução < 20 min
MORRE SE:    zero sobreviventes (sem classe positiva) · > 50% sobreviventes
             (tarefa trivial) · mutmut não configura em 20 min · execução > 30 min
TIMEBOX:     45 min
FALLBACK:    trocar o módulo mutado antes de trocar o repo — a troca declarada
             é adicionar `slugify/__main__.py`; se 2 conjuntos falharem, volta
             ao S0 com `toolz`
ARTEFATO:    data/ground_truth/mutation_report.txt commitado
```

**Módulos declarados ANTES de rodar:** `slugify/slugify.py` (197 linhas,
`smart_truncate` + `slugify`) e `slugify/special.py` (47 linhas,
`add_uppercase_char`). São os módulos de biblioteca; `__main__.py` é cola de CLI
e fica de fora do conjunto primário — ele é o **fallback declarado**, não um
ingrediente que eu adiciono depois de ver o número.

**Guardrail aplicado:** a fração foi anotada **antes** de ler o conteúdo dos
sobreviventes.

### Veredito

| Condição pré-registrada | Medido | |
|---|---|---|
| 40 ≤ mutantes ≤ 400 | 216 | ✅ |
| 5% ≤ sobreviventes ≤ 30% | **21.3%** (46/216) | ✅ |
| execução < 20 min | 2.96s | ✅ |

Fallback não acionado. `slugify/__main__.py` **não** entrou no conjunto primário
— foi promovido a **HOLDOUT**, mutado na mesma sessão (288 mutantes, 99
sobreviventes, 34.4%) e deixado sem leitura até o S7.

**Artefato:** `data/ground_truth/mutation_report.txt` + `mutants-*.json`.
Verificação que sustenta tudo: `parse_errors: 0, line_mismatches: 0` nos 216
e nos 288 — ver [[06 - Hot Takes e Falhas]] § "O offset silencioso".

---

## S2 — Schema e congelamento da métrica ✅ CONFIRMADA

```
HIPÓTESE:    o harness roda de ponta a ponta com predição falsa fabricada à mão
             e produz números
CONFIRMA SE: harness roda ANTES de existir solução e dá número RUIM para
             predição deliberadamente errada
MORRE SE:    não consigo rodar o harness sem ter a solução pronta
FALLBACK:    simplificar a regra de casamento até rodar (casamento por arquivo)
ARTEFATO:    eval/ funcionando + METRIC.md com timestamp
```

**Veredito: confirmada.** Quatro controles, dois conjuntos, todos passando.
Fallback não acionado — a regra de casamento por linha rodou de primeira.

| Controle | DEV F1 | HOLDOUT F1 | Prova |
|---|---:|---:|---|
| prever arquivo inteiro | 0.130 | **0.469** | o piso trivial, e ele não é zero |
| fabricada errada | 0.000 | 0.000 | o harness não premia besteira |
| aleatório, mesmo orçamento | 0.118 | 0.233 | nível de acaso |
| oráculo | 1.000 | 1.000 | o teto é atingível |

**Congelado em 2026-08-29T16:30:00Z:** métrica, schema, taxonomia de 6 tipos,
regra de casamento e corpus. R5 vale a partir daqui.

## S3 — Baseline medido 🔴 BLOQUEADO — [[05 - Decisões Abertas]] D1

Código pronto e testado em seco: `src/deadzone/predict.py --stage baseline`.
Prompt versionado em `prompts/system_baseline.md`. Falta **só** acesso a modelo.

```
HIPÓTESE:    um prompt único produz predições mensuráveis, com desempenho
             pior que o pipeline final
CONFIRMA SE: baseline roda nos dois conjuntos e produz precisão e recall
             registrados com timestamp
MORRE SE:    saída não parseável — nesse caso ajusta-se SÓ o parsing,
             nunca o prompt para melhorar resultado
ARTEFATO:    results/baseline-{dev,holdout}.pred.json + recordings/
```

**Piso a bater, já conhecido:** F1 0.130 no DEV, **0.469 no HOLDOUT**. Se o
baseline sair forte, não se enfraquece o baseline — reporta-se como achado.

## S4/S5/S6 — Iterações ⏳ PENDENTE

## S7 — Congelamento e container ⏳ PENDENTE
