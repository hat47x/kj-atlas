from __future__ import annotations

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from kj_atlas_api.db import get_db
from kj_atlas_api.main import app
from kj_atlas_api.models import Base


def _sample_payload(doc_id: str) -> dict:
    return {
        "version": 1,
        "id": doc_id,
        "title": "handoff-contract",
        "createdAt": "2026-02-11T00:00:00Z",
        "updatedAt": "2026-02-11T00:00:00Z",
        "transform": {"panX": 0, "panY": 0, "zoom": 1},
        "cards": [],
        "edges": [],
    }


def _sample_contract_payload(*, input_hash: str, output_hash: str, padding_violation_count: int, tie_break_changed: bool) -> dict:
    return {
        "input": {
            "gateApprovalRef": "DQ-FB-P2C-01",
            "a2VerifyRef": "A2-HANDOFF-FB-P2C-01-2026-03-14",
            "inputHash": input_hash,
            "deterministicTieBreakOrder": [
                "padding_compliance",
                "self_intersection_avoidance",
                "minimum_area_delta",
                "minimum_vertex_count",
            ],
        },
        "expectedOutput": {
            "outputPolygonHash": output_hash,
            "paddingViolationCount": padding_violation_count,
            "tieBreakOrderChanged": tie_break_changed,
        },
    }


@pytest.fixture()
def client() -> Iterator[TestClient]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
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


def test_verify_polygon_handoff_contract_returns_ok_for_clean_payload(client: TestClient) -> None:
    doc_id = "doc-handoff-ok"
    put_response = client.put(f"/docs/{doc_id}", json=_sample_payload(doc_id))
    assert put_response.status_code == 200

    payload = _sample_contract_payload(
        input_hash="a" * 64,
        output_hash="b" * 64,
        padding_violation_count=0,
        tie_break_changed=False,
    )
    response = client.post(f"/docs/{doc_id}/polygon-handoff/verify-contract", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["rollbackRequired"] is False
    assert body["failureReasons"] == []
    assert isinstance(body["verificationKey"], str)
    assert len(body["verificationKey"]) == 64


def test_verify_polygon_handoff_contract_requests_rollback_on_contract_violation(client: TestClient) -> None:
    doc_id = "doc-handoff-rollback"
    put_response = client.put(f"/docs/{doc_id}", json=_sample_payload(doc_id))
    assert put_response.status_code == 200

    payload = _sample_contract_payload(
        input_hash="c" * 64,
        output_hash="d" * 64,
        padding_violation_count=2,
        tie_break_changed=True,
    )
    response = client.post(f"/docs/{doc_id}/polygon-handoff/verify-contract", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "rollback_required"
    assert body["rollbackRequired"] is True
    assert body["failureReasons"] == ["paddingViolationCount>0", "tieBreakOrderChanged=true"]


def test_verify_polygon_handoff_contract_rejects_invalid_hash_shape(client: TestClient) -> None:
    doc_id = "doc-handoff-invalid"
    put_response = client.put(f"/docs/{doc_id}", json=_sample_payload(doc_id))
    assert put_response.status_code == 200

    payload = _sample_contract_payload(
        input_hash="not-a-sha256",
        output_hash="e" * 64,
        padding_violation_count=0,
        tie_break_changed=False,
    )
    response = client.post(f"/docs/{doc_id}/polygon-handoff/verify-contract", json=payload)

    assert response.status_code == 422
