"""Testes da métrica congelada.

Se estes testes quebrarem, todo número em results/ perde validade. Eles existem
porque a métrica é a única peça do projeto que ninguém audita de fora.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "eval"))
sys.path.insert(0, str(ROOT / "src"))

from metric import SETS, TAXONOMY, GroundTruth, expand, score  # noqa: E402


@pytest.fixture(scope="module")
def dev() -> GroundTruth:
    return GroundTruth.load("dev")


# ------------------------------------------------------- ground truth intacto

@pytest.mark.parametrize(
    "set_name,mutants,killed,survived,blind_lines",
    [
        # DEV: inalterado desde o S1.
        ("dev", 216, 170, 46, 17),
        # HOLDOUT: corrigido em 2026-08-29 por abort declarado em docs/metric-prediction.md § 8.
        # Antes: 288/189/99/30 — 10 mutantes `no tests` eram descartados pelo
        # parser e as 6 linhas deles contavam como COBERTAS.
        ("holdout", 298, 189, 109, 36),
    ],
)
def test_ground_truth_congelado(set_name, mutants, killed, survived, blind_lines):
    """R5: o corpus só muda com abort declarado. Estes são os números vigentes."""
    gt = GroundTruth.load(set_name)
    assert gt.n_mutants == mutants
    assert gt.n_survivors == survived
    assert len(gt.survivor_lines) == blind_lines
    raw = json.loads(
        (ROOT / "data" / "ground_truth" / f"mutants-{gt.corpus}.json").read_text()
    )
    assert raw["totals"]["killed"] == killed
    assert raw["totals"]["parse_errors"] == 0
    assert raw["totals"]["line_mismatches"] == 0, "mapeamento de linha quebrado"


def test_parser_reconheceu_tudo_que_o_mutmut_listou():
    """A defesa que faltava: silêncio no parser é indistinguível de corpus limpo.

    Um esquema de nome desconhecido descartava mutantes sem erro — 10 no HOLDOUT,
    301 num terceiro corpus — com parse_errors 0 e line_mismatches 0. O total
    listado pelo mutmut e o total reconhecido têm que bater.
    """
    for corpus in ("python-slugify", "python-slugify-holdout"):
        raw = json.loads(
            (ROOT / "data" / "ground_truth" / f"mutants-{corpus}.json").read_text()
        )
        t = raw["totals"]
        assert t["mutants"] == t["listed_by_mutmut"], (
            f"{corpus}: {t['listed_by_mutmut']} listados, {t['mutants']} reconhecidos"
        )
        assert t["parsed"] == t["mutants"]


def test_mutante_sem_teste_conta_como_cego():
    """`no tests` = nenhum teste executa a linha. É o ponto cego mais puro.

    Contá-lo como linha coberta penalizava o preditor por acertar. São as 6
    linhas do main() de __main__.py — ver docs/metric-prediction.md § 8.
    """
    gt = GroundTruth.load("holdout")
    raw = json.loads(
        (ROOT / "data" / "ground_truth" / "mutants-python-slugify-holdout.json").read_text()
    )
    sem_teste = {(m["file"], m["line"]) for m in raw["mutants"] if m["status"] == "no tests"}
    assert sem_teste, "o corpus perdeu os mutantes sem teste"
    assert sem_teste <= gt.survivor_lines, "linha sem teste nenhum não está marcada como cega"
    assert not (sem_teste & gt.killed_lines), "linha sem teste contada como coberta"


def test_linha_cega_e_linha_morta_sao_disjuntas(dev):
    """Uma linha com 1 sobrevivente é cega, mesmo tendo mortos junto."""
    assert not (dev.survivor_lines & dev.killed_lines)


def test_toda_linha_do_ground_truth_existe_no_arquivo(dev):
    for file, line in dev.survivor_lines | dev.killed_lines:
        assert 1 <= line <= dev.file_lengths[file]
        assert dev.source_line(file, line).strip(), f"{file}:{line} está em branco"


# --------------------------------------------------------------- expand()

def test_expand_recorta_no_tamanho_do_arquivo(dev):
    file = dev.files[0]
    n = dev.file_lengths[file]
    assert expand({"file": file, "line_range": [1, n + 500]}, dev) == {
        (file, i) for i in range(1, n + 1)
    }


def test_expand_aceita_range_invertido(dev):
    file = dev.files[0]
    assert expand({"file": file, "line_range": [20, 10]}, dev) == {
        (file, i) for i in range(10, 21)
    }


@pytest.mark.parametrize(
    "pred",
    [
        {"file": "nao/existe.py", "line_range": [1, 2]},
        {"file": "slugify/slugify.py", "line_range": [1]},
        {"file": "slugify/slugify.py"},
        {},
    ],
)
def test_expand_descarta_predicao_malformada(pred, dev):
    assert expand(pred, dev) == set()


# ----------------------------------------------------------------- score()

def test_oraculo_da_um(dev):
    preds = [
        {"file": f, "line_range": [ln, ln], "blind_spot_type": "error_path",
         "evidence_quote": dev.source_line(f, ln).strip(), "confidence": 1.0}
        for f, ln in dev.survivor_lines
    ]
    s = score(preds, dev, "oráculo")
    assert s.precision == s.recall == s.f1 == 1.0
    assert s.mutant_recall == 1.0
    assert s.evidence_valid_rate == 1.0
    assert s.noise_rate == s.near_miss_rate == 0.0


def test_prever_tudo_nao_ganha(dev):
    """A defesa contra jogar a métrica: recall 1.0 comprado com precisão baixa."""
    preds = [{"file": f, "line_range": [1, n]} for f, n in dev.file_lengths.items()]
    s = score(preds, dev, "tudo")
    assert s.recall == 1.0
    assert s.f1 < 0.2
    oracle_f1 = 1.0
    assert s.f1 < oracle_f1


def test_predicao_vazia_nao_divide_por_zero(dev):
    s = score([], dev, "vazio")
    assert (s.precision, s.recall, s.f1) == (0.0, 0.0, 0.0)


def test_linha_morta_conta_como_near_miss_nao_como_ruido(dev):
    file, line = sorted(dev.killed_lines)[0]
    s = score([{"file": file, "line_range": [line, line]}], dev, "near")
    assert s.near_miss_rate == 1.0
    assert s.noise_rate == 0.0
    assert s.precision == 0.0


def test_citacao_inventada_e_flagrada(dev):
    file, line = sorted(dev.survivor_lines)[0]
    s = score(
        [{"file": file, "line_range": [line, line],
          "evidence_quote": "isto não está no arquivo", "blind_spot_type": "error_path"}],
        dev, "citação falsa",
    )
    assert s.precision == 1.0, "acertou a linha"
    assert s.evidence_valid_rate == 0.0, "mas a âncora é inventada"


def test_tipo_fora_da_taxonomia_e_flagrado(dev):
    file, line = sorted(dev.survivor_lines)[0]
    s = score(
        [{"file": file, "line_range": [line, line], "blind_spot_type": "inventado",
          "evidence_quote": dev.source_line(file, line).strip()}],
        dev, "tipo inválido",
    )
    assert s.type_validity_rate == 0.0


def test_predicoes_duplicadas_nao_inflam_a_precisao(dev):
    """Precisão é sobre linhas, não sobre itens: repetir a mesma linha não paga."""
    file, line = sorted(dev.survivor_lines)[0]
    one = {"file": file, "line_range": [line, line]}
    s1 = score([one], dev, "uma")
    s10 = score([one] * 10, dev, "dez")
    assert s1.precision == s10.precision
    assert s1.recall == s10.recall
    assert s10.n_predictions == 10 and s10.n_predicted_lines == 1


def test_mutant_recall_pondera_linhas_densas(dev):
    """Linha com muitos sobreviventes vale mais em mutant_recall que em recall."""
    densest = max(dev.survivors_by_line, key=lambda k: dev.survivors_by_line[k])
    assert dev.survivors_by_line[densest] > 1
    s = score([{"file": densest[0], "line_range": [densest[1], densest[1]]}], dev, "densa")
    assert s.mutant_recall > s.recall


# --------------------------------------------------------------- taxonomia

def test_taxonomia_tem_seis_tipos_e_bate_com_o_prompt():
    assert len(TAXONOMY) == 6
    prompt = (ROOT / "prompts" / "system_taxonomy.md").read_text()
    for t in TAXONOMY:
        assert t in prompt, f"tipo {t} congelado em docs/metric-prediction.md mas ausente do prompt"


def test_metric_md_declara_os_mesmos_conjuntos():
    text = (ROOT / "docs" / "metric-prediction.md").read_text()
    for name in SETS:
        assert name.upper() in text
