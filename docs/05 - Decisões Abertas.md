# Decisões Abertas — precisam do Victor

Estado em 2026-08-29 18:00. Tudo que **não** depende de decisão já está feito e
commitado. As três abaixo são as únicas coisas que me travam.

---

## D1 — Acesso a modelo ✅ RESOLVIDA (29/08)

**Decisão do Victor:** Anthropic, `claude-opus-5`, mesmo modelo no baseline e na
solução. Orçamento de US$ 10 em crédito de API.

**Caminho até destravar, registrado porque custou quatro tentativas:**

1. `export` em janela fish não alcança minhas ferramentas — elas rodam num zsh
   separado, criado de um snapshot do profile no início da sessão. Processos
   irmãos, não pai/filho.
2. Resolvido com `~/.anthropic_key` (modo 600) + `env ANTHROPIC_API_KEY="$(cat ...)"`
   no comando: o valor vai do arquivo direto para o processo filho.
3. Quatro `400 credit balance is too low` seguidos. `scripts/check_credentials.py`
   separou as hipóteses com endpoints gratuitos: `models` → 200 (chave válida,
   org com API provisionada), `count_tokens` → 400 (não consome inferência; só o
   portão de faturamento o bloqueia). Diagnóstico: crédito, não credencial.
4. Após recarga, os três degraus em 200.

**Custo medido antes de gastar** (via `count_tokens`, gratuito):

| | |
|---|---|
| chamadas | 15 (12 novas — S5 reusa as gravações do S4) |
| tokens de entrada | 194.996 |
| custo estimado | US$ 1,72 (saída 2k/chamada) a US$ 3,97 (saída 8k) |

**Achado de graça:** S5 usa o mesmo prompt do S4 — o gate de evidência é código,
não prompt — então bate nas mesmas chaves de cache. Custa zero **e** mede o
efeito do gate sobre saída idêntica do modelo. O delta do S5 é 100% atribuível
ao gate, sem re-amostragem no meio.

**Prioridade de economia declarada pelo Victor:** crédito de API (US$ 10) >
assinatura Claude > Cursor.

---|---|
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

**Decisão tomada (29/08):** Anthropic, `claude-opus-4-5`, mesmo modelo no
baseline e na solução.

**Ainda travado — a chave não chegou até mim.** Meu shell é reinicializado a
cada comando a partir do seu profile, então um `export` avulso na sua janela de
terminal não me alcança. Precisa ser um destes:

1. adicionar ao seu profile do fish:
   `set -Ux ANTHROPIC_API_KEY sk-ant-...`
2. ou em `~/.claude/settings.json`, bloco `env`:
   `{"env": {"ANTHROPIC_API_KEY": "sk-ant-..."}}`

Feito isso, é só me dizer "chave no ambiente". A partir daí S3→S6 nos dois
conjuntos são ~14 chamadas, < US$ 2, gravadas em `recordings/` e replicáveis de
graça para sempre.

---

## D2 — Repositório remoto ✅ RESOLVIDA (29/08, decisão do Victor)

Repo público criado e publicado: **https://github.com/lchampz/deadzone**

Verificado do lado de fora, como o juiz faria:

```
git clone https://github.com/lchampz/deadzone.git && cd deadzone
docker build -t deadzone . && docker run --rm --network none deadzone
34 passed in 0.14s
SANIDADE: OK — harness discrimina   (dev)
SANIDADE: OK — harness discrimina   (holdout)
```

Clone público, rede desligada, tabela sai. Reproducibility (15 pts) fechado
exceto pelas linhas de S3–S6.

---

## D3 — Ordem de sacrifício, se D1 demorar 🟡

O plano manda cortar de cima para baixo: 3ª iteração (S6) → sinal de
transferência → 2ª iteração (S5) → métricas secundárias.

**Nota minha:** o "sinal de transferência" já está pronto e custa zero — o
HOLDOUT (`__main__.py`, 288 mutantes) foi gerado no S1 e nunca lido. Ele saiu de
graça da mesma sessão. Sugiro tirá-lo da lista de sacrifício.

Se D1 destravar até **30/08 12:00**, dá para os quatro estágios nos dois
conjuntos com folga. Depois disso, corto S6 primeiro.
