#!/usr/bin/env python3
"""DeepSeek API adapter for kj-atlas — DEPRECATED.

Use ``openai_compatible_adapter.py`` instead. This file is retained for
backward compatibility only and will be removed in a future release.

    python3 openai_compatible_adapter.py --port 8001 \
      --base-url https://api.deepseek.com/v1 --model deepseek-v4-flash

(Original docstring follows)
---

DeepSeek API adapter for kj-atlas local LLM provider.

Bridges DeepSeek's OpenAI-compatible chat completions API to kj-atlas's
``POST /generate`` contract. Requires a DeepSeek API key.

Setup:
    1. Set environment variable:
       export DEEPSEEK_API_KEY="sk-..."

    2. Start adapter:
       python3 deepseek_adapter.py --port 8001

    3. Point kj-atlas at it:
       KJ_ATLAS_LLM_PROVIDER=local
       KJ_ATLAS_LOCAL_LLM_BASE_URL=http://localhost:8001
       KJ_ATLAS_LOCAL_LLM_MODEL=deepseek-chat

DeepSeek API docs: https://api-docs.deepseek.com/
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import requests

logger = logging.getLogger("deepseek-adapter")

DEEPSEEK_API_BASE = "https://api.deepseek.com/v1"
DEFAULT_MODEL = "deepseek-chat"


class DeepSeekAdapter(BaseHTTPRequestHandler):
    api_key: str = ""
    model: str = DEFAULT_MODEL
    timeout: int = 120  # seconds

    def do_POST(self):
        if self.path.rstrip("/") != "/generate":
            self.send_error(404)
            return

        try:
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length))
        except (ValueError, json.JSONDecodeError):
            self._respond(400, {"error": "invalid JSON"})
            return

        task = body.get("task", "")
        prompt = body.get("prompt", "")
        temperature = float(body.get("temperature", 0.2))
        max_tokens = int(body.get("max_tokens", 2000))

        logger.info("task=%s model=%s prompt_len=%d", task, self.model, len(prompt))

        try:
            text = self._call_deepseek(prompt, temperature, max_tokens)
            text = self._extract_json(text)
            self._respond(200, {"text": text})
        except Exception as exc:
            logger.error("DeepSeek API call failed: %s", exc)
            self._respond(502, {"error": str(exc)})

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(
            json.dumps({"status": "ok", "model": self.model,
                        "provider": "deepseek"}).encode()
        )

    def _call_deepseek(self, prompt: str, temperature: float,
                       max_tokens: int) -> str:
        resp = requests.post(
            f"{DEEPSEEK_API_BASE}/chat/completions",
            json={
                "model": self.model,
                "messages": [
                    {"role": "system",
                     "content": "You are a precise JSON generator. "
                     "Return ONLY valid JSON matching the requested schema. "
                     "No markdown, no explanation, no code fences."},
                    {"role": "user", "content": prompt},
                ],
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": False,
            },
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            timeout=self.timeout,
        )
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]

    @staticmethod
    def _extract_json(text: str) -> str:
        """Extract JSON from model output (may contain markdown fences)."""
        fence = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
        if fence:
            candidate = fence.group(1).strip()
            try:
                json.loads(candidate)
                return candidate
            except json.JSONDecodeError:
                pass
        # Try direct JSON
        text = text.strip()
        if text.startswith("{") or text.startswith("["):
            try:
                json.loads(text)
                return text
            except json.JSONDecodeError:
                pass
        return text

    def _respond(self, status: int, data: dict) -> None:
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        logger.info("%s", fmt % args)


def main():
    parser = argparse.ArgumentParser(
        description="DeepSeek API adapter for kj-atlas")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8001)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--api-key", default=None,
                        help="DeepSeek API key (default: $DEEPSEEK_API_KEY)")
    parser.add_argument("--api-base", default=DEEPSEEK_API_BASE)
    parser.add_argument("--timeout", type=int, default=120)
    args = parser.parse_args()

    api_key = args.api_key or os.environ.get("DEEPSEEK_API_KEY", "")
    if not api_key:
        logger.error(
            "No DeepSeek API key found. Set DEEPSEEK_API_KEY env var "
            "or pass --api-key.")
        sys.exit(1)

    DeepSeekAdapter.api_key = api_key
    DeepSeekAdapter.model = args.model
    DeepSeekAdapter.timeout = args.timeout
    global DEEPSEEK_API_BASE
    DEEPSEEK_API_BASE = args.api_base

    logging.basicConfig(level=logging.INFO, stream=sys.stderr)
    server = ThreadingHTTPServer((args.host, args.port), DeepSeekAdapter)
    logger.info("DeepSeek adapter on http://%s:%s (model=%s)",
                args.host, args.port, args.model)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down")
        server.shutdown()


if __name__ == "__main__":
    main()
