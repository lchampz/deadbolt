"""Cliente de modelo com record/replay.

Duas garantias que o brief exige:

1. **Reprodução sem chave.** `DEADZONE_MODE=replay` (default) nunca toca a rede e
   não importa nenhuma dependência de terceiro — só a stdlib. Se faltar gravação,
   quebra alto: nunca silencia, nunca cai para chamada ao vivo, nunca inventa.
2. **Trajetória completa.** Cada chamada grava prompt, resposta, modelo, esforço,
   `stop_reason`, tokens, custo e timestamp em `recordings/`. Esse conjunto de
   arquivos *é* o artefato de trajetória do rubric.

O caminho ao vivo usa o SDK oficial `anthropic` (import tardio, só quando
`DEADZONE_MODE=live`). A chave é resolvida pelo próprio SDK a partir do
ambiente; nunca é lida, impressa, gravada nem incluída em nenhum artefato.

## Decisões de medição registradas aqui, não escondidas

- **`effort` fixo em `high` nos quatro estágios.** É um parâmetro que move
  qualidade e custo; variá-lo entre baseline e solução tornaria a comparação
  inválida. Fica gravado em cada chamada para poder ser auditado.
- **Sem `fallbacks` de recusa.** O SDK oferece troca automática de modelo quando
  um pedido é recusado. Num harness de medição isso seria um modelo diferente
  respondendo no meio da comparação, sem aviso — exatamente o tipo de variável
  não controlada que este projeto existe para expor. Em vez disso,
  `stop_reason == "refusal"` levanta erro e para a execução.
- **Reprodutibilidade honesta.** Opus 5 roda com pensamento adaptativo e não
  aceita `temperature`; duas execuções ao vivo do mesmo prompt podem divergir.
  Por isso o número reportado é o da **gravação**, e o caminho de reprodução do
  juiz é o replay. O caminho ao vivo regrava, não reconfere.
"""

from __future__ import annotations

import hashlib
import json
import os
import time
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RECORDINGS = ROOT / "recordings"

DEFAULT_MODEL = "claude-opus-5"
DEFAULT_EFFORT = "high"
MAX_TOKENS = 48000
# Saída longa vai por streaming: a rodada de reparo devolve o teste inteiro de
# cada falha e estourou 16000 na primeira tentativa. Streaming evita o timeout
# de HTTP que um max_tokens alto provoca em requisição normal.

# USD por 1M tokens (entrada, saída). Fonte e data em REPRODUCTION.md § Cost model.
PRICING = {
    "claude-opus-5": (5.00, 25.00),
    "claude-fable-5": (10.00, 50.00),
    "claude-opus-4-8": (5.00, 25.00),
    "claude-sonnet-5": (2.00, 10.00),
    "claude-haiku-4-5": (1.00, 5.00),
}


class MissingRecording(RuntimeError):
    """Modo replay sem gravação. Falha alta — nunca conserte silenciosamente."""


class ModelRefused(RuntimeError):
    """O modelo recusou. Para a execução em vez de trocar de modelo por baixo."""


@dataclass
class Call:
    key: str
    provider: str
    model: str
    system: str
    prompt: str
    response: str = ""
    effort: str = DEFAULT_EFFORT
    thinking: str = "adaptive"
    stop_reason: str = ""
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = 0.0
    wall_seconds: float = 0.0
    timestamp: str = ""
    stage: str = ""
    unit: str = ""
    error: str = ""

    def as_dict(self) -> dict:
        return self.__dict__.copy()


def _price(model: str, tin: int, tout: int) -> float:
    for name, (pin, pout) in PRICING.items():
        if model.startswith(name):
            return round(tin / 1e6 * pin + tout / 1e6 * pout, 6)
    return 0.0


def cache_key(provider: str, model: str, system: str, prompt: str) -> str:
    blob = json.dumps([provider, model, system, prompt], sort_keys=True).encode()
    return hashlib.sha256(blob).hexdigest()[:20]


