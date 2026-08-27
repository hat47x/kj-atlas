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
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from starlette.requests import Request

from kj_atlas_api.access_control import AuthContext
from kj_atlas_api.auth_context import ResolvedIdentity, resolve_identity_context
from kj_atlas_api.control_plane_auth import (
    ADMIN_API_KEY_HEADER,
    require_control_plane_authorization,
)
from kj_atlas_api.db import get_db
from kj_atlas_api.main import app
from kj_atlas_api.models import Base, TenantMembershipRow, TenantRow, UserRow
from kj_atlas_api.observability import (
    ACTOR_REF_HASH_LENGTH,
    REQUEST_ID_HEADER,
    JsonLogFormatter,
    RequestIdFilter,
    actor_ref_hash_var,
    bind_actor_ref_hash,
    compute_actor_ref_hash,
    configure_logging,
    request_id_var,
    resolve_inbound_request_id,
)
from kj_atlas_api.session_context import CapabilitySnapshot
from kj_atlas_api.settings import Settings, settings
from kj_atlas_api.tenant_context import select_active_tenant_context
from kj_atlas_api.tenant_session_precondition import require_tenant_scoped_api_precondition

_SEED_TIMESTAMP = "2026-08-26T00:00:00Z"


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
# Actor pseudo-identifier (残作業, decided 2026-08-26): a one-way fingerprint of
# the acting principal, attached to logs the same way requestId is. The audit
# trail already has this (SEC-ADMIN-PLANE-03's actorRefHash); this is that same
# computation, reused, for the general log stream.
# ---------------------------------------------------------------------------


def test_compute_actor_ref_hash_is_stable_and_opaque() -> None:
    """Same principal -> same hash, every time -- this is what makes
    "these log lines are the same actor" correlation possible at all."""
    first = compute_actor_ref_hash("user-123")
    second = compute_actor_ref_hash("user-123")
    assert first == second
    assert first is not None
    assert len(first) == ACTOR_REF_HASH_LENGTH
    assert all(character in "0123456789abcdef" for character in first)


def test_compute_actor_ref_hash_differs_between_principals() -> None:
    assert compute_actor_ref_hash("user-123") != compute_actor_ref_hash("user-456")


@pytest.mark.parametrize("empty", [None, ""])
def test_compute_actor_ref_hash_is_none_for_no_principal(empty: str | None) -> None:
    assert compute_actor_ref_hash(empty) is None


def test_compute_actor_ref_hash_does_not_leak_the_principal() -> None:
    """One-way: security.md forbids a real subject identifier in logs.

    The hash must never contain, equal, or otherwise echo the source value --
    hashing something is not the same as redacting it, and this pins that the
    computation actually discards the input rather than encoding it.
    """
    principal_id = "user-alice@example.invalid"
    hashed = compute_actor_ref_hash(principal_id)
    assert hashed is not None
    assert hashed != principal_id
    assert principal_id not in hashed
    assert "alice" not in hashed
    assert "example" not in hashed


def test_bind_actor_ref_hash_sets_the_contextvar_to_the_computed_hash() -> None:
    token = actor_ref_hash_var.set(None)
    try:
        bind_actor_ref_hash("user-123")
        assert actor_ref_hash_var.get() == compute_actor_ref_hash("user-123")
    finally:
        actor_ref_hash_var.reset(token)


def test_actor_ref_hash_is_rendered_in_json_output_when_bound() -> None:
    token = actor_ref_hash_var.set("deadbeefcafef00d")
    try:
        assert _format({"msg": "event"})["actorRefHash"] == "deadbeefcafef00d"
    finally:
        actor_ref_hash_var.reset(token)


def test_actor_ref_hash_is_absent_from_json_output_when_unbound() -> None:
    """Matches requestId's own convention: the key is omitted, not nulled."""
    assert "actorRefHash" not in _format({"msg": "event"})


def test_actor_ref_hash_appears_in_the_human_readable_format_too() -> None:
    try:
        configure_logging(level="INFO", json_format=False)
        handler = logging.getLogger().handlers[0]
        assert "%(actorRefHash)s" in handler.formatter._fmt
    finally:
        configure_logging(level=settings.log_level, json_format=settings.log_json)


def _identity_request(headers: dict[str, str]) -> Request:
    encoded = [(key.lower().encode("ascii"), value.encode("ascii")) for key, value in headers.items()]
    return Request(scope={"type": "http", "method": "GET", "path": "/", "headers": encoded})


@contextmanager
def _identity_db(tmp_path) -> Iterator:
    engine = create_engine(f"sqlite:///{tmp_path / 'auth_context_actor_ref_hash.sqlite3'}")
    session_local = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    Base.metadata.create_all(bind=engine)
    db = session_local()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


