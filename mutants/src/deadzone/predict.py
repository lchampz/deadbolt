"""Deadzone — preditor de ponto cego de teste.

Quatro estágios cumulativos, um por iteração medida:

    baseline  prompt único, arquivo inteiro, sem taxonomia, sem gate
    s4        + taxonomia congelada de 6 tipos (METRIC.md § 4)
    s5        + gate de evidência em código: predição cuja citação não aparece
              literalmente dentro do line_range é DESCARTADA, não corrigida
    s6        + varredura por função com reconciliação

Uso:
    DEADZONE_MODE=live  python -m deadzone.predict --stage baseline --set dev
    DEADZONE_MODE=replay python -m deadzone.predict --stage s6 --set holdout
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "eval"))
sys.path.insert(0, str(ROOT / "src"))

from deadzone.llm import Client  # noqa: E402
from metric import SETS, TAXONOMY  # noqa: E402

PROMPTS = ROOT / "prompts"
CORPUS = ROOT / "corpus"
RESULTS = ROOT / "results"

STAGES = {
    "baseline": {"system": "system_baseline.md", "gate": False, "sweep": False},
    "s4": {"system": "system_taxonomy.md", "gate": False, "sweep": False},
    "s5": {"system": "system_taxonomy.md", "gate": True, "sweep": False},
    "s6": {"system": "system_taxonomy.md", "gate": True, "sweep": True},
}


from mutmut.mutation.trampoline import wrap_in_trampoline as _mutmut_mutated, MutantDict
mutants_x_numbered__mutmut: MutantDict = {}  # type: ignore


# --------------------------------------------------------------------- fonte

@_mutmut_mutated(mutants_x_numbered__mutmut)
def numbered(text: str, start: int = 1) -> str:
    return "\n".join(f"{i:>4} | {ln}" for i, ln in enumerate(text.splitlines(), start=start))


# --------------------------------------------------------------------- fonte

def x_numbered__mutmut_orig(text: str, start: int = 1) -> str:
    return "\n".join(f"{i:>4} | {ln}" for i, ln in enumerate(text.splitlines(), start=start))


# --------------------------------------------------------------------- fonte

def x_numbered__mutmut_1(text: str, start: int = 2) -> str:
    return "\n".join(f"{i:>4} | {ln}" for i, ln in enumerate(text.splitlines(), start=start))


# --------------------------------------------------------------------- fonte

def x_numbered__mutmut_2(text: str, start: int = 1) -> str:
    return "\n".join(None)


# --------------------------------------------------------------------- fonte

def x_numbered__mutmut_3(text: str, start: int = 1) -> str:
    return "XX\nXX".join(f"{i:>4} | {ln}" for i, ln in enumerate(text.splitlines(), start=start))


# --------------------------------------------------------------------- fonte

def x_numbered__mutmut_4(text: str, start: int = 1) -> str:
    return "\n".join(f"{i:>4} | {ln}" for i, ln in enumerate(None, start=start))


# --------------------------------------------------------------------- fonte

def x_numbered__mutmut_5(text: str, start: int = 1) -> str:
    return "\n".join(f"{i:>4} | {ln}" for i, ln in enumerate(text.splitlines(), start=None))


# --------------------------------------------------------------------- fonte

def x_numbered__mutmut_6(text: str, start: int = 1) -> str:
    return "\n".join(f"{i:>4} | {ln}" for i, ln in enumerate(start=start))


# --------------------------------------------------------------------- fonte

def x_numbered__mutmut_7(text: str, start: int = 1) -> str:
    return "\n".join(f"{i:>4} | {ln}" for i, ln in enumerate(text.splitlines(), ))

mutants_x_numbered__mutmut['_mutmut_orig'] = x_numbered__mutmut_orig # type: ignore # mutmut generated
mutants_x_numbered__mutmut['x_numbered__mutmut_1'] = x_numbered__mutmut_1 # type: ignore # mutmut generated
mutants_x_numbered__mutmut['x_numbered__mutmut_2'] = x_numbered__mutmut_2 # type: ignore # mutmut generated
mutants_x_numbered__mutmut['x_numbered__mutmut_3'] = x_numbered__mutmut_3 # type: ignore # mutmut generated
mutants_x_numbered__mutmut['x_numbered__mutmut_4'] = x_numbered__mutmut_4 # type: ignore # mutmut generated
mutants_x_numbered__mutmut['x_numbered__mutmut_5'] = x_numbered__mutmut_5 # type: ignore # mutmut generated
mutants_x_numbered__mutmut['x_numbered__mutmut_6'] = x_numbered__mutmut_6 # type: ignore # mutmut generated
mutants_x_numbered__mutmut['x_numbered__mutmut_7'] = x_numbered__mutmut_7 # type: ignore # mutmut generated


@dataclass
class Target:
    corpus: str
    file: str

    @property
    def path(self) -> Path:
        return CORPUS / self.corpus / self.file

    def source(self) -> str:
        return self.path.read_text()

    def lines(self) -> list[str]:
        return self.source().splitlines()

    def functions(self) -> list[tuple[str, int, int]]:
        """(nome, primeira linha, última linha) de cada def de topo, em ordem."""
        tree = ast.parse(self.source())
        out = []
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                out.append((node.name, node.lineno, node.end_lineno or node.lineno))
            elif isinstance(node, ast.ClassDef):
                for sub in node.body:
                    if isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        out.append(
                            (f"{node.name}.{sub.name}", sub.lineno, sub.end_lineno or sub.lineno)
                        )
        return out


# -------------------------------------------------------------------- parsing

FENCE = re.compile(r"```(?:json)?\s*(.*?)```", re.S)
mutants_x_parse_predictions__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_parse_predictions__mutmut)
def parse_predictions(raw: str) -> list[dict]:
    """S3 morre se a saída não for parseável. Ajusta-se SÓ o parsing, nunca o prompt."""
    text = raw.strip()
    m = FENCE.search(text)
    if m:
        text = m.group(1).strip()
    start = text.find("[")
    end = text.rfind("]")
    if start == -1 or end == -1:
        raise ValueError(f"nenhum array JSON na resposta (primeiros 200 chars): {raw[:200]!r}")
    return json.loads(text[start : end + 1])


def x_parse_predictions__mutmut_orig(raw: str) -> list[dict]:
    """S3 morre se a saída não for parseável. Ajusta-se SÓ o parsing, nunca o prompt."""
    text = raw.strip()
    m = FENCE.search(text)
    if m:
        text = m.group(1).strip()
    start = text.find("[")
    end = text.rfind("]")
    if start == -1 or end == -1:
        raise ValueError(f"nenhum array JSON na resposta (primeiros 200 chars): {raw[:200]!r}")
    return json.loads(text[start : end + 1])


def x_parse_predictions__mutmut_1(raw: str) -> list[dict]:
    """S3 morre se a saída não for parseável. Ajusta-se SÓ o parsing, nunca o prompt."""
    text = None
    m = FENCE.search(text)
    if m:
        text = m.group(1).strip()
    start = text.find("[")
    end = text.rfind("]")
    if start == -1 or end == -1:
        raise ValueError(f"nenhum array JSON na resposta (primeiros 200 chars): {raw[:200]!r}")
    return json.loads(text[start : end + 1])


def x_parse_predictions__mutmut_2(raw: str) -> list[dict]:
    """S3 morre se a saída não for parseável. Ajusta-se SÓ o parsing, nunca o prompt."""
    text = raw.strip()
    m = None
    if m:
        text = m.group(1).strip()
    start = text.find("[")
    end = text.rfind("]")
    if start == -1 or end == -1:
        raise ValueError(f"nenhum array JSON na resposta (primeiros 200 chars): {raw[:200]!r}")
    return json.loads(text[start : end + 1])


def x_parse_predictions__mutmut_3(raw: str) -> list[dict]:
    """S3 morre se a saída não for parseável. Ajusta-se SÓ o parsing, nunca o prompt."""
    text = raw.strip()
    m = FENCE.search(None)
    if m:
        text = m.group(1).strip()
    start = text.find("[")
    end = text.rfind("]")
    if start == -1 or end == -1:
        raise ValueError(f"nenhum array JSON na resposta (primeiros 200 chars): {raw[:200]!r}")
    return json.loads(text[start : end + 1])


def x_parse_predictions__mutmut_4(raw: str) -> list[dict]:
    """S3 morre se a saída não for parseável. Ajusta-se SÓ o parsing, nunca o prompt."""
    text = raw.strip()
    m = FENCE.search(text)
    if m:
        text = None
    start = text.find("[")
    end = text.rfind("]")
    if start == -1 or end == -1:
        raise ValueError(f"nenhum array JSON na resposta (primeiros 200 chars): {raw[:200]!r}")
    return json.loads(text[start : end + 1])


def x_parse_predictions__mutmut_5(raw: str) -> list[dict]:
    """S3 morre se a saída não for parseável. Ajusta-se SÓ o parsing, nunca o prompt."""
    text = raw.strip()
    m = FENCE.search(text)
    if m:
        text = m.group(None).strip()
    start = text.find("[")
    end = text.rfind("]")
    if start == -1 or end == -1:
        raise ValueError(f"nenhum array JSON na resposta (primeiros 200 chars): {raw[:200]!r}")
    return json.loads(text[start : end + 1])


def x_parse_predictions__mutmut_6(raw: str) -> list[dict]:
    """S3 morre se a saída não for parseável. Ajusta-se SÓ o parsing, nunca o prompt."""
    text = raw.strip()
    m = FENCE.search(text)
    if m:
        text = m.group(2).strip()
    start = text.find("[")
    end = text.rfind("]")
    if start == -1 or end == -1:
        raise ValueError(f"nenhum array JSON na resposta (primeiros 200 chars): {raw[:200]!r}")
    return json.loads(text[start : end + 1])


def x_parse_predictions__mutmut_7(raw: str) -> list[dict]:
    """S3 morre se a saída não for parseável. Ajusta-se SÓ o parsing, nunca o prompt."""
    text = raw.strip()
    m = FENCE.search(text)
    if m:
        text = m.group(1).strip()
    start = None
    end = text.rfind("]")
    if start == -1 or end == -1:
        raise ValueError(f"nenhum array JSON na resposta (primeiros 200 chars): {raw[:200]!r}")
    return json.loads(text[start : end + 1])


def x_parse_predictions__mutmut_8(raw: str) -> list[dict]:
    """S3 morre se a saída não for parseável. Ajusta-se SÓ o parsing, nunca o prompt."""
    text = raw.strip()
    m = FENCE.search(text)
    if m:
        text = m.group(1).strip()
    start = text.find(None)
    end = text.rfind("]")
    if start == -1 or end == -1:
        raise ValueError(f"nenhum array JSON na resposta (primeiros 200 chars): {raw[:200]!r}")
    return json.loads(text[start : end + 1])


def x_parse_predictions__mutmut_9(raw: str) -> list[dict]:
    """S3 morre se a saída não for parseável. Ajusta-se SÓ o parsing, nunca o prompt."""
    text = raw.strip()
    m = FENCE.search(text)
    if m:
        text = m.group(1).strip()
    start = text.rfind("[")
    end = text.rfind("]")
    if start == -1 or end == -1:
        raise ValueError(f"nenhum array JSON na resposta (primeiros 200 chars): {raw[:200]!r}")
    return json.loads(text[start : end + 1])


def x_parse_predictions__mutmut_10(raw: str) -> list[dict]:
    """S3 morre se a saída não for parseável. Ajusta-se SÓ o parsing, nunca o prompt."""
    text = raw.strip()
    m = FENCE.search(text)
    if m:
        text = m.group(1).strip()
    start = text.find("XX[XX")
    end = text.rfind("]")
    if start == -1 or end == -1:
        raise ValueError(f"nenhum array JSON na resposta (primeiros 200 chars): {raw[:200]!r}")
    return json.loads(text[start : end + 1])


def x_parse_predictions__mutmut_11(raw: str) -> list[dict]:
    """S3 morre se a saída não for parseável. Ajusta-se SÓ o parsing, nunca o prompt."""
    text = raw.strip()
    m = FENCE.search(text)
    if m:
        text = m.group(1).strip()
    start = text.find("[")
    end = None
    if start == -1 or end == -1:
        raise ValueError(f"nenhum array JSON na resposta (primeiros 200 chars): {raw[:200]!r}")
    return json.loads(text[start : end + 1])


def x_parse_predictions__mutmut_12(raw: str) -> list[dict]:
    """S3 morre se a saída não for parseável. Ajusta-se SÓ o parsing, nunca o prompt."""
    text = raw.strip()
    m = FENCE.search(text)
    if m:
        text = m.group(1).strip()
    start = text.find("[")
    end = text.rfind(None)
    if start == -1 or end == -1:
        raise ValueError(f"nenhum array JSON na resposta (primeiros 200 chars): {raw[:200]!r}")
    return json.loads(text[start : end + 1])


def x_parse_predictions__mutmut_13(raw: str) -> list[dict]:
    """S3 morre se a saída não for parseável. Ajusta-se SÓ o parsing, nunca o prompt."""
    text = raw.strip()
    m = FENCE.search(text)
    if m:
        text = m.group(1).strip()
    start = text.find("[")
    end = text.find("]")
    if start == -1 or end == -1:
        raise ValueError(f"nenhum array JSON na resposta (primeiros 200 chars): {raw[:200]!r}")
    return json.loads(text[start : end + 1])


def x_parse_predictions__mutmut_14(raw: str) -> list[dict]:
    """S3 morre se a saída não for parseável. Ajusta-se SÓ o parsing, nunca o prompt."""
    text = raw.strip()
    m = FENCE.search(text)
    if m:
        text = m.group(1).strip()
    start = text.find("[")
    end = text.rfind("XX]XX")
    if start == -1 or end == -1:
        raise ValueError(f"nenhum array JSON na resposta (primeiros 200 chars): {raw[:200]!r}")
    return json.loads(text[start : end + 1])


def x_parse_predictions__mutmut_15(raw: str) -> list[dict]:
    """S3 morre se a saída não for parseável. Ajusta-se SÓ o parsing, nunca o prompt."""
    text = raw.strip()
    m = FENCE.search(text)
    if m:
        text = m.group(1).strip()
    start = text.find("[")
    end = text.rfind("]")
    if start == -1 and end == -1:
        raise ValueError(f"nenhum array JSON na resposta (primeiros 200 chars): {raw[:200]!r}")
    return json.loads(text[start : end + 1])


def x_parse_predictions__mutmut_16(raw: str) -> list[dict]:
    """S3 morre se a saída não for parseável. Ajusta-se SÓ o parsing, nunca o prompt."""
    text = raw.strip()
    m = FENCE.search(text)
    if m:
        text = m.group(1).strip()
    start = text.find("[")
    end = text.rfind("]")
    if start != -1 or end == -1:
        raise ValueError(f"nenhum array JSON na resposta (primeiros 200 chars): {raw[:200]!r}")
    return json.loads(text[start : end + 1])


def x_parse_predictions__mutmut_17(raw: str) -> list[dict]:
    """S3 morre se a saída não for parseável. Ajusta-se SÓ o parsing, nunca o prompt."""
    text = raw.strip()
    m = FENCE.search(text)
    if m:
        text = m.group(1).strip()
    start = text.find("[")
    end = text.rfind("]")
    if start == +1 or end == -1:
        raise ValueError(f"nenhum array JSON na resposta (primeiros 200 chars): {raw[:200]!r}")
    return json.loads(text[start : end + 1])


def x_parse_predictions__mutmut_18(raw: str) -> list[dict]:
    """S3 morre se a saída não for parseável. Ajusta-se SÓ o parsing, nunca o prompt."""
    text = raw.strip()
    m = FENCE.search(text)
    if m:
        text = m.group(1).strip()
    start = text.find("[")
    end = text.rfind("]")
    if start == -2 or end == -1:
        raise ValueError(f"nenhum array JSON na resposta (primeiros 200 chars): {raw[:200]!r}")
    return json.loads(text[start : end + 1])


def x_parse_predictions__mutmut_19(raw: str) -> list[dict]:
    """S3 morre se a saída não for parseável. Ajusta-se SÓ o parsing, nunca o prompt."""
    text = raw.strip()
    m = FENCE.search(text)
    if m:
        text = m.group(1).strip()
    start = text.find("[")
    end = text.rfind("]")
    if start == -1 or end != -1:
        raise ValueError(f"nenhum array JSON na resposta (primeiros 200 chars): {raw[:200]!r}")
    return json.loads(text[start : end + 1])


def x_parse_predictions__mutmut_20(raw: str) -> list[dict]:
    """S3 morre se a saída não for parseável. Ajusta-se SÓ o parsing, nunca o prompt."""
    text = raw.strip()
    m = FENCE.search(text)
    if m:
        text = m.group(1).strip()
    start = text.find("[")
    end = text.rfind("]")
    if start == -1 or end == +1:
        raise ValueError(f"nenhum array JSON na resposta (primeiros 200 chars): {raw[:200]!r}")
    return json.loads(text[start : end + 1])


def x_parse_predictions__mutmut_21(raw: str) -> list[dict]:
    """S3 morre se a saída não for parseável. Ajusta-se SÓ o parsing, nunca o prompt."""
    text = raw.strip()
    m = FENCE.search(text)
    if m:
        text = m.group(1).strip()
    start = text.find("[")
    end = text.rfind("]")
    if start == -1 or end == -2:
        raise ValueError(f"nenhum array JSON na resposta (primeiros 200 chars): {raw[:200]!r}")
    return json.loads(text[start : end + 1])


def x_parse_predictions__mutmut_22(raw: str) -> list[dict]:
    """S3 morre se a saída não for parseável. Ajusta-se SÓ o parsing, nunca o prompt."""
    text = raw.strip()
    m = FENCE.search(text)
    if m:
        text = m.group(1).strip()
    start = text.find("[")
    end = text.rfind("]")
    if start == -1 or end == -1:
        raise ValueError(None)
    return json.loads(text[start : end + 1])


def x_parse_predictions__mutmut_23(raw: str) -> list[dict]:
    """S3 morre se a saída não for parseável. Ajusta-se SÓ o parsing, nunca o prompt."""
    text = raw.strip()
    m = FENCE.search(text)
    if m:
        text = m.group(1).strip()
    start = text.find("[")
    end = text.rfind("]")
    if start == -1 or end == -1:
        raise ValueError(f"nenhum array JSON na resposta (primeiros 200 chars): {raw[:201]!r}")
    return json.loads(text[start : end + 1])


def x_parse_predictions__mutmut_24(raw: str) -> list[dict]:
    """S3 morre se a saída não for parseável. Ajusta-se SÓ o parsing, nunca o prompt."""
    text = raw.strip()
    m = FENCE.search(text)
    if m:
        text = m.group(1).strip()
    start = text.find("[")
    end = text.rfind("]")
    if start == -1 or end == -1:
        raise ValueError(f"nenhum array JSON na resposta (primeiros 200 chars): {raw[:200]!r}")
    return json.loads(None)


def x_parse_predictions__mutmut_25(raw: str) -> list[dict]:
    """S3 morre se a saída não for parseável. Ajusta-se SÓ o parsing, nunca o prompt."""
    text = raw.strip()
    m = FENCE.search(text)
    if m:
        text = m.group(1).strip()
    start = text.find("[")
    end = text.rfind("]")
    if start == -1 or end == -1:
        raise ValueError(f"nenhum array JSON na resposta (primeiros 200 chars): {raw[:200]!r}")
    return json.loads(text[start : end - 1])


def x_parse_predictions__mutmut_26(raw: str) -> list[dict]:
    """S3 morre se a saída não for parseável. Ajusta-se SÓ o parsing, nunca o prompt."""
    text = raw.strip()
    m = FENCE.search(text)
    if m:
        text = m.group(1).strip()
    start = text.find("[")
    end = text.rfind("]")
    if start == -1 or end == -1:
        raise ValueError(f"nenhum array JSON na resposta (primeiros 200 chars): {raw[:200]!r}")
    return json.loads(text[start : end + 2])

mutants_x_parse_predictions__mutmut['_mutmut_orig'] = x_parse_predictions__mutmut_orig # type: ignore # mutmut generated
mutants_x_parse_predictions__mutmut['x_parse_predictions__mutmut_1'] = x_parse_predictions__mutmut_1 # type: ignore # mutmut generated
mutants_x_parse_predictions__mutmut['x_parse_predictions__mutmut_2'] = x_parse_predictions__mutmut_2 # type: ignore # mutmut generated
mutants_x_parse_predictions__mutmut['x_parse_predictions__mutmut_3'] = x_parse_predictions__mutmut_3 # type: ignore # mutmut generated
mutants_x_parse_predictions__mutmut['x_parse_predictions__mutmut_4'] = x_parse_predictions__mutmut_4 # type: ignore # mutmut generated
mutants_x_parse_predictions__mutmut['x_parse_predictions__mutmut_5'] = x_parse_predictions__mutmut_5 # type: ignore # mutmut generated
mutants_x_parse_predictions__mutmut['x_parse_predictions__mutmut_6'] = x_parse_predictions__mutmut_6 # type: ignore # mutmut generated
mutants_x_parse_predictions__mutmut['x_parse_predictions__mutmut_7'] = x_parse_predictions__mutmut_7 # type: ignore # mutmut generated
mutants_x_parse_predictions__mutmut['x_parse_predictions__mutmut_8'] = x_parse_predictions__mutmut_8 # type: ignore # mutmut generated
mutants_x_parse_predictions__mutmut['x_parse_predictions__mutmut_9'] = x_parse_predictions__mutmut_9 # type: ignore # mutmut generated
mutants_x_parse_predictions__mutmut['x_parse_predictions__mutmut_10'] = x_parse_predictions__mutmut_10 # type: ignore # mutmut generated
mutants_x_parse_predictions__mutmut['x_parse_predictions__mutmut_11'] = x_parse_predictions__mutmut_11 # type: ignore # mutmut generated
mutants_x_parse_predictions__mutmut['x_parse_predictions__mutmut_12'] = x_parse_predictions__mutmut_12 # type: ignore # mutmut generated
mutants_x_parse_predictions__mutmut['x_parse_predictions__mutmut_13'] = x_parse_predictions__mutmut_13 # type: ignore # mutmut generated
mutants_x_parse_predictions__mutmut['x_parse_predictions__mutmut_14'] = x_parse_predictions__mutmut_14 # type: ignore # mutmut generated
mutants_x_parse_predictions__mutmut['x_parse_predictions__mutmut_15'] = x_parse_predictions__mutmut_15 # type: ignore # mutmut generated
mutants_x_parse_predictions__mutmut['x_parse_predictions__mutmut_16'] = x_parse_predictions__mutmut_16 # type: ignore # mutmut generated
mutants_x_parse_predictions__mutmut['x_parse_predictions__mutmut_17'] = x_parse_predictions__mutmut_17 # type: ignore # mutmut generated
mutants_x_parse_predictions__mutmut['x_parse_predictions__mutmut_18'] = x_parse_predictions__mutmut_18 # type: ignore # mutmut generated
mutants_x_parse_predictions__mutmut['x_parse_predictions__mutmut_19'] = x_parse_predictions__mutmut_19 # type: ignore # mutmut generated
mutants_x_parse_predictions__mutmut['x_parse_predictions__mutmut_20'] = x_parse_predictions__mutmut_20 # type: ignore # mutmut generated
mutants_x_parse_predictions__mutmut['x_parse_predictions__mutmut_21'] = x_parse_predictions__mutmut_21 # type: ignore # mutmut generated
mutants_x_parse_predictions__mutmut['x_parse_predictions__mutmut_22'] = x_parse_predictions__mutmut_22 # type: ignore # mutmut generated
mutants_x_parse_predictions__mutmut['x_parse_predictions__mutmut_23'] = x_parse_predictions__mutmut_23 # type: ignore # mutmut generated
mutants_x_parse_predictions__mutmut['x_parse_predictions__mutmut_24'] = x_parse_predictions__mutmut_24 # type: ignore # mutmut generated
mutants_x_parse_predictions__mutmut['x_parse_predictions__mutmut_25'] = x_parse_predictions__mutmut_25 # type: ignore # mutmut generated
mutants_x_parse_predictions__mutmut['x_parse_predictions__mutmut_26'] = x_parse_predictions__mutmut_26 # type: ignore # mutmut generated
mutants_x_evidence_gate__mutmut: MutantDict = {}  # type: ignore


# ---------------------------------------------------------------------- gate

@_mutmut_mutated(mutants_x_evidence_gate__mutmut)
def evidence_gate(preds: list[dict], target: Target) -> tuple[list[dict], list[dict]]:
    """S5. A âncora tem que existir. Predição sem âncora válida é descartada."""
    src = target.lines()
    kept, dropped = [], []
    for p in preds:
        quote = (p.get("evidence_quote") or "").strip()
        rng = p.get("line_range") or []
        ok = False
        if quote and len(rng) == 2:
            lo, hi = sorted(int(x) for x in rng)
            window = src[max(0, lo - 1) : min(len(src), hi)]
            ok = any(quote in line for line in window)
        (kept if ok else dropped).append(
            p if ok else {**p, "_drop_reason": "citação não encontrada no line_range"}
        )
    return kept, dropped


# ---------------------------------------------------------------------- gate

def x_evidence_gate__mutmut_orig(preds: list[dict], target: Target) -> tuple[list[dict], list[dict]]:
    """S5. A âncora tem que existir. Predição sem âncora válida é descartada."""
    src = target.lines()
    kept, dropped = [], []
    for p in preds:
        quote = (p.get("evidence_quote") or "").strip()
        rng = p.get("line_range") or []
        ok = False
        if quote and len(rng) == 2:
            lo, hi = sorted(int(x) for x in rng)
            window = src[max(0, lo - 1) : min(len(src), hi)]
            ok = any(quote in line for line in window)
        (kept if ok else dropped).append(
            p if ok else {**p, "_drop_reason": "citação não encontrada no line_range"}
        )
    return kept, dropped


# ---------------------------------------------------------------------- gate

def x_evidence_gate__mutmut_1(preds: list[dict], target: Target) -> tuple[list[dict], list[dict]]:
    """S5. A âncora tem que existir. Predição sem âncora válida é descartada."""
    src = None
    kept, dropped = [], []
    for p in preds:
        quote = (p.get("evidence_quote") or "").strip()
        rng = p.get("line_range") or []
        ok = False
        if quote and len(rng) == 2:
            lo, hi = sorted(int(x) for x in rng)
            window = src[max(0, lo - 1) : min(len(src), hi)]
            ok = any(quote in line for line in window)
        (kept if ok else dropped).append(
            p if ok else {**p, "_drop_reason": "citação não encontrada no line_range"}
        )
    return kept, dropped


# ---------------------------------------------------------------------- gate

def x_evidence_gate__mutmut_2(preds: list[dict], target: Target) -> tuple[list[dict], list[dict]]:
    """S5. A âncora tem que existir. Predição sem âncora válida é descartada."""
    src = target.lines()
    kept, dropped = None
    for p in preds:
        quote = (p.get("evidence_quote") or "").strip()
        rng = p.get("line_range") or []
        ok = False
        if quote and len(rng) == 2:
            lo, hi = sorted(int(x) for x in rng)
            window = src[max(0, lo - 1) : min(len(src), hi)]
            ok = any(quote in line for line in window)
        (kept if ok else dropped).append(
            p if ok else {**p, "_drop_reason": "citação não encontrada no line_range"}
        )
    return kept, dropped


# ---------------------------------------------------------------------- gate

def x_evidence_gate__mutmut_3(preds: list[dict], target: Target) -> tuple[list[dict], list[dict]]:
    """S5. A âncora tem que existir. Predição sem âncora válida é descartada."""
    src = target.lines()
    kept, dropped = [], []
    for p in preds:
        quote = None
        rng = p.get("line_range") or []
        ok = False
        if quote and len(rng) == 2:
            lo, hi = sorted(int(x) for x in rng)
            window = src[max(0, lo - 1) : min(len(src), hi)]
            ok = any(quote in line for line in window)
        (kept if ok else dropped).append(
            p if ok else {**p, "_drop_reason": "citação não encontrada no line_range"}
        )
    return kept, dropped


# ---------------------------------------------------------------------- gate

def x_evidence_gate__mutmut_4(preds: list[dict], target: Target) -> tuple[list[dict], list[dict]]:
    """S5. A âncora tem que existir. Predição sem âncora válida é descartada."""
    src = target.lines()
    kept, dropped = [], []
    for p in preds:
        quote = (p.get("evidence_quote") and "").strip()
        rng = p.get("line_range") or []
        ok = False
        if quote and len(rng) == 2:
            lo, hi = sorted(int(x) for x in rng)
            window = src[max(0, lo - 1) : min(len(src), hi)]
            ok = any(quote in line for line in window)
        (kept if ok else dropped).append(
            p if ok else {**p, "_drop_reason": "citação não encontrada no line_range"}
        )
    return kept, dropped


# ---------------------------------------------------------------------- gate

def x_evidence_gate__mutmut_5(preds: list[dict], target: Target) -> tuple[list[dict], list[dict]]:
    """S5. A âncora tem que existir. Predição sem âncora válida é descartada."""
    src = target.lines()
    kept, dropped = [], []
    for p in preds:
        quote = (p.get(None) or "").strip()
        rng = p.get("line_range") or []
        ok = False
        if quote and len(rng) == 2:
            lo, hi = sorted(int(x) for x in rng)
            window = src[max(0, lo - 1) : min(len(src), hi)]
            ok = any(quote in line for line in window)
        (kept if ok else dropped).append(
            p if ok else {**p, "_drop_reason": "citação não encontrada no line_range"}
        )
    return kept, dropped


# ---------------------------------------------------------------------- gate

def x_evidence_gate__mutmut_6(preds: list[dict], target: Target) -> tuple[list[dict], list[dict]]:
    """S5. A âncora tem que existir. Predição sem âncora válida é descartada."""
    src = target.lines()
    kept, dropped = [], []
    for p in preds:
        quote = (p.get("XXevidence_quoteXX") or "").strip()
        rng = p.get("line_range") or []
        ok = False
        if quote and len(rng) == 2:
            lo, hi = sorted(int(x) for x in rng)
            window = src[max(0, lo - 1) : min(len(src), hi)]
            ok = any(quote in line for line in window)
        (kept if ok else dropped).append(
            p if ok else {**p, "_drop_reason": "citação não encontrada no line_range"}
        )
    return kept, dropped


# ---------------------------------------------------------------------- gate

def x_evidence_gate__mutmut_7(preds: list[dict], target: Target) -> tuple[list[dict], list[dict]]:
    """S5. A âncora tem que existir. Predição sem âncora válida é descartada."""
    src = target.lines()
    kept, dropped = [], []
    for p in preds:
        quote = (p.get("EVIDENCE_QUOTE") or "").strip()
        rng = p.get("line_range") or []
        ok = False
        if quote and len(rng) == 2:
            lo, hi = sorted(int(x) for x in rng)
            window = src[max(0, lo - 1) : min(len(src), hi)]
            ok = any(quote in line for line in window)
        (kept if ok else dropped).append(
            p if ok else {**p, "_drop_reason": "citação não encontrada no line_range"}
        )
    return kept, dropped


# ---------------------------------------------------------------------- gate

def x_evidence_gate__mutmut_8(preds: list[dict], target: Target) -> tuple[list[dict], list[dict]]:
    """S5. A âncora tem que existir. Predição sem âncora válida é descartada."""
    src = target.lines()
    kept, dropped = [], []
    for p in preds:
        quote = (p.get("evidence_quote") or "XXXX").strip()
        rng = p.get("line_range") or []
        ok = False
        if quote and len(rng) == 2:
            lo, hi = sorted(int(x) for x in rng)
            window = src[max(0, lo - 1) : min(len(src), hi)]
            ok = any(quote in line for line in window)
        (kept if ok else dropped).append(
            p if ok else {**p, "_drop_reason": "citação não encontrada no line_range"}
        )
    return kept, dropped


# ---------------------------------------------------------------------- gate

def x_evidence_gate__mutmut_9(preds: list[dict], target: Target) -> tuple[list[dict], list[dict]]:
    """S5. A âncora tem que existir. Predição sem âncora válida é descartada."""
    src = target.lines()
    kept, dropped = [], []
    for p in preds:
        quote = (p.get("evidence_quote") or "").strip()
        rng = None
        ok = False
        if quote and len(rng) == 2:
            lo, hi = sorted(int(x) for x in rng)
            window = src[max(0, lo - 1) : min(len(src), hi)]
            ok = any(quote in line for line in window)
        (kept if ok else dropped).append(
            p if ok else {**p, "_drop_reason": "citação não encontrada no line_range"}
        )
    return kept, dropped


# ---------------------------------------------------------------------- gate

def x_evidence_gate__mutmut_10(preds: list[dict], target: Target) -> tuple[list[dict], list[dict]]:
    """S5. A âncora tem que existir. Predição sem âncora válida é descartada."""
    src = target.lines()
    kept, dropped = [], []
    for p in preds:
        quote = (p.get("evidence_quote") or "").strip()
        rng = p.get("line_range") and []
        ok = False
        if quote and len(rng) == 2:
            lo, hi = sorted(int(x) for x in rng)
            window = src[max(0, lo - 1) : min(len(src), hi)]
            ok = any(quote in line for line in window)
        (kept if ok else dropped).append(
            p if ok else {**p, "_drop_reason": "citação não encontrada no line_range"}
        )
    return kept, dropped


# ---------------------------------------------------------------------- gate

def x_evidence_gate__mutmut_11(preds: list[dict], target: Target) -> tuple[list[dict], list[dict]]:
    """S5. A âncora tem que existir. Predição sem âncora válida é descartada."""
    src = target.lines()
    kept, dropped = [], []
    for p in preds:
        quote = (p.get("evidence_quote") or "").strip()
        rng = p.get(None) or []
        ok = False
        if quote and len(rng) == 2:
            lo, hi = sorted(int(x) for x in rng)
            window = src[max(0, lo - 1) : min(len(src), hi)]
            ok = any(quote in line for line in window)
        (kept if ok else dropped).append(
            p if ok else {**p, "_drop_reason": "citação não encontrada no line_range"}
        )
    return kept, dropped


# ---------------------------------------------------------------------- gate

def x_evidence_gate__mutmut_12(preds: list[dict], target: Target) -> tuple[list[dict], list[dict]]:
    """S5. A âncora tem que existir. Predição sem âncora válida é descartada."""
    src = target.lines()
    kept, dropped = [], []
    for p in preds:
        quote = (p.get("evidence_quote") or "").strip()
        rng = p.get("XXline_rangeXX") or []
        ok = False
        if quote and len(rng) == 2:
            lo, hi = sorted(int(x) for x in rng)
            window = src[max(0, lo - 1) : min(len(src), hi)]
            ok = any(quote in line for line in window)
        (kept if ok else dropped).append(
            p if ok else {**p, "_drop_reason": "citação não encontrada no line_range"}
        )
    return kept, dropped


# ---------------------------------------------------------------------- gate

def x_evidence_gate__mutmut_13(preds: list[dict], target: Target) -> tuple[list[dict], list[dict]]:
    """S5. A âncora tem que existir. Predição sem âncora válida é descartada."""
    src = target.lines()
    kept, dropped = [], []
    for p in preds:
        quote = (p.get("evidence_quote") or "").strip()
        rng = p.get("LINE_RANGE") or []
        ok = False
        if quote and len(rng) == 2:
            lo, hi = sorted(int(x) for x in rng)
            window = src[max(0, lo - 1) : min(len(src), hi)]
            ok = any(quote in line for line in window)
        (kept if ok else dropped).append(
            p if ok else {**p, "_drop_reason": "citação não encontrada no line_range"}
        )
    return kept, dropped


# ---------------------------------------------------------------------- gate

def x_evidence_gate__mutmut_14(preds: list[dict], target: Target) -> tuple[list[dict], list[dict]]:
    """S5. A âncora tem que existir. Predição sem âncora válida é descartada."""
    src = target.lines()
    kept, dropped = [], []
    for p in preds:
        quote = (p.get("evidence_quote") or "").strip()
        rng = p.get("line_range") or []
        ok = None
        if quote and len(rng) == 2:
            lo, hi = sorted(int(x) for x in rng)
            window = src[max(0, lo - 1) : min(len(src), hi)]
            ok = any(quote in line for line in window)
        (kept if ok else dropped).append(
            p if ok else {**p, "_drop_reason": "citação não encontrada no line_range"}
        )
    return kept, dropped


# ---------------------------------------------------------------------- gate

def x_evidence_gate__mutmut_15(preds: list[dict], target: Target) -> tuple[list[dict], list[dict]]:
    """S5. A âncora tem que existir. Predição sem âncora válida é descartada."""
    src = target.lines()
    kept, dropped = [], []
    for p in preds:
        quote = (p.get("evidence_quote") or "").strip()
        rng = p.get("line_range") or []
        ok = True
        if quote and len(rng) == 2:
            lo, hi = sorted(int(x) for x in rng)
            window = src[max(0, lo - 1) : min(len(src), hi)]
            ok = any(quote in line for line in window)
        (kept if ok else dropped).append(
            p if ok else {**p, "_drop_reason": "citação não encontrada no line_range"}
        )
    return kept, dropped


# ---------------------------------------------------------------------- gate

def x_evidence_gate__mutmut_16(preds: list[dict], target: Target) -> tuple[list[dict], list[dict]]:
    """S5. A âncora tem que existir. Predição sem âncora válida é descartada."""
    src = target.lines()
    kept, dropped = [], []
    for p in preds:
        quote = (p.get("evidence_quote") or "").strip()
        rng = p.get("line_range") or []
        ok = False
        if quote or len(rng) == 2:
            lo, hi = sorted(int(x) for x in rng)
            window = src[max(0, lo - 1) : min(len(src), hi)]
            ok = any(quote in line for line in window)
        (kept if ok else dropped).append(
            p if ok else {**p, "_drop_reason": "citação não encontrada no line_range"}
        )
    return kept, dropped


# ---------------------------------------------------------------------- gate

def x_evidence_gate__mutmut_17(preds: list[dict], target: Target) -> tuple[list[dict], list[dict]]:
    """S5. A âncora tem que existir. Predição sem âncora válida é descartada."""
    src = target.lines()
    kept, dropped = [], []
    for p in preds:
        quote = (p.get("evidence_quote") or "").strip()
        rng = p.get("line_range") or []
        ok = False
        if quote and len(rng) != 2:
            lo, hi = sorted(int(x) for x in rng)
            window = src[max(0, lo - 1) : min(len(src), hi)]
            ok = any(quote in line for line in window)
        (kept if ok else dropped).append(
            p if ok else {**p, "_drop_reason": "citação não encontrada no line_range"}
        )
    return kept, dropped


# ---------------------------------------------------------------------- gate

def x_evidence_gate__mutmut_18(preds: list[dict], target: Target) -> tuple[list[dict], list[dict]]:
    """S5. A âncora tem que existir. Predição sem âncora válida é descartada."""
    src = target.lines()
    kept, dropped = [], []
    for p in preds:
        quote = (p.get("evidence_quote") or "").strip()
        rng = p.get("line_range") or []
        ok = False
        if quote and len(rng) == 3:
            lo, hi = sorted(int(x) for x in rng)
            window = src[max(0, lo - 1) : min(len(src), hi)]
            ok = any(quote in line for line in window)
        (kept if ok else dropped).append(
            p if ok else {**p, "_drop_reason": "citação não encontrada no line_range"}
        )
    return kept, dropped


# ---------------------------------------------------------------------- gate

def x_evidence_gate__mutmut_19(preds: list[dict], target: Target) -> tuple[list[dict], list[dict]]:
    """S5. A âncora tem que existir. Predição sem âncora válida é descartada."""
    src = target.lines()
    kept, dropped = [], []
    for p in preds:
        quote = (p.get("evidence_quote") or "").strip()
        rng = p.get("line_range") or []
        ok = False
        if quote and len(rng) == 2:
            lo, hi = None
            window = src[max(0, lo - 1) : min(len(src), hi)]
            ok = any(quote in line for line in window)
        (kept if ok else dropped).append(
            p if ok else {**p, "_drop_reason": "citação não encontrada no line_range"}
        )
    return kept, dropped


# ---------------------------------------------------------------------- gate

def x_evidence_gate__mutmut_20(preds: list[dict], target: Target) -> tuple[list[dict], list[dict]]:
    """S5. A âncora tem que existir. Predição sem âncora válida é descartada."""
    src = target.lines()
    kept, dropped = [], []
    for p in preds:
        quote = (p.get("evidence_quote") or "").strip()
        rng = p.get("line_range") or []
        ok = False
        if quote and len(rng) == 2:
            lo, hi = sorted(None)
            window = src[max(0, lo - 1) : min(len(src), hi)]
            ok = any(quote in line for line in window)
        (kept if ok else dropped).append(
            p if ok else {**p, "_drop_reason": "citação não encontrada no line_range"}
        )
    return kept, dropped


# ---------------------------------------------------------------------- gate

def x_evidence_gate__mutmut_21(preds: list[dict], target: Target) -> tuple[list[dict], list[dict]]:
    """S5. A âncora tem que existir. Predição sem âncora válida é descartada."""
    src = target.lines()
    kept, dropped = [], []
    for p in preds:
        quote = (p.get("evidence_quote") or "").strip()
        rng = p.get("line_range") or []
        ok = False
        if quote and len(rng) == 2:
            lo, hi = sorted(int(None) for x in rng)
            window = src[max(0, lo - 1) : min(len(src), hi)]
            ok = any(quote in line for line in window)
        (kept if ok else dropped).append(
            p if ok else {**p, "_drop_reason": "citação não encontrada no line_range"}
        )
    return kept, dropped


# ---------------------------------------------------------------------- gate

def x_evidence_gate__mutmut_22(preds: list[dict], target: Target) -> tuple[list[dict], list[dict]]:
    """S5. A âncora tem que existir. Predição sem âncora válida é descartada."""
    src = target.lines()
    kept, dropped = [], []
    for p in preds:
        quote = (p.get("evidence_quote") or "").strip()
        rng = p.get("line_range") or []
        ok = False
        if quote and len(rng) == 2:
            lo, hi = sorted(int(x) for x in rng)
            window = None
            ok = any(quote in line for line in window)
        (kept if ok else dropped).append(
            p if ok else {**p, "_drop_reason": "citação não encontrada no line_range"}
        )
    return kept, dropped


# ---------------------------------------------------------------------- gate

def x_evidence_gate__mutmut_23(preds: list[dict], target: Target) -> tuple[list[dict], list[dict]]:
    """S5. A âncora tem que existir. Predição sem âncora válida é descartada."""
    src = target.lines()
    kept, dropped = [], []
    for p in preds:
        quote = (p.get("evidence_quote") or "").strip()
        rng = p.get("line_range") or []
        ok = False
        if quote and len(rng) == 2:
            lo, hi = sorted(int(x) for x in rng)
            window = src[max(None, lo - 1) : min(len(src), hi)]
            ok = any(quote in line for line in window)
        (kept if ok else dropped).append(
            p if ok else {**p, "_drop_reason": "citação não encontrada no line_range"}
        )
    return kept, dropped


# ---------------------------------------------------------------------- gate

def x_evidence_gate__mutmut_24(preds: list[dict], target: Target) -> tuple[list[dict], list[dict]]:
    """S5. A âncora tem que existir. Predição sem âncora válida é descartada."""
    src = target.lines()
    kept, dropped = [], []
    for p in preds:
        quote = (p.get("evidence_quote") or "").strip()
        rng = p.get("line_range") or []
        ok = False
        if quote and len(rng) == 2:
            lo, hi = sorted(int(x) for x in rng)
            window = src[max(0, None) : min(len(src), hi)]
            ok = any(quote in line for line in window)
        (kept if ok else dropped).append(
            p if ok else {**p, "_drop_reason": "citação não encontrada no line_range"}
        )
    return kept, dropped


# ---------------------------------------------------------------------- gate

def x_evidence_gate__mutmut_25(preds: list[dict], target: Target) -> tuple[list[dict], list[dict]]:
    """S5. A âncora tem que existir. Predição sem âncora válida é descartada."""
    src = target.lines()
    kept, dropped = [], []
    for p in preds:
        quote = (p.get("evidence_quote") or "").strip()
        rng = p.get("line_range") or []
        ok = False
        if quote and len(rng) == 2:
            lo, hi = sorted(int(x) for x in rng)
            window = src[max(lo - 1) : min(len(src), hi)]
            ok = any(quote in line for line in window)
        (kept if ok else dropped).append(
            p if ok else {**p, "_drop_reason": "citação não encontrada no line_range"}
        )
    return kept, dropped


# ---------------------------------------------------------------------- gate

def x_evidence_gate__mutmut_26(preds: list[dict], target: Target) -> tuple[list[dict], list[dict]]:
    """S5. A âncora tem que existir. Predição sem âncora válida é descartada."""
    src = target.lines()
    kept, dropped = [], []
    for p in preds:
        quote = (p.get("evidence_quote") or "").strip()
        rng = p.get("line_range") or []
        ok = False
        if quote and len(rng) == 2:
            lo, hi = sorted(int(x) for x in rng)
            window = src[max(0, ) : min(len(src), hi)]
            ok = any(quote in line for line in window)
        (kept if ok else dropped).append(
            p if ok else {**p, "_drop_reason": "citação não encontrada no line_range"}
        )
    return kept, dropped


# ---------------------------------------------------------------------- gate

def x_evidence_gate__mutmut_27(preds: list[dict], target: Target) -> tuple[list[dict], list[dict]]:
    """S5. A âncora tem que existir. Predição sem âncora válida é descartada."""
    src = target.lines()
    kept, dropped = [], []
    for p in preds:
        quote = (p.get("evidence_quote") or "").strip()
        rng = p.get("line_range") or []
        ok = False
        if quote and len(rng) == 2:
            lo, hi = sorted(int(x) for x in rng)
            window = src[max(1, lo - 1) : min(len(src), hi)]
            ok = any(quote in line for line in window)
        (kept if ok else dropped).append(
            p if ok else {**p, "_drop_reason": "citação não encontrada no line_range"}
        )
    return kept, dropped


# ---------------------------------------------------------------------- gate

def x_evidence_gate__mutmut_28(preds: list[dict], target: Target) -> tuple[list[dict], list[dict]]:
    """S5. A âncora tem que existir. Predição sem âncora válida é descartada."""
    src = target.lines()
    kept, dropped = [], []
    for p in preds:
        quote = (p.get("evidence_quote") or "").strip()
        rng = p.get("line_range") or []
        ok = False
        if quote and len(rng) == 2:
            lo, hi = sorted(int(x) for x in rng)
            window = src[max(0, lo + 1) : min(len(src), hi)]
            ok = any(quote in line for line in window)
        (kept if ok else dropped).append(
            p if ok else {**p, "_drop_reason": "citação não encontrada no line_range"}
        )
    return kept, dropped


# ---------------------------------------------------------------------- gate

def x_evidence_gate__mutmut_29(preds: list[dict], target: Target) -> tuple[list[dict], list[dict]]:
    """S5. A âncora tem que existir. Predição sem âncora válida é descartada."""
    src = target.lines()
    kept, dropped = [], []
    for p in preds:
        quote = (p.get("evidence_quote") or "").strip()
        rng = p.get("line_range") or []
        ok = False
        if quote and len(rng) == 2:
            lo, hi = sorted(int(x) for x in rng)
            window = src[max(0, lo - 2) : min(len(src), hi)]
            ok = any(quote in line for line in window)
        (kept if ok else dropped).append(
            p if ok else {**p, "_drop_reason": "citação não encontrada no line_range"}
        )
    return kept, dropped


# ---------------------------------------------------------------------- gate

def x_evidence_gate__mutmut_30(preds: list[dict], target: Target) -> tuple[list[dict], list[dict]]:
    """S5. A âncora tem que existir. Predição sem âncora válida é descartada."""
    src = target.lines()
    kept, dropped = [], []
    for p in preds:
        quote = (p.get("evidence_quote") or "").strip()
        rng = p.get("line_range") or []
        ok = False
        if quote and len(rng) == 2:
            lo, hi = sorted(int(x) for x in rng)
            window = src[max(0, lo - 1) : min(None, hi)]
            ok = any(quote in line for line in window)
        (kept if ok else dropped).append(
            p if ok else {**p, "_drop_reason": "citação não encontrada no line_range"}
        )
    return kept, dropped


# ---------------------------------------------------------------------- gate

def x_evidence_gate__mutmut_31(preds: list[dict], target: Target) -> tuple[list[dict], list[dict]]:
    """S5. A âncora tem que existir. Predição sem âncora válida é descartada."""
    src = target.lines()
    kept, dropped = [], []
    for p in preds:
        quote = (p.get("evidence_quote") or "").strip()
        rng = p.get("line_range") or []
        ok = False
        if quote and len(rng) == 2:
            lo, hi = sorted(int(x) for x in rng)
            window = src[max(0, lo - 1) : min(len(src), None)]
            ok = any(quote in line for line in window)
        (kept if ok else dropped).append(
            p if ok else {**p, "_drop_reason": "citação não encontrada no line_range"}
        )
    return kept, dropped


# ---------------------------------------------------------------------- gate

def x_evidence_gate__mutmut_32(preds: list[dict], target: Target) -> tuple[list[dict], list[dict]]:
    """S5. A âncora tem que existir. Predição sem âncora válida é descartada."""
    src = target.lines()
    kept, dropped = [], []
    for p in preds:
        quote = (p.get("evidence_quote") or "").strip()
        rng = p.get("line_range") or []
        ok = False
        if quote and len(rng) == 2:
            lo, hi = sorted(int(x) for x in rng)
            window = src[max(0, lo - 1) : min(hi)]
            ok = any(quote in line for line in window)
        (kept if ok else dropped).append(
            p if ok else {**p, "_drop_reason": "citação não encontrada no line_range"}
        )
    return kept, dropped


# ---------------------------------------------------------------------- gate

def x_evidence_gate__mutmut_33(preds: list[dict], target: Target) -> tuple[list[dict], list[dict]]:
    """S5. A âncora tem que existir. Predição sem âncora válida é descartada."""
    src = target.lines()
    kept, dropped = [], []
    for p in preds:
        quote = (p.get("evidence_quote") or "").strip()
        rng = p.get("line_range") or []
        ok = False
        if quote and len(rng) == 2:
            lo, hi = sorted(int(x) for x in rng)
            window = src[max(0, lo - 1) : min(len(src), )]
            ok = any(quote in line for line in window)
        (kept if ok else dropped).append(
            p if ok else {**p, "_drop_reason": "citação não encontrada no line_range"}
        )
    return kept, dropped


# ---------------------------------------------------------------------- gate

def x_evidence_gate__mutmut_34(preds: list[dict], target: Target) -> tuple[list[dict], list[dict]]:
    """S5. A âncora tem que existir. Predição sem âncora válida é descartada."""
    src = target.lines()
    kept, dropped = [], []
    for p in preds:
        quote = (p.get("evidence_quote") or "").strip()
        rng = p.get("line_range") or []
        ok = False
        if quote and len(rng) == 2:
            lo, hi = sorted(int(x) for x in rng)
            window = src[max(0, lo - 1) : min(len(src), hi)]
            ok = None
        (kept if ok else dropped).append(
            p if ok else {**p, "_drop_reason": "citação não encontrada no line_range"}
        )
    return kept, dropped


# ---------------------------------------------------------------------- gate

def x_evidence_gate__mutmut_35(preds: list[dict], target: Target) -> tuple[list[dict], list[dict]]:
    """S5. A âncora tem que existir. Predição sem âncora válida é descartada."""
    src = target.lines()
    kept, dropped = [], []
    for p in preds:
        quote = (p.get("evidence_quote") or "").strip()
        rng = p.get("line_range") or []
        ok = False
        if quote and len(rng) == 2:
            lo, hi = sorted(int(x) for x in rng)
            window = src[max(0, lo - 1) : min(len(src), hi)]
            ok = any(None)
        (kept if ok else dropped).append(
            p if ok else {**p, "_drop_reason": "citação não encontrada no line_range"}
        )
    return kept, dropped


# ---------------------------------------------------------------------- gate

def x_evidence_gate__mutmut_36(preds: list[dict], target: Target) -> tuple[list[dict], list[dict]]:
    """S5. A âncora tem que existir. Predição sem âncora válida é descartada."""
    src = target.lines()
    kept, dropped = [], []
    for p in preds:
        quote = (p.get("evidence_quote") or "").strip()
        rng = p.get("line_range") or []
        ok = False
        if quote and len(rng) == 2:
            lo, hi = sorted(int(x) for x in rng)
            window = src[max(0, lo - 1) : min(len(src), hi)]
            ok = any(quote not in line for line in window)
        (kept if ok else dropped).append(
            p if ok else {**p, "_drop_reason": "citação não encontrada no line_range"}
        )
    return kept, dropped


# ---------------------------------------------------------------------- gate

def x_evidence_gate__mutmut_37(preds: list[dict], target: Target) -> tuple[list[dict], list[dict]]:
    """S5. A âncora tem que existir. Predição sem âncora válida é descartada."""
    src = target.lines()
    kept, dropped = [], []
    for p in preds:
        quote = (p.get("evidence_quote") or "").strip()
        rng = p.get("line_range") or []
        ok = False
        if quote and len(rng) == 2:
            lo, hi = sorted(int(x) for x in rng)
            window = src[max(0, lo - 1) : min(len(src), hi)]
            ok = any(quote in line for line in window)
        (kept if ok else dropped).append(
            None
        )
    return kept, dropped


# ---------------------------------------------------------------------- gate

def x_evidence_gate__mutmut_38(preds: list[dict], target: Target) -> tuple[list[dict], list[dict]]:
    """S5. A âncora tem que existir. Predição sem âncora válida é descartada."""
    src = target.lines()
    kept, dropped = [], []
    for p in preds:
        quote = (p.get("evidence_quote") or "").strip()
        rng = p.get("line_range") or []
        ok = False
        if quote and len(rng) == 2:
            lo, hi = sorted(int(x) for x in rng)
            window = src[max(0, lo - 1) : min(len(src), hi)]
            ok = any(quote in line for line in window)
        (kept if ok else dropped).append(
            p if ok else {**p, "XX_drop_reasonXX": "citação não encontrada no line_range"}
        )
    return kept, dropped


# ---------------------------------------------------------------------- gate

def x_evidence_gate__mutmut_39(preds: list[dict], target: Target) -> tuple[list[dict], list[dict]]:
    """S5. A âncora tem que existir. Predição sem âncora válida é descartada."""
    src = target.lines()
    kept, dropped = [], []
    for p in preds:
        quote = (p.get("evidence_quote") or "").strip()
        rng = p.get("line_range") or []
        ok = False
        if quote and len(rng) == 2:
            lo, hi = sorted(int(x) for x in rng)
            window = src[max(0, lo - 1) : min(len(src), hi)]
            ok = any(quote in line for line in window)
        (kept if ok else dropped).append(
            p if ok else {**p, "_DROP_REASON": "citação não encontrada no line_range"}
        )
    return kept, dropped


# ---------------------------------------------------------------------- gate

def x_evidence_gate__mutmut_40(preds: list[dict], target: Target) -> tuple[list[dict], list[dict]]:
    """S5. A âncora tem que existir. Predição sem âncora válida é descartada."""
    src = target.lines()
    kept, dropped = [], []
    for p in preds:
        quote = (p.get("evidence_quote") or "").strip()
        rng = p.get("line_range") or []
        ok = False
        if quote and len(rng) == 2:
            lo, hi = sorted(int(x) for x in rng)
            window = src[max(0, lo - 1) : min(len(src), hi)]
            ok = any(quote in line for line in window)
        (kept if ok else dropped).append(
            p if ok else {**p, "_drop_reason": "XXcitação não encontrada no line_rangeXX"}
        )
    return kept, dropped


# ---------------------------------------------------------------------- gate

def x_evidence_gate__mutmut_41(preds: list[dict], target: Target) -> tuple[list[dict], list[dict]]:
    """S5. A âncora tem que existir. Predição sem âncora válida é descartada."""
    src = target.lines()
    kept, dropped = [], []
    for p in preds:
        quote = (p.get("evidence_quote") or "").strip()
        rng = p.get("line_range") or []
        ok = False
        if quote and len(rng) == 2:
            lo, hi = sorted(int(x) for x in rng)
            window = src[max(0, lo - 1) : min(len(src), hi)]
            ok = any(quote in line for line in window)
        (kept if ok else dropped).append(
            p if ok else {**p, "_drop_reason": "CITAÇÃO NÃO ENCONTRADA NO LINE_RANGE"}
        )
    return kept, dropped

mutants_x_evidence_gate__mutmut['_mutmut_orig'] = x_evidence_gate__mutmut_orig # type: ignore # mutmut generated
mutants_x_evidence_gate__mutmut['x_evidence_gate__mutmut_1'] = x_evidence_gate__mutmut_1 # type: ignore # mutmut generated
mutants_x_evidence_gate__mutmut['x_evidence_gate__mutmut_2'] = x_evidence_gate__mutmut_2 # type: ignore # mutmut generated
mutants_x_evidence_gate__mutmut['x_evidence_gate__mutmut_3'] = x_evidence_gate__mutmut_3 # type: ignore # mutmut generated
mutants_x_evidence_gate__mutmut['x_evidence_gate__mutmut_4'] = x_evidence_gate__mutmut_4 # type: ignore # mutmut generated
mutants_x_evidence_gate__mutmut['x_evidence_gate__mutmut_5'] = x_evidence_gate__mutmut_5 # type: ignore # mutmut generated
mutants_x_evidence_gate__mutmut['x_evidence_gate__mutmut_6'] = x_evidence_gate__mutmut_6 # type: ignore # mutmut generated
mutants_x_evidence_gate__mutmut['x_evidence_gate__mutmut_7'] = x_evidence_gate__mutmut_7 # type: ignore # mutmut generated
mutants_x_evidence_gate__mutmut['x_evidence_gate__mutmut_8'] = x_evidence_gate__mutmut_8 # type: ignore # mutmut generated
mutants_x_evidence_gate__mutmut['x_evidence_gate__mutmut_9'] = x_evidence_gate__mutmut_9 # type: ignore # mutmut generated
mutants_x_evidence_gate__mutmut['x_evidence_gate__mutmut_10'] = x_evidence_gate__mutmut_10 # type: ignore # mutmut generated
mutants_x_evidence_gate__mutmut['x_evidence_gate__mutmut_11'] = x_evidence_gate__mutmut_11 # type: ignore # mutmut generated
mutants_x_evidence_gate__mutmut['x_evidence_gate__mutmut_12'] = x_evidence_gate__mutmut_12 # type: ignore # mutmut generated
mutants_x_evidence_gate__mutmut['x_evidence_gate__mutmut_13'] = x_evidence_gate__mutmut_13 # type: ignore # mutmut generated
mutants_x_evidence_gate__mutmut['x_evidence_gate__mutmut_14'] = x_evidence_gate__mutmut_14 # type: ignore # mutmut generated
mutants_x_evidence_gate__mutmut['x_evidence_gate__mutmut_15'] = x_evidence_gate__mutmut_15 # type: ignore # mutmut generated
mutants_x_evidence_gate__mutmut['x_evidence_gate__mutmut_16'] = x_evidence_gate__mutmut_16 # type: ignore # mutmut generated
mutants_x_evidence_gate__mutmut['x_evidence_gate__mutmut_17'] = x_evidence_gate__mutmut_17 # type: ignore # mutmut generated
mutants_x_evidence_gate__mutmut['x_evidence_gate__mutmut_18'] = x_evidence_gate__mutmut_18 # type: ignore # mutmut generated
mutants_x_evidence_gate__mutmut['x_evidence_gate__mutmut_19'] = x_evidence_gate__mutmut_19 # type: ignore # mutmut generated
mutants_x_evidence_gate__mutmut['x_evidence_gate__mutmut_20'] = x_evidence_gate__mutmut_20 # type: ignore # mutmut generated
mutants_x_evidence_gate__mutmut['x_evidence_gate__mutmut_21'] = x_evidence_gate__mutmut_21 # type: ignore # mutmut generated
mutants_x_evidence_gate__mutmut['x_evidence_gate__mutmut_22'] = x_evidence_gate__mutmut_22 # type: ignore # mutmut generated
mutants_x_evidence_gate__mutmut['x_evidence_gate__mutmut_23'] = x_evidence_gate__mutmut_23 # type: ignore # mutmut generated
mutants_x_evidence_gate__mutmut['x_evidence_gate__mutmut_24'] = x_evidence_gate__mutmut_24 # type: ignore # mutmut generated
mutants_x_evidence_gate__mutmut['x_evidence_gate__mutmut_25'] = x_evidence_gate__mutmut_25 # type: ignore # mutmut generated
mutants_x_evidence_gate__mutmut['x_evidence_gate__mutmut_26'] = x_evidence_gate__mutmut_26 # type: ignore # mutmut generated
mutants_x_evidence_gate__mutmut['x_evidence_gate__mutmut_27'] = x_evidence_gate__mutmut_27 # type: ignore # mutmut generated
mutants_x_evidence_gate__mutmut['x_evidence_gate__mutmut_28'] = x_evidence_gate__mutmut_28 # type: ignore # mutmut generated
mutants_x_evidence_gate__mutmut['x_evidence_gate__mutmut_29'] = x_evidence_gate__mutmut_29 # type: ignore # mutmut generated
mutants_x_evidence_gate__mutmut['x_evidence_gate__mutmut_30'] = x_evidence_gate__mutmut_30 # type: ignore # mutmut generated
mutants_x_evidence_gate__mutmut['x_evidence_gate__mutmut_31'] = x_evidence_gate__mutmut_31 # type: ignore # mutmut generated
mutants_x_evidence_gate__mutmut['x_evidence_gate__mutmut_32'] = x_evidence_gate__mutmut_32 # type: ignore # mutmut generated
mutants_x_evidence_gate__mutmut['x_evidence_gate__mutmut_33'] = x_evidence_gate__mutmut_33 # type: ignore # mutmut generated
mutants_x_evidence_gate__mutmut['x_evidence_gate__mutmut_34'] = x_evidence_gate__mutmut_34 # type: ignore # mutmut generated
mutants_x_evidence_gate__mutmut['x_evidence_gate__mutmut_35'] = x_evidence_gate__mutmut_35 # type: ignore # mutmut generated
mutants_x_evidence_gate__mutmut['x_evidence_gate__mutmut_36'] = x_evidence_gate__mutmut_36 # type: ignore # mutmut generated
mutants_x_evidence_gate__mutmut['x_evidence_gate__mutmut_37'] = x_evidence_gate__mutmut_37 # type: ignore # mutmut generated
mutants_x_evidence_gate__mutmut['x_evidence_gate__mutmut_38'] = x_evidence_gate__mutmut_38 # type: ignore # mutmut generated
mutants_x_evidence_gate__mutmut['x_evidence_gate__mutmut_39'] = x_evidence_gate__mutmut_39 # type: ignore # mutmut generated
mutants_x_evidence_gate__mutmut['x_evidence_gate__mutmut_40'] = x_evidence_gate__mutmut_40 # type: ignore # mutmut generated
mutants_x_evidence_gate__mutmut['x_evidence_gate__mutmut_41'] = x_evidence_gate__mutmut_41 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_reconcile__mutmut)
def reconcile(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_orig(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_1(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = None
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_2(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = None
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_3(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") and []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_4(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get(None) or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_5(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("XXline_rangeXX") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_6(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("LINE_RANGE") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_7(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) == 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_8(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 3:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_9(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            break
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_10(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = None
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_11(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get(None, ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_12(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", None), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_13(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get(""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_14(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_15(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("XXfileXX", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_16(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("FILE", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_17(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", "XXXX"), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_18(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get(None, ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_19(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", None))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_20(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get(""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_21(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_22(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("XXblind_spot_typeXX", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_23(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("BLIND_SPOT_TYPE", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_24(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", "XXXX"))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_25(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(None)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_26(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(None, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_27(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, None).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_28(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault([]).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_29(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, ).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_30(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = None
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_31(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=None)
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_32(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: None)
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_33(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(None))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_34(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(None) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_35(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["XXline_rangeXX"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_36(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["LINE_RANGE"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_37(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = None
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_38(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = None
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_39(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(None)
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_40(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(None) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_41(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["XXline_rangeXX"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_42(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["LINE_RANGE"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_43(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = None
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_44(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[+1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_45(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-2]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_46(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["XXline_rangeXX"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_47(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["LINE_RANGE"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_48(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo < mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_49(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi - 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_50(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 2:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_51(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = None
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_52(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[+1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_53(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-2]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_54(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = None
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_55(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["XXline_rangeXX"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_56(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["LINE_RANGE"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_57(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(None, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_58(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, None)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_59(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_60(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, )]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_61(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(None) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_62(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get(None, 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_63(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", None)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_64(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get(0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_65(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", )) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_66(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("XXconfidenceXX", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_67(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("CONFIDENCE", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_68(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 1)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_69(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) >= float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_70(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(None):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_71(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get(None, 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_72(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", None)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_73(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get(0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_74(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", )):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_75(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("XXconfidenceXX", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_76(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("CONFIDENCE", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_77(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 1)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_78(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = None
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_79(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["XXevidence_quoteXX"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_80(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["EVIDENCE_QUOTE"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_81(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get(None, "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_82(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", None)
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_83(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_84(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", )
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_85(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("XXevidence_quoteXX", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_86(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("EVIDENCE_QUOTE", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_87(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "XXXX")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_88(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = None
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_89(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["XXconfidenceXX"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_90(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["CONFIDENCE"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_91(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get(None, 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_92(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", None)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_93(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get(0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_94(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", )
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_95(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("XXconfidenceXX", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_96(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("CONFIDENCE", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_97(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 1)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_98(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = None
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_99(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["XXrationaleXX"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_100(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["RATIONALE"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_101(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get(None, "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_102(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", None)
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_103(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_104(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", )
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_105(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("XXrationaleXX", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_106(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("RATIONALE", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_107(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "XXXX")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_108(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = None
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_109(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["XX_mergedXX"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_110(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_MERGED"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_111(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) - 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_112(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get(None, 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_113(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", None) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_114(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get(1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_115(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", ) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_116(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("XX_mergedXX", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_117(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_MERGED", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_118(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 2) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_119(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 2
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_120(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    break
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_121(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append(None)
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_122(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "XXfileXX": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_123(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "FILE": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_124(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "XXblind_spot_typeXX": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_125(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "BLIND_SPOT_TYPE": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_126(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "XXline_rangeXX": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_127(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "LINE_RANGE": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_128(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(None)
    return sorted(out, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_129(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(None, key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_130(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=None)


def x_reconcile__mutmut_131(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(key=lambda p: (p["file"], p["line_range"]))


def x_reconcile__mutmut_132(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, )


def x_reconcile__mutmut_133(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: None)


def x_reconcile__mutmut_134(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["XXfileXX"], p["line_range"]))


def x_reconcile__mutmut_135(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["FILE"], p["line_range"]))


def x_reconcile__mutmut_136(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["XXline_rangeXX"]))


def x_reconcile__mutmut_137(preds: list[dict]) -> list[dict]:
    """S6. Funde predições sobrepostas do mesmo arquivo e tipo; mantém a maior confiança."""
    by_key: dict[tuple[str, str], list[dict]] = {}
    for p in preds:
        rng = p.get("line_range") or []
        if len(rng) != 2:
            continue
        key = (p.get("file", ""), p.get("blind_spot_type", ""))
        by_key.setdefault(key, []).append(p)

    out: list[dict] = []
    for (file, btype), group in by_key.items():
        group.sort(key=lambda p: sorted(int(x) for x in p["line_range"]))
        merged: list[dict] = []
        for p in group:
            lo, hi = sorted(int(x) for x in p["line_range"])
            if merged:
                mlo, mhi = merged[-1]["line_range"]
                if lo <= mhi + 1:  # sobreposto ou adjacente
                    prev = merged[-1]
                    prev["line_range"] = [mlo, max(mhi, hi)]
                    if float(p.get("confidence", 0)) > float(prev.get("confidence", 0)):
                        prev["evidence_quote"] = p.get("evidence_quote", "")
                        prev["confidence"] = p.get("confidence", 0)
                        prev["rationale"] = p.get("rationale", "")
                    prev["_merged"] = prev.get("_merged", 1) + 1
                    continue
            merged.append({**p, "file": file, "blind_spot_type": btype, "line_range": [lo, hi]})
        out.extend(merged)
    return sorted(out, key=lambda p: (p["file"], p["LINE_RANGE"]))

mutants_x_reconcile__mutmut['_mutmut_orig'] = x_reconcile__mutmut_orig # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_1'] = x_reconcile__mutmut_1 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_2'] = x_reconcile__mutmut_2 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_3'] = x_reconcile__mutmut_3 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_4'] = x_reconcile__mutmut_4 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_5'] = x_reconcile__mutmut_5 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_6'] = x_reconcile__mutmut_6 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_7'] = x_reconcile__mutmut_7 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_8'] = x_reconcile__mutmut_8 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_9'] = x_reconcile__mutmut_9 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_10'] = x_reconcile__mutmut_10 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_11'] = x_reconcile__mutmut_11 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_12'] = x_reconcile__mutmut_12 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_13'] = x_reconcile__mutmut_13 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_14'] = x_reconcile__mutmut_14 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_15'] = x_reconcile__mutmut_15 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_16'] = x_reconcile__mutmut_16 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_17'] = x_reconcile__mutmut_17 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_18'] = x_reconcile__mutmut_18 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_19'] = x_reconcile__mutmut_19 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_20'] = x_reconcile__mutmut_20 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_21'] = x_reconcile__mutmut_21 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_22'] = x_reconcile__mutmut_22 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_23'] = x_reconcile__mutmut_23 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_24'] = x_reconcile__mutmut_24 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_25'] = x_reconcile__mutmut_25 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_26'] = x_reconcile__mutmut_26 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_27'] = x_reconcile__mutmut_27 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_28'] = x_reconcile__mutmut_28 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_29'] = x_reconcile__mutmut_29 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_30'] = x_reconcile__mutmut_30 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_31'] = x_reconcile__mutmut_31 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_32'] = x_reconcile__mutmut_32 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_33'] = x_reconcile__mutmut_33 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_34'] = x_reconcile__mutmut_34 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_35'] = x_reconcile__mutmut_35 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_36'] = x_reconcile__mutmut_36 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_37'] = x_reconcile__mutmut_37 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_38'] = x_reconcile__mutmut_38 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_39'] = x_reconcile__mutmut_39 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_40'] = x_reconcile__mutmut_40 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_41'] = x_reconcile__mutmut_41 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_42'] = x_reconcile__mutmut_42 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_43'] = x_reconcile__mutmut_43 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_44'] = x_reconcile__mutmut_44 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_45'] = x_reconcile__mutmut_45 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_46'] = x_reconcile__mutmut_46 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_47'] = x_reconcile__mutmut_47 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_48'] = x_reconcile__mutmut_48 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_49'] = x_reconcile__mutmut_49 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_50'] = x_reconcile__mutmut_50 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_51'] = x_reconcile__mutmut_51 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_52'] = x_reconcile__mutmut_52 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_53'] = x_reconcile__mutmut_53 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_54'] = x_reconcile__mutmut_54 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_55'] = x_reconcile__mutmut_55 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_56'] = x_reconcile__mutmut_56 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_57'] = x_reconcile__mutmut_57 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_58'] = x_reconcile__mutmut_58 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_59'] = x_reconcile__mutmut_59 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_60'] = x_reconcile__mutmut_60 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_61'] = x_reconcile__mutmut_61 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_62'] = x_reconcile__mutmut_62 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_63'] = x_reconcile__mutmut_63 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_64'] = x_reconcile__mutmut_64 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_65'] = x_reconcile__mutmut_65 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_66'] = x_reconcile__mutmut_66 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_67'] = x_reconcile__mutmut_67 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_68'] = x_reconcile__mutmut_68 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_69'] = x_reconcile__mutmut_69 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_70'] = x_reconcile__mutmut_70 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_71'] = x_reconcile__mutmut_71 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_72'] = x_reconcile__mutmut_72 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_73'] = x_reconcile__mutmut_73 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_74'] = x_reconcile__mutmut_74 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_75'] = x_reconcile__mutmut_75 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_76'] = x_reconcile__mutmut_76 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_77'] = x_reconcile__mutmut_77 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_78'] = x_reconcile__mutmut_78 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_79'] = x_reconcile__mutmut_79 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_80'] = x_reconcile__mutmut_80 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_81'] = x_reconcile__mutmut_81 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_82'] = x_reconcile__mutmut_82 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_83'] = x_reconcile__mutmut_83 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_84'] = x_reconcile__mutmut_84 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_85'] = x_reconcile__mutmut_85 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_86'] = x_reconcile__mutmut_86 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_87'] = x_reconcile__mutmut_87 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_88'] = x_reconcile__mutmut_88 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_89'] = x_reconcile__mutmut_89 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_90'] = x_reconcile__mutmut_90 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_91'] = x_reconcile__mutmut_91 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_92'] = x_reconcile__mutmut_92 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_93'] = x_reconcile__mutmut_93 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_94'] = x_reconcile__mutmut_94 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_95'] = x_reconcile__mutmut_95 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_96'] = x_reconcile__mutmut_96 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_97'] = x_reconcile__mutmut_97 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_98'] = x_reconcile__mutmut_98 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_99'] = x_reconcile__mutmut_99 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_100'] = x_reconcile__mutmut_100 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_101'] = x_reconcile__mutmut_101 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_102'] = x_reconcile__mutmut_102 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_103'] = x_reconcile__mutmut_103 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_104'] = x_reconcile__mutmut_104 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_105'] = x_reconcile__mutmut_105 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_106'] = x_reconcile__mutmut_106 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_107'] = x_reconcile__mutmut_107 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_108'] = x_reconcile__mutmut_108 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_109'] = x_reconcile__mutmut_109 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_110'] = x_reconcile__mutmut_110 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_111'] = x_reconcile__mutmut_111 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_112'] = x_reconcile__mutmut_112 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_113'] = x_reconcile__mutmut_113 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_114'] = x_reconcile__mutmut_114 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_115'] = x_reconcile__mutmut_115 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_116'] = x_reconcile__mutmut_116 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_117'] = x_reconcile__mutmut_117 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_118'] = x_reconcile__mutmut_118 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_119'] = x_reconcile__mutmut_119 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_120'] = x_reconcile__mutmut_120 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_121'] = x_reconcile__mutmut_121 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_122'] = x_reconcile__mutmut_122 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_123'] = x_reconcile__mutmut_123 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_124'] = x_reconcile__mutmut_124 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_125'] = x_reconcile__mutmut_125 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_126'] = x_reconcile__mutmut_126 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_127'] = x_reconcile__mutmut_127 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_128'] = x_reconcile__mutmut_128 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_129'] = x_reconcile__mutmut_129 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_130'] = x_reconcile__mutmut_130 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_131'] = x_reconcile__mutmut_131 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_132'] = x_reconcile__mutmut_132 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_133'] = x_reconcile__mutmut_133 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_134'] = x_reconcile__mutmut_134 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_135'] = x_reconcile__mutmut_135 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_136'] = x_reconcile__mutmut_136 # type: ignore # mutmut generated
mutants_x_reconcile__mutmut['x_reconcile__mutmut_137'] = x_reconcile__mutmut_137 # type: ignore # mutmut generated
mutants_x_run__mutmut: MutantDict = {}  # type: ignore


# ----------------------------------------------------------------- execução

@_mutmut_mutated(mutants_x_run__mutmut)
def run(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_orig(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_1(stage: str, set_name: str, client: Client) -> dict:
    cfg = None
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_2(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = None
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_3(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = None
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_4(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS * cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_5(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["XXsystemXX"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_6(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["SYSTEM"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_7(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = None
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_8(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["XXtest_fileXX"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_9(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["TEST_FILE"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_10(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = None

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_11(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] * test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_12(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS * spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_13(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["XXcorpusXX"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_14(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["CORPUS"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_15(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = None
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_16(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = None
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_17(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = None

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_18(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["XXfilesXX"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_19(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["FILES"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_20(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = None

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_21(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(None, file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_22(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], None)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_23(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_24(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], )

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_25(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["XXcorpusXX"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_26(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["CORPUS"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_27(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["XXsweepXX"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_28(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["SWEEP"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_29(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = None
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_30(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS * "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_31(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "XXuser_function.mdXX").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_32(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "USER_FUNCTION.MD").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_33(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = None
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_34(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = None
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_35(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_36(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = None
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_37(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("XX<module>XX", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_38(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<MODULE>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_39(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 2, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_40(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = None
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_41(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(None)
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_42(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "XX\nXX".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_43(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start + 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_44(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 2 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_45(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = None
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_46(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=None, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_47(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=None, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_48(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=None, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_49(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=None,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_50(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=None, test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_51(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=None, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_52(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=None,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_53(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_54(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_55(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_56(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_57(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_58(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_59(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_60(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(None, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_61(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=None), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_62(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_63(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, ), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_64(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = None
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_65(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(None, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_66(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, None, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_67(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=None, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_68(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=None)
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_69(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_70(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_71(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_72(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, )
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_73(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = None
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_74(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(None)
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_75(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(None))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_76(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = None
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_77(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS * "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_78(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "XXuser_whole_file.mdXX").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_79(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "USER_WHOLE_FILE.MD").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_80(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = None
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_81(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=None, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_82(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=None, test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_83(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=None, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_84(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=None
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_85(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_86(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_87(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_88(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_89(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(None), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_90(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = None
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_91(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(None, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_92(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, None, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_93(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=None, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_94(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=None)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_95(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_96(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_97(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_98(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, )
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_99(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = None
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_100(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(None)

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_101(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(None))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_102(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = None
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_103(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(None).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_104(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["XXfilesXX"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_105(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["FILES"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_106(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = None

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_107(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["XXfileXX"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_108(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["FILE"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_109(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(None, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_110(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, None)

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_111(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_112(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, )

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_113(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(None).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_114(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(None)).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_115(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get(None, ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_116(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", None))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_117(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get(""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_118(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_119(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("XXfileXX", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_120(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("FILE", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_121(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", "XXXX"))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_122(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get(None))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_123(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("XXfileXX"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_124(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("FILE"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_125(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["XXgateXX"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_126(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["GATE"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_127(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = None
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_128(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["XXfilesXX"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_129(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["FILES"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_130(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = None
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_131(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(None, file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_132(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], None)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_133(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_134(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], )
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_135(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["XXcorpusXX"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_136(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["CORPUS"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_137(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = None
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_138(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate(None, target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_139(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], None)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_140(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate(target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_141(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], )
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_142(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get(None) == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_143(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("XXfileXX") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_144(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("FILE") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_145(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") != file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_146(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(None)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_147(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(None)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_148(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend(None)
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_149(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get(None) not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_150(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("XXfileXX") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_151(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("FILE") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_152(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_153(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(None)])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_154(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["XXfilesXX"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_155(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["FILES"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_156(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = None

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_157(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["XXsweepXX"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_158(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["SWEEP"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_159(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = None

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_160(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(None)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_161(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = None
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_162(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        None
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_163(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "XXstageXX": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_164(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "STAGE": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_165(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "XXgate_appliedXX": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_166(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "GATE_APPLIED": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_167(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["XXgateXX"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_168(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["GATE"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_169(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "XXsweep_appliedXX": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_170(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "SWEEP_APPLIED": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_171(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["XXsweepXX"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_172(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["SWEEP"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_173(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "XXn_dropped_by_gateXX": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_174(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "N_DROPPED_BY_GATE": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_175(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "XXtypes_off_taxonomyXX": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_176(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "TYPES_OFF_TAXONOMY": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_177(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                None
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_178(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY + {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_179(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} + TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_180(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get(None) for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_181(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("XXblind_spot_typeXX") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_182(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("BLIND_SPOT_TYPE") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_183(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "XXlabelXX": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_184(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "LABEL": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_185(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "XXsetXX": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_186(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "SET": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_187(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "XXstageXX": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_188(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "STAGE": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_189(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "XXpredictionsXX": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_190(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "PREDICTIONS": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_191(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "XXdropped_by_gateXX": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_192(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "DROPPED_BY_GATE": dropped,
        "meta": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_193(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "XXmetaXX": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_194(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "META": meta,
        "raw_responses": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_195(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "XXraw_responsesXX": raw_by_unit,
    }


# ----------------------------------------------------------------- execução

def x_run__mutmut_196(stage: str, set_name: str, client: Client) -> dict:
    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    test_file = spec["test_file"]
    tests = (CORPUS / spec["corpus"] / test_file).read_text()

    preds: list[dict] = []
    dropped: list[dict] = []
    raw_by_unit: dict[str, str] = {}

    for file in spec["files"]:
        target = Target(spec["corpus"], file)

        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            src_lines = target.lines()
            units = target.functions()
            if not units:
                units = [("<module>", 1, len(src_lines))]
            for name, start, end in units:
                body = "\n".join(src_lines[start - 1 : end])
                prompt = tmpl.format(
                    file=file, function=name, start=start, end=end,
                    source=numbered(body, start=start), test_file=test_file, tests=tests,
                )
                call = client.complete(system, prompt, stage=stage, unit=f"{file}::{name}")
                raw_by_unit[f"{file}::{name}"] = call.response
                preds.extend(parse_predictions(call.response))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            prompt = tmpl.format(
                file=file, source=numbered(target.source()), test_file=test_file, tests=tests
            )
            call = client.complete(system, prompt, stage=stage, unit=file)
            raw_by_unit[file] = call.response
            preds.extend(parse_predictions(call.response))

    # normaliza o campo file para o caminho canônico do conjunto
    canonical = {Path(f).name: f for f in spec["files"]}
    for p in preds:
        p["file"] = canonical.get(Path(str(p.get("file", ""))).name, p.get("file"))

    if cfg["gate"]:
        kept: list[dict] = []
        for file in spec["files"]:
            target = Target(spec["corpus"], file)
            k, d = evidence_gate([p for p in preds if p.get("file") == file], target)
            kept.extend(k)
            dropped.extend(d)
        kept.extend([p for p in preds if p.get("file") not in set(spec["files"])])
        preds = kept

    if cfg["sweep"]:
        preds = reconcile(preds)

    meta = client.totals()
    meta.update(
        {
            "stage": stage,
            "gate_applied": cfg["gate"],
            "sweep_applied": cfg["sweep"],
            "n_dropped_by_gate": len(dropped),
            "types_off_taxonomy": sorted(
                {p.get("blind_spot_type") for p in preds} - TAXONOMY - {None}
            ),
        }
    )
    return {
        "label": f"{stage}-{set_name}",
        "set": set_name,
        "stage": stage,
        "predictions": preds,
        "dropped_by_gate": dropped,
        "meta": meta,
        "RAW_RESPONSES": raw_by_unit,
    }

mutants_x_run__mutmut['_mutmut_orig'] = x_run__mutmut_orig # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_1'] = x_run__mutmut_1 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_2'] = x_run__mutmut_2 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_3'] = x_run__mutmut_3 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_4'] = x_run__mutmut_4 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_5'] = x_run__mutmut_5 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_6'] = x_run__mutmut_6 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_7'] = x_run__mutmut_7 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_8'] = x_run__mutmut_8 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_9'] = x_run__mutmut_9 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_10'] = x_run__mutmut_10 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_11'] = x_run__mutmut_11 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_12'] = x_run__mutmut_12 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_13'] = x_run__mutmut_13 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_14'] = x_run__mutmut_14 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_15'] = x_run__mutmut_15 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_16'] = x_run__mutmut_16 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_17'] = x_run__mutmut_17 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_18'] = x_run__mutmut_18 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_19'] = x_run__mutmut_19 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_20'] = x_run__mutmut_20 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_21'] = x_run__mutmut_21 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_22'] = x_run__mutmut_22 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_23'] = x_run__mutmut_23 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_24'] = x_run__mutmut_24 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_25'] = x_run__mutmut_25 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_26'] = x_run__mutmut_26 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_27'] = x_run__mutmut_27 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_28'] = x_run__mutmut_28 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_29'] = x_run__mutmut_29 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_30'] = x_run__mutmut_30 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_31'] = x_run__mutmut_31 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_32'] = x_run__mutmut_32 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_33'] = x_run__mutmut_33 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_34'] = x_run__mutmut_34 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_35'] = x_run__mutmut_35 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_36'] = x_run__mutmut_36 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_37'] = x_run__mutmut_37 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_38'] = x_run__mutmut_38 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_39'] = x_run__mutmut_39 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_40'] = x_run__mutmut_40 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_41'] = x_run__mutmut_41 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_42'] = x_run__mutmut_42 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_43'] = x_run__mutmut_43 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_44'] = x_run__mutmut_44 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_45'] = x_run__mutmut_45 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_46'] = x_run__mutmut_46 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_47'] = x_run__mutmut_47 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_48'] = x_run__mutmut_48 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_49'] = x_run__mutmut_49 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_50'] = x_run__mutmut_50 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_51'] = x_run__mutmut_51 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_52'] = x_run__mutmut_52 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_53'] = x_run__mutmut_53 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_54'] = x_run__mutmut_54 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_55'] = x_run__mutmut_55 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_56'] = x_run__mutmut_56 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_57'] = x_run__mutmut_57 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_58'] = x_run__mutmut_58 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_59'] = x_run__mutmut_59 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_60'] = x_run__mutmut_60 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_61'] = x_run__mutmut_61 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_62'] = x_run__mutmut_62 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_63'] = x_run__mutmut_63 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_64'] = x_run__mutmut_64 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_65'] = x_run__mutmut_65 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_66'] = x_run__mutmut_66 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_67'] = x_run__mutmut_67 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_68'] = x_run__mutmut_68 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_69'] = x_run__mutmut_69 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_70'] = x_run__mutmut_70 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_71'] = x_run__mutmut_71 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_72'] = x_run__mutmut_72 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_73'] = x_run__mutmut_73 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_74'] = x_run__mutmut_74 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_75'] = x_run__mutmut_75 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_76'] = x_run__mutmut_76 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_77'] = x_run__mutmut_77 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_78'] = x_run__mutmut_78 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_79'] = x_run__mutmut_79 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_80'] = x_run__mutmut_80 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_81'] = x_run__mutmut_81 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_82'] = x_run__mutmut_82 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_83'] = x_run__mutmut_83 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_84'] = x_run__mutmut_84 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_85'] = x_run__mutmut_85 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_86'] = x_run__mutmut_86 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_87'] = x_run__mutmut_87 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_88'] = x_run__mutmut_88 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_89'] = x_run__mutmut_89 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_90'] = x_run__mutmut_90 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_91'] = x_run__mutmut_91 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_92'] = x_run__mutmut_92 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_93'] = x_run__mutmut_93 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_94'] = x_run__mutmut_94 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_95'] = x_run__mutmut_95 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_96'] = x_run__mutmut_96 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_97'] = x_run__mutmut_97 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_98'] = x_run__mutmut_98 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_99'] = x_run__mutmut_99 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_100'] = x_run__mutmut_100 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_101'] = x_run__mutmut_101 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_102'] = x_run__mutmut_102 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_103'] = x_run__mutmut_103 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_104'] = x_run__mutmut_104 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_105'] = x_run__mutmut_105 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_106'] = x_run__mutmut_106 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_107'] = x_run__mutmut_107 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_108'] = x_run__mutmut_108 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_109'] = x_run__mutmut_109 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_110'] = x_run__mutmut_110 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_111'] = x_run__mutmut_111 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_112'] = x_run__mutmut_112 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_113'] = x_run__mutmut_113 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_114'] = x_run__mutmut_114 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_115'] = x_run__mutmut_115 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_116'] = x_run__mutmut_116 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_117'] = x_run__mutmut_117 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_118'] = x_run__mutmut_118 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_119'] = x_run__mutmut_119 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_120'] = x_run__mutmut_120 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_121'] = x_run__mutmut_121 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_122'] = x_run__mutmut_122 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_123'] = x_run__mutmut_123 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_124'] = x_run__mutmut_124 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_125'] = x_run__mutmut_125 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_126'] = x_run__mutmut_126 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_127'] = x_run__mutmut_127 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_128'] = x_run__mutmut_128 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_129'] = x_run__mutmut_129 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_130'] = x_run__mutmut_130 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_131'] = x_run__mutmut_131 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_132'] = x_run__mutmut_132 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_133'] = x_run__mutmut_133 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_134'] = x_run__mutmut_134 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_135'] = x_run__mutmut_135 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_136'] = x_run__mutmut_136 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_137'] = x_run__mutmut_137 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_138'] = x_run__mutmut_138 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_139'] = x_run__mutmut_139 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_140'] = x_run__mutmut_140 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_141'] = x_run__mutmut_141 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_142'] = x_run__mutmut_142 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_143'] = x_run__mutmut_143 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_144'] = x_run__mutmut_144 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_145'] = x_run__mutmut_145 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_146'] = x_run__mutmut_146 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_147'] = x_run__mutmut_147 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_148'] = x_run__mutmut_148 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_149'] = x_run__mutmut_149 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_150'] = x_run__mutmut_150 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_151'] = x_run__mutmut_151 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_152'] = x_run__mutmut_152 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_153'] = x_run__mutmut_153 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_154'] = x_run__mutmut_154 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_155'] = x_run__mutmut_155 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_156'] = x_run__mutmut_156 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_157'] = x_run__mutmut_157 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_158'] = x_run__mutmut_158 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_159'] = x_run__mutmut_159 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_160'] = x_run__mutmut_160 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_161'] = x_run__mutmut_161 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_162'] = x_run__mutmut_162 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_163'] = x_run__mutmut_163 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_164'] = x_run__mutmut_164 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_165'] = x_run__mutmut_165 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_166'] = x_run__mutmut_166 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_167'] = x_run__mutmut_167 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_168'] = x_run__mutmut_168 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_169'] = x_run__mutmut_169 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_170'] = x_run__mutmut_170 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_171'] = x_run__mutmut_171 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_172'] = x_run__mutmut_172 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_173'] = x_run__mutmut_173 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_174'] = x_run__mutmut_174 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_175'] = x_run__mutmut_175 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_176'] = x_run__mutmut_176 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_177'] = x_run__mutmut_177 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_178'] = x_run__mutmut_178 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_179'] = x_run__mutmut_179 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_180'] = x_run__mutmut_180 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_181'] = x_run__mutmut_181 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_182'] = x_run__mutmut_182 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_183'] = x_run__mutmut_183 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_184'] = x_run__mutmut_184 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_185'] = x_run__mutmut_185 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_186'] = x_run__mutmut_186 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_187'] = x_run__mutmut_187 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_188'] = x_run__mutmut_188 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_189'] = x_run__mutmut_189 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_190'] = x_run__mutmut_190 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_191'] = x_run__mutmut_191 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_192'] = x_run__mutmut_192 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_193'] = x_run__mutmut_193 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_194'] = x_run__mutmut_194 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_195'] = x_run__mutmut_195 # type: ignore # mutmut generated
mutants_x_run__mutmut['x_run__mutmut_196'] = x_run__mutmut_196 # type: ignore # mutmut generated
mutants_x_main__mutmut: MutantDict = {}  # type: ignore


@_mutmut_mutated(mutants_x_main__mutmut)
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=sorted(STAGES))
    ap.add_argument("--set", default="dev", choices=sorted(SETS))
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()

    client = Client()
    payload = run(args.stage, args.set, client)
    RESULTS.mkdir(exist_ok=True)
    dest = args.out or RESULTS / f"{payload['label']}.pred.json"
    dest.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")

    print(json.dumps(payload["meta"], indent=2))
    print(f"predições: {len(payload['predictions'])}  descartadas pelo gate: {len(payload['dropped_by_gate'])}")
    print(f"gravado: {dest}")
    return 0


def x_main__mutmut_orig() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=sorted(STAGES))
    ap.add_argument("--set", default="dev", choices=sorted(SETS))
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()

    client = Client()
    payload = run(args.stage, args.set, client)
    RESULTS.mkdir(exist_ok=True)
    dest = args.out or RESULTS / f"{payload['label']}.pred.json"
    dest.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")

    print(json.dumps(payload["meta"], indent=2))
    print(f"predições: {len(payload['predictions'])}  descartadas pelo gate: {len(payload['dropped_by_gate'])}")
    print(f"gravado: {dest}")
    return 0


def x_main__mutmut_1() -> int:
    ap = None
    ap.add_argument("--stage", required=True, choices=sorted(STAGES))
    ap.add_argument("--set", default="dev", choices=sorted(SETS))
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()

    client = Client()
    payload = run(args.stage, args.set, client)
    RESULTS.mkdir(exist_ok=True)
    dest = args.out or RESULTS / f"{payload['label']}.pred.json"
    dest.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")

    print(json.dumps(payload["meta"], indent=2))
    print(f"predições: {len(payload['predictions'])}  descartadas pelo gate: {len(payload['dropped_by_gate'])}")
    print(f"gravado: {dest}")
    return 0


def x_main__mutmut_2() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(None, required=True, choices=sorted(STAGES))
    ap.add_argument("--set", default="dev", choices=sorted(SETS))
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()

    client = Client()
    payload = run(args.stage, args.set, client)
    RESULTS.mkdir(exist_ok=True)
    dest = args.out or RESULTS / f"{payload['label']}.pred.json"
    dest.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")

    print(json.dumps(payload["meta"], indent=2))
    print(f"predições: {len(payload['predictions'])}  descartadas pelo gate: {len(payload['dropped_by_gate'])}")
    print(f"gravado: {dest}")
    return 0


def x_main__mutmut_3() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=None, choices=sorted(STAGES))
    ap.add_argument("--set", default="dev", choices=sorted(SETS))
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()

    client = Client()
    payload = run(args.stage, args.set, client)
    RESULTS.mkdir(exist_ok=True)
    dest = args.out or RESULTS / f"{payload['label']}.pred.json"
    dest.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")

    print(json.dumps(payload["meta"], indent=2))
    print(f"predições: {len(payload['predictions'])}  descartadas pelo gate: {len(payload['dropped_by_gate'])}")
    print(f"gravado: {dest}")
    return 0


def x_main__mutmut_4() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=None)
    ap.add_argument("--set", default="dev", choices=sorted(SETS))
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()

    client = Client()
    payload = run(args.stage, args.set, client)
    RESULTS.mkdir(exist_ok=True)
    dest = args.out or RESULTS / f"{payload['label']}.pred.json"
    dest.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")

    print(json.dumps(payload["meta"], indent=2))
    print(f"predições: {len(payload['predictions'])}  descartadas pelo gate: {len(payload['dropped_by_gate'])}")
    print(f"gravado: {dest}")
    return 0


def x_main__mutmut_5() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(required=True, choices=sorted(STAGES))
    ap.add_argument("--set", default="dev", choices=sorted(SETS))
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()

    client = Client()
    payload = run(args.stage, args.set, client)
    RESULTS.mkdir(exist_ok=True)
    dest = args.out or RESULTS / f"{payload['label']}.pred.json"
    dest.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")

    print(json.dumps(payload["meta"], indent=2))
    print(f"predições: {len(payload['predictions'])}  descartadas pelo gate: {len(payload['dropped_by_gate'])}")
    print(f"gravado: {dest}")
    return 0


def x_main__mutmut_6() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", choices=sorted(STAGES))
    ap.add_argument("--set", default="dev", choices=sorted(SETS))
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()

    client = Client()
    payload = run(args.stage, args.set, client)
    RESULTS.mkdir(exist_ok=True)
    dest = args.out or RESULTS / f"{payload['label']}.pred.json"
    dest.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")

    print(json.dumps(payload["meta"], indent=2))
    print(f"predições: {len(payload['predictions'])}  descartadas pelo gate: {len(payload['dropped_by_gate'])}")
    print(f"gravado: {dest}")
    return 0


def x_main__mutmut_7() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, )
    ap.add_argument("--set", default="dev", choices=sorted(SETS))
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()

    client = Client()
    payload = run(args.stage, args.set, client)
    RESULTS.mkdir(exist_ok=True)
    dest = args.out or RESULTS / f"{payload['label']}.pred.json"
    dest.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")

    print(json.dumps(payload["meta"], indent=2))
    print(f"predições: {len(payload['predictions'])}  descartadas pelo gate: {len(payload['dropped_by_gate'])}")
    print(f"gravado: {dest}")
    return 0


def x_main__mutmut_8() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("XX--stageXX", required=True, choices=sorted(STAGES))
    ap.add_argument("--set", default="dev", choices=sorted(SETS))
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()

    client = Client()
    payload = run(args.stage, args.set, client)
    RESULTS.mkdir(exist_ok=True)
    dest = args.out or RESULTS / f"{payload['label']}.pred.json"
    dest.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")

    print(json.dumps(payload["meta"], indent=2))
    print(f"predições: {len(payload['predictions'])}  descartadas pelo gate: {len(payload['dropped_by_gate'])}")
    print(f"gravado: {dest}")
    return 0


def x_main__mutmut_9() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--STAGE", required=True, choices=sorted(STAGES))
    ap.add_argument("--set", default="dev", choices=sorted(SETS))
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()

    client = Client()
    payload = run(args.stage, args.set, client)
    RESULTS.mkdir(exist_ok=True)
    dest = args.out or RESULTS / f"{payload['label']}.pred.json"
    dest.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")

    print(json.dumps(payload["meta"], indent=2))
    print(f"predições: {len(payload['predictions'])}  descartadas pelo gate: {len(payload['dropped_by_gate'])}")
    print(f"gravado: {dest}")
    return 0


def x_main__mutmut_10() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=False, choices=sorted(STAGES))
    ap.add_argument("--set", default="dev", choices=sorted(SETS))
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()

    client = Client()
    payload = run(args.stage, args.set, client)
    RESULTS.mkdir(exist_ok=True)
    dest = args.out or RESULTS / f"{payload['label']}.pred.json"
    dest.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")

    print(json.dumps(payload["meta"], indent=2))
    print(f"predições: {len(payload['predictions'])}  descartadas pelo gate: {len(payload['dropped_by_gate'])}")
    print(f"gravado: {dest}")
    return 0


def x_main__mutmut_11() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=sorted(None))
    ap.add_argument("--set", default="dev", choices=sorted(SETS))
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()

    client = Client()
    payload = run(args.stage, args.set, client)
    RESULTS.mkdir(exist_ok=True)
    dest = args.out or RESULTS / f"{payload['label']}.pred.json"
    dest.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")

    print(json.dumps(payload["meta"], indent=2))
    print(f"predições: {len(payload['predictions'])}  descartadas pelo gate: {len(payload['dropped_by_gate'])}")
    print(f"gravado: {dest}")
    return 0


def x_main__mutmut_12() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=sorted(STAGES))
    ap.add_argument(None, default="dev", choices=sorted(SETS))
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()

    client = Client()
    payload = run(args.stage, args.set, client)
    RESULTS.mkdir(exist_ok=True)
    dest = args.out or RESULTS / f"{payload['label']}.pred.json"
    dest.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")

    print(json.dumps(payload["meta"], indent=2))
    print(f"predições: {len(payload['predictions'])}  descartadas pelo gate: {len(payload['dropped_by_gate'])}")
    print(f"gravado: {dest}")
    return 0


def x_main__mutmut_13() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=sorted(STAGES))
    ap.add_argument("--set", default=None, choices=sorted(SETS))
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()

    client = Client()
    payload = run(args.stage, args.set, client)
    RESULTS.mkdir(exist_ok=True)
    dest = args.out or RESULTS / f"{payload['label']}.pred.json"
    dest.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")

    print(json.dumps(payload["meta"], indent=2))
    print(f"predições: {len(payload['predictions'])}  descartadas pelo gate: {len(payload['dropped_by_gate'])}")
    print(f"gravado: {dest}")
    return 0


def x_main__mutmut_14() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=sorted(STAGES))
    ap.add_argument("--set", default="dev", choices=None)
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()

    client = Client()
    payload = run(args.stage, args.set, client)
    RESULTS.mkdir(exist_ok=True)
    dest = args.out or RESULTS / f"{payload['label']}.pred.json"
    dest.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")

    print(json.dumps(payload["meta"], indent=2))
    print(f"predições: {len(payload['predictions'])}  descartadas pelo gate: {len(payload['dropped_by_gate'])}")
    print(f"gravado: {dest}")
    return 0


def x_main__mutmut_15() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=sorted(STAGES))
    ap.add_argument(default="dev", choices=sorted(SETS))
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()

    client = Client()
    payload = run(args.stage, args.set, client)
    RESULTS.mkdir(exist_ok=True)
    dest = args.out or RESULTS / f"{payload['label']}.pred.json"
    dest.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")

    print(json.dumps(payload["meta"], indent=2))
    print(f"predições: {len(payload['predictions'])}  descartadas pelo gate: {len(payload['dropped_by_gate'])}")
    print(f"gravado: {dest}")
    return 0


def x_main__mutmut_16() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=sorted(STAGES))
    ap.add_argument("--set", choices=sorted(SETS))
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()

    client = Client()
    payload = run(args.stage, args.set, client)
    RESULTS.mkdir(exist_ok=True)
    dest = args.out or RESULTS / f"{payload['label']}.pred.json"
    dest.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")

    print(json.dumps(payload["meta"], indent=2))
    print(f"predições: {len(payload['predictions'])}  descartadas pelo gate: {len(payload['dropped_by_gate'])}")
    print(f"gravado: {dest}")
    return 0


def x_main__mutmut_17() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=sorted(STAGES))
    ap.add_argument("--set", default="dev", )
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()

    client = Client()
    payload = run(args.stage, args.set, client)
    RESULTS.mkdir(exist_ok=True)
    dest = args.out or RESULTS / f"{payload['label']}.pred.json"
    dest.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")

    print(json.dumps(payload["meta"], indent=2))
    print(f"predições: {len(payload['predictions'])}  descartadas pelo gate: {len(payload['dropped_by_gate'])}")
    print(f"gravado: {dest}")
    return 0


def x_main__mutmut_18() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=sorted(STAGES))
    ap.add_argument("XX--setXX", default="dev", choices=sorted(SETS))
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()

    client = Client()
    payload = run(args.stage, args.set, client)
    RESULTS.mkdir(exist_ok=True)
    dest = args.out or RESULTS / f"{payload['label']}.pred.json"
    dest.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")

    print(json.dumps(payload["meta"], indent=2))
    print(f"predições: {len(payload['predictions'])}  descartadas pelo gate: {len(payload['dropped_by_gate'])}")
    print(f"gravado: {dest}")
    return 0


def x_main__mutmut_19() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=sorted(STAGES))
    ap.add_argument("--SET", default="dev", choices=sorted(SETS))
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()

    client = Client()
    payload = run(args.stage, args.set, client)
    RESULTS.mkdir(exist_ok=True)
    dest = args.out or RESULTS / f"{payload['label']}.pred.json"
    dest.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")

    print(json.dumps(payload["meta"], indent=2))
    print(f"predições: {len(payload['predictions'])}  descartadas pelo gate: {len(payload['dropped_by_gate'])}")
    print(f"gravado: {dest}")
    return 0


def x_main__mutmut_20() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=sorted(STAGES))
    ap.add_argument("--set", default="XXdevXX", choices=sorted(SETS))
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()

    client = Client()
    payload = run(args.stage, args.set, client)
    RESULTS.mkdir(exist_ok=True)
    dest = args.out or RESULTS / f"{payload['label']}.pred.json"
    dest.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")

    print(json.dumps(payload["meta"], indent=2))
    print(f"predições: {len(payload['predictions'])}  descartadas pelo gate: {len(payload['dropped_by_gate'])}")
    print(f"gravado: {dest}")
    return 0


def x_main__mutmut_21() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=sorted(STAGES))
    ap.add_argument("--set", default="DEV", choices=sorted(SETS))
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()

    client = Client()
    payload = run(args.stage, args.set, client)
    RESULTS.mkdir(exist_ok=True)
    dest = args.out or RESULTS / f"{payload['label']}.pred.json"
    dest.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")

    print(json.dumps(payload["meta"], indent=2))
    print(f"predições: {len(payload['predictions'])}  descartadas pelo gate: {len(payload['dropped_by_gate'])}")
    print(f"gravado: {dest}")
    return 0


def x_main__mutmut_22() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=sorted(STAGES))
    ap.add_argument("--set", default="dev", choices=sorted(None))
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()

    client = Client()
    payload = run(args.stage, args.set, client)
    RESULTS.mkdir(exist_ok=True)
    dest = args.out or RESULTS / f"{payload['label']}.pred.json"
    dest.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")

    print(json.dumps(payload["meta"], indent=2))
    print(f"predições: {len(payload['predictions'])}  descartadas pelo gate: {len(payload['dropped_by_gate'])}")
    print(f"gravado: {dest}")
    return 0


def x_main__mutmut_23() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=sorted(STAGES))
    ap.add_argument("--set", default="dev", choices=sorted(SETS))
    ap.add_argument(None, type=Path)
    args = ap.parse_args()

    client = Client()
    payload = run(args.stage, args.set, client)
    RESULTS.mkdir(exist_ok=True)
    dest = args.out or RESULTS / f"{payload['label']}.pred.json"
    dest.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")

    print(json.dumps(payload["meta"], indent=2))
    print(f"predições: {len(payload['predictions'])}  descartadas pelo gate: {len(payload['dropped_by_gate'])}")
    print(f"gravado: {dest}")
    return 0


def x_main__mutmut_24() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=sorted(STAGES))
    ap.add_argument("--set", default="dev", choices=sorted(SETS))
    ap.add_argument("--out", type=None)
    args = ap.parse_args()

    client = Client()
    payload = run(args.stage, args.set, client)
    RESULTS.mkdir(exist_ok=True)
    dest = args.out or RESULTS / f"{payload['label']}.pred.json"
    dest.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")

    print(json.dumps(payload["meta"], indent=2))
    print(f"predições: {len(payload['predictions'])}  descartadas pelo gate: {len(payload['dropped_by_gate'])}")
    print(f"gravado: {dest}")
    return 0


def x_main__mutmut_25() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=sorted(STAGES))
    ap.add_argument("--set", default="dev", choices=sorted(SETS))
    ap.add_argument(type=Path)
    args = ap.parse_args()

    client = Client()
    payload = run(args.stage, args.set, client)
    RESULTS.mkdir(exist_ok=True)
    dest = args.out or RESULTS / f"{payload['label']}.pred.json"
    dest.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")

    print(json.dumps(payload["meta"], indent=2))
    print(f"predições: {len(payload['predictions'])}  descartadas pelo gate: {len(payload['dropped_by_gate'])}")
    print(f"gravado: {dest}")
    return 0


def x_main__mutmut_26() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=sorted(STAGES))
    ap.add_argument("--set", default="dev", choices=sorted(SETS))
    ap.add_argument("--out", )
    args = ap.parse_args()

    client = Client()
    payload = run(args.stage, args.set, client)
    RESULTS.mkdir(exist_ok=True)
    dest = args.out or RESULTS / f"{payload['label']}.pred.json"
    dest.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")

    print(json.dumps(payload["meta"], indent=2))
    print(f"predições: {len(payload['predictions'])}  descartadas pelo gate: {len(payload['dropped_by_gate'])}")
    print(f"gravado: {dest}")
    return 0


def x_main__mutmut_27() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=sorted(STAGES))
    ap.add_argument("--set", default="dev", choices=sorted(SETS))
    ap.add_argument("XX--outXX", type=Path)
    args = ap.parse_args()

    client = Client()
    payload = run(args.stage, args.set, client)
    RESULTS.mkdir(exist_ok=True)
    dest = args.out or RESULTS / f"{payload['label']}.pred.json"
    dest.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")

    print(json.dumps(payload["meta"], indent=2))
    print(f"predições: {len(payload['predictions'])}  descartadas pelo gate: {len(payload['dropped_by_gate'])}")
    print(f"gravado: {dest}")
    return 0


def x_main__mutmut_28() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=sorted(STAGES))
    ap.add_argument("--set", default="dev", choices=sorted(SETS))
    ap.add_argument("--OUT", type=Path)
    args = ap.parse_args()

    client = Client()
    payload = run(args.stage, args.set, client)
    RESULTS.mkdir(exist_ok=True)
    dest = args.out or RESULTS / f"{payload['label']}.pred.json"
    dest.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")

    print(json.dumps(payload["meta"], indent=2))
    print(f"predições: {len(payload['predictions'])}  descartadas pelo gate: {len(payload['dropped_by_gate'])}")
    print(f"gravado: {dest}")
    return 0


def x_main__mutmut_29() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=sorted(STAGES))
    ap.add_argument("--set", default="dev", choices=sorted(SETS))
    ap.add_argument("--out", type=Path)
    args = None

    client = Client()
    payload = run(args.stage, args.set, client)
    RESULTS.mkdir(exist_ok=True)
    dest = args.out or RESULTS / f"{payload['label']}.pred.json"
    dest.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")

    print(json.dumps(payload["meta"], indent=2))
    print(f"predições: {len(payload['predictions'])}  descartadas pelo gate: {len(payload['dropped_by_gate'])}")
    print(f"gravado: {dest}")
    return 0


def x_main__mutmut_30() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=sorted(STAGES))
    ap.add_argument("--set", default="dev", choices=sorted(SETS))
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()

    client = None
    payload = run(args.stage, args.set, client)
    RESULTS.mkdir(exist_ok=True)
    dest = args.out or RESULTS / f"{payload['label']}.pred.json"
    dest.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")

    print(json.dumps(payload["meta"], indent=2))
    print(f"predições: {len(payload['predictions'])}  descartadas pelo gate: {len(payload['dropped_by_gate'])}")
    print(f"gravado: {dest}")
    return 0


def x_main__mutmut_31() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=sorted(STAGES))
    ap.add_argument("--set", default="dev", choices=sorted(SETS))
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()

    client = Client()
    payload = None
    RESULTS.mkdir(exist_ok=True)
    dest = args.out or RESULTS / f"{payload['label']}.pred.json"
    dest.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")

    print(json.dumps(payload["meta"], indent=2))
    print(f"predições: {len(payload['predictions'])}  descartadas pelo gate: {len(payload['dropped_by_gate'])}")
    print(f"gravado: {dest}")
    return 0


def x_main__mutmut_32() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=sorted(STAGES))
    ap.add_argument("--set", default="dev", choices=sorted(SETS))
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()

    client = Client()
    payload = run(None, args.set, client)
    RESULTS.mkdir(exist_ok=True)
    dest = args.out or RESULTS / f"{payload['label']}.pred.json"
    dest.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")

    print(json.dumps(payload["meta"], indent=2))
    print(f"predições: {len(payload['predictions'])}  descartadas pelo gate: {len(payload['dropped_by_gate'])}")
    print(f"gravado: {dest}")
    return 0


def x_main__mutmut_33() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=sorted(STAGES))
    ap.add_argument("--set", default="dev", choices=sorted(SETS))
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()

    client = Client()
    payload = run(args.stage, None, client)
    RESULTS.mkdir(exist_ok=True)
    dest = args.out or RESULTS / f"{payload['label']}.pred.json"
    dest.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")

    print(json.dumps(payload["meta"], indent=2))
    print(f"predições: {len(payload['predictions'])}  descartadas pelo gate: {len(payload['dropped_by_gate'])}")
    print(f"gravado: {dest}")
    return 0


def x_main__mutmut_34() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=sorted(STAGES))
    ap.add_argument("--set", default="dev", choices=sorted(SETS))
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()

    client = Client()
    payload = run(args.stage, args.set, None)
    RESULTS.mkdir(exist_ok=True)
    dest = args.out or RESULTS / f"{payload['label']}.pred.json"
    dest.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")

    print(json.dumps(payload["meta"], indent=2))
    print(f"predições: {len(payload['predictions'])}  descartadas pelo gate: {len(payload['dropped_by_gate'])}")
    print(f"gravado: {dest}")
    return 0


def x_main__mutmut_35() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=sorted(STAGES))
    ap.add_argument("--set", default="dev", choices=sorted(SETS))
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()

    client = Client()
    payload = run(args.set, client)
    RESULTS.mkdir(exist_ok=True)
    dest = args.out or RESULTS / f"{payload['label']}.pred.json"
    dest.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")

    print(json.dumps(payload["meta"], indent=2))
    print(f"predições: {len(payload['predictions'])}  descartadas pelo gate: {len(payload['dropped_by_gate'])}")
    print(f"gravado: {dest}")
    return 0


def x_main__mutmut_36() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=sorted(STAGES))
    ap.add_argument("--set", default="dev", choices=sorted(SETS))
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()

    client = Client()
    payload = run(args.stage, client)
    RESULTS.mkdir(exist_ok=True)
    dest = args.out or RESULTS / f"{payload['label']}.pred.json"
    dest.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")

    print(json.dumps(payload["meta"], indent=2))
    print(f"predições: {len(payload['predictions'])}  descartadas pelo gate: {len(payload['dropped_by_gate'])}")
    print(f"gravado: {dest}")
    return 0


def x_main__mutmut_37() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=sorted(STAGES))
    ap.add_argument("--set", default="dev", choices=sorted(SETS))
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()

    client = Client()
    payload = run(args.stage, args.set, )
    RESULTS.mkdir(exist_ok=True)
    dest = args.out or RESULTS / f"{payload['label']}.pred.json"
    dest.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")

    print(json.dumps(payload["meta"], indent=2))
    print(f"predições: {len(payload['predictions'])}  descartadas pelo gate: {len(payload['dropped_by_gate'])}")
    print(f"gravado: {dest}")
    return 0


def x_main__mutmut_38() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=sorted(STAGES))
    ap.add_argument("--set", default="dev", choices=sorted(SETS))
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()

    client = Client()
    payload = run(args.stage, args.set, client)
    RESULTS.mkdir(exist_ok=None)
    dest = args.out or RESULTS / f"{payload['label']}.pred.json"
    dest.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")

    print(json.dumps(payload["meta"], indent=2))
    print(f"predições: {len(payload['predictions'])}  descartadas pelo gate: {len(payload['dropped_by_gate'])}")
    print(f"gravado: {dest}")
    return 0


def x_main__mutmut_39() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=sorted(STAGES))
    ap.add_argument("--set", default="dev", choices=sorted(SETS))
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()

    client = Client()
    payload = run(args.stage, args.set, client)
    RESULTS.mkdir(exist_ok=False)
    dest = args.out or RESULTS / f"{payload['label']}.pred.json"
    dest.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")

    print(json.dumps(payload["meta"], indent=2))
    print(f"predições: {len(payload['predictions'])}  descartadas pelo gate: {len(payload['dropped_by_gate'])}")
    print(f"gravado: {dest}")
    return 0


def x_main__mutmut_40() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=sorted(STAGES))
    ap.add_argument("--set", default="dev", choices=sorted(SETS))
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()

    client = Client()
    payload = run(args.stage, args.set, client)
    RESULTS.mkdir(exist_ok=True)
    dest = None
    dest.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")

    print(json.dumps(payload["meta"], indent=2))
    print(f"predições: {len(payload['predictions'])}  descartadas pelo gate: {len(payload['dropped_by_gate'])}")
    print(f"gravado: {dest}")
    return 0


def x_main__mutmut_41() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=sorted(STAGES))
    ap.add_argument("--set", default="dev", choices=sorted(SETS))
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()

    client = Client()
    payload = run(args.stage, args.set, client)
    RESULTS.mkdir(exist_ok=True)
    dest = args.out and RESULTS / f"{payload['label']}.pred.json"
    dest.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")

    print(json.dumps(payload["meta"], indent=2))
    print(f"predições: {len(payload['predictions'])}  descartadas pelo gate: {len(payload['dropped_by_gate'])}")
    print(f"gravado: {dest}")
    return 0


def x_main__mutmut_42() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=sorted(STAGES))
    ap.add_argument("--set", default="dev", choices=sorted(SETS))
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()

    client = Client()
    payload = run(args.stage, args.set, client)
    RESULTS.mkdir(exist_ok=True)
    dest = args.out or RESULTS * f"{payload['label']}.pred.json"
    dest.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")

    print(json.dumps(payload["meta"], indent=2))
    print(f"predições: {len(payload['predictions'])}  descartadas pelo gate: {len(payload['dropped_by_gate'])}")
    print(f"gravado: {dest}")
    return 0


def x_main__mutmut_43() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=sorted(STAGES))
    ap.add_argument("--set", default="dev", choices=sorted(SETS))
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()

    client = Client()
    payload = run(args.stage, args.set, client)
    RESULTS.mkdir(exist_ok=True)
    dest = args.out or RESULTS / f"{payload['XXlabelXX']}.pred.json"
    dest.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")

    print(json.dumps(payload["meta"], indent=2))
    print(f"predições: {len(payload['predictions'])}  descartadas pelo gate: {len(payload['dropped_by_gate'])}")
    print(f"gravado: {dest}")
    return 0


def x_main__mutmut_44() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=sorted(STAGES))
    ap.add_argument("--set", default="dev", choices=sorted(SETS))
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()

    client = Client()
    payload = run(args.stage, args.set, client)
    RESULTS.mkdir(exist_ok=True)
    dest = args.out or RESULTS / f"{payload['LABEL']}.pred.json"
    dest.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")

    print(json.dumps(payload["meta"], indent=2))
    print(f"predições: {len(payload['predictions'])}  descartadas pelo gate: {len(payload['dropped_by_gate'])}")
    print(f"gravado: {dest}")
    return 0


def x_main__mutmut_45() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=sorted(STAGES))
    ap.add_argument("--set", default="dev", choices=sorted(SETS))
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()

    client = Client()
    payload = run(args.stage, args.set, client)
    RESULTS.mkdir(exist_ok=True)
    dest = args.out or RESULTS / f"{payload['label']}.pred.json"
    dest.write_text(None)

    print(json.dumps(payload["meta"], indent=2))
    print(f"predições: {len(payload['predictions'])}  descartadas pelo gate: {len(payload['dropped_by_gate'])}")
    print(f"gravado: {dest}")
    return 0


def x_main__mutmut_46() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=sorted(STAGES))
    ap.add_argument("--set", default="dev", choices=sorted(SETS))
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()

    client = Client()
    payload = run(args.stage, args.set, client)
    RESULTS.mkdir(exist_ok=True)
    dest = args.out or RESULTS / f"{payload['label']}.pred.json"
    dest.write_text(json.dumps(payload, indent=2, ensure_ascii=False) - "\n")

    print(json.dumps(payload["meta"], indent=2))
    print(f"predições: {len(payload['predictions'])}  descartadas pelo gate: {len(payload['dropped_by_gate'])}")
    print(f"gravado: {dest}")
    return 0


def x_main__mutmut_47() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=sorted(STAGES))
    ap.add_argument("--set", default="dev", choices=sorted(SETS))
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()

    client = Client()
    payload = run(args.stage, args.set, client)
    RESULTS.mkdir(exist_ok=True)
    dest = args.out or RESULTS / f"{payload['label']}.pred.json"
    dest.write_text(json.dumps(None, indent=2, ensure_ascii=False) + "\n")

    print(json.dumps(payload["meta"], indent=2))
    print(f"predições: {len(payload['predictions'])}  descartadas pelo gate: {len(payload['dropped_by_gate'])}")
    print(f"gravado: {dest}")
    return 0


def x_main__mutmut_48() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=sorted(STAGES))
    ap.add_argument("--set", default="dev", choices=sorted(SETS))
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()

    client = Client()
    payload = run(args.stage, args.set, client)
    RESULTS.mkdir(exist_ok=True)
    dest = args.out or RESULTS / f"{payload['label']}.pred.json"
    dest.write_text(json.dumps(payload, indent=None, ensure_ascii=False) + "\n")

    print(json.dumps(payload["meta"], indent=2))
    print(f"predições: {len(payload['predictions'])}  descartadas pelo gate: {len(payload['dropped_by_gate'])}")
    print(f"gravado: {dest}")
    return 0


def x_main__mutmut_49() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=sorted(STAGES))
    ap.add_argument("--set", default="dev", choices=sorted(SETS))
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()

    client = Client()
    payload = run(args.stage, args.set, client)
    RESULTS.mkdir(exist_ok=True)
    dest = args.out or RESULTS / f"{payload['label']}.pred.json"
    dest.write_text(json.dumps(payload, indent=2, ensure_ascii=None) + "\n")

    print(json.dumps(payload["meta"], indent=2))
    print(f"predições: {len(payload['predictions'])}  descartadas pelo gate: {len(payload['dropped_by_gate'])}")
    print(f"gravado: {dest}")
    return 0


def x_main__mutmut_50() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=sorted(STAGES))
    ap.add_argument("--set", default="dev", choices=sorted(SETS))
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()

    client = Client()
    payload = run(args.stage, args.set, client)
    RESULTS.mkdir(exist_ok=True)
    dest = args.out or RESULTS / f"{payload['label']}.pred.json"
    dest.write_text(json.dumps(indent=2, ensure_ascii=False) + "\n")

    print(json.dumps(payload["meta"], indent=2))
    print(f"predições: {len(payload['predictions'])}  descartadas pelo gate: {len(payload['dropped_by_gate'])}")
    print(f"gravado: {dest}")
    return 0


def x_main__mutmut_51() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=sorted(STAGES))
    ap.add_argument("--set", default="dev", choices=sorted(SETS))
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()

    client = Client()
    payload = run(args.stage, args.set, client)
    RESULTS.mkdir(exist_ok=True)
    dest = args.out or RESULTS / f"{payload['label']}.pred.json"
    dest.write_text(json.dumps(payload, ensure_ascii=False) + "\n")

    print(json.dumps(payload["meta"], indent=2))
    print(f"predições: {len(payload['predictions'])}  descartadas pelo gate: {len(payload['dropped_by_gate'])}")
    print(f"gravado: {dest}")
    return 0


def x_main__mutmut_52() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=sorted(STAGES))
    ap.add_argument("--set", default="dev", choices=sorted(SETS))
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()

    client = Client()
    payload = run(args.stage, args.set, client)
    RESULTS.mkdir(exist_ok=True)
    dest = args.out or RESULTS / f"{payload['label']}.pred.json"
    dest.write_text(json.dumps(payload, indent=2, ) + "\n")

    print(json.dumps(payload["meta"], indent=2))
    print(f"predições: {len(payload['predictions'])}  descartadas pelo gate: {len(payload['dropped_by_gate'])}")
    print(f"gravado: {dest}")
    return 0


def x_main__mutmut_53() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=sorted(STAGES))
    ap.add_argument("--set", default="dev", choices=sorted(SETS))
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()

    client = Client()
    payload = run(args.stage, args.set, client)
    RESULTS.mkdir(exist_ok=True)
    dest = args.out or RESULTS / f"{payload['label']}.pred.json"
    dest.write_text(json.dumps(payload, indent=3, ensure_ascii=False) + "\n")

    print(json.dumps(payload["meta"], indent=2))
    print(f"predições: {len(payload['predictions'])}  descartadas pelo gate: {len(payload['dropped_by_gate'])}")
    print(f"gravado: {dest}")
    return 0


def x_main__mutmut_54() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=sorted(STAGES))
    ap.add_argument("--set", default="dev", choices=sorted(SETS))
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()

    client = Client()
    payload = run(args.stage, args.set, client)
    RESULTS.mkdir(exist_ok=True)
    dest = args.out or RESULTS / f"{payload['label']}.pred.json"
    dest.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n")

    print(json.dumps(payload["meta"], indent=2))
    print(f"predições: {len(payload['predictions'])}  descartadas pelo gate: {len(payload['dropped_by_gate'])}")
    print(f"gravado: {dest}")
    return 0


def x_main__mutmut_55() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=sorted(STAGES))
    ap.add_argument("--set", default="dev", choices=sorted(SETS))
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()

    client = Client()
    payload = run(args.stage, args.set, client)
    RESULTS.mkdir(exist_ok=True)
    dest = args.out or RESULTS / f"{payload['label']}.pred.json"
    dest.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "XX\nXX")

    print(json.dumps(payload["meta"], indent=2))
    print(f"predições: {len(payload['predictions'])}  descartadas pelo gate: {len(payload['dropped_by_gate'])}")
    print(f"gravado: {dest}")
    return 0


def x_main__mutmut_56() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=sorted(STAGES))
    ap.add_argument("--set", default="dev", choices=sorted(SETS))
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()

    client = Client()
    payload = run(args.stage, args.set, client)
    RESULTS.mkdir(exist_ok=True)
    dest = args.out or RESULTS / f"{payload['label']}.pred.json"
    dest.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")

    print(None)
    print(f"predições: {len(payload['predictions'])}  descartadas pelo gate: {len(payload['dropped_by_gate'])}")
    print(f"gravado: {dest}")
    return 0


def x_main__mutmut_57() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=sorted(STAGES))
    ap.add_argument("--set", default="dev", choices=sorted(SETS))
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()

    client = Client()
    payload = run(args.stage, args.set, client)
    RESULTS.mkdir(exist_ok=True)
    dest = args.out or RESULTS / f"{payload['label']}.pred.json"
    dest.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")

    print(json.dumps(None, indent=2))
    print(f"predições: {len(payload['predictions'])}  descartadas pelo gate: {len(payload['dropped_by_gate'])}")
    print(f"gravado: {dest}")
    return 0


def x_main__mutmut_58() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=sorted(STAGES))
    ap.add_argument("--set", default="dev", choices=sorted(SETS))
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()

    client = Client()
    payload = run(args.stage, args.set, client)
    RESULTS.mkdir(exist_ok=True)
    dest = args.out or RESULTS / f"{payload['label']}.pred.json"
    dest.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")

    print(json.dumps(payload["meta"], indent=None))
    print(f"predições: {len(payload['predictions'])}  descartadas pelo gate: {len(payload['dropped_by_gate'])}")
    print(f"gravado: {dest}")
    return 0


def x_main__mutmut_59() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=sorted(STAGES))
    ap.add_argument("--set", default="dev", choices=sorted(SETS))
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()

    client = Client()
    payload = run(args.stage, args.set, client)
    RESULTS.mkdir(exist_ok=True)
    dest = args.out or RESULTS / f"{payload['label']}.pred.json"
    dest.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")

    print(json.dumps(indent=2))
    print(f"predições: {len(payload['predictions'])}  descartadas pelo gate: {len(payload['dropped_by_gate'])}")
    print(f"gravado: {dest}")
    return 0


def x_main__mutmut_60() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=sorted(STAGES))
    ap.add_argument("--set", default="dev", choices=sorted(SETS))
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()

    client = Client()
    payload = run(args.stage, args.set, client)
    RESULTS.mkdir(exist_ok=True)
    dest = args.out or RESULTS / f"{payload['label']}.pred.json"
    dest.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")

    print(json.dumps(payload["meta"], ))
    print(f"predições: {len(payload['predictions'])}  descartadas pelo gate: {len(payload['dropped_by_gate'])}")
    print(f"gravado: {dest}")
    return 0


def x_main__mutmut_61() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=sorted(STAGES))
    ap.add_argument("--set", default="dev", choices=sorted(SETS))
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()

    client = Client()
    payload = run(args.stage, args.set, client)
    RESULTS.mkdir(exist_ok=True)
    dest = args.out or RESULTS / f"{payload['label']}.pred.json"
    dest.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")

    print(json.dumps(payload["XXmetaXX"], indent=2))
    print(f"predições: {len(payload['predictions'])}  descartadas pelo gate: {len(payload['dropped_by_gate'])}")
    print(f"gravado: {dest}")
    return 0


def x_main__mutmut_62() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=sorted(STAGES))
    ap.add_argument("--set", default="dev", choices=sorted(SETS))
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()

    client = Client()
    payload = run(args.stage, args.set, client)
    RESULTS.mkdir(exist_ok=True)
    dest = args.out or RESULTS / f"{payload['label']}.pred.json"
    dest.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")

    print(json.dumps(payload["META"], indent=2))
    print(f"predições: {len(payload['predictions'])}  descartadas pelo gate: {len(payload['dropped_by_gate'])}")
    print(f"gravado: {dest}")
    return 0


def x_main__mutmut_63() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=sorted(STAGES))
    ap.add_argument("--set", default="dev", choices=sorted(SETS))
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()

    client = Client()
    payload = run(args.stage, args.set, client)
    RESULTS.mkdir(exist_ok=True)
    dest = args.out or RESULTS / f"{payload['label']}.pred.json"
    dest.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")

    print(json.dumps(payload["meta"], indent=3))
    print(f"predições: {len(payload['predictions'])}  descartadas pelo gate: {len(payload['dropped_by_gate'])}")
    print(f"gravado: {dest}")
    return 0


def x_main__mutmut_64() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=sorted(STAGES))
    ap.add_argument("--set", default="dev", choices=sorted(SETS))
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()

    client = Client()
    payload = run(args.stage, args.set, client)
    RESULTS.mkdir(exist_ok=True)
    dest = args.out or RESULTS / f"{payload['label']}.pred.json"
    dest.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")

    print(json.dumps(payload["meta"], indent=2))
    print(None)
    print(f"gravado: {dest}")
    return 0


def x_main__mutmut_65() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=sorted(STAGES))
    ap.add_argument("--set", default="dev", choices=sorted(SETS))
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()

    client = Client()
    payload = run(args.stage, args.set, client)
    RESULTS.mkdir(exist_ok=True)
    dest = args.out or RESULTS / f"{payload['label']}.pred.json"
    dest.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")

    print(json.dumps(payload["meta"], indent=2))
    print(f"predições: {len(payload['predictions'])}  descartadas pelo gate: {len(payload['dropped_by_gate'])}")
    print(None)
    return 0


def x_main__mutmut_66() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=sorted(STAGES))
    ap.add_argument("--set", default="dev", choices=sorted(SETS))
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()

    client = Client()
    payload = run(args.stage, args.set, client)
    RESULTS.mkdir(exist_ok=True)
    dest = args.out or RESULTS / f"{payload['label']}.pred.json"
    dest.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")

    print(json.dumps(payload["meta"], indent=2))
    print(f"predições: {len(payload['predictions'])}  descartadas pelo gate: {len(payload['dropped_by_gate'])}")
    print(f"gravado: {dest}")
    return 1

mutants_x_main__mutmut['_mutmut_orig'] = x_main__mutmut_orig # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_1'] = x_main__mutmut_1 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_2'] = x_main__mutmut_2 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_3'] = x_main__mutmut_3 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_4'] = x_main__mutmut_4 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_5'] = x_main__mutmut_5 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_6'] = x_main__mutmut_6 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_7'] = x_main__mutmut_7 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_8'] = x_main__mutmut_8 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_9'] = x_main__mutmut_9 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_10'] = x_main__mutmut_10 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_11'] = x_main__mutmut_11 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_12'] = x_main__mutmut_12 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_13'] = x_main__mutmut_13 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_14'] = x_main__mutmut_14 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_15'] = x_main__mutmut_15 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_16'] = x_main__mutmut_16 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_17'] = x_main__mutmut_17 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_18'] = x_main__mutmut_18 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_19'] = x_main__mutmut_19 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_20'] = x_main__mutmut_20 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_21'] = x_main__mutmut_21 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_22'] = x_main__mutmut_22 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_23'] = x_main__mutmut_23 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_24'] = x_main__mutmut_24 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_25'] = x_main__mutmut_25 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_26'] = x_main__mutmut_26 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_27'] = x_main__mutmut_27 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_28'] = x_main__mutmut_28 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_29'] = x_main__mutmut_29 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_30'] = x_main__mutmut_30 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_31'] = x_main__mutmut_31 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_32'] = x_main__mutmut_32 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_33'] = x_main__mutmut_33 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_34'] = x_main__mutmut_34 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_35'] = x_main__mutmut_35 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_36'] = x_main__mutmut_36 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_37'] = x_main__mutmut_37 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_38'] = x_main__mutmut_38 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_39'] = x_main__mutmut_39 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_40'] = x_main__mutmut_40 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_41'] = x_main__mutmut_41 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_42'] = x_main__mutmut_42 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_43'] = x_main__mutmut_43 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_44'] = x_main__mutmut_44 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_45'] = x_main__mutmut_45 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_46'] = x_main__mutmut_46 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_47'] = x_main__mutmut_47 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_48'] = x_main__mutmut_48 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_49'] = x_main__mutmut_49 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_50'] = x_main__mutmut_50 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_51'] = x_main__mutmut_51 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_52'] = x_main__mutmut_52 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_53'] = x_main__mutmut_53 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_54'] = x_main__mutmut_54 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_55'] = x_main__mutmut_55 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_56'] = x_main__mutmut_56 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_57'] = x_main__mutmut_57 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_58'] = x_main__mutmut_58 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_59'] = x_main__mutmut_59 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_60'] = x_main__mutmut_60 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_61'] = x_main__mutmut_61 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_62'] = x_main__mutmut_62 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_63'] = x_main__mutmut_63 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_64'] = x_main__mutmut_64 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_65'] = x_main__mutmut_65 # type: ignore # mutmut generated
mutants_x_main__mutmut['x_main__mutmut_66'] = x_main__mutmut_66 # type: ignore # mutmut generated


if __name__ == "__main__":
    raise SystemExit(main())
