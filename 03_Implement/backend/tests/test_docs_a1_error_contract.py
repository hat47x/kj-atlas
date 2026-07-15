from __future__ import annotations

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from kj_atlas_api.db import _normalize_database_url, get_db
from kj_atlas_api.main import app
from kj_atlas_api.models import Base


@pytest.fixture()
def sqlite_client(tmp_path) -> Iterator[TestClient]:
    db_path = tmp_path / "docs_a1_error_contract.sqlite3"
    database_url = f"sqlite:///{db_path}"
    engine = create_engine(_normalize_database_url(database_url))
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


def _sample_v2_payload(doc_id: str) -> dict:
    return {
        "version": 1,
        "id": doc_id,
        "title": "a1-error-contract",
        "createdAt": "2026-02-11T00:00:00Z",
        "updatedAt": "2026-02-11T00:00:00Z",
        "transform": {"panX": 0, "panY": 0, "zoom": 1},
        "cards": [{"id": "card-1", "text": "alpha", "x": 0, "y": 0}],
        "edges": [],
        "islands": [{"id": "island-1", "cardIds": ["card-1"]}],
    }


def test_put_document_returns_a1_error_contract_for_trace_key_missing(sqlite_client: TestClient) -> None:
    doc_id = "doc-a1-error-tracekey"
    payload = _sample_v2_payload(doc_id)
    payload["reproposalDiffs"] = [
        {
            "schemaVersion": "1.0.0",
            "proposalId": "proposal-1",
            "basedOnIteration": 1,
            "diffOps": [
                {
                    "opId": "op-1",
                    "opType": "move",
                    "targetRef": "card:card-1",
                    "before": {"x": 0, "y": 0},
                    "after": {"x": 1, "y": 1},
                }
            ],
        }
    ]

    response = sqlite_client.put(f"/docs/{doc_id}", json=payload)

    assert response.status_code == 422
    detail = response.json()["detail"]
    assert detail["schemaVersion"] == "1.0.0"
    assert detail["errorEnvelope"]["errorCode"] == "A1_REQUIRED_FIELD_MISSING"
    assert detail["errorEnvelope"]["contractId"] == "A1-REDIFF-IF"
    assert isinstance(detail["errorEnvelope"]["message"], str)
    assert detail["errorEnvelope"]["retryable"] is False


def test_put_document_returns_a1_error_contract_for_pii_violation(sqlite_client: TestClient) -> None:
    doc_id = "doc-a1-error-pii"
    payload = _sample_v2_payload(doc_id)
    payload["reviewAttribution"] = {
        "schemaVersion": "1.0.0",
        "reviewState": "human_reviewed",
        "reviewedAt": "2026-02-11T00:02:00Z",
        "reviewerRef": "alice@example.com",
        "auditRecordedAt": "2026-02-11T00:02:00Z",
    }

    response = sqlite_client.put(
        f"/docs/{doc_id}",
        json=payload,
        headers={"x-actor-ref": "alice@example.com"},
    )

    assert response.status_code == 422
    detail = response.json()["detail"]
    assert detail["schemaVersion"] == "1.0.0"
    assert detail["errorEnvelope"]["errorCode"] == "A1_PII_POLICY_VIOLATION"
    assert detail["errorEnvelope"]["contractId"] == "A1-ATTR-IF"
    assert detail["errorEnvelope"]["retryable"] is False


def test_put_document_returns_a1_error_contract_for_critique_schema_mismatch(sqlite_client: TestClient) -> None:
    doc_id = "doc-a1-error-critique-schema"
    payload = _sample_v2_payload(doc_id)
    payload["critiqueInputs"] = [
        {
            "schemaVersion": "2.0.0",
            "critiqueId": "critique-1",
            "targetRef": "card:card-1",
            "critiqueType": "feels_off",
            "createdAt": "2026-02-11T00:03:00Z",
            "iteration": 1,
        }
    ]

    response = sqlite_client.put(f"/docs/{doc_id}", json=payload)

    assert response.status_code == 422
    detail = response.json()["detail"]
    assert detail["schemaVersion"] == "1.0.0"
    assert detail["errorEnvelope"]["errorCode"] == "A1_SCHEMA_VERSION_MISMATCH"
    assert detail["errorEnvelope"]["contractId"] == "A1-CRITIQUE-IF"
    assert detail["errorEnvelope"]["retryable"] is False


def test_put_document_returns_a1_error_contract_for_override_policy_violation(sqlite_client: TestClient) -> None:
    doc_id = "doc-a1-error-override-policy"
    payload = _sample_v2_payload(doc_id)
    payload["reviewAttribution"] = {
        "schemaVersion": "1.0.0",
        "reviewState": "human_reviewed",
        "reviewedAt": "2026-02-11T00:04:00Z",
        "reviewerRef": "reviewer-opaque-id",
        "auditRecordedAt": "2026-02-11T00:04:00Z",
        "overridePolicy": "single_operator",
    }

    response = sqlite_client.put(
        f"/docs/{doc_id}",
        json=payload,
        headers={"x-actor-ref": "operator-1"},
    )

    assert response.status_code == 422
    detail = response.json()["detail"]
    assert detail["schemaVersion"] == "1.0.0"
    assert detail["errorEnvelope"]["errorCode"] == "A1_OVERRIDE_POLICY_VIOLATION"
    assert detail["errorEnvelope"]["contractId"] == "A1-ATTR-IF"
    assert detail["errorEnvelope"]["retryable"] is False
