from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def write(rel: str, content: str) -> None:
    path = ROOT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def replace_once(rel: str, old: str, new: str) -> None:
    path = ROOT / rel
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"expected exactly one match in {rel}, got {count}: {old!r}")
    path.write_text(text.replace(old, new), encoding="utf-8")


write(
    "03_Implement/backend/src/kj_atlas_api/guest_redeem_state_models.py",
    '''from __future__ import annotations

from sqlalchemy import ForeignKeyConstraint, Index, Text
from sqlalchemy.orm import Mapped, mapped_column

from kj_atlas_api.guest_admission_models import GuestPrincipalRow  # noqa: F401
from kj_atlas_api.models import Base
from kj_atlas_api.persistence_shapes import apply_persistent_text_shapes


class GuestRedeemStateRow(Base):
    """One-time pre-tenant handle binding an invitation to guest login.

    The raw handle is never persisted. This row is intentionally pre-tenant
    authentication state: it must be found from the opaque handle before the
    tenant is known. After resolution, callers immediately apply the normal
    transaction-local tenant guard before touching the guest principal.
    """

    __tablename__ = "guest_redeem_states"
    __table_args__ = (
        ForeignKeyConstraint(
            ["tenant_id", "guest_principal_id"],
            ["guest_principals.tenant_id", "guest_principals.guest_principal_id"],
            name="fk_guest_redeem_states_principal",
            ondelete="CASCADE",
        ),
        Index("ix_guest_redeem_states_principal", "tenant_id", "guest_principal_id"),
    )

    state_key_hash: Mapped[str] = mapped_column(Text, primary_key=True)
    tenant_id: Mapped[str] = mapped_column(Text, nullable=False)
    guest_principal_id: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[str] = mapped_column(Text, nullable=False)
    expires_at: Mapped[str] = mapped_column(Text, nullable=False)
    consumed_at: Mapped[str | None] = mapped_column(Text, nullable=True)


apply_persistent_text_shapes(Base.metadata)
''',
)

