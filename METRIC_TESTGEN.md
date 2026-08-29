# METRIC_TESTGEN.md — métrica congelada da geração de testes

**Congelada em:** 2026-08-29T21:30:00Z — **antes** de qualquer teste ser gerado.
**Regra R5:** depois deste timestamp, métrica, guardas, definição de teto e
corpus não mudam. Alteração exige abort declarado por escrito neste arquivo,
com motivo e data. Precedente: `METRIC.md` § 8.

Sucede, não substitui, `METRIC.md`. Os números do Deadzone permanecem publicados.

---

## 1. A tarefa

> Dado um módulo, sua suíte e os mutantes que sobreviveram, **escrever os testes
> que matam esses mutantes** — e provar mecanicamente que mataram.

Entregável: um diff que um mantenedor faz merge.

## 2. Por que esta métrica não pode dar negativo

Um mutante morre se **algum** teste falha nele. Adicionar testes só amplia o
conjunto de testes que falham.

> **Adicionar teste nunca ressuscita mutante.**

Condicionado à guarda 3 abaixo — a suíte original continua verde — o mutation
score é **monotonicamente não-decrescente**. O pior caso é "não subiu". Isso é
uma propriedade da tarefa, não uma esperança sobre o modelo.

## 3. Linha de partida — já medida e congelada em `METRIC.md`

| Conjunto | módulos | mutantes | mortos | **score atual** |
|---|---|---:|---:|---:|
| DEV | `slugify/slugify.py`, `slugify/special.py` | 216 | 170 | **78.70%** |
| HOLDOUT | `slugify/__main__.py` | 298 | 189 | **63.42%** |
| TRANSFER | `toolz/functoolz.py` | 534 | 416 | **77.90%** |

**Propriedade que torna a evidência forte:** só a suíte muda; o fonte não. Os
IDs de mutante são **estáveis** entre as duas execuções do `mutmut`. Logo o
relatório não afirma apenas que o agregado subiu — ele nomeia **exatamente quais
mutantes morreram**, um a um, e essa lista é conferível.

## 4. Métrica primária

```
mutation_score = mutantes mortos / mutantes totais
delta          = score_depois - score_antes
```

Medido re-executando `mutmut run` **do zero** no corpus com os testes gerados
adicionados. Quem confere é a ferramenta externa, não este projeto.

## 5. As três guardas mecânicas

Todo teste gerado passa pelas três. Nenhuma envolve julgamento.

| # | guarda | o que ela pega |
|---|---|---|
| G1 | passa no código **original** | teste errado — a expectativa do modelo é falsa |
| G2 | falha no código **mutado** | teste inútil — não detecta nada |
| G3 | a suíte original inteira continua **verde** | teste que quebra outra coisa |

Teste que viola qualquer guarda é **descartado ou devolvido ao loop de reparo,
nunca corrigido à mão**. Nenhum teste entra no diff final sem as três.

## 6. Definição de teto — declarada antes, não depois

Reportar "matamos 70%" sem teto é inflar. É o erro do piso trivial do Deadzone,
invertido. Três estados, e só um deles é conclusão:

| estado | definição | como se prova |
|---|---|---|
| **matável demonstrado** | existe teste que o mata | por construção — o teste existe e as 3 guardas passaram |
| **indeterminado** | sobreviveu a 3 tentativas com feedback | estado de ignorância, **não** sinônimo de equivalente |
| **equivalente / inalcançável** | nenhum teste pode matá-lo | **só** após triagem manual, com evidência escrita caso a caso |

**Nenhum percentual é reportado sobre denominador que inclua indeterminado não
triado.**

## 7. Estágios cumulativos, com condição de morte

| # | estágio | capability | hipótese | **MORRE SE** |
|---|---|---|---|---|
| **B** | baseline ingênuo | — | "escreva mais testes para este módulo", sem lista de mutantes, sem verificação | saída não parseável — ajusta-se só o parsing, nunca o prompt |
| **T1** | alvo | contexto | dar o diff dos sobreviventes bate escrever no escuro | não mata mais que o baseline-filtrado |
| **T2** | guardas | verificação | as 3 guardas cortam teste quebrado e inútil | não descarta nada |
| **T3** | reparo | iteração com feedback | devolver a falha da guarda converte indeterminado em morto | converte < 20% do que o T2 rejeitou |

### Regra de justiça do baseline, decidida agora

Teste do baseline que quebra a suíte **não é silenciosamente descartado**.
Reportam-se dois números:

