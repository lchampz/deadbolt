"""Geração de testes verificada — camada 1 e instrumento da camada 2.

Ver METRIC_TESTGEN.md para métrica, guardas e teto, todos congelados antes
desta implementação existir.

Quatro estágios cumulativos:

    B   baseline ingênuo: "escreva mais testes", sem mutantes, sem verificação
    T1  + alvo: recebe o diff de cada sobrevivente
    T2  + guardas: G1 passa no original, G2 falha no mutante, G3 suíte verde
    T3  + reparo: devolve a falha da guarda ao modelo, até 3 rodadas

Nada de julgamento em nenhuma guarda. Teste que viola qualquer uma é descartado
ou devolvido ao loop — nunca corrigido à mão.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "eval"))
sys.path.insert(0, str(ROOT / "src"))

from deadzone.llm import Client  # noqa: E402
from metric import SETS  # noqa: E402

CORPUS = ROOT / "corpus"
GROUND_TRUTH = ROOT / "data" / "ground_truth"
RESULTS = ROOT / "results"
SANDBOXES = ROOT / ".sandboxes"

BATCH = 8
MAX_REPAIR = 3
STAGES = ("B", "T1", "T2", "T3")

SYSTEM_TARGETED = """You write pytest tests that detect specific mutations.

You are given a Python module, its existing test suite, and a list of mutations
that the current suite FAILS to detect. For each mutation, write one test that:

- PASSES on the original code shown below
- FAILS on the mutated code
- uses only the module's public API and pytest — never mock the module itself
- follows the naming and style of the existing suite
- is deterministic: no clock, no network, no randomness, no filesystem

Return ONLY a JSON array, no prose and no markdown fence:

[{"mutant_id": "<exact id given>", "test": "def test_...():\\n    ..."}]

Each `test` is a complete top-level function. Assume these imports already exist
at the top of the file:

{imports}

If you genuinely cannot distinguish a mutation from the original — because the
mutated line is unreachable, or the change is semantically identical for every
input — return that entry with `"test": null` and a `"why"` field explaining
which condition makes it undetectable. A null with a reason is worth more than a
test that does not detect anything.

## The module under test: {file}

```python
{source}
```

## Its existing test suite — it does NOT catch the mutations below

```python
{tests}
```"""

SYSTEM_NAIVE = """You strengthen Python test suites.

You are given a module and its existing test suite. Write additional pytest tests
covering behaviour the current suite does not check.

Return ONLY a JSON array, no prose and no markdown fence:

[{{"mutant_id": "extra_<n>", "test": "def test_...():\\n    ..."}}]

Each `test` is a complete top-level function. Assume these imports already exist:

{imports}

## The module under test: {file}

```python
{source}
```

## Its existing test suite

```python
{tests}
```"""

USER_TARGETED = """Mutations the suite does not catch. Write one test for each.

{mutants}"""

USER_NAIVE = """Write {n} additional tests for `{file}`."""

REPAIR = """These tests did not hold up. Fix each one.

{failures}

