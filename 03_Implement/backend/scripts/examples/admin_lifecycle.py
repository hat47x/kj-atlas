#!/usr/bin/env python3
"""Admin self-written lifecycle script (dogfooding iteration 131).

A realistic example of the "administrator writes their own script to use the
CLI/API" path: drives the document lifecycle and the control-plane audit over
the HTTP API, respecting the two-key separation, and asserts its own
expectations. Any deviation exits non-zero so it is safe to call from the E2E
harness (verify_admin_ops_flow_e2e.sh) as a freeze of this non-Web path.

Dependencies: Python 3 stdlib only (urllib). No venv, no pip -- an admin can
run it on any box that can reach the backend.

Usage:
    KJ_ATLAS_API_BASE_URL=http://127.0.0.1:8000 \
    KJ_ATLAS_API_KEY=biz-key \
    KJ_ATLAS_ADMIN_API_KEY=adm-key \
    python3 admin_lifecycle.py [doc_id]

Env:
    KJ_ATLAS_API_BASE_URL   Backend base URL (default http://127.0.0.1:8000).
    KJ_ATLAS_API_KEY        Business-plane key (X-API-Key) for /docs.
    KJ_ATLAS_ADMIN_API_KEY  Control-plane key (X-Admin-Api-Key) for /admin/*.
    The two keys must differ; a deployment that leaves the admin key unset
    fails closed here (the script refuses to run) rather than guessing.
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request

BASE_URL = (os.environ.get("KJ_ATLAS_API_BASE_URL") or "http://127.0.0.1:8000").rstrip("/")
BIZ_KEY = os.environ.get("KJ_ATLAS_API_KEY") or ""
ADM_KEY = os.environ.get("KJ_ATLAS_ADMIN_API_KEY") or ""
DOC_ID = sys.argv[1] if len(sys.argv) > 1 else "admin-self-script-doc"

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


def request(method: str, path: str, key: str, body: dict | None = None, *, expect_status: int):
    """Perform one HTTP call and return the status code (and parse JSON if any)."""
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(f"{BASE_URL}{path}", data=data, method=method)
    req.add_header("Content-Type", "application/json")
    req.add_header(key_header(key), key)
    try:
        with urllib.request.urlopen(req) as resp:
            raw = resp.read().decode("utf-8")
            parsed = json.loads(raw) if raw else None
            check(f"{method} {path} -> {expect_status}", expect_status, resp.status)
            return resp.status, parsed
    except urllib.error.HTTPError as exc:
        check(f"{method} {path} -> {expect_status}", expect_status, exc.code)
        return exc.code, None


def key_header(key: str) -> str:
    return "X-API-Key" if key == BIZ_KEY else "X-Admin-Api-Key"


def main() -> int:
    if not BIZ_KEY or not ADM_KEY or BIZ_KEY == ADM_KEY:
        print("admin_lifecycle.py: requires distinct KJ_ATLAS_API_KEY and KJ_ATLAS_ADMIN_API_KEY")
        return 2

    print("=== admin self-script: document lifecycle + control-plane audit ===")
    print(f"  base: {BASE_URL}  doc: {DOC_ID}")

    doc = {
        "version": 1,
        "id": DOC_ID,
        "title": "運用マニュアル",
        "createdAt": "2026-08-16T00:00:00Z",
        "updatedAt": "2026-08-16T00:00:00Z",
        "transform": {"panX": 0, "panY": 0, "zoom": 1},
        "cards": [{"id": "c1", "text": "バックアップ手順", "x": 0, "y": 0, "textReviewed": True}],
        "edges": [],
        "islands": [{"id": "i1", "cardIds": ["c1"]}],
        "readingOrder": ["i1"],
    }

    # 1. Business-plane lifecycle (X-API-Key).
    request("GET", "/docs", BIZ_KEY, expect_status=200)
    request("PUT", f"/docs/{DOC_ID}", BIZ_KEY, doc, expect_status=200)
    request("POST", f"/docs/{DOC_ID}/archive", BIZ_KEY, {}, expect_status=204)
    # Archive makes the document read-only (ADR-0073 D2=A): a write is 423.
    request("PUT", f"/docs/{DOC_ID}", BIZ_KEY, doc, expect_status=423)
    request("POST", f"/docs/{DOC_ID}/unarchive", BIZ_KEY, {}, expect_status=204)
    request("PUT", f"/docs/{DOC_ID}", BIZ_KEY, doc, expect_status=200)

    # 2. Control-plane audit (X-Admin-Api-Key).
    request("GET", "/admin/provision/audit", ADM_KEY, expect_status=200)

    # 3. Key separation (SEC-ADMIN-PLANE-02): each key only reaches its own plane.
    request("GET", "/admin/provision/audit", BIZ_KEY, expect_status=401)
    request("GET", "/docs", ADM_KEY, expect_status=401)
    request("GET", "/admin/provision/audit", "wrong-key", expect_status=401)

    print(f"=== admin self-script result: {PASS} passed, {FAIL} failed ===")
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
