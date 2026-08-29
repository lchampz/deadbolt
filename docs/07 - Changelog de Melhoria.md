# Changelog de Melhoria — rascunho vivo

> O changelog **final**, em inglês para os juízes, é `CHANGELOG.md` no repo da
> solução. Aqui fica o que não cabe lá: o raciocínio por trás de cada decisão e
> as entradas ainda não fechadas.

## Fechadas (já em `CHANGELOG.md`)

| Estágio | Entrega | Número | Veredito |
|---|---|---|---|
| S0 | corpus escolhido | `82 passed in 0.04s` | confirmada |
| S1 | ground truth de mutação | 216 mutantes, 46 sobreviventes, **0.213** | confirmada |
| S2 | métrica e harness congelados | 4 controles × 2 conjuntos, todos passando | confirmada |
| S7 | reprodução em container sem chave e sem rede | 216/170/46 e 288/189/99 regerados | confirmada |

## Regra de escrita destas entradas

Cada entrada carrega três coisas, nesta ordem: a **hipótese escrita antes** da
mudança, o **número cru depois**, e a **decisão** — inclusive remoção. Iteração
que não move a métrica é removida do pipeline e registrada como removida. O
brief pede explicitamente experimentos descartados e o que ensinaram; uma
remoção honesta vale mais que três melhorias marginais infladas.

## O que ainda não pode ser escrito

S3 a S6 não têm entrada porque não têm número. Não vou escrever "espera-se que
a taxonomia aumente a precisão" num changelog — changelog registra o que
aconteceu, não o que se pretende. Enquanto [[05 - Decisões Abertas]] D1 estiver
aberta, estas quatro linhas ficam vazias, e `eval/report.py` imprime
`— não medido —` em vez de omitir a linha.

## Candidato a "experimento removido" do vídeo

Ainda indefinido — depende de qual das três iterações não mover a métrica. O
plano já nomeia o critério de remoção antes de medir: S4 morre se a precisão não
subir ≥ 3 pontos, S5 morre se o falso positivo não cair, S6 morre se o recall
não subir. Ver [[03 - Cartões de Hipótese]].
