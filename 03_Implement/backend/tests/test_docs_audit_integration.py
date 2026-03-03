from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from kj_atlas_api.access_control import AccessDecision
from kj_atlas_api.db import get_db
from kj_atlas_api.main import app
from kj_atlas_api.models import Base


class SpyAuditDispatcher:
    def __init__(self) -> None:
        self.events: list[object] = []

    def emit(self, event: object):
        self.events.append(event)
        return None


class AllowAllAdapter:
    name = "allow-all"

    def authorize(self, request):  # noqa: ANN001
        return AccessDecision(allow=True)



def _sample_payload(doc_id: str) -> dict:
    return {
        "version": 1,
        "id": doc_id,
        "title": "audit-test",
        "createdAt": "2026-02-11T00:00:00Z",
        "updatedAt": "2026-02-11T00:00:00Z",
        "transform": {"panX": 0, "panY": 0, "zoom": 1},
        "cards": [{"id": "card-1", "text": "alpha", "x": 0, "y": 0}],
        "edges": [],
    }



@contextmanager
def _sqlite_client(tmp_path) -> Iterator[TestClient]:
    db_path = tmp_path / "docs_audit.sqlite3"
    engine = create_engine(f"sqlite:///{db_path}")
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



def test_get_document_emits_view_audit_event(tmp_path) -> None:
    spy = SpyAuditDispatcher()
    with _sqlite_client(tmp_path) as client:
        client.app.state.audit_dispatcher = spy
        client.app.state.access_control_adapter = AllowAllAdapter()
        payload = _sample_payload("doc-view")
        put_resp = client.put("/docs/doc-view", json=payload)
        assert put_resp.status_code == 200

        get_resp = client.get(
            "/docs/doc-view",
            headers={
                "x-actor-ref": "user-1",
                "x-auth-roles": "admin",
                "x-auth-groups": "team-a",
                "x-policy-ref": "secret-policy-v1",
                "x-doc-visibility": "Org",
                "x-trace-id": "trace-view-1",
            },
        )
        assert get_resp.status_code == 200

    assert len(spy.events) == 1
    event = spy.events[0]
    assert event.eventType == "view"
    assert event.docId == "doc-view"
    assert event.metadata["decision_allow"] is True
    assert event.metadata["decision_read_only"] is False
    assert event.metadata["decision_reason"] is None
    assert event.metadata["policyRefPresent"] is True
    assert event.metadata["adapterName"] == "allow-all"
    assert event.metadata["visibility"] == "Org"
    assert event.metadata["traceId"] == "trace-view-1"
    metadata_json = str(event.metadata)
    assert "secret-policy-v1" not in metadata_json
    assert "team-a" not in metadata_json
    assert "admin" not in metadata_json



def test_post_export_audit_emits_export_event(tmp_path) -> None:
    spy = SpyAuditDispatcher()
    with _sqlite_client(tmp_path) as client:
        client.app.state.audit_dispatcher = spy
        client.app.state.access_control_adapter = AllowAllAdapter()
        response = client.post(
            "/docs/doc-export/export-audit",
            json={"safeMode": False, "exportKind": "bundle"},
            headers={"x-actor-ref": "user-2", "x-trace-id": "trace-export-1"},
        )
        assert response.status_code == 200
        assert response.json() == {"status": "accepted"}

    assert len(spy.events) == 1
    event = spy.events[0]
    assert event.eventType == "export"
    assert event.docId == "doc-export"
    assert event.safeMode is False
    assert event.metadata["action"] == "export"
    assert event.metadata["decision_allow"] is True
    assert event.metadata["decision_read_only"] is False
    assert event.metadata["decision_reason"] is None
    assert event.metadata["adapterName"] == "allow-all"
    assert event.metadata["traceId"] == "trace-export-1"
