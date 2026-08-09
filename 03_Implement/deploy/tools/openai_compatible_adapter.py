#!/usr/bin/env python3
"""OpenAI-compatible API adapter for kj-atlas local LLM provider.

A single adapter that works with ANY OpenAI-compatible API endpoint:
DeepSeek, OpenAI, Ollama (v0.1.14+), Groq, Together, vLLM, etc.

Bridges the provider's chat completions API to kj-atlas's
``POST /generate`` contract::

    POST /generate  {"task","prompt","temperature","max_tokens","model"}
    → {"text": "<JSON>"}

Quick start:
    # Ollama (local, free)
    python3 openai_compatible_adapter.py --port 8001

    # DeepSeek (cloud, high quality)
    export LLM_API_KEY="sk-..."
    python3 openai_compatible_adapter.py --port 8001 \
      --base-url https://api.deepseek.com/v1 --model deepseek-chat

    # OpenAI
    export LLM_API_KEY="sk-..."
    python3 openai_compatible_adapter.py --port 8001 \
      --base-url https://api.openai.com/v1 --model gpt-4o-mini

Design:
    This is the canonical production adapter. Provider-specific adapters
    (ollama_adapter.py, deepseek_adapter.py) are superseded by this
    unified implementation. mock_local_llm.py remains the test-only stub.
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

logger = logging.getLogger("openai-adapter")

# Defaults — override via CLI or environment.
DEFAULT_BASE_URL = os.environ.get("LLM_API_BASE_URL", "http://localhost:11434/v1")
DEFAULT_MODEL = os.environ.get("LLM_MODEL", "deepseek-r1:7b")
DEFAULT_API_KEY = os.environ.get("LLM_API_KEY", "")
DEFAULT_TIMEOUT = 120
# Most OpenAI-compatible APIs use this header. Override with --api-key-header
# for non-standard providers.
DEFAULT_API_KEY_HEADER = "Bearer"

# JSON schema enforced via system prompt for reliable structured output.
_SYSTEM_PROMPT = (
    "You are a precise JSON generator. Return ONLY valid JSON matching "
    "the requested schema. No markdown, no explanation, no code fences. "
    "No  tags. No commentary before or after the JSON."
)


class OpenAICompatibleAdapter(BaseHTTPRequestHandler):
    """HTTP handler bridging OpenAI-compatible API → kj-atlas /generate."""

    base_url: str = DEFAULT_BASE_URL
    model: str = DEFAULT_MODEL
    api_key: str = DEFAULT_API_KEY
    api_key_header: str = DEFAULT_API_KEY_HEADER
    timeout: int = DEFAULT_TIMEOUT

    # ---- HTTP dispatch ----

    def do_POST(self):
        if self.path.rstrip("/") != "/generate":
            self.send_error(404)
            return

        try:
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length))
        except (ValueError, json.JSONDecodeError):
            self._respond(400, {"error": "invalid JSON body"})
            return

        task = body.get("task", "")
        prompt = str(body.get("prompt", ""))
        temperature = float(body.get("temperature", 0.2))
        max_tokens = int(body.get("max_tokens", 2000))

        logger.info("task=%s model=%s prompt_len=%d url=%s",
                     task, self.model, len(prompt), self.base_url)

        try:
            text = self._call_api(prompt, temperature, max_tokens)
            text = _extract_json(text)
            self._respond(200, {"text": text})
        except requests.HTTPError as exc:
            logger.error("API HTTP error %s: %s", exc.response.status_code,
                         exc.response.text[:200] if exc.response else "")
            self._respond(502, {"error": f"upstream API error: {exc}"})
        except requests.Timeout:
            self._respond(504, {"error": "upstream API timeout"})
        except Exception as exc:
            logger.error("API call failed: %s", exc)
            self._respond(502, {"error": str(exc)})

    def do_GET(self):
        self._respond(200, {
            "status": "ok", "model": self.model,
            "base_url": self.base_url, "type": "openai-compatible",
        })

    # ---- Internal ----

    def _call_api(self, prompt: str, temperature: float,
                  max_tokens: int) -> str:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = (
                f"{self.api_key_header} {self.api_key}"
                if self.api_key_header else self.api_key
            )

        resp = requests.post(
            f"{self.base_url}/chat/completions",
            json={
                "model": self.model,
                "messages": [
                    {"role": "system", "content": _SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": False,
            },
            headers=headers,
            timeout=self.timeout,
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]

    def _respond(self, status: int, data: dict) -> None:
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt: str, *args) -> None:
        logger.info("%s", fmt % args)


# ---- JSON extraction (shared) ----


def _extract_json(text: str) -> str:
    """Extract JSON from model output.

    Handles: markdown ```json fences,  tags (deepseek-r1),
    leading/trailing text, and bare JSON objects/arrays.
    """
    text = text.strip()

    # Strip deepseek-r1  reasoning blocks
    text = re.sub(r"", "", text)
    text = re.sub(r"", "", text)

    # Try markdown code fences
    fence = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if fence:
        candidate = fence.group(1).strip()
        if _is_valid_json(candidate):
            return candidate

    # Try the longest JSON-like substring (handles text before/after JSON)
    for pattern in [r"\{[\s\S]*\}", r"\[[\s\S]*\]"]:
        matches = list(re.finditer(pattern, text))
        for match in reversed(matches):
            candidate = match.group(0)
            if _is_valid_json(candidate):
                return candidate

    return text


def _is_valid_json(text: str) -> bool:
    try:
        json.loads(text)
        return True
    except (json.JSONDecodeError, ValueError):
        return False


# ---- Entry point ----


def main():
    parser = argparse.ArgumentParser(
        description="OpenAI-compatible adapter for kj-atlas /generate")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8001)
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL,
                        help="API base URL (default: $LLM_API_BASE_URL or Ollama)")
    parser.add_argument("--model", default=DEFAULT_MODEL,
                        help="Model name (default: $LLM_MODEL or deepseek-r1:7b)")
    parser.add_argument("--api-key", default=DEFAULT_API_KEY,
                        help="API key (default: $LLM_API_KEY)")
    parser.add_argument("--api-key-header", default=DEFAULT_API_KEY_HEADER,
                        help="Auth header prefix (default: 'Bearer')")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT)
    args = parser.parse_args()

    OpenAICompatibleAdapter.base_url = args.base_url.rstrip("/")
    OpenAICompatibleAdapter.model = args.model
    OpenAICompatibleAdapter.api_key = args.api_key
    OpenAICompatibleAdapter.api_key_header = args.api_key_header
    OpenAICompatibleAdapter.timeout = args.timeout

    logging.basicConfig(level=logging.INFO, stream=sys.stderr)
    server = ThreadingHTTPServer((args.host, args.port), OpenAICompatibleAdapter)
    logger.info("OpenAI-compatible adapter on http://%s:%s → %s (model=%s)",
                args.host, args.port, args.base_url, args.model)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down")
        server.shutdown()


if __name__ == "__main__":
    main()
