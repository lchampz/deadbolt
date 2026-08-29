"""Exporta as trajetórias dos agentes — entregável obrigatório do brief.

Uma trajetória = instrução → ações → feedback → resultado. Aqui, por estágio:

    instrução  system prompt + prompt de usuário (versionados em prompts/)
    ações      as chamadas de modelo, uma por unidade (arquivo ou função)
    feedback   o que o gate de evidência descartou e por quê
    resultado  as predições que sobreviveram e a pontuação contra o ground truth

Lê `recordings/` e `results/`. Não faz chamada de rede. Não inventa nada:
estágio sem gravação sai como ausente.

    python scripts/export_trajectories.py            # markdown em docs/trajectories/
    python scripts/export_trajectories.py --json     # também o bundle JSON
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "eval"))
sys.path.insert(0, str(ROOT / "src"))

from metric import GroundTruth, score  # noqa: E402

RECORDINGS = ROOT / "recordings"
RESULTS = ROOT / "results"
OUT = ROOT / "docs" / "trajectories"
STAGES = ["baseline", "s4", "s5", "s6"]
SETS = ["dev", "holdout", "transfer"]


def load_recordings() -> dict[str, dict]:
    out = {}
    for f in sorted(RECORDINGS.glob("*.json")):
        try:
            out[f.stem] = json.loads(f.read_text())
        except json.JSONDecodeError:
            out[f.stem] = {"error": f"gravação ilegível: {f.name}"}
    return out


def trim(text: str, limit: int = 1400) -> str:
    text = (text or "").strip()
    if len(text) <= limit:
        return text
    return text[:limit] + f"\n… [{len(text) - limit} chars omitidos — íntegra em recordings/]"


def render(stage: str, set_name: str, recs: dict) -> str | None:
    pred_path = RESULTS / f"{stage}-{set_name}.pred.json"
    if not pred_path.exists():
        return None
    payload = json.loads(pred_path.read_text())
    gt = GroundTruth.load(set_name)
    s = score(payload["predictions"], gt, f"{stage}-{set_name}", payload.get("meta"))

    calls = [r for r in recs.values() if r.get("stage") == stage and r.get("unit")]
    calls.sort(key=lambda r: r.get("unit", ""))

    L = [
        f"# Trajetória — {stage} · conjunto {set_name}",
        "",
        f"Modelo `{payload['meta'].get('model','?')}` · provider "
        f"`{payload['meta'].get('provider','?')}` · modo `{payload['meta'].get('mode','?')}`",
        f"Custo US$ {payload['meta'].get('cost_usd', 0):.4f} · "
        f"{payload['meta'].get('input_tokens',0)} tokens de entrada · "
        f"{payload['meta'].get('output_tokens',0)} de saída · "
        f"{payload['meta'].get('wall_seconds',0)}s de parede",
        "",
        "## Resultado, contra o ground truth congelado",
        "",
        f"| precisão | recall | F1 | near-miss | ruído | mut-recall | evidência |",
        f"|---:|---:|---:|---:|---:|---:|---:|",
        f"| {s.precision:.3f} | {s.recall:.3f} | {s.f1:.3f} | {s.near_miss_rate:.3f} | "
        f"{s.noise_rate:.3f} | {s.mutant_recall:.3f} | {s.evidence_valid_rate:.3f} |",
        "",
        f"Piso trivial deste conjunto e teto do oráculo em `eval/report.py`.",
        "",
        "## Ações — uma chamada por unidade",
        "",
    ]
    if not calls:
        L.append("_Nenhuma gravação casada com este estágio em `recordings/`._\n")
    for i, c in enumerate(calls, 1):
        L += [
            f"### {i}. `{c.get('unit')}`",
            "",
            f"gravação `{c.get('key')}` · {c.get('input_tokens',0)}→{c.get('output_tokens',0)} tokens "
            f"· US$ {c.get('cost_usd',0):.4f} · {c.get('wall_seconds',0)}s · {c.get('timestamp','')}",
            "",
            "<details><summary>instrução (prompt de usuário)</summary>",
            "",
            "```",
            trim(c.get("prompt", "")),
            "```",
            "</details>",
            "",
            "<details><summary>resposta crua do modelo</summary>",
            "",
            "```",
            trim(c.get("response", "")),
            "```",
            "</details>",
            "",
        ]
        if c.get("error"):
            L += [f"**erro registrado:** `{c['error']}`", ""]

    dropped = payload.get("dropped_by_gate", [])
    L += ["## Feedback — o que o gate de evidência descartou", ""]
    if not payload["meta"].get("gate_applied"):
        L.append("_Gate não aplicado neste estágio._\n")
    elif not dropped:
        L.append("_Nenhuma predição descartada._\n")
    else:
        L.append(f"{len(dropped)} predições descartadas por âncora inválida:\n")
        for d in dropped[:25]:
            L.append(
                f"- `{d.get('file')}` {d.get('line_range')} — citação "
                f"`{trim(str(d.get('evidence_quote')), 90)}` não aparece no intervalo"
            )
        if len(dropped) > 25:
            L.append(f"- … e mais {len(dropped) - 25}")
        L.append("")

    L += ["## Predições que sobreviveram", ""]
    for p in payload["predictions"][:60]:
        L.append(
            f"- `{p.get('file')}:{p.get('line_range')}` · **{p.get('blind_spot_type')}** "
            f"· conf {p.get('confidence')} — {p.get('rationale','')}"
        )
    if len(payload["predictions"]) > 60:
        L.append(f"- … e mais {len(payload['predictions']) - 60}")
    return "\n".join(L) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    recs = load_recordings()
    OUT.mkdir(parents=True, exist_ok=True)
    written, missing = [], []

    for stage in STAGES:
        for set_name in SETS:
            md = render(stage, set_name, recs)
            if md is None:
                missing.append(f"{stage}-{set_name}")
                continue
            dest = OUT / f"{stage}-{set_name}.md"
            dest.write_text(md)
            written.append(dest.name)

    index = [
        "# Trajetórias dos agentes",
        "",
        "Instrução → ações → feedback → resultado, por estágio. Geradas de",
        "`recordings/` e `results/` por `scripts/export_trajectories.py`.",
        "Nada aqui é redigido à mão; estágio sem gravação aparece como ausente.",
        "",
        f"Gravações em `recordings/`: **{len(recs)}**",
        "",
    ]
    index += [f"- [{n}]({n})" for n in written] or ["_Nenhuma trajetória exportada ainda._"]
    if missing:
        index += ["", "Ausentes (sem predição registrada): " + ", ".join(f"`{m}`" for m in missing)]
    (OUT / "README.md").write_text("\n".join(index) + "\n")

    if args.json:
        (OUT / "bundle.json").write_text(
            json.dumps({"recordings": recs, "exported": written, "missing": missing},
                       indent=2, ensure_ascii=False) + "\n"
        )

    print(f"trajetórias exportadas: {len(written)}  ausentes: {len(missing)}")
    print(f"gravações lidas: {len(recs)}")
    print(f"destino: {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
