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
DATABASE_URL_ENV = "KJ_ATLAS_DATABASE_URL"
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
                "placardCardId": "card-1",
                "collapsed": True,
                "title": "Parent",
            },
            {
                "id": "child-island",
                "cardIds": ["card-2"],
                "parentIslandId": "parent-island",
                "placardCardId": "card-2",
                "collapsed": False,
                "title": "Child",
            },
        ],
    }




def _sample_payload_v2_with_canonical(doc_id: str) -> dict:
    return {
        "version": 2,
        "id": doc_id,
        "title": "roundtrip-v2-canonical",
        "createdAt": "2026-02-11T00:00:00Z",
        "updatedAt": "2026-02-11T00:00:00Z",
        "transform": {"panX": 0, "panY": 0, "zoom": 1},
        "cards": [
            {
                "id": "card-canonical",
                "text": "alpha",
                "x": 12.5,
                "y": -9.0,
                "sources": ["card-source"],
            },
            {
                "id": "card-source",
                "text": "alpha (duplicate)",
                "x": 212.5,
                "y": 91.0,
                "canonicalId": "card-canonical",
            },
        ],
        "edges": [],
        "islands": [],
    }






def _sample_payload_v2_with_merge_suggestion_decisions(doc_id: str) -> dict:
    return {
        "version": 2,
        "id": doc_id,
        "title": "roundtrip-v2-merge-decisions",
        "createdAt": "2026-02-11T00:00:00Z",
        "updatedAt": "2026-02-11T00:00:00Z",
        "transform": {"panX": 0, "panY": 0, "zoom": 1},
        "cards": [
            {"id": "card-1", "text": "alpha", "x": 12.5, "y": -9.0},
            {"id": "card-2", "text": "Alpha", "x": 212.5, "y": 91.0},
        ],
        "edges": [],
        "islands": [],
        "mergeSuggestionDecisions": [
            {
                "id": "decision-1",
                "groupId": "heuristic-alpha-card-1-card-2",
                "decision": "defer",
                "decidedAt": "2026-02-11T00:03:00Z",
                "cardIds": ["card-1", "card-2"],
                "mergedTextDraft": "alpha",
                "editedText": "alpha",
                "rationale": "heuristic:normalized-text",
            }
        ],
    }


def _sample_merge_decision_record(*, decision_id: str, group_id: str, snapshot_version: str, action: str = "defer") -> dict:
    return {
        "decisionId": decision_id,
        "groupId": group_id,
        "action": action,
        "selectedCardIds": ["card-1", "card-2"],
        "note": "manual assisted decision",
        "decidedBy": "reviewer:opaque-1",
        "decidedAt": "2026-02-11T00:03:00Z",
        "snapshotVersion": snapshot_version,
    }


def _sample_payload_v2_with_relation_summaries(doc_id: str) -> dict:
    return {
        "version": 2,
        "id": doc_id,
        "title": "roundtrip-v2-relations",
        "createdAt": "2026-02-11T00:00:00Z",
        "updatedAt": "2026-02-11T00:00:00Z",
        "transform": {"panX": 0, "panY": 0, "zoom": 1},
        "cards": [
            {"id": "card-1", "text": "alpha", "x": 12.5, "y": -9.0},
            {"id": "card-2", "text": "beta", "x": 212.5, "y": 91.0},
        ],
        "edges": [
            {"id": "edge-1", "fromId": "card-1", "toId": "card-2", "type": "related"}
        ],
        "islands": [
            {"id": "island-1", "cardIds": ["card-1"]},
            {"id": "island-2", "cardIds": ["card-2"]},
        ],
        "relationSummaries": [
            {
                "id": "rs-1",
                "createdAt": "2026-02-11T00:01:00Z",
                "islandAId": "island-1",
                "islandBId": "island-2",
                "relationType": "related",
                "derived": False,
                "text": "alpha supports beta",
                "reviewed": True,
                "groundingCardIds": ["card-1", "card-2"],
                "groundingEdgeIds": ["edge-1"],
                "warnings": ["reviewed by user"],
                "sourceSignature": "edge:edge-1",
                "history": [
                    {
                        "id": "h-ai",
                        "createdAt": "2026-02-11T00:01:00Z",
                        "changeKind": "ai",
                        "fromText": None,
                        "toText": "alpha and beta are related",
                        "fromReviewed": None,
                        "toReviewed": False,
                        "warningsSnapshot": ["initial draft"],
                        "groundingCardIdsSnapshot": ["card-1", "card-2"],
                        "groundingEdgeIdsSnapshot": ["edge-1"],
                    },
                    {
                        "id": "h-manual",
                        "createdAt": "2026-02-11T00:02:00Z",
                        "changeKind": "manual",
                        "fromText": "alpha and beta are related",
                        "toText": "alpha supports beta",
                        "fromReviewed": False,
                        "toReviewed": True,
                        "warningsSnapshot": ["reviewed by user"],
                        "groundingCardIdsSnapshot": ["card-1", "card-2"],
                        "groundingEdgeIdsSnapshot": ["edge-1"],
                    },
                ],
            }
        ],
    }


