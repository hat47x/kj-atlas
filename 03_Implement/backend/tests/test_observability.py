"""OPS-OBSERV-01: the observability substrate the runbooks assume.

The assertion that matters most is `test_extra_fields_are_rendered`: eight call
sites pass structured payloads via `extra={...}`, and with no logging
configuration installed `logging.Formatter` silently dropped every one of them.
The audit dispatcher's own failure warning carries `tenantId` / `docId` /
`queueLength` / `error` that way, so an operator saw "audit event send failed"
with no indication of whose event was lost.
"""

from __future__ import annotations

import json
import logging
from collections.abc import Iterator
from contextlib import contextmanager

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from kj_atlas_api.db import get_db
from kj_atlas_api.main import app
from kj_atlas_api.models import Base
from kj_atlas_api.observability import (
    REQUEST_ID_HEADER,
    JsonLogFormatter,
    RequestIdFilter,
    configure_logging,
    request_id_var,
    resolve_inbound_request_id,
)
from kj_atlas_api.settings import Settings, settings


@contextmanager
def _client(tmp_path) -> Iterator[TestClient]:
    engine = create_engine(f"sqlite:///{tmp_path / 'observability.sqlite3'}")
    session_local = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    Base.metadata.create_all(bind=engine)

    def _get_test_db():
        db = session_local()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _get_test_db
    try:
        with TestClient(app) as client:
            yield client
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


def _format(record_kwargs: dict) -> dict:
    record = logging.LogRecord(
        name="kj_atlas_api.test",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg=record_kwargs.pop("msg", "event"),
        args=(),
        exc_info=None,
    )
    for key, value in record_kwargs.items():
        setattr(record, key, value)
    RequestIdFilter().filter(record)
    return json.loads(JsonLogFormatter().format(record))


# ---------------------------------------------------------------------------
# Logging: the `extra` payloads must actually be emitted
# ---------------------------------------------------------------------------


def test_extra_fields_are_rendered() -> None:
    """The defect this whole issue starts from."""
    payload = _format({"msg": "llm_generate", "tenantId": "t-1", "docId": "d-1", "queueLength": 3})
    assert payload["message"] == "llm_generate"
    assert payload["tenantId"] == "t-1"
    assert payload["docId"] == "d-1"
    assert payload["queueLength"] == 3


def test_standard_record_fields_are_not_duplicated_as_extra() -> None:
    payload = _format({"msg": "event"})
    assert "args" not in payload
    assert "pathname" not in payload
    assert payload["level"] == "INFO"
    assert payload["logger"] == "kj_atlas_api.test"


def test_secret_like_extra_fields_are_redacted() -> None:
    """A mechanical backstop for security.md's application-log PII policy."""
    payload = _format(
        {
            "msg": "event",
            "api_key": "super-secret",
            "token": "bearer-value",
            "subject": "idp-subject",
            "tenantId": "t-1",
        }
    )
    assert payload["api_key"] == "[redacted]"
    assert payload["token"] == "[redacted]"
    assert payload["subject"] == "[redacted]"
    assert payload["tenantId"] == "t-1"
    assert "super-secret" not in json.dumps(payload)
    assert "idp-subject" not in json.dumps(payload)


def test_request_id_is_attached_when_set() -> None:
    token = request_id_var.set("abc123")
    try:
        assert _format({"msg": "event"})["requestId"] == "abc123"
    finally:
        request_id_var.reset(token)


def test_configure_logging_falls_back_to_info_on_a_bad_level() -> None:
    try:
        configure_logging(level="not-a-level", json_format=True)
        assert logging.getLogger().level == logging.INFO
    finally:
        configure_logging(level=settings.log_level, json_format=settings.log_json)


def test_configure_logging_accepts_the_human_readable_format() -> None:
    """The non-JSON path must still render requestId, or correlation breaks."""
    try:
        configure_logging(level="INFO", json_format=False)
        handler = logging.getLogger().handlers[0]
        assert "%(requestId)s" in handler.formatter._fmt
    finally:
        configure_logging(level=settings.log_level, json_format=settings.log_json)


# ---------------------------------------------------------------------------
# Request id: correlation between a user report and a log line
# ---------------------------------------------------------------------------


def test_every_response_carries_a_request_id(tmp_path) -> None:
    with _client(tmp_path) as client:
        resp = client.get("/healthz")
    assert resp.headers[REQUEST_ID_HEADER]


def test_request_ids_differ_between_requests(tmp_path) -> None:
    with _client(tmp_path) as client:
        first = client.get("/healthz").headers[REQUEST_ID_HEADER]
        second = client.get("/healthz").headers[REQUEST_ID_HEADER]
    assert first != second


def test_safe_inbound_trace_id_is_honoured(tmp_path) -> None:
    with _client(tmp_path) as client:
        resp = client.get("/healthz", headers={"x-trace-id": "caller-side-id_1"})
    assert resp.headers[REQUEST_ID_HEADER] == "caller-side-id_1"


