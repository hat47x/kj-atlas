#!/usr/bin/env python3
"""Deterministic mock ``/generate`` server for kj-atlas local-LLM (GPU-free) demos.

kj-atlas's local provider (``KJ_ATLAS_LLM_PROVIDER=local``) POSTs to
``{base_url}/generate`` a body ``{"task","prompt","temperature","max_tokens","model"}``
and expects ``{"text": "<JSON>"}`` where ``<JSON>`` is a *string* whose contents match
the strict per-task schema the API then validates. Small CPU-only models rarely emit
that exact JSON reliably, so this stub returns minimal VALID responses per task — letting
you SEE the AI-assisted UI flow without a GPU or a real model.

This is NOT an LLM. Layout is a plain grid, summaries/narratives are canned drafts, and
merge/issue suggestions are empty. Use it only to demonstrate the operational feel.

Usage:
    python3 mock_local_llm.py                       # 127.0.0.1:8001
    python3 mock_local_llm.py --host 0.0.0.0 --port 8001

Then point kj-atlas at it:
    export KJ_ATLAS_LLM_PROVIDER=local
    export KJ_ATLAS_LOCAL_LLM_BASE_URL=http://localhost:8001
    export KJ_ATLAS_LOCAL_LLM_MODEL=mock
"""
from __future__ import annotations

import argparse
import json
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# Card lines in the layout / island-summary prompts:  - id="<id>", text=...
# (island lines use `, title=` instead of `, text=`, so they are not matched.)
_CARD_LINE = re.compile(r'^- id="([^"]+)", text=', re.MULTILINE)
# Reading-order lines in the narrative prompt:  - 1. card id="<id>", ...
_READING_ORDER_LINE = re.compile(r'^- \d+\. \w+ id="([^"]+)"', re.MULTILINE)

_GRID_COLUMNS = 4
_GRID_SPACING_X = 280
_GRID_SPACING_Y = 160


def build_text_for_task(task: str, prompt: str) -> str:
    """Return the stringified per-task JSON the kj-atlas API will ``json.loads(text)``."""
    if task == "re_layout":
        card_ids = _CARD_LINE.findall(prompt)
        cards = [
            {
                "id": card_id,
                "x": (index % _GRID_COLUMNS) * _GRID_SPACING_X,
                "y": (index // _GRID_COLUMNS) * _GRID_SPACING_Y,
            }
            for index, card_id in enumerate(card_ids)
        ]
        return json.dumps({"transform": {"panX": 0, "panY": 0, "zoom": 1}, "cards": cards})

    if task == "suggest_merges":
        return json.dumps({"suggestions": []})

    if task == "suggest_island_summary":
        member_ids = _CARD_LINE.findall(prompt)
        grounding = member_ids[:1] if member_ids else []
        return json.dumps(
            {
                "summaryText": "（モック）メンバーカードに基づく下書き要約です。レビュー前の暫定です。",
                "groundingIds": grounding,
                "warnings": [],
            }
        )

    if task == "summarize_island_relation":
        return json.dumps(
            {
                "text": "（モック）島間の関係に関する下書きの示唆です。確証ではありません。",
                "groundingCardIds": [],
                "groundingEdgeIds": [],
                "warnings": [],
            }
        )

    if task == "generate_narrative":
        order_ids = _READING_ORDER_LINE.findall(prompt)
        return json.dumps(
            {
                "text": "（モック・未レビュー）読み順に沿った解釈の下書きです。事実の主張ではありません。",
                "basedOnReadingOrder": order_ids,
                "warnings": [],
            }
        )

    if task == "check_narrative":
        return json.dumps({"issues": []})

    # No other task strings are emitted by kj-atlas; return an empty object as a safe default.
    return json.dumps({})


class _Handler(BaseHTTPRequestHandler):
    def log_message(self, *_args) -> None:  # keep the console quiet
        return

    def do_POST(self) -> None:
        if self.path.rstrip("/") != "/generate":
            self._send(404, {"error": "not found"})
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
            body = self.rfile.read(length) if length > 0 else b"{}"
            payload = json.loads(body.decode("utf-8"))
        except (ValueError, json.JSONDecodeError):
            self._send(400, {"error": "invalid JSON body"})
            return

        task = str(payload.get("task", ""))
        prompt = payload.get("prompt", "")
        if not isinstance(prompt, str):
            prompt = ""

        self._send(200, {"text": build_text_for_task(task, prompt)})

    def _send(self, status: int, obj: dict) -> None:
        data = json.dumps(obj).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Deterministic mock /generate server for kj-atlas local-LLM demos."
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8001)
    args = parser.parse_args()

    server = ThreadingHTTPServer((args.host, args.port), _Handler)
    print(f"kj-atlas mock /generate server listening on http://{args.host}:{args.port}")
    print("Set KJ_ATLAS_LLM_PROVIDER=local and KJ_ATLAS_LOCAL_LLM_BASE_URL to this URL.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
