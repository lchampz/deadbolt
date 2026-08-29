# Pivô — de prever o buraco para fechá-lo

Documento de decisão. Escrito em 2026-08-29, **antes** de qualquer implementação.
Sucessor de `DISCUSSION_01-deadzone-plano-execucao.md`. As cinco regras
invioláveis daquele documento continuam valendo na íntegra — R1 pré-registro,
R2 output cru, R3 falsificação explícita, R4 timebox com fallback, R5
congelamento. Nada aqui as relaxa.

---

## 1. Por que pivotar

O Deadzone foi medido honestamente e o resultado está publicado:

| Conjunto | piso trivial | baseline | melhor configuração |
|---|---:|---:|---:|
| DEV | 0.130 | 0.292 | **0.571** |
| HOLDOUT | **0.537** | 0.464 | 0.473 |
| TRANSFER | 0.091 | 0.131 | **0.148** |

No holdout **nada bate prever o arquivo inteiro**. Em linhas absolutas, o
aparato inteiro acha uma linha cega a mais que um prompt único.

O erro não foi execução. Foi a **forma da tarefa**: localização de alta
cardinalidade, sem retorno. O agente apontava 17 linhas em 244 e nunca descobria
se tinha acertado. E havia uma assimetria absurda — **o oráculo estava na mesa o
tempo todo** e o agente foi proibido de usá-lo.

### A propriedade que faltava

Apura e Deadzone apostaram o projeto numa hipótese que podia ser falsa. Executar
bem não protege contra isso. A correção não é escolher hipótese melhor; é
escolher uma tarefa cuja **métrica seja monotônica por construção**.

> Um mutante morre se **algum** teste falha nele. Adicionar testes só amplia o
> conjunto de testes que falham. **Adicionar teste nunca ressuscita mutante.**

Condicionado a uma guarda mecânica — a suíte original tem que continuar verde —
o mutation score é **incapaz de cair**. O pior caso deste projeto é "subiu
pouco". Não existe quadrante negativo.

---

## 2. A tarefa

> Dado um módulo, sua suíte e os mutantes que sobreviveram, **escrever os testes
> que matam esses mutantes** — e provar que mataram.

Entregável: um **diff que um mantenedor faz merge**, não um relatório.

### Por que o oráculo muda tudo

O preditor chutava no escuro. O gerador fecha o loop contra a verdade no momento
da geração. É a diferença estrutural, e é a razão para eu esperar que **desta vez
transfira** — não há heurística de corpus para superajustar.

---

## 3. Evidência que já existe (spike de 2026-08-29)

Cinco sobreviventes do DEV, escolhidos por regra declarada antes de olhar
(ordenar por arquivo/linha/id, passo 9). Um disparo, sem loop de reparo.

```
[1/5] slugify/slugify.py:30   MATOU   word_boundary: bool = False → True
[2/5] slugify/slugify.py:115  MATOU   text = str(...) → text = None
[3/5] slugify/slugify.py:115  MATOU   'ignore' → 'XXignoreXX'
[4/5] slugify/slugify.py:129  não matou
[5/5] slugify/special.py:9    não matou
MATOU 3/5 em uma tentativa, sem loop de reparo
custo US$ 0.4965 · 66407 in / 6579 out
```

**Caso 4 não é falha — é mutante impossível.** A linha 129 está sob
`if not isinstance(text, str)`, mas a linha 125 é `unidecode.unidecode(text)`,
que sempre devolve `str`. **Código morto e inalcançável.** Nenhum teste mata.
Achado de produto, não erro: *linha cuja mutação ninguém mata é candidata a
código morto.*

**Caso 5 é exatamente o caso do loop.** O modelo escreveu
`assert slugify('ÄÖÜ') == 'aeoeue'` — plausível, no estilo da suíte, e errado:
`python-slugify` não faz transliteração alemã por padrão. **O teste falhou no
código original.** Num fluxo ingênuo de "peça testes ao LLM e commite", esse
teste teria quebrado a suíte.

