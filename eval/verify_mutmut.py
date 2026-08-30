"""Verificação independente: roda o `mutmut` de verdade sobre a suíte + testes gerados.

METRIC_TESTGEN.md § 4 diz que o número da manchete vem de `mutmut run` do zero,
não da medição incremental do pipeline. A medição incremental é rápida e exata
sob a monotonicidade, mas ela é MINHA — e já reportou 1.0000 duas vezes por bug.
Esta aqui é a ferramenta externa dando o veredito.

    python eval/verify_mutmut.py dev
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "eval"))
sys.path.insert(0, str(ROOT / "src"))

from deadbolt.testgen import Corpus, Sandbox  # noqa: E402

COUNT = re.compile(r"(\d+)/(\d+)\s+🎉\s*(\d+).*?🙁\s*(\d+)", re.S)


def main() -> int:
    set_name = sys.argv[1] if len(sys.argv) > 1 else "dev"
    stage = sys.argv[2] if len(sys.argv) > 2 else "T3"
    suf = sys.argv[3] if len(sys.argv) > 3 else ""

    corpus = Corpus(set_name)
    res = json.loads((ROOT / "results" / f"testgen-{stage}-{set_name}{suf}.json").read_text())
    tests = [g["test"] for g in res["accepted"]]

    sb = Sandbox(corpus, f"verify-{stage}{suf}")
    sb.write_tests("test_deadbolt.py", tests)

    # O mutmut roda pytest com a seleção de testes da própria config dele. Trocar
    # `testpaths` no pyproject só funcionava para o layout do slugify; no toolz não
    # casava nada, o arquivo gerado nunca era coletado, e a verificação reportou
    # +0.0000 de melhoria — tão implausível quanto o 1.0000 de antes.
    cfg = sb.path / "setup.cfg"
    txt = cfg.read_text() if cfg.exists() else "[mutmut]\n"
    if "pytest_add_cli_args_test_selection" not in txt:
        txt = txt.rstrip() + (
            f"\npytest_add_cli_args_test_selection=\n"
            f"    {corpus.spec['test_file']}\n"
            f"    test_deadbolt.py\n"
        )
    cfg.write_text(txt)
    print(f"[mutmut] seleção de teste: {corpus.spec['test_file']} + test_deadbolt.py")

    green = sb.pytest(corpus.spec["test_file"], "test_deadbolt.py")
    print(f"suíte + testes gerados: {'VERDE' if green.returncode == 0 else 'VERMELHA'}")
    if green.returncode != 0:
        print(green.stdout[-1500:])
        return 1

    # `python -m mutmut` em vez do script de console: o script tem shebang com
    # caminho absoluto gravado na criação do venv, e renomear a pasta do projeto
    # o quebra com um FileNotFoundError que nomeia o SCRIPT, não o interpretador
    # que sumiu. Chamar pelo módulo não tem esse modo de falha.
    mut = [corpus.python, "-m", "mutmut"]
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
    print(f"\nrodando mutmut do zero em {sb.path.name} …")
    p = subprocess.run([*mut, "run"], cwd=sb.path, capture_output=True, text=True,
                       env=env, timeout=3600)
    saida = re.sub(r"[⠀-⣿]", "", (p.stdout + p.stderr).replace("\r", "\n"))
    ultimas = [l for l in saida.splitlines() if "🎉" in l]
    linha = ultimas[-1].strip() if ultimas else saida[-400:]
    print(f"  {linha}")

    # quem sobreviveu segundo o mutmut, para cruzar com o proxy incremental
    r = subprocess.run([*mut, "results", "--all", "True"], cwd=sb.path,
                       capture_output=True, text=True, env=env, timeout=600)
    limpo = re.sub(r"[⠀-⣿]", "", (r.stdout + r.stderr).replace("\r", "\n"))
    vivos = {ln.strip().rpartition(":")[0].strip()
             for ln in limpo.splitlines()
             if "__mutmut_" in ln and ln.strip().rpartition(":")[2].strip() != "killed"}
    proxy_mortos = set(res["killed_ids"])
    discordam = sorted(vivos & proxy_mortos)
    if discordam:
        print(f"\nDIVERGEM — o proxy disse morto, o mutmut diz vivo ({len(discordam)}):")
        gt = {m["id"]: m for m in corpus.survivors()}
        for i in discordam:
            g = gt.get(i)
            if g:
                print(f"  {g['file']}:{g['line']:<4} {g['original'][:44]!r}")
                print(f"       → {g['mutated'][:60]!r}")
            else:
                print(f"  {i}")
    (ROOT / "results" / f"verify-{stage}-{set_name}{suf}.json").write_text(json.dumps({
        "set": set_name, "stage": stage, "tool": "mutmut 3.7.0 run from scratch",
        "survivors_after": sorted(vivos), "proxy_disagreements": discordam,
    }, indent=2) + "\n")

    m = COUNT.search(linha)
    total, killed, survived = (int(m.group(2)), int(m.group(3)), int(m.group(4))) if m else (0, 0, 0)
    antes_total, antes_killed = corpus.totals()

    print(f"\n{'':<26}{'mutantes':>10}{'mortos':>9}{'score':>9}")
    print("-" * 54)
    print(f"{'antes (suíte original)':<26}{antes_total:>10}{antes_killed:>9}"
          f"{antes_killed / antes_total:>9.4f}")
    if not total:
        print("mutmut não devolveu contagem — saída bruta acima")
        sb.cleanup()
        return 1

    score = killed / total
    print(f"{'depois (+ gerados)':<26}{total:>10}{killed:>9}{score:>9.4f}")
    print(f"\ndelta: {score - antes_killed / antes_total:+.4f}")

    # Reprodutibilidade: esta execução bate com o número publicado?
    anterior = ROOT / "results" / f"verify-{stage}-{set_name}{suf}.json"
    publicado = None
    if anterior.exists():
        d = json.loads(anterior.read_text())
        publicado = (total - len(d["survivors_after"])) / total

    if publicado is None:
        print("primeira verificação deste conjunto — nada com que comparar ainda")
    elif abs(score - publicado) < 1e-9:
        print(f"REPRODUZ o número publicado ({publicado:.4f}) — OK")
    else:
        print(f"NÃO REPRODUZ: publicado {publicado:.4f}, agora {score:.4f}")
        sb.cleanup()
        return 1

    # O proxy interno aparece só como nota de rodapé: ele está desqualificado
    # desde METRIC_TESTGEN.md § 14 e não entra em nenhum número reportado.
    proxy = res["meta"]["score_after"]
    if abs(score - proxy) >= 0.001:
        print(f"nota: o proxy interno dizia {proxy:.4f} — desqualificado, "
              f"ver METRIC_TESTGEN.md § 14")

    sb.cleanup()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