def _sample_payload_v2_without_relation_summary_history(doc_id: str) -> dict:
    payload = _sample_payload_v2_with_relation_summaries(doc_id)
    payload["relationSummaries"][0].pop("history", None)
    return payload


def _assert_v2_canonical_roundtrip(client: TestClient) -> None:
    doc_id = "doc-roundtrip-v2-canonical"
    payload = _sample_payload_v2_with_canonical(doc_id)

    put_response = client.put(f"/docs/{doc_id}", json=payload)
    assert put_response.status_code == 200
    put_json = put_response.json()
    put_cards_by_id = {card["id"]: card for card in put_json["cards"]}
    assert put_cards_by_id["card-source"]["canonicalId"] == "card-canonical"
    assert put_cards_by_id["card-canonical"]["sources"] == ["card-source"]

    get_response = client.get(f"/docs/{doc_id}")
    assert get_response.status_code == 200
    get_json = get_response.json()
    get_cards_by_id = {card["id"]: card for card in get_json["cards"]}
    assert get_cards_by_id["card-source"]["canonicalId"] == "card-canonical"
    assert get_cards_by_id["card-canonical"]["sources"] == ["card-source"]


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
    assert put_islands_by_id["child-island"]["parentIslandId"] == "parent-island"
    assert "parentIslandId" not in put_islands_by_id["parent-island"]
    assert put_islands_by_id["parent-island"]["placardCardId"] == "card-1"
    assert put_islands_by_id["child-island"]["placardCardId"] == "card-2"

    get_response = client.get(f"/docs/{doc_id}")
    assert get_response.status_code == 200
    get_json = get_response.json()

    get_islands_by_id = {island["id"]: island for island in get_json["islands"]}
    assert get_islands_by_id["parent-island"]["collapsed"] is True
    assert get_islands_by_id["child-island"]["collapsed"] is False
    assert get_islands_by_id["child-island"]["parentIslandId"] == "parent-island"
    assert "parentIslandId" not in get_islands_by_id["parent-island"]
    assert get_islands_by_id["parent-island"]["placardCardId"] == "card-1"
    assert get_islands_by_id["child-island"]["placardCardId"] == "card-2"





def _assert_v2_merge_suggestion_decisions_roundtrip(client: TestClient) -> None:
    doc_id = "doc-roundtrip-v2-merge-decisions"
    payload = _sample_payload_v2_with_merge_suggestion_decisions(doc_id)

    put_response = client.put(f"/docs/{doc_id}", json=payload)
    assert put_response.status_code == 200
    put_json = put_response.json()
    assert put_json["mergeSuggestionDecisions"][0]["decision"] == "defer"

    get_response = client.get(f"/docs/{doc_id}")
    assert get_response.status_code == 200
    get_json = get_response.json()
    assert get_json["mergeSuggestionDecisions"][0]["id"] == "decision-1"
    assert get_json["mergeSuggestionDecisions"][0]["groupId"] == "heuristic-alpha-card-1-card-2"


