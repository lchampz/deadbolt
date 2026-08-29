# Trajetória — s5 · conjunto holdout

Modelo `claude-opus-5` · provider `anthropic` · modo `live`
Custo US$ 0.1424 · 13338 tokens de entrada · 3029 de saída · 36.92s de parede

## Resultado, contra o ground truth congelado

| precisão | recall | F1 | near-miss | ruído | mut-recall | evidência |
|---:|---:|---:|---:|---:|---:|---:|
| 0.818 | 0.300 | 0.439 | 0.091 | 0.091 | 0.323 | 1.000 |

Piso trivial deste conjunto e teto do oráculo em `eval/report.py`.

## Ações — uma chamada por unidade

_Nenhuma gravação casada com este estágio em `recordings/`._

## Feedback — o que o gate de evidência descartou

2 predições descartadas por âncora inválida:

- `slugify/__main__.py` [85, 88] — citação `if argv is None:
        argv = sys.argv` não aparece no intervalo
- `slugify/__main__.py` [91, 94] — citação `except KeyboardInterrupt:
        sys.exit(-1)` não aparece no intervalo

## Predições que sobreviveram

- `slugify/__main__.py:[35, 36]` · **dead_config** · conf 0.85 — No test passes --regex-pattern and slugify_params never forwards it, so renaming, removing or changing this option is invisible.
- `slugify/__main__.py:[41, 42]` · **dead_config** · conf 0.8 — The CLI tests' DEFAULTS dict omits allow_unicode and assertParamsMatch only compares expected keys, so flipping this default or flag action is never observed.
- `slugify/__main__.py:[81, 81]` · **output_shape** · conf 0.7 — assertParamsMatch reduces the produced dict to the expected keys only, so this entry's value (or its absence) is never inspected.
- `slugify/__main__.py:[62, 63]` · **unasserted_branch** · conf 0.65 — test_defaults runs with no input so this branch executes, but 'text' is absent from the asserted DEFAULTS keys, so setting '' vs anything else is indistinguishable.
- `slugify/__main__.py:[54, 54]` · **boundary_condition** · conf 0.6 — Only replacements containing exactly one '->' are tested, so the maxsplit limit of 1 could be dropped or changed without any failure.
- `slugify/__main__.py:[11, 13]` · **dead_config** · conf 0.5 — Parser description and argument-group text are never rendered or asserted by any test, so their values are interchangeable.