write(
    "03_Implement/backend/src/kj_atlas_api/guest_redeem.py",
    '''"""ADR-0080 guest invitation redeem boundary.

The opaque redeem state is host-created and is the sole source of tenant and
principal identity. External identity verification remains a separate trusted
adapter: this module accepts only its verified issuer/subject result and never a
member ``VerifiedTenantClaim``.
"""

from __future__ import annotations

import secrets
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Protocol

from sqlalchemy import select
from sqlalchemy.orm import Session

from kj_atlas_api.auth_session_hash import derive_session_key_hash
from kj_atlas_api.guest_admission_models import GuestPrincipalRow
from kj_atlas_api.guest_admission_repository import GuestAdmissionError, GuestAdmissionRepository
from kj_atlas_api.guest_auth_state import create_guest_auth_session_in_transaction
from kj_atlas_api.guest_redeem_state_models import GuestRedeemStateRow
from kj_atlas_api.tenant_db_guard import apply_database_tenant_id

_REDEEM_STATE_LIFETIME = timedelta(minutes=15)
_REDEEM_STATE_DOMAIN = "guest-redeem-v1\\x00"


class GuestRedeemError(ValueError):
    """Redeem state is invalid, stale, consumed, or cannot be activated."""


class GuestIdentityVerificationError(ValueError):
    """Trusted guest identity verification failed."""


@dataclass(frozen=True, slots=True)
class VerifiedGuestIdentity:
    issuer: str
    subject: str


@dataclass(frozen=True, slots=True)
class GuestRedeemChallenge:
    tenant_id: str
    guest_principal_id: str
    verification_method: str


class GuestIdentityVerifier(Protocol):
    def verify_identity(
        self, *, credential: str, verification_method: str
    ) -> VerifiedGuestIdentity: ...


def _utc(now: datetime | None = None) -> datetime:
    value = now or datetime.now(timezone.utc)
    if value.tzinfo is None or value.utcoffset() is None:
        raise GuestRedeemError("now must be timezone-aware")
    return value.astimezone(timezone.utc)


def _parse_timestamp(value: str) -> datetime | None:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        return None
    return parsed.astimezone(timezone.utc)


def _state_hash(raw_state: str, *, hash_key: bytes) -> str:
    if not raw_state or len(raw_state) > 256 or raw_state.strip() != raw_state:
        raise GuestRedeemError("redeem state is invalid")
    return derive_session_key_hash(_REDEEM_STATE_DOMAIN + raw_state, key=hash_key)


def _valid_state(row: GuestRedeemStateRow | None, *, now: datetime) -> GuestRedeemStateRow:
    if row is None or row.consumed_at is not None:
        raise GuestRedeemError("redeem state is invalid")
    expiry = _parse_timestamp(row.expires_at)
    if expiry is None or expiry <= now:
        raise GuestRedeemError("redeem state is invalid")
    return row


class DatabaseGuestRedeemStateStore:
    """Issue and redeem one-time invitation handles without client tenant input."""

    def __init__(self, session_factory: Callable[[], Session]) -> None:
        self._session_factory = session_factory

    def issue_redeem_state(
        self,
        *,
        tenant_id: str,
        guest_principal_id: str,
        hash_key: bytes,
        now: datetime | None = None,
    ) -> str:
        current = _utc(now)
        raw_state = secrets.token_urlsafe(32)
        state_key_hash = _state_hash(raw_state, hash_key=hash_key)
        with self._session_factory() as db:
            apply_database_tenant_id(db=db, tenant_id=tenant_id)
            principal = db.get(GuestPrincipalRow, (tenant_id, guest_principal_id))
            if principal is None or principal.status != "pending" or principal.revoked_at is not None:
                raise GuestRedeemError("guest invitation is not redeemable")
            invitation_expiry = _parse_timestamp(principal.expires_at)
            if invitation_expiry is None or invitation_expiry <= current:
                raise GuestRedeemError("guest invitation is not redeemable")
            expires_at = min(current + _REDEEM_STATE_LIFETIME, invitation_expiry)
            db.add(
                GuestRedeemStateRow(
                    state_key_hash=state_key_hash,
                    tenant_id=tenant_id,
                    guest_principal_id=guest_principal_id,
                    created_at=current.isoformat(),
                    expires_at=expires_at.isoformat(),
                    consumed_at=None,
                )
            )
            db.commit()
        return raw_state

    def resolve_challenge(
        self,
        *,
        raw_state: str,
        hash_key: bytes,
        now: datetime | None = None,
    ) -> GuestRedeemChallenge:
        current = _utc(now)
        state_key_hash = _state_hash(raw_state, hash_key=hash_key)
        with self._session_factory() as db:
            row = _valid_state(db.get(GuestRedeemStateRow, state_key_hash), now=current)
            apply_database_tenant_id(db=db, tenant_id=row.tenant_id)
            principal = db.get(GuestPrincipalRow, (row.tenant_id, row.guest_principal_id))
            if principal is None or principal.status != "pending" or principal.revoked_at is not None:
                raise GuestRedeemError("redeem state is invalid")
            return GuestRedeemChallenge(
                tenant_id=row.tenant_id,
                guest_principal_id=row.guest_principal_id,
                verification_method=principal.verification_method,
            )

    def redeem_verified_identity(
        self,
        *,
        raw_state: str,
        hash_key: bytes,
        session_hash_key: bytes,
        identity: VerifiedGuestIdentity,
        now: datetime | None = None,
    ) -> str:
        """Atomically activate the principal, consume state, and mint a session."""
        current = _utc(now)
        state_key_hash = _state_hash(raw_state, hash_key=hash_key)
        raw_session_id = secrets.token_urlsafe(32)
        session_key_hash = derive_session_key_hash(raw_session_id, key=session_hash_key)
        with self._session_factory() as db:
            try:
                row = _valid_state(
                    db.scalar(
                        select(GuestRedeemStateRow)
                        .where(GuestRedeemStateRow.state_key_hash == state_key_hash)
                        .with_for_update()
                    ),
                    now=current,
                )
                apply_database_tenant_id(db=db, tenant_id=row.tenant_id)
                repo = GuestAdmissionRepository(db, tenant_id=row.tenant_id)
                repo.activate_verified_guest(
                    guest_principal_id=row.guest_principal_id,
                    verified_issuer=identity.issuer,
                    verified_subject=identity.subject,
                    redeemed_at=current.isoformat(),
                    now=current,
                )
                create_guest_auth_session_in_transaction(
                    db,
                    session_key_hash=session_key_hash,
                    tenant_id=row.tenant_id,
                    guest_principal_id=row.guest_principal_id,
                    issuer=identity.issuer,
                    subject=identity.subject,
                    now=current,
                )
                row.consumed_at = current.isoformat()
                db.commit()
            except (GuestAdmissionError, GuestRedeemError) as exc:
                db.rollback()
                raise GuestRedeemError("redeem state is invalid") from exc
            except Exception:
                db.rollback()
                raise
        return raw_session_id

    def preflight(self) -> None:
        with self._session_factory() as db:
            db.execute(select(GuestRedeemStateRow.state_key_hash).limit(1))
''',
)

