# Trajetória — baseline · conjunto holdout

Modelo `claude-opus-5` · provider `anthropic` · modo `live`
Custo US$ 0.0940 · 13023 tokens de entrada · 1154 de saída · 13.716s de parede

## Resultado, contra o ground truth congelado

| precisão | recall | F1 | near-miss | ruído | mut-recall | evidência |
|---:|---:|---:|---:|---:|---:|---:|
| 0.650 | 0.361 | 0.464 | 0.050 | 0.300 | 0.321 | 1.000 |

Piso trivial deste conjunto e teto do oráculo em `eval/report.py`.

## Ações — uma chamada por unidade

### 1. `slugify/__main__.py`

gravação `65bf281b70a059dd2e43` · 13023→1154 tokens · US$ 0.0940 · 13.716s · 2026-08-29T18:38:26Z

<details><summary>instrução (prompt de usuário)</summary>

```
## Module under analysis: slugify/__main__.py

```python
   1 | from __future__ import annotations
   2 | 
   3 | import argparse
   4 | import sys
   5 | from typing import Any
   6 | 
   7 | from .slugify import slugify, DEFAULT_SEPARATOR
   8 | 
   9 | 
  10 | def parse_args(argv: list[str]) -> argparse.Namespace:
  11 |     parser = argparse.ArgumentParser(description="Slug string")
  12 | 
  13 |     input_group = parser.add_argument_group(description="Input")
  14 |     input_group.add_argument("input_string", nargs='*',
  15 |                              help='Text to slugify')
  16 |     input_group.add_argument("--stdin", action='store_true',
  17 |                              help="Take the text from STDIN")
  18 | 
  19 |     parser.add_argument("--no-entities", action='store_false', dest='entities', default=True,
  20 |                         help="Do not convert HTML entities to unicode")
  21 |     parser.add_argument("--no-decimal", action='store_false', dest='decimal', default=True,
  22 |                         help="Do not convert HTML decimal to unicode")
  23 |     parser.add_argument("--no-hexadecimal", action='store_false', dest='hexadecimal', default=True,
  24 |                         help="Do not convert HTML hexadecimal to unicode")
  25 |     parser.add_argument("--max-length", type=int, default=0,
  26 |                         help="Output stri
… [27520 chars omitidos — íntegra em recordings/]
```
</details>

<details><summary>resposta crua do modelo</summary>

```
[
  {
    "file": "slugify/__main__.py",
    "line_range": [85, 94],
    "blind_spot_type": "untested entry point",
    "evidence_quote": "def main(argv: list[str] | None = None) -> None:",
    "confidence": 0.95,
    "rationale": "The test suite only imports parse_args and slugify_params; main() is never invoked, so its argv defaulting, printing and KeyboardInterrupt handling are unexercised."
  },
  {
    "file": "slugify/__main__.py",
    "line_range": [87, 88],
    "blind_spot_type": "default argument branch",
    "evidence_quote": "        argv = sys.argv",
    "confidence": 0.92,
    "rationale": "No test calls main() without argv, so the sys.argv fallback is never executed."
  },
  {
    "file": "slugify/__main__.py",
    "line_range": [91, 94],
    "blind_spot_type": "exception handling",
    "evidence_quote": "    except KeyboardInterrupt:",
    "confidence": 0.95,
    "rationale": "No test raises KeyboardInterrupt during slugify, so the sys.exit(-1) path is unverified."
  },
  {
    "file": "slugify/__main__.py",
    "line_range": [97, 98],
    "blind_spot_type": "module __main__ guard",
    "evidence_quote": "if __name__ == '__main__':",
    "confidence": 0.9,
    "rationale": "The module is imported, never executed as a script, so this guard body never runs in tests."
  },
  {
    "file": "slugify/__main__.py",
    "line_range": [62, 63],
    "blind_spot_type": "red
… [1449 chars omitidos — íntegra em recordings/]
```
</details>

### 2. `slugify/slugify.py`

gravação `04d4611b25cac97c057f` · 14565→1268 tokens · US$ 0.1045 · 15.987s · 2026-08-29T18:37:25Z

<details><summary>instrução (prompt de usuário)</summary>

```
## Module under analysis: slugify/slugify.py

```python
   1 | from __future__ import annotations
   2 | 
   3 | import re
   4 | import unicodedata
   5 | from collections.abc import Iterable
   6 | from html.entities import name2codepoint
   7 | 
   8 | try:
   9 |     import unidecode
  10 | except ImportError:
  11 |     import text_unidecode as unidecode  # type: ignore[import-untyped, no-redef]
  12 | 
  13 | __all__ = ['slugify', 'smart_truncate']
  14 | 
  15 | 
  16 | CHAR_ENTITY_PATTERN = re.compile(r'&(%s);' % '|'.join(name2codepoint))
  17 | DECIMAL_PATTERN = re.compile(r'&#(\d+);')
  18 | HEX_PATTERN = re.compile(r'&#x([\da-fA-F]+);')
  19 | QUOTE_PATTERN = re.compile(r'[\']+')
  20 | DISALLOWED_CHARS_PATTERN = re.compile(r'[^-a-zA-Z0-9]+')
  21 | DISALLOWED_UNICODE_CHARS_PATTERN = re.compile(r'[\W_]+')
  22 | DUPLICATE_DASH_PATTERN = re.compile(r'-{2,}')
  23 | NUMBERS_PATTERN = re.compile(r'(?<=\d),(?=\d)')
  24 | DEFAULT_SEPARATOR = '-'
  25 | 
  26 | 
  27 | def smart_truncate(
  28 |     string: str,
  29 |     max_length: int = 0,
  30 |     word_boundary: bool = False,
  31 |     separator: str = " ",
  32 |     save_order: bool = False,
  33 | ) -> str:
  34 |     """
  35 |     Truncate a string.
  36 |     :param string (str): string for modification
  37 |     :param max_length (int): output string length
  38 |     :param word_boundary (bool):
  39 |   
… [30455 chars omitidos — íntegra em recordings/]
```
</details>

<details><summary>resposta crua do modelo</summary>

```
[
  {
    "file": "slugify/slugify.py",
    "line_range": [114, 115],
    "blind_spot_type": "unreachable defensive branch",
    "evidence_quote": "        text = str(text, 'utf-8', 'ignore')",
    "confidence": 0.9,
    "rationale": "All tests pass str input, so the bytes-decoding branch is never executed and could be changed or deleted undetected."
  },
  {
    "file": "slugify/slugify.py",
    "line_range": [128, 129],
    "blind_spot_type": "unreachable defensive branch",
    "evidence_quote": "    if not isinstance(text, str):",
    "confidence": 0.9,
    "rationale": "After normalization/unidecode the value is always str, so this second re-decode branch is never taken by any test."
  },
  {
    "file": "slugify/slugify.py",
    "line_range": [136, 140],
    "blind_spot_type": "untested exception handler",
    "evidence_quote": "        except Exception:\n            pass",
    "confidence": 0.85,
    "rationale": "No test feeds an out-of-range decimal entity that raises inside the sub, so the try/except swallow path is never exercised."
  },
  {
    "file": "slugify/slugify.py",
    "line_range": [143, 147],
    "blind_spot_type": "untested exception handler",
    "evidence_quote": "            text = HEX_PATTERN.sub(lambda m: chr(int(m.group(1), 16)), text)",
    "confidence": 0.85,
    "rationale": "Only valid hex entities are tested, so the except branch that ignores c
… [1857 chars omitidos — íntegra em recordings/]
```
</details>

### 3. `slugify/special.py`

gravação `16a9484daa327da803d7` · 12042→3697 tokens · US$ 0.1526 · 46.852s · 2026-08-29T18:38:12Z

<details><summary>instrução (prompt de usuário)</summary>

```
## Module under analysis: slugify/special.py

```python
   1 | from __future__ import annotations
   2 | 
   3 | 
   4 | def add_uppercase_char(char_list: list[tuple[str, str]]) -> list[tuple[str, str]]:
   5 |     """ Given a replacement char list, this adds uppercase chars to the list """
   6 | 
   7 |     for item in char_list:
   8 |         char, xlate = item
   9 |         upper_dict = char.upper(), xlate.capitalize()
  10 |         if upper_dict not in char_list and char != upper_dict[0]:
  11 |             char_list.insert(0, upper_dict)
  12 |     return char_list
  13 | 
  14 | 
  15 | # Language specific pre translations
  16 | # Source awesome-slugify
  17 | 
  18 | _CYRILLIC = [      # package defaults:
  19 |     (u'ё', u'e'),    # io / yo
  20 |     (u'я', u'ya'),   # ia
  21 |     (u'х', u'h'),    # kh
  22 |     (u'у', u'y'),    # u
  23 |     (u'щ', u'sch'),  # sch
  24 |     (u'ю', u'u'),    # iu / yu
  25 | ]
  26 | CYRILLIC = add_uppercase_char(_CYRILLIC)
  27 | 
  28 | _GERMAN = [        # package defaults:
  29 |     (u'ä', u'ae'),   # a
  30 |     (u'ö', u'oe'),   # o
  31 |     (u'ü', u'ue'),   # u
  32 | ]
  33 | GERMAN = add_uppercase_char(_GERMAN)
  34 | 
  35 | _GREEK = [         # package defaults:
  36 |     (u'χ', u'ch'),   # kh
  37 |     (u'Ξ', u'X'),    # Ks
  38 |     (u'ϒ', u'Y'),    # U
  39 |     (u'υ', u'y'),    # u
  40 |     (u'ύ', u'y
… [24420 chars omitidos — íntegra em recordings/]
```
</details>

<details><summary>resposta crua do modelo</summary>

```
[
  {
    "file": "slugify/special.py",
    "line_range": [10, 10],
    "blind_spot_type": "redundant/unreachable guard clause",
    "evidence_quote": "if upper_dict not in char_list and char != upper_dict[0]:",
    "confidence": 0.6,
    "rationale": "For every entry in the three built-in lists the already-uppercase cases are also blocked by the first `not in char_list` test, so dropping or inverting the `char != upper_dict[0]` clause leaves PRE_TRANSLATIONS byte-identical and the sole equality assertion still passes."
  },
  {
    "file": "slugify/special.py",
    "line_range": [11, 12],
    "blind_spot_type": "unobserved in-place mutation / aliasing",
    "evidence_quote": "        return char_list",
    "confidence": 0.5,
    "rationale": "The test only compares the concatenated PRE_TRANSLATIONS value, so changing the function to copy the input instead of mutating and returning the same list object (or vice versa) is invisible."
  },
  {
    "file": "slugify/special.py",
    "line_range": [4, 5],
    "blind_spot_type": "untested API surface / annotations",
    "evidence_quote": "def add_uppercase_char(char_list: list[tuple[str, str]]) -> list[tuple[str, str]]:",
    "confidence": 0.45,
    "rationale": "add_uppercase_char is never imported or called directly by the tests, only implicitly at import time with three fixed inputs, so its signature, annotations and behaviour on 
… [806 chars omitidos — íntegra em recordings/]
```
</details>

### 4. `toolz/functoolz.py`

gravação `3bef0eaece9c99eb18d3` · 24908→2138 tokens · US$ 0.1780 · 24.478s · 2026-08-29T19:38:22Z

<details><summary>instrução (prompt de usuário)</summary>

```
## Module under analysis: toolz/functoolz.py

```python
   1 | from functools import reduce, partial
   2 | import inspect
   3 | import sys
   4 | from operator import attrgetter, not_
   5 | from importlib import import_module
   6 | from types import MethodType
   7 | 
   8 | from .utils import no_default
   9 | 
  10 | PYPY = hasattr(sys, 'pypy_version_info') and sys.version_info[0] > 2
  11 | 
  12 | 
  13 | __all__ = ('identity', 'apply', 'thread_first', 'thread_last', 'memoize',
  14 |            'compose', 'compose_left', 'pipe', 'complement', 'juxt', 'do',
  15 |            'curry', 'flip', 'excepts')
  16 | 
  17 | PYPY = hasattr(sys, 'pypy_version_info')
  18 | 
  19 | 
  20 | def identity(x):
  21 |     """ Identity function. Return x
  22 | 
  23 |     >>> identity(3)
  24 |     3
  25 |     """
  26 |     return x
  27 | 
  28 | 
  29 | def apply(*func_and_args, **kwargs):
  30 |     """ Applies a function and returns the results
  31 | 
  32 |     >>> def double(x): return 2*x
  33 |     >>> def inc(x):    return x + 1
  34 |     >>> apply(double, 5)
  35 |     10
  36 | 
  37 |     >>> tuple(map(apply, [double, inc, double], [10, 500, 8000]))
  38 |     (20, 501, 16000)
  39 |     """
  40 |     if not func_and_args:
  41 |         raise TypeError('func argument is required')
  42 |     func, args = func_and_args[0], func_and_args[1:]
  43 |     return func(*arg
… [56220 chars omitidos — íntegra em recordings/]
```
</details>

<details><summary>resposta crua do modelo</summary>

```
[
  {
    "file": "toolz/functoolz.py",
    "line_range": [347, 375],
    "blind_spot_type": "unpickled-serialization-path",
    "evidence_quote": "    def __reduce__(self):",
    "confidence": 0.85,
    "rationale": "No test in this file pickles or copies a curry object, so the module/qualname lookup and state tuple construction are never exercised."
  },
  {
    "file": "toolz/functoolz.py",
    "line_range": [378, 389],
    "blind_spot_type": "unpickled-serialization-path",
    "evidence_quote": "def _restore_curry(cls, func, args, kwargs, userdict, is_decorated):",
    "confidence": 0.85,
    "rationale": "This restore helper is only invoked during unpickling, which the test suite never performs."
  },
  {
    "file": "toolz/functoolz.py",
    "line_range": [163, 165],
    "blind_spot_type": "unpickled-serialization-path",
    "evidence_quote": "        state = (self.fget, self.fset, self.fdel, self.__doc__, self.classval)",
    "confidence": 0.85,
    "rationale": "InstanceProperty.__reduce__ is only used when pickling descriptors, never triggered by any test."
  },
  {
    "file": "toolz/functoolz.py",
    "line_range": [242, 270],
    "blind_spot_type": "introspection-detail-untested",
    "evidence_quote": "        params = list(sig.parameters.values())",
    "confidence": 0.7,
    "rationale": "No test inspects inspect.signature() of a curry object, so the parameter re
… [3877 chars omitidos — íntegra em recordings/]
```
</details>

## Feedback — o que o gate de evidência descartou

_Gate não aplicado neste estágio._

## Predições que sobreviveram

- `slugify/__main__.py:[85, 94]` · **untested entry point** · conf 0.95 — The test suite only imports parse_args and slugify_params; main() is never invoked, so its argv defaulting, printing and KeyboardInterrupt handling are unexercised.
- `slugify/__main__.py:[87, 88]` · **default argument branch** · conf 0.92 — No test calls main() without argv, so the sys.argv fallback is never executed.
- `slugify/__main__.py:[91, 94]` · **exception handling** · conf 0.95 — No test raises KeyboardInterrupt during slugify, so the sys.exit(-1) path is unverified.
- `slugify/__main__.py:[97, 98]` · **module __main__ guard** · conf 0.9 — The module is imported, never executed as a script, so this guard body never runs in tests.
- `slugify/__main__.py:[62, 63]` · **redundant/unreached default** · conf 0.6 — input_string already defaults to an empty list turned into '' or nothing, so this fallback assignment can be altered without any assertion detecting it beyond the default test that also passes with the list default.
- `slugify/__main__.py:[41, 42]` · **untested CLI option** · conf 0.75 — allow_unicode is not in the DEFAULTS dict compared by assertParamsMatch and no CLI test passes --allow-unicode, so changes to it go unnoticed.
- `slugify/__main__.py:[35, 36]` · **unused/unpropagated option** · conf 0.85 — regex_pattern is parsed but never included in slugify_params and no test asserts on it, so removing or renaming it is invisible.
- `slugify/__main__.py:[31, 32]` · **help text / default string** · conf 0.55 — Help strings are never asserted; only the parsed value is checked.
