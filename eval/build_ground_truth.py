"""Converte a saída do mutmut em ground truth estruturado.

Contrato: roda DEPOIS de `mutmut run` dentro de corpus/python-slugify.
Não inspeciona o conteúdo dos sobreviventes para tomar decisão — só transcreve.

Mapeamento de linha (verificado empiricamente em S1):
    mutmut show emite um diff unificado da FUNÇÃO extraída, não do arquivo.
    A linha original = linha do `def` + linha relativa no hunk - 1.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORPUS_NAME = sys.argv[1] if len(sys.argv) > 1 else "python-slugify"
CORPUS = ROOT / "corpus" / CORPUS_NAME
_venv_mutmut = CORPUS / ".venv" / "bin" / "mutmut"
# no container não há venv por corpus; cai para o mutmut do PATH
MUTMUT = _venv_mutmut.resolve() if _venv_mutmut.exists() else Path("mutmut")
SPINNER = re.compile(r"[⠀-⣿]")

# mutmut nomeia o mutante como <modulo>.x_<funcao>__mutmut_<n>
MUTANT_RE = re.compile(r"^\s*([\w.]+)\.x_(\w+)__mutmut_(\d+):\s*(\w+)\s*$")
HUNK_RE = re.compile(r"^@@ -(\d+),\d+ \+\d+,\d+ @@")


def _clean(raw: str) -> str:
    return SPINNER.sub("", raw.replace("\r", "\n"))


def _run(args: list[str]) -> str:
    out = subprocess.run(
        [str(MUTMUT), *args], cwd=CORPUS, capture_output=True, text=True
    )
    return _clean(out.stdout + out.stderr)


def def_lines(path: Path) -> dict[str, int]:
    """Linha 1-based onde cada `def <nome>` começa."""
    found: dict[str, int] = {}
    for i, line in enumerate(path.read_text().splitlines(), start=1):
        m = re.match(r"^\s*def\s+(\w+)\s*\(", line)
        if m and m.group(1) not in found:
            found[m.group(1)] = i
    return found


def list_mutants() -> list[dict]:
    mutants = []
    for line in _run(["results", "--all", "True"]).splitlines():
        m = MUTANT_RE.match(line)
        if m:
            module, func, idx, status = m.groups()
            mutants.append(
                {
                    "id": f"{module}.x_{func}__mutmut_{idx}",
                    "module": module,
                    "function": func,
                    "status": status,
                }
            )
    return mutants


def parse_show(mutant: dict, defs: dict[str, dict[str, int]]) -> dict:
    text = _run(["show", mutant["id"]])
    file_path, rel_start, removed, added = None, None, [], []
    offset = None
    for line in text.splitlines():
        if line.startswith("--- "):
            file_path = line[4:].strip()
            continue
        h = HUNK_RE.match(line)
        if h:
            rel_start = int(h.group(1))
            offset = 0
            continue
        if rel_start is None:
            continue
        if line.startswith("-") and not line.startswith("---"):
            if not removed:
                # primeira linha removida define a posição
                mutant["_rel"] = rel_start + offset
            removed.append(line[1:])
        elif line.startswith("+") and not line.startswith("+++"):
            added.append(line[1:])
        else:
            if not removed:
                offset += 1

    if file_path is None or "_rel" not in mutant:
        mutant["error"] = "diff não parseável"
        return mutant

    def_line = defs.get(file_path, {}).get(mutant["function"])
    if def_line is None:
        mutant["error"] = f"função {mutant['function']} não encontrada em {file_path}"
        return mutant

    mutant["file"] = file_path
    mutant["line"] = def_line + mutant.pop("_rel") - 1
    mutant["original"] = removed[0].strip() if removed else ""
    mutant["mutated"] = added[0].strip() if added else ""
    return mutant


def main() -> int:
    mutants = list_mutants()
    if not mutants:
        print("ERRO: mutmut results não retornou mutantes", file=sys.stderr)
        return 1

    files = sorted({m["module"].replace(".", "/") + ".py" for m in mutants})
    defs = {f: def_lines(CORPUS / f) for f in files}

    with ThreadPoolExecutor(max_workers=8) as pool:
        parsed = list(pool.map(lambda m: parse_show(m, defs), mutants))

    errors = [m for m in parsed if "error" in m]
    ok = [m for m in parsed if "error" not in m]

    # sanidade: a linha original citada tem que bater com o arquivo real
    mismatches = []
    for m in ok:
        actual = (CORPUS / m["file"]).read_text().splitlines()[m["line"] - 1].strip()
        if actual != m["original"]:
            mismatches.append({**m, "actual_at_line": actual})

    survivors = [m for m in ok if m["status"] == "survived"]
    killed = [m for m in ok if m["status"] == "killed"]
    no_tests = [m for m in ok if m["status"] not in ("killed", "survived")]
    survivor_lines = sorted({(m["file"], m["line"]) for m in survivors})
    killed_lines = sorted({(m["file"], m["line"]) for m in killed})

    out = {
        "corpus": CORPUS_NAME,
        "pinned_sha": (CORPUS / "PINNED_SHA.txt").read_text().splitlines()[0],
        "tool": _run(["--version"]).strip(),
        "totals": {
            "mutants": len(mutants),
            "parsed": len(ok),
            "parse_errors": len(errors),
            "line_mismatches": len(mismatches),
            "killed": len(killed),
            "survived": len(survivors),
            "survivor_fraction": round(len(survivors) / len(mutants), 4),
            "other_status": {s: sum(1 for m in no_tests if m["status"] == s) for s in sorted({m["status"] for m in no_tests})},
        },
        "survivor_lines": [{"file": f, "line": ln} for f, ln in survivor_lines],
        "killed_lines": [{"file": f, "line": ln} for f, ln in killed_lines],
        "mutants": sorted(ok, key=lambda m: (m["file"], m["line"], m["id"])),
        "parse_errors": errors,
        "line_mismatches": mismatches,
    }

    dest = Path(__file__).resolve().parents[1] / "data" / "ground_truth"
    dest.mkdir(parents=True, exist_ok=True)
    (dest / f"mutants-{CORPUS_NAME}.json").write_text(json.dumps(out, indent=2) + "\n")

    print(json.dumps(out["totals"], indent=2))
    print(f"linhas com sobrevivente: {len(survivor_lines)}")
    print(f"linhas só com mortos:    {len(killed_lines)}")
    print(f"escrito: {dest / f'mutants-{CORPUS_NAME}.json'}")
    return 1 if (errors or mismatches) else 0


if __name__ == "__main__":
    raise SystemExit(main())
