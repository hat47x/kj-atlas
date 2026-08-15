"""AI-MODEL-GOVERNANCE-01 R1/R3: model/provider registry + tenant allowlist.

Covers dynamic provider/model registration, listing, disable, the tenant
allowlist set/get, env-provider seeding, and control-plane auth on the admin
surface.
"""

from __future__ import annotations

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
    TenantModelAllowlistRow,
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


def test_tenant_allowlist_set_get(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(settings, "admin_api_key", _ADMIN_KEY)

    with _client(tmp_path) as (client, _session_local):
        client.post("/admin/provision/models/providers", json={"id": "p", "providerKind": "external", "displayName": "P"}, headers={"X-Admin-Api-Key": _ADMIN_KEY})
        for model_id in ("m1", "m2", "m3"):
            client.post("/admin/provision/models", json={"id": model_id, "providerId": "p", "displayName": model_id}, headers={"X-Admin-Api-Key": _ADMIN_KEY})

        resp = client.put(
            "/admin/provision/models/tenants/tenant-a/allowlist",
            json={"modelIds": ["m1", "m3"]},
            headers={"X-Admin-Api-Key": _ADMIN_KEY},
        )
        assert resp.status_code == 200, resp.text

        got = client.get("/admin/provision/models/tenants/tenant-a/allowlist", headers={"X-Admin-Api-Key": _ADMIN_KEY}).json()
        assert got["modelIds"] == ["m1", "m3"]


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
