"""Cliente LLM provider-agnóstico com record/replay.

Duas garantias que o brief exige:

1. **Reprodução sem chave.** `DEADZONE_MODE=replay` (default) nunca toca a rede.
   Se faltar gravação, quebra alto — nunca silencia nem inventa resposta.
2. **Trajetória completa.** Cada chamada grava prompt, resposta, modelo, tokens,
   custo e timestamp em `recordings/`. É o artefato de trajetória do rubric.

A chave é lida do ambiente pelo processo; nunca é impressa, gravada nem
incluída em nenhum artefato.
"""

from __future__ import annotations

import hashlib
import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RECORDINGS = ROOT / "recordings"

# USD por 1M tokens (entrada, saída). Fonte declarada em REPRODUCTION.md.
PRICING = {
    "claude-opus-4-5": (5.00, 25.00),
    "claude-sonnet-4-5": (3.00, 15.00),
    "claude-haiku-4-5": (1.00, 5.00),
    "gpt-4o-mini": (0.15, 0.60),
    "gpt-4o": (2.50, 10.00),
}


class MissingRecording(RuntimeError):
    """Modo replay sem gravação. Falha alta — R2: nunca conserte silenciosamente."""


@dataclass
class Call:
    key: str
    provider: str
    model: str
    system: str
    prompt: str
    response: str = ""
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
    model: str = field(default_factory=lambda: os.environ.get("DEADZONE_MODEL", "claude-opus-4-5"))
    mode: str = field(default_factory=lambda: os.environ.get("DEADZONE_MODE", "replay"))
    recordings: Path = RECORDINGS
    calls: list[Call] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.recordings.mkdir(parents=True, exist_ok=True)
        if self.mode not in ("replay", "live"):
            raise ValueError(f"DEADZONE_MODE inválido: {self.mode!r} (use replay|live)")

    # ---------------------------------------------------------------- público

    def complete(self, system: str, prompt: str, *, stage: str = "", unit: str = "") -> Call:
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

        call = Call(key=key, provider=self.provider, model=self.model,
                    system=system, prompt=prompt, stage=stage, unit=unit)
        started = time.time()
        try:
            text, tin, tout = self._live(system, prompt)
            call.response, call.input_tokens, call.output_tokens = text, tin, tout
        except Exception as exc:  # noqa: BLE001 — o erro vira artefato, não é engolido
            call.error = f"{type(exc).__name__}: {exc}"
            raise
        finally:
            call.wall_seconds = round(time.time() - started, 3)
            call.cost_usd = _price(self.model, call.input_tokens, call.output_tokens)
            call.timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
            path.write_text(json.dumps(call.as_dict(), indent=2, ensure_ascii=False) + "\n")
            self.calls.append(call)
        return call

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
        }

    # ----------------------------------------------------------------- rede

    def _live(self, system: str, prompt: str) -> tuple[str, int, int]:
        if self.provider == "anthropic":
            key = os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("DEADZONE_API_KEY")
            if not key:
                raise RuntimeError("ANTHROPIC_API_KEY ausente")
            body = {
                "model": self.model,
                "max_tokens": 8000,
                "system": system,
                "messages": [{"role": "user", "content": prompt}],
            }
            data = self._post(
                "https://api.anthropic.com/v1/messages",
                body,
                {"x-api-key": key, "anthropic-version": "2023-06-01"},
            )
            text = "".join(b.get("text", "") for b in data.get("content", []))
            usage = data.get("usage", {})
            return text, usage.get("input_tokens", 0), usage.get("output_tokens", 0)

        if self.provider == "openai":
            key = os.environ.get("OPENAI_API_KEY") or os.environ.get("DEADZONE_API_KEY")
            if not key:
                raise RuntimeError("OPENAI_API_KEY ausente")
            base = os.environ.get("DEADZONE_BASE_URL", "https://api.openai.com/v1")
            body = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt},
                ],
            }
            data = self._post(f"{base}/chat/completions", body, {"Authorization": f"Bearer {key}"})
            text = data["choices"][0]["message"]["content"]
            usage = data.get("usage", {})
            return text, usage.get("prompt_tokens", 0), usage.get("completion_tokens", 0)

        raise ValueError(f"provider desconhecido: {self.provider}")

    @staticmethod
    def _post(url: str, body: dict, headers: dict) -> dict:
        req = urllib.request.Request(
            url,
            data=json.dumps(body).encode(),
            headers={"content-type": "application/json", **headers},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=180) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode()[:400]
            raise RuntimeError(f"HTTP {exc.code}: {detail}") from None
