# Decisões Abertas — precisam do Victor

## D1 — Acesso a LLM para S3–S6 🔴 BLOQUEANTE a partir de H+1,75

**Fato:** nenhuma chave no ambiente. `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`,
`ANTHROPIC_AUTH_TOKEN` e `LLM_API_KEY` estão todas *unset* no shell.
`~/Documents/dev/hackaton/.env` tem `LLM_API_KEY` declarada (provider `openai`,
modelo `gpt-4o-mini`), mas o classificador de segurança bloqueou a leitura do
arquivo — não sei se está preenchida nem se ainda tem saldo.

**Por que bloqueia:** S3 (baseline) em diante são chamadas reais de modelo. Sem
chave não existe número medido — e "Measured Improvement" (15 pts) + baseline
são itens **não cortáveis** na ordem de sacrifício do plano.

**O que NÃO bloqueia:** S0, S1 e S2 são 100% locais. O harness de avaliação roda
com predição fabricada à mão. Sigo até o fim do S2 sem resposta.

## D2 — Repositório de submissão 🟡

Repo git novo criado em `~/Documents/dev/deadzone` (história limpa desde 29/08,
como o brief exige). Falta destino remoto — o Apura vive em
`github.com/lchampz/apura`. Assumo repo novo `lchampz/deadzone` salvo objeção.
Não crio nem publico nada sem o "ok".

## D3 — Orçamento de tokens 🟡

O plano prevê record/replay desde S3: cada chamada gravada em `recordings/`,
reavaliação em `--replay` a custo zero. Isso limita o gasto ao número de
execuções *novas*: baseline + 3 iterações × ~8 funções. Estimativa < US$ 5 com
modelo forte. Só vira decisão se D1 vier com teto apertado.