**Taxa real one-shot: 3 de 4 matáveis = 75%.** Alto o bastante para entregar
valor, baixo o bastante para o loop ter o que provar.

---

## 4. Métrica primária — a congelar antes de rodar

**Mutation score do módulo, antes vs. depois**, medido por `mutmut` rodando do
zero. Não é auto-relato: quem confere é a mesma ferramenta externa que gerou o
ground truth.

Linha de partida, já medida e congelada:

| Conjunto | módulos | mutantes | mortos | score atual |
|---|---|---:|---:|---:|
| DEV | `slugify.py`, `special.py` | 216 | 170 | **78.7%** |
| HOLDOUT | `__main__.py` | 298 | 189 | **63.4%** |
| TRANSFER | `toolz/functoolz.py` | 534 | 416 | **77.9%** |

**Propriedade que torna a evidência forte:** só a suíte muda, o fonte não. Os
IDs de mutante são estáveis entre as duas execuções. Então o relatório não diz
só "o agregado subiu" — diz **exatamente quais mutantes morreram**, um a um.

### O teto, declarado antes e não depois

Reportar "matamos 70%" sem teto é inflar — o mesmo erro do piso, invertido.
Definição operacional, escrita agora:

- **matável demonstrado** — existe um teste que o mata. Provado por construção.
- **indeterminado** — sobreviveu a N tentativas com feedback. **Não é sinônimo
  de equivalente.**
- **equivalente/inalcançável** — só após triagem manual do conjunto
  indeterminado, com evidência escrita caso a caso (como a linha 129 acima).

Nenhum percentual é reportado sobre um denominador que inclua indeterminados
não triados.

### Métricas secundárias

| métrica | por quê |
|---|---|
| testes gerados vs. testes que mataram algo | desperdício do modelo |
| testes que **quebram** a suíte original | dano que a guarda evita |
| mutantes mortos por teste | densidade, não volume |
| custo e tempo por módulo | FinOps vira feature |
| linhas de teste adicionadas | tamanho do diff que o humano revisa |

---

## 5. As três guardas mecânicas

Toda predição de teste passa pelas três. Nenhuma é julgamento.

1. **Passa no código original.** Senão o teste está errado, não o código.
2. **Falha no código mutado.** Senão não mata nada.
3. **A suíte original inteira continua verde.** Senão o teste quebrou outra coisa.

Teste que viola qualquer uma é **descartado ou devolvido ao loop, nunca
corrigido à mão**.

---

## 6. Estágios cumulativos

| # | Estágio | Capability | Hipótese | **MORRE SE** |
|---|---|---|---|---|
| **B** | Baseline ingênuo | — | "escreva mais testes para este módulo", sem lista de mutantes, sem verificação | saída não parseável (ajusta-se só o parsing) |
| **T1** | Alvo | contexto | dar os diffs dos sobreviventes bate escrever no escuro | não mata mais que o baseline filtrado |
| **T2** | Guardas | verificação | as três guardas cortam teste quebrado e inútil | não descarta nada |
| **T3** | Reparo | iteração com feedback | devolver a falha da guarda converte indeterminado em morto | converte < 20% do que o T2 rejeitou |

### Regra de justiça do baseline, decidida agora

Teste do baseline que quebra a suíte **não é silenciosamente descartado**. Reporta-se:

- **baseline-cru** — o que você realmente commitaria, quebras incluídas
- **baseline-filtrado** — quebras removidas

A diferença entre os dois **é o valor da guarda**. A diferença entre
baseline-filtrado e T3 é o valor do alvo + reparo. Enfraquecer baseline continua
proibido.

### Disciplina de holdout

Prompt e loop são desenvolvidos olhando **só o DEV** (`slugify.py`, `special.py`).
`__main__.py` e `toolz/functoolz.py` ficam **fechados** até a rodada final.

