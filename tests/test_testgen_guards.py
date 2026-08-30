"""Testes do maquinário de geração — as guardas e a medição.

Existem porque a primeira versão deste harness reportou score 1.0000: o
`.resolve()` no python do venv saía do venv, TODA execução de pytest morria com
ModuleNotFoundError, e returncode != 0 era lido como "mutante morto". Um harness
quebrado que reporta perfeição é indistinguível de um que funciona — a não ser
que existam controles negativos.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "eval"))
sys.path.insert(0, str(ROOT / "src"))

from deadzone.testgen import Corpus, Sandbox, check, measure  # noqa: E402


@pytest.fixture(scope="module")
def dev():
    c = Corpus("dev")
    sb = Sandbox(c, "pytest")
    yield c, sb
    sb.cleanup()


def test_interpretador_do_corpus_tem_pytest():
    """Regressão: `.resolve()` no bin/python do venv saía do venv e perdia o pytest.

    A primeira versão deste teste afirmava o FORMATO do caminho
    (`".venv/bin/python" in c.python`) e quebrou no container, onde os pacotes
    são globais e não há venv por corpus. Afirmar formato em vez da propriedade
    é o mesmo erro em miniatura: o que importa não é onde o interpretador está,
    é que ele consegue importar pytest.
    """
    import subprocess

    c = Corpus("dev")
    assert Path(c.python).exists(), c.python
    r = subprocess.run([c.python, "-c", "import pytest"], capture_output=True, text=True)
    assert r.returncode == 0, f"{c.python} não tem pytest: {r.stderr[-200:]}"


@pytest.mark.parametrize("set_name", ["dev", "holdout", "transfer"])
def test_sandbox_importa_do_proprio_sandbox(set_name):
    """Sem isso, mediríamos o corpus pinado e não a cópia mutada.

    O risco é real no `toolz`, instalado em modo editável apontando para o corpus.
    """
    c = Corpus(set_name)
    sb = Sandbox(c, f"import-{set_name}")
    try:
        mod = c.spec["files"][0].split("/")[0]
        sb.write_tests("test_probe.py", [
            f"def test_origem():\n"
            f"    import {mod}\n"
            f"    assert '{sb.path.name}' in {mod}.__file__, {mod}.__file__"
        ])
        assert sb.pytest("test_probe.py").returncode == 0
    finally:
        sb.cleanup()


def test_teste_tautologico_nao_conta_como_morte(dev):
    """`assert True` passa na G1 e tem que reprovar na G2."""
    c, sb = dev
    v = check(sb, c.survivors()[0], "def test_taut():\n    assert True")
    assert v.g1_passes_original is True
    assert v.g2_fails_on_mutant is False
    assert v.kills is False


def test_expectativa_falsa_e_barrada_pela_g1(dev):
    """Teste que falha no código ORIGINAL é erro do teste, não do código."""
    c, sb = dev
    v = check(sb, c.survivors()[0], "def test_falsa():\n    assert slugify('abc') == 'ZZZ'")
    assert v.g1_passes_original is False
    assert v.kills is False
    assert "G1" in v.reason


def test_teste_correto_mas_nao_relacionado_nao_conta(dev):
    """Passa no original e no mutante: não detecta nada."""
    c, sb = dev
    v = check(sb, c.survivors()[0],
              "def test_outro():\n    assert slugify('Hello World') == 'hello-world'")
    assert v.g1_passes_original is True
    assert v.kills is False
    assert "G2" in v.reason


def test_medicao_cobre_todo_sobrevivente_e_nao_da_tudo_morto(dev):
    """Um teste inócuo não pode matar nada. Se matar, o harness está quebrado."""
    c, sb = dev
    survivors = c.survivors()[:12]
    sb.write_tests("test_inocuo.py", ["def test_inocuo():\n    assert slugify('a') == 'a'"])
    killed = measure(sb, survivors, "test_inocuo.py")
    assert set(killed) == {m["id"] for m in survivors}
    assert not any(killed.values()), "teste inócuo matou mutante — vazamento"


def test_linha_de_partida_bate_com_a_metrica_congelada():
    """METRIC_TESTGEN.md § 3. Se isto mudar, todo delta reportado é inválido."""
    esperado = {"dev": (216, 170, 46), "holdout": (298, 189, 109), "transfer": (534, 416, 118)}
    for name, (total, killed, surv) in esperado.items():
        c = Corpus(name)
        assert c.totals() == (total, killed), name
        assert len(c.survivors()) == surv, name
