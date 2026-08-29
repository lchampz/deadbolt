# Deadzone — plano de execução

Preditor de ponto cego de teste. Submissão para o micro1 Frontier Engineering Challenge 2026.
Prazo: **31/08 18:00 UTC**. Orçamento: ~9,5h de trabalho real.

Harness: **Claude pensa → Cursor executa → Claude revisa.** Todo estágio fecha com revisão.

---

## 1. As cinco regras invioláveis

Estas regras existem porque hipótese falsamente validada é o modo de falha que já te custou um dia. Cada uma fecha uma porta específica.

**R1 — Pré-registro.** O critério de saída de um estágio é escrito **antes** de rodar qualquer coisa. Se depois de ver o resultado você sentir vontade de ajustar o critério, pare. Essa vontade é o sintoma. O critério não muda.

**R2 — Output cru.** O Cursor nunca reporta resultado em prosa. Ele cola `stdout` e `stderr` literais. Claude lê o output, não o resumo. "Os testes passaram" não é evidência; `47 passed in 3.21s` é.

**R3 — Falsificação explícita.** Todo cartão de hipótese declara **o que mataria a hipótese**, não só o que a confirmaria. Se você não consegue escrever como ela morre, ela não é testável e o estágio está mal definido.

**R4 — Timebox com fallback nomeado.** Todo estágio tem teto de tempo e um plano B escrito antes de começar. Estourou o teto, executa o plano B. Não negocia, não estende "só mais quinze minutos".

**R5 — Congelamento é congelamento.** Depois do primeiro número medido, métrica e corpus não mudam. Adicionar caso ou ajustar métrica depois de ver resultado destrói a comparação inteira e te custa Measured Improvement.

> Ironia útil: o projeto audita agentes que declaram sucesso sem verificar. R2 é a mesma disciplina aplicada a você.

---

## 2. Protocolo do ciclo

Todo estágio roda em quatro tempos. Não pule o quarto.

### T1 — Claude pensa (5–10 min)
Entrada: estado atual + objetivo do estágio.
Saída: **cartão de hipótese preenchido** + instrução de execução para o Cursor.
Regra: o cartão sai antes da instrução. Se você não consegue preencher o cartão, não delega.

### T2 — Cursor executa
Entrada: instrução com escopo fechado e comandos explícitos.
Saída: **output cru**, colado inteiro.
Regra: o Cursor não decide, não amplia escopo, não "aproveita para arrumar". Executa e devolve.

### T3 — Claude revisa
Entrada: output cru + cartão de hipótese.
Saída: veredito em três valores — **confirmada / morta / inconclusiva**.
Regra: rodar o checklist de red flags (seção 5) antes de dar veredito.

### T4 — Decisão
- **Confirmada** → commita o artefato, avança.
- **Morta** → executa o fallback do cartão. Não improvisa.
- **Inconclusiva** → é morta. Não existe "quase". Inconclusiva com timebox estourado vira fallback.

### Formato da instrução ao Cursor

```
CONTEXTO: <uma frase>
COMANDOS: <lista exata, copiável>
ESCOPO: apenas os comandos acima. Não instale nada extra,
        não edite arquivo não listado, não corrija erro por conta própria.
SE FALHAR: pare e cole o erro completo. Não tente consertar.
DEVOLVA: stdout e stderr literais, sem resumo e sem interpretação.
```

A cláusula **SE FALHAR** é a mais importante. Agente que conserta silenciosamente é como hipótese errada vira verdade.

### Cartão de hipótese

```
ESTÁGIO:
HIPÓTESE:            <afirmação falsificável>
CONFIRMA SE:         <comando + saída esperada, numérica quando possível>
MORRE SE:            <resultado concreto que aborta>
TIMEBOX:             <minutos>
FALLBACK:            <ação exata se morrer ou estourar>
ARTEFATO:            <o que fica commitado se confirmar>
```

---

## 3. Estágios

Horas relativas ao início (H+0).

### S0 — Seleção de repositório · H+0 → H+0,5

**Hipótese:** existe uma lib Python pura, entre os candidatos, cuja suíte fica verde de primeira em menos de 30s.

**Candidatos, nesta ordem:** `python-semver` · `cachetools` · `python-slugify` · `toolz`

**Cursor executa, por candidato (15 min de teto cada, dois candidatos no máximo):**
```
git clone <repo> && cd <repo>
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]" || (pip install -e . && pip install pytest)
time pytest
```

**Confirma se:** suíte verde sem intervenção manual **e** tempo total < 30s.

