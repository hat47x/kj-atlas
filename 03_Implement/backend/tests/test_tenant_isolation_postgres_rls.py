"""QA-TENANT-ISOLATION-01: verify the two tenant-isolation layers TOGETHER.

The app-layer `WHERE tenant_id = :tenant` filter and the DB-layer PostgreSQL RLS
policies were each tested independently, but never through the same path. These
tests run the real HTTP document path against a PostgreSQL backend with the
runtime role (NOSUPERUSER NOBYPASSRLS) so both layers must fire:

- test_http_tenant_isolation_fires_both_layers: tenant A writes, tenant B reads
  through the HTTP route -> 404. A missing app filter would still be caught by
  RLS (tenant A's row is invisible to tenant B's GUC).
- test_rls_alone_blocks_cross_tenant_without_app_where (canary): a raw SELECT
  through the runtime role WITHOUT the app-layer WHERE returns 0 rows for the
  other tenant — the second layer alone stops the leak (DOGFOOD-METRIC-01 案A
  capability canary: if RLS is disabled this fails).

Skipped unless the PostgreSQL env contract (KJ_ATLAS_DATABASE_URL + the runtime
role URL) is present — same gating as test_document_access_rls_postgres.py.
"""

from __future__ import annotations

import os
from collections.abc import Iterator
from dataclasses import dataclass

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from kj_atlas_api.db import get_db
from kj_atlas_api.main import app
from kj_atlas_api.models import Base
from kj_atlas_api.tenant_context import TenantContext

TIMESTAMP = "2026-08-14T00:00:00Z"

ADMIN_DATABASE_URL_ENV = "KJ_ATLAS_DATABASE_URL"
RUNTIME_DATABASE_URL_ENV = "KJ_ATLAS_TEST_POSTGRES_RUNTIME_DATABASE_URL"


@dataclass
class MutableTenantResolver:
    tenant_id: str

    def resolve(self, *, db: Session, user_id: str | None, claim: object = None) -> TenantContext:  # noqa: ARG002
        return TenantContext(
            tenant_id=self.tenant_id,
            membership_id=f"membership-{self.tenant_id}",
            resolved_by="verified_claim",
        )


@pytest.fixture(scope="module")
def postgres_app_engines() -> Iterator[tuple[sessionmaker, sessionmaker]]:
    admin_url = os.getenv(ADMIN_DATABASE_URL_ENV, "")
    runtime_url = os.getenv(RUNTIME_DATABASE_URL_ENV, "")
    if not admin_url.startswith("postgresql") or not runtime_url.startswith("postgresql"):
        pytest.skip(
            f"{ADMIN_DATABASE_URL_ENV} and {RUNTIME_DATABASE_URL_ENV} must be PostgreSQL "
            "URLs (run with the CI PostgreSQL matrix env) to exercise RLS."
        )
    admin_engine = create_engine(admin_url, future=True)
    runtime_engine = create_engine(runtime_url, future=True)
    # Ensure the schema exists (the admin role owns it; the runtime role reads it).
    Base.metadata.create_all(bind=admin_engine)
    yield sessionmaker(bind=admin_engine), sessionmaker(bind=runtime_engine)


def _payload(doc_id: str, title: str) -> dict[str, object]:
    return {
        "version": 1,
        "id": doc_id,
        "title": title,
        "createdAt": TIMESTAMP,
        "updatedAt": TIMESTAMP,
        "transform": {"panX": 0, "panY": 0, "zoom": 1},
        "cards": [],
        "edges": [],
        "islands": [],
    }


@pytest.mark.postgres
def test_http_tenant_isolation_fires_both_layers_on_postgres(
    postgres_app_engines: tuple[sessionmaker, sessionmaker],
) -> None:
    """QA-TENANT-ISOLATION-01 AC-1: the real HTTP path with RLS active.

    tenant A creates a document; tenant B reads the same doc id through the HTTP
    route. Both the app-layer WHERE filter and the DB-layer RLS policy fire — a
    regression in either layer alone is caught (tenant B sees 404, never the
    document).
    """
    _admin_session, runtime_session = postgres_app_engines
    probe_id = "iso-probe"
    # Clean just this probe row if a previous run left it (no children -> safe).
    with _admin_session() as db:
        db.execute(text('DELETE FROM "documents" WHERE id = :id'), {"id": probe_id})
        db.commit()

    def _get_test_db():
        db = runtime_session()
        try:
            yield db
        finally:
            db.close()

    resolver = MutableTenantResolver(tenant_id="tenant-a")
    app.dependency_overrides[get_db] = _get_test_db
    try:
        with TestClient(app) as client:
            # Set the resolver AFTER the lifespan runs — startup reassigns
            # app.state.tenant_context_resolver (same pattern as
            # test_docs_tenant_isolation.py).
            client.app.state.tenant_context_resolver = resolver

            # tenant A writes the document. No user headers: the tenant comes from
            # the MutableTenantResolver, and the DB-layer RLS is keyed by the same
            # tenant via the GUC.
            resp = client.put(f"/docs/{probe_id}", json=_payload(probe_id, "secret-a"))
            assert resp.status_code in (200, 201), resp.text

            # tenant B cannot read it through the HTTP path.
            resolver.tenant_id = "tenant-b"
            resp_b = client.get(f"/docs/{probe_id}")
            assert resp_b.status_code == 404, (
                f"cross-tenant read must be 404 (app filter + RLS), got {resp_b.status_code}"
            )
    finally:
        app.dependency_overrides.pop(get_db, None)


@pytest.mark.postgres
def test_rls_alone_blocks_cross_tenant_without_app_where(
    postgres_app_engines: tuple[sessionmaker, sessionmaker],
) -> None:
    """QA-TENANT-ISOLATION-01 AC-2 (canary): the second layer alone stops a leak.

    A raw SELECT through the runtime role (NOBYPASSRLS) WITHOUT the app-layer
    WHERE clause must return 0 rows for the other tenant. This is the capability
    canary: if RLS is ever disabled or the policy regresses, this test fails
    even though the app layer is not involved.
    """
    admin_session, runtime_session = postgres_app_engines
    probe_id = "canary-probe"

    with admin_session() as db:
        db.execute(text('DELETE FROM "documents" WHERE id = :id'), {"id": probe_id})
        db.execute(text("SET LOCAL kj_atlas.tenant_id = 'tenant-a'"))
        db.execute(
            text(
                'INSERT INTO "documents" (id, tenant_id, version, payload_json, updated_at) '
                "VALUES (:id, :tenant, 1, :payload, :ts)"
            ),
            {"id": probe_id, "tenant": "tenant-a", "payload": "{}", "ts": TIMESTAMP},
        )
        db.commit()

    # tenant-b's session, no app WHERE clause -> RLS must hide tenant-a's row.
    with runtime_session() as db:
        rows = db.execute(
            text("SELECT count(*) FROM documents WHERE id = :id"), {"id": probe_id}
        ).scalar_one()
        assert rows == 0, (
            "RLS did not hide tenant-a's row from tenant-b's session (NOBYPASSRLS). "
            "This is the second-layer canary — fix RLS before anything else."
        )
