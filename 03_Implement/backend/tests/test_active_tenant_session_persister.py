"""ADR-0063 D9-6: unit tests for InMemoryActiveTenantSessionPersister."""

from __future__ import annotations

import pytest

import kj_atlas_api.active_tenant_session as active_tenant_session
from kj_atlas_api.active_tenant_session import (
    InMemoryActiveTenantSessionPersister,
    TenantSessionChangedError,
    _new_session_version,
    canonical_tenant_session_version,
)
from kj_atlas_api.tenant_context import TenantContext
from tests.conftest import fake_request, fake_response


def _tenant_ctx(tenant_id: str = "tenant-a") -> TenantContext:
    return TenantContext(
        tenant_id=tenant_id,
        membership_id=f"membership-{tenant_id}",
        resolved_by="verified_claim",
    )


def test_generated_session_versions_are_always_canonical() -> None:
    for _ in range(200_000):
        version = _new_session_version()
        assert canonical_tenant_session_version(version) == version


class TestInMemoryActiveTenantSessionPersister:
    def test_current_version_returns_stable_value(self) -> None:
        persister = InMemoryActiveTenantSessionPersister()
        v1 = persister.current_version(
            request=fake_request(),
            principal_id="user-1",
            active_tenant=_tenant_ctx(),
        )
        v2 = persister.current_version(
            request=fake_request(),
            principal_id="user-1",
            active_tenant=_tenant_ctx(),
        )
        assert v1 == v2
        assert canonical_tenant_session_version(v1) == v1

    def test_different_principals_get_different_versions(self) -> None:
        persister = InMemoryActiveTenantSessionPersister()
        v1 = persister.current_version(
            request=fake_request(),
            principal_id="user-1",
            active_tenant=_tenant_ctx(),
        )
        v2 = persister.current_version(
            request=fake_request(),
            principal_id="user-2",
            active_tenant=_tenant_ctx(),
        )
        assert v1 != v2

    def test_persist_returns_new_version(self) -> None:
        persister = InMemoryActiveTenantSessionPersister()
        expected = persister.current_version(
            request=fake_request(),
            principal_id="user-1",
            active_tenant=_tenant_ctx("tenant-a"),
        )
        new_version = persister.persist(
            request=fake_request(),
            response=fake_response(),
            principal_id="user-1",
            previous_tenant=_tenant_ctx("tenant-a"),
            selected_tenant=_tenant_ctx("tenant-b"),
            expected_tenant_session_version=expected,
        )
        assert new_version != expected
        assert canonical_tenant_session_version(new_version) == new_version

    def test_persist_rejects_wrong_expected_version(self) -> None:
        persister = InMemoryActiveTenantSessionPersister()
        persister.current_version(
            request=fake_request(),
            principal_id="user-1",
            active_tenant=_tenant_ctx(),
        )
        with pytest.raises(TenantSessionChangedError):
            persister.persist(
                request=fake_request(),
                response=fake_response(),
                principal_id="user-1",
                previous_tenant=_tenant_ctx("tenant-a"),
                selected_tenant=_tenant_ctx("tenant-b"),
                expected_tenant_session_version="wrong-version",
            )

    def test_current_version_changes_after_persist(self) -> None:
        persister = InMemoryActiveTenantSessionPersister()
        v1 = persister.current_version(
            request=fake_request(),
            principal_id="user-1",
            active_tenant=_tenant_ctx(),
        )
        v2 = persister.persist(
            request=fake_request(),
            response=fake_response(),
            principal_id="user-1",
            previous_tenant=_tenant_ctx("tenant-a"),
            selected_tenant=_tenant_ctx("tenant-b"),
            expected_tenant_session_version=v1,
        )
        v3 = persister.current_version(
            request=fake_request(),
            principal_id="user-1",
            active_tenant=_tenant_ctx(),
        )
        assert v3 == v2
        assert v3 != v1

    def test_current_version_rotates_legacy_noncanonical_state(self) -> None:
        persister = InMemoryActiveTenantSessionPersister()
        persister._sessions["user-1"] = "_legacy-invalid-version"

        recovered = persister.current_version(
            request=fake_request(),
            principal_id="user-1",
            active_tenant=_tenant_ctx(),
        )

        assert recovered != "_legacy-invalid-version"
        assert canonical_tenant_session_version(recovered) == recovered
        assert persister._sessions["user-1"] == recovered

    def test_persist_validates_new_version_before_state_or_cookie_mutation(
        self,
        monkeypatch,
    ) -> None:  # type: ignore[no-untyped-def]
        persister = InMemoryActiveTenantSessionPersister()
        expected = persister.current_version(
            request=fake_request(),
            principal_id="user-1",
            active_tenant=_tenant_ctx("tenant-a"),
        )
        response = fake_response()
        monkeypatch.setattr(
            active_tenant_session,
            "_new_session_version",
            lambda: "_invalid-new-version",
        )

        with pytest.raises(ValueError, match="not canonical"):
            persister.persist(
                request=fake_request(),
                response=response,
                principal_id="user-1",
                previous_tenant=_tenant_ctx("tenant-a"),
                selected_tenant=_tenant_ctx("tenant-b"),
                expected_tenant_session_version=expected,
            )

        assert persister._sessions["user-1"] == expected
        assert "Kj-Atlas-Tenant-Session-Version" not in response.headers.get(
            "set-cookie", ""
        )
