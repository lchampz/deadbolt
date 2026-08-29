# Trajetória — s5 · conjunto transfer

Modelo `claude-opus-5` · provider `anthropic` · modo `live`
Custo US$ 0.3182 · 25223 tokens de entrada · 7683 de saída · 92.463s de parede

## Resultado, contra o ground truth congelado

| precisão | recall | F1 | near-miss | ruído | mut-recall | evidência |
|---:|---:|---:|---:|---:|---:|---:|
| 0.125 | 0.180 | 0.148 | 0.208 | 0.667 | 0.220 | 1.000 |

Piso trivial deste conjunto e teto do oráculo em `eval/report.py`.

## Ações — uma chamada por unidade

_Nenhuma gravação casada com este estágio em `recordings/`._

## Feedback — o que o gate de evidência descartou

_Nenhuma predição descartada._

## Predições que sobreviveram

- `toolz/functoolz.py:[10, 10]` · **dead_config** · conf 0.85 — This constant is unconditionally overwritten at line 17, so any change to its expression is invisible to every test.
- `toolz/functoolz.py:[847, 855]` · **dead_config** · conf 0.8 — The PyPy-only rebinding of _check_sigspec is never taken on the CPython test runs, so its contents can change freely.
- `toolz/functoolz.py:[201, 201]` · **output_shape** · conf 0.6 — Tests only assert that TypeError is raised via raises(), so the message text is unchecked and can be altered unnoticed.
- `toolz/functoolz.py:[204, 209]` · **error_path** · conf 0.55 — No test passes a partial-like object whose .args is not a tuple, so this guard's False outcome is never exercised.
- `toolz/functoolz.py:[224, 226]` · **error_path** · conf 0.5 — Every curried callable in the tests has __name__/__qualname__, so the getattr fallback values are never produced or asserted.
- `toolz/functoolz.py:[239, 240]` · **error_path** · conf 0.6 — No test calls inspect.signature on a curry object with invalid bound arguments, so this raise never fires.
- `toolz/functoolz.py:[254, 268]` · **unasserted_branch** · conf 0.6 — The test file never inspects a curry object's __signature__, so the VAR_KEYWORD / VAR_POSITIONAL / keyword-only branches are indistinguishable from each other.
- `toolz/functoolz.py:[315, 319]` · **unasserted_branch** · conf 0.4 — Each currying TypeError in the tests happens on a freshly created curry object, so the cached-sigspec branch is never distinguished from recomputation.
- `toolz/functoolz.py:[365, 368]` · **unasserted_branch** · conf 0.55 — This test module never pickles or calls __reduce__ on a curry, so the decorated-vs-not determination is never observed.
- `toolz/functoolz.py:[384, 386]` · **unasserted_branch** · conf 0.5 — _restore_curry is only reached through unpickling, which this test suite never performs, so neither side of the branch is checked.
- `toolz/functoolz.py:[436, 438]` · **error_path** · conf 0.75 — No memoized callable in the tests makes introspection raise TypeError, so this fallback assignment never executes.
- `toolz/functoolz.py:[459, 459]` · **output_shape** · conf 0.6 — test_memoize only asserts raises(TypeError, ...), so the wording of the message can change without detection.
- `toolz/functoolz.py:[464, 468]` · **output_shape** · conf 0.5 — No test asserts the memoized wrapper's __name__, so the copied name value could change (only __doc__ and __wrapped__ are checked).
- `toolz/functoolz.py:[667, 668]` · **boundary_condition** · conf 0.55 — Only the single-generator case is exercised; the single-callable and multi-function boundaries of this length/callable test are never tested in this module.
- `toolz/functoolz.py:[834, 843]` · **error_path** · conf 0.55 — No test drives _check_sigspec with a non-Signature, non-ValueError sigspec for a registered builtin, so this fallback pair is never returned.
- `toolz/functoolz.py:[946, 947]` · **error_path** · conf 0.7 — The tests never introspect a callable whose arity information is undeterminable, so this None-returning guard never runs.
