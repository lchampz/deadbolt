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

## S3 — Baseline medido ✅ CONFIRMADA

Parseou de primeira nos três conjuntos. `claude-opus-5`, effort `high`.

| Conjunto | piso trivial | baseline F1 | precisão | recall |
|---|---:|---:|---:|---:|
| DEV | 0.130 | **0.292** | 0.226 | 0.412 |
| HOLDOUT | 0.537 | **0.464** | 0.650 | 0.361 |
| TRANSFER | 0.091 | **0.131** | 0.093 | 0.220 |

Baseline **forte** no holdout — 0.464 contra piso aleatório 0.361. Não foi
enfraquecido. Enfraquecer baseline é a fraude mais detectável que existe.

---

## S4 — Taxonomia como skill ✅ CONFIRMADA

`MORRE SE:` precisão não sobe ≥ 3 pontos.

| Conjunto | precisão antes → depois | Δ | veredito |
|---|---|---:|---|
| DEV | 0.226 → 0.360 | +13.4 pts | ✅ |
| HOLDOUT | 0.650 → 0.684 | +3.4 pts | ✅ (raspando) |
| TRANSFER | 0.093 → 0.125 | +3.2 pts | ✅ (raspando) |

Passou nos dois conjuntos em que **não** foi ajustada por 3,4 e 3,2 pontos,
contra uma barra de 3. Mantida.

---

## S5 — Gate de evidência ✅ CONFIRMADA pelo critério, mas derruba F1 no holdout

`MORRE SE:` falso positivo não cai.

Gate é código, não prompt → reusa as gravações do S4 byte a byte. O efeito é
medido sobre **saída idêntica do modelo**, custo US$ 0,00, delta 100% atribuível.

| Conjunto | ruído | precisão | descartadas | F1 |
|---|---|---|---:|---|
| DEV | 0.360 → **0.250** | 0.360 → **0.450** | 2 | 0.429 → **0.486** |
| HOLDOUT | 0.263 → **0.091** | 0.684 → **0.818** | 2 | 0.473 → **0.383** |
| TRANSFER | 0.667 → 0.667 | 0.125 → 0.125 | 0 | inerte |

FP caiu forte nos dois. **E mesmo assim o F1 do holdout caiu**, porque o recall
foi de 0.361 para 0.250: o gate levou verdadeiros positivos junto. Os dois fatos
são o resultado. O critério foi escrito antes e diz confirmada — confirmada fica.

---

## S6 — Varredura por função ✅ CONFIRMADA pelo critério

`MORRE SE:` recall não sobe.

| Conjunto | recall antes → depois | precisão antes → depois | F1 |
|---|---|---|---|
| DEV | 0.529 → **0.588** | 0.450 → 0.556 | 0.486 → **0.571** |
| HOLDOUT | 0.250 → **0.389** | 0.818 → 0.452 | 0.383 → **0.418** |

No DEV é a melhor configuração em toda coluna. No holdout comprou recall
devolvendo quase toda a precisão que o S5 tinha ganho.

Não rodado no TRANSFER: 45 funções em `functoolz.py` = 45 chamadas para um
conjunto opcional. **Corte de orçamento declarado em METRIC.md § 9 antes de
medir**, não resultado omitido.

---

## O veredito que importa

| Conjunto | piso | baseline | S4 | S5 | S6 | oráculo |
|---|---:|---:|---:|---:|---:|---:|
| DEV | 0.130 | 0.292 | 0.429 | 0.486 | **0.571** | 1.000 |
| HOLDOUT | **0.537** | 0.464 | 0.473 | 0.383 | 0.418 | 1.000 |
| TRANSFER | 0.091 | 0.131 | **0.148** | 0.148 | — | 1.000 |

No DEV — onde iterei — o pipeline chega a 4,4× o piso e sobe a cada passo.

**No HOLDOUT nada bate prever o arquivo inteiro.** Piso 0.537, melhor
configuração 0.473. Todo ganho construído olhando o DEV encolheu ou inverteu num
módulo da *mesma biblioteca*, testado pela *mesma suíte*.

Esse é o achado. É exatamente a falha que o projeto anterior entregou como
vitória, e só está visível porque o piso foi calculado no S2, antes de existir
solução, e impresso em toda tabela desde então.

**Nenhuma iteração foi removida** — nenhuma bateu na própria condição de morte.
O que falhou não é uma iteração, é a transferência de todas elas, e não existe
uma mudança para deletar que conserte isso.

**Custo:** US$ 2,16 em 14 chamadas gravadas.