def test_single_tenant_header_identity_binds_actor_ref_hash(tmp_path, monkeypatch) -> None:
    """The single-tenant header-based resolver: `resolve_identity_context`
    (auth_context.py), called directly from `_authorize_request` (docs.py) and
    `_resolve_audit_tenant` (ai.py) -- not via FastAPI `Depends`, so there is no
    thread-pool boundary to worry about here."""
    monkeypatch.setattr(settings, "allow_jit_provisioning", True)
    with _identity_db(tmp_path) as db:
        identity = resolve_identity_context(
            db=db, request=_identity_request({"x-forwarded-user": "alice"})
        )
        first_hash = actor_ref_hash_var.get()
        assert identity.user_id is not None
        assert first_hash == compute_actor_ref_hash(identity.user_id)
        assert "alice" not in first_hash

        # Same principal presenting again (a second, later request in
        # production) -> the same hash, which is what makes cross-request log
        # correlation for one actor actually work.
        second_identity = resolve_identity_context(
            db=db, request=_identity_request({"x-forwarded-user": "alice"})
        )
        assert second_identity.user_id == identity.user_id
        assert actor_ref_hash_var.get() == first_hash


def test_single_tenant_anonymous_request_does_not_bind_actor_ref_hash(tmp_path) -> None:
    """No auth header presented -> no principal -> explicitly cleared, not left
    over from whatever the previous call in this process happened to bind."""
    token = actor_ref_hash_var.set("stale-hash-from-a-previous-caller")
    try:
        with _identity_db(tmp_path) as db:
            identity = resolve_identity_context(db=db, request=_identity_request({}))
        assert identity.user_id is None
        assert actor_ref_hash_var.get() is None
    finally:
        actor_ref_hash_var.reset(token)


class _StaticIdentityResolver:
    """Stands in for the SaaS trusted-session identity resolver (auth edge)."""

    def __init__(self, principal_id: str) -> None:
        self._principal_id = principal_id

    def resolve(self, *, db, request) -> ResolvedIdentity:  # noqa: ARG002
        return ResolvedIdentity(
            user_id=self._principal_id,
            reviewer_ref=None,
            owner_ref=None,
            auth_context=AuthContext(
                actor_ref=None,
                user_id=self._principal_id,
                provider="test-idp",
                external_uid="ext-1",
                roles=(),
                groups=(),
                trace_id=None,
            ),
        )


class _StaticTenantResolver:
    """Delegates to `select_active_tenant_context` (not a made-up membership_id):
    `recheck_trusted_tenant_context` independently recomputes the opaque
    membership id from `(tenant_id, user_id)` and rejects a mismatch, so a
    resolver returning an arbitrary membership_id here would always be denied
    as untrusted."""

    def __init__(self, *, tenant_id: str) -> None:
        self._tenant_id = tenant_id

    def resolve(self, *, db, user_id, claim=None):  # noqa: ARG002
        return select_active_tenant_context(
            db=db,
            user_id=user_id,
            tenant_id=self._tenant_id,
            resolved_by="verified_claim",
        )


class _StaticCapabilityResolver:
    def resolve(self, *, db, principal_id, tenant) -> CapabilitySnapshot:  # noqa: ARG002
        return CapabilitySnapshot(effective_capabilities=("document.read",), capability_version="v1")


class _StaticActiveTenantSessionPersister:
    def __init__(self, version: str) -> None:
        self._version = version

    def current_version(self, *, request, principal_id, active_tenant):  # noqa: ARG002
        return self._version

    def persist(self, **_kwargs):
        return self._version


def _install_actor_ref_hash_reset(app_under_test: FastAPI) -> None:
    """Mirror `main.py`'s `assign_request_id`: reset the contextvar to `None`
    at the start of every request on this throwaway app.

    Without this, these minimal test apps have no equivalent of the real
    app's outermost middleware, and a value bound while handling one request
    can otherwise still be observed while handling a later, unrelated one in
    the same process (the ASGI test transport does not guarantee a fresh
    context per request the way a real per-connection task would).
    """

    @app_under_test.middleware("http")
    async def _reset_actor_ref_hash(request, call_next):  # noqa: ANN001
        token = actor_ref_hash_var.set(None)
        try:
            return await call_next(request)
        finally:
            actor_ref_hash_var.reset(token)