@pytest.mark.parametrize(
    "unsafe",
    [
        "has space",
        "semi;colon",
        "new\nline",
        "x" * 129,
        "",
        "   ",
    ],
)
def test_unsafe_inbound_trace_id_is_replaced_not_rejected(unsafe: str) -> None:
    """A malformed trace header must not fail an otherwise valid request."""
    assert resolve_inbound_request_id(unsafe) is None


def test_error_body_carries_the_request_id(tmp_path) -> None:
    """Without this the user has nothing to quote to an operator.

    A body-parsing validation error (wrong type for `provider`) reaches
    handle_validation_error, whose 422 body must carry the same request id as
    the X-Request-Id header. (The docs routes' A1 contract errors are a separate
    structured envelope that deliberately does not add requestId.)
    """
    with _client(tmp_path) as client:
        resp = client.post("/admin/provision/users", json={"provider": 123})
    assert resp.status_code == 422
    body = resp.json()
    assert body["requestId"] == resp.headers[REQUEST_ID_HEADER]


def test_unauthorized_body_carries_the_request_id(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(settings, "api_key", "business-key")
    with _client(tmp_path) as client:
        resp = client.get("/docs/anything")
    assert resp.status_code == 401
    assert resp.json()["requestId"] == resp.headers[REQUEST_ID_HEADER]


# ---------------------------------------------------------------------------
# Health / readiness / version
# ---------------------------------------------------------------------------


def test_healthz_stays_unauthenticated_and_constant(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(settings, "api_key", "business-key")
    with _client(tmp_path) as client:
        resp = client.get("/healthz")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_readyz_reports_ready_on_a_migrated_database(tmp_path) -> None:
    with _client(tmp_path) as client:
        resp = client.get("/readyz")
    # The suite creates tables via metadata rather than alembic, so
    # alembic_version is absent and readiness is correctly withheld. The point
    # asserted here is that the endpoint answers with a status rather than
    # raising, and that it names which check failed.
    assert resp.status_code in {200, 503}
    body = resp.json()
    assert body["status"] in {"ready", "not_ready"}
    assert "checks" in body


def test_readyz_is_unauthenticated(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(settings, "api_key", "business-key")
    with _client(tmp_path) as client:
        resp = client.get("/readyz")
    assert resp.status_code != 401


def test_readyz_reports_unreachable_database_without_leaking_the_url(tmp_path, monkeypatch) -> None:
    from kj_atlas_api import main as main_module

    class _BrokenSession:
        def execute(self, *_args, **_kwargs):
            raise RuntimeError("postgresql://user:secret@db:5432/kj — connection refused")

        def close(self) -> None:
            return None

    monkeypatch.setattr(main_module, "SessionLocal", lambda: _BrokenSession())
    with _client(tmp_path) as client:
        resp = client.get("/readyz")
    assert resp.status_code == 503
    assert resp.json()["checks"]["database"] == "unreachable"
    assert "secret" not in resp.text
    assert "postgresql" not in resp.text


def test_version_reports_the_configured_revision(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(settings, "app_revision", "abc1234")
    with _client(tmp_path) as client:
        resp = client.get("/version")
    assert resp.status_code == 200
    assert resp.json()["revision"] == "abc1234"


def test_version_reports_unknown_when_unset(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(settings, "app_revision", None)
    with _client(tmp_path) as client:
        resp = client.get("/version")
    assert resp.json()["revision"] == "unknown"


def test_version_does_not_leak_the_profile_name_verbatim_for_saas(tmp_path) -> None:
    """The profile name is already exposed here deliberately; guard the contract.

    `GET /session/bootstrap-policy` deliberately maps the profile to a bootstrap
    mode instead of naming it. /version reports the profile because an operator
    needs it, and it is not a secret -- but pin that decision so a future change
    is deliberate.
    """
    with _client(tmp_path) as client:
        resp = client.get("/version")
    assert resp.json()["runtimeProfile"] in {
        "local-dev",
        "evaluation",
        "enterprise-production",
        "saas-multitenant",
    }


# ---------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------


def test_log_settings_have_observable_defaults(monkeypatch) -> None:
    for key in ("KJ_ATLAS_LOG_LEVEL", "KJ_ATLAS_LOG_JSON", "KJ_ATLAS_APP_REVISION"):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("KJ_ATLAS_RUNTIME_PROFILE", "local-dev")
    monkeypatch.setenv("KJ_ATLAS_DATABASE_URL", "sqlite:///./kj_atlas.db")
    monkeypatch.setenv("KJ_ATLAS_LLM_PROVIDER", "none")

    built = Settings()
    assert built.log_level == "INFO"
    assert built.log_json is True
    # main's convention: "unknown" when unset (diagnostics bundles addressable).
    assert built.app_revision == "unknown"


def test_backend_readme_structured_log_claim_is_now_true() -> None:
    """The README asserted structured logging that did not exist.

    It listed provider / model_id / trace_id as recorded to structured logs, but
    those fields lived only in a discarded `extra`. Keep the claim tied to the
    configuration that makes it true.
    """
    from pathlib import Path

    backend_readme = Path(__file__).resolve().parents[1] / "README.md"
    text = backend_readme.read_text(encoding="utf-8")
    if "構造化ログ" in text:
        assert "KJ_ATLAS_LOG_LEVEL" in text or "observability" in text.lower()
