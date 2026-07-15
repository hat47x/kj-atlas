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


class AllowAllAdapter:
    name = "allow-all"

    def authorize(self, request):  # noqa: ANN001
        return AccessDecision(allow=True)


@contextmanager
def _sqlite_client(tmp_path) -> Iterator[TestClient]:
    db_path = tmp_path / "qa_e2e_realistic_journey.sqlite3"
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
            client.app.state.access_control_adapter = AllowAllAdapter()
            yield client
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


def _doc_payload(doc_id: str, *, reviewed: bool) -> dict:
    return {
        "version": 1,
        "id": doc_id,
        "title": "qa-e2e-realistic-journey",
        "createdAt": "2026-05-04T00:00:00Z",
        "updatedAt": "2026-05-04T00:00:00Z",
        "transform": {"panX": 0, "panY": 0, "zoom": 1},
        "cards": [
            {"id": "c-reviewed", "text": "Reviewed card", "x": 0, "y": 0, "reviewed": True},
            {"id": "c-unreviewed", "text": "Unreviewed card", "x": 180, "y": 40, "reviewed": reviewed},
        ],
        "edges": [{"id": "e-1", "fromId": "c-reviewed", "toId": "c-unreviewed", "type": "related"}],
        "islands": [{"id": "island-1", "cardIds": ["c-reviewed", "c-unreviewed"], "shape": {"kind": "rect"}}],
    }


def _context_query_payload(*, review_filter: str) -> dict:
    return {
        "query": {
            "queryId": "query-1",
            "goal": "qa-e2e-journey",
            "scope": "document",
            "depth": 1,
            "constraints": {},
            "reviewFilter": review_filter,
            "safeModePolicy": "strict",
            "outputMode": "summary",
            "previewConfirmed": True,
        },
        "stubDatasetId": "A2-minimal-v1",
    }


def test_journey_a_authoring_continuity_put_get_roundtrip(tmp_path) -> None:
    with _sqlite_client(tmp_path) as client:
        create = client.put("/docs/doc-journey-a", json=_doc_payload("doc-journey-a", reviewed=False))
        assert create.status_code == 200

        loaded = client.get("/docs/doc-journey-a")
        assert loaded.status_code == 200
        body = loaded.json()
        assert body["id"] == "doc-journey-a"
        assert len(body["cards"]) == 2
        assert body["islands"][0]["id"] == "island-1"


def test_journey_b_review_governance_requires_preview_confirmation(tmp_path) -> None:
    with _sqlite_client(tmp_path) as client:
        payload = _context_query_payload(review_filter="includeUnreviewed")
        payload["query"]["previewConfirmed"] = False

        response = client.post("/context/bundle", json=payload)
        assert response.status_code == 422
        assert response.json()["detail"]["code"] == "preview_required"


def test_journey_c_safe_sharing_gate_records_fail_closed_reason_for_unreviewed(tmp_path) -> None:
    with _sqlite_client(tmp_path) as client:
        response = client.post(
            "/docs/doc-journey-c/export-audit",
            json={
                "safeMode": True,
                "exportKind": "bundle",
                "allowUnreviewedText": False,
                "containsUnreviewedText": True,
                "blockReason": "safe_mode_unreviewed_text",
            },
        )
        assert response.status_code == 403
        assert "safe_mode" in str(response.json()).lower()

        bundle = client.post("/context/bundle", json=_context_query_payload(review_filter="includeUnreviewed"))
        assert bundle.status_code == 200
        bundle_body = bundle.json()
        assert bundle_body["reviewFlags"]["unreviewed"] == 0
        assert "safe_mode_unreviewed_text" in bundle_body["excludedReason"]
