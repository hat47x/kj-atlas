"""AI-MODEL-GOVERNANCE-01 R1/R3: model/provider registry + tenant allowlist.

Covers dynamic provider/model registration, listing, disable, the tenant
allowlist set/get, env-provider seeding, and control-plane auth on the admin
surface.
"""

from __future__ import annotations

import io
import json
from collections.abc import Iterator
from contextlib import contextmanager

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from kj_atlas_api.db import get_db
from kj_atlas_api.main import app
from kj_atlas_api.models import (
    Base,
    LLMModelRegistryRow,
    LLMProviderRegistryRow,
    TenantRow,
)
from kj_atlas_api.settings import settings

_ADMIN_KEY = "control-plane-model-key"
_BUSINESS_KEY = "business-plane-key"
_NOW = "2026-08-15T00:00:00+00:00"


@contextmanager
def _client(tmp_path) -> Iterator[tuple[TestClient, sessionmaker]]:
    engine = create_engine(f"sqlite:///{tmp_path / 'model_governance.sqlite3'}")
    session_local = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    Base.metadata.create_all(bind=engine)
    with session_local() as db:
        db.add(TenantRow(id="local-default", display_name="Local Default", lifecycle_state="active", created_at=_NOW, updated_at=_NOW))
        db.add(TenantRow(id="tenant-a", display_name="Tenant A", lifecycle_state="active", created_at=_NOW, updated_at=_NOW))
        db.commit()

    def _get_test_db():
        db = session_local()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _get_test_db
    try:
        with TestClient(app) as client:
            # Point the admin-audit recording middleware at the test DB.
            client.app.state.admin_audit_session_factory = session_local
            yield client, session_local
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


