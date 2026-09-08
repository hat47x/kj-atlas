"""SEC-DOC-BOUND-01: document size + card count bounds on PUT /docs."""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from kj_atlas_api.db import _normalize_database_url, get_db
from kj_atlas_api.main import app
from kj_atlas_api.models import Base
from kj_atlas_api.settings import settings


@pytest.fixture()
def client(tmp_path) -> Iterator[TestClient]:
    """A client backed by its own migrated SQLite file.

    The SQLite CI job runs pytest without `alembic upgrade head`, so nothing
    creates the schema ambiently -- every DB-touching test builds its own via
    `Base.metadata.create_all`. Without this fixture the accept-path test below
    reached the repository and failed with "no such table: documents"; the two
    reject-path tests passed only because the 413 short-circuits before any
    query. Same shape as `test_docs_roundtrip.py::sqlite_client`.
    """
    engine = create_engine(_normalize_database_url(f"sqlite:///{tmp_path / 'docs_bounds.sqlite3'}"))
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
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


def _payload(doc_id: str, cards: int) -> dict:
    return {
        "version": 1,
        "id": doc_id,
        "title": "bounds",
        "createdAt": "2026-08-12T00:00:00Z",
        "updatedAt": "2026-08-12T00:00:00Z",
        "transform": {"panX": 0, "panY": 0, "zoom": 1},
        "cards": [{"id": f"c{i}", "text": "x", "x": i, "y": 0} for i in range(cards)],
        "edges": [],
        "islands": [],
    }


def test_put_rejects_document_over_card_count_limit(client, monkeypatch) -> None:
    monkeypatch.setattr(settings, "max_document_cards", 3)
    resp = client.put("/docs/bounds-cc", json=_payload("bounds-cc", 4))
    assert resp.status_code == 413
    assert resp.json()["detail"]["code"] == "document_too_many_cards"


def test_put_rejects_document_over_byte_limit(client, monkeypatch) -> None:
    # A tiny byte ceiling forces the size check without a huge payload.
    monkeypatch.setattr(settings, "max_document_bytes", 200)
    resp = client.put("/docs/bounds-bytes", json=_payload("bounds-bytes", 3))
    assert resp.status_code == 413
    assert resp.json()["detail"]["code"] == "document_too_large"


def test_put_accepts_document_under_limits(client, monkeypatch) -> None:
    monkeypatch.setattr(settings, "max_document_cards", 10_000)
    monkeypatch.setattr(settings, "max_document_bytes", 20 * 1024 * 1024)
    resp = client.put("/docs/bounds-ok", json=_payload("bounds-ok", 3))
    assert resp.status_code == 200
    body = resp.json()
    assert len(body["cards"]) == 3


def test_settings_defaults_are_bounded() -> None:
    # The defaults are public runtime contract: bytes match the inquiry bundle
    # and cards retain the meta-dogfooding headroom documented in the registry.
    assert settings.max_document_bytes == 20 * 1024 * 1024
    assert settings.max_document_cards == 50_000