write(
    "03_Implement/backend/src/kj_atlas_api/routes/guest_session.py",
    '''from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

from kj_atlas_api.active_tenant_session import tenant_session_cookie_is_secure
from kj_atlas_api.guest_redeem import (
    GuestIdentityVerificationError,
    GuestRedeemError,
)
from kj_atlas_api.guest_request_auth import GUEST_AUTH_SESSION_COOKIE

router = APIRouter(prefix="/session/guest", tags=["guest-session"])
_GUEST_SESSION_MAX_AGE_SECONDS = 12 * 60 * 60


class GuestRedeemRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    state: str = Field(min_length=16, max_length=256)
    identity_credential: str = Field(alias="identityCredential", min_length=1, max_length=8192)


@router.post("/redeem")
def redeem_guest_session(payload: GuestRedeemRequest, request: Request) -> JSONResponse:
    """Exchange a host-bound redeem state plus trusted identity proof for a guest session.

    Tenant/principal are deliberately absent from the request schema. They are
    recovered only from the one-time state. The verifier is a guest-specific
    trusted adapter and must not return a member VerifiedTenantClaim.
    """
    store = getattr(request.app.state, "guest_redeem_state_store", None)
    verifier = getattr(request.app.state, "guest_identity_verifier", None)
    state_hash_key = getattr(request.app.state, "guest_redeem_state_hash_key", None)
    session_hash_key = getattr(request.app.state, "guest_auth_session_hash_key", None)
    if store is None or verifier is None or state_hash_key is None or session_hash_key is None:
        raise HTTPException(
            status_code=503,
            detail={
                "code": "guest_redeem_unavailable",
                "message": "Guest sign-in is unavailable.",
            },
        )

    try:
        challenge = store.resolve_challenge(
            raw_state=payload.state,
            hash_key=state_hash_key,
        )
        identity = verifier.verify_identity(
            credential=payload.identity_credential,
            verification_method=challenge.verification_method,
        )
        raw_session_id = store.redeem_verified_identity(
            raw_state=payload.state,
            hash_key=state_hash_key,
            session_hash_key=session_hash_key,
            identity=identity,
        )
    except (GuestRedeemError, GuestIdentityVerificationError):
        raise HTTPException(
            status_code=401,
            detail={"code": "guest_redeem_invalid", "message": "Guest sign-in failed."},
        ) from None
    except Exception:
        raise HTTPException(
            status_code=503,
            detail={
                "code": "guest_redeem_persistence_failed",
                "message": "Guest sign-in could not be completed.",
            },
        ) from None

    runtime_profile = getattr(request.app.state, "runtime_profile", "local-dev")
    response = JSONResponse(
        status_code=200,
        content={"status": "redeemed"},
        headers={"Cache-Control": "no-store", "Pragma": "no-cache"},
    )
    response.set_cookie(
        key=GUEST_AUTH_SESSION_COOKIE,
        value=raw_session_id,
        httponly=True,
        secure=tenant_session_cookie_is_secure(runtime_profile),
        samesite="strict",
        max_age=_GUEST_SESSION_MAX_AGE_SECONDS,
        path="/",
    )
    return response
''',
)

