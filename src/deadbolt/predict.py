"""Deadzone — preditor de ponto cego de teste.

Quatro estágios cumulativos, um por iteração medida:

    baseline  prompt único, arquivo inteiro, sem taxonomia, sem gate
    s4        + taxonomia congelada de 6 tipos (docs/metric-prediction.md § 4)
    s5        + gate de evidência em código: predição cuja citação não aparece
              literalmente dentro do line_range é DESCARTADA, não corrigida
    s6        + varredura por função com reconciliação

Uso:
    DEADBOLT_MODE=live  python -m deadbolt.predict --stage baseline --set dev
    DEADBOLT_MODE=replay python -m deadbolt.predict --stage s6 --set holdout
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

from deadbolt.llm import Client  # noqa: E402
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


# --------------------------------------------------------------------- fonte

def numbered(text: str, start: int = 1) -> str:
    return "\n".join(f"{i:>4} | {ln}" for i, ln in enumerate(text.splitlines(), start=start))


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


# ---------------------------------------------------------------------- gate

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


# ----------------------------------------------------------------- execução

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


if __name__ == "__main__":
    raise SystemExit(main())
