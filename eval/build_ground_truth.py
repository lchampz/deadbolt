"""Converte a saída do mutmut em ground truth estruturado.

Contrato: roda DEPOIS de `mutmut run` dentro de corpus/python-slugify.
Não inspeciona o conteúdo dos sobreviventes para tomar decisão — só transcreve.

Mapeamento de linha (verificado empiricamente em S1):
    mutmut show emite um diff unificado da FUNÇÃO extraída, não do arquivo.
    A linha original = linha do `def` + linha relativa no hunk - 1.
"""

from __future__ import annotations

import ast
import json
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORPUS_NAME = sys.argv[1] if len(sys.argv) > 1 else "python-slugify"
CORPUS = ROOT / "corpus" / CORPUS_NAME
# `python -m mutmut`, nunca o script de console: o shebang dele guarda o caminho
# absoluto de quando o venv foi criado, e renomear a pasta do projeto o quebra.
_venv_py = CORPUS / ".venv" / "bin" / "python"
MUTMUT = [str(_venv_py) if _venv_py.exists() else sys.executable, "-m", "mutmut"]
SPINNER = re.compile(r"[⠀-⣿]")

# mutmut usa DOIS esquemas de nome. O segundo custou 301 mutantes descartados
# em silêncio antes de eu notar (ver docs/06 - Hot Takes e Falhas):
#   função de módulo:  <modulo>.x_<funcao>__mutmut_<n>
#   método de classe:  <modulo>.xǁ<Classe>ǁ<metodo>__mutmut_<n>   (U+01C1 separando)
# Dois esquemas de nome, e reconstruir o id a partir deles é frágil — o id é
# extraído literal da linha e só o NOME DA FUNÇÃO sai da regex, para achar a
# linha do `def` no arquivo original.
#   função de módulo:  <modulo>.x_<funcao>__mutmut_<n>: <status>
#   método de classe:  <modulo>.xǁ<Classe>ǁ<metodo>__mutmut_<n>: <status>
MUTANT_RE = re.compile(
    r"^([\w.]+?)\."
    r"(?:x_(?P<func>\w+)|x\u01c1(?P<cls>\w+)\u01c1(?P<meth>\w+))"
    r"__mutmut_\d+$"
)
ANY_MUTANT_RE = re.compile(r"__mutmut_\d+:")
HUNK_RE = re.compile(r"^@@ -(\d+),\d+ \+\d+,\d+ @@")


def _clean(raw: str) -> str:
    return SPINNER.sub("", raw.replace("\r", "\n"))


def _run(args: list[str]) -> str:
    out = subprocess.run([*MUTMUT, *args], cwd=CORPUS, capture_output=True, text=True)
    return _clean(out.stdout + out.stderr)


def def_lines(path: Path) -> dict[str, tuple[int, int]]:
    """Linha 1-based de cada def, indexada por `nome` e por `Classe.metodo`.

    Usa `ast`, não regex: `__call__` existe em várias classes do mesmo arquivo e
    a primeira ocorrência não é a certa para as demais.
    """
    tree = ast.parse(path.read_text())
    found: dict[str, tuple[int, int]] = {}

    def visit(node, prefix: str = "") -> None:
        for child in getattr(node, "body", []):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                found.setdefault(
                    f"{prefix}{child.name}", (child.lineno, child.end_lineno or child.lineno)
                )
            elif isinstance(child, ast.ClassDef):
                found.setdefault(child.name, (child.lineno, child.end_lineno or child.lineno))
                visit(child, prefix=f"{child.name}.")

    visit(tree)
    return found


def list_mutants() -> tuple[list[dict], int]:
    """Devolve (mutantes reconhecidos, linhas de mutante vistas na saída).

    Os dois números vêm juntos de propósito: a diferença entre eles é a única
    coisa que denuncia um esquema de nome que a regex não conhece, e sozinha ela
    não faz barulho nenhum. Custou 301 mutantes descartados em silêncio.
    """
    raw = _run(["results", "--all", "True"])
    seen = 0
    mutants = []
    for line in raw.splitlines():
        if not ANY_MUTANT_RE.search(line):
            continue
        seen += 1
        mutant_id, _, status = line.strip().rpartition(":")
        m = MUTANT_RE.match(mutant_id.strip())
        if not m:
            continue
        name = m.group("func") or f"{m.group('cls')}.{m.group('meth')}"
        mutants.append(
            {
                "id": mutant_id.strip(),
                "module": m.group(1),
                "function": name,
                "status": status.strip(),
            }
        )
    return mutants, seen


