from __future__ import annotations

import json
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from kj_atlas_api.db import get_db
from kj_atlas_api.main import app
from kj_atlas_api.models import Base, DocumentRow, TenantRow
from kj_atlas_api.tenant_context import TenantContext


TIMESTAMP = "2026-07-17T00:00:00Z"


@dataclass
class MutableTenantResolver:
    tenant_id: str

    def resolve(self, *, db: Session, user_id: str | None) -> TenantContext:  # noqa: ARG002
        return TenantContext(
            tenant_id=self.tenant_id,
            membership_id=f"membership-{self.tenant_id}",
            resolved_by="verified_claim",
        )


def _payload(*, doc_id: str, title: str) -> dict[str, object]:
    return {
        "version": 1,
        "id": doc_id,
        "title": title,
        "createdAt": "2026-07-17T00:00:00Z",
        "updatedAt": "2026-07-17T00:00:00Z",
        "transform": {"panX": 0, "panY": 0, "zoom": 1},
        "cards": [],
        "edges": [],
        "islands": [],
    }


@contextmanager
def _tenant_client(
    tmp_path,
) -> Iterator[tuple[TestClient, sessionmaker, MutableTenantResolver]]:
    db_path = tmp_path / "docs_tenant_isolation.sqlite3"
    engine = create_engine(f"sqlite:///{db_path}")
    session_local = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    Base.metadata.create_all(bind=engine)

    with session_local() as db:
        db.add_all(
            [
                TenantRow(
                    id="tenant-a",
                    display_name="Tenant A",
                    lifecycle_state="active",
                    created_at=TIMESTAMP,
                    updated_at=TIMESTAMP,
                ),
                TenantRow(
                    id="tenant-b",
                    display_name="Tenant B",
                    lifecycle_state="active",
                    created_at=TIMESTAMP,
                    updated_at=TIMESTAMP,
                ),
                DocumentRow(
                    tenant_id="tenant-a",
                    id="shared-doc",
                    version=1,
                    updated_at=TIMESTAMP,
                    payload_json=json.dumps(
                        _payload(doc_id="shared-doc", title="Tenant A document")
                    ),
                ),
                DocumentRow(
                    tenant_id="tenant-b",
                    id="shared-doc",
                    version=1,
                    updated_at=TIMESTAMP,
                    payload_json=json.dumps(
                        _payload(doc_id="shared-doc", title="Tenant B document")
                    ),
                ),
            ]
        )
        db.commit()

    def _get_test_db():
        db = session_local()
        try:
            yield db
        finally:
            db.close()

    resolver = MutableTenantResolver(tenant_id="tenant-a")
    app.dependency_overrides[get_db] = _get_test_db
    try:
        with TestClient(app) as client:
            client.app.state.tenant_context_resolver = resolver
            yield client, session_local, resolver
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


def test_same_doc_id_reads_only_active_tenant_payload(tmp_path) -> None:
    with _tenant_client(tmp_path) as fixture:
        client, _, resolver = fixture

        resolver.tenant_id = "tenant-a"
        tenant_a = client.get("/docs/shared-doc")
        resolver.tenant_id = "tenant-b"
        tenant_b = client.get("/docs/shared-doc")
        resolver.tenant_id = "tenant-c"
        missing = client.get("/docs/shared-doc")

    assert tenant_a.status_code == 200
    assert tenant_a.json()["title"] == "Tenant A document"
    assert tenant_b.status_code == 200
    assert tenant_b.json()["title"] == "Tenant B document"
    assert missing.status_code == 404
    assert missing.json()["detail"] == "Document not found"


def test_put_updates_only_the_resolved_tenant_row(tmp_path) -> None:
    with _tenant_client(tmp_path) as fixture:
        client, session_local, resolver = fixture
        resolver.tenant_id = "tenant-a"
        updated = client.put(
            "/docs/shared-doc",
            json=_payload(doc_id="shared-doc", title="Tenant A updated"),
        )
        assert updated.status_code == 200

        with session_local() as db:
            tenant_a = db.get(DocumentRow, ("tenant-a", "shared-doc"))
            tenant_b = db.get(DocumentRow, ("tenant-b", "shared-doc"))
            assert tenant_a is not None
            assert tenant_b is not None
            assert json.loads(tenant_a.payload_json)["title"] == "Tenant A updated"
            assert json.loads(tenant_b.payload_json)["title"] == "Tenant B document"