@dataclass
class Client:
    provider: str = field(default_factory=lambda: os.environ.get("DEADZONE_PROVIDER", "anthropic"))
    model: str = field(default_factory=lambda: os.environ.get("DEADZONE_MODEL", DEFAULT_MODEL))
    mode: str = field(default_factory=lambda: os.environ.get("DEADZONE_MODE", "replay"))
    effort: str = field(default_factory=lambda: os.environ.get("DEADZONE_EFFORT", DEFAULT_EFFORT))
    recordings: Path = RECORDINGS
    calls: list[Call] = field(default_factory=list)
    cache_read: int = 0
    cache_write: int = 0

    def __post_init__(self) -> None:
        self.recordings.mkdir(parents=True, exist_ok=True)
        if self.mode not in ("replay", "live"):
            raise ValueError(f"DEADZONE_MODE inválido: {self.mode!r} (use replay|live)")

    # ---------------------------------------------------------------- público

    def complete(self, system: str, prompt: str, *, stage: str = "", unit: str = "",
                 cache_system: bool = False) -> Call:
        """`cache_system` marca o bloco system para cache de prefixo.

        O system carrega o módulo e a suíte inteira — dezenas de milhares de
        tokens **idênticos** em toda chamada do mesmo módulo. Sem isso o custo
        por mutante inviabiliza o orçamento (medido no spike: US$ 0,10/chamada).
        A chave de cache do replay NÃO inclui esta flag: ela muda o custo, nunca
        a resposta, e uma gravação feita com cache é igual a uma feita sem.
        """
        key = cache_key(self.provider, self.model, system, prompt)
        path = self.recordings / f"{key}.json"

        if path.exists():
            call = Call(**json.loads(path.read_text()))
            call.stage, call.unit = stage or call.stage, unit or call.unit
            self.calls.append(call)
            return call

        if self.mode == "replay":
            raise MissingRecording(
                f"sem gravação para {key} (stage={stage} unit={unit} model={self.model}).\n"
                f"Rode com DEADZONE_MODE=live e a chave no ambiente para gravar."
            )

        call = Call(key=key, provider=self.provider, model=self.model, system=system,
                    prompt=prompt, effort=self.effort, stage=stage, unit=unit)
        started = time.time()
        try:
            text, tin, tout, stop = self._live(system, prompt, cache_system=cache_system)
        except Exception as exc:  # noqa: BLE001 — o erro vira artefato, mas NUNCA cache
            call.error = f"{type(exc).__name__}: {exc}"
            call.wall_seconds = round(time.time() - started, 3)
            call.timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            self._record_failure(call)
            raise

        call.response, call.input_tokens, call.output_tokens = text, tin, tout
        call.stop_reason = stop
        call.wall_seconds = round(time.time() - started, 3)
        call.cost_usd = _price(self.model, call.input_tokens, call.output_tokens)
        call.timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        path.write_text(json.dumps(call.as_dict(), indent=2, ensure_ascii=False) + "\n")
        self.calls.append(call)
        return call

    def _record_failure(self, call: Call) -> None:
        """Falha vai para recordings/failed/, nunca para o cache de replay.

        A distinção não é cosmética. Uma chamada que morreu com resposta vazia,
        gravada no cache, é indistinguível de um modelo que respondeu vazio: a
        próxima execução em replay serviria o vazio como se fosse resultado. É
        exatamente o modo de falha que este projeto existe para expor, e ele
        apareceu aqui primeiro. As falhas ficam registradas — o brief pede o
        histórico de erro — mas fora do caminho que alimenta a métrica.
        """
        failed = self.recordings / "failed"
        failed.mkdir(parents=True, exist_ok=True)
        stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
        (failed / f"{call.key}-{stamp}.json").write_text(
            json.dumps(call.as_dict(), indent=2, ensure_ascii=False) + "\n"
        )

    def totals(self) -> dict:
        return {
            "n_calls": len(self.calls),
            "input_tokens": sum(c.input_tokens for c in self.calls),
            "output_tokens": sum(c.output_tokens for c in self.calls),
            "cost_usd": round(sum(c.cost_usd for c in self.calls), 6),
            "wall_seconds": round(sum(c.wall_seconds for c in self.calls), 3),
            "model": self.model,
            "provider": self.provider,
            "mode": self.mode,
            "effort": self.effort,
            "cache_read_tokens": self.cache_read,
            "cache_write_tokens": self.cache_write,
        }

    # ----------------------------------------------------------------- rede

    def _live(self, system: str, prompt: str, *, cache_system: bool = False) -> tuple[str, int, int, str]:
        if self.provider != "anthropic":
            raise NotImplementedError(
                f"provider {self.provider!r} não implementado. Este projeto mede um "
                f"modelo só, de propósito: trocar de provider no meio invalidaria a "
                f"comparação baseline↔solução. Para medir outro, rode a suíte inteira "
                f"de novo com DEADZONE_PROVIDER e grave em recordings/ separado."
            )

        import anthropic  # import tardio: o caminho de replay não depende disto

        client = anthropic.Anthropic()
        system_arg = (
            [{"type": "text", "text": system, "cache_control": {"type": "ephemeral"}}]
            if cache_system
            else system
        )
        with client.messages.stream(
            model=self.model,
            max_tokens=MAX_TOKENS,
            system=system_arg,
            thinking={"type": "adaptive"},
            output_config={"effort": self.effort},
            messages=[{"role": "user", "content": prompt}],
        ) as stream:
            response = stream.get_final_message()

        if response.stop_reason == "refusal":
            detail = getattr(response, "stop_details", None)
            raise ModelRefused(
                f"modelo recusou (categoria={getattr(detail, 'category', None)}). "
                f"Nenhum fallback é acionado de propósito — trocar de modelo aqui "
                f"quebraria a comparação. Ver src/deadzone/llm.py."
            )
        if response.stop_reason == "max_tokens":
            raise RuntimeError(
                f"resposta truncada em max_tokens={MAX_TOKENS} (stage/unit na gravação). "
                f"Predição truncada não é predição ruim, é predição ausente — "
                f"aumente MAX_TOKENS e regrave, não pontue isto."
            )

        text = "".join(b.text for b in response.content if b.type == "text")
        u = response.usage
        # tokens lidos do cache custam ~0.1x; escritos custam ~1.25x. Somados à
        # entrada para que o custo reportado seja o real, não o otimista.
        self.cache_read += getattr(u, "cache_read_input_tokens", 0) or 0
        self.cache_write += getattr(u, "cache_creation_input_tokens", 0) or 0
        return text, u.input_tokens, u.output_tokens, response.stop_reason or ""
