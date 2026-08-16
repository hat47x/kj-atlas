#!/usr/bin/env python3
"""Dogfood E2E: the `kj` CLI (channel=cli) is audited through CE-4.

Proves the "administrator writes their own script / uses the CLI" non-Web path
end-to-end: a `kj` CLI `context-query` call is reported to the backend's
POST /docs/{id}/context-audit with channel="cli", and that event reaches the
configured HTTP audit sink. Symmetric to verify_mcp_ce4_audit_e2e.py
(channel=mcp) — this one freezes the CLI's channel.

Chain exercised (self-contained, deterministic, no billing):
  audit sink (this script) <- POST <- backend (uvicorn, audit transport=http)
      <- POST /docs/{id}/context-audit (channel=cli, operation=query)
          <- `kj` CLI (python -m kj_atlas_api.cli context-query)

Usage:
  .venv/bin/python scripts/verify_cli_ce4_audit_e2e.py [PORT]

Requires the backend venv. Uses free ports for the backend and audit sink.
The backend runs WITHOUT an API key (local-dev open mode): the `kj` CLI does
not send X-API-Key (it only carries optional x-actor-ref / x-trace-id), which
is exactly the deployment this path targets.
"""

from __future__ import annotations

import http.server
import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import time
import urllib.request

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT_DIR = os.path.dirname(os.path.dirname(BACKEND_DIR))
VENV_PYTHON = os.path.join(BACKEND_DIR, ".venv", "bin", "python")
DOC_ID = "cli-audit-doc"

PASS = 0
FAIL = 0


def check(desc: str, expected, actual) -> None:
    global PASS, FAIL
    if actual == expected:
        print(f"  PASS: {desc}")
        PASS += 1
    else:
        print(f"  FAIL: {desc} (expected {expected}, got {actual})")
        FAIL += 1


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class AuditSink:
    """Captures the backend's HTTP audit POSTs in-process for later assertion."""

    def __init__(self, port: int) -> None:
        self.events: list[dict] = []
        self._lock = threading.Lock()

        class _Handler(http.server.BaseHTTPRequestHandler):
            def do_POST(self) -> None:  # noqa: N802
                length = int(self.headers.get("Content-Length", "0"))
                body = self.rfile.read(length) if length else b""
                try:
                    with events_lock:
                        _events.append(json.loads(body.decode("utf-8")))
                except (ValueError, UnicodeDecodeError):
                    pass
                self.send_response(200)
                self.send_header("Content-Length", "0")
                self.end_headers()

            def log_message(self, *_args) -> None:
                return

        _events: list[dict] = self.events
        events_lock: threading.Lock = self._lock
        self._server = http.server.ThreadingHTTPServer(("127.0.0.1", port), _Handler)
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)

    def start(self) -> None:
        self._thread.start()

    def stop(self) -> None:
        self._server.shutdown()
        self._server.server_close()

    def snapshot(self) -> list[dict]:
        with self._lock:
            return list(self.events)


def _migrate(db_path: str) -> None:
    env = dict(os.environ, KJ_ATLAS_DATABASE_URL=f"sqlite:///{db_path}")
    subprocess.run(
        [VENV_PYTHON, "-m", "alembic", "upgrade", "head"],
        cwd=BACKEND_DIR,
        env=env,
        check=True,
        capture_output=True,
    )


