from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

PG_TEST = ROOT / "03_Implement/backend/tests/test_guest_redeem_postgres.py"
PG_TEST.write_text(
    '''from __future__ import annotations

import os
import subprocess
import sys
from collections.abc import Iterator
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, delete, select, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from kj_atlas_api.auth_session_hash import derive_session_key_hash
from kj_atlas_api.db import _normalize_database_url
from kj_atlas_api.guest_admission_models import GuestPrincipalRow
from kj_atlas_api.guest_auth_session_models import GuestAuthSessionRow
from kj_atlas_api.guest_redeem import DatabaseGuestRedeemStateStore, VerifiedGuestIdentity
from kj_atlas_api.guest_redeem_state_models import GuestRedeemStateRow
from kj_atlas_api.models import TenantRow
from kj_atlas_api.tenant_db_guard import apply_database_tenant_id

RUN_RLS_TESTS_ENV = "KJ_ATLAS_RUN_PG_RLS_TESTS"
ADMIN_DATABASE_URL_ENV = "KJ_ATLAS_DATABASE_URL"
RUNTIME_DATABASE_URL_ENV = "KJ_ATLAS_TEST_POSTGRES_RUNTIME_DATABASE_URL"
BACKEND_DIR = Path(__file__).resolve().parents[1]
NOW = datetime(2026, 9, 7, 1, 0, tzinfo=timezone.utc)
ISSUER = "https://personal-idp.example.test"
STATE_HASH_KEY = b"postgres-guest-redeem-state-key-01"
SESSION_HASH_KEY = b"postgres-guest-session-key-00001"


@pytest.fixture(scope="module")
def postgres_guest_redeem_engines() -> Iterator[tuple[Engine, Engine]]:
    if os.getenv(RUN_RLS_TESTS_ENV) != "1":
        pytest.skip(f"set {RUN_RLS_TESTS_ENV}=1 to exercise PostgreSQL guest redeem state")
    admin_url = os.getenv(ADMIN_DATABASE_URL_ENV, "")
    runtime_url = os.getenv(RUNTIME_DATABASE_URL_ENV, "")
    if not admin_url.startswith("postgresql") or not runtime_url.startswith("postgresql"):
        pytest.fail("guest redeem verification requires PostgreSQL admin and runtime URLs")

    migration_env = os.environ.copy()
    migration_env[ADMIN_DATABASE_URL_ENV] = admin_url
    subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=BACKEND_DIR,
        env=migration_env,
        check=True,
    )
    admin_engine = create_engine(_normalize_database_url(admin_url))
    runtime_engine = create_engine(_normalize_database_url(runtime_url), pool_size=1, max_overflow=0)
    try:
        yield admin_engine, runtime_engine
    finally:
        runtime_engine.dispose()
        admin_engine.dispose()


@pytest.mark.postgres
def test_pre_tenant_redeem_state_returns_to_forced_rls_and_redeems_atomically(
    postgres_guest_redeem_engines: tuple[Engine, Engine],
) -> None:
    admin_engine, runtime_engine = postgres_guest_redeem_engines
    suffix = uuid4().hex
    tenant_id = f"guest-redeem-{suffix}"
    principal_id = f"principal-{suffix}"
    subject = f"subject-{suffix}"

    with admin_engine.connect() as connection:
        redeem_posture = connection.execute(
            text(
                "SELECT relrowsecurity, relforcerowsecurity FROM pg_class "
                "WHERE relname = 'guest_redeem_states'"
            )
        ).one()
        principal_posture = connection.execute(
            text(
                "SELECT relrowsecurity, relforcerowsecurity FROM pg_class "
                "WHERE relname = 'guest_principals'"
            )
        ).one()
    assert tuple(redeem_posture) == (False, False)
    assert tuple(principal_posture) == (True, True)

    with Session(admin_engine) as db:
        db.add(
            TenantRow(
                id=tenant_id,
                display_name=tenant_id,
                lifecycle_state="active",
                created_at=NOW.isoformat(),
                updated_at=NOW.isoformat(),
            )
        )
        db.commit()
    with Session(admin_engine) as db:
        apply_database_tenant_id(db=db, tenant_id=tenant_id)
        db.add(
            GuestPrincipalRow(
                tenant_id=tenant_id,
                guest_principal_id=principal_id,
                invited_email=f"{principal_id}@example.test",
                status="pending",
                verification_method="personal_account",
                verified_issuer=None,
                verified_subject=None,
                created_by="host-admin",
                created_at=NOW.isoformat(),
                expires_at=(NOW + timedelta(hours=2)).isoformat(),
                redeemed_at=None,
                revoked_at=None,
            )
        )
        db.commit()

    runtime_factory = sessionmaker(bind=runtime_engine, class_=Session, expire_on_commit=False)
    store = DatabaseGuestRedeemStateStore(runtime_factory)
    raw_state = ""
    try:
        with Session(runtime_engine) as db:
            assert db.get(GuestPrincipalRow, (tenant_id, principal_id)) is None

        raw_state = store.issue_redeem_state(
            tenant_id=tenant_id,
            guest_principal_id=principal_id,
            hash_key=STATE_HASH_KEY,
            now=NOW,
        )
        challenge = store.resolve_challenge(
            raw_state=raw_state,
            hash_key=STATE_HASH_KEY,
            now=NOW,
        )
        assert challenge.tenant_id == tenant_id
        assert challenge.guest_principal_id == principal_id
        assert challenge.verification_method == "personal_account"

        raw_session_id = store.redeem_verified_identity(
            raw_state=raw_state,
            hash_key=STATE_HASH_KEY,
            session_hash_key=SESSION_HASH_KEY,
            identity=VerifiedGuestIdentity(issuer=ISSUER, subject=subject),
            now=NOW,
        )
        session_hash = derive_session_key_hash(raw_session_id, key=SESSION_HASH_KEY)

        with Session(admin_engine) as db:
            state = db.scalar(
                select(GuestRedeemStateRow).where(GuestRedeemStateRow.tenant_id == tenant_id)
            )
            assert state is not None and state.consumed_at is not None
            session_row = db.get(GuestAuthSessionRow, session_hash)
            assert session_row is not None
            assert session_row.tenant_id == tenant_id
            assert session_row.guest_principal_id == principal_id
        with Session(admin_engine) as db:
            apply_database_tenant_id(db=db, tenant_id=tenant_id)
            principal = db.get(GuestPrincipalRow, (tenant_id, principal_id))
            assert principal is not None
            assert principal.status == "active"
            assert principal.verified_issuer == ISSUER
            assert principal.verified_subject == subject

        with pytest.raises(Exception):
            store.redeem_verified_identity(
                raw_state=raw_state,
                hash_key=STATE_HASH_KEY,
                session_hash_key=SESSION_HASH_KEY,
                identity=VerifiedGuestIdentity(issuer=ISSUER, subject=subject),
                now=NOW,
            )
    finally:
        with Session(admin_engine) as db:
            db.execute(delete(GuestAuthSessionRow).where(GuestAuthSessionRow.tenant_id == tenant_id))
            db.execute(delete(GuestRedeemStateRow).where(GuestRedeemStateRow.tenant_id == tenant_id))
            db.commit()
        with Session(admin_engine) as db:
            apply_database_tenant_id(db=db, tenant_id=tenant_id)
            db.execute(delete(GuestPrincipalRow).where(GuestPrincipalRow.tenant_id == tenant_id))
            db.commit()
        with Session(admin_engine) as db:
            db.execute(delete(TenantRow).where(TenantRow.id == tenant_id))
            db.commit()
''',
    encoding="utf-8",
)