Da última vez essa regra mordeu e revelou que os ganhos não transferiam. Se
morder de novo, entra na tabela do mesmo jeito.

---

## 7. Orçamento

O spike custou **US$ 0,10 por chamada** — módulo inteiro mais 657 linhas de
`test.py` reenviados a cada vez. Nesse ritmo, 273 sobreviventes custariam ~US$ 27
contra **US$ 7,34** disponíveis.

Duas correções, ambas viram argumento de engenharia no relatório:

1. **Prompt caching** — o prefixo é byte-idêntico entre chamadas. Corta ~90% da
   entrada.
2. **Batelada** — 8 a 10 mutantes por chamada em vez de um.

Estimativa depois das duas: **US$ 2 a 3 para o projeto inteiro**, e "custo por
módulo" deixa de ser risco e vira métrica secundária.

---

## 8. Riscos, escritos antes

| risco | mitigação |
|---|---|
| Baseline forte demais e o loop não tem o que provar | reporta honesto; a história desloca para `__main__` (63.4%, o mais cego) e `toolz` |
| Equivalentes inflam o percentual | definição operacional do § 4 + triagem manual só do indeterminado |
| Teste que mata mas é ruim | o diff fica visível e segue o estilo da suíte; conta-se linhas adicionadas |
| **Prior art — TestGen-LLM (Meta)** | encarar de frente no README. O diferencial é a disciplina de medição e o teto declarado, não a ideia |
| Não transferir também | risco real, menor que no Deadzone: o loop verifica contra o oráculo em vez de adivinhar |
| Tempo | ~46h até 31/08 18:00 UTC; ~14h de execução previstas |

**Rede de segurança:** o Deadzone está entregue — repo público, container
reproduzindo offline, 37 testes, changelog, trajetórias, submission mapeado no
rubric. Se este pivô falhar, aquilo é submetido como está. **Este trabalho é
estritamente aditivo.**

---

## 9. O que o resultado negativo vira

Capítulo um, e ele justifica a arquitetura:

> "Construí um preditor de ponto cego. Medi honestamente e ele não transferiu —
> no holdout perde para uma heurística de uma linha. Aí vi o erro: eu tinha o
> oráculo na mão e estava pedindo ao agente para adivinhar. O agente não precisa
> prever onde a suíte é cega. Precisa fechar o buraco e provar que fechou."

Isso é o Hot Take (5 pts) e é a razão de existir de cada capability (30 pts).
Juiz desconta falha escondida, não falha que virou decisão.

---

## 10. Cronograma

| etapa | duração |
|---|---|
| Congelar métrica, teto e guardas | 1,5h |
| Pipeline de geração + guardas + reparo | 3h |
| Loop de dev **só no DEV** | 1,5h |
| Congelar; rodar holdout e transfer | 1h |
| Re-rodar `mutmut`, tabelas antes/depois | 1h |
| Ablação (B / T1 / T2 / T3) | 1h |
| Docs, changelog, submission, README | 3h |
| **Vídeo — Victor** | 3h |

~14h de execução, ~3h de gravação, dentro das ~46h com folga.

---

## 11. Decisões tomadas

| # | decisão |
|---|---|
| D1 | Pivotar para geração de testes verificada. **Aprovado 2026-08-29.** |
| D2 | Escopo: **os três corpora** — DEV, HOLDOUT e TRANSFER. **Aprovado 2026-08-29.** |
| D3 | Mesmo repositório. O resultado negativo do Deadzone fica publicado como capítulo um, não é apagado nem reescrito. |
| D4 | Modelo `claude-opus-5`, effort `high`, idêntico no baseline e em todos os estágios — igual ao Deadzone. |

## 12. Aguardando aprovação

Nada é implementado antes do "ok" nos cartões acima. O primeiro artefato depois
da aprovação é `METRIC_TESTGEN.md` com a métrica, o teto e as guardas
congelados e datados — **antes** de qualquer geração.
