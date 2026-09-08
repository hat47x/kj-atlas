from __future__ import annotations

import os
import subprocess
import sys
from collections.abc import Iterator
from pathlib import Path
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, delete, select, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from kj_atlas_api.db import _normalize_database_url
from kj_atlas_api.guest_admission_models import GuestDocumentGrantRow, GuestPrincipalRow
from kj_atlas_api.models import DocumentRow, TenantRow
from kj_atlas_api.tenant_db_guard import apply_database_tenant_id

RUN_RLS_TESTS_ENV = "KJ_ATLAS_RUN_PG_RLS_TESTS"
ADMIN_DATABASE_URL_ENV = "KJ_ATLAS_DATABASE_URL"
RUNTIME_DATABASE_URL_ENV = "KJ_ATLAS_TEST_POSTGRES_RUNTIME_DATABASE_URL"
BACKEND_DIR = Path(__file__).resolve().parents[1]
TS = "2026-09-06T12:00:00Z"


@pytest.fixture(scope="module")
def postgres_guest_engines() -> Iterator[tuple[Engine, Engine]]:
    if os.getenv(RUN_RLS_TESTS_ENV) != "1":
        pytest.skip(f"set {RUN_RLS_TESTS_ENV}=1 to exercise PostgreSQL guest RLS")
    admin_url = os.getenv(ADMIN_DATABASE_URL_ENV, "")
    runtime_url = os.getenv(RUNTIME_DATABASE_URL_ENV, "")
    if not admin_url.startswith("postgresql") or not runtime_url.startswith("postgresql"):
        pytest.fail("guest RLS verification requires PostgreSQL admin and runtime URLs")
    if admin_url == runtime_url:
        pytest.fail("guest RLS verification requires distinct admin/runtime credentials")

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
        with runtime_engine.connect() as connection:
            posture = connection.execute(
                text("SELECT rolsuper, rolbypassrls FROM pg_roles WHERE rolname = current_user")
            ).one()
            assert posture.rolsuper is False
            assert posture.rolbypassrls is False
            assert connection.execute(text("SHOW row_security")).scalar_one() == "on"
        yield admin_engine, runtime_engine
    finally:
        runtime_engine.dispose()
        admin_engine.dispose()


@pytest.mark.postgres
def test_guest_tables_are_forced_rls_and_fail_closed_without_context(
    postgres_guest_engines: tuple[Engine, Engine],
) -> None:
    admin_engine, runtime_engine = postgres_guest_engines
    expected = {"guest_principals", "guest_document_grants"}
    with admin_engine.connect() as connection:
        posture = {
            row.relname: (row.relrowsecurity, row.relforcerowsecurity)
            for row in connection.execute(
                text(
                    "SELECT c.relname, c.relrowsecurity, c.relforcerowsecurity "
                    "FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace "
                    "WHERE n.nspname = 'public' AND c.relname IN "
                    "('guest_principals', 'guest_document_grants')"
                )
            )
        }
        policies = {
            row.tablename: (row.qual, row.with_check)
            for row in connection.execute(
                text(
                    "SELECT tablename, qual, with_check FROM pg_policies "
                    "WHERE schemaname = 'public' AND tablename IN "
                    "('guest_principals', 'guest_document_grants')"
                )
            )
        }
    assert set(posture) == expected
    assert all(enabled and forced for enabled, forced in posture.values())
    assert set(policies) == expected
    for qual, with_check in policies.values():
        assert "current_setting('kj_atlas.tenant_id'" in qual
        assert "current_setting('kj_atlas.tenant_id'" in with_check

    with runtime_engine.connect() as connection:
        assert connection.execute(text("SELECT count(*) FROM guest_principals")).scalar_one() == 0
        assert connection.execute(text("SELECT count(*) FROM guest_document_grants")).scalar_one() == 0