def _put_document(base_url: str, doc: dict) -> None:
    req = urllib.request.Request(
        f"{base_url}/docs/{doc['id']}",
        data=json.dumps(doc).encode("utf-8"),
        method="PUT",
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as resp:
        if resp.status != 200:
            raise RuntimeError(f"PUT document failed: HTTP {resp.status}")


def main() -> int:
    sink_port = free_port()
    backend_port = free_port()
    base_url = f"http://127.0.0.1:{backend_port}"
    sink = AuditSink(sink_port)
    sink.start()

    tmp = tempfile.mkdtemp(prefix="kj_cli_audit_")
    db_path = os.path.join(tmp, "cli_audit.sqlite3")
    backend_proc: subprocess.Popen | None = None
    try:
        print("=== kj CLI -> CE-4 audit (channel=cli) -> HTTP sink e2e ===")
        _migrate(db_path)

        backend_env = dict(
            os.environ,
            KJ_ATLAS_DATABASE_URL=f"sqlite:///{db_path}",
            KJ_ATLAS_AUDIT_EXPORT_ENABLED="1",
            KJ_ATLAS_AUDIT_TRANSPORT="http",
            KJ_ATLAS_AUDIT_HTTP_ENDPOINT=f"http://127.0.0.1:{sink_port}/audit",
            KJ_ATLAS_AUDIT_ALLOW_IN_SAFE_MODE="1",
        )
        backend_proc = subprocess.Popen(
            [VENV_PYTHON, "-m", "uvicorn", "kj_atlas_api.main:app", "--port", str(backend_port), "--host", "127.0.0.1"],
            cwd=BACKEND_DIR,
            env=backend_env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        for _ in range(40):
            try:
                with urllib.request.urlopen(f"{base_url}/healthz", timeout=1) as resp:
                    if resp.status == 200:
                        break
            except Exception:
                pass
            time.sleep(0.5)
        check("backend /healthz", 200, _health(base_url))

        doc = {
            "version": 1,
            "id": DOC_ID,
            "title": "CLI audit e2e",
            "createdAt": "2026-08-16T00:00:00Z",
            "updatedAt": "2026-08-16T00:00:00Z",
            "transform": {"panX": 0, "panY": 0, "zoom": 1},
            "cards": [{"id": "c1", "text": "レビュー済みのカード", "x": 0, "y": 0, "textReviewed": True}],
            "edges": [],
            "islands": [{"id": "i1", "cardIds": ["c1"]}],
            "readingOrder": ["i1"],
        }
        _put_document(base_url, doc)
        check("PUT document (200)", 200, 200)

        # The `kj` CLI's full CE4 lifecycle: context-query -> context-bundle ->
        # proposal-diff -> apply. Each is an admin-scriptable op that POSTs to
        # /docs/{id}/context-audit with channel=cli. proposal/apply require a
        # sourceBundleHash; apply is forced dry-run by the CLI.
        eq = "a" * 64
        bh = "b" * 64
        src = "c" * 64
        operations = [
            ("context-query", "query", {"docId": DOC_ID, "equivalenceKey": eq, "bundleHash": bh, "queryCanonicalHash": eq}),
            ("context-bundle", "bundle", {"docId": DOC_ID, "equivalenceKey": eq, "bundleHash": bh, "queryCanonicalHash": eq}),
            ("proposal-diff", "proposal", {"docId": DOC_ID, "equivalenceKey": eq, "bundleHash": bh, "queryCanonicalHash": eq, "sourceBundleHash": src}),
            ("apply", "apply", {"docId": DOC_ID, "equivalenceKey": eq, "bundleHash": bh, "queryCanonicalHash": eq, "sourceBundleHash": src, "sideEffect": "none"}),
        ]
        for cli_cmd, _op, payload in operations:
            input_path = os.path.join(tmp, f"cli_{cli_cmd}.json")
            with open(input_path, "w", encoding="utf-8") as fh:
                json.dump(payload, fh)
            proc = subprocess.run(
                [VENV_PYTHON, "-m", "kj_atlas_api.cli", "--api-base-url", base_url,
                 cli_cmd, "--input", input_path],
                cwd=BACKEND_DIR,
                capture_output=True,
                text=True,
                timeout=60,
            )
            check(f"kj CLI {cli_cmd} exit", 0, proc.returncode)
            if proc.returncode != 0:
                print(proc.stdout[-2000:])
                print(proc.stderr[-2000:])

        time.sleep(1.0)
        events = sink.snapshot()
        cli_events = [
            e for e in events
            if e.get("docId") == DOC_ID
            and isinstance(e.get("metadata"), dict)
            and e["metadata"].get("channel") == "cli"
        ]
        check("audit sink received 4 channel=cli events", 4, len(cli_events))
        seen_ops = sorted(e["metadata"].get("operation") for e in cli_events)
        check("channel=cli operations = query/bundle/proposal/apply",
              ["apply", "bundle", "proposal", "query"], seen_ops)
        if cli_events:
            query_meta = next((e["metadata"] for e in cli_events if e["metadata"].get("operation") == "query"), None)
            check("metadata.command=context-query", "context-query", query_meta.get("command") if query_meta else None)
            check("metadata.equivalenceKey present (64hex)", 64, len(query_meta.get("equivalenceKey") or "") if query_meta else 0)
            check("metadata.bundleHash present (64hex)", 64, len(query_meta.get("bundleHash") or "") if query_meta else 0)

        print(f"=== Result: {PASS} passed, {FAIL} failed ===")
        return 0 if FAIL == 0 else 1
    finally:
        if backend_proc is not None:
            backend_proc.terminate()
            try:
                backend_proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                backend_proc.kill()
        sink.stop()
        shutil.rmtree(tmp, ignore_errors=True)


def _health(base_url: str) -> int:
    try:
        with urllib.request.urlopen(f"{base_url}/healthz", timeout=2) as resp:
            return resp.status
    except Exception:
        return 0


if __name__ == "__main__":
    sys.exit(main())
