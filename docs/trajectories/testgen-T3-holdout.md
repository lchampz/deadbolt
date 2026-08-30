# Trajetória — geração de testes · T3 · holdout

Backend `anthropic` · modelo `claude-opus-5` · effort `high` · modo `live`
Custo US$ 1.3104 · 12862 in / 49844 out · cache 183624 lidos

## Resultado

| | mutantes | mortos | score |
|---|---:|---:|---:|
| antes | 298 | 189 | 0.6342 |
| depois (**mutmut do zero**) | 298 | 289 | **0.9698** |

## Ações — uma chamada por lote de mutantes

### 1. `holdout#0`

gravação `308e778201158ea373c8` · 2600 tokens de saída · US$ 0.0688 · 2026-08-29T21:55:25Z

<details><summary>instrução</summary>

```
Mutations the suite does not catch. Write one test for each.

### `slugify.__main__.x_parse_args__mutmut_2` — slugify/__main__.py line 11
```diff
- parser = argparse.ArgumentParser(description="Slug string")
+ parser = argparse.ArgumentParser(description=None)
```

### `slugify.__main__.x_parse_args__mutmut_3` — slugify/__main__.py line 11
```diff
- parser = argparse.ArgumentParser(description="Slug string")
+ parser = argparse.ArgumentParser(description="XXSlug stringXX")
```

### `slugify.__main__.x_parse_args__mutmut_4` — slugify/__main__.py line 11
```diff
- parser = argparse.ArgumentParser(description="Slug string")
+ parser = argparse.ArgumentParser(description="slug string")
```

### `slugify.__main__.x_parse_args__mutmut_5` — slugify/__main__.py line 11
```diff
- parser = argparse.ArgumentParser(description="Slug string")
+ parser = argparse.ArgumentParser(description="SLUG STRIN
… [869 chars omitidos — íntegra em recordings/]
```
</details>

<details><summary>resposta crua</summary>

```
[{"mutant_id": "slugify.__main__.x_parse_args__mutmut_2", "test": "def test_help_shows_parser_description(capsys):\n    with pytest.raises(SystemExit) as err:\n        parse_args(['prog', '--help'])\n    assert err.value.code == 0\n    out = capsys.readouterr().out\n    lines = [line.strip() for line in out.splitlines()]\n    assert 'Slug string' in lines"}, {"mutant_id": "slugify.__main__.x_parse_args__mutmut_3", "test": "def test_help_parser_description_has_no_marker_characters(capsys):\n    with pytest.raises(SystemExit) as err:\n        parse_args(['prog', '--help'])\n    assert err.value.code == 0\n    out = capsys.readouterr().out\n    lines = [line.strip() for line in out.splitlines()]\n    assert 'Slug string' in lines\n    assert 'XXSlug stringXX' not in lines"}, {"mutant_id": "slugify.__main__.x_parse_args__mutmut_4", "test": "def test_help_parser_description_is_capitalized(cap
… [2281 chars omitidos — íntegra em recordings/]
```
</details>

### 2. `holdout#1`

gravação `f0902e388bf2c659e6d4` · 2610 tokens de saída · US$ 0.0680 · 2026-08-29T21:55:53Z

<details><summary>instrução</summary>

```
Mutations the suite does not catch. Write one test for each.

### `slugify.__main__.x_parse_args__mutmut_13` — slugify/__main__.py line 15
```diff
- help='Text to slugify')
+ help=None)
```

### `slugify.__main__.x_parse_args__mutmut_16` — slugify/__main__.py line 15
```diff
- help='Text to slugify')
+ )
```

### `slugify.__main__.x_parse_args__mutmut_20` — slugify/__main__.py line 15
```diff
- help='Text to slugify')
+ help='XXText to slugifyXX')
```

### `slugify.__main__.x_parse_args__mutmut_21` — slugify/__main__.py line 15
```diff
- help='Text to slugify')
+ help='text to slugify')
```

### `slugify.__main__.x_parse_args__mutmut_22` — slugify/__main__.py line 15
```diff
- help='Text to slugify')
+ help='TEXT TO SLUGIFY')
```

### `slugify.__main__.x_parse_args__mutmut_25` — slugify/__main__.py line 17
```diff
- help="Take the text from STDIN")
+ help=None)
```

### `slugify.__main__
… [270 chars omitidos — íntegra em recordings/]
```
</details>

<details><summary>resposta crua</summary>

```
[{"mutant_id": "slugify.__main__.x_parse_args__mutmut_13", "test": "def test_input_string_help_present_in_usage(capsys):\n    with pytest.raises(SystemExit) as err:\n        parse_args(['prog', '--help'])\n    assert err.value.code == 0\n    normalized = \" \".join(capsys.readouterr().out.split())\n    assert \"input_string Text to slugify\" in normalized"}, {"mutant_id": "slugify.__main__.x_parse_args__mutmut_16", "test": "def test_input_string_help_not_omitted(capsys):\n    with pytest.raises(SystemExit):\n        parse_args(['prog', '--help'])\n    normalized = \" \".join(capsys.readouterr().out.split())\n    assert \"input_string Text to slugify\" in normalized\n    assert \"input_string --stdin\" not in normalized"}, {"mutant_id": "slugify.__main__.x_parse_args__mutmut_20", "test": "def test_input_string_help_has_no_marker_prefix(capsys):\n    with pytest.raises(SystemExit):\n      
… [2036 chars omitidos — íntegra em recordings/]
```
</details>

### 3. `holdout#10`

gravação `4c67bd430414872a947e` · 3540 tokens de saída · US$ 0.0920 · 2026-08-29T22:02:14Z

<details><summary>instrução</summary>

```
Mutations the suite does not catch. Write one test for each.

### `slugify.__main__.x_parse_args__mutmut_208` — slugify/__main__.py line 41
```diff
- parser.add_argument("--allow-unicode", action='store_true', default=False,
+ parser.add_argument("--allow-unicode", action='store_true', default=None,
```

### `slugify.__main__.x_parse_args__mutmut_211` — slugify/__main__.py line 41
```diff
- parser.add_argument("--allow-unicode", action='store_true', default=False,
+ parser.add_argument("--allow-unicode", default=False,
```

### `slugify.__main__.x_parse_args__mutmut_212` — slugify/__main__.py line 41
```diff
- parser.add_argument("--allow-unicode", action='store_true', default=False,
+ parser.add_argument("--allow-unicode", action='store_true', help="Allow unicode characters")
```

### `slugify.__main__.x_parse_args__mutmut_218` — slugify/__main__.py line 41
```diff
- parser.add_argument
… [730 chars omitidos — íntegra em recordings/]
```
</details>

<details><summary>resposta crua</summary>

```
[{"mutant_id": "slugify.__main__.x_parse_args__mutmut_208", "test": "def test_allow_unicode_default_is_exactly_false():\n    params = slugify_params(parse_args([None]))\n    assert params['allow_unicode'] is False"}, {"mutant_id": "slugify.__main__.x_parse_args__mutmut_211", "test": "def test_allow_unicode_is_a_boolean_flag():\n    args = parse_args([None, '--allow-unicode', 'Cool Text'])\n    assert args.allow_unicode is True\n    assert args.input_string == 'Cool Text'"}, {"mutant_id": "slugify.__main__.x_parse_args__mutmut_212", "test": null, "targets": ["slugify.__main__.x_parse_args__mutmut_212"], "why": "argparse gives an action='store_true' argument an implicit default of False, so writing default=False explicitly or omitting it produces identical Namespace values for every possible argv; the help text is unchanged too, so no observable difference exists."}, {"mutant_id": "slugify
… [1691 chars omitidos — íntegra em recordings/]
```
</details>

### 4. `holdout#11`

gravação `db5a108787fc01a48c6e` · 2481 tokens de saída · US$ 0.0655 · 2026-08-29T22:02:40Z

<details><summary>instrução</summary>

```
Mutations the suite does not catch. Write one test for each.

### `slugify.__main__.x_parse_args__mutmut_221` — slugify/__main__.py line 42
```diff
- help="Allow unicode characters")
+ help="ALLOW UNICODE CHARACTERS")
```

### `slugify.__main__.x_parse_args__mutmut_227` — slugify/__main__.py line 47
```diff
- parser.error("Input strings and --stdin cannot work together")
+ parser.error("XXInput strings and --stdin cannot work togetherXX")
```

### `slugify.__main__.x_parse_args__mutmut_235` — slugify/__main__.py line 53
```diff
- parser.error("Replacements must be of the form: ORIGINAL{SEP}REPLACED".format(SEP=SEP))
+ parser.error("XXReplacements must be of the form: ORIGINAL{SEP}REPLACEDXX".format(SEP=SEP))
```

### `slugify.__main__.x_parse_args__mutmut_241` — slugify/__main__.py line 54
```diff
- return repl.split(SEP, 1)
+ return repl.split(SEP, )
```

### `slugify.__main__.x_parse_a
… [550 chars omitidos — íntegra em recordings/]
```
</details>

<details><summary>resposta crua</summary>

```
[{"mutant_id": "slugify.__main__.x_parse_args__mutmut_221", "test": "def test_allow_unicode_help_text(capsys):\n    with pytest.raises(SystemExit) as err:\n        parse_args(['prog', '--help'])\n    assert err.value.code == 0\n    out = ' '.join(capsys.readouterr().out.split())\n    assert '--allow-unicode' in out\n    assert 'Allow unicode characters' in out\n    assert 'ALLOW UNICODE CHARACTERS' not in out\n"}, {"mutant_id": "slugify.__main__.x_parse_args__mutmut_227", "test": "def test_two_text_sources_error_message(capsys):\n    with pytest.raises(SystemExit) as err:\n        parse_args(['prog', '--stdin', 'Text'])\n    assert err.value.code == 2\n    stderr = ' '.join(capsys.readouterr().err.split())\n    assert 'error: Input strings and --stdin cannot work together' in stderr\n    assert 'XX' not in stderr\n"}, {"mutant_id": "slugify.__main__.x_parse_args__mutmut_235", "test": "de
… [1784 chars omitidos — íntegra em recordings/]
```
</details>

### 5. `holdout#12`

gravação `8afe0bf23af6b5be3a70` · 3687 tokens de saída · US$ 0.0949 · 2026-08-29T22:03:20Z

<details><summary>instrução</summary>

```
Mutations the suite does not catch. Write one test for each.

### `slugify.__main__.x_slugify_params__mutmut_12` — slugify/__main__.py line 81
```diff
- allow_unicode=args.allow_unicode
+ allow_unicodeXX=args.allow_unicode
```

### `slugify.__main__.x_slugify_params__mutmut_24` — slugify/__main__.py line 81
```diff
- allow_unicode=args.allow_unicode
+ allow_unicode=None
```

### `slugify.__main__.x_slugify_params__mutmut_36` — slugify/__main__.py line 81
```diff
- allow_unicode=args.allow_unicode
+ )
```

### `slugify.__main__.x_main__mutmut_1` — slugify/__main__.py line 87
```diff
- if argv is None:
+ if argv is not None:
```

### `slugify.__main__.x_main__mutmut_2` — slugify/__main__.py line 88
```diff
- argv = sys.argv
+ argv = None
```

### `slugify.__main__.x_main__mutmut_3` — slugify/__main__.py line 89
```diff
- args = parse_args(argv)
+ args = None
```

### `slugify.__main__.x_ma
… [238 chars omitidos — íntegra em recordings/]
```
</details>

<details><summary>resposta crua</summary>

```
[{"mutant_id": "slugify.__main__.x_slugify_params__mutmut_12", "test": "def test_slugify_params_key_is_named_allow_unicode():\n    params = slugify_params(parse_args([None, 'Cool Text']))\n    assert 'allow_unicode' in params\n    assert 'allow_unicodeXX' not in params\n    assert params['allow_unicode'] is False"}, {"mutant_id": "slugify.__main__.x_slugify_params__mutmut_24", "test": "def test_slugify_params_allow_unicode_flag_is_passed_through():\n    params = slugify_params(parse_args([None, '--allow-unicode', 'Cool Text']))\n    assert params['allow_unicode'] is True"}, {"mutant_id": "slugify.__main__.x_slugify_params__mutmut_36", "test": "def test_slugify_params_contains_every_expected_key():\n    params = slugify_params(parse_args([None, 'Cool Text']))\n    expected_keys = [\n        'text', 'entities', 'decimal', 'hexadecimal', 'max_length',\n        'word_boundary', 'save_order',
… [1648 chars omitidos — íntegra em recordings/]
```
</details>

### 6. `holdout#13`

gravação `0d9a7c332af1655733b3` · 2189 tokens de saída · US$ 0.0564 · 2026-08-29T22:03:45Z

<details><summary>instrução</summary>

```
Mutations the suite does not catch. Write one test for each.

### `slugify.__main__.x_main__mutmut_6` — slugify/__main__.py line 90
```diff
- params = slugify_params(args)
+ params = slugify_params(None)
```

### `slugify.__main__.x_main__mutmut_7` — slugify/__main__.py line 92
```diff
- print(slugify(**params))
+ print(None)
```

### `slugify.__main__.x_main__mutmut_10` — slugify/__main__.py line 94
```diff
- sys.exit(-1)
+ sys.exit(-2)
```

### `slugify.__main__.x_main__mutmut_8` — slugify/__main__.py line 94
```diff
- sys.exit(-1)
+ sys.exit(None)
```

### `slugify.__main__.x_main__mutmut_9` — slugify/__main__.py line 94
```diff
- sys.exit(-1)
+ sys.exit(+1)
```
```
</details>

<details><summary>resposta crua</summary>

```
[{"mutant_id": "slugify.__main__.x_main__mutmut_6", "test": "def test_main_uses_parsed_args_for_params(capsys):\n    main(['prog', '--separator', '_', 'Hello World'])\n    out = capsys.readouterr().out\n    assert out == 'hello_world\\n'"}, {"mutant_id": "slugify.__main__.x_main__mutmut_7", "test": "def test_main_prints_slugified_text(capsys):\n    main(['prog', 'Cool Text'])\n    out = capsys.readouterr().out\n    assert out == 'cool-text\\n'\n    assert 'None' not in out"}, {"mutant_id": "slugify.__main__.x_main__mutmut_10", "test": "def test_main_exit_code_on_keyboard_interrupt_is_minus_one(monkeypatch):\n    class InterruptingStdout:\n        def write(self, text):\n            raise KeyboardInterrupt\n\n        def flush(self):\n            pass\n\n    monkeypatch.setattr(sys, 'stdout', InterruptingStdout())\n    with pytest.raises(SystemExit) as err:\n        main(['prog', 'Cool Te
… [1073 chars omitidos — íntegra em recordings/]
```
</details>

### 7. `holdout#2`

gravação `dc7f17236bed8823d403` · 2789 tokens de saída · US$ 0.0732 · 2026-08-29T21:56:23Z

<details><summary>instrução</summary>

```
Mutations the suite does not catch. Write one test for each.

### `slugify.__main__.x_parse_args__mutmut_34` — slugify/__main__.py line 17
```diff
- help="Take the text from STDIN")
+ help="take the text from stdin")
```

### `slugify.__main__.x_parse_args__mutmut_35` — slugify/__main__.py line 17
```diff
- help="Take the text from STDIN")
+ help="TAKE THE TEXT FROM STDIN")
```

### `slugify.__main__.x_parse_args__mutmut_44` — slugify/__main__.py line 19
```diff
- parser.add_argument("--no-entities", action='store_false', dest='entities', default=True,
+ parser.add_argument("--no-entities", action='store_false', dest='entities', help="Do not convert HTML entities to unicode")
```

### `slugify.__main__.x_parse_args__mutmut_40` — slugify/__main__.py line 20
```diff
- help="Do not convert HTML entities to unicode")
+ help=None)
```

### `slugify.__main__.x_parse_args__mutmut_45` — slugify/
… [659 chars omitidos — íntegra em recordings/]
```
</details>

<details><summary>resposta crua</summary>

```
[{"mutant_id": "slugify.__main__.x_parse_args__mutmut_34", "test": "def test_help_shows_stdin_description_capitalized(capsys):\n    with pytest.raises(SystemExit) as err:\n        parse_args(['slugify', '--help'])\n    assert err.value.code == 0\n    out = \" \".join(capsys.readouterr().out.split())\n    assert \"Take the text from STDIN\" in out\n    assert \"take the text from stdin\" not in out\n"}, {"mutant_id": "slugify.__main__.x_parse_args__mutmut_35", "test": "def test_help_shows_stdin_description_not_shouted(capsys):\n    with pytest.raises(SystemExit) as err:\n        parse_args(['slugify', '--help'])\n    assert err.value.code == 0\n    out = \" \".join(capsys.readouterr().out.split())\n    assert \"Take the text from STDIN\" in out\n    assert \"TAKE THE TEXT FROM STDIN\" not in out\n"}, {"mutant_id": "slugify.__main__.x_parse_args__mutmut_40", "test": "def test_help_shows_no
… [2454 chars omitidos — íntegra em recordings/]
```
</details>

### 8. `holdout#3`

gravação `45d72d594547f99bada2` · 4096 tokens de saída · US$ 0.1063 · 2026-08-29T21:57:08Z

<details><summary>instrução</summary>

```
Mutations the suite does not catch. Write one test for each.

### `slugify.__main__.x_parse_args__mutmut_64` — slugify/__main__.py line 21
```diff
- parser.add_argument("--no-decimal", action='store_false', dest='decimal', default=True,
+ parser.add_argument("--no-decimal", action='store_false', dest='decimal', help="Do not convert HTML decimal to unicode")
```

### `slugify.__main__.x_parse_args__mutmut_60` — slugify/__main__.py line 22
```diff
- help="Do not convert HTML decimal to unicode")
+ help=None)
```

### `slugify.__main__.x_parse_args__mutmut_65` — slugify/__main__.py line 22
```diff
- help="Do not convert HTML decimal to unicode")
+ )
```

### `slugify.__main__.x_parse_args__mutmut_73` — slugify/__main__.py line 22
```diff
- help="Do not convert HTML decimal to unicode")
+ help="XXDo not convert HTML decimal to unicodeXX")
```

### `slugify.__main__.x_parse_args__mutmut_74` —
… [805 chars omitidos — íntegra em recordings/]
```
</details>