issue = ROOT / "01_Plans/issues/issue-PGM-ITER-05-03-cross-tenant-guest-admission-primitive-requirements.md"
text = issue.read_text(encoding="utf-8")
start = text.index("### R2bに残す境界")
end = text.index("\n## 受入条件", start)
run_id = os.environ.get("GITHUB_RUN_ID", "<verification-run>")
replacement = f'''### R2b: host-bound redeem state → verified guest identity → guest session（2026-09-07）

`lane-c/guest-admission-redeem-r2b-20260906`で、R2aが残した「外部本人確認結果を、client自己申告のtenant/principalを信じずに招待へbindし、guest sessionへ交換する」入口を実装した。

- `guest_redeem_states`をpre-tenant authentication stateとして追加した。raw stateは返却時にだけ存在し、DB正本はdomain-separated keyed hashのみとする。stateは15分または招待期限の短い方で失効し、一度consumeしたstateは再利用できない。
- 公開`POST /session/guest/redeem`のrequest schemaは`state`と`identityCredential`だけを受け付け、`tenantId` / `guestPrincipalId` / `issuer` / `subject`等のclient自己申告を`extra=forbid`で拒否する。tenant・guest principal・verification methodはhost-created stateからのみ復元する。
- 本人確認結果はguest専用`VerifiedGuestIdentity(issuer, subject)`へ閉じ、member用`VerifiedTenantClaim`、`TenantMembershipRow`、`TenantIdentityProviderRow`へのfallbackを設けない。production verifierはdeployment adapterから明示注入する契約とし、未構成時は503でfail closedする。
- state rowを`FOR UPDATE`で一回性確認した後、pending principalのverified identity bind、`guest_auth_sessions` row発行、state consumeを**同一DB transaction**でcommitする。session persistence失敗を強制したintegration testではprincipal activation・state consume・session rowのすべてがrollbackされる。
- redeem成功後はR2aの`Kj-Atlas-Guest-Session`をそのまま利用し、既存exact document grantだけがreadを許可する。guest principalの存在だけでtenant内文書へ広がる経路は追加していない。
- SQLite HTTP integrationではstate非平文保存、redeem→cookie→exact grant GET、replay拒否、期限切れ拒否、identity verifier失敗、client tenant/principal/claim注入拒否、atomic rollback、membership/tenant-IdP行0件を固定した。
- PostgreSQL 16 restricted runtime roleでは、`guest_redeem_states`が意図したpre-tenant非RLS、`guest_principals`がFORCE RLSのままであることを確認し、state解決後だけtenant scopeへ戻ってprincipalをactivateし、state consumeとsession rowを同時commitできることを固定した。
- 最終verification run `{run_id}`でRuff、focused HTTP/repository tests、PostgreSQL 16、migration lineage、persistence shapes、`docs_check`、`git diff --check`を確認する。

### R2cに残す境界

- `ADR-0080` D1=A1/A2の**実provider adapter**（home organization IdP / general personal account）をproduction deploymentへ接続し、署名/JWKS/issuer/audience等の検証を実際のprovider contractで固定すること。R2bはguest専用trusted verifier interfaceとfail-closed wiringを実装したが、member用OAuth adapterをguestへ流用してはいない。
- provider redirect/callback方式を採る場合は、R2bのone-time stateをcallback correlationへ接続し、provider固有nonce/PKCE等を必要に応じて追加すること。`identityCredential`を受ける現在のHTTP境界はtrusted verifier adapterへの最小交換面であり、特定providerのOAuth UI完了を意味しない。
- guest session logout / explicit revokeの公開境界が必要なら、そのCSRF・cookie属性・監査契約をmember cookieとは別に固定すること。
- R2aでread-onlyに閉じたguest writeを将来開く場合は、document grantのread/write意味、CSRF、PDPとの責務分離を別途設計してから扱うこと。
'''
text = text[:start] + replacement + text[end:]
old_ac3 = "- [ ] AC-3: ADR承認後、個人単位・IdP不問の招待・許可プリミティブが実装され、既定拒否・既定ゼロ件がintegration testで固定される。— R1でstorage/repository/RLS、R2aでserver-owned guest session→実HTTP exact document readのdefault-zeroまで固定した。残りはD1の外部verified guest identityをhost-created invitationへ安全にbind/redeemし、guest sessionを発行するR2b入口。公開入口がない段階では「個人単位・IdP不問の受入journey」全体の完了とは扱わない。"
new_ac3 = "- [ ] AC-3: ADR承認後、個人単位・IdP不問の招待・許可プリミティブが実装され、既定拒否・既定ゼロ件がintegration testで固定される。— R1でstorage/repository/RLS、R2aでserver-owned guest session→実HTTP exact document read、R2bでhost-bound one-time redeem state→guest専用verified identity→session発行まで固定した。ただしproductionでhome-org IdP / general personal accountを実検証するprovider adapterはまだ未接続であり、「IdP不問の受入journey」全体の完了とはまだ扱わない。"
if old_ac3 not in text:
    raise RuntimeError("AC-3 baseline changed unexpectedly")
