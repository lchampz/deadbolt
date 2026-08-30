# Trajetória — geração de testes · T3 · transfer-cursor

Backend `cursor` · modelo `composer-2.5` · effort `high` · modo `live`
Custo US$ 0.0000 · 0 in / 0 out · cache 0 lidos

## Resultado

| | mutantes | mortos | score |
|---|---:|---:|---:|
| antes | 534 | 416 | 0.7790 |
| depois (**mutmut do zero**) | 534 | 427 | **0.7996** |

## Ações — uma chamada por lote de mutantes

### 1. `transfer#0`

gravação `eb39fbdbf418e0a7a86b` · 0 tokens de saída · US$ 0.0000 · 2026-08-29T22:47:58Z

<details><summary>instrução</summary>

```
Mutations the suite does not catch. Write one test for each.

### `toolz.functoolz.x_apply__mutmut_2` — toolz/functoolz.py line 41
```diff
- raise TypeError('func argument is required')
+ raise TypeError(None)
```

### `toolz.functoolz.x_apply__mutmut_3` — toolz/functoolz.py line 41
```diff
- raise TypeError('func argument is required')
+ raise TypeError('XXfunc argument is requiredXX')
```

### `toolz.functoolz.x_apply__mutmut_4` — toolz/functoolz.py line 41
```diff
- raise TypeError('func argument is required')
+ raise TypeError('FUNC ARGUMENT IS REQUIRED')
```

### `toolz.functoolz.x_apply__mutmut_9` — toolz/functoolz.py line 43
```diff
- return func(*args, **kwargs)
+ return func(*args, )
```

### `toolz.functoolz.x_instanceproperty__mutmut_1` — toolz/functoolz.py line 141
```diff
- if fget is None:
+ if fget is not None:
```

### `toolz.functoolz.x_instanceproperty__mutmut_10` — too
… [618 chars omitidos — íntegra em recordings/]
```
</details>

<details><summary>resposta crua</summary>

```
[
  {
    "mutant_id": "toolz.functoolz.x_apply__mutmut_2",
    "test": "def test_apply_no_func_error_message():\n    with pytest.raises(TypeError, match=r'^func argument is required$'):\n        apply()"
  },
  {
    "mutant_id": "toolz.functoolz.x_apply__mutmut_3",
    "test": "def test_apply_no_func_error_message_exact():\n    with pytest.raises(TypeError, match=r'^func argument is required$'):\n        apply()"
  },
  {
    "mutant_id": "toolz.functoolz.x_apply__mutmut_4",
    "test": "def test_apply_no_func_error_message_case():\n    with pytest.raises(TypeError, match=r'^func argument is required$'):\n        apply()"
  },
  {
    "mutant_id": "toolz.functoolz.x_apply__mutmut_9",
    "test": "def test_apply_forwards_kwargs():\n    assert apply(lambda x, y: x + y, 1, y=2) == 3"
  },
  {
    "mutant_id": "toolz.functoolz.x_instanceproperty__mutmut_1",
    "test": "def test_curry_inst
… [1041 chars omitidos — íntegra em recordings/]
```
</details>

### 2. `transfer#1`

gravação `f57cc69f2b04f33c8e46` · 0 tokens de saída · US$ 0.0000 · 2026-08-29T22:48:54Z

<details><summary>instrução</summary>