write(
    "03_Implement/backend/alembic/versions/20260907_0035_add_guest_redeem_states.py",
    '''"""add one-time guest invitation redeem state

Revision ID: 20260907_0035
Revises: 20260906_0034

The opaque state is resolved before a tenant is known, so this table is
intentionally pre-tenant authentication state and is not protected by tenant
RLS. It grants no document access and only binds a short-lived handle to an
existing pending guest principal; tenant-scoped work resumes immediately after
state resolution.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260907_0035"
down_revision: str | None = "20260906_0034"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "guest_redeem_states",
        sa.Column("state_key_hash", sa.String(256), nullable=False),
        sa.Column("tenant_id", sa.String(128), nullable=False),
        sa.Column("guest_principal_id", sa.String(128), nullable=False),
        sa.Column("created_at", sa.String(40), nullable=False),
        sa.Column("expires_at", sa.String(40), nullable=False),
        sa.Column("consumed_at", sa.String(40), nullable=True),
        sa.PrimaryKeyConstraint("state_key_hash", name="pk_guest_redeem_states"),
        sa.ForeignKeyConstraint(
            ["tenant_id", "guest_principal_id"],
            ["guest_principals.tenant_id", "guest_principals.guest_principal_id"],
            name="fk_guest_redeem_states_principal",
            ondelete="CASCADE",
        ),
    )
    op.create_index(
        "ix_guest_redeem_states_principal",
        "guest_redeem_states",
        ["tenant_id", "guest_principal_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_guest_redeem_states_principal", table_name="guest_redeem_states")
    op.drop_table("guest_redeem_states")
''',
)