- **baseline-cru** — o que você realmente commitaria, quebras incluídas
- **baseline-filtrado** — quebras removidas

A diferença entre os dois **é o valor da guarda**. A diferença entre
baseline-filtrado e T3 é o valor do alvo mais o reparo. Enfraquecer baseline
continua proibido; baseline forte é achado honesto e reporta-se como tal.

### Disciplina de holdout

Prompt e loop são desenvolvidos olhando **exclusivamente o DEV**. `__main__.py`
e `toolz/functoolz.py` ficam fechados até a rodada final, executada uma vez.

Da última vez essa regra mordeu e revelou que os ganhos não transferiam. Se
morder de novo, entra na tabela do mesmo jeito.

---

## 8. Camada 2 — o que sobrevive é sinal, não ruído

Em MuTAP, MUTGEN, PRIMG e no ACH da Meta, o mutante que sobrevive à geração é
tratado como fracasso: ruído a minimizar. Aqui ele é a saída.

### O argumento, que é prova e não experimento

Detecção de mutante equivalente é o problema clássico em aberto de teste de
mutação, e na prática se resolve com leitura humana de cada sobrevivente.

> Um mutante equivalente **não pode ser morto** — é essa a definição dele.
> Logo, todo mutante que a geração verificada mata é **provadamente não
> equivalente**.

Portanto a geração verificada é um **pré-filtro sonoro** para triagem de
equivalência: ela nunca descarta um mutante equivalente, porque matá-lo é
impossível. O humano só inspeciona o que sobrou.

**Isso é dedutivo. Não depende do modelo ser bom.** Um modelo ruim reduz pouco;
um bom reduz muito; nenhum dos dois pode produzir falso descarte.

### Métrica da camada 2

```
fator_de_reducao_de_triagem = |sobreviventes| / |indeterminados|
precisao_do_indeterminado   = |equivalente ou inalcançável| / |indeterminados|
```

O primeiro é o ganho garantido (esforço humano evitado, sem perda). O segundo
mede quão enriquecido ficou o resto, e sai da triagem manual.

### Protocolo de triagem manual — escrito antes de olhar qualquer mutante

Cada indeterminado recebe **exatamente um** rótulo, com justificativa escrita:

- **`inalcançável`** — a linha mutada não pode ser executada por nenhuma entrada.
  Prova: exibir a condição que a guarda e por que ela é insatisfazível.
  *Exemplo já encontrado no spike:* `slugify.py:129` está sob
  `if not isinstance(text, str)`, logo após `unidecode.unidecode(text)`, que
  sempre devolve `str`. Código morto.
- **`equivalente`** — a mutação produz comportamento idêntico para toda entrada.
  Prova: argumento sobre o domínio de entrada.
- **`difícil`** — matável em princípio; o agente não conseguiu. **Este é o rótulo
  padrão.** Na dúvida, `difícil` — nunca `equivalente`.

A regra do rótulo padrão existe porque o viés natural aqui é classificar como
equivalente o que eu não consegui matar, e isso infla a camada 2 exatamente como
o teto inflaria a camada 1.

### O que a camada 2 promete e o que não promete

**Promete:** reduzir o conjunto que um humano precisa ler, sem perda, por um
fator medido; e reportar os achados de código morto com evidência.

**Não promete:** classificar equivalência automaticamente. O rótulo final é
humano, e está declarado como humano.

---

## 9. Métricas secundárias

| métrica | por quê |
|---|---|
| testes gerados vs. testes que mataram algo | desperdício do modelo |
| testes que **violam G1 ou G3** | dano concreto que a guarda evita |
| mutantes mortos por teste | densidade, não volume |
| custo (US$) e tempo por módulo | FinOps é feature, não nota de rodapé |
| linhas de teste adicionadas | tamanho do diff que o humano revisa |

## 10. O que estes números NÃO dizem

- **Matar mutante não é ser bom teste.** A métrica mede detecção, não legibilidade
  nem intenção. O diff fica visível justamente porque isso é julgamento humano.
- **Domínio:** duas bibliotecas Python puras. Nada aqui sustenta claim sobre
  código com I/O, concorrência ou framework.
- **Prior art:** geração de teste guiada por mutação com LLM é área estabelecida —
  MuTAP, MUTGEN, PRIMG, ACH (Meta). A camada 1 é reimplementação honesta e
  citada. O que não encontrei publicado é a camada 2: tratar o resíduo como
  detector sonoro de equivalência. É lá que está a contribuição, e ela é
  declarada como tal, sem inflar a camada 1.
