"""SAAS-TENANT-01 AC-4: Document read から外部PDP不達までのfail-closed縦断証拠。"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from types import SimpleNamespace
from urllib import error as urllib_error

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from kj_atlas_api.access_control import (
    AuthContext,
    ExternalPolicyAccessControlAdapter,
    ExternalPolicyAdapterConfig,
)
from kj_atlas_api.db import get_db
from kj_atlas_api.main import app
from kj_atlas_api.models import LOCAL_DEFAULT_TENANT_ID, Base
from kj_atlas_api.tenant_context import TenantContext


@contextmanager
def _sqlite_client(tmp_path) -> Iterator[TestClient]:
    db_path = tmp_path / "saas_document_read_pdp_outage.sqlite3"
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
        "title": "pdp-outage-secret-title",
        "createdAt": "2026-09-05T00:00:00Z",
        "updatedAt": "2026-09-05T00:00:00Z",
        "transform": {"panX": 0, "panY": 0, "zoom": 1},
        "cards": [
            {
                "id": "card-1",
                "text": "pdp-outage-secret-card-body",
                "x": 0,
                "y": 0,
            }
        ],
        "edges": [],
        "islands": [],
    }


def test_saas_document_read_denies_without_body_when_external_pdp_transport_is_down(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The request reaches the real external-policy adapter transport boundary.

    A document is seeded while the local-compatible profile is active. The same
    document is then read through the SaaS request path with a server-resolved
    tenant session and an external PDP adapter whose transport is unreachable.
    The route must deny before returning any document content.
    """

    monkeypatch.setattr(
        "kj_atlas_api.routes.docs.resolve_trusted_saas_request_session",
        lambda **_: SimpleNamespace(
            identity=SimpleNamespace(
                auth_context=AuthContext(actor_ref="user-1", user_id="user-1"),
            ),
            tenant=TenantContext(
                tenant_id=LOCAL_DEFAULT_TENANT_ID,
                membership_id="membership-1",
                resolved_by="verified_claim",
            ),
            session=SimpleNamespace(tenant_session_version="session-v2"),
        ),
    )

    transport_calls = 0

    def _raise_unreachable(request, timeout_seconds):  # noqa: ANN001, ARG001
        nonlocal transport_calls
        transport_calls += 1
        raise urllib_error.URLError("pdp unavailable")

    monkeypatch.setattr(
        "kj_atlas_api.access_control.open_trusted_http",
        _raise_unreachable,
    )

    with _sqlite_client(tmp_path) as client:
        original_adapter = client.app.state.access_control_adapter
        original_fail_safe_mode = client.app.state.access_control_fail_safe_mode
        original_runtime_profile = client.app.state.runtime_profile
        try:
            client.app.state.access_control_adapter = None
            seed_response = client.put(
                "/docs/doc-pdp-outage",
                json=_sample_payload("doc-pdp-outage"),
            )
            assert seed_response.status_code == 200, seed_response.text

            client.app.state.access_control_adapter = ExternalPolicyAccessControlAdapter(
                config=ExternalPolicyAdapterConfig(
                    endpoint="https://policy.example.local/evaluate",
                    timeout_seconds=0.25,
                )
            )
            client.app.state.access_control_fail_safe_mode = "deny"
            client.app.state.runtime_profile = "saas-multitenant"

            response = client.get(
                "/docs/doc-pdp-outage",
                headers={
                    "KJ-Atlas-Tenant-Session-Version": "session-v2",
                    "x-doc-visibility": "Org",
                    "x-policy-ref": "opa://tenant/document-read/v1",
                },
            )
        finally:
            client.app.state.access_control_adapter = original_adapter
            client.app.state.access_control_fail_safe_mode = original_fail_safe_mode
            client.app.state.runtime_profile = original_runtime_profile

    assert transport_calls == 1
    assert response.status_code == 403
    assert response.json()["detail"] == "Access denied: policy_ref_unreachable"
    assert "pdp-outage-secret-title" not in response.text
    assert "pdp-outage-secret-card-body" not in response.text
