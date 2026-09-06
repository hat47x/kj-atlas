from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BACKEND = ROOT / "03_Implement/backend"


def replace(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise RuntimeError(f"anchor not found in {path}: {old[:120]!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


trusted = BACKEND / "src/kj_atlas_api/trusted_auth_edge.py"
replace(
    trusted,
    '''@dataclass(frozen=True, slots=True)
class JwtIdentityError(Exception):
    """Identity layer error — opaque to the caller (ADR-0063 D6)."""

    status_code: int
    code: str


def _resolve_identity_provider''',
    '''@dataclass(frozen=True, slots=True)
class JwtIdentityError(Exception):
    """Identity layer error — opaque to the caller (ADR-0063 D6)."""

    status_code: int
    code: str


@dataclass(frozen=True, slots=True)
class VerifiedOidcToken:
    """Cryptographically verified provider token, before any tenant mapping.

    This is intentionally narrower than ``VerifiedTenantClaim``.  Guest
    admission may consume issuer/subject evidence without inheriting a receiving
    tenant's IdP trust, membership, or provisioning semantics.
    """

    provider: IdentityProviderRow
    claims: dict[str, object]
    subject: str


def _resolve_identity_provider''',
)

anchor = '''def _resolve_subject_to_user_id(db: Session, provider_id: str, subject: str) -> str | None:
'''
insert = '''def _jwks_keys_for_provider(
    *,
    jwks_store: JwksStore,
    provider: IdentityProviderRow,
) -> list[dict[str, object]]:
    """Return cached or freshly fetched keys for a globally configured IdP."""
    if not jwks_store.needs_refresh(provider.id):
        cached = jwks_store.get(provider.id)
        if cached is not None:
            return cached

    if not jwks_store.can_force_refresh(provider.id):
        stale = jwks_store.get(provider.id)
        if stale is not None:
            return stale
        raise JwtIdentityError(status_code=503, code="jwks_unavailable")

    try:
        keys = _fetch_jwks(provider.jwks_uri)
        jwks_store.set(provider.id, keys)
        return keys
    except OSError:
        jwks_store.set_fresh_failure(provider.id)
        stale = jwks_store.get(provider.id)
        if stale is not None:
            return stale
        raise JwtIdentityError(status_code=503, code="jwks_unavailable") from None


def verify_configured_oidc_token(
    *,
    db: Session,
    token: str,
    jwks_store: JwksStore,
) -> VerifiedOidcToken:
    """Verify a configured OIDC token without resolving user or tenant trust.

    ``IdentityProviderRow`` is the global cryptographic provider registry.  This
    function deliberately stops before ``UserIdentityRow``,
    ``TenantIdentityProviderRow``, ``TenantMembershipRow`` and
    ``VerifiedTenantClaim`` so guest admission can reuse the hardened JWT/JWKS
    verifier without becoming a tenant member.
    """
    try:
        claims_unverified: dict[str, object] = jwt.decode(
            token,
            options={"verify_signature": False},
            algorithms=list(_jwt_algorithms()),
        )
    except jwt.PyJWTError:
        raise JwtIdentityError(status_code=401, code="invalid_token") from None

    issuer = claims_unverified.get("iss")
    if not isinstance(issuer, str):
        raise JwtIdentityError(status_code=401, code="invalid_token")
    aud_values = _normalize_audience(claims_unverified.get("aud"))
    if not aud_values:
        raise JwtIdentityError(status_code=401, code="invalid_token")

    provider = None
    matched_audience = ""
    for audience in aud_values:
        provider = _resolve_identity_provider(db, issuer, audience)
        if provider is not None:
            matched_audience = audience
            break
    if provider is None:
        logger.info("auth edge: unknown provider issuer=%s", issuer)
        raise JwtIdentityError(status_code=401, code="unknown_provider")

    verified = _verify_jwt(
        token,
        _jwks_keys_for_provider(jwks_store=jwks_store, provider=provider),
        issuer,
        matched_audience,
    )
    subject = verified.get("sub")
    if not isinstance(subject, str) or not subject:
        raise JwtIdentityError(status_code=401, code="invalid_token")
    return VerifiedOidcToken(provider=provider, claims=verified, subject=subject)


'''
replace(trusted, anchor, insert + anchor)

write(
    BACKEND / "src/kj_atlas_api/guest_identity_verifier.py",
    '''"""ADR-0080 D1 guest identity verification adapter.

The adapter reuses the hardened configured OIDC JWT/JWKS verifier but stops
before member provisioning and receiving-tenant IdP trust.  A guest therefore
proves an external identity without becoming a TenantMembership row or relying
on TenantIdentityProviderRow.
"""

from __future__ import annotations

import logging
from collections.abc import Callable

from sqlalchemy.orm import Session

from kj_atlas_api.guest_redeem import (
    GuestIdentityVerificationError,
    GuestIdentityVerificationUnavailableError,
    VerifiedGuestIdentity,
)
from kj_atlas_api.jwks_store import JwksStore
from kj_atlas_api.trusted_auth_edge import JwtIdentityError, verify_configured_oidc_token

logger = logging.getLogger(__name__)
_ALLOWED_VERIFICATION_METHODS = frozenset({"home_org_idp", "personal_account"})


class DatabaseJwtGuestIdentityVerifier:
    """Verify guest OIDC/broker JWTs without resolving member tenant context."""

    def __init__(
        self,
        *,
        session_factory: Callable[[], Session],
        jwks_store: JwksStore,
    ) -> None:
        self._session_factory = session_factory
        self._jwks_store = jwks_store

    def verify_identity(
        self,
        *,
        credential: str,
        verification_method: str,
    ) -> VerifiedGuestIdentity:
        if verification_method not in _ALLOWED_VERIFICATION_METHODS:
            raise GuestIdentityVerificationError("unsupported guest verification method")
        token = credential.strip()
        if not token or token != credential:
            raise GuestIdentityVerificationError("invalid guest identity credential")

        try:
            with self._session_factory() as db:
                verified = verify_configured_oidc_token(
                    db=db,
                    token=token,
                    jwks_store=self._jwks_store,
                )
        except JwtIdentityError as exc:
            if exc.status_code >= 500:
                logger.warning("guest identity provider verification unavailable")
                raise GuestIdentityVerificationUnavailableError(
                    "guest identity provider verification unavailable"
                ) from None
            logger.info("guest identity verification rejected")
            raise GuestIdentityVerificationError("guest identity verification failed") from None

        return VerifiedGuestIdentity(
            issuer=verified.provider.issuer,
            subject=verified.subject,
        )
''',
)

guest_redeem = BACKEND / "src/kj_atlas_api/guest_redeem.py"
replace(
    guest_redeem,
    '''class GuestIdentityVerificationError(ValueError):
    """Trusted guest identity verification failed."""


@dataclass''',
    '''class GuestIdentityVerificationError(ValueError):
    """Trusted guest identity verification rejected the presented credential."""


class GuestIdentityVerificationUnavailableError(RuntimeError):
    """Trusted guest identity verification infrastructure is unavailable."""


@dataclass''',
)

route = BACKEND / "src/kj_atlas_api/routes/guest_session.py"
replace(
    route,
    '''from kj_atlas_api.guest_redeem import (
    GuestIdentityVerificationError,
    GuestRedeemError,
)''',
    '''from kj_atlas_api.guest_redeem import (
    GuestIdentityVerificationError,
    GuestIdentityVerificationUnavailableError,
    GuestRedeemError,
)''',
)
replace(
    route,
    '''    except (GuestRedeemError, GuestIdentityVerificationError):
        raise HTTPException(
            status_code=401,
            detail={"code": "guest_redeem_invalid", "message": "Guest sign-in failed."},
        ) from None
    except Exception:
''',
    '''    except (GuestRedeemError, GuestIdentityVerificationError):
        raise HTTPException(
            status_code=401,
            detail={"code": "guest_redeem_invalid", "message": "Guest sign-in failed."},
        ) from None
    except GuestIdentityVerificationUnavailableError:
        raise HTTPException(
            status_code=503,
            detail={
                "code": "guest_identity_verification_unavailable",
                "message": "Guest identity verification is unavailable.",
            },
        ) from None
    except Exception:
''',
)

main = BACKEND / "src/kj_atlas_api/main.py"
replace(
    main,
    '''from kj_atlas_api.guest_auth_state import DatabaseGuestAuthSessionStore
from kj_atlas_api.guest_redeem import DatabaseGuestRedeemStateStore
''',
    '''from kj_atlas_api.guest_auth_state import DatabaseGuestAuthSessionStore
from kj_atlas_api.guest_identity_verifier import DatabaseJwtGuestIdentityVerifier
from kj_atlas_api.guest_redeem import DatabaseGuestRedeemStateStore
''',
)
replace(
    main,
    '''    app.state.guest_redeem_state_store = _guest_redeem_state_store
    # Domain separation in guest_redeem.py makes key reuse cryptographically distinct.
    app.state.guest_redeem_state_hash_key = _saas_auth_session_hash_key
    # guest_identity_verifier is deliberately supplied by a deployment adapter;
    # member VerifiedTenantClaim / tenant_identity_providers are not a guest fallback.

    install_trusted_saas_runtime(
''',
    '''    app.state.guest_redeem_state_store = _guest_redeem_state_store
    # Domain separation in guest_redeem.py makes key reuse cryptographically distinct.
    app.state.guest_redeem_state_hash_key = _saas_auth_session_hash_key
    # R2c shares only the hardened provider/JWKS cache with member auth.  Guest
    # verification stops before user provisioning, tenant IdP trust and membership.
    _shared_jwks_store = JwksStore()
    app.state.guest_identity_verifier = DatabaseJwtGuestIdentityVerifier(
        session_factory=SessionLocal,
        jwks_store=_shared_jwks_store,
    )

    install_trusted_saas_runtime(
''',
)
replace(
    main,
    '''            identity_context_resolver=JwtSaasIdentityContextResolver(
                jwks_store=JwksStore(),
''',
    '''            identity_context_resolver=JwtSaasIdentityContextResolver(
                jwks_store=_shared_jwks_store,
''',
)

write(
    BACKEND / "tests/test_guest_identity_verifier.py",
    '''from __future__ import annotations

import base64
import json
import time
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import jwt
import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from kj_atlas_api.db import get_db
from kj_atlas_api.guest_admission_models import GuestDocumentGrantRow, GuestPrincipalRow
from kj_atlas_api.guest_admission_repository import GuestAdmissionRepository
from kj_atlas_api.guest_auth_state import DatabaseGuestAuthSessionStore
from kj_atlas_api.guest_identity_verifier import DatabaseJwtGuestIdentityVerifier
from kj_atlas_api.guest_redeem import (
    DatabaseGuestRedeemStateStore,
    GuestIdentityVerificationError,
    GuestIdentityVerificationUnavailableError,
)
from kj_atlas_api.jwks_store import JwksStore
from kj_atlas_api.models import (
    Base,
    DocumentRow,
    IdentityProviderRow,
    TenantIdentityProviderRow,
    TenantMembershipRow,
    TenantRow,
    UserIdentityRow,
)
from kj_atlas_api.routes.docs import router as docs_router
from kj_atlas_api.routes.guest_session import router as guest_session_router

NOW = datetime.now(timezone.utc).replace(microsecond=0)
TS = NOW.isoformat()
ISSUER = "https://personal-idp.example.test"
AUDIENCE = "kj-atlas-guest"
STATE_HASH_KEY = b"guest-r2c-state-hash-key-0123456789"
SESSION_HASH_KEY = b"guest-r2c-session-hash-key-0123456"


def _b64url(value: int) -> str:
    length = (value.bit_length() + 7) // 8
    return base64.urlsafe_b64encode(value.to_bytes(length, "big")).rstrip(b"=").decode()


def _key_pair() -> tuple[rsa.RSAPrivateKey, dict[str, object]]:
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    numbers = private_key.public_key().public_numbers()
    return private_key, {
        "kty": "RSA",
        "kid": "guest-r2c-key",
        "use": "sig",
        "alg": "RS256",
        "n": _b64url(numbers.n),
        "e": _b64url(numbers.e),
    }


def _pem(private_key: rsa.RSAPrivateKey) -> str:
    return private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode()


def _token(
    private_key: rsa.RSAPrivateKey,
    *,
    issuer: str = ISSUER,
    audience: str = AUDIENCE,
    subject: str = "guest-subject-1",
) -> str:
    now = int(time.time())
    return jwt.encode(
        {
            "iss": issuer,
            "aud": audience,
            "sub": subject,
            "iat": now - 5,
            "exp": now + 3600,
        },
        _pem(private_key),
        algorithm="RS256",
        headers={"kid": "guest-r2c-key"},
    )


def _payload(doc_id: str) -> dict[str, object]:
    return {
        "version": 1,
        "id": doc_id,
        "title": doc_id,
        "createdAt": TS,
        "updatedAt": TS,
        "transform": {"panX": 0, "panY": 0, "zoom": 1},
        "cards": [],
        "edges": [],
        "islands": [],
    }


@pytest.fixture
def guest_env(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path}/guest-r2c.db")
    factory = sessionmaker(bind=engine, class_=Session, expire_on_commit=False)
    Base.metadata.create_all(engine)
    private_key, jwk = _key_pair()

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
            IdentityProviderRow(
                id="guest-idp",
                issuer=ISSUER,
                audience=AUDIENCE,
                protocol="oidc",
                jwks_uri="https://personal-idp.example.test/.well-known/jwks.json",
                lifecycle_state="active",
                created_at=TS,
                updated_at=TS,
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

    jwks = JwksStore()
    jwks.set("guest-idp", [jwk])
    verifier = DatabaseJwtGuestIdentityVerifier(
        session_factory=factory,
        jwks_store=jwks,
    )
    redeem_store = DatabaseGuestRedeemStateStore(factory)
    auth_store = DatabaseGuestAuthSessionStore(factory)
    raw_state = redeem_store.issue_redeem_state(
        tenant_id="tenant-a",
        guest_principal_id="guest-1",
        hash_key=STATE_HASH_KEY,
        now=NOW,
    )

    app = FastAPI()
    app.include_router(guest_session_router)
    app.include_router(docs_router)
    app.state.runtime_profile = "evaluation"
    app.state.guest_redeem_state_store = redeem_store
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
    yield factory, private_key, jwk, verifier, raw_state, TestClient(app)
    engine.dispose()


def _redeem(client: TestClient, raw_state: str, token: str):
    return client.post(
        "/session/guest/redeem",
        json={"state": raw_state, "identityCredential": token},
    )


def _guest_cookie(response) -> dict[str, str]:
    return {"Kj-Atlas-Guest-Session": response.cookies["Kj-Atlas-Guest-Session"]}


def test_real_signed_guest_token_redeems_without_member_or_tenant_idp_trust(guest_env) -> None:
    factory, private_key, _, _, raw_state, client = guest_env
    with client:
        response = _redeem(client, raw_state, _token(private_key))
        assert response.status_code == 200
        read = client.get("/docs/doc-granted", cookies=_guest_cookie(response))
        assert read.status_code == 200

    with factory() as db:
        principal = db.get(GuestPrincipalRow, ("tenant-a", "guest-1"))
        assert principal is not None
        assert principal.status == "active"
        assert principal.verified_issuer == ISSUER
        assert principal.verified_subject == "guest-subject-1"
        assert db.scalars(select(TenantIdentityProviderRow)).all() == []
        assert db.scalars(select(TenantMembershipRow)).all() == []
        assert db.scalars(select(UserIdentityRow)).all() == []


def test_real_provider_journey_observes_host_grant_revoke_on_next_request(guest_env) -> None:
    factory, private_key, _, _, raw_state, client = guest_env
    with client:
        response = _redeem(client, raw_state, _token(private_key))
        assert response.status_code == 200
        cookie = _guest_cookie(response)
        assert client.get("/docs/doc-granted", cookies=cookie).status_code == 200
        with factory() as db:
            repo = GuestAdmissionRepository(db, tenant_id="tenant-a")
            assert repo.revoke_document_grant(
                guest_principal_id="guest-1",
                doc_id="doc-granted",
                revoked_at=(NOW + timedelta(minutes=1)).isoformat(),
            )
            db.commit()
        assert client.get("/docs/doc-granted", cookies=cookie).status_code == 404


def test_real_provider_journey_observes_host_principal_revoke_on_next_request(guest_env) -> None:
    factory, private_key, _, _, raw_state, client = guest_env
    with client:
        response = _redeem(client, raw_state, _token(private_key))
        assert response.status_code == 200
        cookie = _guest_cookie(response)
        with factory() as db:
            repo = GuestAdmissionRepository(db, tenant_id="tenant-a")
            assert repo.revoke_guest_principal(
                guest_principal_id="guest-1",
                revoked_at=(NOW + timedelta(minutes=1)).isoformat(),
            )
            db.commit()
        assert client.get("/docs/doc-granted", cookies=cookie).status_code == 401


def test_home_org_and_personal_account_methods_use_same_tenant_independent_crypto_boundary(
    guest_env,
) -> None:
    _, private_key, _, verifier, _, _ = guest_env
    token = _token(private_key)
    personal = verifier.verify_identity(
        credential=token,
        verification_method="personal_account",
    )
    home_org = verifier.verify_identity(
        credential=token,
        verification_method="home_org_idp",
    )
    assert personal == home_org
    assert personal.issuer == ISSUER


def test_unknown_verification_method_fails_closed(guest_env) -> None:
    _, private_key, _, verifier, _, _ = guest_env
    with pytest.raises(GuestIdentityVerificationError):
        verifier.verify_identity(
            credential=_token(private_key),
            verification_method="receiving_tenant_membership",
        )


def test_unknown_provider_and_wrong_audience_fail_closed(guest_env) -> None:
    _, private_key, _, verifier, _, _ = guest_env
    with pytest.raises(GuestIdentityVerificationError):
        verifier.verify_identity(
            credential=_token(private_key, issuer="https://unknown.example.test"),
            verification_method="personal_account",
        )
    with pytest.raises(GuestIdentityVerificationError):
        verifier.verify_identity(
            credential=_token(private_key, audience="wrong-audience"),
            verification_method="personal_account",
        )


def test_invalid_signature_fails_closed(guest_env) -> None:
    _, _, _, verifier, _, _ = guest_env
    attacker_key, _ = _key_pair()
    with pytest.raises(GuestIdentityVerificationError):
        verifier.verify_identity(
            credential=_token(attacker_key),
            verification_method="personal_account",
        )


def test_inactive_provider_fails_closed(guest_env) -> None:
    factory, private_key, _, verifier, _, _ = guest_env
    with factory() as db:
        provider = db.get(IdentityProviderRow, "guest-idp")
        assert provider is not None
        provider.lifecycle_state = "disabled"
        db.commit()
    with pytest.raises(GuestIdentityVerificationError):
        verifier.verify_identity(
            credential=_token(private_key),
            verification_method="personal_account",
        )


def test_jwks_outage_is_distinct_from_bad_identity(guest_env) -> None:
    factory, private_key, _, _, _, _ = guest_env
    verifier = DatabaseJwtGuestIdentityVerifier(
        session_factory=factory,
        jwks_store=JwksStore(),
    )
    with patch("kj_atlas_api.trusted_auth_edge._fetch_jwks", side_effect=OSError):
        with pytest.raises(GuestIdentityVerificationUnavailableError):
            verifier.verify_identity(
                credential=_token(private_key),
                verification_method="personal_account",
            )
''',
)

issue = ROOT / "01_Plans/issues/issue-PGM-ITER-05-03-cross-tenant-guest-admission-primitive-requirements.md"
replace(
    issue,
    '''### R2cに残す境界

- `ADR-0080` D1=A1/A2の**実provider adapter**（home organization IdP / general personal account）をproduction deploymentへ接続し、署名/JWKS/issuer/audience等の検証を実際のprovider contractで固定すること。R2bはguest専用trusted verifier interfaceとfail-closed wiringを実装したが、member用OAuth adapterをguestへ流用してはいない。
- provider redirect/callback方式を採る場合は、R2bのone-time stateをcallback correlationへ接続し、provider固有nonce/PKCE等を必要に応じて追加すること。`identityCredential`を受ける現在のHTTP境界はtrusted verifier adapterへの最小交換面であり、特定providerのOAuth UI完了を意味しない。
- guest session logout / explicit revokeの公開境界が必要なら、そのCSRF・cookie属性・監査契約をmember cookieとは別に固定すること。
- R2aでread-onlyに閉じたguest writeを将来開く場合は、document grantのread/write意味、CSRF、PDPとの責務分離を別途設計してから扱うこと。
''',
    '''### R2c: configured OIDC/JWKS provider → guest-only verified identity（2026-09-07）

`lane-c/guest-idp-verifier-r2c-20260907`で、R2bのdeployment-adapter空所へproduction用の署名検証境界を接続する。

- member authで既に固定されているRS256/ES256 allowlist、JWKS取得・cache、issuer/audience/exp/iat/nbf/signature検証を共通の`verify_configured_oidc_token()`として利用する。暗号検証規則をguest専用に作り直さない。
- guest verifierが参照するのはglobalな`IdentityProviderRow`のprovider設定だけであり、受入先tenantの`TenantIdentityProviderRow`、`UserIdentityRow`、`TenantMembershipRow`、member `VerifiedTenantClaim`は解決しない。したがって「受入先tenant自身のIdPに属すること」をguest認証条件へ戻さない。
- host-created stateに固定された`home_org_idp` / `personal_account`の両verification methodを同じguest-only crypto boundaryで受け、検証済みissuer/subjectだけをR2bへ返す。未知methodはfail closedする。
- provider/JWKS障害はcredential不正と区別して503、署名・issuer・audience・provider不一致は401へ閉じる。
- 実署名RS256 tokenを使うHTTP integrationで、tenant IdP trust/member rowsが0件のままredeem→guest cookie→exact-grant readへ到達し、その同一sessionに対するhost側grant revokeは次GETで404、principal revokeは次GETで401となることを固定する。

R2cが固定するのは**configured OIDCまたはbroker-issued JWTの検証境界**である。provider固有のredirect UI、authorization-code exchange、nonce/PKCEをkj-atlas自身が直接担うことや、opaque OAuth tokenしか提供しない全providerを同一adapterで直接処理することまでは主張しない。それらはdeployment broker/provider adapterの責務であり、guest admissionのtenant-independent trust primitiveとは分離する。

### 親issue外に残す将来境界

- provider redirect/callbackをkj-atlas自身が直接実装する場合のprovider固有nonce/PKCE/UI。
- guest session logout / explicit revokeの公開境界と、そのCSRF・監査契約。
- guest writeを将来開く場合のgrant read/write意味、CSRF、PDPとの責務分離。
''',
)
replace(
    issue,
    '''- [ ] AC-3: ADR承認後、個人単位・IdP不問の招待・許可プリミティブが実装され、既定拒否・既定ゼロ件がintegration testで固定される。— R1でstorage/repository/RLS、R2aでserver-owned guest session→実HTTP exact document read、R2bでhost-bound one-time redeem state→guest専用verified identity→session発行まで固定した。ただしproductionでhome-org IdP / general personal accountを実検証するprovider adapterはまだ未接続であり、「IdP不問の受入journey」全体の完了とはまだ扱わない。
- [ ] AC-4: 招待の取り消し・失効が、相手側（招待された個人の状態）と無関係にテナント側から単独で実行できることがtestで固定される。— R1のrepository predicate、R2aのlive-cookie HTTP revoke挙動に加え、R2bでhost-bound redeem→session入口まで到達した。revokeの技術挙動自体は固定済みだが、AC-3と同じproduction provider journeyを通したend-to-end受入・取消証跡がまだないため、親issue closeoutまでは未完了として維持する。
''',
    '''- [x] AC-3: ADR承認後、個人単位・IdP不問の招待・許可プリミティブが実装され、既定拒否・既定ゼロ件がintegration testで固定される。— R1のstorage/repository/RLS、R2aのserver-owned guest session→exact document read、R2bのhost-bound one-time redeem、R2cのconfigured OIDC/JWKS実署名検証を縦に接続した。受入先tenantの`TenantIdentityProviderRow`・membership・member identityを作らず、実署名token→guest cookie→exact grantだけが200となるintegration testで固定する。
- [x] AC-4: 招待の取り消し・失効が、相手側（招待された個人の状態）と無関係にテナント側から単独で実行できることがtestで固定される。— R1/R2aのpredicate/live-cookie証跡に加え、R2cの実署名provider journeyでredeem済み同一sessionに対するhost側grant revoke→次GET 404、principal revoke→次GET 401を固定する。
''',
)
replace(
    issue,
    '''- R2b verification: GitHub Actions run `34046511190`（HTTP/repository + PostgreSQL 16 restricted runtime role + docs/diff hygiene）''',
    '''- R2b verification: GitHub Actions run `34046511190`（HTTP/repository + PostgreSQL 16 restricted runtime role + docs/diff hygiene）
- R2c verification: branch CIの実署名JWT + guest redeem/read/revoke + trusted-auth regressions + docs/diff hygieneを参照''',
)

print("R2c transformation applied")
