"""Tabela final do Deadzone: pisos, teto, e cada estágio medido.

Roda sem chave de API. Estágio sem gravação em recordings/ aparece como
"não medido" — nunca é omitido, nunca é preenchido por estimativa.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "eval"))
sys.path.insert(0, str(ROOT / "src"))

from metric import SETS, GroundTruth, score  # noqa: E402
from run import sanity  # noqa: E402

RESULTS = ROOT / "results"
STAGE_ORDER = ["baseline", "s4", "s5", "s6"]
STAGE_LABEL = {
    "baseline": "S3 baseline — prompt único",
    "s4": "S4 + taxonomia congelada",
    "s5": "S5 + gate de evidência",
    "s6": "S6 + varredura por função",
}

COLS = [("precision", "prec"), ("recall", "rec"), ("f1", "F1"),
        ("near_miss_rate", "near"), ("noise_rate", "noise"),
        ("mutant_recall", "mut-rec"), ("evidence_valid_rate", "evid")]


def fmt(rows: list[tuple[str, object]]) -> str:
    head = f"{'':<34}" + "".join(f"{h:>9}" for _, h in COLS) + f"{'#pred':>7}{'#lin':>7}{'US$':>9}"
    out = [head, "-" * len(head)]
    for name, s in rows:
        if s is None:
            out.append(f"{name:<34}{'— não medido (sem gravação em recordings/) —':>60}")
            continue
        cells = "".join(f"{getattr(s, k):>9.3f}" for k, _ in COLS)
        cost = s.meta.get("cost_usd", 0.0) if s.meta else 0.0
        out.append(f"{name:<34}{cells}{s.n_predictions:>7}{s.n_predicted_lines:>7}{cost:>9.4f}")
    return "\n".join(out)


def stage_score(stage: str, set_name: str):
    path = RESULTS / f"{stage}-{set_name}.pred.json"
    if not path.exists():
        return None
    payload = json.loads(path.read_text())
    gt = GroundTruth.load(set_name)
    return score(payload["predictions"], gt, f"{stage}-{set_name}", payload.get("meta"))


def main() -> int:
    print("# Deadzone — tabela final\n")
    print("Ground truth: mutmut 3.7.0 sobre python-slugify @ 7b6d5d96, congelado em S1.")
    print("Métrica congelada em METRIC.md § 5. Nenhum número abaixo mudou de definição depois de medido.\n")

    for set_name in ("dev", "holdout", "transfer"):
        gt = GroundTruth.load(set_name)
        c1, c2, c3, c4 = sanity(set_name)
        print(f"\n## Conjunto {set_name.upper()} — {', '.join(gt.files)}")
        print(
            f"{gt.n_mutants} mutantes · {gt.n_survivors} sobreviventes · "
            f"|G|={len(gt.survivor_lines)} linhas cegas · N={sum(gt.file_lengths.values())} linhas\n"
        )
        rows: list[tuple[str, object]] = [
            ("PISO prever o arquivo inteiro", c1),
            ("PISO aleatório, mesmo orçamento", c3),
        ]
        for st in STAGE_ORDER:
            rows.append((STAGE_LABEL[st], stage_score(st, set_name)))
        rows.append(("TETO oráculo (= ground truth)", c4))
        print(fmt(rows))

        measured = [(st, stage_score(st, set_name)) for st in STAGE_ORDER]
        measured = [(st, s) for st, s in measured if s is not None]
        if len(measured) >= 2:
            print("\n### Delta por iteração (F1)")
            for (pst, ps), (cst, cs) in zip(measured, measured[1:]):
                d = cs.f1 - ps.f1
                verdict = "mantida" if d > 0 else "REMOVIDA — não moveu a métrica"
                print(f"  {pst:>8} → {cst:<8} ΔF1 {d:+.3f}   {verdict}")
        elif not measured:
            print("\n  Nenhum estágio medido ainda. Ver README § Status.")
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
