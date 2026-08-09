"""ADR-0063/0064: tests for IdP registration admin API and policy validation."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from kj_atlas_api.db import get_db
from kj_atlas_api.main import app
from kj_atlas_api.models import (
    Base,
    TenantRow,
)
from kj_atlas_api.trusted_saas_runtime import TrustedSaasRuntimePolicy
from tests.conftest import TIMESTAMP


# ---------------------------------------------------------------------------
# Test fixture with proper schema
# ---------------------------------------------------------------------------


@contextmanager
def _admin_test_client(tmp_path) -> Iterator[TestClient]:
    db_path = tmp_path / "admin_idp_test.sqlite3"
    engine = create_engine(f"sqlite:///{db_path}")
    session_local = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    Base.metadata.create_all(bind=engine)

    with session_local() as db:
        db.add(
            TenantRow(
                id="local-default",
                display_name="Local Default",
                lifecycle_state="active",
                created_at=TIMESTAMP,
                updated_at=TIMESTAMP,
            )
        )
        db.add(
            TenantRow(
                id="tenant-a",
                display_name="Tenant A",
                lifecycle_state="active",
                created_at=TIMESTAMP,
                updated_at=TIMESTAMP,
            )
        )
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
            yield client
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


# ---------------------------------------------------------------------------
# Identity Provider Registration API tests
# ---------------------------------------------------------------------------


class TestRegisterIdentityProvider:
    def test_registers_valid_oidc_provider(self, tmp_path) -> None:
        with _admin_test_client(tmp_path) as client:
            resp = client.post(
                "/admin/provision/identity-providers",
                json={
                    "issuer": "https://broker.example.com/issuer",
                    "audience": "kj-atlas",
                    "protocol": "oidc",
                    "jwksUri": "https://broker.example.com/jwks.json",
                },
            )
            assert resp.status_code == 201, f"body={resp.json()}"
            data = resp.json()
            assert data["issuer"] == "https://broker.example.com/issuer"
            assert data["audience"] == "kj-atlas"
            assert data["protocol"] == "oidc"
            assert data["jwksUri"] == "https://broker.example.com/jwks.json"
            assert data["identityProviderId"].startswith("idp-")

    def test_registers_provider_without_jwks_uri(self, tmp_path) -> None:
        with _admin_test_client(tmp_path) as client:
            resp = client.post(
                "/admin/provision/identity-providers",
                json={
                    "issuer": "https://idp2.example.com/issuer",
                    "audience": "app2",
                    "protocol": "oidc",
                },
            )
            assert resp.status_code == 201
            assert resp.json()["jwksUri"] is None

    def test_rejects_unsupported_protocol(self, tmp_path) -> None:
        with _admin_test_client(tmp_path) as client:
            resp = client.post(
                "/admin/provision/identity-providers",
                json={
                    "issuer": "https://x.invalid/issuer",
                    "audience": "x",
                    "protocol": "saml",
                },
            )
            assert resp.status_code == 400
            assert resp.json()["detail"]["code"] == "unsupported_protocol"

    def test_rejects_duplicate_issuer_audience(self, tmp_path) -> None:
        with _admin_test_client(tmp_path) as client:
            payload = {
                "issuer": "https://dup.example.com/issuer",
                "audience": "dup-app",
                "protocol": "oidc",
            }
            r1 = client.post("/admin/provision/identity-providers", json=payload)
            assert r1.status_code == 201
            r2 = client.post("/admin/provision/identity-providers", json=payload)
            assert r2.status_code == 409
            assert r2.json()["detail"]["code"] == "identity_provider_exists"

    def test_rejects_jwks_uri_with_credentials(self, tmp_path) -> None:
        with _admin_test_client(tmp_path) as client:
            resp = client.post(
                "/admin/provision/identity-providers",
                json={
                    "issuer": "https://cred.example.com/issuer",
                    "audience": "app",
                    "jwksUri": "https://user:pass@cred.example.com/jwks.json",
                },
            )
            assert resp.status_code == 400

    def test_rejects_jwks_uri_non_https_non_loopback(self, tmp_path) -> None:
        with _admin_test_client(tmp_path) as client:
            resp = client.post(
                "/admin/provision/identity-providers",
                json={
                    "issuer": "https://plain.example.com/issuer",
                    "audience": "app",
                    "jwksUri": "http://plain.example.com/jwks.json",
                },
            )
            assert resp.status_code == 400

    def test_accepts_jwks_uri_localhost_http(self, tmp_path) -> None:
        with _admin_test_client(tmp_path) as client:
            resp = client.post(
                "/admin/provision/identity-providers",
                json={
                    "issuer": "https://local.example.com/issuer",
                    "audience": "app",
                    "jwksUri": "http://localhost:8080/jwks.json",
                },
            )
            assert resp.status_code == 201

    def test_jwks_uri_empty_string_is_rejected(self, tmp_path) -> None:
        with _admin_test_client(tmp_path) as client:
            resp = client.post(
                "/admin/provision/identity-providers",
                json={
                    "issuer": "https://empty-jwks.example.com/issuer",
                    "audience": "app",
                    "jwksUri": "   ",
                },
            )
            assert resp.status_code == 400

    def test_extra_fields_are_rejected(self, tmp_path) -> None:
        with _admin_test_client(tmp_path) as client:
            resp = client.post(
                "/admin/provision/identity-providers",
                json={
                    "issuer": "https://extra.example.com/issuer",
                    "audience": "app",
                    "protocol": "oidc",
                    "secretKey": "should-not-be-accepted",
                },
            )
            assert resp.status_code == 422


# ---------------------------------------------------------------------------
# Tenant Identity Provider Registration API tests
# ---------------------------------------------------------------------------


class TestRegisterTenantIdentityProvider:
    def test_links_tenant_to_provider_with_external_ref(
        self, tmp_path,
    ) -> None:
        with _admin_test_client(tmp_path) as client:
            idp_resp = client.post(
                "/admin/provision/identity-providers",
                json={
                    "issuer": "https://link.example.com/issuer",
                    "audience": "link-app",
                    "protocol": "oidc",
                },
            )
            assert idp_resp.status_code == 201
            idp_id = idp_resp.json()["identityProviderId"]

            resp = client.post(
                "/admin/provision/tenant-identity-providers",
                json={
                    "tenantId": "local-default",
                    "identityProviderId": idp_id,
                    "externalTenantRef": "org-123",
                },
            )
            assert resp.status_code == 201, f"body={resp.json()}"
            data = resp.json()
            assert data["tenantId"] == "local-default"
            assert data["identityProviderId"] == idp_id
            assert data["externalTenantRef"] == "org-123"

    def test_rejects_nonexistent_tenant(self, tmp_path) -> None:
        with _admin_test_client(tmp_path) as client:
            idp_resp = client.post(
                "/admin/provision/identity-providers",
                json={
                    "issuer": "https://notenant.example.com/issuer",
                    "audience": "no-tenant-app",
                    "protocol": "oidc",
                },
            )
            idp_id = idp_resp.json()["identityProviderId"]

            resp = client.post(
                "/admin/provision/tenant-identity-providers",
                json={
                    "tenantId": "nonexistent-tenant",
                    "identityProviderId": idp_id,
                    "externalTenantRef": "org-xyz",
                },
            )
            assert resp.status_code == 404
            assert resp.json()["detail"]["code"] == "tenant_not_found"

    def test_rejects_nonexistent_provider(self, tmp_path) -> None:
        with _admin_test_client(tmp_path) as client:
            resp = client.post(
                "/admin/provision/tenant-identity-providers",
                json={
                    "tenantId": "local-default",
                    "identityProviderId": "idp-nonexistent",
                    "externalTenantRef": "org-xyz",
                },
            )
            assert resp.status_code == 404
            assert resp.json()["detail"]["code"] == "identity_provider_not_found"

    def test_rejects_duplicate_link(self, tmp_path) -> None:
        with _admin_test_client(tmp_path) as client:
            idp_resp = client.post(
                "/admin/provision/identity-providers",
                json={
                    "issuer": "https://dup-link.example.com/issuer",
                    "audience": "dup-link-app",
                    "protocol": "oidc",
                },
            )
            idp_id = idp_resp.json()["identityProviderId"]

            payload = {
                "tenantId": "local-default",
                "identityProviderId": idp_id,
                "externalTenantRef": "org-dup",
            }
            r1 = client.post(
                "/admin/provision/tenant-identity-providers", json=payload,
            )
            assert r1.status_code == 201
            r2 = client.post(
                "/admin/provision/tenant-identity-providers", json=payload,
            )
            assert r2.status_code == 409


# ---------------------------------------------------------------------------
# TrustedSaasRuntimePolicy validation tests
# ---------------------------------------------------------------------------


class TestTrustedSaasRuntimePolicyJwt:
    def test_default_jwt_fields_are_set(self) -> None:
        policy = TrustedSaasRuntimePolicy(
            database_backend="postgresql",
            allow_jit_provisioning=False,
            access_control_adapter="external_http",
            access_control_fail_safe_mode="deny",
            document_policy_binding_resolver="external_http",
            tenant_capability_resolver="external_http",
        )
        assert policy.jwt_algorithms == "RS256,ES256"
        assert policy.tenant_claim_name == "tenant_ref"

    def test_empty_jwt_algorithms_rejected(self) -> None:
        policy = TrustedSaasRuntimePolicy(
            database_backend="postgresql",
            allow_jit_provisioning=False,
            access_control_adapter="external_http",
            access_control_fail_safe_mode="deny",
            document_policy_binding_resolver="external_http",
            tenant_capability_resolver="external_http",
            jwt_algorithms="   ",
        )
        with pytest.raises(RuntimeError, match="JWT algorithm allowlist"):
            policy.validate()

    def test_empty_tenant_claim_name_rejected(self) -> None:
        policy = TrustedSaasRuntimePolicy(
            database_backend="postgresql",
            allow_jit_provisioning=False,
            access_control_adapter="external_http",
            access_control_fail_safe_mode="deny",
            document_policy_binding_resolver="external_http",
            tenant_capability_resolver="external_http",
            tenant_claim_name="",
        )
        with pytest.raises(RuntimeError, match="tenant claim name"):
            policy.validate()

    def test_full_valid_policy_passes(self) -> None:
        policy = TrustedSaasRuntimePolicy(
            database_backend="postgresql",
            allow_jit_provisioning=False,
            access_control_adapter="external_http",
            access_control_fail_safe_mode="deny",
            document_policy_binding_resolver="external_http",
            tenant_capability_resolver="external_http",
            jwt_algorithms="ES256,RS256",
            tenant_claim_name="org_id",
        )
        policy.validate()  # Should not raise