<details><summary>resposta crua</summary>

```
[
  {
    "mutant_id": "slugify.__main__.x_parse_args__mutmut_64",
    "targets": ["slugify.__main__.x_parse_args__mutmut_64", "slugify.__main__.x_parse_args__mutmut_84"],
    "test": null,
    "why": "Both mutants only drop the explicit `default=True` from an `action='store_false'` argument. argparse's `_StoreFalseAction.__init__` already declares `default=True`, so the resulting parser default for `decimal` (and `hexadecimal`) is identical, and the help string is preserved on the merged line. No input can distinguish the mutated parser from the original."
  },
  {
    "mutant_id": "slugify.__main__.x_parse_args__mutmut_84",
    "targets": ["slugify.__main__.x_parse_args__mutmut_64", "slugify.__main__.x_parse_args__mutmut_84"],
    "test": null,
    "why": "Same reason as mutmut_64: removing `default=True` from a `store_false` action is a no-op because argparse's `_StoreFalseAction` def
… [2379 chars omitidos — íntegra em recordings/]
```
</details>

### 9. `holdout#4`

gravação `45b14d88d6fe34dd0f90` · 3649 tokens de saída · US$ 0.0947 · 2026-08-29T21:57:45Z

<details><summary>instrução</summary>

```
Mutations the suite does not catch. Write one test for each.

### `slugify.__main__.x_parse_args__mutmut_85` — slugify/__main__.py line 24
```diff
- help="Do not convert HTML hexadecimal to unicode")
+ )
```

### `slugify.__main__.x_parse_args__mutmut_93` — slugify/__main__.py line 24
```diff
- help="Do not convert HTML hexadecimal to unicode")
+ help="XXDo not convert HTML hexadecimal to unicodeXX")
```

### `slugify.__main__.x_parse_args__mutmut_94` — slugify/__main__.py line 24
```diff
- help="Do not convert HTML hexadecimal to unicode")
+ help="do not convert html hexadecimal to unicode")
```

### `slugify.__main__.x_parse_args__mutmut_95` — slugify/__main__.py line 24
```diff
- help="Do not convert HTML hexadecimal to unicode")
+ help="DO NOT CONVERT HTML HEXADECIMAL TO UNICODE")
```

### `slugify.__main__.x_parse_args__mutmut_103` — slugify/__main__.py line 26
```diff
- help="Outpu
… [600 chars omitidos — íntegra em recordings/]
```
</details>

<details><summary>resposta crua</summary>

```
[{"mutant_id": "slugify.__main__.x_parse_args__mutmut_85", "test": "def test_help_lists_no_hexadecimal_description(capsys, monkeypatch):\n    monkeypatch.setenv(\"COLUMNS\", \"200\")\n    with pytest.raises(SystemExit):\n        parse_args([\"prog\", \"--help\"])\n    out = \" \".join(capsys.readouterr().out.split())\n    assert \"--no-hexadecimal Do not convert HTML hexadecimal to unicode\" in out"}, {"mutant_id": "slugify.__main__.x_parse_args__mutmut_93", "test": "def test_help_no_hexadecimal_description_has_no_marker(capsys, monkeypatch):\n    monkeypatch.setenv(\"COLUMNS\", \"200\")\n    with pytest.raises(SystemExit):\n        parse_args([\"prog\", \"--help\"])\n    out = \" \".join(capsys.readouterr().out.split())\n    assert \"XX\" not in out\n    assert \"--no-hexadecimal Do not convert HTML hexadecimal to unicode\" in out"}, {"mutant_id": "slugify.__main__.x_parse_args__mutmut_
… [2716 chars omitidos — íntegra em recordings/]
```
</details>

### 10. `holdout#5`

gravação `c0ffb3c1a5b6e352c1c6` · 3558 tokens de saída · US$ 0.0930 · 2026-08-29T21:58:25Z

<details><summary>instrução</summary>

```
Mutations the suite does not catch. Write one test for each.

### `slugify.__main__.x_parse_args__mutmut_99` — slugify/__main__.py line 26
```diff
- help="Output string length, 0 for no limit")
+ help=None)
```

### `slugify.__main__.x_parse_args__mutmut_116` — slugify/__main__.py line 27
```diff
- parser.add_argument("--word-boundary", action='store_true', default=False,
+ parser.add_argument("--word-boundary", action='store_true', help="Truncate to complete word even if length ends up shorter than --max_length")
```

### `slugify.__main__.x_parse_args__mutmut_113` — slugify/__main__.py line 28
```diff
- help="Truncate to complete word even if length ends up shorter than --max_length")
+ help=None)
```

### `slugify.__main__.x_parse_args__mutmut_117` — slugify/__main__.py line 28
```diff
- help="Truncate to complete word even if length ends up shorter than --max_length")
+ )
```

### `s
… [1081 chars omitidos — íntegra em recordings/]
```
</details>

<details><summary>resposta crua</summary>

```
[{"mutant_id": "slugify.__main__.x_parse_args__mutmut_99", "test": "def test_help_shows_max_length_description(capsys):\n    with pytest.raises(SystemExit) as err:\n        parse_args(['prog', '--help'])\n    assert err.value.code == 0\n    out = \" \".join(capsys.readouterr().out.split())\n    assert \"--max-length\" in out\n    assert \"Output string length, 0 for no limit\" in out"}, {"mutant_id": "slugify.__main__.x_parse_args__mutmut_113", "test": "def test_help_shows_word_boundary_description(capsys):\n    with pytest.raises(SystemExit) as err:\n        parse_args(['prog', '--help'])\n    assert err.value.code == 0\n    out = \" \".join(capsys.readouterr().out.split())\n    assert \"--word-boundary\" in out\n    assert \"Truncate to complete word even if length ends up shorter than --max_length\" in out"}, {"mutant_id": "slugify.__main__.x_parse_args__mutmut_117", "test": "def test
… [2504 chars omitidos — íntegra em recordings/]
```
</details>

### 11. `holdout#6`

gravação `42540f17479514652ff8` · 3679 tokens de saída · US$ 0.0960 · 2026-08-29T21:59:06Z

<details><summary>instrução</summary>

```
Mutations the suite does not catch. Write one test for each.

### `slugify.__main__.x_parse_args__mutmut_129` — slugify/__main__.py line 30
```diff
- help="When set and --max_length > 0 return whole words in the initial order")
+ help=None)
```

### `slugify.__main__.x_parse_args__mutmut_133` — slugify/__main__.py line 30
```diff
- help="When set and --max_length > 0 return whole words in the initial order")
+ )
```

### `slugify.__main__.x_parse_args__mutmut_139` — slugify/__main__.py line 30
```diff
- help="When set and --max_length > 0 return whole words in the initial order")
+ help="XXWhen set and --max_length > 0 return whole words in the initial orderXX")
```

### `slugify.__main__.x_parse_args__mutmut_140` — slugify/__main__.py line 30
```diff
- help="When set and --max_length > 0 return whole words in the initial order")
+ help="when set and --max_length > 0 return whole words i
… [916 chars omitidos — íntegra em recordings/]
```
</details>

<details><summary>resposta crua</summary>

```
[{"mutant_id": "slugify.__main__.x_parse_args__mutmut_129", "test": "def test_save_order_help_text_is_present(capsys, monkeypatch):\n    monkeypatch.setenv(\"COLUMNS\", \"200\")\n    with pytest.raises(SystemExit) as err:\n        parse_args([\"prog\", \"--help\"])\n    assert err.value.code == 0\n    out = capsys.readouterr().out\n    assert \"--save-order\" in out\n    assert \"When set and --max_length > 0 return whole words in the initial order\" in out\n"}, {"mutant_id": "slugify.__main__.x_parse_args__mutmut_133", "test": "def test_save_order_help_text_not_empty(capsys, monkeypatch):\n    monkeypatch.setenv(\"COLUMNS\", \"200\")\n    with pytest.raises(SystemExit):\n        parse_args([\"prog\", \"--help\"])\n    out = capsys.readouterr().out\n    save_order_lines = [line for line in out.splitlines() if \"--save-order\" in line]\n    assert save_order_lines\n    assert save_order_l
… [2523 chars omitidos — íntegra em recordings/]
```
</details>

### 12. `holdout#7`

gravação `e2631391d34e67779d7e` · 4915 tokens de saída · US$ 0.1263 · 2026-08-29T21:59:58Z

<details><summary>instrução</summary>

```
Mutations the suite does not catch. Write one test for each.

### `slugify.__main__.x_parse_args__mutmut_149` — slugify/__main__.py line 32
```diff
- help="Separator between words. By default " + DEFAULT_SEPARATOR)
+ )
```

### `slugify.__main__.x_parse_args__mutmut_153` — slugify/__main__.py line 32
```diff
- help="Separator between words. By default " + DEFAULT_SEPARATOR)
+ help="XXSeparator between words. By default XX" + DEFAULT_SEPARATOR)
```

### `slugify.__main__.x_parse_args__mutmut_154` — slugify/__main__.py line 32
```diff
- help="Separator between words. By default " + DEFAULT_SEPARATOR)
+ help="separator between words. by default " + DEFAULT_SEPARATOR)
```

### `slugify.__main__.x_parse_args__mutmut_155` — slugify/__main__.py line 32
```diff
- help="Separator between words. By default " + DEFAULT_SEPARATOR)
+ help="SEPARATOR BETWEEN WORDS. BY DEFAULT " + DEFAULT_SEPARATOR)
``
… [554 chars omitidos — íntegra em recordings/]
```
</details>

<details><summary>resposta crua</summary>

```
[{"mutant_id": "slugify.__main__.x_parse_args__mutmut_149", "test": "def test_separator_help_text_present(capsys, monkeypatch):\n    from slugify.slugify import DEFAULT_SEPARATOR\n    monkeypatch.setenv(\"COLUMNS\", \"200\")\n    with pytest.raises(SystemExit) as err:\n        parse_args([None, '--help'])\n    assert err.value.code == 0\n    out = capsys.readouterr().out\n    assert \"--separator\" in out\n    assert \"Separator between words. By default \" + DEFAULT_SEPARATOR in out"}, {"mutant_id": "slugify.__main__.x_parse_args__mutmut_153", "test": "def test_separator_help_text_has_no_marker(capsys, monkeypatch):\n    from slugify.slugify import DEFAULT_SEPARATOR\n    monkeypatch.setenv(\"COLUMNS\", \"200\")\n    with pytest.raises(SystemExit) as err:\n        parse_args([None, '--help'])\n    assert err.value.code == 0\n    out = capsys.readouterr().out\n    assert \"Separator betwe
… [2832 chars omitidos — íntegra em recordings/]
```
</details>

### 13. `holdout#8`

gravação `a563714b36384a010038` · 5274 tokens de saída · US$ 0.1354 · 2026-08-29T22:00:55Z

<details><summary>instrução</summary>

```
Mutations the suite does not catch. Write one test for each.

### `slugify.__main__.x_parse_args__mutmut_167` — slugify/__main__.py line 34
```diff
- help="Words to discount")
+ help="WORDS TO DISCOUNT")
```

### `slugify.__main__.x_parse_args__mutmut_173` — slugify/__main__.py line 35
```diff
- parser.add_argument("--regex-pattern",
+ parser.add_argument("--REGEX-PATTERN",
```

### `slugify.__main__.x_parse_args__mutmut_169` — slugify/__main__.py line 36
```diff
- help="Python regex pattern for disallowed characters")
+ help=None)
```

### `slugify.__main__.x_parse_args__mutmut_171` — slugify/__main__.py line 36
```diff
- help="Python regex pattern for disallowed characters")
+ )
```

### `slugify.__main__.x_parse_args__mutmut_174` — slugify/__main__.py line 36
```diff
- help="Python regex pattern for disallowed characters")
+ help="XXPython regex pattern for disallowed charactersXX")
`
… [711 chars omitidos — íntegra em recordings/]
```
</details>

