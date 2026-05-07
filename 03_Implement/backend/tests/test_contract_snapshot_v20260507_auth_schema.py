from __future__ import annotations

from fastapi.testclient import TestClient

from kj_atlas_api.main import app

CONTRACT_SNAPSHOT_ID = "contract_snapshot_v20260507"


def test_a2_gate_endpoint_signature_snapshot() -> None:
    with TestClient(app) as client:
        response = client.get("/openapi.json")

    assert response.status_code == 200
    paths = response.json()["paths"]
    endpoint = "/admin/provision/hil-rs/a2a3-gate:validate"
    assert endpoint in paths, f"{CONTRACT_SNAPSHOT_ID}: missing endpoint {endpoint}"
    assert "post" in paths[endpoint], f"{CONTRACT_SNAPSHOT_ID}: missing POST method"


def test_a2_gate_request_schema_snapshot_literals() -> None:
    with TestClient(app) as client:
        response = client.get("/openapi.json")

    assert response.status_code == 200
    components = response.json()["components"]["schemas"]
    request_schema = components["A2A3GateValidationRequest"]

    properties = request_schema["properties"]
    assert properties["freezeContractId"]["const"] == "HIL-RS-02-A1-CONTRACT-FREEZE-v1"
    assert properties["schemaVersion"]["const"] == "1.0.0"
    assert properties["overridePolicy"]["const"] == "human_dual_control_only"
    assert properties["pendingDecisionQueueCount"]["const"] == 0
    assert properties["contractLinkLocked"]["const"] is True
    assert properties["sharedResourceFreeze"]["const"] is True
    assert properties["hasUndefinedContractChangeRequest"]["const"] is False
    assert properties["hasSafeModeRegressionRequest"]["const"] is False
    assert properties["hasShareExportLeakageRelaxationRequest"]["const"] is False


def test_a2_gate_response_schema_snapshot_literals() -> None:
    with TestClient(app) as client:
        response = client.get("/openapi.json")

    assert response.status_code == 200
    components = response.json()["components"]["schemas"]
    response_schema = components["A2A3GateValidationResponse"]
    props = response_schema["properties"]

    assert props["schemaVersion"]["default"] == "1.0.0"
    assert props["freezeContractId"]["default"] == "HIL-RS-02-A1-CONTRACT-FREEZE-v1"
