from __future__ import annotations

import json
import os
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

import httpx
from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from kj_atlas_api.db import get_db
from kj_atlas_api.main import app
from kj_atlas_api.models import Base
from kj_atlas_api.settings import settings
from tests.federation.profile_loader import profile_names


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


def _require_auth_level2_mock_sp(base_url: str) -> None:
    try:
        with httpx.Client(timeout=2.0) as client:
            response = client.get(f"{base_url}/healthz")
    except httpx.HTTPError:
        pytest.skip(
            "auth_level2 mock SP is not reachable; run tests/scripts/run_auth_level2.sh or set KJ_ATLAS_AUTH_LEVEL2_SP_BASE_URL"
        )

    if response.status_code != 200:
        pytest.skip(
            f"auth_level2 mock SP health check failed ({response.status_code}); check KJ_ATLAS_AUTH_LEVEL2_SP_BASE_URL={base_url}"
        )


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


@pytest.mark.auth_level2
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


@pytest.mark.auth_level2
@pytest.mark.parametrize("profile_name", profile_names())
def test_provider_profile_fixture_via_mock_sp(profile_name: str) -> None:
    base_url = os.getenv("KJ_ATLAS_AUTH_LEVEL2_SP_BASE_URL", "http://127.0.0.1:18080")
    payload = _sample_payload(f"doc-{profile_name}")
    _require_auth_level2_mock_sp(base_url)

    with httpx.Client(timeout=10.0) as client:
        response = client.post(f"{base_url}/sp/profile/{profile_name}/docs/doc-{profile_name}", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["put_status"] == 200
    assert body["get_status"] == 200
    assert body["provider"]