**Morre se:** qualquer teste falha no clone limpo · tempo ≥ 30s · aparece `requests`, `urllib`, `socket`, `datetime.now`, `sqlite3` nos testes · precisa de env var.

**Fallback:** próximo candidato. Esgotou os quatro → **pare e reavalie a abordagem**, não o repo. Quatro falhas seguidas significam critério errado, não azar.

**Artefato:** repo pinado (commit SHA fixo) + `requirements.lock`.

> **Guardrail específico:** "verde depois que eu instalei tal pacote" é **morta**, não confirmada. O juiz clona limpo. Se você precisou de um passo manual, ele também vai precisar, e ele não vai saber qual.

---

### S1 — Ground truth de mutação · H+0,5 → H+1,25

**Hipótese:** `mutmut` roda em 1–2 módulos do repo escolhido e produz fração de sobreviventes entre 5% e 30%.

**Cursor executa:**
```
pip install mutmut
mutmut run --paths-to-mutate <src>/<modulo>
mutmut results
mutmut results > mutation_report.txt
```

**Confirma se:** total de mutantes entre ~40 e ~400 **e** sobreviventes entre 5% e 30% **e** execução < 20 min.

**Morre se:** zero sobreviventes (sem classe positiva) · mais de 50% sobreviventes (suíte fraca demais, tarefa trivial) · `mutmut` não configura em 20 min · execução passa de 30 min.

**Fallback:** trocar o módulo mutado antes de trocar o repo. Se dois módulos falharem, volta ao S0 com o próximo candidato.

**Artefato:** `mutation_report.txt` **commitado**. Este é o ativo mais valioso do projeto — o juiz nunca vai regerá-lo.

> **Guardrail específico:** anote a fração de sobreviventes **antes** de olhar o conteúdo deles. Ler os sobreviventes primeiro contamina seu julgamento sobre a dificuldade da tarefa e leva a calibrar a métrica para o que você já viu.

---

### S2 — Schema e congelamento da métrica · H+1,25 → H+1,75

**Claude pensa. Cursor só escreve o esqueleto.**

Define e **congela**:
- Schema de saída da predição: por função — `file`, `line_range`, `blind_spot_type`, `evidence_quote`, `confidence`
- Taxonomia de ponto cego (4 a 6 tipos nomeados)
- Métrica primária: **precisão e recall contra os mutantes sobreviventes**
- Métricas secundárias: taxa de falso positivo, custo por módulo, tempo por módulo
- Regra de casamento: quando uma predição "acerta" um mutante sobrevivente (por arquivo + faixa de linha)

**Confirma se:** o harness de avaliação roda de ponta a ponta com predição **falsa fabricada à mão** e produz números.

**Morre se:** você não consegue rodar o harness sem ter a solução pronta.

**Fallback:** simplificar a regra de casamento até rodar. Casamento por arquivo apenas, se preciso.

**Artefato:** `eval/` com harness funcionando + `METRIC.md` com a métrica congelada e timestamp.

> **Guardrail específico:** o harness tem que rodar **antes** de existir qualquer solução. Harness construído depois é harness moldado ao resultado. Teste-o com uma predição deliberadamente errada e confirme que ele dá números ruins — se der números bons, o harness está quebrado.

---

### S3 — Baseline medido · H+1,75 → H+2,25

**Hipótese:** um prompt único produz predições mensuráveis, com desempenho pior que o pipeline final.

Baseline: um prompt, mesmo modelo, **mesmo schema de saída**, sem taxonomia, sem gate, sem varredura por função.

**Confirma se:** baseline roda nos módulos escolhidos e produz precisão e recall registrados com timestamp.

**Morre se:** baseline não produz saída parseável — nesse caso ajuste **só o parsing**, nunca o prompt para melhorar resultado.

**Artefato:** `results/baseline.json` **commitado com timestamp**, e a gravação bruta da chamada em `recordings/`.

> **Guardrail específico:** este é o estágio onde a tentação de trapacear é máxima. Se o baseline sair bom demais, **não o piore**. Baseline forte é achado honesto e você reporta como tal. Enfraquecer baseline é a fraude mais detectável que existe num relatório de hackathon.

---

### S4–S6 — Três iterações · H+2,25 → H+5

Uma medição por iteração. Cada uma tem cartão próprio.

| # | Mudança | Hipótese | Morre se |
|---|---|---|---|
| S4 | Taxonomia como skill | Nomear os tipos aumenta precisão | precisão não sobe ≥ 3 pontos |
| S5 | Gate de evidência (código) | Exigir âncora arquivo+linha derruba falso positivo | FP não cai |
| S6 | Varredura por função + reconciliação | Dividir contexto aumenta recall | recall não sobe |