def _assert_merge_decision_logs_contract_roundtrip(client: TestClient) -> None:
    doc_id = "doc-merge-decision-log"
    payload = _sample_payload_v2_with_merge_suggestion_decisions(doc_id)

    put_response = client.put(f"/docs/{doc_id}", json=payload)
    assert put_response.status_code == 200

    first_record = _sample_merge_decision_record(
        decision_id="decision-1",
        group_id="group-1",
        snapshot_version="snap-1",
        action="accept",
    )
    second_record = _sample_merge_decision_record(
        decision_id="decision-2",
        group_id="group-1",
        snapshot_version="snap-1",
        action="partial",
    )

    append_first = client.post(f"/docs/{doc_id}/merge-decision-logs", json={"record": first_record})
    assert append_first.status_code == 201
    assert append_first.json()["action"] == "accept"

    append_second = client.post(f"/docs/{doc_id}/merge-decision-logs", json={"record": second_record})
    assert append_second.status_code == 201
    assert append_second.json()["action"] == "partial"

    by_group_response = client.get(f"/docs/{doc_id}/merge-decision-logs/by-group/group-1")
    assert by_group_response.status_code == 200
    by_group_json = by_group_response.json()
    assert [entry["decisionId"] for entry in by_group_json] == ["decision-1", "decision-2"]

    restore_response = client.get(f"/docs/{doc_id}/merge-decision-logs/restore/snap-1")
    assert restore_response.status_code == 200
    restore_json = restore_response.json()
    assert [entry["action"] for entry in restore_json] == ["accept", "partial"]


def _assert_merge_decision_logs_contract_validation(client: TestClient) -> None:
    doc_id = "doc-merge-decision-log-validation"
    payload = _sample_payload_v2_with_merge_suggestion_decisions(doc_id)
    put_response = client.put(f"/docs/{doc_id}", json=payload)
    assert put_response.status_code == 200

    invalid_record = _sample_merge_decision_record(
        decision_id="decision-invalid",
        group_id="group-invalid",
        snapshot_version="snap-invalid",
        action="auto",
    )
    invalid_response = client.post(f"/docs/{doc_id}/merge-decision-logs", json={"record": invalid_record})
    assert invalid_response.status_code == 422

    first_record = _sample_merge_decision_record(
        decision_id="decision-dup",
        group_id="group-dup",
        snapshot_version="snap-dup",
    )
    second_record = _sample_merge_decision_record(
        decision_id="decision-dup",
        group_id="group-dup",
        snapshot_version="snap-dup-2",
    )
    first_response = client.post(f"/docs/{doc_id}/merge-decision-logs", json={"record": first_record})
    assert first_response.status_code == 201
    duplicate_response = client.post(f"/docs/{doc_id}/merge-decision-logs", json={"record": second_record})
    assert duplicate_response.status_code == 409


def _assert_v2_relation_summary_roundtrip(client: TestClient) -> None:
    doc_id = "doc-roundtrip-v2-relations"
    payload = _sample_payload_v2_with_relation_summaries(doc_id)

    put_response = client.put(f"/docs/{doc_id}", json=payload)
    assert put_response.status_code == 200
    put_json = put_response.json()
    put_relation_summary = put_json["relationSummaries"][0]
    assert put_relation_summary["id"] == "rs-1"
    assert put_relation_summary["history"][0]["changeKind"] == "ai"
    assert put_relation_summary["history"][1]["changeKind"] == "manual"

    get_response = client.get(f"/docs/{doc_id}")
    assert get_response.status_code == 200
    get_json = get_response.json()
    get_relation_summary = get_json["relationSummaries"][0]
    assert get_relation_summary["text"] == "alpha supports beta"
    assert get_relation_summary["reviewed"] is True
    assert len(get_relation_summary["history"]) == 2
    assert get_relation_summary["history"][1]["toText"] == "alpha supports beta"