<details><summary>resposta crua</summary>

```
[{"mutant_id": "slugify.__main__.x_parse_args__mutmut_167", "test": "def test_stopwords_help_text_keeps_original_casing(monkeypatch, capsys):\n    monkeypatch.setenv(\"COLUMNS\", \"200\")\n    with pytest.raises(SystemExit) as err:\n        parse_args([\"prog\", \"--help\"])\n    assert err.value.code == 0\n    out = capsys.readouterr().out\n    assert \"Words to discount\" in out\n    assert \"WORDS TO DISCOUNT\" not in out"}, {"mutant_id": "slugify.__main__.x_parse_args__mutmut_173", "test": "def test_regex_pattern_option_is_lowercase_and_parsed():\n    args = parse_args([\"prog\", \"--regex-pattern\", \"[^a-z0-9]+\"])\n    assert args.regex_pattern == \"[^a-z0-9]+\"\n    assert args.input_string == \"\""}, {"mutant_id": "slugify.__main__.x_parse_args__mutmut_169", "test": "def test_regex_pattern_help_text_is_present(monkeypatch, capsys):\n    monkeypatch.setenv(\"COLUMNS\", \"200\")\n
… [2601 chars omitidos — íntegra em recordings/]
```
</details>

### 14. `holdout#9`