text = text.replace(old_ac3, new_ac3)
old_ac4 = "- [ ] AC-4: 招待の取り消し・失効が、相手側（招待された個人の状態）と無関係にテナント側から単独で実行できることがtestで固定される。— R1のrepository predicateに加え、R2aではgrant revoke→同じlive cookieの次GETが404、principal revoke→同じcookieの次GETが401となる実HTTP挙動まで固定済み。ただし外部IdPからsessionを発行する公開journey自体がR2b未実装のため、親issue closeoutまでは未完了として維持する。"
new_ac4 = "- [ ] AC-4: 招待の取り消し・失効が、相手側（招待された個人の状態）と無関係にテナント側から単独で実行できることがtestで固定される。— R1のrepository predicate、R2aのlive-cookie HTTP revoke挙動に加え、R2bでhost-bound redeem→session入口まで到達した。revokeの技術挙動自体は固定済みだが、AC-3と同じproduction provider journeyを通したend-to-end受入・取消証跡がまだないため、親issue closeoutまでは未完了として維持する。"
if old_ac4 not in text:
    raise RuntimeError("AC-4 baseline changed unexpectedly")
text = text.replace(old_ac4, new_ac4)
verification_anchor = "- R2a verification: GitHub Actions run `34039105022`（59 focused tests + docs/diff hygiene）"
if verification_anchor not in text:
    raise RuntimeError("verification baseline changed unexpectedly")
text = text.replace(
    verification_anchor,
    verification_anchor
    + f"\n- R2b verification: GitHub Actions run `{run_id}`（HTTP/repository + PostgreSQL 16 restricted runtime role + docs/diff hygiene）",
)
issue.write_text(text, encoding="utf-8")
print(f"R2b finalization patch applied for run {run_id}")
