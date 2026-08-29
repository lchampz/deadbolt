# Trajetória — s5 · conjunto dev

Modelo `claude-opus-5` · provider `anthropic` · modo `live`
Custo US$ 0.4047 · 27237 tokens de entrada · 10740 de saída · 133.122s de parede

## Resultado, contra o ground truth congelado

| precisão | recall | F1 | near-miss | ruído | mut-recall | evidência |
|---:|---:|---:|---:|---:|---:|---:|
| 0.450 | 0.529 | 0.486 | 0.300 | 0.250 | 0.717 | 1.000 |

Piso trivial deste conjunto e teto do oráculo em `eval/report.py`.

## Ações — uma chamada por unidade

_Nenhuma gravação casada com este estágio em `recordings/`._

## Feedback — o que o gate de evidência descartou

2 predições descartadas por âncora inválida:

- `slugify/slugify.py` [139, 140] — citação `except Exception:
            pass` não aparece no intervalo
- `slugify/slugify.py` [186, 188] — citação `# finalize user-specific replacements` não aparece no intervalo

## Predições que sobreviveram

- `slugify/slugify.py:[114, 115]` · **error_path** · conf 0.9 — Every test passes a str, so the bytes-decoding fallback never runs and could be deleted or altered undetected.
- `slugify/slugify.py:[128, 129]` · **error_path** · conf 0.9 — After normalization/unidecode the value is always str in the tests, so this second decoding guard is never triggered.
- `slugify/slugify.py:[146, 147]` · **error_path** · conf 0.85 — Only valid hexadecimal entities are tested, so the exception fallback for invalid/overflowing code points is never reached.
- `slugify/slugify.py:[49, 50]` · **boundary_condition** · conf 0.7 — The only case where len(string) equals max_length (max_length=19 with a 19-char slug) yields the same output whether '<' or '<=' is used, so the boundary is untested.
- `slugify/slugify.py:[55, 56]` · **error_path** · conf 0.75 — Every word_boundary test uses multi-word text containing the separator, so this single-word fallback return is never executed.
- `slugify/slugify.py:[62, 63]` · **boundary_condition** · conf 0.65 — Changing '<' to '<=' produces identical output in all word_boundary tests because the trailing separator is stripped at the end, so the strict comparison is never distinguished from the inclusive one.
- `slugify/slugify.py:[70, 71]` · **error_path** · conf 0.8 — No test uses a max_length shorter than the first word, so the empty-truncation fallback slice is never taken.
- `slugify/slugify.py:[191, 192]` · **boundary_condition** · conf 0.6 — max_length is only 0 or clearly positive in tests, and with 0 smart_truncate returns the same string anyway, so '>0' vs '>=0' or a negative value is indistinguishable.
- `slugify/slugify.py:[31, 31]` · **default_argument** · conf 0.55 — smart_truncate is only called with its default separator on a path that returns before the separator matters, and slugify always passes '-', so most changes to this default are invisible.
- `slugify/special.py:[10, 10]` · **unasserted_branch** · conf 0.6 — The second clause `char != upper_dict[0]` only ever evaluates False for entries like ('Ξ','X') and ('ϒ','Y') whose uppercase form already equals themselves and is therefore already caught by the first clause, so deleting it leaves PRE_TRANSLATIONS byte-identical and the only assertion (test_pre_translation) still passes.
- `slugify/special.py:[7, 8]` · **boundary_condition** · conf 0.35 — add_uppercase_char is only ever invoked at import time on the three non-empty hard-coded tables, so the empty-list / single-item edge of the loop is never exercised and a change to its handling would go unnoticed.