gravação `feea5e26f0fa6de071e7` · 3554 tokens de saída · US$ 0.0921 · 2026-08-29T22:01:33Z

<details><summary>instrução</summary>

```
Mutations the suite does not catch. Write one test for each.

### `slugify.__main__.x_parse_args__mutmut_181` — slugify/__main__.py line 38
```diff
- help="Activate case sensitivity")
+ help=None)
```

### `slugify.__main__.x_parse_args__mutmut_186` — slugify/__main__.py line 38
```diff
- help="Activate case sensitivity")
+ )
```

### `slugify.__main__.x_parse_args__mutmut_194` — slugify/__main__.py line 38
```diff
- help="Activate case sensitivity")
+ help="XXActivate case sensitivityXX")
```

### `slugify.__main__.x_parse_args__mutmut_195` — slugify/__main__.py line 38
```diff
- help="Activate case sensitivity")
+ help="activate case sensitivity")
```

### `slugify.__main__.x_parse_args__mutmut_196` — slugify/__main__.py line 38
```diff
- help="Activate case sensitivity")
+ help="ACTIVATE CASE SENSITIVITY")
```

### `slugify.__main__.x_parse_args__mutmut_199` — slugify/__main__.py line
… [504 chars omitidos — íntegra em recordings/]
```
</details>