Return the same JSON array shape, only for the entries listed above."""

IMPORTS = {
    "python-slugify": "import pytest\nfrom slugify import slugify, smart_truncate\nfrom slugify.special import add_uppercase_char",
    "python-slugify-holdout": "import pytest\nimport sys\nfrom slugify.__main__ import parse_args, slugify_params, main",
    "toolz-transfer": "import pytest\nimport toolz\nfrom toolz.functoolz import *  # noqa: F403",
}


# --------------------------------------------------------------------- corpus

@dataclass
class Corpus:
    set_name: str

    def __post_init__(self) -> None:
        self.spec = SETS[self.set_name]
        self.name = self.spec["corpus"]
        self.root = CORPUS / self.name
        # SEM .resolve(): o bin/python do venv é symlink para o Python do sistema, e
        # resolvê-lo sai do venv — o processo perde pytest e todo import falha.
        # Custou um harness que reportava score 1.0000 porque TODA execução dava
        # returncode != 0 por ModuleNotFoundError, e isso conta como "mutante morto".
        self.python = str(self.root.absolute() / ".venv/bin/python")

    def survivors(self) -> list[dict]:
        raw = json.loads((GROUND_TRUTH / f"mutants-{self.name}.json").read_text())
        files = set(self.spec["files"])
        return sorted(
            (m for m in raw["mutants"] if m["file"] in files and m["status"] != "killed"),
            key=lambda m: (m["file"], m["line"], m["id"]),
        )

    def totals(self) -> tuple[int, int]:
        raw = json.loads((GROUND_TRUTH / f"mutants-{self.name}.json").read_text())
        files = set(self.spec["files"])
        ms = [m for m in raw["mutants"] if m["file"] in files]
        return len(ms), sum(1 for m in ms if m["status"] == "killed")


# ------------------------------------------------------------------ sandbox

class Sandbox:
    """Cópia descartável do corpus. O corpus pinado nunca é tocado."""

    def __init__(self, corpus: Corpus, tag: str) -> None:
        self.corpus = corpus
        self.path = SANDBOXES / f"{corpus.name}-{tag}"
        shutil.rmtree(self.path, ignore_errors=True)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(
            corpus.root, self.path,
            ignore=shutil.ignore_patterns(".venv", "mutants", "__pycache__", "*.egg-info"),
        )

    def write_tests(self, name: str, tests: list[str]) -> Path:
        header = IMPORTS[self.corpus.name] + "\n\n\n"
        body = "\n\n\n".join(t.strip() for t in tests)
        dest = self.path / name
        dest.write_text(header + body + "\n")
        return dest

    def pytest(self, target: str | None = None, timeout: int = 30) -> subprocess.CompletedProcess:
        """Timeout curto de propósito.

        Mutar um limite de laço produz mutante que NÃO TERMINA — `smart_truncate`
        tem um while cujo mutante roda para sempre. A suíte original leva 0.04s,
        então 30s é 750x de folga: se estourou, o mutante mudou o comportamento
        de forma observável. Timeout é tratado como detecção, contado à parte, e
        o número final vem do `mutmut` de verdade, que tem a própria lógica.
        """
        cmd = [self.corpus.python, "-m", "pytest", "-q", "-p", "no:cacheprovider"]
        if target:
            cmd.append(target)
        try:
            return subprocess.run(cmd, cwd=self.path, capture_output=True,
                                  text=True, timeout=timeout)
        except subprocess.TimeoutExpired:
            return subprocess.CompletedProcess(cmd, returncode=124, stdout="",
                                               stderr=f"TIMEOUT após {timeout}s")

    def mutate(self, mutant: dict):
        """Aplica uma mutação. Devolve um restaurador."""
        src = self.path / mutant["file"]
        lines = src.read_text().splitlines()
        i = mutant["line"] - 1
        before = lines[i]
        indent = re.match(r"\s*", before).group(0)
        lines[i] = indent + mutant["mutated"]
        src.write_text("\n".join(lines) + "\n")

        def restore() -> None:
            cur = src.read_text().splitlines()
            cur[i] = before
            src.write_text("\n".join(cur) + "\n")

        return restore

    def cleanup(self) -> None:
        shutil.rmtree(self.path, ignore_errors=True)


# ------------------------------------------------------------------- guardas

@dataclass
class Verdict:
    mutant_id: str
    g1_passes_original: bool = False
    g2_fails_on_mutant: bool = False
    reason: str = ""
    output: str = ""

    @property
    def kills(self) -> bool:
        return self.g1_passes_original and self.g2_fails_on_mutant


def check(sandbox: Sandbox, mutant: dict, test_src: str) -> Verdict:
    """G1 e G2, isoladas. G3 roda uma vez no fim, com o conjunto aceito."""
    v = Verdict(mutant_id=mutant["id"])
    sandbox.write_tests("test_probe.py", [test_src])

    g1 = sandbox.pytest("test_probe.py")
    v.g1_passes_original = g1.returncode == 0
    if not v.g1_passes_original:
        v.reason = "G1: o teste falha no código ORIGINAL — a expectativa está errada"
        v.output = _tail(g1)
        return v

    restore = sandbox.mutate(mutant)
    try:
        g2 = sandbox.pytest("test_probe.py")
    finally:
        restore()
    v.g2_fails_on_mutant = g2.returncode != 0
    if not v.g2_fails_on_mutant:
        v.reason = "G2: o teste PASSA no código mutado — não detecta a mutação"
        v.output = _tail(g2)
    return v


def _tail(proc: subprocess.CompletedProcess, n: int = 1800) -> str:
    out = (proc.stdout or "") + (proc.stderr or "")
    return re.sub(r"\x1b\[[0-9;]*m", "", out)[-n:]


# -------------------------------------------------------------------- prompt

def describe(mutants: list[dict]) -> str:
    out = []
    for m in mutants:
        out.append(
            f"### `{m['id']}` — {m['file']} line {m['line']}\n"
            f"```diff\n- {m['original']}\n+ {m['mutated']}\n```"
        )
    return "\n\n".join(out)


FENCE = re.compile(r"```(?:json)?\s*(.*?)```", re.S)


def parse(raw: str) -> list[dict]:
    text = raw.strip()
    m = FENCE.search(text)
    if m:
        text = m.group(1).strip()
    a, b = text.find("["), text.rfind("]")
    if a == -1 or b == -1:
        raise ValueError(f"nenhum array JSON na resposta: {raw[:200]!r}")
    return json.loads(text[a : b + 1])


def numbered(text: str) -> str:
    return "\n".join(f"{i:>4} | {ln}" for i, ln in enumerate(text.splitlines(), 1))


# ------------------------------------------------------------------- medição

def measure(sandbox: Sandbox, survivors: list[dict], test_name: str) -> dict[str, object]:
    """Quais sobreviventes o arquivo de testes mata.

    Só sobreviventes são testados: mutante já morto continua morto quando se
    ADICIONA teste (METRIC_TESTGEN.md § 2). Isso torna a medição incremental
    exata, não uma aproximação.
    """
    killed = {}
    for m in survivors:
        restore = sandbox.mutate(m)
        try:
            rc = sandbox.pytest(test_name).returncode
        finally:
            restore()
        killed[m["id"]] = "timeout" if rc == 124 else (rc != 0)
    return killed


# ----------------------------------------------------------------- estágios

@dataclass
class Run:
    set_name: str
    stage: str
    generated: list[dict] = field(default_factory=list)
    accepted: list[dict] = field(default_factory=list)
    rejected: list[dict] = field(default_factory=list)
    undetermined: list[dict] = field(default_factory=list)
    repair_rounds: int = 0
    repaired: int = 0
    suite_green: bool = False
    killed_ids: list[str] = field(default_factory=list)
    timeout_ids: list[str] = field(default_factory=list)
    meta: dict = field(default_factory=dict)


def generate(corpus: Corpus, stage: str, client: Client, sandbox: Sandbox) -> Run:
    run_ = Run(set_name=corpus.set_name, stage=stage)
    survivors = corpus.survivors()
    file = corpus.spec["files"][0]
    source = (corpus.root / file).read_text()
    tests = (corpus.root / corpus.spec["test_file"]).read_text()
    imports = IMPORTS[corpus.name]
    batches = [survivors[i : i + BATCH] for i in range(0, len(survivors), BATCH)]

    if stage == "B":
        # Justiça: mesmo número de chamadas e mesmo orçamento de saída do T1.
        # O baseline não sabe quais mutantes existem — é essa a variável isolada.
        system = SYSTEM_NAIVE.format(imports=imports, file=file, source=numbered(source), tests=tests)
        for i in range(len(batches)):
            call = client.complete(system, USER_NAIVE.format(n=BATCH, file=file),
                                   stage=f"testgen-{stage}", unit=f"{corpus.set_name}#{i}",
                                   cache_system=True)
            run_.generated.extend(parse(call.response))
    else:
        system = SYSTEM_TARGETED.format(imports=imports, file=file,
                                        source=numbered(source), tests=tests)
        for i, batch in enumerate(batches):
            call = client.complete(system, USER_TARGETED.format(mutants=describe(batch)),
                                   stage=f"testgen-{stage}", unit=f"{corpus.set_name}#{i}",
                                   cache_system=True)
            run_.generated.extend(parse(call.response))

    by_id = {m["id"]: m for m in survivors}
    candidates = [g for g in run_.generated if g.get("test")]
    run_.undetermined = [
        {"mutant_id": g.get("mutant_id"), "why": g.get("why", "")}
        for g in run_.generated if not g.get("test")
    ]

    if stage in ("B", "T1"):
        # sem guardas: aceita tudo que veio. É essa a ausência que T2 mede.
        run_.accepted = candidates
    else:
        pending = candidates
        for round_ in range(MAX_REPAIR + 1):
            failures = []
            for g in pending:
                mut = by_id.get(g.get("mutant_id"))
                if mut is None:
                    run_.rejected.append({**g, "reason": "id de mutante desconhecido"})
                    continue
                v = check(sandbox, mut, g["test"])
                if v.kills:
                    run_.accepted.append(g)
                else:
                    failures.append({**g, "reason": v.reason, "output": v.output})

            if not failures or stage != "T3" or round_ == MAX_REPAIR:
                run_.rejected.extend(failures)
                break

            run_.repair_rounds = round_ + 1
            blob = "\n\n".join(
                f"### `{f['mutant_id']}`\n{f['reason']}\n\nYour test:\n```python\n{f['test']}\n```"
                f"\n\nWhat happened:\n```\n{f['output'][-900:]}\n```"
                for f in failures
            )
            call = client.complete(system, REPAIR.format(failures=blob),
                                   stage=f"testgen-{stage}", unit=f"{corpus.set_name}#repair{round_}",
                                   cache_system=True)
            before = len(run_.accepted)
            pending = [g for g in parse(call.response) if g.get("test")]
            run_.repaired += 0  # contabilizado ao fim da rodada seguinte
            del before

    # G3 uma única vez, com o conjunto aceito inteiro
    final = "test_deadbolt.py"
    if run_.accepted:
        sandbox.write_tests(final, [g["test"] for g in run_.accepted])
        run_.suite_green = sandbox.pytest().returncode == 0
    else:
        sandbox.write_tests(final, ["def test_placeholder():\n    assert True"])
        run_.suite_green = sandbox.pytest().returncode == 0

    killed = measure(sandbox, survivors, final)
    run_.killed_ids = sorted(k for k, v in killed.items() if v)
    run_.timeout_ids = sorted(k for k, v in killed.items() if v == "timeout")

    total, already = corpus.totals()
    run_.meta = {
        **client.totals(),
        "set": corpus.set_name,
        "stage": stage,
        "mutants_total": total,
        "killed_before": already,
        "score_before": round(already / total, 4),
        "newly_killed": len(run_.killed_ids),
        "of_which_timeout": len(run_.timeout_ids),
        "killed_after": already + len(run_.killed_ids),
        "score_after": round((already + len(run_.killed_ids)) / total, 4),
        "n_generated": len(run_.generated),
        "n_accepted": len(run_.accepted),
        "n_rejected": len(run_.rejected),
        "n_model_declined": len(run_.undetermined),
        "suite_green": run_.suite_green,
        "repair_rounds": run_.repair_rounds,
        "survivors_attacked": len(survivors),
    }
    return run_


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=STAGES)
    ap.add_argument("--set", default="dev", choices=sorted(SETS))
    ap.add_argument("--keep-sandbox", action="store_true")
    args = ap.parse_args()

    corpus = Corpus(args.set)
    sandbox = Sandbox(corpus, f"{args.stage}-{int(time.time())}")
    client = Client()
    try:
        run_ = generate(corpus, args.stage, client, sandbox)
    finally:
        if not args.keep_sandbox:
            sandbox.cleanup()

    RESULTS.mkdir(exist_ok=True)
    dest = RESULTS / f"testgen-{args.stage}-{args.set}.json"
    dest.write_text(json.dumps({
        "meta": run_.meta,
        "killed_ids": run_.killed_ids,
        "timeout_ids": run_.timeout_ids,
        "accepted": run_.accepted,
        "rejected": run_.rejected,
        "model_declined": run_.undetermined,
        "generated": run_.generated,
    }, indent=2, ensure_ascii=False) + "\n")

    m = run_.meta
    print(json.dumps(m, indent=2))
    print(f"\nscore {m['score_before']:.4f} → {m['score_after']:.4f} "
          f"(+{m['newly_killed']} de {m['survivors_attacked']} sobreviventes) "
          f"· suíte verde: {m['suite_green']}")
    print(f"gravado: {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