**Regra de cada iteração:**
1. Escreve a hipótese e o delta esperado **antes** de implementar
2. Cursor implementa, escopo fechado
3. Roda a avaliação **inteira**, não um subconjunto
4. Registra o número, mesmo que ruim
5. Decide: mantém, revisa, ou **remove**

**Guardrail:** iteração que não move a métrica é **removida e registrada como removida**. O brief pede explicitamente experimentos descartados e o que ensinaram. Uma remoção honesta vale mais que três melhorias marginais infladas.

**Timebox:** 50 min por iteração. Estourou, congela onde está e passa para a próxima.

**Record/replay:** toda chamada de modelo gravada desde S3. Reavaliar roda em `--replay`, custo zero.

---

### S7 — Congelamento e container · H+5 → H+6

Run final. Resultados congelados. Dockerfile com um comando. Teste de ambiente limpo feito **por você**, não presumido.

**Confirma se:** `docker build` seguido de um comando produz a tabela final **sem chave de API**, lendo de `recordings/`.

**Morre se:** o caminho de reprodução exige credencial para chegar ao número principal.

**Fallback:** cortar o caminho `--live` da documentação principal e deixá-lo como apêndice opcional.

---

### S8 — Documentação · H+6 → H+7,5

- README: usuário, gargalo, por que importa, o que existia antes de 28/08 (regra 02)
- Improvement Changelog: uma entrada por iteração, com evidência e decisão
- Guia de reprodução: ambiente limpo, comandos exatos, saída esperada, versões, runtime
- Limitações conhecidas: domínio calibrado só em lib pura; mutantes equivalentes
- Hot take: o modo de falha principal e o que ele ensina

**Guardrail:** escreva as limitações **antes** dos resultados. Ordem inversa produz limitação suavizada.

---

### S9 — Vídeo · H+7,5 → H+8,5

≤5 min, roteirizado. Problema → baseline → uma execução real completa → comparação final → changelog → a mudança que mais contribuiu → o experimento removido.

**Dois takes no máximo.** O terceiro take nunca é melhor que o segundo, só mais tarde.

---

### S10 — Buffer · H+8,5 → H+9,5

Não planeje nada aqui. Algo vai pegar fogo.

---

## 4. Congelamentos

| Momento | O que congela |
|---|---|
| Fim de S1 | Corpus e relatório de mutação |
| Fim de S2 | Métrica e schema |
| Fim de S3 | Baseline |
| Fim de S6 | Solução final |

Depois de cada congelamento, o artefato só muda com **abort declarado por escrito**, com motivo. Não com ajuste silencioso.

---

## 5. Checklist de red flags — rodar em todo T3

Se qualquer item marcar, o veredito é **morta ou inconclusiva**, nunca confirmada.

- [ ] O resultado ficou "perto" do critério e eu quis arredondar a favor
- [ ] Eu mudei o critério depois de ver o número
- [ ] O Cursor disse que funcionou mas não colou output cru
- [ ] Apareceu `|| true`, `try/except` vazio, `--continue-on-error`, ou `pytest -x` mascarando falha
- [ ] Algum teste foi marcado `skip` ou `xfail` para a suíte ficar verde
- [ ] Reduzi N de casos para caber no tempo
- [ ] "Quase funcionou, só falta X" — X é o estágio inteiro
- [ ] Comparei baseline e solução com entradas ou modelos diferentes
- [ ] Rodei a avaliação num subconjunto e extrapolei
- [ ] O número melhorou e eu não sei explicar por quê

O último é o mais perigoso. Melhoria inexplicada é geralmente vazamento de dado, não progresso.

---

## 6. Abort geral

Três gatilhos param o projeto e forçam replanejamento, não continuação:

1. **H+1,25 sem repo e relatório de mutação** → a abordagem inteira está errada, não o repo. Volte à conversa antes de gastar mais uma hora.
2. **H+2,25 sem baseline medido** → corte para duas iterações. Baseline sem solução ainda é submissão; solução sem baseline não é.
3. **H+6 sem container reproduzindo o número** → pare de iterar imediatamente e gaste tudo em documentação. Solução boa sem reprodução perde para solução estreita e reproduzível.

---

## 7. Ordem de sacrifício

Se o tempo apertar, corte nesta ordem — de cima para baixo:

1. Terceira iteração (S6)
2. Sinal de transferência em módulo de perfil diferente
3. Segunda iteração (S5)
4. Métricas secundárias de custo e tempo

**Nunca cortável:** baseline medido, guia de reprodução, changelog, vídeo. São quatro dos seis critérios de nota.