<details><summary>resposta crua</summary>

```
[{"mutant_id": "slugify.__main__.x_parse_args__mutmut_181", "test": "def test_help_output_documents_no_lowercase_option(capsys):\n    with pytest.raises(SystemExit):\n        parse_args([None, '--help'])\n    out = \" \".join(capsys.readouterr().out.split())\n    assert \"--no-lowercase Activate case sensitivity\" in out"}, {"mutant_id": "slugify.__main__.x_parse_args__mutmut_186", "test": "def test_help_output_no_lowercase_option_has_help_text(capsys):\n    with pytest.raises(SystemExit):\n        parse_args([None, '--help'])\n    out = \" \".join(capsys.readouterr().out.split())\n    assert \"--no-lowercase Activate case sensitivity\" in out\n    assert \"--no-lowercase --replacements\" not in out"}, {"mutant_id": "slugify.__main__.x_parse_args__mutmut_194", "test": "def test_help_output_no_lowercase_help_text_is_exact(capsys):\n    with pytest.raises(SystemExit):\n        parse_args([
… [1945 chars omitidos — íntegra em recordings/]
```
</details>

### 15. `holdout#repair0.0`

gravação `1c330e915c8889d21a9c` · 663 tokens de saída · US$ 0.0250 · 2026-08-29T22:04:27Z

