from __future__ import annotations

import json
import os

from fastapi.testclient import TestClient

from kj_atlas_api.main import app


DOC_ID = os.getenv("KJ_ATLAS_RECOVERY_DOC_ID", "doc-data-maint-pg-recovery-20260525")
GROUP_ID = "group-recovery-pg"
SNAPSHOT_VERSION = "snapshot-recovery-pg-1"


def _recovery_document() -> dict:
    return {
        "version": 1,
        "id": DOC_ID,
        "title": "PostgreSQL data maintenance recovery rehearsal",
        "createdAt": "2026-05-25T01:00:00Z",
        "updatedAt": "2026-05-25T01:01:00Z",
        "transform": {"panX": 0, "panY": 0, "zoom": 1},
        "cards": [
            {
                "id": "card-reviewed-pg",
                "text": "Reviewed PostgreSQL recovery note",
                "x": 0,
                "y": 0,
                "claimType": "fact",
                "textReviewed": True,
            },
            {
                "id": "card-unreviewed-pg",
                "text": "Unreviewed PostgreSQL recovery note",
                "x": 180,
                "y": 40,
                "claimType": "hypothesis",
                "textReviewed": False,
            },
        ],
        "edges": [
            {
                "id": "edge-pg-1",
                "fromId": "card-reviewed-pg",
                "toId": "card-unreviewed-pg",
                "type": "related",
            }
        ],
        "islands": [
            {
                "id": "island-recovery-pg",
                "cardIds": ["card-reviewed-pg", "card-unreviewed-pg"],
                "shape": {"kind": "rect"},
                "title": "PostgreSQL recovery scope",
            }
        ],
        "mergeSuggestionDecisions": [
            {
                "id": "embedded-decision-pg-1",
                "groupId": GROUP_ID,
                "decision": "defer",
                "decidedAt": "2026-05-25T01:02:00Z",
                "cardIds": ["card-reviewed-pg", "card-unreviewed-pg"],
                "mergedTextDraft": (
                    "Reviewed PostgreSQL recovery note / Unreviewed PostgreSQL recovery note"
                ),
                "editedText": (
                    "Reviewed PostgreSQL recovery note / Unreviewed PostgreSQL recovery note"
                ),
                "rationale": "PostgreSQL backup restore rehearsal",
            }
        ],
    }


def _decision_record(*, decision_id: str, action: str) -> dict:
    return {
        "decisionId": decision_id,
        "groupId": GROUP_ID,
        "action": action,
        "selectedCardIds": ["card-reviewed-pg", "card-unreviewed-pg"],
        "note": "DATA-MAINT-02 PostgreSQL recovery rehearsal",
        "decidedBy": "reviewer:opaque-data-maint-pg",
        "decidedAt": "2026-05-25T01:03:00Z",
        "snapshotVersion": SNAPSHOT_VERSION,
    }


def _require_status(response, expected_status: int, label: str) -> None:
    if response.status_code != expected_status:
        raise RuntimeError(
            f"{label}: expected {expected_status}, got {response.status_code}: {response.text}"
        )


def main() -> None:
    with TestClient(app) as client:
        put_response = client.put(f"/docs/{DOC_ID}", json=_recovery_document())
        _require_status(put_response, 200, "put document")

        for decision_id, action in (("decision-pg-1", "accept"), ("decision-pg-2", "partial")):
            log_response = client.post(
                f"/docs/{DOC_ID}/merge-decision-logs",
                json={"record": _decision_record(decision_id=decision_id, action=action)},
            )
            _require_status(log_response, 201, f"create {decision_id}")

        loaded_response = client.get(f"/docs/{DOC_ID}")
        _require_status(loaded_response, 200, "load document")
        loaded = loaded_response.json()

        group_response = client.get(f"/docs/{DOC_ID}/merge-decision-logs/by-group/{GROUP_ID}")
        _require_status(group_response, 200, "load logs by group")
        group_logs = group_response.json()

        snapshot_response = client.get(
            f"/docs/{DOC_ID}/merge-decision-logs/restore/{SNAPSHOT_VERSION}"
        )
        _require_status(snapshot_response, 200, "load logs by snapshot")
        snapshot_logs = snapshot_response.json()

        safe_export_response = client.post(
            f"/docs/{DOC_ID}/export-audit",
            json={"safeMode": True, "exportKind": "bundle"},
        )
        _require_status(safe_export_response, 403, "safe mode export block")

    summary = {
        "docId": DOC_ID,
        "documentVersion": loaded["version"],
        "cardReviewFlags": [card.get("textReviewed") for card in loaded["cards"]],
        "embeddedDecisionGroup": loaded["mergeSuggestionDecisions"][0]["groupId"],
        "groupLogDecisionIds": [entry["decisionId"] for entry in group_logs],
        "snapshotLogActions": [entry["action"] for entry in snapshot_logs],
        "safeModeExportDetail": safe_export_response.json()["detail"],
    }
    print(json.dumps(summary, ensure_ascii=True, sort_keys=True))


if __name__ == "__main__":
    main()
