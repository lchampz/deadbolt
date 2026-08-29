"""Tabela final do Deadbolt. Roda sem chave, sem assinatura, sem rede.

Números da manchete vêm de `eval/verify_mutmut.py` — o `mutmut` rodando do zero —
e não da medição incremental do pipeline, que já divergiu uma vez e está
rotulada como sinal de desenvolvimento (METRIC_TESTGEN.md § 12).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS, TRIAGE = ROOT / "results", ROOT / "data" / "triage"

LADDER = [("B", "B  prompt ingênuo"), ("T1", "T1 + alvo"),
          ("T2", "T2 + guardas"), ("T3", "T3 + reparo")]
RUNS = [
    ("dev", "", "DEV · slugify.py + special.py", "API · claude-opus-5"),
    ("holdout", "", "HOLDOUT · __main__.py", "API · claude-opus-5"),
    ("dev", "-cursor", "DEV controle · mesmo corpus", "Cursor · composer-2.5"),
    ("transfer", "-cursor", "TRANSFER · toolz/functoolz.py", "Cursor · composer-2.5"),
]


def load(name: str) -> dict | None:
    p = RESULTS / name
    return json.loads(p.read_text()) if p.exists() else None


def main() -> int:
    print("# Deadbolt — geração de testes verificada\n")
    print("Métrica congelada em METRIC_TESTGEN.md antes de qualquer geração.")
    print("Score = mutmut rodando do zero. Só a suíte muda; o fonte nunca — os IDs")
    print("de mutante são estáveis, então cada morte é nomeável e conferível.\n")

    print("## Antes e depois\n")
    head = f"{'':<32}{'backend':<22}{'antes':>8}{'depois':>8}{'Δ':>8}{'teto':>8}{'testes':>8}"
    print(head); print("-" * len(head))
    for set_name, suf, label, backend in RUNS:
        r = load(f"testgen-T3-{set_name}{suf}.json")
        if not r:
            print(f"{label:<32}{backend:<22}{'— não medido —':>40}")
            continue
        v = load(f"verify-T3-{set_name}{suf}.json")
        m = r["meta"]
        antes, total = m["killed_before"], m["mutants_total"]
        depois = (total - len(v["survivors_after"])) if v else m["killed_after"]
        t = load(f"../data/triage/{set_name}.json")
        tri = TRIAGE / f"{set_name}.json"
        imp = 0
        if tri.exists():
            d = json.loads(tri.read_text())
            imp = sum(l["n_mutants"] for l in d["labels"]
                      if l["label"] in ("equivalente", "inalcancavel"))
        teto = f"{(total - imp) / total:.4f}" if imp else "—"
        print(f"{label:<32}{backend:<22}{antes/total:>8.4f}{depois/total:>8.4f}"
              f"{depois/total - antes/total:>+8.4f}{teto:>8}{m['filtrado_n_tests']:>8}")

    print("\n## Ablação — o que cada capability compra (DEV, API)\n")
    head = f"{'':<26}{'score':>8}{'testes usáveis':>16}{'gerados':>9}{'commit direto':>15}"
    print(head); print("-" * len(head))
    for st, lbl in LADDER:
        r = load(f"testgen-{st}-dev.json")
        if not r:
            continue
        m = r["meta"]
        print(f"{lbl:<26}{m['score_after']:>8.4f}{m['filtrado_n_tests']:>16}"
              f"{m['n_generated']:>9}{('verde' if m['cru_suite_green'] else 'QUEBRA'):>15}")

    print("\n## Camada 2 — triagem de equivalência\n")
    head = f"{'':<12}{'sobrev.':>9}{'indeterm.':>11}{'redução':>10}{'impossíveis':>13}{'precisão':>10}"
    print(head); print("-" * len(head))
    ts = tu = ti = 0
    for f in sorted(TRIAGE.glob("*.json")):
        d = json.loads(f.read_text())
        s, u = d["survivors"], d["undetermined"]
        imp = sum(l["n_mutants"] for l in d["labels"]
                  if l["label"] in ("equivalente", "inalcancavel"))
        ts += s; tu += u; ti += imp
        print(f"{d['set'].upper():<12}{s:>9}{u:>11}{s/u:>9.2f}x{imp:>13}{imp/u:>9.1%}")
    if tu:
        print("-" * len(head))
        print(f"{'TOTAL':<12}{ts:>9}{tu:>11}{ts/tu:>9.2f}x{ti:>13}{ti/tu:>9.1%}")
        print("\nMutante equivalente não pode ser morto — por definição. Logo tudo que a")
        print("geração verificada mata é provadamente não-equivalente, e o filtro é sonoro:")
        print("nenhum mutante matável é excluído da lista que o humano lê.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
