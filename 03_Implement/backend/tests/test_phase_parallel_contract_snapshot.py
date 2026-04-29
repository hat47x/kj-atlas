from __future__ import annotations

from fastapi.testclient import TestClient

from kj_atlas_api.main import app
from kj_atlas_api.models import Base


# Stream B mock contract snapshot for parallel work.
CONTRACT_SNAPSHOT_ID = "ce0-contract-freeze-2026-04-27"


def test_api_signature_snapshot_keeps_minimum_paths_and_methods() -> None:
    expected_paths = {
        "/healthz": {"get"},
        "/docs/{doc_id}": {"get", "put"},
        "/docs/{doc_id}/merge-decision-logs": {"post"},
        "/docs/{doc_id}/merge-decision-logs/by-group/{group_id}": {"get"},
        "/docs/{doc_id}/merge-decision-logs/restore/{snapshot_version}": {"get"},
        "/docs/{doc_id}/similar-candidate-groups": {"get"},
        "/context/query": {"post"},
        "/context/bundle": {"post"},
        "/ai/suggest-merges": {"post"},
        "/ai/suggest-layout": {"post"},
        "/ai/summarize-island-relation": {"post"},
        "/admin/provision/users": {"post"},
        "/context/bundles:resolve": {"post"},
        "/context/v1/bundles:resolve": {"post"},
    }

    with TestClient(app) as client:
        response = client.get("/openapi.json")

    assert response.status_code == 200
    spec = response.json()
    assert spec["info"]["title"] == "kj-atlas API"

    for path, methods in expected_paths.items():
        assert path in spec["paths"], f"{CONTRACT_SNAPSHOT_ID}: missing path {path}"
        assert methods.issubset(spec["paths"][path].keys()), (
            f"{CONTRACT_SNAPSHOT_ID}: {path} missing methods {sorted(methods - set(spec['paths'][path].keys()))}"
        )


def test_db_signature_snapshot_keeps_minimum_columns() -> None:
    expected_table_columns = {
        "documents": {"id", "version", "updated_at", "payload_json"},
        "users": {"id", "display_name", "email", "lifecycle_state", "created_at", "updated_at"},
        "user_identities": {"id", "user_id", "provider", "external_uid", "created_at"},
        "merge_decision_logs": {
            "id",
            "doc_id",
            "decision_id",
            "group_id",
            "snapshot_version",
            "decided_at",
            "payload_json",
        },
    }

    for table_name, columns in expected_table_columns.items():
        assert table_name in Base.metadata.tables, f"{CONTRACT_SNAPSHOT_ID}: missing table {table_name}"
        actual_columns = set(Base.metadata.tables[table_name].columns.keys())
        assert columns.issubset(actual_columns), (
            f"{CONTRACT_SNAPSHOT_ID}: {table_name} missing columns {sorted(columns - actual_columns)}"
        )
