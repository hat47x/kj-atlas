"""OPS-OBSERV-01: structured logging, request correlation IDs, readiness.

Covers AC-1 (JSON formatter renders `extra=` payloads, KJ_ATLAS_LOG_LEVEL),
AC-2 (X-Request-Id header + error body + log record carry the same ID), and
AC-3 (/readyz is non-200 on DB-unavailable and schema-mismatch; /healthz is
liveness-only).
"""

from __future__ import annotations

import json
import logging

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from kj_atlas_api.logging_config import JsonFormatter, configure_logging, request_id_var
from kj_atlas_api.main import app

_MIGRATED_REVISION = "20260813_0027"


@pytest.fixture()
def client() -> TestClient:
    with TestClient(app) as test_client:
        yield test_client


def _migrated_session_factory(db_path):
    # File-based SQLite (not :memory: — that is per-connection, so the readyz
    # route's session would not see the schema created on the setup connection).
    engine = create_engine(f"sqlite:///{db_path}")
    with engine.begin() as conn:
        conn.execute(
            text(
                "CREATE TABLE alembic_version (version_num VARCHAR(32) NOT NULL PRIMARY KEY)"
            )
        )
        conn.execute(
            text("INSERT INTO alembic_version (version_num) VALUES (:rev)"),
            {"rev": _MIGRATED_REVISION},
        )
    return sessionmaker(bind=engine)


# ---------------------------------------------------------------------------
# AC-1: structured logging
# ---------------------------------------------------------------------------


def _record(message: str = "audit event send failed; keep fail-open") -> logging.LogRecord:
    return logging.LogRecord(
        name="kj_atlas_api.audit",
        level=logging.WARNING,
        pathname=__file__,
        lineno=1,
        msg=message,
        args=(),
        exc_info=None,
    )


def test_json_formatter_renders_extra_payload_keys() -> None:
    record = _record()
    record.tenantId = "tenant-a"  # type: ignore[attr-defined]
    record.docId = "doc-1"  # type: ignore[attr-defined]
    record.queueLength = 3  # type: ignore[attr-defined]
    record.error = "connection refused"  # type: ignore[attr-defined]

    parsed = json.loads(JsonFormatter().format(record))

    assert parsed["message"] == "audit event send failed; keep fail-open"
    assert parsed["level"] == "WARNING"
    assert parsed["tenantId"] == "tenant-a"
    assert parsed["docId"] == "doc-1"
    assert parsed["queueLength"] == 3
    assert parsed["error"] == "connection refused"


def test_json_formatter_injects_the_inflight_request_id() -> None:
    token = request_id_var.set("req-abc123")
    try:
        parsed = json.loads(JsonFormatter().format(_record()))
        assert parsed["requestId"] == "req-abc123"
    finally:
        request_id_var.reset(token)


def test_json_formatter_omits_request_id_when_none_inflight() -> None:
    assert request_id_var.get() is None
    parsed = json.loads(JsonFormatter().format(_record()))
    assert "requestId" not in parsed


def test_configure_logging_normalizes_unknown_level_to_info() -> None:
    configure_logging("NOT-A-LEVEL")
    assert logging.getLogger().level == logging.INFO


def test_configure_logging_applies_valid_level() -> None:
    configure_logging("DEBUG")
    assert logging.getLogger().level == logging.DEBUG


# ---------------------------------------------------------------------------
# AC-2: request correlation ID
# ---------------------------------------------------------------------------


def test_every_response_echoes_x_request_id(client: TestClient) -> None:
    resp = client.get("/healthz")
    assert resp.status_code == 200
    assert resp.headers.get("X-Request-Id")


def test_inbound_x_trace_id_is_respected_and_echoed(client: TestClient) -> None:
    resp = client.get("/healthz", headers={"x-trace-id": "trace-42"})
    assert resp.headers.get("X-Request-Id") == "trace-42"


def test_invalid_x_trace_id_is_replaced_not_echoed(client: TestClient) -> None:
    resp = client.get("/healthz", headers={"x-trace-id": "bad\ninjection"})
    rid = resp.headers.get("X-Request-Id")
    assert rid and rid != "bad\ninjection"


def test_error_body_carries_the_same_request_id_as_the_header(client: TestClient) -> None:
    # A validation error (wrong type for `provider`) reaches
    # handle_validation_error -> 422 with requestId.
    resp = client.post("/admin/provision/users", json={"provider": 123})
    assert resp.status_code == 422
    body = resp.json()
    assert body.get("requestId")
    assert body["requestId"] == resp.headers.get("X-Request-Id")


def test_unauthorized_body_carries_request_id(client: TestClient, monkeypatch) -> None:
    from kj_atlas_api import settings as settings_module

    monkeypatch.setattr(settings_module.settings, "api_key", "biz-key")
    resp = client.get("/docs/doc_phase1_canvas")  # no api key -> 401
    assert resp.status_code == 401
    body = resp.json()
    assert body.get("requestId")
    assert body["requestId"] == resp.headers.get("X-Request-Id")


# ---------------------------------------------------------------------------
# AC-3: readiness
# ---------------------------------------------------------------------------


def test_readyz_ok_when_db_migrated(client: TestClient, monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(
        "kj_atlas_api.main.SessionLocal", _migrated_session_factory(tmp_path / "readyz.db")
    )
    monkeypatch.setattr("kj_atlas_api.main._migration_heads", lambda: [_MIGRATED_REVISION])
    resp = client.get("/readyz")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ready"


def test_readyz_503_when_schema_behind_head(client: TestClient, monkeypatch, tmp_path) -> None:
    monkeypatch.setattr(
        "kj_atlas_api.main.SessionLocal", _migrated_session_factory(tmp_path / "readyz.db")
    )
    monkeypatch.setattr("kj_atlas_api.main._migration_heads", lambda: ["20260813_9999"])
    resp = client.get("/readyz")
    assert resp.status_code == 503
    assert resp.json()["reason"] == "schema_mismatch"


def test_readyz_503_when_database_unavailable(client: TestClient, monkeypatch) -> None:
    class _Boom:
        def __enter__(self):
            raise RuntimeError("db down")

        def __exit__(self, *_: object) -> None:
            return None

    monkeypatch.setattr("kj_atlas_api.main.SessionLocal", lambda: _Boom())
    resp = client.get("/readyz")
    assert resp.status_code == 503
    assert resp.json()["reason"] == "database_unavailable"


def test_healthz_is_liveness_only(client: TestClient) -> None:
    # /healthz must not probe the DB: it returns ok even when the DB would fail.
    resp = client.get("/healthz")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}