write(
    "03_Implement/backend/tests/test_guest_redeem_http.py",
    '''from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select, update
from sqlalchemy.orm import Session, sessionmaker

import kj_atlas_api.guest_redeem as guest_redeem_module
from kj_atlas_api.db import get_db
from kj_atlas_api.guest_admission_models import GuestDocumentGrantRow, GuestPrincipalRow
from kj_atlas_api.guest_auth_session_models import GuestAuthSessionRow
from kj_atlas_api.guest_auth_state import DatabaseGuestAuthSessionStore
from kj_atlas_api.guest_redeem import (
    DatabaseGuestRedeemStateStore,
    GuestIdentityVerificationError,
    VerifiedGuestIdentity,
)
from kj_atlas_api.guest_redeem_state_models import GuestRedeemStateRow
from kj_atlas_api.models import (
    Base,
    DocumentRow,
    TenantIdentityProviderRow,
    TenantMembershipRow,
    TenantRow,
)
from kj_atlas_api.routes.docs import router as docs_router
from kj_atlas_api.routes.guest_session import router as guest_session_router

NOW = datetime(2026, 9, 7, 0, 30, tzinfo=timezone.utc)
TS = NOW.isoformat()
STATE_HASH_KEY = b"guest-redeem-state-test-key-012345"
SESSION_HASH_KEY = b"guest-session-test-key-01234567890"
ISSUER = "https://personal-idp.example.test"
SUBJECT = "personal-subject-1"


def _payload(doc_id: str) -> dict[str, object]:
    return {
        "version": 1,
        "id": doc_id,
        "title": doc_id,
        "createdAt": "2026-09-07T00:30:00Z",
        "updatedAt": "2026-09-07T00:30:00Z",
        "transform": {"panX": 0, "panY": 0, "zoom": 1},
        "cards": [],
        "edges": [],
        "islands": [],
    }


class AcceptingVerifier:
    def verify_identity(self, *, credential: str, verification_method: str) -> VerifiedGuestIdentity:
        assert credential == "provider-proof"
        assert verification_method == "personal_account"
        return VerifiedGuestIdentity(issuer=ISSUER, subject=SUBJECT)


class RejectingVerifier:
    def verify_identity(self, *, credential: str, verification_method: str) -> VerifiedGuestIdentity:
        raise GuestIdentityVerificationError("provider rejected credential")


@pytest.fixture
def redeem_env(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path}/guest-redeem.db")
    factory = sessionmaker(bind=engine, class_=Session, expire_on_commit=False)
    Base.metadata.create_all(engine)
    with factory() as db:
        db.add(
            TenantRow(
                id="tenant-a",
                display_name="Tenant A",
                lifecycle_state="active",
                created_at=TS,
                updated_at=TS,
            )
        )
        db.add(
            DocumentRow(
                tenant_id="tenant-a",
                id="doc-granted",
                version=1,
                updated_at=TS,
                payload_json=json.dumps(_payload("doc-granted")),
                created_by="owner-1",
                lifecycle_state="active",
            )
        )
        db.add(
            GuestPrincipalRow(
                tenant_id="tenant-a",
                guest_principal_id="guest-1",
                invited_email="guest@example.test",
                status="pending",
                verification_method="personal_account",
                verified_issuer=None,
                verified_subject=None,
                created_by="owner-1",
                created_at=TS,
                expires_at=(NOW + timedelta(hours=2)).isoformat(),
                redeemed_at=None,
                revoked_at=None,
            )
        )
        db.add(
            GuestDocumentGrantRow(
                tenant_id="tenant-a",
                guest_principal_id="guest-1",
                doc_id="doc-granted",
                granted_by="owner-1",
                granted_at=TS,
                revoked_at=None,
            )
        )
        db.commit()

    state_store = DatabaseGuestRedeemStateStore(factory)
    auth_store = DatabaseGuestAuthSessionStore(factory)
    raw_state = state_store.issue_redeem_state(
        tenant_id="tenant-a",
        guest_principal_id="guest-1",
        hash_key=STATE_HASH_KEY,
        now=NOW,
    )

    def make_client(verifier=AcceptingVerifier()):
        app = FastAPI()
        app.include_router(guest_session_router)
        app.include_router(docs_router)
        app.state.runtime_profile = "evaluation"
        app.state.guest_redeem_state_store = state_store
        app.state.guest_redeem_state_hash_key = STATE_HASH_KEY
        app.state.guest_identity_verifier = verifier
        app.state.guest_auth_session_store = auth_store
        app.state.guest_auth_session_hash_key = SESSION_HASH_KEY
        app.state.access_control_adapter = None
        app.state.audit_dispatcher = None

        def _test_db():
            with factory() as db:
                yield db

        app.dependency_overrides[get_db] = _test_db
        return TestClient(app)

    yield factory, state_store, raw_state, make_client
    engine.dispose()


def _redeem(client: TestClient, raw_state: str, **extra):
    payload = {"state": raw_state, "identityCredential": "provider-proof", **extra}
    return client.post("/session/guest/redeem", json=payload)


def test_redeem_uses_host_state_then_existing_exact_grant(redeem_env) -> None:
    factory, _, raw_state, make_client = redeem_env
    with factory() as db:
        stored = db.scalar(select(GuestRedeemStateRow))
        assert stored is not None
        assert raw_state not in stored.state_key_hash

    with make_client() as client:
        response = _redeem(client, raw_state)
        assert response.status_code == 200
        assert response.json() == {"status": "redeemed"}
        assert "Kj-Atlas-Guest-Session" in response.cookies
        read = client.get("/docs/doc-granted")
        assert read.status_code == 200
        assert read.json()["id"] == "doc-granted"

    with factory() as db:
        principal = db.get(GuestPrincipalRow, ("tenant-a", "guest-1"))
        assert principal is not None
        assert principal.status == "active"
        assert principal.verified_issuer == ISSUER
        assert principal.verified_subject == SUBJECT
        assert db.scalars(select(TenantMembershipRow)).all() == []
        assert db.scalars(select(TenantIdentityProviderRow)).all() == []
        assert len(db.scalars(select(GuestAuthSessionRow)).all()) == 1
        state = db.scalar(select(GuestRedeemStateRow))
        assert state is not None and state.consumed_at is not None


def test_redeem_state_is_one_time(redeem_env) -> None:
    _, _, raw_state, make_client = redeem_env
    with make_client() as client:
        assert _redeem(client, raw_state).status_code == 200
        replay = _redeem(client, raw_state)
    assert replay.status_code == 401
    assert replay.json()["detail"]["code"] == "guest_redeem_invalid"


def test_client_cannot_supply_tenant_principal_or_identity_claims(redeem_env) -> None:
    factory, _, raw_state, make_client = redeem_env
    with make_client() as client:
        response = _redeem(
            client,
            raw_state,
            tenantId="tenant-b",
            guestPrincipalId="attacker",
            issuer="https://attacker.invalid",
            subject="attacker",
        )
    assert response.status_code == 422
    with factory() as db:
        principal = db.get(GuestPrincipalRow, ("tenant-a", "guest-1"))
        state = db.scalar(select(GuestRedeemStateRow))
        assert principal is not None and principal.status == "pending"
        assert state is not None and state.consumed_at is None


def test_identity_verification_failure_does_not_consume_or_activate(redeem_env) -> None:
    factory, _, raw_state, make_client = redeem_env
    with make_client(RejectingVerifier()) as client:
        response = _redeem(client, raw_state)
    assert response.status_code == 401
    with factory() as db:
        principal = db.get(GuestPrincipalRow, ("tenant-a", "guest-1"))
        state = db.scalar(select(GuestRedeemStateRow))
        assert principal is not None and principal.status == "pending"
        assert state is not None and state.consumed_at is None
        assert db.scalars(select(GuestAuthSessionRow)).all() == []


def test_session_persistence_failure_rolls_back_activation_and_state(redeem_env, monkeypatch) -> None:
    factory, _, raw_state, make_client = redeem_env

    def fail_session(*args, **kwargs):
        raise RuntimeError("forced session persistence failure")

    monkeypatch.setattr(
        guest_redeem_module,
        "create_guest_auth_session_in_transaction",
        fail_session,
    )
    with make_client() as client:
        response = _redeem(client, raw_state)
    assert response.status_code == 503
    with factory() as db:
        principal = db.get(GuestPrincipalRow, ("tenant-a", "guest-1"))
        state = db.scalar(select(GuestRedeemStateRow))
        assert principal is not None and principal.status == "pending"
        assert principal.verified_issuer is None
        assert state is not None and state.consumed_at is None
        assert db.scalars(select(GuestAuthSessionRow)).all() == []


def test_expired_state_fails_closed(redeem_env) -> None:
    factory, _, raw_state, make_client = redeem_env
    with factory() as db:
        db.execute(
            update(GuestRedeemStateRow).values(
                expires_at=(datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat()
            )
        )
        db.commit()
    with make_client() as client:
        response = _redeem(client, raw_state)
    assert response.status_code == 401
''',
)