def parse_show(mutant: dict, defs: dict[str, dict[str, tuple[int, int]]]) -> dict:
    """Mapeia um mutante para a linha real no arquivo original.

    NÃO usa aritmética de offset. A primeira versão fazia
    `linha = linha_do_def + posição_no_hunk - 1` e funcionou nos dois primeiros
    corpora por acidente: o `mutmut` extrai a função **junto com comentários e
    decoradores colados acima dela**, então o `def` não está sempre na posição 1
    do bloco extraído. Em `toolz` isso errou 5 mutantes de `Compose.__get__` —
    quatro linhas de comentário acima do `def` deslocaram tudo.

    Em vez disso, reconstrói o lado "antes" do hunk (contexto + linhas removidas)
    e procura essa sequência literal dentro da faixa da função no arquivo. Se
    encontrar em exatamente um lugar, aquela é a posição. Se encontrar em zero ou
    em mais de um, é erro declarado — nunca um palpite.
    """
    text = _run(["show", mutant["id"]])
    file_path = None
    before: list[str] = []      # contexto + removidas, na ordem do arquivo
    removed_at = None           # índice da primeira removida dentro de `before`
    added: list[str] = []
    in_hunk = False

    for line in text.splitlines():
        if line.startswith("--- "):
            file_path = line[4:].strip()
            continue
        if line.startswith("+++"):
            continue
        if HUNK_RE.match(line):
            in_hunk = True
            continue
        if not in_hunk:
            continue
        if line.startswith("-"):
            if removed_at is None:
                removed_at = len(before)
            before.append(line[1:])
        elif line.startswith("+"):
            added.append(line[1:])
        else:
            before.append(line[1:] if line.startswith(" ") else line)

    if file_path is None or removed_at is None:
        mutant["error"] = "diff sem arquivo ou sem linha removida"
        return mutant

    span = defs.get(file_path, {}).get(mutant["function"])
    if span is None:
        mutant["error"] = f"função {mutant['function']} não encontrada em {file_path}"
        return mutant

    src = (CORPUS / file_path).read_text().splitlines()
    lo, hi = span
    # folga para comentários/decoradores que o mutmut inclui acima do `def`
    lo = max(1, lo - 20)
    hi = min(len(src), hi + 2)

    # comparação sem indentação: o mutmut DESINDENTA o corpo do método ao
    # extraí-lo, então `def __get__` sai na coluna 0 mesmo estando dentro de uma
    # classe. Comparar texto cru não casa nada; comparar conteúdo casa.
    want = [ln.strip() for ln in before]
    hits = [
        i
        for i in range(lo - 1, hi - len(want) + 1)
        if [ln.strip() for ln in src[i : i + len(want)]] == want
    ]
    if len(hits) != 1:
        mutant["error"] = (
            f"bloco do diff encontrado {len(hits)}x na faixa {lo}-{hi} de "
            f"{mutant['function']} — ambíguo, não vou adivinhar"
        )
        return mutant

    mutant["file"] = file_path
    mutant["line"] = hits[0] + removed_at + 1
    mutant["original"] = before[removed_at].strip()
    mutant["mutated"] = added[0].strip() if added else ""
    return mutant


def main() -> int:
    mutants, seen = list_mutants()
    if not mutants:
        print("ERRO: mutmut results não retornou mutantes", file=sys.stderr)
        return 1
    if len(mutants) != seen:
        print(
            f"ERRO: mutmut listou {seen} mutantes, o parser reconheceu {len(mutants)} "
            f"— {seen - len(mutants)} descartados por esquema de nome desconhecido.\n"
            f"Ground truth incompleto mede um subconjunto enviesado. Corrija "
            f"MUTANT_RE antes de usar qualquer número deste corpus.",
            file=sys.stderr,
        )
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
            "listed_by_mutmut": seen,
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