def _assert_v2_relation_summary_without_history_roundtrip(client: TestClient) -> None:
    doc_id = "doc-roundtrip-v2-relations-no-history"
    payload = _sample_payload_v2_without_relation_summary_history(doc_id)

    put_response = client.put(f"/docs/{doc_id}", json=payload)
    assert put_response.status_code == 200
    put_json = put_response.json()
    put_relation_summary = put_json["relationSummaries"][0]
    assert "history" not in put_relation_summary

    get_response = client.get(f"/docs/{doc_id}")
    assert get_response.status_code == 200
    get_json = get_response.json()
    get_relation_summary = get_json["relationSummaries"][0]
    assert get_relation_summary["id"] == "rs-1"
    assert "history" not in get_relation_summary




def _assert_v2_polygon_geometry_roundtrip(client: TestClient) -> None:
    doc_id = "doc-roundtrip-v2-polygon"
    payload = {
        "version": 2,
        "id": doc_id,
        "title": "polygon-roundtrip",
        "createdAt": "2026-02-11T00:00:00Z",
        "updatedAt": "2026-02-11T00:00:00Z",
        "transform": {"panX": 0, "panY": 0, "zoom": 1},
        "cards": [{"id": "card-1", "text": "alpha", "x": 12.5, "y": -9.0}],
        "edges": [],
        "islands": [
            {
                "id": "poly-island",
                "cardIds": ["card-1"],
                "geometry": {
                    "type": "polygon",
                    "points": [
                        {"x": 0, "y": 0},
                        {"x": 100, "y": 0},
                        {"x": 80, "y": 70},
                    ],
                },
            }
        ],
    }

    put_response = client.put(f"/docs/{doc_id}", json=payload)
    assert put_response.status_code == 200
    put_island = put_response.json()["islands"][0]
    assert put_island["geometry"] == payload["islands"][0]["geometry"]

    get_response = client.get(f"/docs/{doc_id}")
    assert get_response.status_code == 200
    get_island = get_response.json()["islands"][0]
    assert get_island["geometry"] == payload["islands"][0]["geometry"]


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


def test_docs_v2_canonical_roundtrip_sqlite(sqlite_client: TestClient) -> None:
    _assert_v2_canonical_roundtrip(sqlite_client)


@pytest.mark.postgres
def test_docs_v2_canonical_roundtrip_postgres(postgres_client: TestClient) -> None:
    _assert_v2_canonical_roundtrip(postgres_client)




def test_docs_v2_merge_suggestion_decisions_roundtrip_sqlite(sqlite_client: TestClient) -> None:
    _assert_v2_merge_suggestion_decisions_roundtrip(sqlite_client)


def test_docs_merge_decision_logs_contract_roundtrip_sqlite(sqlite_client: TestClient) -> None:
    _assert_merge_decision_logs_contract_roundtrip(sqlite_client)


def test_docs_merge_decision_logs_contract_validation_sqlite(sqlite_client: TestClient) -> None:
    _assert_merge_decision_logs_contract_validation(sqlite_client)


@pytest.mark.postgres
def test_docs_v2_merge_suggestion_decisions_roundtrip_postgres(postgres_client: TestClient) -> None:
    _assert_v2_merge_suggestion_decisions_roundtrip(postgres_client)


def test_docs_merge_decision_logs_contract_roundtrip_postgres(postgres_client: TestClient) -> None:
    _assert_merge_decision_logs_contract_roundtrip(postgres_client)


def test_docs_merge_decision_logs_contract_validation_postgres(postgres_client: TestClient) -> None:
    _assert_merge_decision_logs_contract_validation(postgres_client)

def test_docs_v2_relation_summary_roundtrip_sqlite(sqlite_client: TestClient) -> None:
    _assert_v2_relation_summary_roundtrip(sqlite_client)


@pytest.mark.postgres
def test_docs_v2_relation_summary_roundtrip_postgres(postgres_client: TestClient) -> None:
    _assert_v2_relation_summary_roundtrip(postgres_client)


def test_docs_v2_relation_summary_without_history_roundtrip_sqlite(sqlite_client: TestClient) -> None:
    _assert_v2_relation_summary_without_history_roundtrip(sqlite_client)


def test_docs_v2_polygon_geometry_roundtrip_sqlite(sqlite_client: TestClient) -> None:
    _assert_v2_polygon_geometry_roundtrip(sqlite_client)