# Atomic session creation helper: R2a's public store keeps its commit behavior,
# while R2b can compose the row insert into invitation activation transaction.
replace_once(
    "03_Implement/backend/src/kj_atlas_api/guest_auth_state.py",
    "    def resolve_guest_auth_session(\n",
    '''    def resolve_guest_auth_session(\n''',
)
# Insert helper after the class body so it can reuse the exact R2a principal validator.
path = ROOT / "03_Implement/backend/src/kj_atlas_api/guest_auth_state.py"
text = path.read_text(encoding="utf-8")
if "def create_guest_auth_session_in_transaction(" not in text:
    text += '''\n\ndef create_guest_auth_session_in_transaction(\n    db: Session,\n    *,\n    session_key_hash: str,\n    tenant_id: str,\n    guest_principal_id: str,\n    issuer: str,\n    subject: str,\n    now: datetime | None = None,\n) -> None:\n    """Insert a guest auth session without committing the caller transaction."""\n    current = now or datetime.now(timezone.utc)\n    if current.tzinfo is None or current.utcoffset() is None:\n        raise GuestAuthSessionError("now must be timezone-aware")\n    current = current.astimezone(timezone.utc)\n    DatabaseGuestAuthSessionStore._require_verified_principal(\n        db,\n        tenant_id=tenant_id,\n        guest_principal_id=guest_principal_id,\n        issuer=issuer,\n        subject=subject,\n    )\n    db.add(\n        GuestAuthSessionRow(\n            session_key_hash=session_key_hash,\n            tenant_id=tenant_id,\n            guest_principal_id=guest_principal_id,\n            issuer=issuer,\n            subject=subject,\n            created_at=current.isoformat(),\n            last_used_at=current.isoformat(),\n            absolute_expires_at=(current + _ABSOLUTE_SESSION_LIFETIME).isoformat(),\n            revoked_at=None,\n        )\n    )\n    db.flush()\n'''
    path.write_text(text, encoding="utf-8")

