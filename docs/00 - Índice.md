# Deadzone — Second Brain

> Preditor de ponto cego de teste. Submissão micro1 Frontier Engineering Challenge 2026.
> **Prazo: 31/08/2026 18:00 UTC.** Repo da solução: `~/Documents/dev/deadzone`.
> Regra do vault: **toda decisão, falha e número entra aqui na hora em que acontece.**

## Mapa

- [[01 - Briefing e Rubric]] — o que o juiz pontua (herdado do Apura, ainda vale)
- [[02 - Herança do Apura]] — o que existia antes de 28/08 (exigência do brief)
- [[03 - Cartões de Hipótese]] — pré-registro S0–S9, **escrito antes de rodar**
- [[04 - Diário de Bordo]] — log cronológico com output cru (R2)
- [[05 - Decisões Abertas]] — o que depende do Victor
- [[06 - Hot Takes e Falhas]] — modo de falha observado → lição
- [[07 - Changelog de Melhoria]] — uma entrada por iteração, com evidência

## O projeto em uma frase

**Deadzone** — agente que lê um módulo Python e sua suíte de testes e prevê
**onde a suíte é cega**: as linhas cuja mutação passa despercebida. O ground
truth não é opinião — é o relatório de mutação do `mutmut`, gerado antes de
existir qualquer solução.

## Por que isso e não o Apura

O Apura foi arquivado em 29/08 00:20 (`80e6e23`) porque sua própria medição
honesta refutou a tese: pipeline determinístico com verificação adversarial
(F1 0.227) perdeu para prompt único (F1 0.382) num ground truth independente.
**O pivô carrega o método, não o código.** Ver [[02 - Herança do Apura]].
