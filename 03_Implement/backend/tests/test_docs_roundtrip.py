from __future__ import annotations

import os
import subprocess
from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from kj_atlas_api.db import _normalize_database_url, get_db
from kj_atlas_api.main import app
from kj_atlas_api.models import Base

RUN_PG_TESTS_ENV = "RUN_PG_TESTS"
DATABASE_URL_ENV = "DATABASE_URL"
BACKEND_DIR = Path(__file__).resolve().parents[1]


@pytest.fixture()
def sqlite_client(tmp_path) -> Iterator[TestClient]:
    db_path = tmp_path / "docs_roundtrip.sqlite3"
    database_url = f"sqlite:///{db_path}"
    yield from _client_for_database_url(database_url, use_create_drop_tables=True)


@pytest.fixture()
def postgres_client() -> Iterator[TestClient]:
    postgres_url = os.getenv(DATABASE_URL_ENV, "")
    should_run_pg_tests = os.getenv(RUN_PG_TESTS_ENV) == "1" or postgres_url.startswith(
        "postgresql"
    )

    if not should_run_pg_tests or not postgres_url.startswith("postgresql"):
        pytest.skip(
            f"set {RUN_PG_TESTS_ENV}=1 and {DATABASE_URL_ENV}=postgresql://... to run PostgreSQL docs roundtrip tests",
            allow_module_level=False,
        )

    subprocess.run(["alembic", "upgrade", "head"], check=True, cwd=BACKEND_DIR)

    yield from _client_for_database_url(postgres_url, use_create_drop_tables=False)


def _client_for_database_url(database_url: str, *, use_create_drop_tables: bool) -> Iterator[TestClient]:
    engine = create_engine(_normalize_database_url(database_url))
    session_local = sessionmaker(bind=engine, autocommit=False, autoflush=False)

    if use_create_drop_tables:
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
        if use_create_drop_tables:
            Base.metadata.drop_all(bind=engine)
        engine.dispose()


def _sample_payload(doc_id: str) -> dict:
    return {
        "version": 1,
        "id": doc_id,
        "title": "roundtrip",
        "createdAt": "2026-02-11T00:00:00Z",
        "updatedAt": "2026-02-11T00:00:00Z",
        "transform": {"panX": 10, "panY": -5, "zoom": 1.25},
        "cards": [
            {
                "id": "card-1",
                "text": "alpha",
                "x": 12.5,
                "y": -9.0,
                "critique": None,
            }
        ],
        "edges": [],
    }




def _sample_payload_v2_with_collapsed(doc_id: str) -> dict:
    return {
        "version": 2,
        "id": doc_id,
        "title": "roundtrip-v2",
        "createdAt": "2026-02-11T00:00:00Z",
        "updatedAt": "2026-02-11T00:00:00Z",
        "transform": {"panX": 0, "panY": 0, "zoom": 1},
        "cards": [
            {
                "id": "card-1",
                "text": "alpha",
                "x": 12.5,
                "y": -9.0,
            },
            {
                "id": "card-2",
                "text": "beta",
                "x": 212.5,
                "y": 91.0,
            },
        ],
        "edges": [
            {
                "id": "edge-1",
                "fromId": "card-1",
                "toId": "card-2",
                "type": "related",
            }
        ],
        "islands": [
            {
                "id": "parent-island",
                "cardIds": ["card-1"],
                "collapsed": True,
                "title": "Parent",
            },
            {
                "id": "child-island",
                "cardIds": ["card-2"],
                "parentIslandId": "parent-island",
                "collapsed": False,
                "title": "Child",
            },
        ],
    }


def _assert_v2_collapsed_roundtrip(client: TestClient) -> None:
    doc_id = "doc-roundtrip-v2-collapsed"
    payload = _sample_payload_v2_with_collapsed(doc_id)

    put_response = client.put(f"/docs/{doc_id}", json=payload)
    assert put_response.status_code == 200
    put_json = put_response.json()
    assert put_json["version"] == 2
    assert put_json["id"] == doc_id

    put_islands_by_id = {island["id"]: island for island in put_json["islands"]}
    assert put_islands_by_id["parent-island"]["collapsed"] is True
    assert put_islands_by_id["child-island"]["collapsed"] is False

    get_response = client.get(f"/docs/{doc_id}")
    assert get_response.status_code == 200
    get_json = get_response.json()

    get_islands_by_id = {island["id"]: island for island in get_json["islands"]}
    assert get_islands_by_id["parent-island"]["collapsed"] is True
    assert get_islands_by_id["child-island"]["collapsed"] is False

def _assert_put_get_roundtrip(client: TestClient) -> None:
    doc_id = "doc-roundtrip"
    payload = _sample_payload(doc_id)

    put_response = client.put(f"/docs/{doc_id}", json=payload)
    assert put_response.status_code == 200
    assert put_response.json() == payload

    get_response = client.get(f"/docs/{doc_id}")
    assert get_response.status_code == 200
    assert get_response.json() == payload


def _assert_etag_optimistic_locking(client: TestClient) -> None:
    doc_id = "doc-etag"
    payload = _sample_payload(doc_id)

    put_response = client.put(f"/docs/{doc_id}", json=payload)
    assert put_response.status_code == 200
    first_etag = put_response.headers.get("etag")
    assert first_etag

    get_response = client.get(f"/docs/{doc_id}")
    assert get_response.status_code == 200
    assert get_response.headers.get("etag") == first_etag

    stale_payload = {**payload, "updatedAt": "2026-02-11T00:01:00Z", "title": "stale update"}
    stale_put = client.put(
        f"/docs/{doc_id}",
        json=stale_payload,
        headers={"If-Match": '"definitely-stale-etag"'},
    )
    assert stale_put.status_code == 409

    fresh_payload = {**payload, "updatedAt": "2026-02-11T00:02:00Z", "title": "fresh update"}
    fresh_put = client.put(f"/docs/{doc_id}", json=fresh_payload, headers={"If-Match": first_etag})
    assert fresh_put.status_code == 200
    second_etag = fresh_put.headers.get("etag")
    assert second_etag
    assert second_etag != first_etag

def test_docs_put_get_roundtrip_sqlite(sqlite_client: TestClient) -> None:
    _assert_put_get_roundtrip(sqlite_client)


def test_docs_etag_sqlite(sqlite_client: TestClient) -> None:
    _assert_etag_optimistic_locking(sqlite_client)


@pytest.mark.postgres
def test_docs_put_get_roundtrip_postgres(postgres_client: TestClient) -> None:
    _assert_put_get_roundtrip(postgres_client)


@pytest.mark.postgres
def test_docs_etag_postgres(postgres_client: TestClient) -> None:
    _assert_etag_optimistic_locking(postgres_client)


def test_docs_v2_collapsed_roundtrip_sqlite(sqlite_client: TestClient) -> None:
    _assert_v2_collapsed_roundtrip(sqlite_client)


@pytest.mark.postgres
def test_docs_v2_collapsed_roundtrip_postgres(postgres_client: TestClient) -> None:
    _assert_v2_collapsed_roundtrip(postgres_client)
