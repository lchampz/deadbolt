# Herança do Apura — o que existia antes de 28/08

Exigência explícita do brief: separar o que preexistia do que foi construído no hackathon.

## Preexistia (declarar)

| Ativo | Onde | Papel no Deadzone |
|---|---|---|
| Harness squad (papéis, board, RFC) | `~/Documents/dev/squad` | Processo, não código do produto |
| Vault Obsidian Hackaton | `obsidian/Hackaton` | Briefing/rubric herdados |
| Repo Apura | `github.com/lchampz/apura` (`80e6e23`) | **Arquivado.** Nenhum código reaproveitado |
| Disciplina de eval (holdout, contaminação declarada) | `07 - Hot Takes` do Apura | **Método herdado** — é o que sobrevive |

## Construído no Deadzone (29–31/08)

Tudo em `~/Documents/dev/deadzone`, repo git novo, história limpa a partir de 29/08.

## O que o Apura ensinou e o Deadzone aplica

1. **Ground truth precisa ser independente do sistema que ele julga.** O gabarito
   do Apura foi moldado pelo próprio pipeline → F1 0.987 era ilusão. No Deadzone o
   ground truth é gerado por `mutmut`, uma ferramenta externa, **antes** de existir
   solução, e é congelado.
2. **Se um ajuste melhora o holdout, isso não é vitória — é sinal de contaminação.**
3. **Modelo maior não resolve ausência de critério.** Baseline em `claude-opus-5`
   deu F1 0.447 no Apura. O ganho tem que vir de arquitetura.
4. **Quatro vieses empilhados só apareceram um depois do outro.** Corpus homogêneo,
   tuning vazado, gabarito enviesado, leitor acoplado a um vendor.
