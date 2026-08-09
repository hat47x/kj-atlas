#!/usr/bin/env python3
"""Ollama adapter for kj-atlas — DEPRECATED.

Use ``openai_compatible_adapter.py`` instead. This file is retained for
backward compatibility only and will be removed in a future release.

Ollama v0.1.14+ supports the OpenAI-compatible API natively, so the
unified adapter works with Ollama out of the box:

    python3 openai_compatible_adapter.py --port 8001

(Original docstring follows)
---

Ollama adapter for kj-atlas local LLM provider.

Bridges Ollama's native API to kj-atlas's ``POST /generate`` contract::

    POST /generate
    {"task": "...", "prompt": "...", "temperature": 0.2, "max_tokens": 2000, "model": "..."}
    → {"text": "<JSON>"}

Usage:
    python3 ollama_adapter.py                           # 127.0.0.1:8001
    python3 ollama_adapter.py --host 0.0.0.0 --port 8001 --model deepseek-r1:14b

Then point kj-atlas at it:
    KJ_ATLAS_LLM_PROVIDER=local
    KJ_ATLAS_LOCAL_LLM_BASE_URL=http://localhost:8001
    KJ_ATLAS_LOCAL_LLM_MODEL=deepseek-r1:7b
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import requests

logger = logging.getLogger("ollama-adapter")


class OllamaAdapter(BaseHTTPRequestHandler):
    ollama_base = "http://localhost:11434"
    model = "deepseek-r1:7b"
    timeout = 120  # seconds — local models can be slow

    def do_POST(self):
        if self.path != "/generate":
            self.send_error(404)
            return

        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length))

        task = body.get("task", "")
        prompt = body.get("prompt", "")
        temperature = float(body.get("temperature", 0.2))
        max_tokens = int(body.get("max_tokens", 2000))
        model = body.get("model", self.model)

        logger.info("task=%s model=%s prompt_len=%d", task, model, len(prompt))

        try:
            text = self._call_ollama(prompt, temperature, max_tokens, model)
            # Extract JSON from the response (deepseek-r1 wraps in <｜end▁of▁thinking｜>)
            text = self._extract_json(text)
            self._respond(200, {"text": text})
        except Exception as exc:
            logger.error("Ollama call failed: %s", exc)
            self._respond(502, {"error": str(exc)})

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(
            json.dumps({"status": "ok", "model": self.model}).encode()
        )

    def _call_ollama(self, prompt, temperature, max_tokens, model):
        resp = requests.post(
            f"{self.ollama_base}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens,
                },
            },
            timeout=self.timeout,
        )
        resp.raise_for_status()
        return resp.json()["response"]

    @staticmethod
    def _extract_json(text: str) -> str:
        """Extract JSON from model output — handles deepseek-r1  blocks,
        markdown ```json fences, and bare JSON objects."""
        # Strip  reasoning blocks (deepseek-r1)
        text = re.sub(r"", "", text)
        text = re.sub(r"", "", text)

        # Try markdown code fences first
        fence = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
        if fence:
            candidate = fence.group(1).strip()
            try:
                json.loads(candidate)
                return candidate
            except json.JSONDecodeError:
                pass

        # Try to find the LAST JSON-like block (deepseek-r1 puts reasoning
        # before the actual answer)
        for pattern in [r"\{[\s\S]*\}", r"\[[\s\S]*\]"]:
            matches = list(re.finditer(pattern, text))
            for match in reversed(matches):  # Try last match first
                candidate = match.group(0)
                try:
                    json.loads(candidate)
                    return candidate
                except json.JSONDecodeError:
                    continue

        # Fallback: return stripped text
        return text.strip()

    def _respond(self, status, data):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def log_message(self, fmt, *args):
        logger.info("%s", fmt % args)


def main():
    parser = argparse.ArgumentParser(description="Ollama adapter for kj-atlas")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8001)
    parser.add_argument("--model", default="deepseek-r1:7b")
    parser.add_argument("--ollama-base", default="http://localhost:11434")
    parser.add_argument("--timeout", type=int, default=120)
    args = parser.parse_args()

    OllamaAdapter.model = args.model
    OllamaAdapter.ollama_base = args.ollama_base
    OllamaAdapter.timeout = args.timeout

    logging.basicConfig(level=logging.INFO, stream=sys.stderr)
    server = ThreadingHTTPServer((args.host, args.port), OllamaAdapter)
    logger.info(
        "Ollama adapter listening on %s:%s → %s (model=%s)",
        args.host,
        args.port,
        args.ollama_base,
        args.model,
    )
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down")
        server.shutdown()


if __name__ == "__main__":
    main()
