# Briefing e Rubric

Fonte: PDF oficial "micro1 Agentic Workflows Hackathon". Herdado do vault Hackaton.

## As 4 perguntas que o juiz faz

1. Quem tem esse problema?
2. Qual gargalo torna isso digno de resolver?
3. O agente resolve bem?
4. Outra pessoa consegue reproduzir o resultado?

## Rubric (100 pts)

| Critério | Pts | Como o Deadzone pontua |
|---|---|---|
| Agent Solution & Engineering | 30 | Cada capability existe porque matou uma falha medida — [[07 - Changelog de Melhoria]] prova |
| End to End Quality | 20 | Relatório de ponto cego que um dev assinaria: arquivo, linhas, tipo, citação literal, confiança |
| Problem & User Value | 15 | Dev/mantenedor com suíte verde e falsa segurança; cobertura de linha ≠ cobertura de comportamento |
| Measured Improvement | 15 | Precisão/recall contra sobreviventes de mutação, baseline justo, mesmo corpus e modelo |
| Reproducibility | 15 | `docker build` + 1 comando → tabela final, **sem chave de API** (replay) |
| Hot Take / Insights | 5 | O modo de falha real + o experimento removido |

**Leitura fria:** 60/100 = engenharia com propósito + medição + reprodução.

## Entregáveis obrigatórios

1. Código completo + Improvement Changelog
2. Guia de reprodução (ambiente limpo, comandos exatos, versões, custo, runtime)
3. Vídeo ≤ 5 min
4. Trajetórias dos agentes (instrução → ações → feedback → resultado)

## Ground rules

- Dados públicos ou sintéticos → corpus é `python-slugify`, **MIT**, vendorizado e pinado.
- Toda claim ligada a evidência submetida.
- Explicitar o que existia antes vs. o que foi feito → [[02 - Herança do Apura]].
