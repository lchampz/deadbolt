"""Diagnóstico de credencial — separa "chave inválida" de "saldo/limite zerado".

Usa apenas endpoints que não consomem token. Nunca imprime a chave.

    env ANTHROPIC_API_KEY="$(cat ~/.anthropic_key)" python scripts/check_credentials.py
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request

KEY = os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN")
if not KEY:
    sys.exit("nenhuma credencial no ambiente (ANTHROPIC_API_KEY / ANTHROPIC_AUTH_TOKEN)")

HEADERS = {"x-api-key": KEY, "anthropic-version": "2023-06-01",
           "content-type": "application/json"}
print(f"credencial presente: {len(KEY)} chars, prefixo {KEY[:7]}…\n")


def call(name: str, url: str, body: dict | None = None) -> None:
    req = urllib.request.Request(
        url, headers=HEADERS, method="POST" if body else "GET",
        data=json.dumps(body).encode() if body else None,
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.loads(r.read())
        if name == "models":
            ids = [m.get("id") for m in data.get("data", [])]
            print(f"[200] {name}: {len(ids)} modelos visíveis")
            print(f"      {', '.join(str(i) for i in ids[:6])}")
        else:
            print(f"[200] {name}: {json.dumps(data)[:200]}")
    except urllib.error.HTTPError as e:
        detail = json.loads(e.read() or b"{}").get("error", {})
        print(f"[{e.code}] {name}: {detail.get('type')} — {detail.get('message')}")
    except Exception as e:  # noqa: BLE001
        print(f"[erro] {name}: {type(e).__name__}: {e}")


# 1. Endpoint gratuito: não consome token, não checa saldo de inferência.
call("models", "https://api.anthropic.com/v1/models")

# 2. Contagem de tokens: valida o corpo do pedido, também sem consumir cota.
call("count_tokens", "https://api.anthropic.com/v1/messages/count_tokens",
     {"model": "claude-opus-5", "messages": [{"role": "user", "content": "oi"}]})

# 3. Inferência mínima: 1 token de saída. É aqui que saldo/limite mordem.
call("messages(1 token)", "https://api.anthropic.com/v1/messages",
     {"model": "claude-opus-5", "max_tokens": 1,
      "messages": [{"role": "user", "content": "oi"}]})

print("""
Leitura:
  models 200 + messages 400 saldo → chave válida; bloqueio é de crédito ou de
    limite de gasto do WORKSPACE. Créditos são por organização: recarregar a org
    A não destrava uma chave da org B, e um workspace com spend limit em zero
    produz esta mesma mensagem mesmo com a org cheia.
  models 401 → chave inválida ou revogada.
  tudo 200 → pode rodar: make run-all
""")