def test_register_list_disable_model_flow(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(settings, "admin_api_key", _ADMIN_KEY)
    monkeypatch.setattr(settings, "api_key", _BUSINESS_KEY)

    with _client(tmp_path) as (client, session_local):
        # Register a provider.
        resp = client.post(
            "/admin/provision/models/providers",
            json={"id": "deepseek", "providerKind": "deepseek", "displayName": "DeepSeek", "baseUrl": "https://api.deepseek.com", "apiKeyRef": "KJ_ATLAS_DEEPSEEK_API_KEY"},
            headers={"X-Admin-Api-Key": _ADMIN_KEY},
        )
        assert resp.status_code == 201, resp.text

        # Register two models under it.
        for model_id, caps in (("deepseek-chat", "intermediate,generate"), ("deepseek-reasoner", "final_judgement")):
            resp = client.post(
                "/admin/provision/models",
                json={"id": model_id, "providerId": "deepseek", "displayName": model_id, "capabilities": caps},
                headers={"X-Admin-Api-Key": _ADMIN_KEY},
            )
            assert resp.status_code == 201, resp.text

        # List.
        registry = client.get("/admin/provision/models", headers={"X-Admin-Api-Key": _ADMIN_KEY}).json()
        assert [p["id"] for p in registry["providers"]] == ["deepseek"]
        assert {m["id"] for m in registry["models"]} == {"deepseek-chat", "deepseek-reasoner"}

        # Disable a model -> fail-closed lifecycle.
        resp = client.patch(
            "/admin/provision/models/deepseek-reasoner",
            json={"lifecycleState": "disabled"},
            headers={"X-Admin-Api-Key": _ADMIN_KEY},
        )
        assert resp.status_code == 200, resp.text
        with session_local() as db:
            assert db.get(LLMModelRegistryRow, "deepseek-reasoner").lifecycle_state == "disabled"


def test_provider_api_key_ref_never_exposed_to_api_or_audit(tmp_path, monkeypatch) -> None:
    """AI-MODEL-GOVERNANCE-03 AC-4: apiKeyRef is a reference (env/secret-manager
    key), never a plaintext key, and it must not surface in the registry API
    response or the control-plane audit trail."""
    monkeypatch.setattr(settings, "admin_api_key", _ADMIN_KEY)
    monkeypatch.setattr(settings, "api_key", _BUSINESS_KEY)

    from kj_atlas_api.models import AdminAuditEventRow

    with _client(tmp_path) as (client, session_local):
        api_key_ref = "KJ_ATLAS_DEEPSEEK_API_KEY"
        resp = client.post(
            "/admin/provision/models/providers",
            json={"id": "deepseek", "providerKind": "deepseek", "displayName": "DeepSeek",
                  "baseUrl": "https://api.deepseek.com", "apiKeyRef": api_key_ref},
            headers={"X-Admin-Api-Key": _ADMIN_KEY},
        )
        assert resp.status_code == 201, resp.text

        # 1. The registry list response never echoes apiKeyRef (key or value).
        registry_text = client.get("/admin/provision/models", headers={"X-Admin-Api-Key": _ADMIN_KEY}).text
        assert "apiKeyRef" not in registry_text
        assert api_key_ref not in registry_text

        # 2. The control-plane audit records metadata only -- never the
        #    registration payload (which would carry the secret reference).
        with session_local() as db:
            events = db.query(AdminAuditEventRow).all()
        assert events, "expected at least one admin audit event"
        for ev in events:
            for field in (ev.route or "", ev.operation or "", ev.target or ""):
                assert api_key_ref not in field


def test_provider_api_key_ref_rejects_plaintext_at_registration(tmp_path, monkeypatch) -> None:
    """AI-MODEL-GOVERNANCE-03 AC-4 (DB side): apiKeyRef must be a reference --
    a plaintext secret or an arbitrary env-var name is rejected at the API
    boundary so it is never stored in the registry column."""
    monkeypatch.setattr(settings, "admin_api_key", _ADMIN_KEY)
    monkeypatch.setattr(settings, "api_key", _BUSINESS_KEY)

    with _client(tmp_path) as (client, _session_local):
        base = {"id": "p", "providerKind": "external", "displayName": "P", "baseUrl": "https://example.test"}
        # Plaintext secret (looks like an API key) -> 422, nothing stored.
        resp = client.post(
            "/admin/provision/models/providers",
            json={**base, "apiKeyRef": "sk-this-is-a-plaintext-secret-12345"},
            headers={"X-Admin-Api-Key": _ADMIN_KEY},
        )
        assert resp.status_code == 422, resp.text
        # Arbitrary env-var name (not KJ_ATLAS_*) -> 422.
        resp = client.post(
            "/admin/provision/models/providers",
            json={**base, "apiKeyRef": "MY_RANDOM_API_KEY"},
            headers={"X-Admin-Api-Key": _ADMIN_KEY},
        )
        assert resp.status_code == 422, resp.text
        # Valid allowlisted KJ_ATLAS_* ref -> 201.
        resp = client.post(
            "/admin/provision/models/providers",
            json={**base, "id": "p2", "apiKeyRef": "KJ_ATLAS_DEEPSEEK_API_KEY"},
            headers={"X-Admin-Api-Key": _ADMIN_KEY},
        )
        assert resp.status_code == 201, resp.text
        # Valid secret-manager ref -> 201.
        resp = client.post(
            "/admin/provision/models/providers",
            json={**base, "id": "p3", "apiKeyRef": "secret:prod/deepseek-key"},
            headers={"X-Admin-Api-Key": _ADMIN_KEY},
        )
        assert resp.status_code == 201, resp.text


def test_tenant_allowlist_set_get(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(settings, "admin_api_key", _ADMIN_KEY)

    with _client(tmp_path) as (client, _session_local):
        headers = {"X-Admin-Api-Key": _ADMIN_KEY}
        client.post("/admin/provision/models/providers", json={"id": "p", "providerKind": "external", "displayName": "P"}, headers=headers)
        for model_id in ("m1", "m2", "m3"):
            client.post("/admin/provision/models", json={"id": model_id, "providerId": "p", "displayName": model_id}, headers=headers)

        initial = client.get("/admin/provision/models/tenants/tenant-a/allowlist", headers=headers).json()
        resp = client.put(
            "/admin/provision/models/tenants/tenant-a/allowlist",
            json={"modelIds": ["m1", "m3"], "expectedRevision": initial["revision"]},
            headers=headers,
        )
        assert resp.status_code == 200, resp.text

        got = client.get("/admin/provision/models/tenants/tenant-a/allowlist", headers=headers).json()
        assert got["modelIds"] == ["m1", "m3"]
        assert len(got["revision"]) == 64


def test_registry_create_rejects_duplicate_ids_without_overwriting(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(settings, "admin_api_key", _ADMIN_KEY)

    with _client(tmp_path) as (client, session_local):
        headers = {"X-Admin-Api-Key": _ADMIN_KEY}
        first_provider = client.post(
            "/admin/provision/models/providers",
            json={"id": "p", "providerKind": "local", "displayName": "Original"},
            headers=headers,
        )
        assert first_provider.status_code == 201
        duplicate_provider = client.post(
            "/admin/provision/models/providers",
            json={"id": "p", "providerKind": "deepseek", "displayName": "Replacement"},
            headers=headers,
        )
        assert duplicate_provider.status_code == 409
        assert duplicate_provider.json()["detail"]["code"] == "provider_already_exists"

        client.post(
            "/admin/provision/models/providers",
            json={"id": "p2", "providerKind": "local", "displayName": "P2"},
            headers=headers,
        )
        first_model = client.post(
            "/admin/provision/models",
            json={"id": "m", "providerId": "p", "displayName": "Original Model"},
            headers=headers,
        )
        assert first_model.status_code == 201
        duplicate_model = client.post(
            "/admin/provision/models",
            json={"id": "m", "providerId": "p2", "displayName": "Replacement Model"},
            headers=headers,
        )
        assert duplicate_model.status_code == 409
        assert duplicate_model.json()["detail"]["code"] == "model_already_exists"

        with session_local() as db:
            assert db.get(LLMProviderRegistryRow, "p").provider_kind == "local"
            assert db.get(LLMProviderRegistryRow, "p").display_name == "Original"
            assert db.get(LLMModelRegistryRow, "m").provider_id == "p"
            assert db.get(LLMModelRegistryRow, "m").display_name == "Original Model"


def test_tenant_allowlist_rejects_stale_revision_without_lost_update(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(settings, "admin_api_key", _ADMIN_KEY)

    with _client(tmp_path) as (client, _session_local):
        headers = {"X-Admin-Api-Key": _ADMIN_KEY}
        client.post(
            "/admin/provision/models/providers",
            json={"id": "p", "providerKind": "local", "displayName": "P"},
            headers=headers,
        )
        for model_id in ("m1", "m2"):
            client.post(
                "/admin/provision/models",
                json={"id": model_id, "providerId": "p", "displayName": model_id},
                headers=headers,
            )

        initial = client.get(
            "/admin/provision/models/tenants/tenant-a/allowlist", headers=headers
        ).json()
        first_write = client.put(
            "/admin/provision/models/tenants/tenant-a/allowlist",
            json={"modelIds": ["m1"], "expectedRevision": initial["revision"]},
            headers=headers,
        )
        assert first_write.status_code == 200

        stale_write = client.put(
            "/admin/provision/models/tenants/tenant-a/allowlist",
            json={"modelIds": ["m2"], "expectedRevision": initial["revision"]},
            headers=headers,
        )
        assert stale_write.status_code == 409
        assert stale_write.json()["detail"]["code"] == "model_allowlist_conflict"
        assert stale_write.json()["detail"]["currentRevision"] == first_write.json()["revision"]

        current = client.get(
            "/admin/provision/models/tenants/tenant-a/allowlist", headers=headers
        ).json()
        assert current["modelIds"] == ["m1"]


def test_tenant_allowlist_put_without_expected_revision_is_rejected_428(tmp_path, monkeypatch) -> None:
    """OPS-ADMIN-CONCURRENCY-01 AC-4: the compatibility window for an
    unconditional PUT is over (Maintainer decision, 2026-08-26). A direct API
    caller that omits expectedRevision must be rejected with 428 Precondition
    Required and must NOT mutate the allowlist -- mirroring
    inquiry_bundles.py's If-Match requirement for its update/delete routes.
    A PUT with a correct expectedRevision must still succeed (unaffected by
    this change), and a PUT with a stale expectedRevision must still 409
    (unchanged conflict behavior, proven separately above)."""
    monkeypatch.setattr(settings, "admin_api_key", _ADMIN_KEY)

    with _client(tmp_path) as (client, _session_local):
        headers = {"X-Admin-Api-Key": _ADMIN_KEY}
        client.post(
            "/admin/provision/models/providers",
            json={"id": "p", "providerKind": "local", "displayName": "P"},
            headers=headers,
        )
        for model_id in ("m1", "m2"):
            client.post(
                "/admin/provision/models",
                json={"id": model_id, "providerId": "p", "displayName": model_id},
                headers=headers,
            )

        # Missing expectedRevision -> 428, and the allowlist is NOT mutated.
        missing_revision = client.put(
            "/admin/provision/models/tenants/tenant-a/allowlist",
            json={"modelIds": ["m1"]},
            headers=headers,
        )
        assert missing_revision.status_code == 428, missing_revision.text
        assert missing_revision.json()["detail"] == {
            "code": "model_allowlist_expected_revision_required",
            "message": "expectedRevision is required to update the tenant model allowlist.",
        }
        untouched = client.get(
            "/admin/provision/models/tenants/tenant-a/allowlist", headers=headers
        ).json()
        assert untouched["modelIds"] == []

        # Correct expectedRevision -> still succeeds (428 guard does not
        # interfere with the already-proven happy path).
        correct_write = client.put(
            "/admin/provision/models/tenants/tenant-a/allowlist",
            json={"modelIds": ["m1"], "expectedRevision": untouched["revision"]},
            headers=headers,
        )
        assert correct_write.status_code == 200, correct_write.text

        # Stale expectedRevision -> still 409 model_allowlist_conflict, not 428
        # and not a silent overwrite (unchanged behavior).
        stale_write = client.put(
            "/admin/provision/models/tenants/tenant-a/allowlist",
            json={"modelIds": ["m2"], "expectedRevision": untouched["revision"]},
            headers=headers,
        )
        assert stale_write.status_code == 409, stale_write.text
        assert stale_write.json()["detail"]["code"] == "model_allowlist_conflict"

        final = client.get(
            "/admin/provision/models/tenants/tenant-a/allowlist", headers=headers
        ).json()
        assert final["modelIds"] == ["m1"]


def test_tenant_allowlist_rejects_invalid_targets_without_partial_write(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(settings, "admin_api_key", _ADMIN_KEY)

    with _client(tmp_path) as (client, _session_local):
        headers = {"X-Admin-Api-Key": _ADMIN_KEY}
        client.post(
            "/admin/provision/models/providers",
            json={"id": "p", "providerKind": "external", "displayName": "P"},
            headers=headers,
        )
        for model_id in ("m1", "m2"):
            client.post(
                "/admin/provision/models",
                json={"id": model_id, "providerId": "p", "displayName": model_id},
                headers=headers,
            )
        client.patch(
            "/admin/provision/models/m2",
            json={"lifecycleState": "disabled"},
            headers=headers,
        )

        missing_tenant = client.put(
            "/admin/provision/models/tenants/missing/allowlist",
            json={"modelIds": ["m1"]},
            headers=headers,
        )
        assert missing_tenant.status_code == 404
        assert missing_tenant.json()["detail"]["code"] == "tenant_not_found"

        expected_revision = client.get(
            "/admin/provision/models/tenants/tenant-a/allowlist", headers=headers
        ).json()["revision"]

        invalid_models = client.put(
            "/admin/provision/models/tenants/tenant-a/allowlist",
            json={"modelIds": ["missing-model", "m2"], "expectedRevision": expected_revision},
            headers=headers,
        )
        assert invalid_models.status_code == 422
        assert invalid_models.json()["detail"] == {
            "code": "invalid_model_allowlist",
            "message": "Every allowlisted model must be registered and active.",
            "unknownModelIds": ["missing-model"],
            "inactiveModelIds": ["m2"],
        }

        duplicate_models = client.put(
            "/admin/provision/models/tenants/tenant-a/allowlist",
            json={"modelIds": ["m1", "m1"], "expectedRevision": expected_revision},
            headers=headers,
        )
        assert duplicate_models.status_code == 422
        assert duplicate_models.json()["detail"]["code"] == "duplicate_model_ids"

        current = client.get(
            "/admin/provision/models/tenants/tenant-a/allowlist",
            headers=headers,
        )
        assert current.status_code == 200
        assert current.json()["modelIds"] == []


def test_admin_surface_requires_control_plane(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(settings, "admin_api_key", _ADMIN_KEY)
    monkeypatch.setattr(settings, "api_key", _BUSINESS_KEY)

    with _client(tmp_path) as (client, _session_local):
        resp = client.get("/admin/provision/models", headers={"X-API-Key": _BUSINESS_KEY})
        assert resp.status_code == 401
        assert resp.json()["detail"]["code"] == "control_plane_unauthorized"


def test_env_seeding_registers_provider_and_model(tmp_path, monkeypatch) -> None:
    """U4: the env-configured provider/model is seeded into the registry."""
    monkeypatch.setattr(settings, "llm_provider", "deepseek")
    monkeypatch.setattr(settings, "deepseek_model", "deepseek-chat")
    from kj_atlas_api.model_registry_seed import seed_registry_from_env

    engine = create_engine(f"sqlite:///{tmp_path / 'seed.sqlite3'}")
    session_local = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    Base.metadata.create_all(bind=engine)

    seed_registry_from_env(session_factory=session_local)

    with session_local() as db:
        assert db.get(LLMProviderRegistryRow, "deepseek") is not None
        assert db.get(LLMModelRegistryRow, "deepseek-chat") is not None


def test_allowlist_repository_semantics(tmp_path, monkeypatch) -> None:
    """R3: the allowlist repository stores/clears tenant model ids."""
    monkeypatch.setattr(settings, "llm_provider", "none")
    from kj_atlas_api.model_registry_repository import (
        list_tenant_allowed_model_ids,
        register_model,
        register_provider,
        set_tenant_model_allowlist,
    )

    engine = create_engine(f"sqlite:///{tmp_path / 'repo.sqlite3'}")
    session_local = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    Base.metadata.create_all(bind=engine)
    with session_local() as db:
        db.add(TenantRow(id="t1", display_name="T1", lifecycle_state="active", created_at=_NOW, updated_at=_NOW))
        db.commit()

    with session_local() as db:
        register_provider(db, provider_id="p", provider_kind="external", display_name="P", occurred_at=_NOW)
        register_model(db, model_id="m1", provider_id="p", display_name="M1", occurred_at=_NOW)
        set_tenant_model_allowlist(db, tenant_id="t1", model_ids=["m1"], occurred_at=_NOW)
        db.commit()
        assert list_tenant_allowed_model_ids(db, tenant_id="t1") == {"m1"}
        set_tenant_model_allowlist(db, tenant_id="t1", model_ids=[], occurred_at=_NOW)
        db.commit()
        assert list_tenant_allowed_model_ids(db, tenant_id="t1") == set()


def test_allowlist_enforced_on_ai_route(tmp_path, monkeypatch) -> None:
    """R3: a disallowed model override is rejected 403 before any LLM call."""
    monkeypatch.setattr(settings, "admin_api_key", _ADMIN_KEY)
    monkeypatch.setattr(settings, "api_key", _BUSINESS_KEY)
    monkeypatch.setattr(settings, "llm_provider", "local")

    doc = {
        "version": 1,
        "id": "allow-doc",
        "title": "allowlist test",
        "createdAt": "2026-08-15T00:00:00Z",
        "updatedAt": "2026-08-15T00:00:00Z",
        "transform": {"panX": 0, "panY": 0, "zoom": 1},
        "cards": [{"id": "c1", "text": "alpha", "x": 0, "y": 0, "textReviewed": True}],
        "edges": [],
        "islands": [{"id": "i1", "cardIds": ["c1"]}],
        "readingOrder": ["i1"],
    }

    with _client(tmp_path) as (client, _session_local):
        admin_headers = {"X-Admin-Api-Key": _ADMIN_KEY}
        client.post("/admin/provision/models/providers", json={"id": "p", "providerKind": "local", "displayName": "P"}, headers=admin_headers)
        for model_id in ("m1", "m2"):
            client.post("/admin/provision/models", json={"id": model_id, "providerId": "p", "displayName": model_id}, headers=admin_headers)
        initial_revision = client.get(
            "/admin/provision/models/tenants/local-default/allowlist", headers=admin_headers
        ).json()["revision"]
        client.put(
            "/admin/provision/models/tenants/local-default/allowlist",
            json={"modelIds": ["m1"], "expectedRevision": initial_revision},
            headers=admin_headers,
        )

        # Disallowed override -> 403 model_not_allowed (fail-closed, no LLM call).
        denied = client.post("/ai/suggest-island-summary", json={"doc": doc, "islandId": "i1", "model": "m2"}, headers={"X-API-Key": _BUSINESS_KEY})
        assert denied.status_code == 403, denied.text
        assert denied.json()["detail"]["code"] == "model_not_allowed"
        assert denied.json()["detail"]["allowedModels"] == ["m1"]

        # Allowed override passes the allowlist gate (then fails only because no
        # local LLM base URL is configured -> 503 provider_unavailable, NOT 403).
        allowed = client.post("/ai/suggest-island-summary", json={"doc": doc, "islandId": "i1", "model": "m1"}, headers={"X-API-Key": _BUSINESS_KEY})
        assert allowed.status_code == 503, allowed.text
        assert allowed.json()["detail"]["code"] != "model_not_allowed"


def test_unregistered_model_rejected_under_platform_default(tmp_path, monkeypatch) -> None:
    """AI-MODEL-GOVERNANCE-02: even with an empty tenant allowlist
    (platform-default = "all active registered models allowed"), an unregistered
    or inactive model id must fail closed (403 model_not_registered) before any
    LLM call. The registry, not the allowlist, is the source of truth for what
    is callable."""
    monkeypatch.setattr(settings, "admin_api_key", _ADMIN_KEY)
    monkeypatch.setattr(settings, "api_key", _BUSINESS_KEY)
    monkeypatch.setattr(settings, "llm_provider", "local")

    doc = {
        "version": 1,
        "id": "platform-default-doc",
        "title": "platform default",
        "createdAt": "2026-08-15T00:00:00Z",
        "updatedAt": "2026-08-15T00:00:00Z",
        "transform": {"panX": 0, "panY": 0, "zoom": 1},
        "cards": [{"id": "c1", "text": "alpha", "x": 0, "y": 0, "textReviewed": True}],
        "edges": [],
        "islands": [{"id": "i1", "cardIds": ["c1"]}],
        "readingOrder": ["i1"],
    }

    with _client(tmp_path) as (client, _session_local):
        client.post("/admin/provision/models/providers", json={"id": "p", "providerKind": "local", "displayName": "P"}, headers={"X-Admin-Api-Key": _ADMIN_KEY})
        client.post("/admin/provision/models", json={"id": "m1", "providerId": "p", "displayName": "M1"}, headers={"X-Admin-Api-Key": _ADMIN_KEY})

        # No allowlist set -> platform-default. Unregistered id -> 403 model_not_registered.
        denied = client.post(
            "/ai/suggest-island-summary",
            json={"doc": doc, "islandId": "i1", "model": "totally-bogus-model"},
            headers={"X-API-Key": _BUSINESS_KEY},
        )
        assert denied.status_code == 403, denied.text
        assert denied.json()["detail"]["code"] == "model_not_registered"

        # Registered active model passes the gate (then fails only because no
        # local LLM base URL is configured -> 503 provider_unavailable, NOT 403).
        allowed = client.post(
            "/ai/suggest-island-summary",
            json={"doc": doc, "islandId": "i1", "model": "m1"},
            headers={"X-API-Key": _BUSINESS_KEY},
        )
        assert allowed.status_code == 503, allowed.text
        assert allowed.json()["detail"]["code"] != "model_not_registered"


def test_model_crud_and_allowlist_changes_are_audited(tmp_path, monkeypatch) -> None:
    """R4: model/provider CRUD and allowlist changes land in the admin audit trail."""
    monkeypatch.setattr(settings, "admin_api_key", _ADMIN_KEY)
    monkeypatch.setattr(settings, "api_key", _BUSINESS_KEY)

    with _client(tmp_path) as (client, _session_local):
        admin_headers = {"X-Admin-Api-Key": _ADMIN_KEY}
        client.post("/admin/provision/models/providers", json={"id": "p", "providerKind": "external", "displayName": "P"}, headers=admin_headers)
        client.post("/admin/provision/models", json={"id": "m1", "providerId": "p", "displayName": "M1"}, headers=admin_headers)
        initial_revision = client.get(
            "/admin/provision/models/tenants/tenant-a/allowlist", headers=admin_headers
        ).json()["revision"]
        client.put(
            "/admin/provision/models/tenants/tenant-a/allowlist",
            json={"modelIds": ["m1"], "expectedRevision": initial_revision},
            headers=admin_headers,
        )

        audit = client.get("/admin/provision/audit", headers=admin_headers).json()
        routes = {event["route"] for event in audit["events"]}
        assert "/admin/provision/models/providers" in routes
        assert "/admin/provision/models" in routes
        assert "/admin/provision/models/tenants/tenant-a/allowlist" in routes


def test_available_models_reflects_tenant_allowlist(tmp_path, monkeypatch) -> None:
    """R2: GET /ai/available-models returns the tenant's allowed active models."""
    monkeypatch.setattr(settings, "admin_api_key", _ADMIN_KEY)
    monkeypatch.setattr(settings, "api_key", _BUSINESS_KEY)
    monkeypatch.setattr(settings, "llm_provider", "local")

    with _client(tmp_path) as (client, _session_local):
        admin_headers = {"X-Admin-Api-Key": _ADMIN_KEY}
        client.post("/admin/provision/models/providers", json={"id": "p", "providerKind": "local", "displayName": "P"}, headers=admin_headers)
        for model_id, state in (("m1", "active"), ("m2", "active"), ("m3", "disabled")):
            client.post("/admin/provision/models", json={"id": model_id, "providerId": "p", "displayName": model_id}, headers=admin_headers)
        client.patch("/admin/provision/models/m3", json={"lifecycleState": "disabled"}, headers=admin_headers)

        # No allowlist -> platform-default: m1 + m2 (m3 disabled excluded).
        default_models = client.get("/ai/available-models", headers={"X-API-Key": _BUSINESS_KEY}).json()["models"]
        assert {m["id"] for m in default_models} == {"m1", "m2"}

        # Allowlist [m2] -> only m2 offered.
        initial_revision = client.get(
            "/admin/provision/models/tenants/local-default/allowlist", headers=admin_headers
        ).json()["revision"]
        client.put(
            "/admin/provision/models/tenants/local-default/allowlist",
            json={"modelIds": ["m2"], "expectedRevision": initial_revision},
            headers=admin_headers,
        )
        filtered = client.get("/ai/available-models", headers={"X-API-Key": _BUSINESS_KEY}).json()["models"]
        assert [m["id"] for m in filtered] == ["m2"]


def test_available_models_explains_empty_registry_without_leaking_details(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(settings, "api_key", _BUSINESS_KEY)
    monkeypatch.setattr(settings, "llm_provider", "local")

    with _client(tmp_path) as (client, _session_local):
        response = client.get("/ai/available-models", headers={"X-API-Key": _BUSINESS_KEY})
        assert response.status_code == 200
        assert response.json() == {
            "models": [],
            "unavailableReason": "no_active_models",
        }


def test_available_models_explains_tenant_policy_and_selectable_capability(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(settings, "admin_api_key", _ADMIN_KEY)
    monkeypatch.setattr(settings, "api_key", _BUSINESS_KEY)
    monkeypatch.setattr(settings, "llm_provider", "local")

    with _client(tmp_path) as (client, _session_local):
        admin_headers = {"X-Admin-Api-Key": _ADMIN_KEY}
        client.post(
            "/admin/provision/models/providers",
            json={"id": "p", "providerKind": "local", "displayName": "P"},
            headers=admin_headers,
        )
        for model_id, capabilities in (
            ("allowed-disabled", "intermediate,generate"),
            ("judgement-only", "final_judgement"),
        ):
            client.post(
                "/admin/provision/models",
                json={
                    "id": model_id,
                    "providerId": "p",
                    "displayName": model_id,
                    "capabilities": capabilities,
                },
                headers=admin_headers,
            )
        first_revision = client.get(
            "/admin/provision/models/tenants/local-default/allowlist", headers=admin_headers
        ).json()["revision"]
        client.put(
            "/admin/provision/models/tenants/local-default/allowlist",
            json={"modelIds": ["allowed-disabled"], "expectedRevision": first_revision},
            headers=admin_headers,
        )
        client.patch(
            "/admin/provision/models/allowed-disabled",
            json={"lifecycleState": "disabled"},
            headers=admin_headers,
        )

        policy_empty = client.get(
            "/ai/available-models", headers={"X-API-Key": _BUSINESS_KEY}
        ).json()
        assert policy_empty == {
            "models": [],
            "unavailableReason": "tenant_policy_excludes_all",
        }

        second_revision = client.get(
            "/admin/provision/models/tenants/local-default/allowlist", headers=admin_headers
        ).json()["revision"]
        client.put(
            "/admin/provision/models/tenants/local-default/allowlist",
            json={"modelIds": ["judgement-only"], "expectedRevision": second_revision},
            headers=admin_headers,
        )
        not_selectable = client.get(
            "/ai/available-models", headers={"X-API-Key": _BUSINESS_KEY}
        ).json()
        assert not_selectable == {
            "models": [],
            "unavailableReason": "no_user_selectable_models",
        }


def test_available_models_excludes_final_judgement_only(tmp_path, monkeypatch) -> None:
    """MMR-04: final_judgement-only models are not offered for user selection."""
    monkeypatch.setattr(settings, "admin_api_key", _ADMIN_KEY)
    monkeypatch.setattr(settings, "api_key", _BUSINESS_KEY)
    monkeypatch.setattr(settings, "llm_provider", "local")

    with _client(tmp_path) as (client, _session_local):
        client.post("/admin/provision/models/providers", json={"id": "p", "providerKind": "local", "displayName": "P"}, headers={"X-Admin-Api-Key": _ADMIN_KEY})
        for model_id, caps in (
            ("intermediate-model", "intermediate,generate"),
            ("judgement-only", "final_judgement"),
            ("mixed-model", "intermediate,final_judgement"),
        ):
            client.post("/admin/provision/models", json={"id": model_id, "providerId": "p", "displayName": model_id, "capabilities": caps}, headers={"X-Admin-Api-Key": _ADMIN_KEY})

        available = client.get("/ai/available-models", headers={"X-API-Key": _BUSINESS_KEY}).json()["models"]
        ids = {m["id"] for m in available}
        assert "intermediate-model" in ids
        assert "mixed-model" in ids  # intermediate tier present -> selectable
        assert "judgement-only" not in ids  # final_judgement-only -> excluded (MMR-04)


def test_model_provider_must_match_runtime_transport(tmp_path, monkeypatch) -> None:
    """AI-MODEL-GOVERNANCE-03 short-term fail-closed boundary.

    Registry metadata must not cause a local-runtime process to send a model
    registered under the DeepSeek transport to the local endpoint (or vice
    versa). The UI list and API execution gate use the same intersection.
    """
    monkeypatch.setattr(settings, "admin_api_key", _ADMIN_KEY)
    monkeypatch.setattr(settings, "api_key", _BUSINESS_KEY)
    monkeypatch.setattr(settings, "llm_provider", "local")

    doc = {
        "version": 1,
        "id": "provider-drift-doc",
        "title": "provider drift",
        "createdAt": "2026-08-16T00:00:00Z",
        "updatedAt": "2026-08-16T00:00:00Z",
        "transform": {"panX": 0, "panY": 0, "zoom": 1},
        "cards": [{"id": "c1", "text": "alpha", "x": 0, "y": 0, "textReviewed": True}],
        "edges": [],
        "islands": [{"id": "i1", "cardIds": ["c1"]}],
        "readingOrder": ["i1"],
    }

    with _client(tmp_path) as (client, _session_local):
        admin_headers = {"X-Admin-Api-Key": _ADMIN_KEY}
        client.post(
            "/admin/provision/models/providers",
            json={"id": "deepseek", "providerKind": "deepseek", "displayName": "DeepSeek"},
            headers=admin_headers,
        )
        client.post(
            "/admin/provision/models",
            json={
                "id": "deepseek-chat",
                "providerId": "deepseek",
                "displayName": "DeepSeek Chat",
                "capabilities": "intermediate,generate",
            },
            headers=admin_headers,
        )

        listed = client.get("/ai/available-models", headers={"X-API-Key": _BUSINESS_KEY})
        assert listed.status_code == 200
        assert listed.json()["models"] == []
        assert listed.json()["unavailableReason"] == "provider_unavailable"

        attempted = client.post(
            "/ai/suggest-island-summary",
            json={"doc": doc, "islandId": "i1", "model": "deepseek-chat"},
            headers={"X-API-Key": _BUSINESS_KEY},
        )
        assert attempted.status_code == 503
        assert attempted.json()["detail"] == {
            "code": "model_provider_unavailable",
            "message": "The model's registered provider is not available in this runtime.",
        }


class _StubHTTPResponse:
    """Minimal urlopen()-shaped stub (matches test_llm_provider.py's helper of
    the same name) so kj_atlas_api.llm.provider.open_trusted_http can be
    monkeypatched without a real network call."""

    def __init__(self, body: dict) -> None:
        self._buffer = io.BytesIO(json.dumps(body).encode("utf-8"))

    def read(self, size: int = -1) -> bytes:
        return self._buffer.read(size)

    def __enter__(self) -> "_StubHTTPResponse":
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        return False


def test_dynamic_dispatch_local_and_deepseek_simultaneously(tmp_path, monkeypatch) -> None:
    """AI-MODEL-GOVERNANCE-03 remaining AC: register DeepSeek and local
    providers simultaneously (both configured), register a model under each,
    and prove per-model dynamic dispatch -- the actual behavior change that
    replaces the short-term "model's provider kind must equal the
    process-wide KJ_ATLAS_LLM_PROVIDER" gate covered by
    test_model_provider_must_match_runtime_transport above.

    The runtime primary is "local". A request naming the DeepSeek-registered
    model must reach the DeepSeek transport -- NOT local, and NOT rejected
    just because it differs from KJ_ATLAS_LLM_PROVIDER -- a request naming the
    local-registered model must reach the local transport, and once DeepSeek's
    own required setting (its API key) is removed, its model is rejected with
    the existing model_provider_unavailable shape before any further LLM call
    is attempted (no unhandled exception, no fallback to the wrong provider)."""
    monkeypatch.setattr(settings, "admin_api_key", _ADMIN_KEY)
    monkeypatch.setattr(settings, "api_key", _BUSINESS_KEY)
    monkeypatch.setattr(settings, "llm_provider", "local")
    monkeypatch.setattr(settings, "local_llm_base_url", "http://local-llm.test")
    monkeypatch.setattr(settings, "deepseek_api_key", "sk-test-key")
    monkeypatch.setattr(settings, "deepseek_base_url", "https://api.deepseek.com")

    from kj_atlas_api.llm import provider as llm_provider

    calls: list[str] = []

    def _fake_urlopen(req, timeout_seconds=60):
        calls.append(req.full_url)
        if req.full_url == "http://local-llm.test/generate":
            return _StubHTTPResponse(
                {"text": json.dumps({"candidates": [{"title": "ローカル応答"}]})}
            )
        if req.full_url == "https://api.deepseek.com/v1/chat/completions":
            content = json.dumps({"candidates": [{"title": "DeepSeek応答"}]})
            return _StubHTTPResponse(
                {"choices": [{"message": {"content": content}}]}
            )
        raise AssertionError(f"unexpected endpoint reached: {req.full_url}")

    monkeypatch.setattr(llm_provider, "open_trusted_http", _fake_urlopen)

    with _client(tmp_path) as (client, _session_local):
        admin_headers = {"X-Admin-Api-Key": _ADMIN_KEY}
        business_headers = {"X-API-Key": _BUSINESS_KEY}

        client.post(
            "/admin/provision/models/providers",
            json={"id": "local", "providerKind": "local", "displayName": "Local"},
            headers=admin_headers,
        )
        client.post(
            "/admin/provision/models",
            json={
                "id": "local-model",
                "providerId": "local",
                "displayName": "Local Model",
                "capabilities": "intermediate,generate",
            },
            headers=admin_headers,
        )
        client.post(
            "/admin/provision/models/providers",
            json={"id": "deepseek", "providerKind": "deepseek", "displayName": "DeepSeek"},
            headers=admin_headers,
        )
        client.post(
            "/admin/provision/models",
            json={
                "id": "deepseek-model",
                "providerId": "deepseek",
                "displayName": "DeepSeek Model",
                "capabilities": "intermediate,generate",
            },
            headers=admin_headers,
        )

        # Both models are simultaneously offered -- both are ready even though
        # only "local" is the process-wide KJ_ATLAS_LLM_PROVIDER.
        available = client.get("/ai/available-models", headers=business_headers).json()["models"]
        assert {m["id"] for m in available} == {"local-model", "deepseek-model"}

        # local-model -> the local HTTP transport.
        local_resp = client.post(
            "/ai/suggest-document-title",
            json={"islandTitles": [], "cardTexts": ["alpha"], "model": "local-model", "textReviewed": True},
            headers=business_headers,
        )
        assert local_resp.status_code == 200, local_resp.text
        assert local_resp.json()["candidates"][0]["title"] == "ローカル応答"

        # deepseek-model -> the DeepSeek transport, even though
        # KJ_ATLAS_LLM_PROVIDER is "local" -- this is the actual dynamic
        # dispatch behavior AC-5 asks to prove (not merely gating).
        deepseek_resp = client.post(
            "/ai/suggest-document-title",
            json={"islandTitles": [], "cardTexts": ["alpha"], "model": "deepseek-model", "textReviewed": True},
            headers=business_headers,
        )
        assert deepseek_resp.status_code == 200, deepseek_resp.text
        assert deepseek_resp.json()["candidates"][0]["title"] == "DeepSeek応答"

        assert calls == [
            "http://local-llm.test/generate",
            "https://api.deepseek.com/v1/chat/completions",
        ]

        # Remove DeepSeek's own required setting (its API key). Its model must
        # now be rejected with the existing model_provider_unavailable shape
        # -- fail-closed at the gate, before any further LLM call -- not an
        # unhandled exception and not a silent fallback to the local
        # transport.
        monkeypatch.setattr(settings, "deepseek_api_key", None)
        calls_before = len(calls)
        unconfigured_resp = client.post(
            "/ai/suggest-document-title",
            json={"islandTitles": [], "cardTexts": ["alpha"], "model": "deepseek-model", "textReviewed": True},
            headers=business_headers,
        )
        assert unconfigured_resp.status_code == 503, unconfigured_resp.text
        assert unconfigured_resp.json()["detail"] == {
            "code": "model_provider_unavailable",
            "message": "The model's registered provider is not available in this runtime.",
        }
        assert len(calls) == calls_before  # no LLM call attempted

        # The local model is unaffected by DeepSeek's own config going stale.
        still_local = client.post(
            "/ai/suggest-document-title",
            json={"islandTitles": [], "cardTexts": ["alpha"], "model": "local-model", "textReviewed": True},
            headers=business_headers,
        )
        assert still_local.status_code == 200, still_local.text


def test_dynamic_dispatch_disabled_by_none_kill_switch(tmp_path, monkeypatch) -> None:
    """AI-MODEL-GOVERNANCE-03 design decision: KJ_ATLAS_LLM_PROVIDER=none
    remains a hard kill switch under dynamic dispatch. Even a fully-configured
    alternate provider (deepseek, with its API key set) registered in the DB
    must not become reachable just because a model names it explicitly --
    "none" means AI is off for this process, full stop (AGENTS.md: "KJ_ATLAS_
    LLM_PROVIDER=none でも主要価値が成立する")."""
    monkeypatch.setattr(settings, "admin_api_key", _ADMIN_KEY)
    monkeypatch.setattr(settings, "api_key", _BUSINESS_KEY)
    monkeypatch.setattr(settings, "llm_provider", "none")
    monkeypatch.setattr(settings, "deepseek_api_key", "sk-test-key")
    monkeypatch.setattr(settings, "deepseek_base_url", "https://api.deepseek.com")

    from kj_atlas_api.llm import provider as llm_provider

    def _fail_if_called(req, timeout_seconds=60):
        raise AssertionError("no LLM call should be attempted under the none kill switch")

    monkeypatch.setattr(llm_provider, "open_trusted_http", _fail_if_called)

    with _client(tmp_path) as (client, _session_local):
        admin_headers = {"X-Admin-Api-Key": _ADMIN_KEY}
        client.post(
            "/admin/provision/models/providers",
            json={"id": "deepseek", "providerKind": "deepseek", "displayName": "DeepSeek"},
            headers=admin_headers,
        )
        client.post(
            "/admin/provision/models",
            json={
                "id": "deepseek-model",
                "providerId": "deepseek",
                "displayName": "DeepSeek Model",
                "capabilities": "intermediate,generate",
            },
            headers=admin_headers,
        )

        available = client.get("/ai/available-models", headers={"X-API-Key": _BUSINESS_KEY}).json()
        assert available["models"] == []

        denied = client.post(
            "/ai/suggest-document-title",
            json={"islandTitles": [], "cardTexts": ["alpha"], "model": "deepseek-model", "textReviewed": True},
            headers={"X-API-Key": _BUSINESS_KEY},
        )
        assert denied.status_code == 503, denied.text
        assert denied.json()["detail"]["code"] == "model_provider_unavailable"
