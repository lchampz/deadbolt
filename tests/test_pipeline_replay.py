"""Pipeline de ponta a ponta em replay, com gravação sintética.

Mesma disciplina do S2 aplicada ao pipeline: provar o caminho — prompt, parsing,
gate de evidência, reconciliação, pontuação, exportação de trajetória — ANTES de
existir resposta real de modelo. Se algo aqui só funcionar com a resposta certa,
não é pipeline, é sorte.

Nenhuma chamada de rede. Nenhuma gravação real é tocada: tudo em tmp_path.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "eval"))
sys.path.insert(0, str(ROOT / "src"))

from deadbolt.llm import Call, Client, MissingRecording, cache_key  # noqa: E402
from deadbolt.predict import STAGES, Target, evidence_gate, numbered, reconcile, run  # noqa: E402
from metric import GroundTruth, score  # noqa: E402

PROMPTS = ROOT / "prompts"
CORPUS = ROOT / "corpus"
MODEL, PROVIDER = "modelo-de-teste", "anthropic"


def _prompts_for(stage: str, set_name: str) -> list[tuple[str, str, str]]:
    """Reconstrói exatamente os prompts que predict.run vai montar."""
    from metric import SETS

    cfg = STAGES[stage]
    spec = SETS[set_name]
    system = (PROMPTS / cfg["system"]).read_text()
    tests = (CORPUS / spec["corpus"] / spec["test_file"]).read_text()
    out = []
    for file in spec["files"]:
        target = Target(spec["corpus"], file)
        if cfg["sweep"]:
            tmpl = (PROMPTS / "user_function.md").read_text()
            lines = target.lines()
            for name, start, end in target.functions() or [("<module>", 1, len(lines))]:
                body = "\n".join(lines[start - 1 : end])
                out.append((
                    system,
                    tmpl.format(file=file, function=name, start=start, end=end,
                                source=numbered(body, start=start),
                                test_file=spec["test_file"], tests=tests),
                    f"{file}::{name}",
                ))
        else:
            tmpl = (PROMPTS / "user_whole_file.md").read_text()
            out.append((
                system,
                tmpl.format(file=file, source=numbered(target.source()),
                            test_file=spec["test_file"], tests=tests),
                file,
            ))
    return out


def _plant(tmp_path: Path, stage: str, set_name: str, respond) -> Client:
    """Grava respostas sintéticas nas chaves que o pipeline vai procurar."""
    tmp_path.mkdir(parents=True, exist_ok=True)
    for system, prompt, unit in _prompts_for(stage, set_name):
        key = cache_key(PROVIDER, MODEL, system, prompt)
        call = Call(key=key, provider=PROVIDER, model=MODEL, system=system, prompt=prompt,
                    response=respond(unit), input_tokens=1000, output_tokens=200,
                    cost_usd=0.01, wall_seconds=1.0, timestamp="2026-08-29T00:00:00Z",
                    stage=stage, unit=unit)
        (tmp_path / f"{key}.json").write_text(json.dumps(call.as_dict(), ensure_ascii=False))
    return Client(provider=PROVIDER, model=MODEL, mode="replay", recordings=tmp_path)


def _oracle_json(gt: GroundTruth, file: str, lo: int = 1, hi: int = 10**9) -> str:
    picks = [(f, ln) for f, ln in sorted(gt.survivor_lines) if f == file and lo <= ln <= hi]
    return json.dumps([
        {"file": f, "line_range": [ln, ln], "blind_spot_type": "error_path",
         "evidence_quote": gt.source_line(f, ln).strip(), "confidence": 0.9,
         "rationale": "sintético"}
        for f, ln in picks
    ])


# ------------------------------------------------------------------ replay

def test_replay_sem_gravacao_falha_alto(tmp_path):
    """R2: nunca conserte silenciosamente. Sem gravação, quebra."""
    client = Client(provider=PROVIDER, model=MODEL, mode="replay", recordings=tmp_path)
    with pytest.raises(MissingRecording):
        client.complete("sys", "prompt inédito")


def test_replay_nao_degrada_para_live(tmp_path, monkeypatch):
    def boom(*a, **k):
        raise AssertionError("replay tentou ir na rede")

    monkeypatch.setattr(Client, "_live", boom)
    client = Client(provider=PROVIDER, model=MODEL, mode="replay", recordings=tmp_path)
    with pytest.raises(MissingRecording):
        client.complete("sys", "outro prompt inédito")


def test_chamada_que_falha_nunca_vira_cache(tmp_path, monkeypatch):
    """Regressão real: uma 400 de saldo foi gravada como resposta vazia.

    Gravada no cache, ela é indistinguível de um modelo que respondeu vazio, e a
    execução seguinte em replay serviria o vazio como resultado. A falha tem que
    ficar registrada FORA do caminho que alimenta a métrica.
    """
    def explode(*a, **k):
        raise RuntimeError("400 saldo insuficiente")

    monkeypatch.setattr(Client, "_live", explode)
    client = Client(provider=PROVIDER, model=MODEL, mode="live", recordings=tmp_path)

    with pytest.raises(RuntimeError, match="saldo"):
        client.complete("sys", "prompt")

    assert list(tmp_path.glob("*.json")) == [], "falha entrou no cache de replay"
    falhas = list((tmp_path / "failed").glob("*.json"))
    assert len(falhas) == 1, "falha não foi registrada"
    assert "saldo" in json.loads(falhas[0].read_text())["error"]

    # e o replay seguinte tem que continuar quebrando, não servir vazio
    replay = Client(provider=PROVIDER, model=MODEL, mode="replay", recordings=tmp_path)
    with pytest.raises(MissingRecording):
        replay.complete("sys", "prompt")


def test_gravacao_nunca_guarda_a_chave(tmp_path, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "segredo-que-nao-pode-vazar")
    client = _plant(tmp_path, "baseline", "dev", lambda unit: "[]")
    blob = "".join(p.read_text() for p in tmp_path.glob("*.json"))
    assert "segredo-que-nao-pode-vazar" not in blob


# -------------------------------------------------------------- estágios

@pytest.mark.parametrize("stage", sorted(STAGES))
def test_estagio_roda_ponta_a_ponta_e_pontua(tmp_path, stage):
    gt = GroundTruth.load("dev")
    client = _plant(tmp_path, stage, "dev",
                    lambda unit: _oracle_json(gt, unit.split("::")[0]))
    payload = run(stage, "dev", client)
    s = score(payload["predictions"], gt, stage)
    assert s.recall == 1.0, f"{stage} perdeu linhas do oráculo no caminho"
    assert s.precision == 1.0, f"{stage} inventou linha fora do oráculo"
    assert payload["meta"]["stage"] == stage
    assert payload["meta"]["cost_usd"] > 0


def test_saida_nao_parseavel_quebra_em_vez_de_silenciar(tmp_path):
    client = _plant(tmp_path, "baseline", "dev", lambda unit: "desculpe, não consegui")
    with pytest.raises(ValueError, match="nenhum array JSON"):
        run("baseline", "dev", client)


def test_resposta_em_fence_markdown_e_aceita(tmp_path):
    gt = GroundTruth.load("dev")
    client = _plant(tmp_path, "baseline", "dev",
                    lambda unit: f"Claro!\n```json\n{_oracle_json(gt, unit)}\n```\n")
    assert run("baseline", "dev", client)["predictions"]


# ------------------------------------------------------------------ gate

def test_gate_descarta_ancora_inventada(tmp_path):
    gt = GroundTruth.load("dev")
    file = gt.files[0]
    line = sorted(ln for f, ln in gt.survivor_lines if f == file)[0]

    def respond(unit):
        if unit.split("::")[0] != file:
            return "[]"
        return json.dumps([
            {"file": file, "line_range": [line, line], "blind_spot_type": "error_path",
             "evidence_quote": gt.source_line(file, line).strip(), "confidence": 0.9},
            {"file": file, "line_range": [line, line], "blind_spot_type": "error_path",
             "evidence_quote": "texto que não existe neste arquivo", "confidence": 0.9},
        ])

    sem_gate = run("s4", "dev", _plant(tmp_path / "a", "s4", "dev", respond))
    com_gate = run("s5", "dev", _plant(tmp_path / "b", "s5", "dev", respond))

    assert len(sem_gate["predictions"]) == 2
    assert len(com_gate["predictions"]) == 1
    assert com_gate["meta"]["n_dropped_by_gate"] == 1


def test_gate_e_funcao_pura(tmp_path):
    gt = GroundTruth.load("dev")
    file = gt.files[0]
    line = sorted(ln for f, ln in gt.survivor_lines if f == file)[0]
    kept, dropped = evidence_gate(
        [{"file": file, "line_range": [line, line], "evidence_quote": "não existe"}],
        Target("python-slugify", file),
    )
    assert kept == [] and len(dropped) == 1
    assert "citação" in dropped[0]["_drop_reason"]


# ---------------------------------------------------------- reconciliação

def test_reconcile_funde_sobreposto_e_preserva_disjunto():
    out = reconcile([
        {"file": "f", "blind_spot_type": "error_path", "line_range": [10, 12], "confidence": 0.5},
        {"file": "f", "blind_spot_type": "error_path", "line_range": [11, 15], "confidence": 0.9},
        {"file": "f", "blind_spot_type": "error_path", "line_range": [40, 41], "confidence": 0.2},
    ])
    assert [p["line_range"] for p in out] == [[10, 15], [40, 41]]
    assert out[0]["confidence"] == 0.9


def test_reconcile_nao_funde_tipos_diferentes():
    out = reconcile([
        {"file": "f", "blind_spot_type": "error_path", "line_range": [10, 12], "confidence": 0.5},
        {"file": "f", "blind_spot_type": "output_shape", "line_range": [11, 13], "confidence": 0.5},
    ])
    assert len(out) == 2


def test_varredura_cobre_toda_funcao_do_arquivo():
    t = Target("python-slugify", "slugify/slugify.py")
    nomes = [n for n, _, _ in t.functions()]
    assert nomes == ["smart_truncate", "slugify"]
    for _, start, end in t.functions():
        assert start < end <= len(t.lines())
