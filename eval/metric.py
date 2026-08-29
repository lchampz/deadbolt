"""Métrica congelada do Deadzone. Ver METRIC.md § 5 e § 6.

R5: este arquivo não muda depois de 2026-08-29T16:30:00Z sem abort declarado
por escrito em METRIC.md. Qualquer alteração aqui invalida toda comparação
baseline↔solução já registrada em results/.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GROUND_TRUTH = ROOT / "data" / "ground_truth"
CORPUS = ROOT / "corpus"

TAXONOMY = {
    "unasserted_branch",
    "default_argument",
    "boundary_condition",
    "error_path",
    "output_shape",
    "dead_config",
}

SETS = {
    "dev": {
        "corpus": "python-slugify",
        "files": ["slugify/slugify.py", "slugify/special.py"],
        "test_file": "test.py",
    },
    "holdout": {
        "corpus": "python-slugify-holdout",
        "files": ["slugify/__main__.py"],
        "test_file": "test.py",
    },
    # Terceiro conjunto, outro repositório. Ver METRIC.md § 9.
    "transfer": {
        "corpus": "toolz-transfer",
        "files": ["toolz/functoolz.py"],
        "test_file": "toolz/tests/test_functoolz.py",
    },
}


@dataclass
class GroundTruth:
    name: str
    corpus: str
    files: list[str]
    survivor_lines: set[tuple[str, int]]
    killed_lines: set[tuple[str, int]]
    survivors_by_line: dict[tuple[str, int], int]
    file_lengths: dict[str, int]
    n_mutants: int
    n_survivors: int

    @classmethod
    def load(cls, name: str) -> GroundTruth:
        spec = SETS[name]
        raw = json.loads((GROUND_TRUTH / f"mutants-{spec['corpus']}.json").read_text())
        files = set(spec["files"])

        # `no tests` é a forma mais pura de ponto cego: nenhum teste sequer
        # executa a linha. Ver METRIC.md § 8 — correção declarada de 2026-08-29.
        BLIND = {"survived", "no tests"}

        surv: set[tuple[str, int]] = set()
        killed: set[tuple[str, int]] = set()
        by_line: dict[tuple[str, int], int] = {}
        n_surv = 0
        for m in raw["mutants"]:
            if m["file"] not in files:
                continue
            key = (m["file"], m["line"])
            if m["status"] in BLIND:
                surv.add(key)
                by_line[key] = by_line.get(key, 0) + 1
                n_surv += 1
            else:
                killed.add(key)
        killed -= surv  # linha com 1 sobrevivente é linha cega, mesmo com mortos junto

        lengths = {
            f: len((CORPUS / spec["corpus"] / f).read_text().splitlines())
            for f in spec["files"]
        }
        return cls(
            name=name,
            corpus=spec["corpus"],
            files=spec["files"],
            survivor_lines=surv,
            killed_lines=killed,
            survivors_by_line=by_line,
            file_lengths=lengths,
            n_mutants=sum(1 for m in raw["mutants"] if m["file"] in files),
            n_survivors=n_surv,
        )

    def source_line(self, file: str, line: int) -> str:
        text = (CORPUS / self.corpus / file).read_text().splitlines()
        return text[line - 1] if 1 <= line <= len(text) else ""


@dataclass
class Score:
    label: str
    set: str
    precision: float = 0.0
    recall: float = 0.0
    f1: float = 0.0
    near_miss_rate: float = 0.0
    noise_rate: float = 0.0
    mutant_recall: float = 0.0
    evidence_valid_rate: float = 0.0
    type_validity_rate: float = 0.0
    n_predictions: int = 0
    n_predicted_lines: int = 0
    n_hit_lines: int = 0
    n_survivor_lines: int = 0
    invalid_predictions: list[dict] = field(default_factory=list)
    meta: dict = field(default_factory=dict)

    def as_dict(self) -> dict:
        return asdict(self)


def _f1(p: float, r: float) -> float:
    return 0.0 if p + r == 0 else 2 * p * r / (p + r)


def expand(pred: dict, gt: GroundTruth) -> set[tuple[str, int]]:
    """Linhas cobertas por uma predição, recortadas no arquivo real."""
    file = pred.get("file")
    if file not in gt.file_lengths:
        return set()
    rng = pred.get("line_range") or []
    if len(rng) != 2:
        return set()
    lo, hi = int(rng[0]), int(rng[1])
    if lo > hi:
        lo, hi = hi, lo
    lo = max(1, lo)
    hi = min(gt.file_lengths[file], hi)
    return {(file, ln) for ln in range(lo, hi + 1)}


def score(predictions: list[dict], gt: GroundTruth, label: str, meta: dict | None = None) -> Score:
    s = Score(label=label, set=gt.name, meta=meta or {})
    s.n_predictions = len(predictions)
    s.n_survivor_lines = len(gt.survivor_lines)

    covered: set[tuple[str, int]] = set()
    evidence_ok = 0
    type_ok = 0

    for pred in predictions:
        lines = expand(pred, gt)
        if not lines:
            s.invalid_predictions.append({"reason": "range fora do corpus", "pred": pred})
        covered |= lines

        quote = (pred.get("evidence_quote") or "").strip()
        if quote and any(quote in gt.source_line(f, ln) for f, ln in lines):
            evidence_ok += 1
        if pred.get("blind_spot_type") in TAXONOMY:
            type_ok += 1

    P = covered
    G = gt.survivor_lines
    K = gt.killed_lines
    hits = P & G

    s.n_predicted_lines = len(P)
    s.n_hit_lines = len(hits)
    s.precision = len(hits) / len(P) if P else 0.0
    s.recall = len(hits) / len(G) if G else 0.0
    s.f1 = _f1(s.precision, s.recall)
    s.near_miss_rate = len(P & K) / len(P) if P else 0.0
    s.noise_rate = len(P - G - K) / len(P) if P else 0.0
    s.mutant_recall = (
        sum(n for key, n in gt.survivors_by_line.items() if key in P) / gt.n_survivors
        if gt.n_survivors
        else 0.0
    )
    s.evidence_valid_rate = evidence_ok / len(predictions) if predictions else 0.0
    s.type_validity_rate = type_ok / len(predictions) if predictions else 0.0
    return s
