from __future__ import annotations

import pytest
from fastapi import HTTPException
from starlette.requests import Request
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from kj_atlas_api.auth_context import (
    _check_trusted_proxy,
    _header,
    _normalize_provider,
    resolve_identity_context,
)
from kj_atlas_api.models import Base, UserIdentityRow, UserRow
from kj_atlas_api.settings import settings


def _request(headers: dict[str, str], *, client_host: str | None = None) -> Request:
    scope = {
        "type": "http",
        "method": "GET",
        "path": "/",
        "headers": [(k.lower().encode("latin-1"), v.encode("latin-1")) for k, v in headers.items()],
    }
    if client_host is not None:
        scope["client"] = (client_host, 0)
    return Request(scope)


def _db_session(*, allow_legacy_ambiguous_identities: bool = False) -> Session:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    if allow_legacy_ambiguous_identities:
        with engine.begin() as connection:
            connection.execute(text("DROP INDEX uq_user_identities_provider_lower_external_uid"))
    return Session(engine)


def test_header_trims_and_empty_to_none() -> None:
    request = _request({"x-actor-ref": "  actor:demo  ", "x-empty": "   "})

    assert _header(request, "x-actor-ref") == "actor:demo"
    assert _header(request, "x-empty") is None
    assert _header(request, "x-missing") is None


def test_normalize_provider_defaults_to_header_and_lowercases() -> None:
    assert _normalize_provider(None) == "header"
    assert _normalize_provider("   ") == "header"
    assert _normalize_provider(" OIDC ") == "oidc"


def test_resolve_identity_context_returns_actor_ref_without_subject() -> None:
    with _db_session() as db:
        resolved = resolve_identity_context(
            db=db,
            request=_request({"x-actor-ref": "actor:legacy", "x-trace-id": "trace-1"}),
        )

    assert resolved.user_id is None
    assert resolved.reviewer_ref == "actor:legacy"
    assert resolved.owner_ref == "actor:legacy"
    assert resolved.auth_context.actor_ref == "actor:legacy"
    assert resolved.auth_context.trace_id == "trace-1"


def test_resolve_identity_context_raises_when_identity_missing_and_jit_disabled() -> None:
    original = settings.allow_jit_provisioning
    settings.allow_jit_provisioning = False
    try:
        with _db_session() as db:
            try:
                resolve_identity_context(
                    db=db,
                    request=_request({"x-auth-subject": "sub-1", "x-auth-provider": "oidc"}),
                )
            except HTTPException as exc:
                assert exc.status_code == 403
                assert exc.detail["code"] == "identity_not_provisioned"
            else:  # pragma: no cover
                raise AssertionError("Expected HTTPException")
    finally:
        settings.allow_jit_provisioning = original


def test_resolve_identity_context_raises_conflict_for_duplicate_provider_subject() -> None:
    with _db_session(allow_legacy_ambiguous_identities=True) as db:
        db.add_all(
            [
                UserRow(
                    id="u-1",
                    display_name=None,
                    email=None,
                    lifecycle_state="active",
                    created_at="2026-01-01T00:00:00+00:00",
                    updated_at="2026-01-01T00:00:00+00:00",
                ),
                UserRow(
                    id="u-2",
                    display_name=None,
                    email=None,
                    lifecycle_state="active",
                    created_at="2026-01-01T00:00:00+00:00",
                    updated_at="2026-01-01T00:00:00+00:00",
                ),
            ]
        )
        db.commit()
        db.add_all(
            [
                UserIdentityRow(user_id="u-1", provider="oidc", external_uid="dup", created_at="2026-01-01T00:00:00+00:00"),
                UserIdentityRow(user_id="u-2", provider="OIDC", external_uid="dup", created_at="2026-01-01T00:00:00+00:00"),
            ]
        )
        db.commit()

        try:
            resolve_identity_context(
                db=db,
                request=_request({"x-auth-subject": "dup", "x-auth-provider": "oidc"}),
            )
        except HTTPException as exc:
            assert exc.status_code == 409
            assert exc.detail["code"] == "identity_mapping_conflict"
        else:  # pragma: no cover
            raise AssertionError("Expected HTTPException")


@pytest.fixture
def _restore_trusted_proxies():
    original = settings.trusted_proxies
    yield
    settings.trusted_proxies = original


def test_check_trusted_proxy_allows_any_origin_when_unconfigured(_restore_trusted_proxies) -> None:
    settings.trusted_proxies = ""

    _check_trusted_proxy(_request({}, client_host="203.0.113.7"))
    _check_trusted_proxy(_request({}))  # no client info at all


def test_check_trusted_proxy_allows_ip_inside_configured_cidr(_restore_trusted_proxies) -> None:
    settings.trusted_proxies = "10.0.0.0/8,172.16.0.0/12"

    _check_trusted_proxy(_request({}, client_host="10.1.2.3"))
    _check_trusted_proxy(_request({}, client_host="172.16.5.5"))


def test_check_trusted_proxy_rejects_ip_outside_configured_cidr(_restore_trusted_proxies) -> None:
    settings.trusted_proxies = "10.0.0.0/8"

    with pytest.raises(HTTPException) as exc_info:
        _check_trusted_proxy(_request({}, client_host="203.0.113.7"))

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail["code"] == "untrusted_proxy"


def test_check_trusted_proxy_rejects_when_client_ip_unknown(_restore_trusted_proxies) -> None:
    settings.trusted_proxies = "10.0.0.0/8"

    with pytest.raises(HTTPException) as exc_info:
        _check_trusted_proxy(_request({}))  # no client info

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail["code"] == "untrusted_proxy"


def test_check_trusted_proxy_rejects_malformed_client_ip(_restore_trusted_proxies) -> None:
    settings.trusted_proxies = "10.0.0.0/8"

    with pytest.raises(HTTPException) as exc_info:
        _check_trusted_proxy(_request({}, client_host="not-an-ip"))

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail["code"] == "untrusted_proxy"


def test_resolve_identity_context_rejects_untrusted_proxy_before_reading_headers(
    _restore_trusted_proxies,
) -> None:
    """The trusted-proxy check must run before forwarded headers are trusted;
    an untrusted origin is rejected even if it supplies a fully-formed
    identity header set."""
    settings.trusted_proxies = "10.0.0.0/8"

    with _db_session() as db:
        with pytest.raises(HTTPException) as exc_info:
            resolve_identity_context(
                db=db,
                request=_request(
                    {"x-auth-subject": "sub-1", "x-auth-provider": "oidc"},
                    client_host="203.0.113.7",
                ),
            )

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail["code"] == "untrusted_proxy"
