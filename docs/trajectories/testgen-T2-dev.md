# Trajetória — geração de testes · T2 · dev

Backend `anthropic` · modelo `claude-opus-5` · effort `high` · modo `replay`
Custo US$ 0.8622 · 3848 in / 33717 out · cache 0 lidos

## Resultado

| | mutantes | mortos | score |
|---|---:|---:|---:|
| antes | 216 | 170 | 0.7870 |

## Ações — uma chamada por lote de mutantes

_Nenhuma gravação casada._

## Feedback — o que as guardas rejeitaram

- G1: o teste falha no código ORIGINAL — a expectativa está errada

## Recusas do modelo — entrada da camada 2

- `` — Changing `if next_len < max_length` to `<=` only affects the iteration where next_len == max_length. Originally that word is appended without a separa
- `` — Python normalizes codec names case-insensitively (codecs.lookup('UTF-8') is codecs.lookup('utf-8')), so decoding with 'UTF-8' produces byte-for-byte i
- `` — Line 129 sits inside `if not isinstance(text, str)` at line 128, which is unreachable: by that point text has already been forced to str (line 115), p
- `` — Line 129 sits inside `if not isinstance(text, str)` right after the normalization block. At that point `text` is the result of `unicodedata.normalize(

## Testes que embarcaram: 32

```python
def test_smart_truncate_default_word_boundary_is_false():
    txt = 'one two three'
    r = smart_truncate(txt, max_length=9)
    assert r == 'one two t'

```

```python
def test_smart_truncate_default_separator_is_space():
    txt = 'one two three'
    r = smart_truncate(txt, max_length=9, word_boundary=True)
    assert r == 'one two'

```

```python
def test_smart_truncate_default_save_order_is_false():
    txt = 'one two three four'
    r = smart_truncate(txt, max_length=12, word_boundary=True)
    assert r == 'one two four'

```

```python
def test_smart_truncate_strips_given_separator_only():
    txt = '--abc--'
    r = smart_truncate(txt, separator='-')
    assert r == 'abc'

```

```python
def test_smart_truncate_length_equal_to_max_length():
    txt = 'a  b'
    r = smart_truncate(txt, max_length=4, word_boundary=True)
    assert r == 'a b'

```

```python
def test_smart_truncate_word_boundary_when_no_word_fits():
    txt = 'aaaa bbbb'
    r = smart_truncate(txt, max_length=3, word_boundary=True)
    assert r == 'aaa'

```