<details><summary>instrução</summary>

```
These tests did not hold up. Fix each one.

### `slugify.__main__.x_parse_args__mutmut_133`
G1: o teste falha no código ORIGINAL — a expectativa está errada

Your test:
```python
def test_save_order_help_text_not_empty(capsys, monkeypatch):
    monkeypatch.setenv("COLUMNS", "200")
    with pytest.raises(SystemExit):
        parse_args(["prog", "--help"])
    out = capsys.readouterr().out
    save_order_lines = [line for line in out.splitlines() if "--save-order" in line]
    assert save_order_lines
    assert save_order_lines[0].strip() != "--save-order"
    assert "return whole words in the initial order" in save_order_lines[0]

```

What happened:
```
 in line]
        assert save_order_lines
        assert save_order_lines[0].strip() != "--save-order"
>       assert "return whole words in the initial order" in save_order_lines[0]
E       AssertionError: assert 'return whole words in t
… [2671 chars omitidos — íntegra em recordings/]
```
</details>

<details><summary>resposta crua</summary>

```
[{"mutant_id": "slugify.__main__.x_parse_args__mutmut_133", "test": "def test_save_order_help_text_present(capsys):\n    with pytest.raises(SystemExit):\n        parse_args([\"prog\", \"--help\"])\n    out = capsys.readouterr().out\n    assert \"--save-order\" in out\n    assert \"return whole words in the initial order\" in \" \".join(out.split())"}, {"mutant_id": "slugify.__main__.x_main__mutmut_1", "test": "def test_main_uses_the_given_argv(capsys, monkeypatch):\n    monkeypatch.setattr(sys, 'argv', ['prog', 'Other Text'])\n    main(['prog', 'Hello World'])\n    out = capsys.readouterr().out.strip()\n    assert out == 'hello-world'"}, {"mutant_id": "slugify.__main__.x_main__mutmut_2", "test": "def test_main_falls_back_to_sys_argv(capsys, monkeypatch):\n    monkeypatch.setattr(sys, 'argv', ['prog', 'From Argv'])\n    main()\n    out = capsys.readouterr().out.strip()\n    assert out == 
… [14 chars omitidos — íntegra em recordings/]
```
</details>

### 16. `holdout#repair0.1`

gravação `553c7440d5c69ec61a38` · 560 tokens de saída · US$ 0.0228 · 2026-08-29T22:04:33Z

<details><summary>instrução</summary>

```
These tests did not hold up. Fix each one.

### `slugify.__main__.x_main__mutmut_3`
G1: o teste falha no código ORIGINAL — a expectativa está errada

Your test:
```python
def test_main_parses_arguments_into_args(capsys, monkeypatch):
    monkeypatch.setattr(sys, 'argv', [None, 'Other Text'])
    main([None, '--separator', '+', 'Cool Text'])
    out = capsys.readouterr().out.strip()
    assert out == 'cool+text'
```

What happened:
```
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
/opt/homebrew/Cellar/python@3.12/3.12.13_4/Frameworks/Python.framework/Versions/3.12/lib/python3.12/argparse.py:1795: in __init__
    prog = _os.path.basename(_sys.argv[0])
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

p = None

>   ???
E   TypeError: expected str, bytes or os.PathLike object, not NoneType

<frozen posixpath>:171
… [2510 chars omitidos — íntegra em recordings/]
```
</details>

<details><summary>resposta crua</summary>

```
[{"mutant_id": "slugify.__main__.x_main__mutmut_3", "test": "def test_main_parses_arguments_into_args(capsys, monkeypatch):\n    monkeypatch.setattr(sys, 'argv', ['slugify', 'Other Text'])\n    main(['slugify', '--separator', '+', 'Cool Text'])\n    out = capsys.readouterr().out.strip()\n    assert out == 'cool+text'"}, {"mutant_id": "slugify.__main__.x_main__mutmut_4", "test": "def test_main_passes_argv_to_parse_args(capsys, monkeypatch):\n    monkeypatch.setattr(sys, 'argv', ['slugify', 'Other Text'])\n    main(['slugify', 'Compl\u00e8tement D\u00e9j\u00e0'])\n    out = capsys.readouterr().out.strip()\n    assert out == 'completement-deja'"}, {"mutant_id": "slugify.__main__.x_main__mutmut_5", "test": "def test_main_builds_slugify_params(capsys, monkeypatch):\n    monkeypatch.setattr(sys, 'argv', ['slugify', 'Other Text'])\n    main(['slugify', '--max-length', '9', 'jaja lol memes'])\n 
… [73 chars omitidos — íntegra em recordings/]
```
</details>

## Feedback — o que as guardas rejeitaram

- nome de teste repetido: test_allow_unicode_is_a_boolean_flag

## Recusas do modelo — entrada da camada 2

- `` — The mutation only drops `default=True` from the `--no-entities` argument, but argparse's 'store_false' action already uses `default=True` as its own d
- `` — Both mutants only drop the explicit `default=True` from an `action='store_false'` argument. argparse's `_StoreFalseAction.__init__` already declares `
- `` — Same reason as mutmut_64: removing `default=True` from a `store_false` action is a no-op because argparse's `_StoreFalseAction` defaults to True alrea
- `` — The mutation only drops `default=False` from an argument declared with action='store_true'. argparse already uses False as the implicit default for 's
- `` — Same situation as for --word-boundary: removing `default=False` from a 'store_true' argument is a no-op because argparse supplies False as the default
- `` — For --separator, argparse resolves `type=None` (and an omitted `type`) through its registry to the identity function, while `type=str` calls `str()` o
- `` — The mutation only drops the explicit `default=True` from the `--no-lowercase` option. argparse's `_StoreFalseAction.__init__` already declares `defaul
- `` — argparse gives an action='store_true' argument an implicit default of False, so writing default=False explicitly or omitting it produces identical Nam

## Testes que embarcaram: 99

```python
def test_help_shows_parser_description(capsys):
    with pytest.raises(SystemExit) as err:
        parse_args(['prog', '--help'])
    assert err.value.code == 0
    out = capsys.readouterr().out
    lines = [line.strip() for line in out.splitlines()]
    assert 'Slug string' in lines
```

```python
def test_help_parser_description_has_no_marker_characters(capsys):
    with pytest.raises(SystemExit) as err:
        parse_args(['prog', '--help'])
    assert err.value.code == 0
    out = capsys.readouterr().out
    lines = [line.strip() for line in out.splitlines()]
    assert 'Slug string' in lines
    assert 'XXSlug stringXX' not in lines
```

```python
def test_help_parser_description_is_capitalized(capsys):
    with pytest.raises(SystemExit) as err:
        parse_args(['prog', '--help'])
    assert err.value.code == 0
    out = capsys.readouterr().out
    lines = [line.strip() for line in out.splitlines()]
    assert 'Slug string' in lines
    assert 'slug string' not in lines
```

```python
def test_help_parser_description_is_not_upper_case(capsys):
    with pytest.raises(SystemExit) as err:
        parse_args(['prog', '--help'])
    assert err.value.code == 0
    out = capsys.readouterr().out
    lines = [line.strip() for line in out.splitlines()]
    assert 'Slug string' in lines
    assert 'SLUG STRING' not in lines
```

```python
def test_help_shows_input_group_description(capsys):
    with pytest.raises(SystemExit) as err:
        parse_args(['prog', '--help'])
    assert err.value.code == 0
    out = capsys.readouterr().out
    lines = [line.strip() for line in out.splitlines()]
    assert 'Input' in lines
```

```python
def test_help_input_group_description_has_no_marker_characters(capsys):
    with pytest.raises(SystemExit) as err:
        parse_args(['prog', '--help'])
    assert err.value.code == 0
    out = capsys.readouterr().out
    lines = [line.strip() for line in out.splitlines()]
    assert 'Input' in lines
    assert 'XXInputXX' not in lines
```