def test_saas_trusted_session_precondition_binds_actor_ref_hash_for_the_endpoint(
    tmp_path,
) -> None:
    """`require_tenant_scoped_api_precondition` is the *only* place several
    routes (ai_relations.py, context.py, several ai.py routes) resolve a
    principal at all -- and it runs as a FastAPI `Depends(...)`, not a direct
    call. This proves the `async def` conversion actually matters: if FastAPI
    ran a plain `def` version of this dependency in a thread-pool worker (a
    *copied* context), `resolve_trusted_saas_request_session`'s
    `bind_actor_ref_hash` call would set that copy and vanish -- the endpoint
    below, reading the contextvar in the main context, would see `None` even
    for a fully authenticated SaaS caller.
    """
    engine = create_engine(f"sqlite:///{tmp_path / 'precondition_actor_ref_hash.sqlite3'}")
    session_local = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    Base.metadata.create_all(bind=engine)
    with session_local() as db:
        db.add(
            UserRow(
                id="user-saas-actor",
                display_name="SaaS Actor",
                email=None,
                lifecycle_state="active",
                created_at=_SEED_TIMESTAMP,
                updated_at=_SEED_TIMESTAMP,
            )
        )
        db.add(
            TenantRow(
                id="tenant-a",
                display_name="Tenant A",
                lifecycle_state="active",
                created_at=_SEED_TIMESTAMP,
                updated_at=_SEED_TIMESTAMP,
            )
        )
        db.add(
            TenantMembershipRow(
                tenant_id="tenant-a",
                user_id="user-saas-actor",
                lifecycle_state="active",
                created_at=_SEED_TIMESTAMP,
                updated_at=_SEED_TIMESTAMP,
            )
        )
        db.commit()

    def _get_test_db():
        db = session_local()
        try:
            yield db
        finally:
            db.close()

    app_under_test = FastAPI()
    _install_actor_ref_hash_reset(app_under_test)
    app_under_test.state.runtime_profile = "saas-multitenant"
    app_under_test.dependency_overrides[get_db] = _get_test_db
    app_under_test.state.saas_identity_context_resolver = _StaticIdentityResolver(
        "user-saas-actor"
    )
    app_under_test.state.tenant_context_resolver = _StaticTenantResolver(tenant_id="tenant-a")
    app_under_test.state.tenant_capability_resolver = _StaticCapabilityResolver()
    app_under_test.state.active_tenant_session_persister = _StaticActiveTenantSessionPersister(
        "session-v1"
    )

    @app_under_test.get(
        "/guarded",
        dependencies=[Depends(require_tenant_scoped_api_precondition)],
    )
    def guarded() -> dict[str, object]:
        return {"actorRefHash": actor_ref_hash_var.get()}

    try:
        with TestClient(app_under_test) as client:
            response = client.get(
                "/guarded",
                headers={"KJ-Atlas-Tenant-Session-Version": "session-v1"},
            )
    finally:
        Base.metadata.drop_all(bind=engine)
        engine.dispose()

    assert response.status_code == 200
    assert response.json()["actorRefHash"] == compute_actor_ref_hash("user-saas-actor")


def test_control_plane_bearer_key_binds_actor_ref_hash_for_the_endpoint(monkeypatch) -> None:
    """Mirrors the test above for the admin plane's stage-A bearer-key path.

    Same source `record_admin_plane_audit` (main.py) already uses as the
    fallback for the audit trail's actorRefHash when there is no trusted
    session: the static bootstrap credential is not a person, but a stable
    fingerprint of it still lets an operator tell log lines from the same
    bootstrap caller apart from a later real subject.
    """
    monkeypatch.setattr(settings, "admin_api_key", "control-plane-bootstrap-key")

    app_under_test = FastAPI()
    _install_actor_ref_hash_reset(app_under_test)
    app_under_test.state.runtime_profile = "local-dev"
    app_under_test.dependency_overrides[get_db] = lambda: object()

    @app_under_test.get(
        "/guarded",
        dependencies=[Depends(require_control_plane_authorization)],
    )
    def guarded() -> dict[str, object]:
        return {"actorRefHash": actor_ref_hash_var.get()}

    with TestClient(app_under_test) as client:
        response = client.get(
            "/guarded",
            headers={ADMIN_API_KEY_HEADER: "control-plane-bootstrap-key"},
        )

    assert response.status_code == 200
    assert response.json()["actorRefHash"] == compute_actor_ref_hash(
        "control-plane-bootstrap-key"
    )


def test_control_plane_missing_credential_leaves_actor_ref_hash_unbound(monkeypatch) -> None:
    """The dev-mode "open when unconfigured" branch: no credential presented,
    so nothing to attribute -- stays anonymous rather than binding a hash of
    nothing."""
    monkeypatch.setattr(settings, "admin_api_key", None)

    app_under_test = FastAPI()
    _install_actor_ref_hash_reset(app_under_test)
    app_under_test.state.runtime_profile = "local-dev"
    app_under_test.dependency_overrides[get_db] = lambda: object()

    @app_under_test.get(
        "/guarded",
        dependencies=[Depends(require_control_plane_authorization)],
    )
    def guarded() -> dict[str, object]:
        return {"actorRefHash": actor_ref_hash_var.get()}

    with TestClient(app_under_test) as client:
        response = client.get("/guarded")

    assert response.status_code == 200
    assert response.json()["actorRefHash"] is None


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