@pytest.mark.postgres
def test_guest_rows_are_tenant_isolated_and_cross_tenant_write_is_blocked(
    postgres_guest_engines: tuple[Engine, Engine],
) -> None:
    admin_engine, runtime_engine = postgres_guest_engines
    suffix = uuid4().hex
    tenant_a = f"guest-a-{suffix}"
    tenant_b = f"guest-b-{suffix}"
    doc_a = f"doc-a-{suffix}"
    doc_b = f"doc-b-{suffix}"
    guest_a = f"principal-a-{suffix}"
    guest_b = f"principal-b-{suffix}"

    with Session(admin_engine) as db:
        db.add_all(
            [
                TenantRow(id=tenant_a, display_name=tenant_a, lifecycle_state="active", created_at=TS, updated_at=TS),
                TenantRow(id=tenant_b, display_name=tenant_b, lifecycle_state="active", created_at=TS, updated_at=TS),
            ]
        )
        db.commit()

    for tenant_id, doc_id, principal_id in (
        (tenant_a, doc_a, guest_a),
        (tenant_b, doc_b, guest_b),
    ):
        with Session(admin_engine) as db:
            apply_database_tenant_id(db=db, tenant_id=tenant_id)
            db.add(DocumentRow(tenant_id=tenant_id, id=doc_id, version=1, updated_at=TS, payload_json="{}"))
            db.flush()
            db.add(
                GuestPrincipalRow(
                    tenant_id=tenant_id,
                    guest_principal_id=principal_id,
                    invited_email=f"{principal_id}@example.test",
                    status="active",
                    verification_method="personal_account",
                    verified_issuer="https://accounts.example.test",
                    verified_subject=f"subject-{principal_id}",
                    created_by="host-admin",
                    created_at=TS,
                    expires_at="2026-09-07T12:00:00Z",
                    redeemed_at=TS,
                    revoked_at=None,
                )
            )
            db.flush()
            db.add(
                GuestDocumentGrantRow(
                    tenant_id=tenant_id,
                    guest_principal_id=principal_id,
                    doc_id=doc_id,
                    granted_by="host-admin",
                    granted_at=TS,
                    revoked_at=None,
                )
            )
            db.commit()

    try:
        with Session(runtime_engine) as db:
            apply_database_tenant_id(db=db, tenant_id=tenant_a)
            principals = db.scalars(select(GuestPrincipalRow)).all()
            grants = db.scalars(select(GuestDocumentGrantRow)).all()
            assert [(row.tenant_id, row.guest_principal_id) for row in principals] == [(tenant_a, guest_a)]
            assert [(row.tenant_id, row.doc_id) for row in grants] == [(tenant_a, doc_a)]
            db.commit()

        with Session(runtime_engine) as db:
            apply_database_tenant_id(db=db, tenant_id=tenant_a)
            with pytest.raises(SQLAlchemyError):
                db.add(
                    GuestDocumentGrantRow(
                        tenant_id=tenant_b,
                        guest_principal_id=guest_b,
                        doc_id=doc_b,
                        granted_by="tenant-a-attacker",
                        granted_at=TS,
                        revoked_at=None,
                    )
                )
                db.flush()
            db.rollback()

        # Transaction-local scope must disappear on pool reuse.
        with Session(runtime_engine) as db:
            assert db.scalars(select(GuestPrincipalRow)).all() == []
            assert db.scalars(select(GuestDocumentGrantRow)).all() == []
    finally:
        for tenant_id in (tenant_a, tenant_b):
            with Session(admin_engine) as db:
                apply_database_tenant_id(db=db, tenant_id=tenant_id)
                db.execute(delete(GuestDocumentGrantRow).where(GuestDocumentGrantRow.tenant_id == tenant_id))
                db.execute(delete(GuestPrincipalRow).where(GuestPrincipalRow.tenant_id == tenant_id))
                db.execute(delete(DocumentRow).where(DocumentRow.tenant_id == tenant_id))
                db.commit()
        with Session(admin_engine) as db:
            db.execute(delete(TenantRow).where(TenantRow.id.in_((tenant_a, tenant_b))))
            db.commit()
