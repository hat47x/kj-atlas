#!/usr/bin/env python3
"""OpenAI-compatible API adapter for kj-atlas — multi-LLM routing.

Routes kj-atlas /generate requests to different LLM backends based on
the ``model`` field in the request body. Supports simultaneous use of
multiple providers with different models, API keys, and endpoints.

Usage:
    # Single backend (Ollama)
    python3 openai_compatible_adapter.py --port 8001

    # Multiple backends with per-model routing
    python3 openai_compatible_adapter.py --port 8001 --backends "
      deepseek-chat@https://api.deepseek.com/v1:sk-xxx,
      deepseek-reasoner@https://api.deepseek.com/v1:sk-xxx,
      llama3@http://localhost:11434/v1:
    "

    # Via environment
    export LLM_DEFAULT_BASE_URL=http://localhost:11434/v1
    export LLM_DEFAULT_API_KEY=""
    export LLM_BACKENDS="deepseek-chat@https://api.deepseek.com/v1:sk-xxx"
    python3 openai_compatible_adapter.py --port 8001

Backend config format: ``model@base_url:api_key``

- ``model``: model name (matched against /generate request ``model`` field)
- ``base_url``: API base URL (OpenAI-compatible)
- ``api_key``: API key (empty string for no-auth, e.g. local Ollama)
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
import sys
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import requests

logger = logging.getLogger("openai-adapter")

_SYSTEM_PROMPT = (
    "You are a precise JSON generator. Return ONLY valid JSON matching "
    "the requested schema. No markdown, no explanation, no code fences."
)


# ---- Backend config ----


@dataclass
class Backend:
    model: str
    base_url: str
    api_key: str


def _parse_backends(raw: str) -> dict[str, Backend]:
    """Parse backend config string into {model_name: Backend} map.

    Format: "model@base_url:api_key,model2@base_url2:api_key2,..."
    """
    backends: dict[str, Backend] = {}
    if not raw.strip():
        return backends
    for entry in raw.split(","):
        entry = entry.strip()
        if not entry:
            continue
        model, rest = entry.split("@", 1)
        if ":" in rest:
            base_url, api_key = rest.rsplit(":", 1)
        else:
            base_url, api_key = rest, ""
        backends[model.strip()] = Backend(
            model=model.strip(), base_url=base_url.strip(),
            api_key=api_key.strip(),
        )
    return backends


# ---- JSON extraction ----


def _extract_json(text: str) -> str:
    text = re.sub(r"", "", text)
    text = re.sub(r"", "", text)
    fence = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if fence:
        candidate = fence.group(1).strip()
        if _is_valid_json(candidate):
            return candidate
    for pattern in [r"\{[\s\S]*\}", r"\[[\s\S]*\]"]:
        matches = list(re.finditer(pattern, text))
        for match in reversed(matches):
            candidate = match.group(0)
            if _is_valid_json(candidate):
                return candidate
    return text.strip()


def _is_valid_json(text: str) -> bool:
    try:
        json.loads(text)
        return True
    except (json.JSONDecodeError, ValueError):
        return False


# ---- HTTP handler ----


class MultiBackendAdapter(BaseHTTPRequestHandler):
    """Routes /generate requests to the correct LLM backend by model name."""

    backends: dict[str, Backend] = {}
    default_backend: Backend | None = None
    timeout: int = 120

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
        model = str(body.get("model", ""))

        backend = self._resolve_backend(model)
        logger.info("task=%s model=%s → %s", task, model, backend.base_url)

        try:
            text = self._call_backend(backend, prompt, temperature, max_tokens)
            text = _extract_json(text)
            self._respond(200, {"text": text})
        except requests.HTTPError as exc:
            logger.error("HTTP %s: %s", exc.response.status_code if exc.response else "?", str(exc)[:200])
            self._respond(502, {"error": f"upstream error: {exc}"})
        except requests.Timeout:
            self._respond(504, {"error": "upstream timeout"})
        except Exception as exc:
            logger.error("Failed: %s", exc)
            self._respond(502, {"error": str(exc)})

    def do_GET(self):
        self._respond(200, {
            "status": "ok", "type": "openai-compatible-multi-backend",
            "backends": list(self.backends.keys()),
            "default": self.default_backend.model if self.default_backend else None,
        })

    def _resolve_backend(self, model: str) -> Backend:
        if self.backends.get(model):
            return self.backends[model]
        if self.default_backend:
            return self.default_backend
        raise RuntimeError(f"No backend for model '{model}' and no default configured")

    def _call_backend(self, backend: Backend, prompt: str,
                      temperature: float, max_tokens: int) -> str:
        headers = {"Content-Type": "application/json"}
        if backend.api_key:
            headers["Authorization"] = f"Bearer {backend.api_key}"
        resp = requests.post(
            f"{backend.base_url}/chat/completions",
            json={
                "model": backend.model,
                "messages": [
                    {"role": "system", "content": _SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                "temperature": temperature, "max_tokens": max_tokens,
                "stream": False,
            },
            headers=headers, timeout=self.timeout,
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


# ---- Entry point ----


def main():
    parser = argparse.ArgumentParser(
        description="Multi-backend OpenAI-compatible adapter for kj-atlas")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8001)
    parser.add_argument("--backends", default=os.environ.get("LLM_BACKENDS", ""),
                        help='"model@base_url:api_key,model2@base_url2:key2,..."')
    parser.add_argument("--default-base-url",
                        default=os.environ.get("LLM_DEFAULT_BASE_URL",
                                               "http://localhost:11434/v1"))
    parser.add_argument("--default-model",
                        default=os.environ.get("LLM_DEFAULT_MODEL", "local"))
    parser.add_argument("--default-api-key",
                        default=os.environ.get("LLM_DEFAULT_API_KEY", ""))
    parser.add_argument("--timeout", type=int, default=120)
    args = parser.parse_args()

    backends = _parse_backends(args.backends)
    default = Backend(model=args.default_model,
                      base_url=args.default_base_url.rstrip("/"),
                      api_key=args.default_api_key)

    MultiBackendAdapter.backends = backends
    MultiBackendAdapter.default_backend = default
    MultiBackendAdapter.timeout = args.timeout

    logging.basicConfig(level=logging.INFO, stream=sys.stderr)
    server = ThreadingHTTPServer((args.host, args.port), MultiBackendAdapter)
    logger.info("Multi-backend adapter on http://%s:%s", args.host, args.port)
    logger.info("  Default: %s → %s", default.model, default.base_url)
    for b in backends.values():
        logger.info("  Backend: %s → %s", b.model, b.base_url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down")
        server.shutdown()


if __name__ == "__main__":
    main()