```
Mutations the suite does not catch. Write one test for each.

### `toolz.functoolz.x_instanceproperty__mutmut_4` — toolz/functoolz.py line 142
```diff
- return partial(instanceproperty, fset=fset, fdel=fdel, doc=doc,
+ return partial(instanceproperty, fset=fset, fdel=None, doc=doc,
```

### `toolz.functoolz.x_instanceproperty__mutmut_5` — toolz/functoolz.py line 142
```diff
- return partial(instanceproperty, fset=fset, fdel=fdel, doc=doc,
+ return partial(instanceproperty, fset=fset, fdel=fdel, doc=None,
```

### `toolz.functoolz.x_instanceproperty__mutmut_7` — toolz/functoolz.py line 142
```diff
- return partial(instanceproperty, fset=fset, fdel=fdel, doc=doc,
+ return partial(fset=fset, fdel=fdel, doc=doc,
```

### `toolz.functoolz.x_instanceproperty__mutmut_8` — toolz/functoolz.py line 142
```diff
- return partial(instanceproperty, fset=fset, fdel=fdel, doc=doc,
+ return partial(insta
… [734 chars omitidos — íntegra em recordings/]
```
</details>

<details><summary>resposta crua</summary>

```
[{"mutant_id": "toolz.functoolz.x_instanceproperty__mutmut_4", "test": null, "targets": ["toolz.functoolz.x_instanceproperty__mutmut_4"], "why": "A linha 142 so e executada no caminho decorador `@instanceproperty(...)` com `fget is None`. Nenhum uso na API publica passa `fdel` nao nulo nesse caminho; forcar `fdel=None` no `partial` e semanticamente identico a omitir `fdel` quando o decorador e chamado sem esse argumento."}, {"mutant_id": "toolz.functoolz.x_instanceproperty__mutmut_5", "test": null, "targets": ["toolz.functoolz.x_instanceproperty__mutmut_5"], "why": "A linha 142 so e executada no caminho decorador `@instanceproperty(...)` com `fget is None`. Nenhum uso na API publica passa `doc` nao nulo nesse caminho; forcar `doc=None` no `partial` e identico ao valor padrao quando o decorador e invocado sem `doc`."}, {"mutant_id": "toolz.functoolz.x_instanceproperty__mutmut_7", "test": 
… [1842 chars omitidos — íntegra em recordings/]
```
</details>

### 3. `transfer#10`

gravação `2cc8a99ca21019dc320d` · 0 tokens de saída · US$ 0.0000 · 2026-08-29T23:00:49Z

<details><summary>instrução</summary>

```
Mutations the suite does not catch. Write one test for each.

### `toolz.functoolz.xǁcurryǁ__reduce____mutmut_27` — toolz/functoolz.py line 353
```diff
- is_decorated = None
+ is_decorated = ""
```

### `toolz.functoolz.xǁcurryǁ__reduce____mutmut_28` — toolz/functoolz.py line 354
```diff
- if modname and qualname:
+ if modname or qualname:
```

### `toolz.functoolz.xǁcurryǁ__reduce____mutmut_45` — toolz/functoolz.py line 363
```diff
- break
+ return
```

### `toolz.functoolz.xǁcurryǁ__reduce____mutmut_60` — toolz/functoolz.py line 372
```diff
- if k not in ('_partial', '_sigspec'))
+ if k not in ('_partial', 'XX_sigspecXX'))
```

### `toolz.functoolz.xǁcurryǁ__reduce____mutmut_61` — toolz/functoolz.py line 372
```diff
- if k not in ('_partial', '_sigspec'))
+ if k not in ('_partial', '_SIGSPEC'))
```

### `toolz.functoolz.x__restore_curry__mutmut_5` — toolz/functoolz.py line 380
```diff

… [437 chars omitidos — íntegra em recordings/]
```
</details>

<details><summary>resposta crua</summary>

```
[
  {
    "mutant_id": "toolz.functoolz.xǁcurryǁ__reduce____mutmut_27",
    "test": null,
    "targets": ["toolz.functoolz.xǁcurryǁ__reduce____mutmut_27"],
    "why": "is_decorated is only consumed as `if is_decorated:` in _restore_curry; both None and the empty string are falsy, and whenever the decorated-curry branch runs it overwrites the initial value with the boolean `obj is self`."
  },
  {
    "mutant_id": "toolz.functoolz.xǁcurryǁ__reduce____mutmut_28",
    "test": "def test_curry_reduce_skips_lookup_without_module():\n    import pickle\n\n    def f(x, y):\n        return x + y\n\n    f.__module__ = ''\n    c = curry(f)(1)\n    restored = pickle.loads(pickle.dumps(c))\n    assert restored(2) == 3"
  },
  {
    "mutant_id": "toolz.functoolz.xǁcurryǁ__reduce____mutmut_45",
    "test": "def test_curry_reduce_survives_missing_qualname_attr():\n    import pickle\n\n    def f(x, y):\n 
… [2126 chars omitidos — íntegra em recordings/]
```
</details>

### 4. `transfer#11`

gravação `8669ddbf4a5ab62fb85c` · 0 tokens de saída · US$ 0.0000 · 2026-08-29T23:01:48Z

<details><summary>instrução</summary>

```
Mutations the suite does not catch. Write one test for each.

### `toolz.functoolz.x__restore_curry__mutmut_23` — toolz/functoolz.py line 387
```diff
- obj = cls(func, *args, **(kwargs or {}))
+ obj = cls(func, *args, )
```

### `toolz.functoolz.x__restore_curry__mutmut_24` — toolz/functoolz.py line 387
```diff
- obj = cls(func, *args, **(kwargs or {}))
+ obj = cls(func, *args, **(kwargs and {}))
```

### `toolz.functoolz.xǁComposeǁ__eq____mutmut_1` — toolz/functoolz.py line 533
```diff
- return other.first == self.first and other.funcs == self.funcs
+ return other.first == self.first or other.funcs == self.funcs
```

### `toolz.functoolz.xǁComposeǁ__hash____mutmut_1` — toolz/functoolz.py line 541
```diff
- return hash(self.first) ^ hash(self.funcs)
+ return hash(self.first) & hash(self.funcs)
```

### `toolz.functoolz.xǁComposeǁ__hash____mutmut_2` — toolz/functoolz.py line 541
```diff
-
… [637 chars omitidos — íntegra em recordings/]
```
</details>

<details><summary>resposta crua</summary>

```
[
  {
    "mutant_id": "toolz.functoolz.x__restore_curry__mutmut_23",
    "test": "def test_curry_pickle_restore_preserves_keywords():\n    import pickle\n\n    def foo(a, b, c=1):\n        return a + b + c\n\n    f = curry(foo, 1, c=2)\n    g = pickle.loads(pickle.dumps(f))\n    assert g(3) == 6\n    assert g(3) == f(3)"
  },
  {
    "mutant_id": "toolz.functoolz.x__restore_curry__mutmut_24",
    "test": "def test_curry_pickle_restore_without_keywords():\n    import pickle\n\n    def foo(a, b):\n        return a + b\n\n    f = curry(foo, 1)\n    g = pickle.loads(pickle.dumps(f))\n    assert g(2) == 3\n    assert g(2) == f(2)"
  },
  {
    "mutant_id": "toolz.functoolz.xǁComposeǁ__eq____mutmut_1",
    "test": "def test_compose_eq_requires_first_and_funcs():\n    def f(x):\n        return x\n\n    def g(x):\n        return x + 1\n\n    def h(x):\n        return x + 2\n\n    assert compose
… [1129 chars omitidos — íntegra em recordings/]
```
</details>

### 5. `transfer#12`

gravação `02a38dea8cfc72674421` · 0 tokens de saída · US$ 0.0000 · 2026-08-29T23:03:05Z

<details><summary>instrução</summary>

```
Mutations the suite does not catch. Write one test for each.

### `toolz.functoolz.xǁjuxtǁ__call____mutmut_3` — toolz/functoolz.py line 672
```diff
- return tuple(func(*args, **kwargs) for func in self.funcs)
+ return tuple(func(*args, ) for func in self.funcs)
```

### `toolz.functoolz.xǁexceptsǁ__call____mutmut_2` — toolz/functoolz.py line 776
```diff
- return self.func(*args, **kwargs)
+ return self.func(*args, )
```

### `toolz.functoolz.x__check_sigspec__mutmut_8` — toolz/functoolz.py line 837
```diff
- hasattr(func, '__signature__')
+ hasattr(func, '__signature__') or hasattr(func.__signature__, '__get__')
```

### `toolz.functoolz.x_num_required_args__mutmut_2` — toolz/functoolz.py line 867
```diff
- sigspec, rv = _check_sigspec(sigspec, func, _sigs._num_required_args,
+ sigspec, rv = _check_sigspec(None, func, _sigs._num_required_args,
```

### `toolz.functoolz.x_has_varargs__mut
… [781 chars omitidos — íntegra em recordings/]
```
</details>

<details><summary>resposta crua</summary>

```
[{"mutant_id": "toolz.functoolz.xǁjuxtǁ__call____mutmut_3", "test": "def test_juxt_passes_kwargs():\n    assert juxt(lambda x, n=0: x + n)(2, n=10) == (2, 12)"}, {"mutant_id": "toolz.functoolz.xǁexceptsǁ__call____mutmut_2", "test": "def test_excepts_passes_kwargs():\n    def divide(a, b=1):\n        return a // b\n\n    assert excepts(ValueError, divide)(10, b=2) == 5"}, {"mutant_id": "toolz.functoolz.x__check_sigspec__mutmut_8", "test": null, "targets": ["toolz.functoolz.x__check_sigspec__mutmut_8"], "why": "A condição mutada (hasattr(func, '__signature__') or hasattr(func.__signature__, '__get__')) and hasattr(func.__signature__, '__get__') é logicamente equivalente à original (hasattr(func, '__signature__') and hasattr(func.__signature__, '__get__')) para todo callable alcançável: se func não tem __signature__, ambas falham; se tem __signature__ sem __get__, ambas falham; se tem __sig
… [1752 chars omitidos — íntegra em recordings/]
```
</details>

### 6. `transfer#13`

gravação `13f17d75d195850fbeed` · 0 tokens de saída · US$ 0.0000 · 2026-08-29T23:06:42Z

<details><summary>instrução</summary>

```
Mutations the suite does not catch. Write one test for each.

### `toolz.functoolz.x_is_valid_args__mutmut_7` — toolz/functoolz.py line 895
```diff
- func, args, kwargs)
+ func, args, None)
```

### `toolz.functoolz.x_is_partial_args__mutmut_2` — toolz/functoolz.py line 906
```diff
- sigspec, rv = _check_sigspec(sigspec, func, _sigs._is_partial_args,
+ sigspec, rv = _check_sigspec(None, func, _sigs._is_partial_args,
```

### `toolz.functoolz.x_is_arity__mutmut_2` — toolz/functoolz.py line 932
```diff
- sigspec, rv = _check_sigspec(sigspec, func, _sigs._is_arity, n, func)
+ sigspec, rv = _check_sigspec(None, func, _sigs._is_arity, n, func)
```

### `toolz.functoolz.x_is_arity__mutmut_14` — toolz/functoolz.py line 935
```diff
- num = num_required_args(func, sigspec)
+ num = num_required_args(None, sigspec)
```

### `toolz.functoolz.x_is_arity__mutmut_15` — toolz/functoolz.py line 935
```di
… [574 chars omitidos — íntegra em recordings/]
```
</details>

<details><summary>resposta crua</summary>

```
[{"mutant_id": "toolz.functoolz.x_is_valid_args__mutmut_7", "test": "def test_is_valid_args_respects_kwargs_with_registry():\n    exc = ValueError('no signature')\n    assert toolz.functoolz.is_valid_args(max, ([1, 2],), {'key': len}, sigspec=exc) is True\n    assert toolz.functoolz.is_valid_args(max, ([1, 2],), {'extra': 1}, sigspec=exc) is False"}, {"mutant_id": "toolz.functoolz.x_is_partial_args__mutmut_2", "test": "def test_is_partial_args_honors_sigspec():\n    def f(a, b):\n        return a + b\n    wrong_sig = inspect.signature(lambda x: x)\n    assert toolz.functoolz.is_partial_args(f, (1, 2), {}, sigspec=wrong_sig) is False"}, {"mutant_id": "toolz.functoolz.x_is_arity__mutmut_2", "test": "def test_is_arity_honors_sigspec_num_required():\n    def f(x):\n        return x\n    wrong_sig = inspect.signature(lambda a, b: a)\n    assert toolz.functoolz.is_arity(1, f, sigspec=wrong_sig
… [1511 chars omitidos — íntegra em recordings/]
```
</details>

### 7. `transfer#14`

gravação `a1c83bf7141acf70ec75` · 0 tokens de saída · US$ 0.0000 · 2026-08-29T23:08:03Z

<details><summary>instrução</summary>

```
Mutations the suite does not catch. Write one test for each.

### `toolz.functoolz.x_is_arity__mutmut_27` — toolz/functoolz.py line 940
```diff
- varargs = has_varargs(func, sigspec)
+ varargs = has_varargs(func, )
```

### `toolz.functoolz.x_is_arity__mutmut_30` — toolz/functoolz.py line 943
```diff
- keywords = has_keywords(func, sigspec)
+ keywords = has_keywords(None, sigspec)
```

### `toolz.functoolz.x_is_arity__mutmut_31` — toolz/functoolz.py line 943
```diff
- keywords = has_keywords(func, sigspec)
+ keywords = has_keywords(func, None)
```

### `toolz.functoolz.x_is_arity__mutmut_33` — toolz/functoolz.py line 943
```diff
- keywords = has_keywords(func, sigspec)
+ keywords = has_keywords(func, )
```

### `toolz.functoolz.x_is_arity__mutmut_35` — toolz/functoolz.py line 946
```diff
- if num is None or varargs is None or keywords is None:  # pragma: no cover
+ if num is None or vara
… [299 chars omitidos — íntegra em recordings/]
```
</details>

<details><summary>resposta crua</summary>

```
[{"mutant_id": "toolz.functoolz.x_is_arity__mutmut_27", "test": null, "why": "is_arity only reaches line 940 after _check_sigspec returns a valid inspect.Signature for func. has_varargs(func, sigspec) and has_varargs(func) both resolve the same signature for that func and return a bool (never None), so is_arity’s result is unchanged. memoize is the only public entry point that calls is_arity, and no public input makes this branch observably different."}, {"mutant_id": "toolz.functoolz.x_is_arity__mutmut_30", "test": null, "why": "When is_arity calls has_keywords with a precomputed valid sigspec, _check_sigspec(sigspec, None, ...) returns that sigspec without consulting func. has_keywords(None, sigspec) and has_keywords(func, sigspec) therefore inspect the same parameter list and return the same bool. No memoize/cache-key behavior changes through the public API."}, {"mutant_id": "toolz.fu
… [1574 chars omitidos — íntegra em recordings/]
```
</details>

### 8. `transfer#2`

gravação `4614aa5c21d684e214ce` · 0 tokens de saída · US$ 0.0000 · 2026-08-29T22:49:52Z

<details><summary>instrução</summary>

```
Mutations the suite does not catch. Write one test for each.

### `toolz.functoolz.x_instanceproperty__mutmut_13` — toolz/functoolz.py line 144
```diff
- return InstanceProperty(fget=fget, fset=fset, fdel=fdel, doc=doc,
+ return InstanceProperty(fget=fget, fset=None, fdel=fdel, doc=doc,
```

### `toolz.functoolz.x_instanceproperty__mutmut_14` — toolz/functoolz.py line 144
```diff
- return InstanceProperty(fget=fget, fset=fset, fdel=fdel, doc=doc,
+ return InstanceProperty(fget=fget, fset=fset, fdel=None, doc=doc,
```

### `toolz.functoolz.x_instanceproperty__mutmut_15` — toolz/functoolz.py line 144
```diff
- return InstanceProperty(fget=fget, fset=fset, fdel=fdel, doc=doc,
+ return InstanceProperty(fget=fget, fset=fset, fdel=fdel, doc=None,
```

### `toolz.functoolz.x_instanceproperty__mutmut_17` — toolz/functoolz.py line 144
```diff
- return InstanceProperty(fget=fget, fset=fset, fdel=f
… [888 chars omitidos — íntegra em recordings/]
```
</details>

<details><summary>resposta crua</summary>

```
[{"mutant_id": "toolz.functoolz.x_instanceproperty__mutmut_13", "test": null, "why": "Every public @instanceproperty usage is read-only with fset=None; hardcoding fset=None is identical to fset=fset when the decorator never supplies a setter."}, {"mutant_id": "toolz.functoolz.x_instanceproperty__mutmut_14", "test": null, "why": "No public API path uses instanceproperty with a deleter; fdel=None hardcoded matches fdel=fdel when fdel is always None."}, {"mutant_id": "toolz.functoolz.x_instanceproperty__mutmut_15", "test": null, "why": "All public @instanceproperty decorators omit doc, so doc is always None; explicit doc=None is the same as omitting it because property.__init__ falls back to fget.__doc__."}, {"mutant_id": "toolz.functoolz.x_instanceproperty__mutmut_16", "test": "def test_excepts_class_doc_instanceproperty_classval():\n    assert excepts.__doc__ is not None\n    assert 'wrap
… [894 chars omitidos — íntegra em recordings/]
```
</details>

### 9. `transfer#3`

gravação `25a8ec78b8ad59049b98` · 0 tokens de saída · US$ 0.0000 · 2026-08-29T22:50:44Z

<details><summary>instrução</summary>

```
Mutations the suite does not catch. Write one test for each.

### `toolz.functoolz.x_instanceproperty__mutmut_21` — toolz/functoolz.py line 145
```diff
- classval=classval)
+ )
```

### `toolz.functoolz.xǁInstancePropertyǁ__init____mutmut_1` — toolz/functoolz.py line 155
```diff
- self.classval = classval
+ self.classval = None
```

### `toolz.functoolz.xǁInstancePropertyǁ__init____mutmut_10` — toolz/functoolz.py line 156
```diff
- property.__init__(self, fget=fget, fset=fset, fdel=fdel, doc=doc)
+ property.__init__(self, fget=fget, fset=fset, doc=doc)
```

### `toolz.functoolz.xǁInstancePropertyǁ__init____mutmut_11` — toolz/functoolz.py line 156
```diff
- property.__init__(self, fget=fget, fset=fset, fdel=fdel, doc=doc)
+ property.__init__(self, fget=fget, fset=fset, fdel=fdel, )
```

### `toolz.functoolz.xǁInstancePropertyǁ__init____mutmut_4` — toolz/functoolz.py line 156
```diff
- pro
… [841 chars omitidos — íntegra em recordings/]
```
</details>

<details><summary>resposta crua</summary>

```
[{"mutant_id": "toolz.functoolz.x_instanceproperty__mutmut_21", "test": "def test_instanceproperty_forwards_classval():\n    C = type(compose(inc))\n    assert C.__doc__ is not None\n    assert 'composition' in C.__doc__.lower()"}, {"mutant_id": "toolz.functoolz.xǁInstancePropertyǁ__init____mutmut_1", "test": "def test_instanceproperty_stores_classval():\n    assert excepts.__doc__ is not None\n    assert 'wrapper around a function' in excepts.__doc__.lower()"}, {"mutant_id": "toolz.functoolz.xǁInstancePropertyǁ__init____mutmut_10", "test": null, "targets": ["toolz.functoolz.xǁInstancePropertyǁ__init____mutmut_10"], "why": "Every InstanceProperty in this module is constructed with fdel=None; omitting fdel in property.__init__ is the same as passing fdel=None."}, {"mutant_id": "toolz.functoolz.xǁInstancePropertyǁ__init____mutmut_11", "test": null, "targets": ["toolz.functoolz.xǁInstancePr
… [1444 chars omitidos — íntegra em recordings/]
```
</details>

### 10. `transfer#4`

gravação `f3cac888e0f2c81f1dbe` · 0 tokens de saída · US$ 0.0000 · 2026-08-29T22:51:25Z

<details><summary>instrução</summary>

```
Mutations the suite does not catch. Write one test for each.

### `toolz.functoolz.xǁInstancePropertyǁ__get____mutmut_4` — toolz/functoolz.py line 161
```diff
- return property.__get__(self, obj, type)
+ return property.__get__(self, obj, None)
```

### `toolz.functoolz.xǁInstancePropertyǁ__get____mutmut_7` — toolz/functoolz.py line 161
```diff
- return property.__get__(self, obj, type)
+ return property.__get__(self, obj, )
```

### `toolz.functoolz.xǁcurryǁ__init____mutmut_2` — toolz/functoolz.py line 198
```diff
- raise TypeError('__init__() takes at least 2 arguments (1 given)')
+ raise TypeError(None)
```

### `toolz.functoolz.xǁcurryǁ__init____mutmut_3` — toolz/functoolz.py line 198
```diff
- raise TypeError('__init__() takes at least 2 arguments (1 given)')
+ raise TypeError('XX__init__() takes at least 2 arguments (1 given)XX')
```

### `toolz.functoolz.xǁcurryǁ__init____mutmut_4
… [708 chars omitidos — íntegra em recordings/]
```
</details>

<details><summary>resposta crua</summary>

```
[{"mutant_id": "toolz.functoolz.xǁInstancePropertyǁ__get____mutmut_4", "targets": ["toolz.functoolz.xǁInstancePropertyǁ__get____mutmut_4"], "test": null, "why": "Na linha 161, obj nunca é None; property.__get__(self, obj, type) com instância ignora o terceiro argumento (objtype) e só chama fget(obj). Todos os acessos públicos a instanceproperty (curry.func, curry.args, compose.__wrapped__, etc.) são via instância, então passar None em vez de type é semanticamente idêntico."}, {"mutant_id": "toolz.functoolz.xǁInstancePropertyǁ__get____mutmut_7", "targets": ["toolz.functoolz.xǁInstancePropertyǁ__get____mutmut_7"], "test": null, "why": "property.__get__(self, obj,) omite o terceiro argumento, que por padrão é None — equivalente a mutmut_4. Com obj não-None, CPython ignora objtype em property.__get__, então nenhum acesso público a instanceproperty distingue essa mutação."}, {"mutant_id": "to
… [1589 chars omitidos — íntegra em recordings/]
```
</details>

### 11. `transfer#5`

gravação `fc0f42762f6bb4c74437` · 0 tokens de saída · US$ 0.0000 · 2026-08-29T22:51:56Z

<details><summary>instrução</summary>

```
Mutations the suite does not catch. Write one test for each.

### `toolz.functoolz.xǁcurryǁ__init____mutmut_13` — toolz/functoolz.py line 201
```diff
- raise TypeError("Input must be callable")
+ raise TypeError("INPUT MUST BE CALLABLE")
```

### `toolz.functoolz.xǁcurryǁ__init____mutmut_56` — toolz/functoolz.py line 223
```diff
- self.__doc__ = getattr(func, '__doc__', None)
+ self.__doc__ = getattr(func, '__doc__', )
```

### `toolz.functoolz.xǁcurryǁ__init____mutmut_60` — toolz/functoolz.py line 224
```diff
- self.__name__ = getattr(func, '__name__', '<curry>')
+ self.__name__ = getattr(None, '__name__', '<curry>')
```

### `toolz.functoolz.xǁcurryǁ__init____mutmut_62` — toolz/functoolz.py line 224
```diff
- self.__name__ = getattr(func, '__name__', '<curry>')
+ self.__name__ = getattr(func, '__name__', None)
```

### `toolz.functoolz.xǁcurryǁ__init____mutmut_66` — toolz/functoolz.py 
… [747 chars omitidos — íntegra em recordings/]
```
</details>

<details><summary>resposta crua</summary>

```
[{"mutant_id": "toolz.functoolz.xǁcurryǁ__init____mutmut_13", "test": "def test_curry_non_callable_error_message():\n    with pytest.raises(TypeError, match='Input must be callable'):\n        curry(1)"}, {"mutant_id": "toolz.functoolz.xǁcurryǁ__init____mutmut_56", "test": null, "targets": ["toolz.functoolz.xǁcurryǁ__init____mutmut_56"], "why": "A mutação introduz getattr(func, '__doc__', ) sem terceiro argumento, o que é SyntaxError em tempo de importação; nenhum teste comportamental passa no original e falha só neste mutante de forma distinguível."}, {"mutant_id": "toolz.functoolz.xǁcurryǁ__init____mutmut_60", "test": "def test_curry_name_from_wrapped_function():\n    def myfunc(x, y):\n        return x + y\n    assert curry(myfunc).__name__ == 'myfunc'"}, {"mutant_id": "toolz.functoolz.xǁcurryǁ__init____mutmut_62", "test": "def test_curry_name_default_for_callable_without_name():\n   
… [1114 chars omitidos — íntegra em recordings/]
```
</details>

### 12. `transfer#6`

gravação `6b41b67f1de96cbb25d1` · 0 tokens de saída · US$ 0.0000 · 2026-08-29T22:52:32Z

<details><summary>instrução</summary>

```
Mutations the suite does not catch. Write one test for each.

### `toolz.functoolz.xǁcurryǁ__init____mutmut_70` — toolz/functoolz.py line 225
```diff
- self.__module__ = getattr(func, '__module__', None)
+ self.__module__ = None
```

### `toolz.functoolz.xǁcurryǁ__init____mutmut_71` — toolz/functoolz.py line 225
```diff
- self.__module__ = getattr(func, '__module__', None)
+ self.__module__ = getattr(None, '__module__', None)
```

### `toolz.functoolz.xǁcurryǁ__init____mutmut_75` — toolz/functoolz.py line 225
```diff
- self.__module__ = getattr(func, '__module__', None)
+ self.__module__ = getattr(func, '__module__', )
```

### `toolz.functoolz.xǁcurryǁ__init____mutmut_76` — toolz/functoolz.py line 225
```diff
- self.__module__ = getattr(func, '__module__', None)
+ self.__module__ = getattr(func, 'XX__module__XX', None)
```

### `toolz.functoolz.xǁcurryǁ__init____mutmut_77` — toolz/funct
… [649 chars omitidos — íntegra em recordings/]
```
</details>

<details><summary>resposta crua</summary>

```
[{"mutant_id": "toolz.functoolz.xǁcurryǁ__init____mutmut_70", "test": "def test_curry_inherits_func_module():\n    def foo(a, b):\n        return a + b\n    foo.__module__ = 'this.is.foo'\n    assert curry(foo).__module__ == 'this.is.foo'"}, {"mutant_id": "toolz.functoolz.xǁcurryǁ__init____mutmut_71", "test": "def test_curry_inherits_func_module():\n    def foo(a, b):\n        return a + b\n    foo.__module__ = 'this.is.foo'\n    assert curry(foo).__module__ == 'this.is.foo'"}, {"mutant_id": "toolz.functoolz.xǁcurryǁ__init____mutmut_75", "test": null, "why": "A mutação introduz getattr(func, '__module__', ) sem valor padrão, o que é SyntaxError em Python; o módulo mutado nem carrega, logo nenhum teste em runtime pode distinguir o original do mutante."}, {"mutant_id": "toolz.functoolz.xǁcurryǁ__init____mutmut_76", "test": "def test_curry_inherits_func_module():\n    def foo(a, b):\n      
… [1159 chars omitidos — íntegra em recordings/]
```
</details>

### 13. `transfer#7`

gravação `6ccb265a81a51610f0ce` · 0 tokens de saída · US$ 0.0000 · 2026-08-29T22:55:01Z

<details><summary>instrução</summary>

```
Mutations the suite does not catch. Write one test for each.

### `toolz.functoolz.xǁcurryǁ_should_curry__mutmut_6` — toolz/functoolz.py line 314
```diff
- kwargs = dict(self.keywords, **kwargs)
+ kwargs = dict(**kwargs)
```

### `toolz.functoolz.xǁcurryǁ_should_curry__mutmut_7` — toolz/functoolz.py line 314
```diff
- kwargs = dict(self.keywords, **kwargs)
+ kwargs = dict(self.keywords, )
```

### `toolz.functoolz.xǁcurryǁ_should_curry__mutmut_10` — toolz/functoolz.py line 316
```diff
- sigspec = self._sigspec = _sigs.signature_or_spec(func)
+ sigspec = self._sigspec = _sigs.signature_or_spec(None)
```

### `toolz.functoolz.xǁcurryǁ_should_curry__mutmut_9` — toolz/functoolz.py line 316
```diff
- sigspec = self._sigspec = _sigs.signature_or_spec(func)
+ sigspec = self._sigspec = None
```

### `toolz.functoolz.xǁcurryǁ_should_curry__mutmut_12` — toolz/functoolz.py line 317
```diff
- self._
… [724 chars omitidos — íntegra em recordings/]
```
</details>

<details><summary>resposta crua</summary>

```
Verificando comportamento de `signature_or_spec` e `has_varargs` para casos limítrofes.
[
  {
    "mutant_id": "toolz.functoolz.xǁcurryǁ_should_curry__mutmut_6",
    "test": "def test_curry_should_curry_includes_bound_keywords():\n    @curry\n    def f(a, b):\n        return a + b\n    cf = f(a=1, b=2)\n    assert raises(TypeError, lambda: cf(3))"
  },
  {
    "mutant_id": "toolz.functoolz.xǁcurryǁ_should_curry__mutmut_7",
    "test": "def test_curry_should_curry_includes_call_keywords():\n    @curry\n    def f(a, b, c=0):\n        return a + b + c\n    cf = f(a=1)\n    assert raises(TypeError, lambda: cf(b=2, d=5))"
  },
  {
    "mutant_id": "toolz.functoolz.xǁcurryǁ_should_curry__mutmut_10",
    "test": "def test_curry_varargs_typeerror_continues_currying():\n    @curry\n    def f(*args):\n        if len(args) < 2:\n            raise TypeError('need 2 args')\n        return args[0] + a
… [1799 chars omitidos — íntegra em recordings/]
```
</details>

### 14. `transfer#8`

gravação `990193dcb24e1faa7dc2` · 0 tokens de saída · US$ 0.0000 · 2026-08-29T22:58:24Z

<details><summary>instrução</summary>

```
Mutations the suite does not catch. Write one test for each.

### `toolz.functoolz.xǁcurryǁ_should_curry__mutmut_22` — toolz/functoolz.py line 321
```diff
- if is_partial_args(func, args, kwargs, sigspec) is False:
+ if is_partial_args(func, args, kwargs, None) is False:
```

### `toolz.functoolz.xǁcurryǁ_should_curry__mutmut_26` — toolz/functoolz.py line 321
```diff
- if is_partial_args(func, args, kwargs, sigspec) is False:
+ if is_partial_args(func, args, kwargs, ) is False:
```

### `toolz.functoolz.xǁcurryǁ_should_curry__mutmut_32` — toolz/functoolz.py line 329
```diff
- elif not is_valid_args(func, args, kwargs, sigspec):
+ elif not is_valid_args(None, args, kwargs, sigspec):
```

### `toolz.functoolz.xǁcurryǁ_should_curry__mutmut_35` — toolz/functoolz.py line 329
```diff
- elif not is_valid_args(func, args, kwargs, sigspec):
+ elif not is_valid_args(func, args, kwargs, None):
```

… [731 chars omitidos — íntegra em recordings/]
```
</details>

<details><summary>resposta crua</summary>

```
[{"mutant_id": "toolz.functoolz.xǁcurryǁ_should_curry__mutmut_22", "test": "def test_curry_zip_empty_call_curries():\n    cz = curry(zip)\n    curried = cz()\n    assert callable(curried)\n    assert list(curried([1], [2])) == [(1, 2)]"}, {"mutant_id": "toolz.functoolz.xǁcurryǁ_should_curry__mutmut_26", "test": "def test_curry_zip_empty_call_curries():\n    cz = curry(zip)\n    curried = cz()\n    assert callable(curried)\n    assert list(curried([1], [2])) == [(1, 2)]"}, {"mutant_id": "toolz.functoolz.xǁcurryǁ_should_curry__mutmut_32", "test": null, "targets": ["toolz.functoolz.xǁcurryǁ_should_curry__mutmut_32"], "why": "Na linha 329, sigspec ja foi obtido do cache em _should_curry. Quando sigspec e um inspect.Signature valido, is_valid_args ignora o parametro func e usa apenas sigspec.bind; trocar func por None nao altera o resultado. Quando sigspec e um objeto TypeError em cache, _che
… [1444 chars omitidos — íntegra em recordings/]
```
</details>

### 15. `transfer#9`

gravação `b91e994809a3f14eeb5f` · 0 tokens de saída · US$ 0.0000 · 2026-08-29T22:59:15Z

<details><summary>instrução</summary>

```
Mutations the suite does not catch. Write one test for each.

### `toolz.functoolz.xǁcurryǁ__reduce____mutmut_19` — toolz/functoolz.py line 352
```diff
- qualname = getattr(func, '__name__', None)
+ qualname = None
```

### `toolz.functoolz.xǁcurryǁ__reduce____mutmut_20` — toolz/functoolz.py line 352
```diff
- qualname = getattr(func, '__name__', None)
+ qualname = getattr(None, '__name__', None)
```

### `toolz.functoolz.xǁcurryǁ__reduce____mutmut_21` — toolz/functoolz.py line 352
```diff
- qualname = getattr(func, '__name__', None)
+ qualname = getattr(func, None, None)
```

### `toolz.functoolz.xǁcurryǁ__reduce____mutmut_22` — toolz/functoolz.py line 352
```diff
- qualname = getattr(func, '__name__', None)
+ qualname = getattr('__name__', None)
```

### `toolz.functoolz.xǁcurryǁ__reduce____mutmut_23` — toolz/functoolz.py line 352
```diff
- qualname = getattr(func, '__name__', None)
+ 
… [589 chars omitidos — íntegra em recordings/]
```
</details>

<details><summary>resposta crua</summary>

```
[{"mutant_id": "toolz.functoolz.xǁcurryǁ__reduce____mutmut_19", "test": "def test_curry_reduce_fallback_to_name_without_qualname_mutmut_19():\n    import pickle\n\n    class NamedCallable:\n        __module__ = __name__\n\n        def __call__(self, x, y=0):\n            return x + y\n\n    target = NamedCallable()\n    target.__name__ = 'curry_reduce_fallback_named_curry_mutmut_19'\n    globals()['curry_reduce_fallback_named_curry_mutmut_19'] = curry(target)\n    c = curry_reduce_fallback_named_curry_mutmut_19\n    assert pickle.loads(pickle.dumps(c)) is c"}, {"mutant_id": "toolz.functoolz.xǁcurryǁ__reduce____mutmut_20", "test": "def test_curry_reduce_fallback_to_name_without_qualname_mutmut_20():\n    import pickle\n\n    class NamedCallable:\n        __module__ = __name__\n\n        def __call__(self, x, y=0):\n            return x + y\n\n    target = NamedCallable()\n    target.__nam
… [3628 chars omitidos — íntegra em recordings/]
```
</details>

### 16. `transfer#repair0.0`

gravação `d75100d4644a8ca8d297` · 0 tokens de saída · US$ 0.0000 · 2026-08-29T23:09:17Z

<details><summary>instrução</summary>

```
These tests did not hold up. Fix each one.

### `toolz.functoolz.x_instanceproperty__mutmut_1`
G1: o teste falha no código ORIGINAL — a expectativa está errada

Your test:
```python
def test_curry_instanceproperty_descriptor():
    assert curry.func is None
    assert curry(mul).func(2, 3) == 6
```

What happened:
```
F                                                                        [100%]
=================================== FAILURES ===================================
____________________ test_curry_instanceproperty_descriptor ____________________

    def test_curry_instanceproperty_descriptor():
        assert curry.func is None
>       assert curry(mul).func(2, 3) == 6
                     ^^^
E       NameError: name 'mul' is not defined

test_probe.py:8: NameError
=========================== short test summary info ============================
FAILED test_probe.py::test_curry
… [2223 chars omitidos — íntegra em recordings/]
```
</details>

<details><summary>resposta crua</summary>

```
[{"mutant_id": "toolz.functoolz.x_instanceproperty__mutmut_1", "test": "def test_curry_instanceproperty_descriptor():\n    from operator import mul\n    assert curry.func is None\n    assert curry(mul).func is mul\n    assert curry(mul).func(2, 3) == 6"}, {"mutant_id": "toolz.functoolz.x_instanceproperty__mutmut_7", "test": "def test_instanceproperty_decorator_with_classval():\n    def inc(x):\n        return x + 1\n    def double(x):\n        return 2 * x\n    composed = compose(inc, double)\n    assert type(composed).__doc__ is not None\n    assert 'composition of functions' in type(composed).__doc__\n    assert excepts.__doc__ is not None\n    assert 'catch exceptions' in excepts.__doc__"}, {"mutant_id": "toolz.functoolz.x_instanceproperty__mutmut_11", "test": "def test_compose_class_doc_from_instanceproperty():\n    def inc(x):\n        return x + 1\n    def double(x):\n        retur
… [223 chars omitidos — íntegra em recordings/]
```
</details>

### 17. `transfer#repair0.1`

gravação `c8bd006c9287ee70e69d` · 0 tokens de saída · US$ 0.0000 · 2026-08-29T23:09:46Z

<details><summary>instrução</summary>

```
These tests did not hold up. Fix each one.

### `toolz.functoolz.x_instanceproperty__mutmut_12`
G1: o teste falha no código ORIGINAL — a expectativa está errada

Your test:
```python
def test_curry_instanceproperty_reads_func():
    cm = curry(mul)
    assert cm.func is mul
    assert cm.args == ()
    assert cm.keywords is None
    assert list(inspect.signature(cm).parameters) == ['a', 'b']
```

What happened:
```
F                                                                        [100%]
=================================== FAILURES ===================================
____________________ test_curry_instanceproperty_reads_func ____________________

    def test_curry_instanceproperty_reads_func():
>       cm = curry(mul)
                   ^^^
E       NameError: name 'mul' is not defined

test_probe.py:7: NameError
=========================== short test summary info ================
… [1977 chars omitidos — íntegra em recordings/]
```
</details>

<details><summary>resposta crua</summary>

```
[{"mutant_id": "toolz.functoolz.x_instanceproperty__mutmut_12", "test": "def test_curry_instanceproperty_reads_func():\n    def mul(a, b):\n        return a * b\n    cm = curry(mul)\n    assert cm.func is mul\n    assert cm.args == ()\n    assert cm.keywords is None"}, {"mutant_id": "toolz.functoolz.x_instanceproperty__mutmut_17", "test": "def test_curry_instanceproperty_fget():\n    def add(a, b):\n        return a + b\n    f = curry(add)\n    assert f.func is add\n    assert f.args == ()\n    bound = f(1)\n    assert bound.func is add\n    assert bound.args == (1,)"}, {"mutant_id": "toolz.functoolz.x_instanceproperty__mutmut_21", "test": "def test_instanceproperty_forwards_classval():\n    composed = compose(lambda x: x + 1)\n    cls = type(composed)\n    assert cls.__doc__ is not None\n    assert 'composition' in cls.__doc__.lower()\n    assert 'lambda' not in cls.__doc__.lower()\n   
… [47 chars omitidos — íntegra em recordings/]
```
</details>

### 18. `transfer#repair0.10`

gravação `cb4174a1e29b4109ca35` · 0 tokens de saída · US$ 0.0000 · 2026-08-29T23:30:40Z

<details><summary>instrução</summary>

```
These tests did not hold up. Fix each one.

### `toolz.functoolz.xǁjuxtǁ__call____mutmut_3`
G1: o teste falha no código ORIGINAL — a expectativa está errada

Your test:
```python
def test_juxt_passes_kwargs():
    assert juxt(lambda x, n=0: x + n)(2, n=10) == (2, 12)
```

What happened:
```
F                                                                        [100%]
=================================== FAILURES ===================================
___________________________ test_juxt_passes_kwargs ____________________________

    def test_juxt_passes_kwargs():
>       assert juxt(lambda x, n=0: x + n)(2, n=10) == (2, 12)
E       assert (12,) == (2, 12)
E         
E         At index 0 diff: 12 != 2
E         Right contains one more item: 12
E         Use -v to get more diff

test_probe.py:7: AssertionError
=========================== short test summary info ============================
… [2306 chars omitidos — íntegra em recordings/]
```
</details>

<details><summary>resposta crua</summary>

```
[{"mutant_id": "toolz.functoolz.xǁjuxtǁ__call____mutmut_3", "test": "def test_juxt_passes_kwargs():\n    assert juxt(lambda x, n=0: x, lambda x, n=0: x + n)(2, n=10) == (2, 12)"}, {"mutant_id": "toolz.functoolz.x_is_partial_args__mutmut_2", "test": "def test_is_partial_args_honors_sigspec():\n    def f(a, b):\n        return a + b\n    sig = toolz.functoolz.inspect.signature(lambda x: x)\n    assert is_partial_args(f, (1, 2), {}, sigspec=sig) is False"}, {"mutant_id": "toolz.functoolz.x_is_arity__mutmut_2", "test": "def test_is_arity_honors_sigspec_num_required():\n    def f(x):\n        return x\n    sig = toolz.functoolz.inspect.signature(lambda a, b: a)\n    assert is_arity(1, f, sigspec=sig) is False"}]
```
</details>

### 19. `transfer#repair0.11`

gravação `fb0c4c62c90e20079538` · 0 tokens de saída · US$ 0.0000 · 2026-08-29T23:31:30Z

<details><summary>instrução</summary>

```
These tests did not hold up. Fix each one.

### `toolz.functoolz.x_is_arity__mutmut_15`
G1: o teste falha no código ORIGINAL — a expectativa está errada

Your test:
```python
def test_is_arity_honors_sigspec_num_required():
    def f(x):
        return x
    wrong_sig = inspect.signature(lambda a, b: a)
    assert toolz.functoolz.is_arity(1, f, sigspec=wrong_sig) is False
```

What happened:
```
                                                               [100%]
=================================== FAILURES ===================================
__________________ test_is_arity_honors_sigspec_num_required ___________________

    def test_is_arity_honors_sigspec_num_required():
        def f(x):
            return x
>       wrong_sig = inspect.signature(lambda a, b: a)
                    ^^^^^^^
E       NameError: name 'inspect' is not defined. Did you forget to import 'inspect'

test_pro
… [2388 chars omitidos — íntegra em recordings/]
```
</details>

<details><summary>resposta crua</summary>

```
[
  {
    "mutant_id": "toolz.functoolz.x_is_arity__mutmut_15",
    "test": "def test_is_arity_honors_sigspec_num_required():\n    def f(x):\n        return x\n\n    def other(a, b):\n        return a\n\n    wrong_sig = curry(other).__signature__\n    assert toolz.functoolz.is_arity(1, f, sigspec=wrong_sig) is False"
  },
  {
    "mutant_id": "toolz.functoolz.x_is_arity__mutmut_17",
    "test": "def test_is_arity_honors_sigspec_num_required():\n    def f(x):\n        return x\n\n    def other(a, b):\n        return a\n\n    wrong_sig = curry(other).__signature__\n    assert toolz.functoolz.is_arity(1, f, sigspec=wrong_sig) is False"
  },
  {
    "mutant_id": "toolz.functoolz.x_is_arity__mutmut_25",
    "test": "def test_is_arity_honors_sigspec_varargs():\n    def f(x):\n        return x\n\n    def other(x, *rest):\n        return x\n\n    wrong_sig = curry(other).__signature__\n    asser
… [67 chars omitidos — íntegra em recordings/]
```
</details>

### 20. `transfer#repair0.2`

gravação `3b26a4ae12e71b22b1f1` · 0 tokens de saída · US$ 0.0000 · 2026-08-29T23:10:19Z

<details><summary>instrução</summary>

```
These tests did not hold up. Fix each one.

### `toolz.functoolz.xǁInstancePropertyǁ__init____mutmut_9`
G1: o teste falha no código ORIGINAL — a expectativa está errada

Your test:
```python
def test_instanceproperty_passes_fget_to_property():
    c = curry(mul)
    assert c.func is mul
    assert c.args == ()
    composed = compose(inc, double)
    assert composed.__doc__.startswith('lambda')
    assert composed.__wrapped__ is double
```

What happened:
```
F                                                                        [100%]
=================================== FAILURES ===================================
________________ test_instanceproperty_passes_fget_to_property _________________

    def test_instanceproperty_passes_fget_to_property():
>       c = curry(mul)
                  ^^^
E       NameError: name 'mul' is not defined

test_probe.py:7: NameError
===================
… [2325 chars omitidos — íntegra em recordings/]
```
</details>

<details><summary>resposta crua</summary>

```
[{"mutant_id": "toolz.functoolz.xǁInstancePropertyǁ__init____mutmut_9", "test": "def test_instanceproperty_passes_fget_to_property():\n    def _mul(x, y):\n        return x * y\n    def _inc(x):\n        return x + 1\n    def _double(x):\n        return 2 * x\n    c = curry(_mul)\n    assert c.func is _mul\n    assert c.args == ()\n    composed = compose(_inc, _double)\n    assert composed.__doc__.startswith('lambda')\n    assert composed.__wrapped__ is _double"}, {"mutant_id": "toolz.functoolz.xǁcurryǁ_should_curry__mutmut_6", "test": "def test_curry_should_curry_includes_bound_keywords():\n    @curry\n    def f(a, b):\n        return a + b\n    cf = f(a=1, b=2)\n    with pytest.raises(TypeError):\n        cf(3)"}, {"mutant_id": "toolz.functoolz.xǁcurryǁ_should_curry__mutmut_7", "test": "def test_curry_should_curry_includes_call_keywords():\n    @curry\n    def f(a, b, c=0):\n        re
… [92 chars omitidos — íntegra em recordings/]
```
</details>

### 21. `transfer#repair0.3`

gravação `cfe15272d526a9844264` · 0 tokens de saída · US$ 0.0000 · 2026-08-29T23:14:48Z

<details><summary>instrução</summary>

```
These tests did not hold up. Fix each one.

### `toolz.functoolz.xǁcurryǁ_should_curry__mutmut_10`
G2: o teste PASSA no código mutado — não detecta a mutação

Your test:
```python
def test_curry_varargs_typeerror_continues_currying():
    @curry
    def f(*args):
        if len(args) < 2:
            raise TypeError('need 2 args')
        return args[0] + args[1]
    assert f(1)(2) == 3
```

What happened:
```
.                                                                        [100%]
1 passed in 0.02s

```

### `toolz.functoolz.xǁcurryǁ_should_curry__mutmut_12`
G2: o teste PASSA no código mutado — não detecta a mutação

Your test:
```python
def test_curry_varargs_typeerror_continues_currying_has_varargs_func():
    @curry
    def f(*args):
        if len(args) < 2:
            raise TypeError('need 2 args')
        return args[0] + args[1]
    assert f(1)(2) == 3
```

What happened:
… [1260 chars omitidos — íntegra em recordings/]
```
</details>

<details><summary>resposta crua</summary>

```
[{"mutant_id": "toolz.functoolz.xǁcurryǁ_should_curry__mutmut_10", "test": "def test_curry_should_curry_caches_function_sigspec():\n    @curry\n    def f(a, b):\n        return a + b\n    assert f(1)(2) == 3"}, {"mutant_id": "toolz.functoolz.xǁcurryǁ_should_curry__mutmut_12", "test": "def test_curry_zip_empty_call_curries():\n    cz = curry(zip)\n    curried = cz()\n    assert callable(curried)\n    assert list(curried([1], [2])) == [(1, 2)]"}, {"mutant_id": "toolz.functoolz.xǁcurryǁ_should_curry__mutmut_18", "test": "def test_curry_reuses_cached_sigspec_on_second_should_curry():\n    cz = curry(zip)\n    cz()\n    curried = cz()\n    assert callable(curried)\n    assert list(curried([1], [2])) == [(1, 2)]"}]
```
</details>

### 22. `transfer#repair0.4`

gravação `42d06e27e0f08abe295a` · 0 tokens de saída · US$ 0.0000 · 2026-08-29T23:18:58Z

<details><summary>instrução</summary>

```
These tests did not hold up. Fix each one.

### `toolz.functoolz.xǁcurryǁ_should_curry__mutmut_22`
G1: o teste falha no código ORIGINAL — a expectativa está errada

Your test:
```python
def test_curry_zip_empty_call_curries():
    cz = curry(zip)
    curried = cz()
    assert callable(curried)
    assert list(curried([1], [2])) == [(1, 2)]
```

What happened:
```
F                                                                        [100%]
=================================== FAILURES ===================================
______________________ test_curry_zip_empty_call_curries _______________________

    def test_curry_zip_empty_call_curries():
        cz = curry(zip)
        curried = cz()
>       assert callable(curried)
E       assert False
E        +  where False = callable(<zip object at 0x101bd3b80>)

test_probe.py:9: AssertionError
=========================== short test summary i
… [2192 chars omitidos — íntegra em recordings/]
```
</details>

<details><summary>resposta crua</summary>

```
[{"mutant_id": "toolz.functoolz.xǁcurryǁ_should_curry__mutmut_22", "test": "def test_curry_map_empty_call_curries():\n    cm = curry(map)\n    curried = cm()\n    assert isinstance(curried, curry)\n    assert list(curried(inc, [1, 2, 3])) == [2, 3, 4]"}, {"mutant_id": "toolz.functoolz.xǁcurryǁ_should_curry__mutmut_26", "test": "def test_curry_map_empty_call_is_partial_args_sigspec():\n    cm = curry(map)\n    curried = cm()\n    assert isinstance(curried, curry)\n    assert list(curried(inc, [1, 2, 3])) == [2, 3, 4]"}, {"mutant_id": "toolz.functoolz.xǁcurryǁ_should_curry__mutmut_35", "test": "def test_curry_should_curry_is_valid_args_uses_cached_sigspec():\n    @curry\n    def f(a, b):\n        return a + b\n    cf = f(a=1, b=2)\n    with pytest.raises(TypeError):\n        cf(3)\n    with pytest.raises(TypeError):\n        cf(3)"}]
```
</details>

### 23. `transfer#repair0.4`

gravação `e61bdca7191e0ec47bb7` · 0 tokens de saída · US$ 0.0000 · 2026-08-29T23:24:35Z

<details><summary>instrução</summary>

```
These tests did not hold up. Fix each one.

### `toolz.functoolz.xǁcurryǁ_should_curry__mutmut_22`
G1: o teste falha no código ORIGINAL — a expectativa está errada

Your test:
```python
def test_curry_zip_empty_call_curries():
    cz = curry(zip)
    curried = cz()
    assert callable(curried)
    assert list(curried([1], [2])) == [(1, 2)]
```

What happened:
```
F                                                                        [100%]
=================================== FAILURES ===================================
______________________ test_curry_zip_empty_call_curries _______________________

    def test_curry_zip_empty_call_curries():
        cz = curry(zip)
        curried = cz()
>       assert callable(curried)
E       assert False
E        +  where False = callable(<zip object at 0x10177fb40>)

test_probe.py:9: AssertionError
=========================== short test summary i
… [2192 chars omitidos — íntegra em recordings/]
```
</details>

<details><summary>resposta crua</summary>

```
[{"mutant_id": "toolz.functoolz.xǁcurryǁ_should_curry__mutmut_22", "test": "def test_curry_varargs_typeerror_still_curries():\n    @curry\n    def f(*args):\n        raise TypeError('nope')\n    assert isinstance(f(1), curry)"}, {"mutant_id": "toolz.functoolz.xǁcurryǁ_should_curry__mutmut_26", "test": "def test_curry_saturated_args_typeerror_raises():\n    @curry\n    def f(a, b):\n        raise TypeError('nope')\n    assert raises(TypeError, lambda: f(1, 2))"}, {"mutant_id": "toolz.functoolz.xǁcurryǁ_should_curry__mutmut_35", "test": "def test_curry_zip_strict_kwarg_partial():\n    z = curry(zip)(strict=True)\n    assert isinstance(z, curry)\n    assert list(z([1], [2])) == [(1, 2)]"}]
```
</details>

### 24. `transfer#repair0.5`

gravação `5132debb72d5e5234627` · 0 tokens de saída · US$ 0.0000 · 2026-08-29T23:20:54Z

<details><summary>instrução</summary>

```
These tests did not hold up. Fix each one.

### `toolz.functoolz.xǁcurryǁ_should_curry__mutmut_39`
G1: o teste falha no código ORIGINAL — a expectativa está errada

Your test:
```python
def test_curry_zip_strict_after_curry():
    cz = curry(zip)
    curried = cz()
    assert list(curried([1], [2], strict=True)) == [(1, 2)]
```

What happened:
```
                                                                   [100%]
=================================== FAILURES ===================================
______________________ test_curry_zip_strict_after_curry _______________________

    def test_curry_zip_strict_after_curry():
        cz = curry(zip)
        curried = cz()
>       assert list(curried([1], [2], strict=True)) == [(1, 2)]
                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       TypeError: 'zip' object is not callable

test_probe.py:9: TypeError
=========================== sh
… [2459 chars omitidos — íntegra em recordings/]
```
</details>

<details><summary>resposta crua</summary>

```
[{"mutant_id": "toolz.functoolz.xǁcurryǁ_should_curry__mutmut_39", "test": "def test_curry_sorted_key_after_curry():\n    cs = curry(sorted)\n    assert cs()(key=int)([3, 1, 2]) == [1, 2, 3]"}, {"mutant_id": "toolz.functoolz.xǁcurryǁ__reduce____mutmut_7", "test": "def test_curry_pickle_operator_without_module():\n    import pickle\n    from operator import add\n    saved = add.__module__\n    add.__module__ = None\n    try:\n        assert pickle.loads(pickle.dumps(curry(add, 1)))(2) == 3\n    finally:\n        add.__module__ = saved"}, {"mutant_id": "toolz.functoolz.xǁcurryǁ__reduce____mutmut_15", "test": "def test_curry_pickle_operator_without_qualname():\n    import pickle\n    from operator import add\n    saved = add.__qualname__\n    add.__qualname__ = None\n    try:\n        assert pickle.loads(pickle.dumps(curry(add, 1)))(2) == 3\n    finally:\n        add.__qualname__ = saved"}]
```
</details>

### 25. `transfer#repair0.6`

gravação `fdc0df35f6e27154a0a4` · 0 tokens de saída · US$ 0.0000 · 2026-08-29T23:26:43Z

<details><summary>instrução</summary>

```
These tests did not hold up. Fix each one.

### `toolz.functoolz.xǁcurryǁ__reduce____mutmut_24`
G2: o teste PASSA no código mutado — não detecta a mutação

Your test:
```python
def test_curry_reduce_fallback_to_name_without_qualname_mutmut_24():
    import pickle

    class NamedCallable:
        __module__ = __name__

        def __call__(self, x, y=0):
            return x + y

    target = NamedCallable()
    target.__name__ = 'curry_reduce_fallback_named_curry_mutmut_24'
    globals()['curry_reduce_fallback_named_curry_mutmut_24'] = curry(target)
    c = curry_reduce_fallback_named_curry_mutmut_24
    assert pickle.loads(pickle.dumps(c)) is c
```

What happened:
```
.                                                                        [100%]
1 passed in 0.02s

```

### `toolz.functoolz.xǁcurryǁ__reduce____mutmut_28`
G1: o teste falha no código ORIGINAL — a expectativa está errada

… [2197 chars omitidos — íntegra em recordings/]
```
</details>

<details><summary>resposta crua</summary>

```
[{"mutant_id": "toolz.functoolz.xǁcurryǁ__reduce____mutmut_24", "test": "def test_curry_reduce_uses_qualname_for_class_method():\n    class A:\n        @curry\n        def add(self, x, y):\n            return x + y\n\n    c = A().add\n    _, state = c.__reduce__()\n    func_ref, is_decorated = state[1], state[5]\n    assert isinstance(func_ref, str)\n    assert func_ref.endswith('.A.add')\n    assert is_decorated is True"}, {"mutant_id": "toolz.functoolz.xǁcurryǁ__reduce____mutmut_28", "test": "def test_curry_reduce_skips_lookup_without_module():\n    class C:\n        __module__ = None\n        __name__ = 'ignored'\n\n        def __call__(self, x, y):\n            return x + y\n\n    c = curry(C())(1)\n    _, state = c.__reduce__()\n    func_ref, is_decorated = state[1], state[5]\n    assert is_decorated is None\n    assert not isinstance(func_ref, str)\n    assert callable(func_ref)"},
… [437 chars omitidos — íntegra em recordings/]
```
</details>

### 26. `transfer#repair0.7`

gravação `f05497c9a2024639f30a` · 0 tokens de saída · US$ 0.0000 · 2026-08-29T23:28:26Z

<details><summary>instrução</summary>

```
These tests did not hold up. Fix each one.

### `toolz.functoolz.xǁcurryǁ__reduce____mutmut_60`
G1: o teste falha no código ORIGINAL — a expectativa está errada

Your test:
```python
def test_curry_pickle_does_not_persist_sigspec():
    import pickle

    @curry
    def add(x, y):
        return x + y

    partial = add(1)
    assert partial._sigspec is not None
    restored = pickle.loads(pickle.dumps(partial))
    assert restored._sigspec is None
    assert restored(2) == 3
```

What happened:
```
S ===================================
__________________ test_curry_pickle_does_not_persist_sigspec __________________

    def test_curry_pickle_does_not_persist_sigspec():
        import pickle
    
        @curry
        def add(x, y):
            return x + y
    
        partial = add(1)
>       assert partial._sigspec is not None
E       assert None is not None
E        +  where None = 
… [2644 chars omitidos — íntegra em recordings/]
```
</details>

<details><summary>resposta crua</summary>

```
[{"mutant_id": "toolz.functoolz.xǁcurryǁ__reduce____mutmut_60", "test": "def test_curry_pickle_does_not_persist_sigspec():\n    import pickle\n    from operator import add\n\n    partial = curry(add)(1)\n    assert raises(TypeError, partial)\n    assert partial._sigspec is not None\n    restored = pickle.loads(pickle.dumps(partial))\n    assert restored._sigspec is None\n    assert restored(2) == 3"}, {"mutant_id": "toolz.functoolz.xǁcurryǁ__reduce____mutmut_61", "test": "def test_curry_pickle_does_not_persist_sigspec():\n    import pickle\n    from operator import add\n\n    partial = curry(add)(1)\n    assert raises(TypeError, partial)\n    assert partial._sigspec is not None\n    restored = pickle.loads(pickle.dumps(partial))\n    assert restored._sigspec is None\n    assert restored(2) == 3"}, {"mutant_id": "toolz.functoolz.x__restore_curry__mutmut_23", "test": "def test_curry_pickle
… [256 chars omitidos — íntegra em recordings/]
```
</details>

### 27. `transfer#repair0.8`

gravação `7ca20ba37bb667feef72` · 0 tokens de saída · US$ 0.0000 · 2026-08-29T23:29:22Z

<details><summary>instrução</summary>

```
These tests did not hold up. Fix each one.

### `toolz.functoolz.x__restore_curry__mutmut_24`
G1: o teste falha no código ORIGINAL — a expectativa está errada

Your test:
```python
def test_curry_pickle_restore_without_keywords():
    import pickle

    def foo(a, b):
        return a + b

    f = curry(foo, 1)
    g = pickle.loads(pickle.dumps(f))
    assert g(2) == 3
    assert g(2) == f(2)
```

What happened:
```
========== FAILURES ===================================
__________________ test_curry_pickle_restore_without_keywords __________________

    def test_curry_pickle_restore_without_keywords():
        import pickle
    
        def foo(a, b):
            return a + b
    
        f = curry(foo, 1)
>       g = pickle.loads(pickle.dumps(f))
                         ^^^^^^^^^^^^^^^
E       AttributeError: Can't get local object 'test_curry_pickle_restore_without_keywords.<locals>
… [2135 chars omitidos — íntegra em recordings/]
```
</details>

<details><summary>resposta crua</summary>

```
[{"mutant_id": "toolz.functoolz.x__restore_curry__mutmut_24", "test": "def test_curry_pickle_restore_without_keywords():\n    import pickle\n    from operator import add\n\n    f = curry(add, 1)\n    assert f.keywords is None\n    g = pickle.loads(pickle.dumps(f))\n    assert g(2) == 3\n    assert g(2) == f(2)"}, {"mutant_id": "toolz.functoolz.xǁComposeǁ__hash____mutmut_1", "test": "def test_compose_hash_uses_bitwise_xor():\n    double_fn = lambda x: 2 * x\n    inc_fn = lambda x: x + 1\n    composed = compose(double_fn, inc_fn)\n    assert hash(composed) == hash(composed.first) ^ hash(composed.funcs)"}, {"mutant_id": "toolz.functoolz.xǁComposeǁ__hash____mutmut_2", "test": "def test_compose_hash_includes_first():\n    double_fn = lambda x: 2 * x\n    c1 = compose(double_fn, lambda x: x + 1)\n    c2 = compose(double_fn, str)\n    assert c1 != c2\n    assert c1.funcs == c2.funcs\n    assert
… [24 chars omitidos — íntegra em recordings/]
```
</details>

### 28. `transfer#repair0.9`

gravação `0aeebcd0d0865064c019` · 0 tokens de saída · US$ 0.0000 · 2026-08-29T23:30:09Z

<details><summary>instrução</summary>

```
These tests did not hold up. Fix each one.

### `toolz.functoolz.xǁComposeǁ__hash____mutmut_3`
G1: o teste falha no código ORIGINAL — a expectativa está errada

Your test:
```python
def test_compose_hash_includes_funcs():
    c1 = compose(double, inc)
    c2 = compose(str, inc)
    assert c1 != c2
    assert hash(c1) != hash(c2)
```

What happened:
```
F                                                                        [100%]
=================================== FAILURES ===================================
_______________________ test_compose_hash_includes_funcs _______________________

    def test_compose_hash_includes_funcs():
>       c1 = compose(double, inc)
                     ^^^^^^
E       NameError: name 'double' is not defined

test_probe.py:7: NameError
=========================== short test summary info ============================
FAILED test_probe.py::test_compose_hash
… [1816 chars omitidos — íntegra em recordings/]
```
</details>

<details><summary>resposta crua</summary>

```
[{"mutant_id": "toolz.functoolz.xǁComposeǁ__hash____mutmut_3", "test": "def test_compose_hash_includes_funcs():\n    last = lambda x: x + 1\n    c1 = compose(lambda x: x * 2, last)\n    c2 = compose(str, last)\n    assert c1 != c2\n    assert hash(c1) != hash(c2)"}, {"mutant_id": "toolz.functoolz.xǁjuxtǁ__init____mutmut_1", "test": "def test_juxt_accepts_list_of_funcs():\n    assert juxt([lambda x: x + 1, lambda x: x * 2])(10) == (11, 20)"}, {"mutant_id": "toolz.functoolz.xǁjuxtǁ__init____mutmut_5", "test": "def test_juxt_single_callable_not_unwrapped():\n    assert juxt(lambda x: x + 1)(10) == (11,)"}]
```
</details>

### 29. `transfer#repair1.0`

gravação `5a704b45e7a8ef8f52a0` · 0 tokens de saída · US$ 0.0000 · 2026-08-29T23:32:46Z

<details><summary>instrução</summary>

```
These tests did not hold up. Fix each one.

### `toolz.functoolz.x_instanceproperty__mutmut_12`
G1: o teste falha no código ORIGINAL — a expectativa está errada

Your test:
```python
def test_curry_instanceproperty_reads_func():
    def mul(a, b):
        return a * b
    cm = curry(mul)
    assert cm.func is mul
    assert cm.args == ()
    assert cm.keywords is None
```

What happened:
```
====== FAILURES ===================================
____________________ test_curry_instanceproperty_reads_func ____________________

    def test_curry_instanceproperty_reads_func():
        def mul(a, b):
            return a * b
        cm = curry(mul)
        assert cm.func is mul
        assert cm.args == ()
>       assert cm.keywords is None
E       assert {} is None
E        +  where {} = <function test_curry_instanceproperty_reads_func.<locals>.mul at 0x103de79c0>.keywords

test_probe.py:12: 
… [2070 chars omitidos — íntegra em recordings/]
```
</details>

<details><summary>resposta crua</summary>

```
[{"mutant_id": "toolz.functoolz.x_instanceproperty__mutmut_12", "test": "def test_curry_instanceproperty_reads_on_instance():\n    def mul(a, b):\n        return a * b\n    cm = curry(mul)\n    assert cm.func is mul\n    assert cm.args == ()\n    assert cm.keywords == {}\n    assert curry.func is None\n    assert curry.keywords is None"}, {"mutant_id": "toolz.functoolz.x_instanceproperty__mutmut_21", "test": "def test_compose_instanceproperty_class_doc():\n    composed = compose(inc, double)\n    cls = type(composed)\n    assert cls.__name__ == 'Compose'\n    assert isinstance(cls.__doc__, str)\n    assert 'composition' in cls.__doc__.lower()\n    assert 'lambda' not in cls.__doc__.lower()\n    assert composed.__doc__.startswith('lambda')"}, {"mutant_id": "toolz.functoolz.x\u01c1InstanceProperty\u01c1__init____mutmut_9", "test": "def test_instanceproperty_init_stores_classval():\n    ass
… [247 chars omitidos — íntegra em recordings/]
```
</details>

### 30. `transfer#repair1.1`

gravação `fdf088fd521a41c889e3` · 0 tokens de saída · US$ 0.0000 · 2026-08-29T23:35:21Z

<details><summary>instrução</summary>

```
These tests did not hold up. Fix each one.

### `toolz.functoolz.xǁcurryǁ_should_curry__mutmut_6`
G2: o teste PASSA no código mutado — não detecta a mutação

Your test:
```python
def test_curry_should_curry_includes_bound_keywords():
    @curry
    def f(a, b):
        return a + b
    cf = f(a=1, b=2)
    with pytest.raises(TypeError):
        cf(3)
```

What happened:
```
.                                                                        [100%]
1 passed in 0.01s

```

### `toolz.functoolz.xǁcurryǁ_should_curry__mutmut_10`
G2: o teste PASSA no código mutado — não detecta a mutação

Your test:
```python
def test_curry_should_curry_caches_function_sigspec():
    @curry
    def f(a, b):
        return a + b
    assert f(1)(2) == 3
```

What happened:
```
.                                                                        [100%]
1 passed in 0.02s

```

### `toolz.functoolz.xǁcurr
… [1025 chars omitidos — íntegra em recordings/]
```
</details>

<details><summary>resposta crua</summary>

```
[{"mutant_id": "toolz.functoolz.xǁcurryǁ_should_curry__mutmut_6", "test": "def test_curry_should_curry_includes_call_args():\n    @curry\n    def f(a, b):\n        return a + b\n    with pytest.raises(TypeError):\n        f(1)(2, 3)"}, {"mutant_id": "toolz.functoolz.xǁcurryǁ_should_curry__mutmut_10", "test": "def test_curry_should_curry_when_partial_args_unknown():\n    assert callable(curry(pow)())"}, {"mutant_id": "toolz.functoolz.xǁcurryǁ_should_curry__mutmut_12", "test": "def test_curry_should_curry_when_more_args_needed():\n    @curry\n    def f(a, b):\n        return a + b\n    assert f()(1)(2) == 3"}]
```
</details>

### 31. `transfer#repair1.2`

gravação `40348df0661ae0376b3f` · 0 tokens de saída · US$ 0.0000 · 2026-08-29T23:40:09Z

<details><summary>instrução</summary>

```
These tests did not hold up. Fix each one.

### `toolz.functoolz.xǁcurryǁ_should_curry__mutmut_18`
G1: o teste falha no código ORIGINAL — a expectativa está errada

Your test:
```python
def test_curry_reuses_cached_sigspec_on_second_should_curry():
    cz = curry(zip)
    cz()
    curried = cz()
    assert callable(curried)
    assert list(curried([1], [2])) == [(1, 2)]
```

What happened:
```
F                                                                        [100%]
=================================== FAILURES ===================================
___________ test_curry_reuses_cached_sigspec_on_second_should_curry ____________

    def test_curry_reuses_cached_sigspec_on_second_should_curry():
        cz = curry(zip)
        cz()
        curried = cz()
>       assert callable(curried)
E       assert False
E        +  where False = callable(<zip object at 0x10151db80>)

test_probe.py:
… [1706 chars omitidos — íntegra em recordings/]
```
</details>

<details><summary>resposta crua</summary>

```
Analisando as mutações em `_should_curry` e o comportamento esperado com base no código e nos erros reportados.
[{"mutant_id": "toolz.functoolz.xǁcurryǁ_should_curry__mutmut_18", "test": "def test_curry_sigspec_cached_for_repeated_calls():\n    @curry\n    def add2(x, y):\n        return x + y\n\n    cf = curry(add2)\n    assert cf(1)(9) == 10\n    assert cf(2)(8) == 10"}, {"mutant_id": "toolz.functoolz.xǁcurryǁ_should_curry__mutmut_22", "test": "def test_curry_too_many_args_typeerror_raises():\n    @curry\n    def f(a, b):\n        raise TypeError('nope')\n\n    with pytest.raises(TypeError):\n        f(1, 2, 3)"}, {"mutant_id": "toolz.functoolz.xǁcurryǁ_should_curry__mutmut_26", "test": "def test_curry_saturated_args_typeerror_raises():\n    @curry\n    def f(a, b):\n        raise TypeError('nope')\n\n    with pytest.raises(TypeError):\n        f(1, 2)"}]
```
</details>

### 32. `transfer#repair1.3`

gravação `063583dac5671bec94b5` · 0 tokens de saída · US$ 0.0000 · 2026-08-29T23:41:40Z

<details><summary>instrução</summary>

```
These tests did not hold up. Fix each one.

### `toolz.functoolz.xǁcurryǁ_should_curry__mutmut_35`
G1: o teste falha no código ORIGINAL — a expectativa está errada

Your test:
```python
def test_curry_zip_strict_kwarg_partial():
    z = curry(zip)(strict=True)
    assert isinstance(z, curry)
    assert list(z([1], [2])) == [(1, 2)]
```

What happened:
```
F                                                                        [100%]
=================================== FAILURES ===================================
_____________________ test_curry_zip_strict_kwarg_partial ______________________

    def test_curry_zip_strict_kwarg_partial():
        z = curry(zip)(strict=True)
>       assert isinstance(z, curry)
E       assert False
E        +  where False = isinstance(<zip object at 0x10224fb80>, curry)

test_probe.py:8: AssertionError
=========================== short test summary info =
… [1097 chars omitidos — íntegra em recordings/]
```
</details>

<details><summary>resposta crua</summary>

```
[{"mutant_id": "toolz.functoolz.xǁcurryǁ_should_curry__mutmut_35", "test": "def test_curry_varargs_delegation_typeerror_curries():\n    def pair(a, b):\n        return a, b\n    delegated = curry(lambda *args: pair(*args))\n    partial = delegated(1)\n    assert isinstance(partial, curry)\n    assert partial(2) == (1, 2)"}, {"mutant_id": "toolz.functoolz.xǁcurryǁ_should_curry__mutmut_39", "test": "def test_curry_genuine_typeerror_with_valid_args():\n    @curry\n    def add(a, b):\n        return a + b\n    assert raises(TypeError, lambda: add('a', 2))"}, {"mutant_id": "toolz.functoolz.xǁcurryǁ__reduce____mutmut_7", "test": "def test_curry_pickle_decorated_identity():\n    import pickle\n    @curry\n    def add(x, y):\n        return x + y\n    restored = pickle.loads(pickle.dumps(add))\n    assert restored is add\n    assert restored(2, 3) == 5"}]
```
</details>

### 33. `transfer#repair1.4`

gravação `ee904f6185a42530a503` · 0 tokens de saída · US$ 0.0000 · 2026-08-29T23:43:49Z

<details><summary>instrução</summary>

```
These tests did not hold up. Fix each one.

### `toolz.functoolz.xǁcurryǁ__reduce____mutmut_15`
G1: o teste falha no código ORIGINAL — a expectativa está errada

Your test:
```python
def test_curry_pickle_operator_without_qualname():
    import pickle
    from operator import add
    saved = add.__qualname__
    add.__qualname__ = None
    try:
        assert pickle.loads(pickle.dumps(curry(add, 1)))(2) == 3
    finally:
        add.__qualname__ = saved
```

What happened:
```
           [100%]
=================================== FAILURES ===================================
_________________ test_curry_pickle_operator_without_qualname __________________

    def test_curry_pickle_operator_without_qualname():
        import pickle
        from operator import add
        saved = add.__qualname__
>       add.__qualname__ = None
        ^^^^^^^^^^^^^^^^
E       AttributeError: attribute '__
… [2786 chars omitidos — íntegra em recordings/]
```
</details>

<details><summary>resposta crua</summary>

```
[{"mutant_id": "toolz.functoolz.xǁcurryǁ__reduce____mutmut_15", "test": "def test_curry_reduce_name_fallback_when_qualname_is_none():\n    import sys\n    module = sys.modules[__name__]\n\n    @curry\n    def decorated_add(a, b):\n        return a + b\n\n    module.name_fallback_curry = decorated_add\n    raw = decorated_add.func\n    old_name, old_qual = raw.__name__, raw.__qualname__\n    try:\n        raw.__name__ = 'name_fallback_curry'\n        raw.__qualname__ = None\n        _, state = decorated_add.__reduce__()\n        assert isinstance(state[1], str)\n        assert state[1] == f'{raw.__module__}:name_fallback_curry'\n        assert state[5] is True\n    finally:\n        raw.__name__ = old_name\n        raw.__qualname__ = old_qual\n        del module.name_fallback_curry"}, {"mutant_id": "toolz.functoolz.xǁcurryǁ__reduce____mutmut_24", "test": "def test_curry_pickle_module_deco
… [976 chars omitidos — íntegra em recordings/]
```
</details>

### 34. `transfer#repair1.5`

gravação `dbb2ec9f61e7165f6de7` · 0 tokens de saída · US$ 0.0000 · 2026-08-29T23:45:10Z

<details><summary>instrução</summary>

```
These tests did not hold up. Fix each one.

### `toolz.functoolz.xǁcurryǁ__reduce____mutmut_60`
G1: o teste falha no código ORIGINAL — a expectativa está errada

Your test:
```python
def test_curry_pickle_does_not_persist_sigspec():
    import pickle
    from operator import add

    partial = curry(add)(1)
    assert raises(TypeError, partial)
    assert partial._sigspec is not None
    restored = pickle.loads(pickle.dumps(partial))
    assert restored._sigspec is None
    assert restored(2) == 3
```

What happened:
```
                                                               [100%]
=================================== FAILURES ===================================
__________________ test_curry_pickle_does_not_persist_sigspec __________________

    def test_curry_pickle_does_not_persist_sigspec():
        import pickle
        from operator import add
    
        partial = curry(ad
… [2725 chars omitidos — íntegra em recordings/]
```
</details>

<details><summary>resposta crua</summary>

```
[{"mutant_id": "toolz.functoolz.xǁcurryǁ__reduce____mutmut_60", "test": "def test_curry_pickle_does_not_persist_sigspec():\n    import pickle\n    from operator import add\n\n    partial = curry(add)(1)\n    try:\n        partial(2, 3)\n    except TypeError:\n        pass\n    assert partial._sigspec is not None\n    restored = pickle.loads(pickle.dumps(partial))\n    assert restored._sigspec is None\n    assert restored(2) == 3"}, {"mutant_id": "toolz.functoolz.xǁcurryǁ__reduce____mutmut_61", "test": "def test_curry_pickle_does_not_persist_sigspec():\n    import pickle\n    from operator import add\n\n    partial = curry(add)(1)\n    try:\n        partial(2, 3)\n    except TypeError:\n        pass\n    assert partial._sigspec is not None\n    restored = pickle.loads(pickle.dumps(partial))\n    assert restored._sigspec is None\n    assert restored(2) == 3"}, {"mutant_id": "toolz.functool
… [274 chars omitidos — íntegra em recordings/]
```
</details>

### 35. `transfer#repair1.6`

gravação `f5cdaa5412705df82350` · 0 tokens de saída · US$ 0.0000 · 2026-08-29T23:46:08Z

<details><summary>instrução</summary>

```
These tests did not hold up. Fix each one.

### `toolz.functoolz.x__restore_curry__mutmut_24`
G1: o teste falha no código ORIGINAL — a expectativa está errada

Your test:
```python
def test_curry_pickle_restore_without_keywords():
    import pickle
    from operator import add

    f = curry(add, 1)
    assert f.keywords is None
    g = pickle.loads(pickle.dumps(f))
    assert g(2) == 3
    assert g(2) == f(2)
```

What happened:
```
                                                            [100%]
=================================== FAILURES ===================================
__________________ test_curry_pickle_restore_without_keywords __________________

    def test_curry_pickle_restore_without_keywords():
        import pickle
        from operator import add
    
        f = curry(add, 1)
>       assert f.keywords is None
E       assert {} is None
E        +  where {} = <built-in
… [1745 chars omitidos — íntegra em recordings/]
```
</details>

<details><summary>resposta crua</summary>

```
[{"mutant_id": "toolz.functoolz.x__restore_curry__mutmut_24", "test": "def test_curry_pickle_preserves_keywords():\n    import pickle\n\n    def f(a, b, c=0):\n        return a + b + c\n\n    cf = curry(f, 1, c=2)\n    g = pickle.loads(pickle.dumps(cf))\n    assert g(3) == 6"}, {"mutant_id": "toolz.functoolz.xǁjuxtǁ__init____mutmut_1", "test": "def test_juxt_single_callable():\n    assert juxt(inc)(10) == 11"}, {"mutant_id": "toolz.functoolz.x_is_partial_args__mutmut_2", "test": "def test_is_partial_args_with_explicit_sigspec():\n    from operator import add\n    import inspect\n\n    sig = inspect.signature(add)\n    assert toolz.functoolz.is_partial_args(add, (1,), {}, sigspec=sig) is True\n    assert toolz.functoolz.is_partial_args(add, (1, 2, 3), {}, sigspec=sig) is False"}]
```
</details>

### 36. `transfer#repair1.7`

gravação `26aebe5241c955bd988e` · 0 tokens de saída · US$ 0.0000 · 2026-08-29T23:47:50Z

<details><summary>instrução</summary>

```
These tests did not hold up. Fix each one.

### `toolz.functoolz.x_is_arity__mutmut_2`
G1: o teste falha no código ORIGINAL — a expectativa está errada

Your test:
```python
def test_is_arity_honors_sigspec_num_required():
    def f(x):
        return x
    sig = toolz.functoolz.inspect.signature(lambda a, b: a)
    assert is_arity(1, f, sigspec=sig) is False
```

What happened:
```
                                       [100%]
=================================== FAILURES ===================================
__________________ test_is_arity_honors_sigspec_num_required ___________________

    def test_is_arity_honors_sigspec_num_required():
        def f(x):
            return x
        sig = toolz.functoolz.inspect.signature(lambda a, b: a)
>       assert is_arity(1, f, sigspec=sig) is False
               ^^^^^^^^
E       NameError: name 'is_arity' is not defined

test_probe.py:10: Name
… [1232 chars omitidos — íntegra em recordings/]
```
</details>

<details><summary>resposta crua</summary>

```
[{"mutant_id": "toolz.functoolz.x_is_arity__mutmut_2", "test": "def test_is_arity_uses_provided_sigspec():\n    def f(x):\n        return x\n    sig = toolz.functoolz.inspect.signature(lambda a, b: a)\n    assert toolz.functoolz.is_arity(1, f, sigspec=sig) is False"}, {"mutant_id": "toolz.functoolz.x_is_arity__mutmut_15", "test": "def test_is_arity_rejects_keywords_from_sigspec():\n    def f(x):\n        return x\n    sig = toolz.functoolz.inspect.signature(lambda a, y=0: a)\n    assert toolz.functoolz.is_arity(1, f, sigspec=sig) is False"}, {"mutant_id": "toolz.functoolz.x_is_arity__mutmut_17", "test": "def test_is_arity_accepts_exact_unary_function():\n    assert toolz.functoolz.is_arity(1, lambda x: x) is True"}]
```
</details>

### 37. `transfer#repair1.8`

gravação `e9ddfcdeae0236b0aeed` · 0 tokens de saída · US$ 0.0000 · 2026-08-29T23:49:22Z

<details><summary>instrução</summary>

```
These tests did not hold up. Fix each one.

### `toolz.functoolz.x_is_arity__mutmut_25`
G2: o teste PASSA no código mutado — não detecta a mutação

Your test:
```python
def test_is_arity_honors_sigspec_varargs():
    def f(x):
        return x

    def other(x, *rest):
        return x

    wrong_sig = curry(other).__signature__
    assert toolz.functoolz.is_arity(1, f, sigspec=wrong_sig) is False
```

What happened:
```
.                                                                        [100%]
1 passed in 0.02s

```

Return the same JSON array shape, only for the entries listed above.
```
</details>

<details><summary>resposta crua</summary>

```
[{"mutant_id": "toolz.functoolz.x_is_arity__mutmut_25", "test": "def test_is_arity_single_positional_argument():\n    def f(x):\n        return x\n    assert toolz.functoolz.is_arity(1, f) is True"}]
```
</details>

## Feedback — o que as guardas rejeitaram

- G1: o teste falha no código ORIGINAL — a expectativa está errada
- G1: o teste falha no código ORIGINAL — a expectativa está errada
- G2: o teste PASSA no código mutado — não detecta a mutação
- G2: o teste PASSA no código mutado — não detecta a mutação
- G2: o teste PASSA no código mutado — não detecta a mutação
- G2: o teste PASSA no código mutado — não detecta a mutação
- G2: o teste PASSA no código mutado — não detecta a mutação
- G2: o teste PASSA no código mutado — não detecta a mutação
- G2: o teste PASSA no código mutado — não detecta a mutação
- G1: o teste falha no código ORIGINAL — a expectativa está errada
- G1: o teste falha no código ORIGINAL — a expectativa está errada
- G1: o teste falha no código ORIGINAL — a expectativa está errada
- G2: o teste PASSA no código mutado — não detecta a mutação
- G2: o teste PASSA no código mutado — não detecta a mutação
- G1: o teste falha no código ORIGINAL — a expectativa está errada
- G1: o teste falha no código ORIGINAL — a expectativa está errada
- G1: o teste falha no código ORIGINAL — a expectativa está errada
- G2: o teste PASSA no código mutado — não detecta a mutação
- G2: o teste PASSA no código mutado — não detecta a mutação
- G2: o teste PASSA no código mutado — não detecta a mutação
- … e mais 6

## Recusas do modelo — entrada da camada 2

- `` — A linha 142 so e executada no caminho decorador `@instanceproperty(...)` com `fget is None`. Nenhum uso na API publica passa `fdel` nao nulo nesse cam
- `` — A linha 142 so e executada no caminho decorador `@instanceproperty(...)` com `fget is None`. Nenhum uso na API publica passa `doc` nao nulo nesse cami
- `` — A linha 142 so e executada no caminho decorador `@instanceproperty(...)` com `fget is None`. Nenhum uso na API publica passa `fset` nao nulo nesse cam
- `` — A linha 142 so e executada no caminho decorador `@instanceproperty(...)` com `fget is None`. Nenhum uso na API publica passa `fdel` nao nulo nesse cam
- `` — Every public @instanceproperty usage is read-only with fset=None; hardcoding fset=None is identical to fset=fset when the decorator never supplies a s
- `` — No public API path uses instanceproperty with a deleter; fdel=None hardcoded matches fdel=fdel when fdel is always None.
- `` — All public @instanceproperty decorators omit doc, so doc is always None; explicit doc=None is the same as omitting it because property.__init__ falls 
- `` — Omitting fset= in the InstanceProperty constructor still defaults fset to None; no public descriptor defines a setter.
- `` — Omitting fdel= in the InstanceProperty constructor still defaults fdel to None; no public descriptor defines a deleter.
- `` — Removing doc=doc only matters when a non-None doc is passed to instanceproperty(); all public decorators leave doc as None, so property still uses fge
- `` — Every InstanceProperty in this module is constructed with fdel=None; omitting fdel in property.__init__ is the same as passing fdel=None.
- `` — Every InstanceProperty is constructed with doc=None, and CPython copies fget.__doc__ in both cases when doc is omitted or explicitly None.

## Testes que embarcaram: 53

```python
def test_apply_no_func_error_message():
    with pytest.raises(TypeError, match=r'^func argument is required$'):
        apply()
```

```python
def test_apply_no_func_error_message_exact():
    with pytest.raises(TypeError, match=r'^func argument is required$'):
        apply()
```

```python
def test_apply_no_func_error_message_case():
    with pytest.raises(TypeError, match=r'^func argument is required$'):
        apply()
```

```python
def test_apply_forwards_kwargs():
    assert apply(lambda x, y: x + y, 1, y=2) == 3
```

```python
def test_instanceproperty_forwards_doc():
    class C:
        @toolz.functoolz.instanceproperty(doc='custom doc', classval='class doc')
        def prop(self):
            pass
    assert C.__dict__['prop'].__doc__ == 'custom doc'
```

```python
def test_excepts_class_doc_from_instanceproperty():
    assert 'dispatch to a handler' in excepts.__doc__
```

