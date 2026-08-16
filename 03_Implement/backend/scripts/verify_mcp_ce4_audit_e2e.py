#!/usr/bin/env python3
"""Dogfood E2E: MCP read is audited through the backend's CE-4 audit trail.

Proves the "generative-AI verifies via MCP" path end-to-end: an MCP-originated
read of a document is reported to the backend's POST /docs/{id}/context-audit
with channel="mcp", and that event reaches the configured HTTP audit sink.

Chain exercised (self-contained, deterministic, no billing):
  audit sink (this script) <- POST <- backend (uvicorn, audit transport=http)
      <- POST /docs/{id}/context-audit (channel=mcp, operation=query)
          <- MCP server (03_Implement/mcp, get_context_projection)
              <- verify_mcp.ts (the generative-AI MCP client path)

Usage:
  .venv/bin/python scripts/verify_mcp_ce4_audit_e2e.py [PORT]

Requires the backend venv (uvicorn/alembic) and the mcp package's node_modules
(npm install already run). Uses free ports for the backend and audit sink.
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
MCP_DIR = os.path.join(ROOT_DIR, "03_Implement", "mcp")
VENV_PYTHON = os.path.join(BACKEND_DIR, ".venv", "bin", "python")
BIZ_KEY = "biz-test-key-mcp-audit"
DOC_ID = "mcp-audit-doc"

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
                    pass  # not a JSON audit event; ignore
                self.send_response(200)
                self.send_header("Content-Length", "0")
                self.end_headers()

            def log_message(self, *_args) -> None:  # keep the console quiet
                return

        # closure bucket + lock shared with the handler above
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
        headers={"Content-Type": "application/json", "X-API-Key": BIZ_KEY},
    )
    with urllib.request.urlopen(req) as resp:
        if resp.status != 200:
            raise RuntimeError(f"PUT document failed: HTTP {resp.status}")


def main() -> int:
    if not os.path.isdir(MCP_DIR) or not os.path.exists(os.path.join(MCP_DIR, "node_modules", ".bin", "tsx")):
        print("verify_mcp_ce4_audit_e2e.py: mcp package deps not installed (cd 03_Implement/mcp && npm install)")
        return 2

    sink_port = free_port()
    backend_port = free_port()
    base_url = f"http://127.0.0.1:{backend_port}"
    sink = AuditSink(sink_port)
    sink.start()

    tmp = tempfile.mkdtemp(prefix="kj_mcp_audit_")
    db_path = os.path.join(tmp, "mcp_audit.sqlite3")
    backend_proc: subprocess.Popen | None = None
    try:
        print("=== MCP read -> CE-4 audit (channel=mcp) -> HTTP sink e2e ===")
        _migrate(db_path)

        backend_env = dict(
            os.environ,
            KJ_ATLAS_DATABASE_URL=f"sqlite:///{db_path}",
            KJ_ATLAS_API_KEY=BIZ_KEY,
            KJ_ATLAS_ADMIN_API_KEY="adm-test-key-mcp-audit",
            KJ_ATLAS_AUDIT_EXPORT_ENABLED="1",
            KJ_ATLAS_AUDIT_TRANSPORT="http",
            KJ_ATLAS_AUDIT_HTTP_ENDPOINT=f"http://127.0.0.1:{sink_port}/audit",
            # MCP reads are safeMode=true by default; the audit dispatcher drops
            # safe-mode events unless this is set, so the audit-chain E2E enables
            # it to prove the channel=mcp event is actually delivered.
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
            "title": "MCP audit e2e",
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

        # 4. Run the generative-AI MCP client path (verify_mcp.ts) against this
        #    backend. It calls get_context_projection -> triggers the CE-4 emit.
        mcp_env = dict(
            os.environ,
            KJ_ATLAS_MCP_API_BASE_URL=base_url,
            KJ_ATLAS_API_KEY=BIZ_KEY,
        )
        proc = subprocess.run(
            ["npm", "run", "verify", "--", DOC_ID, "reviewed-only"],
            cwd=MCP_DIR,
            env=mcp_env,
            capture_output=True,
            text=True,
            timeout=180,
        )
        check("MCP client (verify_mcp.ts) exit", 0, proc.returncode)
        if proc.returncode != 0:
            print(proc.stdout[-2000:])
            print(proc.stderr[-2000:])

        # 5. Give the async audit queue a moment, then assert the sink saw the
        #    channel=mcp context-audit event for this document.
        time.sleep(1.0)
        events = sink.snapshot()
        mcp_events = [
            e for e in events
            if e.get("eventType") == "query"
            and e.get("docId") == DOC_ID
            and isinstance(e.get("metadata"), dict)
            and e["metadata"].get("channel") == "mcp"
        ]
        check("audit sink received channel=mcp event", 1, len(mcp_events))
        if mcp_events:
            meta = mcp_events[0]["metadata"]
            check("metadata.operation=query", "query", meta.get("operation"))
            check("metadata.command=context-query", "context-query", meta.get("command"))
            check("metadata.equivalenceKey present (64hex)", 64, len(meta.get("equivalenceKey") or ""))
            check("metadata.bundleHash present (64hex)", 64, len(meta.get("bundleHash") or ""))

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
