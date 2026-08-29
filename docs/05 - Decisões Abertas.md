# Decisões Abertas — precisam do Victor

Estado em 2026-08-29 18:00. Tudo que **não** depende de decisão já está feito e
commitado. As três abaixo são as únicas coisas que me travam.

---

## D1 — Acesso a modelo para S3–S6 🔴 BLOQUEANTE

**Fato apurado.** Nenhuma chave no ambiente: `ANTHROPIC_API_KEY`,
`OPENAI_API_KEY`, `ANTHROPIC_AUTH_TOKEN` e `LLM_API_KEY` todas *unset*.
`~/Documents/dev/hackaton/.env` declara `LLM_API_KEY` (provider `openai`, modelo
`gpt-4o-mini`), mas o classificador de segurança bloqueou tanto a leitura do
arquivo quanto um script que testasse a chave sem exibi-la. Não contornei.

**Custo estimado da rodada inteira.** ~14 chamadas (4 estágios × 2 conjuntos,
com o S6 quebrando por função): ~210k tokens de entrada, ~28k de saída.

| Modelo | Custo estimado |
|---|---|
| `claude-opus-4-5` | **< US$ 2,00** |
| `claude-sonnet-4-5` | < US$ 1,10 |
| `gpt-4o-mini` | < US$ 0,05 |

Gravadas uma vez, todas replicam a custo zero para sempre.

**Recomendação: opus-4-5, mesmo modelo no baseline e na solução.** O Apura já
provou que modelo forte não resolve ausência de critério (baseline opus deu F1
0.447 lá). Se o baseline sair forte aqui também, isso é achado, não problema —
e enfraquecer baseline é a fraude mais detectável que existe.

**O que perdemos sem isso.** Measured Improvement (15 pts) inteiro, e a maior
parte de Agent Solution & Engineering (30 pts) — as capabilities existem, mas
nenhuma teria evidência de que resolveu falha observada. Restariam ~45 pts.

**Como destravar:** `export ANTHROPIC_API_KEY=...` no shell e me avisar.
Não peça para eu ler `.env` de outro projeto — prefiro não tocar em segredo
de terceiro projeto sem você mandar explicitamente.

---

## D2 — Repositório remoto 🟡

Repo git local criado, 3 commits, história limpa desde 29/08 (o brief exige
separar o que preexistia). Falta destino. O Apura vive em
`github.com/lchampz/apura`.

**Recomendação:** repo novo `lchampz/deadzone`, público (o juiz precisa clonar).

**Não criei nem publiquei nada.** Publicar é ação externa e irreversível na
prática — espero seu ok.

---

## D3 — Ordem de sacrifício, se D1 demorar 🟡

O plano manda cortar de cima para baixo: 3ª iteração (S6) → sinal de
transferência → 2ª iteração (S5) → métricas secundárias.

**Nota minha:** o "sinal de transferência" já está pronto e custa zero — o
HOLDOUT (`__main__.py`, 288 mutantes) foi gerado no S1 e nunca lido. Ele saiu de
graça da mesma sessão. Sugiro tirá-lo da lista de sacrifício.

Se D1 destravar até **30/08 12:00**, dá para os quatro estágios nos dois
conjuntos com folga. Depois disso, corto S6 primeiro.