replace_once(
    "03_Implement/backend/alembic/env.py",
    "from kj_atlas_api import guest_auth_session_models as _guest_auth_session_models  # noqa: E402,F401\n",
    "from kj_atlas_api import guest_auth_session_models as _guest_auth_session_models  # noqa: E402,F401\nfrom kj_atlas_api import guest_redeem_state_models as _guest_redeem_state_models  # noqa: E402,F401\n",
)

replace_once(
    "03_Implement/backend/src/kj_atlas_api/persistence_shapes.py",
    '    "guest_auth_sessions.revoked_at": TIMESTAMP,\n',
    '''    "guest_auth_sessions.revoked_at": TIMESTAMP,\n    "guest_redeem_states.state_key_hash": _bounded(\n        256, "keyed hash of a one-time guest invitation redeem handle"\n    ),\n    "guest_redeem_states.tenant_id": INTERNAL_ID,\n    "guest_redeem_states.guest_principal_id": INTERNAL_ID,\n    "guest_redeem_states.created_at": TIMESTAMP,\n    "guest_redeem_states.expires_at": TIMESTAMP,\n    "guest_redeem_states.consumed_at": TIMESTAMP,\n''',
)

replace_once(
    "03_Implement/backend/tests/test_alembic_lineage.py",
    '    assert heads == ["20260906_0034"], (\n',
    '    assert heads == ["20260907_0035"], (\n',
)
replace_once(
    "03_Implement/backend/tests/test_alembic_lineage.py",
    '    assert "20260906_0034" in history_ids\n',
    '    assert "20260906_0034" in history_ids\n    assert "20260907_0035" in history_ids\n',
)
replace_once(
    "03_Implement/backend/tests/test_alembic_lineage.py",
    '        history_ids.index("20260906_0034")\n',
    '        history_ids.index("20260907_0035")\n        < history_ids.index("20260906_0034")\n',
)

replace_once(
    "03_Implement/backend/src/kj_atlas_api/main.py",
    "from kj_atlas_api.guest_auth_state import DatabaseGuestAuthSessionStore\n",
    "from kj_atlas_api.guest_auth_state import DatabaseGuestAuthSessionStore\nfrom kj_atlas_api.guest_redeem import DatabaseGuestRedeemStateStore\n",
)
replace_once(
    "03_Implement/backend/src/kj_atlas_api/main.py",
    "from kj_atlas_api.routes.inquiry_bundles import router as inquiry_bundles_router\n",
    "from kj_atlas_api.routes.inquiry_bundles import router as inquiry_bundles_router\nfrom kj_atlas_api.routes.guest_session import router as guest_session_router\n",
)
replace_once(
    "03_Implement/backend/src/kj_atlas_api/main.py",
    "        _guest_auth_session_store.preflight()\n",
    "        _guest_auth_session_store.preflight()\n        _guest_redeem_state_store.preflight()\n",
)
replace_once(
    "03_Implement/backend/src/kj_atlas_api/main.py",
    "_guest_auth_session_store = DatabaseGuestAuthSessionStore(SessionLocal)\n",
    "_guest_auth_session_store = DatabaseGuestAuthSessionStore(SessionLocal)\n_guest_redeem_state_store = DatabaseGuestRedeemStateStore(SessionLocal)\n",
)
replace_once(
    "03_Implement/backend/src/kj_atlas_api/main.py",
    "    app.state.guest_auth_session_hash_key = _saas_auth_session_hash_key\n",
    "    app.state.guest_auth_session_hash_key = _saas_auth_session_hash_key\n    app.state.guest_redeem_state_store = _guest_redeem_state_store\n    # Domain separation in guest_redeem.py makes key reuse cryptographically distinct.\n    app.state.guest_redeem_state_hash_key = _saas_auth_session_hash_key\n    # guest_identity_verifier is deliberately supplied by a deployment adapter;\n    # member VerifiedTenantClaim / tenant_identity_providers are not a guest fallback.\n",
)
replace_once(
    "03_Implement/backend/src/kj_atlas_api/main.py",
    "app.include_router(session_router)\n",
    "app.include_router(session_router)\napp.include_router(guest_session_router)\n",
)

print("R2b transformation applied")
