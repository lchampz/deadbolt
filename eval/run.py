"""Harness de avaliação do Deadzone.

    python eval/run.py --predictions results/baseline.json
    python eval/run.py --sanity          # roda os 3 controles de sanidade

O harness roda ANTES de existir solução (guardrail do S2): se ele der número bom
para predição deliberadamente errada, ele está quebrado.
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from metric import SETS, GroundTruth, score  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"

COLS = [
    ("precision", "prec"),
    ("recall", "rec"),
    ("f1", "F1"),
    ("near_miss_rate", "near"),
    ("noise_rate", "noise"),
    ("mutant_recall", "mut-rec"),
    ("evidence_valid_rate", "evid"),
    ("type_validity_rate", "type"),
]


def table(scores: list) -> str:
    head = f"{'label':<26} {'set':<8} " + " ".join(f"{h:>7}" for _, h in COLS) + f" {'#pred':>6} {'#lin':>6}"
    rows = [head, "-" * len(head)]
    for s in scores:
        cells = " ".join(f"{getattr(s, k):>7.3f}" for k, _ in COLS)
        rows.append(f"{s.label:<26} {s.set:<8} {cells} {s.n_predictions:>6} {s.n_predicted_lines:>6}")
    return "\n".join(rows)


def sanity(set_name: str = "dev") -> list:
    """Três controles. Se algum sair fora do esperado, o harness está quebrado."""
    gt = GroundTruth.load(set_name)
    out = []

    # C1 — prever o arquivo inteiro: recall 1.000, precisão ~|G|/N, F1 baixo
    everything = [
        {"file": f, "line_range": [1, n], "blind_spot_type": "dead_config",
         "evidence_quote": "", "confidence": 1.0}
        for f, n in gt.file_lengths.items()
    ]
    out.append(score(everything, gt, "C1-prevê-tudo"))

    # C2 — predição fabricada à mão, deliberadamente errada: linhas de import/def
    wrong = [
        {"file": gt.files[0], "line_range": [1, 3], "blind_spot_type": "boundary_condition",
         "evidence_quote": "import re", "confidence": 0.9},
        {"file": gt.files[0], "line_range": [5, 8], "blind_spot_type": "nao_existe_na_taxonomia",
         "evidence_quote": "texto que não está no arquivo", "confidence": 0.9},
        {"file": gt.files[-1], "line_range": [1, 2], "blind_spot_type": "error_path",
         "evidence_quote": "from __future__ import annotations", "confidence": 0.9},
    ]
    out.append(score(wrong, gt, "C2-fabricada-errada"))

    # C3 — aleatório com o mesmo orçamento de linhas do oráculo
    rng = random.Random(20260829)
    budget = len(gt.survivor_lines)
    pool = [(f, ln) for f, n in gt.file_lengths.items() for ln in range(1, n + 1)]
    picks = rng.sample(pool, budget)
    rand = [
        {"file": f, "line_range": [ln, ln], "blind_spot_type": "unasserted_branch",
         "evidence_quote": gt.source_line(f, ln).strip(), "confidence": 0.5}
        for f, ln in picks
    ]
    out.append(score(rand, gt, "C3-aleatório-mesmo-orçamento"))

    # C4 — oráculo: exatamente as linhas de G. Teto da métrica.
    oracle = [
        {"file": f, "line_range": [ln, ln], "blind_spot_type": "unasserted_branch",
         "evidence_quote": gt.source_line(f, ln).strip(), "confidence": 1.0}
        for f, ln in sorted(gt.survivor_lines)
    ]
    out.append(score(oracle, gt, "C4-oráculo"))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--predictions", type=Path)
    ap.add_argument("--set", default="dev", choices=sorted(SETS))
    ap.add_argument("--label")
    ap.add_argument("--sanity", action="store_true")
    ap.add_argument("--save", action="store_true", help="grava em results/")
    args = ap.parse_args()

    if args.sanity:
        scores = sanity(args.set)
        print(table(scores))
        print()
        gt = GroundTruth.load(args.set)
        print(
            f"conjunto '{args.set}': {gt.n_mutants} mutantes, {gt.n_survivors} sobreviventes, "
            f"|G|={len(gt.survivor_lines)} linhas cegas, |K|={len(gt.killed_lines)} linhas mutáveis cobertas, "
            f"N={sum(gt.file_lengths.values())} linhas de arquivo"
        )
        c1, c2, c3, c4 = scores
        density = len(gt.survivor_lines) / sum(gt.file_lengths.values())
        checks = {
            "C1 recall == 1.000 (prever tudo pega tudo)": abs(c1.recall - 1.0) < 1e-9,
            "C1 precisão == densidade de G": abs(c1.precision - density) < 1e-6,
            "C2 F1 == 0.000 (fabricada errada não pontua)": c2.f1 == 0.0,
            "C2 flagra citação inventada": c2.evidence_valid_rate < 1.0,
            "C2 flagra tipo fora da taxonomia": c2.type_validity_rate < 1.0,
            "C3 aleatório <= densidade + folga": c3.f1 <= density + 0.10,
            "C4 oráculo F1 == 1.000 (teto atingível)": abs(c4.f1 - 1.0) < 1e-9,
            "C1 < C4 (piso trivial abaixo do teto)": c1.f1 < c4.f1,
        }
        print()
        for name, passed in checks.items():
            print(f"  [{'ok' if passed else 'FALHOU'}] {name}")
        print()
        print(
            f"PISO TRIVIAL neste conjunto: F1 {c1.f1:.3f} (prever o arquivo inteiro).\n"
            f"Nenhum número de solução significa nada sem estar ao lado deste piso."
        )
        ok = all(checks.values())
        print("SANIDADE:", "OK — harness discrimina" if ok else "FALHOU — harness não discrimina")
        return 0 if ok else 1

    if not args.predictions:
        ap.error("--predictions ou --sanity")

    payload = json.loads(args.predictions.read_text())
    set_name = payload.get("set", args.set)
    label = args.label or payload.get("label") or args.predictions.stem
    gt = GroundTruth.load(set_name)
    s = score(payload["predictions"], gt, label, payload.get("meta"))
    print(table([s]))

    if args.save:
        RESULTS.mkdir(exist_ok=True)
        out = s.as_dict()
        out["timestamp"] = datetime.now(timezone.utc).isoformat()
        out["ground_truth_sha"] = gt.corpus
        dest = RESULTS / f"{label}.json"
        dest.write_text(json.dumps(out, indent=2) + "\n")
        print(f"\ngravado: {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