@pytest.mark.postgres
def test_docs_v2_relation_summary_without_history_roundtrip_postgres(postgres_client: TestClient) -> None:
    _assert_v2_relation_summary_without_history_roundtrip(postgres_client)


@pytest.mark.postgres
def test_docs_v2_polygon_geometry_roundtrip_postgres(postgres_client: TestClient) -> None:
    _assert_v2_polygon_geometry_roundtrip(postgres_client)


def _sample_payload_v2_with_hil_rs_contract_fields(doc_id: str, *, reviewer_ref: str = "user:u-1") -> dict:
    return {
        "version": 2,
        "id": doc_id,
        "title": "roundtrip-v2-hil-rs",
        "createdAt": "2026-02-11T00:00:00Z",
        "updatedAt": "2026-02-11T00:00:00Z",
        "transform": {"panX": 0, "panY": 0, "zoom": 1},
        "cards": [{"id": "card-1", "text": "alpha", "x": 0, "y": 0}],
        "edges": [],
        "islands": [{"id": "island-1", "cardIds": ["card-1"]}],
        "critiqueInputs": [
            {
                "schemaVersion": "1.0.0",
                "critiqueId": "crit-1",
                "targetRef": "card:card-1",
                "critiqueType": "too_close",
                "createdAt": "2026-02-11T00:01:00Z",
                "iteration": 1,
            }
        ],
        "reproposalDiffs": [
            {
                "proposalId": "proposal-1",
                "basedOnIteration": 1,
                "traceKey": "crit-1:proposal-1",
                "diffOps": [
                    {
                        "opId": "op-1",
                        "opType": "move",
                        "targetRef": "card:card-1",
                        "before": {"x": 0, "y": 0},
                        "after": {"x": 12.5, "y": 9.0},
                    }
                ],
            }
        ],
        "reviewAttribution": {
            "schemaVersion": "1.0.0",
            "reviewState": "human_reviewed",
            "reviewedAt": "2026-02-11T00:02:00Z",
            "reviewerRef": reviewer_ref,
            "auditRecordedAt": "2026-02-11T00:02:00Z",
        },
    }


def _assert_v2_hil_rs_contract_fields_roundtrip(client: TestClient) -> None:
    doc_id = "doc-roundtrip-v2-hil-rs"
    payload = _sample_payload_v2_with_hil_rs_contract_fields(doc_id, reviewer_ref="reviewer:opaque-1")

    put_response = client.put(
        f"/docs/{doc_id}",
        json=payload,
        headers={"x-actor-ref": "reviewer:opaque-1"},
    )
    assert put_response.status_code == 200
    put_json = put_response.json()
    assert put_json["critiqueInputs"][0]["schemaVersion"] == "1.0.0"

    get_response = client.get(f"/docs/{doc_id}")
    assert get_response.status_code == 200
    get_json = get_response.json()
    assert get_json["reproposalDiffs"][0]["traceKey"] == "crit-1:proposal-1"
    assert get_json["reviewAttribution"]["reviewState"] == "human_reviewed"


def test_docs_v2_hil_rs_contract_fields_roundtrip_sqlite(sqlite_client: TestClient) -> None:
    _assert_v2_hil_rs_contract_fields_roundtrip(sqlite_client)


def test_docs_v2_hil_rs_contract_fields_roundtrip_postgres(postgres_client: TestClient) -> None:
    _assert_v2_hil_rs_contract_fields_roundtrip(postgres_client)


def test_docs_v2_hil_rs_contract_fields_reject_spoofed_reviewer_sqlite(sqlite_client: TestClient) -> None:
    doc_id = "doc-roundtrip-v2-hil-rs-spoofed"
    payload = _sample_payload_v2_with_hil_rs_contract_fields(doc_id, reviewer_ref="reviewer:other")

    put_response = sqlite_client.put(
        f"/docs/{doc_id}",
        json=payload,
        headers={"x-actor-ref": "reviewer:opaque-1"},
    )
    assert put_response.status_code == 403
    assert put_response.json()["detail"] == "reviewerRef must match authenticated identity"
