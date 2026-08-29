"""Tabela final da geração de testes: antes, depois, e o que a guarda evitou.

Roda sem chave. Estágio sem resultado aparece como não medido, nunca omitido.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
STAGES = [
    ("B", "B  baseline ingênuo"),
    ("T1", "T1 + alvo (diffs dos mutantes)"),
    ("T2", "T2 + guardas G1/G2/G3"),
    ("T3", "T3 + reparo com feedback"),
]
SETS = [("dev", "DEV — slugify.py + special.py"),
        ("holdout", "HOLDOUT — __main__.py"),
        ("transfer", "TRANSFER — toolz/functoolz.py")]


def load(stage: str, set_name: str) -> dict | None:
    p = RESULTS / f"testgen-{stage}-{set_name}.json"
    return json.loads(p.read_text()) if p.exists() else None


def main() -> int:
    print("# Deadbolt — geração de testes verificada\n")
    print("Métrica congelada em METRIC_TESTGEN.md antes de qualquer geração.")
    print("Mutation score medido re-executando mutmut; só a suíte muda, o fonte nunca —")
    print("os IDs de mutante são estáveis, então cada morte é nomeável e conferível.\n")

    for set_name, label in SETS:
        rows = [(s, lbl, load(s, set_name)) for s, lbl in STAGES]
        if not any(d for _, _, d in rows):
            continue
        base = next(d for _, _, d in rows if d)["meta"]
        print(f"\n## {label}")
        print(f"{base['mutants_total']} mutantes · {base['killed_before']} já mortos · "
              f"{base['survivors_attacked']} sobreviventes atacados · "
              f"score de partida **{base['score_before']:.4f}**\n")

        head = (f"{'':<32}{'score':>8}{'Δ':>8}{'+mata':>7}{'testes':>8}"
                f"{'cru ok':>8}{'desc.':>7}{'recusa':>8}{'US$':>8}")
        print(head)
        print("-" * len(head))
        for stage, lbl, d in rows:
            if d is None:
                print(f"{lbl:<32}{'— não medido —':>39}")
                continue
            m = d["meta"]
            delta = m["score_after"] - m["score_before"]
            descartados = (m.get("dropped_duplicate_name", 0)
                           + m.get("dropped_failing_on_original", 0)
                           + m.get("n_rejected_by_guards", 0))
            print(f"{lbl:<32}{m['score_after']:>8.4f}{delta:>+8.4f}"
                  f"{m['newly_killed']:>7}{m['filtrado_n_tests']:>8}"
                  f"{str(m['cru_suite_green']):>8}{descartados:>7}"
                  f"{m['n_model_declined']:>8}{m.get('cost_usd', 0):>8.2f}")

        # o que o cru esconde
        print()
        for stage, lbl, d in rows:
            if d is None:
                continue
            m = d["meta"]
            if not m["cru_suite_green"]:
                print(f"  ⚠ {stage}: commitado como veio, **quebra a suíte** "
                      f"({m['cru_n_tests']} testes gerados, "
                      f"{m['dropped_duplicate_name']} com nome repetido, "
                      f"{m['dropped_failing_on_original']} vermelhos no original)")

    print("\nLegenda: `cru ok` = a suíte continua verde se você commitar a saída do")
    print("modelo sem nenhuma guarda. `desc.` = testes descartados. `recusa` = mutantes")
    print("que o modelo declarou indetectáveis, com justificativa — entrada da camada 2.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
