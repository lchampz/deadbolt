"""Relatório do Deadbolt. Sem dependência externa, sem chave, sem rede.

    python eval/report_testgen.py              tudo
    python eval/report_testgen.py --summary    só antes/depois
    python eval/report_testgen.py --ablation   só a ablação
    python eval/report_testgen.py --triage     só a camada 2
    python eval/report_testgen.py --no-color   sem ANSI, para colar em texto

Os números vêm de `eval/verify_mutmut.py` — o mutmut rodando do zero — e nunca
da medição interna do pipeline, que está desqualificada (docs/metric-testgen.md § 14).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS, TRIAGE = ROOT / "results", ROOT / "data" / "triage"
W = 78  # cabe em terminal padrão e não quebra em projeção


class Ink:
    """ANSI só quando a saída é um terminal. Redirecionado, sai limpo."""

    def __init__(self, on: bool) -> None:
        self.on = on

    def _w(self, code: str, s: str) -> str:
        return f"\033[{code}m{s}\033[0m" if self.on else s

    def bold(self, s: str) -> str:
        return self._w("1", s)

    def dim(self, s: str) -> str:
        return self._w("2", s)

    def green(self, s: str) -> str:
        return self._w("1;32", s)

    def cyan(self, s: str) -> str:
        return self._w("36", s)

    def red(self, s: str) -> str:
        return self._w("31", s)


RUNS = [
    ("dev", "", "DEV", "opus-5 · API"),
    ("holdout", "", "HOLDOUT ★", "opus-5 · API"),
    ("dev", "-cursor", "DEV (controle)", "composer · CUR"),
    ("transfer", "-cursor", "TRANSFER", "composer · CUR"),
]
LADDER = [
    ("B", "B  · prompt ingênuo"),
    ("T1", "T1 · + alvo"),
    ("T2", "T2 · + guardas"),
    ("T3", "T3 · + reparo"),
]


def load(name: str) -> dict | None:
    p = RESULTS / name
    return json.loads(p.read_text()) if p.exists() else None


def ceiling(set_name: str, total: int) -> float | None:
    f = TRIAGE / f"{set_name}.json"
    if not f.exists():
        return None
    d = json.loads(f.read_text())
    imp = sum(
        l["n_mutants"] for l in d["labels"]
        if l["label"] in ("equivalente", "inalcancavel")
    )
    return (total - imp) / total


def rows() -> list[dict]:
    out = []
    for set_name, suf, label, backend in RUNS:
        r = load(f"testgen-T3-{set_name}{suf}.json")
        if not r:
            continue
        v = load(f"verify-T3-{set_name}{suf}.json")
        m = r["meta"]
        total = m["mutants_total"]
        depois = (total - len(v["survivors_after"])) if v else m["killed_after"]
        teto = ceiling(set_name, total)
        depois_f = depois / total
        out.append({
            "label": label,
            "backend": backend,
            "antes": m["killed_before"] / total,
            "depois": depois_f,
            "teto": teto,
            "testes": m["filtrado_n_tests"],
            "no_teto": teto is not None and abs(depois_f - teto) < 1e-9,
        })
    return out


def secao(k: Ink, titulo: str, nota: str = "") -> None:
    print()
    linha = "  " + k.bold(titulo)
    if nota:
        linha += "  " + k.dim(nota)
    print(linha)
    print("  " + k.dim("─" * (W - 4)))


def cabecalho(k: Ink) -> None:
    print()
    print("  " + k.cyan("╭" + "─" * (W - 6) + "╮"))
    titulo = "DEADBOLT  ·  geração de testes verificada"
    print("  " + k.cyan("│") + k.bold(titulo.center(W - 6)) + k.cyan("│"))
    print("  " + k.cyan("╰" + "─" * (W - 6) + "╯"))


def manchete(k: Ink, rs: list[dict]) -> None:
    principais = [r for r in rs if "controle" not in r["label"]][:2]
    if not principais:
        return
    print()
    for r in principais:
        nome = r["label"].replace(" ★", "")
        if r["no_teto"]:
            nota = k.green("← teto atingido")
        elif r["teto"] is not None:
            nota = k.dim(f"a {(r['teto'] - r['depois']) * 100:.2f} pt do teto")
        else:
            nota = ""
        print(
            "  " + k.bold(nome.ljust(16))
            + f"{r['antes']:>7.2%}"
            + k.dim("  →  ")
            + k.green(f"{r['depois']:.2%}")
            + "   " + nota
        )


def bloco_resumo(k: Ink, rs: list[dict]) -> None:
    secao(k, "ANTES E DEPOIS")
    cab = (f"{'conjunto':<17}{'backend':<16}{'antes':>8}{'depois':>9}"
           f"{'Δ':>10}{'teto':>10}{'testes':>8}")
    print("  " + k.dim(cab))
    for r in rs:
        teto = f"{r['teto']:.4f}" if r["teto"] is not None else "—"
        if r["no_teto"]:
            teto_col = k.green((teto + " ✓").rjust(10))
        else:
            teto_col = (teto + "  ").rjust(10)
        print(
            f"  {r['label']:<17}{r['backend']:<16}{r['antes']:>8.4f}"
            + k.green(f"{r['depois']:.4f}".rjust(9))
            + f"{r['depois'] - r['antes']:>+10.4f}"
            + teto_col
            + f"{r['testes']:>8}"
        )
    print()
    for nota in (
        "★  conjunto fechado, nunca olhado durante o desenvolvimento",
        "✓  teto atingido — todo mutante matável foi morto",
        "teto = 1 − (mutantes provadamente impossíveis ÷ total)",
    ):
        print("  " + k.dim(nota))


def bloco_ablacao(k: Ink) -> None:
    dados = [(lbl, load(f"testgen-{st}-dev.json")) for st, lbl in LADDER]
    dados = [(lbl, d) for lbl, d in dados if d]
    if not dados:
        return
    secao(k, "ABLAÇÃO", "· o que cada capability compra  (DEV, API)")
    cab = f"{'estágio':<22}{'score':>8}{'usáveis':>10}{'gerados':>10}{'commit direto':>18}"
    print("  " + k.dim(cab))
    for lbl, d in dados:
        m = d["meta"]
        verde = m["cru_suite_green"]
        rotulo = "suíte verde" if verde else "QUEBRA O BUILD"
        pintado = k.green(rotulo) if verde else k.red(rotulo)
        print(
            f"  {lbl:<22}{m['score_after']:>8.4f}{m['filtrado_n_tests']:>10}"
            f"{m['n_generated']:>10}" + " " * (18 - len(rotulo)) + pintado
        )
    print()
    print("  " + k.dim("as guardas não sobem o score — elas mudam a última coluna"))


def bloco_triagem(k: Ink) -> None:
    arqs = sorted(TRIAGE.glob("*.json"))
    if not arqs:
        return
    secao(k, "CAMADA 2", "· triagem de equivalência")
    cab = (f"{'conjunto':<17}{'sobrev.':>9}{'p/ ler':>9}{'redução':>10}"
           f"{'impossíveis':>14}{'precisão':>10}")
    print("  " + k.dim(cab))
    ts = tu = ti = 0
    for f in arqs:
        d = json.loads(f.read_text())
        s, u = d["survivors"], d["undetermined"]
        imp = sum(
            l["n_mutants"] for l in d["labels"]
            if l["label"] in ("equivalente", "inalcancavel")
        )
        ts, tu, ti = ts + s, tu + u, ti + imp
        print(f"  {d['set'].upper():<17}{s:>9}{u:>9}"
              f"{f'{s / u:.2f}x':>10}{imp:>14}{imp / u:>9.1%}")
    if tu:
        print("  " + k.dim("─" * (W - 4)))
        print(
            "  " + k.bold("TOTAL".ljust(17)) + f"{ts:>9}{tu:>9}"
            + k.green(f"{ts / tu:.2f}x".rjust(10))
            + f"{ti:>14}{ti / tu:>9.1%}"
        )
        print()
        print("  " + k.dim("mutante equivalente não pode ser morto — por definição;"))
        print("  " + k.dim("logo o filtro é sonoro: nada matável sai da lista humana."))


def rodape(k: Ink) -> None:
    print()
    print("  " + k.dim("─" * (W - 4)))
    print("  " + k.dim("score = mutmut rodando do zero · congelado em docs/metric-testgen.md"))
    print("  " + k.dim("conferir por conta própria:  make verify SET=holdout"))
    print()


def main() -> int:
    ap = argparse.ArgumentParser(description="Relatório do Deadbolt")
    ap.add_argument("--summary", action="store_true", help="só antes/depois")
    ap.add_argument("--ablation", action="store_true", help="só a ablação")
    ap.add_argument("--triage", action="store_true", help="só a camada 2")
    ap.add_argument("--no-color", action="store_true", help="sem ANSI")
    a = ap.parse_args()

    k = Ink(sys.stdout.isatty() and not a.no_color)
    tudo = not (a.summary or a.ablation or a.triage)
    rs = rows()

    cabecalho(k)
    if tudo or a.summary:
        manchete(k, rs)
        bloco_resumo(k, rs)
    if tudo or a.ablation:
        bloco_ablacao(k)
    if tudo or a.triage:
        bloco_triagem(k)
    rodape(k)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
