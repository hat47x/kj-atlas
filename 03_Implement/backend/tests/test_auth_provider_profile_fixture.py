from __future__ import annotations

import json
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from kj_atlas_api.db import get_db
from kj_atlas_api.main import app
from kj_atlas_api.models import Base
from kj_atlas_api.settings import settings


@contextmanager
def _sqlite_client(tmp_path) -> Iterator[TestClient]:
    db_path = tmp_path / "provider_fixture.sqlite3"
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


def _sample_payload(doc_id: str) -> dict:
    return {
        "version": 1,
        "id": doc_id,
        "title": "provider-fixture-test",
        "createdAt": "2026-02-11T00:00:00Z",
        "updatedAt": "2026-02-11T00:00:00Z",
        "transform": {"panX": 0, "panY": 0, "zoom": 1},
        "cards": [{"id": "card-1", "text": "alpha", "x": 0, "y": 0}],
        "edges": [],
    }


def test_provider_profile_fixture_google_oidc_roundtrip(tmp_path) -> None:
    fixture_path = Path(__file__).parent / "fixtures" / "provider_profile_google_oidc.json"
    fixture = json.loads(fixture_path.read_text())

    original_allow_jit = settings.allow_jit_provisioning
    settings.allow_jit_provisioning = True
    try:
        with _sqlite_client(tmp_path) as client:
            put_resp = client.put(
                "/docs/doc-provider-google",
                json=_sample_payload("doc-provider-google"),
                headers=fixture["headers"],
            )
            assert put_resp.status_code == 200

            get_resp = client.get("/docs/doc-provider-google", headers=fixture["headers"])
            assert get_resp.status_code == 200
    finally:
        settings.allow_jit_provisioning = original_allow_jit
