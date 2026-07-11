"""Deterministic local-LLM stub for release-candidate provider verification.

Implements the exact HTTP contract LocalProvider speaks (POST {base_url}/generate
with {task, prompt, temperature, max_tokens, model} -> {"text": <string>}), so
KJ_ATLAS_LLM_PROVIDER=local can be exercised end-to-end through the real
provider transport, request audit, and response parsing code paths without a
real inference server. Responses are deterministic and derived only from the
request prompt (card ids are extracted from the prompt's `- id="..."` lines),
which keeps the e2e evidence reproducible.

This is a verification harness, not a product feature: it never runs in any
user-facing deployment, and it produces proposal-only content exactly like a
real provider would -- adoption still requires an explicit human action in
the UI (DOMAIN-EXPR-03 / ADR-0042 proposal-only invariant).

Run via docker-compose.llm-stub.yml (see that file for wiring).
"""

import json
import re
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = 8089
ID_PATTERN = re.compile(r'- id="([^"]+)"')


def build_re_layout_text(prompt: str) -> str:
    # The layout parser requires every card id exactly once. The e2e fixture
    # must not contain islands: island lines also match `- id="..."` and
    # would corrupt the extracted card list.
    card_ids = ID_PATTERN.findall(prompt)
    return json.dumps(
        {
            "transform": {"panX": 0, "panY": 0, "zoom": 1},
            "cards": [
                {"id": card_id, "x": 120 + index * 260, "y": 140}
                for index, card_id in enumerate(card_ids)
            ],
            "notes": "llm-stub: deterministic grid layout (provider=local success path)",
        }
    )


def build_suggest_merges_text(prompt: str) -> str:
    card_ids = ID_PATTERN.findall(prompt)
    if len(card_ids) < 2:
        return json.dumps({"suggestions": []})
    return json.dumps(
        {
            "suggestions": [
                {
                    "groupId": "llm-stub-group-1",
                    "cardIds": card_ids[:2],
                    "mergedTextDraft": "llm-stub merged draft",
                    "rationale": "llm-stub deterministic candidate",
                }
            ]
        }
    )


class StubHandler(BaseHTTPRequestHandler):
    def do_POST(self) -> None:  # noqa: N802 (http.server API)
        if self.path.rstrip("/") != "/generate":
            self.send_error(404)
            return

        length = int(self.headers.get("Content-Length", "0"))
        payload = json.loads(self.rfile.read(length).decode("utf-8"))
        task = payload.get("task", "")
        prompt = payload.get("prompt", "")

        if task == "re_layout":
            text = build_re_layout_text(prompt)
        elif task == "suggest_merges":
            text = build_suggest_merges_text(prompt)
        else:
            # Unknown tasks get an empty JSON object; callers that reach this
            # in the e2e are out of scope and will surface a 422 upstream,
            # which is itself a visible signal rather than a silent pass.
            text = "{}"

        body = json.dumps({"text": text}).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: object) -> None:  # noqa: A002
        print(f"[llm-stub] {format % args}", flush=True)


if __name__ == "__main__":
    print(f"[llm-stub] listening on :{PORT}", flush=True)
    HTTPServer(("0.0.0.0", PORT), StubHandler).serve_forever()
