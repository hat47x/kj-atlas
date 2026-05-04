from __future__ import annotations

from fastapi.testclient import TestClient

from kj_atlas_api.main import app


def _valid_payload() -> dict[str, object]:
    return {
        "freezeContractId": "HIL-RS-02-A1-CONTRACT-FREEZE-v1",
        "schemaVersion": "1.0.0",
        "overridePolicy": "human_dual_control_only",
        "contractLinkLocked": True,
        "sharedResourceFreeze": True,
        "a1Status": "Done",
        "pendingDecisionQueueCount": 0,
        "hasUndefinedContractChangeRequest": False,
        "hasSafeModeRegressionRequest": False,
        "hasShareExportLeakageRelaxationRequest": False,
    }


def test_validate_gate_accepts_frozen_contract_values() -> None:
    with TestClient(app) as client:
        response = client.post("/admin/provision/hil-rs/a2a3-gate:validate", json=_valid_payload())

    assert response.status_code == 200
    assert response.json() == {
        "go": True,
        "schemaVersion": "1.0.0",
        "freezeContractId": "HIL-RS-02-A1-CONTRACT-FREEZE-v1",
    }


def test_validate_gate_rejects_non_frozen_schema_version() -> None:
    payload = _valid_payload()
    payload["schemaVersion"] = "2.0.0"

    with TestClient(app) as client:
        response = client.post("/admin/provision/hil-rs/a2a3-gate:validate", json=payload)

    assert response.status_code == 422
