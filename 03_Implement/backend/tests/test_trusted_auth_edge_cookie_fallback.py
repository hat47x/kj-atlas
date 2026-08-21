"""SAAS-TENANT-SESSION-BINDING-01 AC-1: the BFF cookie-fallback branch of
JwtSaasIdentityContextResolver shipped without tests.

These pin the fail-closed contract of _resolve_from_auth_session_cookie
(ADR-0074 decisions 2/3): every way a presented cookie can fail to name a
live, tenant-bound session must end in 401 rather than in an identity.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

import pytest
from fastapi import Request
from sqlalchemy import create_engine, update
from sqlalchemy.orm import Session, sessionmaker

import kj_atlas_api.trusted_auth_edge as trusted_auth_edge
from kj_atlas_api.auth_session_hash import derive_session_key_hash
from kj_atlas_api.jwks_store import JwksStore
from kj_atlas_api.models import Base, IdentityProviderRow, SaasAuthSessionRow, TenantRow
from kj_atlas_api.saas_auth_state import DatabaseSaasAuthSessionStore
from kj_atlas_api.trusted_auth_edge import (
    JwtIdentityError,
    JwtSaasIdentityContextResolver,
)

TIMESTAMP = "2026-08-20T00:00:00Z"
COOKIE_NAME = "Kj-Atlas-Auth-Session"
HASH_KEY = b"cookie-fallback-test-key-0123456"
ISSUER = "https://broker.invalid/issuer"
RAW_SESSION = "opaque-raw-session-value-abcdef"


@dataclass
class _Edge:
    resolver: JwtSaasIdentityContextResolver
    store: DatabaseSaasAuthSessionStore
    factory: object
    db: Session


@pytest.fixture
def edge(tmp_path):
    """A resolver wired to a real auth-session store over one sqlite file."""
    engine = create_engine(
        f"sqlite:///{tmp_path}/edge.db",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, class_=Session, expire_on_commit=False)
    with factory() as seed:
        seed.add_all(
            [
                TenantRow(
                    id="tenant-a",
                    display_name="Tenant A",
                    lifecycle_state="active",
                    created_at=TIMESTAMP,
                    updated_at=TIMESTAMP,
                ),
                IdentityProviderRow(
                    id="idp-1",
                    issuer=ISSUER,
                    audience="kj-atlas",
                    protocol="oidc",
                    jwks_uri="https://broker.invalid/jwks.json",
                    lifecycle_state="active",
                    created_at=TIMESTAMP,
                    updated_at=TIMESTAMP,
                ),
            ]
        )
        seed.commit()

    store = DatabaseSaasAuthSessionStore(factory)
    resolver = JwtSaasIdentityContextResolver(
        jwks_store=JwksStore(),
        auth_session_store=store,
        auth_session_hash_key=HASH_KEY,
    )
    with factory() as db:
        yield _Edge(resolver=resolver, store=store, factory=factory, db=db)


def _request(cookie: str | None = None, bearer: str | None = None) -> Request:
    headers: list[tuple[bytes, bytes]] = []
    if cookie is not None:
        headers.append((b"cookie", f"{COOKIE_NAME}={cookie}".encode()))
    if bearer is not None:
        headers.append((b"x-kj-atlas-authorization", f"Bearer {bearer}".encode()))
    return Request(scope={"type": "http", "method": "GET", "path": "/", "headers": headers})


def _login(
    store: DatabaseSaasAuthSessionStore,
    tenant: str | None = "tenant-a",
    raw: str = RAW_SESSION,
) -> None:
    store.create_auth_session(
        session_key_hash=derive_session_key_hash(raw, key=HASH_KEY),
        principal_id="user-1",
        issuer=ISSUER,
        subject="subject-1",
        active_tenant_id=tenant,
        tenant_session_version="version-1",
    )


def test_valid_cookie_resolves_identity_and_tenant_claim(edge) -> None:
    _login(edge.store)

    identity = edge.resolver.resolve(db=edge.db, request=_request(cookie=RAW_SESSION))

    assert identity.user_id == "user-1"
    assert identity.auth_context.provider == "idp-1"
    assert identity.auth_context.external_uid == "subject-1"
    claim = identity.verified_tenant_claim
    assert claim is not None
    assert claim.tenant_id == "tenant-a"
    assert claim.issuer == ISSUER
    assert claim.audience == "kj-atlas"
    assert claim.subject == "subject-1"
    assert claim.identity_provider_id == "idp-1"


def test_missing_cookie_is_reported_as_a_missing_token(edge) -> None:
    with pytest.raises(JwtIdentityError) as exc:
        edge.resolver.resolve(db=edge.db, request=_request())

    assert exc.value.status_code == 401
    assert exc.value.code == "missing_token"


def test_resolver_without_an_auth_session_store_cannot_use_the_cookie(edge) -> None:
    _login(edge.store)
    unwired = JwtSaasIdentityContextResolver(jwks_store=JwksStore())

    with pytest.raises(JwtIdentityError) as exc:
        unwired.resolve(db=edge.db, request=_request(cookie=RAW_SESSION))

    assert exc.value.status_code == 401
    assert exc.value.code == "missing_token"


def test_unknown_cookie_value_is_rejected(edge) -> None:
    with pytest.raises(JwtIdentityError) as exc:
        edge.resolver.resolve(db=edge.db, request=_request(cookie="never-issued"))

    assert exc.value.status_code == 401
    assert exc.value.code == "session_invalid"


def test_oversized_cookie_is_rejected_before_hashing_or_lookup(edge, monkeypatch) -> None:
    """AC-6: an oversized presented value fails closed without ever reaching
    the hash/store-lookup step -- not merely because an oversized value
    happens to be unknown (an unknown-but-in-bounds value would 401 the
    same way, so this pins the length check specifically)."""
    _login(edge.store)
    oversized = "x" * 257

    def _fail_if_called(*_args, **_kwargs):
        raise AssertionError("derive_session_key_hash must not be called for an oversized cookie")

    monkeypatch.setattr(trusted_auth_edge, "derive_session_key_hash", _fail_if_called)

    with pytest.raises(JwtIdentityError) as exc:
        edge.resolver.resolve(db=edge.db, request=_request(cookie=oversized))

    assert exc.value.status_code == 401
    assert exc.value.code == "session_invalid"


def test_cookie_hashed_under_a_different_key_is_rejected(edge) -> None:
    """ADR-0074 decision 2: lookup goes through the keyed hash, so a cookie
    minted under another key must not resolve."""
    _login(edge.store)
    other = JwtSaasIdentityContextResolver(
        jwks_store=JwksStore(),
        auth_session_store=edge.store,
        auth_session_hash_key=b"a-completely-different-hash-key01",
    )

    with pytest.raises(JwtIdentityError) as exc:
        other.resolve(db=edge.db, request=_request(cookie=RAW_SESSION))

    assert exc.value.status_code == 401
    assert exc.value.code == "session_invalid"


def test_revoked_session_cookie_is_rejected(edge) -> None:
    _login(edge.store)
    edge.store.revoke_auth_session(
        session_key_hash=derive_session_key_hash(RAW_SESSION, key=HASH_KEY)
    )

    with pytest.raises(JwtIdentityError) as exc:
        edge.resolver.resolve(db=edge.db, request=_request(cookie=RAW_SESSION))

    assert exc.value.status_code == 401
    assert exc.value.code == "session_invalid"


def test_idle_expired_session_cookie_is_rejected(edge) -> None:
    _login(edge.store)
    stale = (datetime.now(timezone.utc) - timedelta(minutes=61)).isoformat()
    with edge.factory() as db:
        db.execute(update(SaasAuthSessionRow).values(last_used_at=stale))
        db.commit()

    with pytest.raises(JwtIdentityError) as exc:
        edge.resolver.resolve(db=edge.db, request=_request(cookie=RAW_SESSION))

    assert exc.value.status_code == 401
    assert exc.value.code == "session_invalid"


def test_session_without_an_active_tenant_fails_closed(edge) -> None:
    """The tenant FK is ON DELETE SET NULL, so a login whose tenant went away
    must not resolve to an identity with no tenant to bind against."""
    _login(edge.store, tenant=None)

    with pytest.raises(JwtIdentityError) as exc:
        edge.resolver.resolve(db=edge.db, request=_request(cookie=RAW_SESSION))

    assert exc.value.status_code == 401
    assert exc.value.code == "session_invalid"


def test_unresolvable_issuer_is_a_configuration_error_not_an_auth_failure(edge) -> None:
    _login(edge.store)
    with edge.factory() as db:
        db.execute(update(IdentityProviderRow).values(lifecycle_state="disabled"))
        db.commit()

    with pytest.raises(JwtIdentityError) as exc:
        edge.resolver.resolve(db=edge.db, request=_request(cookie=RAW_SESSION))

    assert exc.value.status_code == 503
    assert exc.value.code == "configuration_error"


def test_cookie_path_surfaces_a_session_identifier_distinct_from_the_principal(edge) -> None:
    """AC-1 proper: the auth edge must not merely consume the session identifier
    internally, it must surface it, so session-scoped state (AC-2 onward) can key
    on the login session instead of the principal."""
    _login(edge.store)

    identity = edge.resolver.resolve(db=edge.db, request=_request(cookie=RAW_SESSION))

    assert identity.auth_session_key_hash == derive_session_key_hash(RAW_SESSION, key=HASH_KEY)
    assert identity.auth_session_key_hash != identity.user_id


def test_two_logins_of_one_principal_surface_distinct_session_identifiers(edge) -> None:
    """ADR-0074 decision 3 / AC-5 prerequisite: same user, two browsers, two
    independent session identities."""
    second_raw = "second-browser-opaque-session"
    _login(edge.store)
    _login(edge.store, raw=second_raw)

    first = edge.resolver.resolve(db=edge.db, request=_request(cookie=RAW_SESSION))
    second = edge.resolver.resolve(db=edge.db, request=_request(cookie=second_raw))

    assert first.user_id == second.user_id == "user-1"
    assert first.auth_session_key_hash != second.auth_session_key_hash


def test_a_bearer_header_takes_precedence_over_a_valid_cookie(edge) -> None:
    """Documented AC-1 limitation: resolve() never reaches the cookie branch
    while a bearer header is present, so a bearer-first SPA never exercises it."""
    _login(edge.store)

    with pytest.raises(JwtIdentityError) as exc:
        edge.resolver.resolve(
            db=edge.db, request=_request(cookie=RAW_SESSION, bearer="not-a-jwt")
        )

    assert exc.value.code == "invalid_token"
