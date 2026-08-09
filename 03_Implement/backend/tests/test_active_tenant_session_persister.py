"""ADR-0063 D9-6: unit tests for InMemoryActiveTenantSessionPersister."""

from __future__ import annotations

import pytest
from starlette.requests import Request
from starlette.responses import Response

from kj_atlas_api.active_tenant_session import (
    InMemoryActiveTenantSessionPersister,
    TenantSessionChangedError,
    canonical_tenant_session_version,
)
from kj_atlas_api.tenant_context import TenantContext

_FAKE_SCOPE: dict = {"type": "http", "method": "GET", "path": "/"}


def _fake_request() -> Request:
    return Request(scope=_FAKE_SCOPE)


def _fake_response() -> Response:
    return Response()


def _tenant_ctx(tenant_id: str = "tenant-a") -> TenantContext:
    return TenantContext(
        tenant_id=tenant_id,
        membership_id=f"membership-{tenant_id}",
        resolved_by="verified_claim",
    )


class TestInMemoryActiveTenantSessionPersister:
    def test_current_version_returns_stable_value(self) -> None:
        persister = InMemoryActiveTenantSessionPersister()
        v1 = persister.current_version(
            request=_fake_request(),
            principal_id="user-1",
            active_tenant=_tenant_ctx(),
        )
        v2 = persister.current_version(
            request=_fake_request(),
            principal_id="user-1",
            active_tenant=_tenant_ctx(),
        )
        assert v1 == v2
        assert canonical_tenant_session_version(v1) == v1

    def test_different_principals_get_different_versions(self) -> None:
        persister = InMemoryActiveTenantSessionPersister()
        v1 = persister.current_version(
            request=_fake_request(),
            principal_id="user-1",
            active_tenant=_tenant_ctx(),
        )
        v2 = persister.current_version(
            request=_fake_request(),
            principal_id="user-2",
            active_tenant=_tenant_ctx(),
        )
        assert v1 != v2

    def test_persist_returns_new_version(self) -> None:
        persister = InMemoryActiveTenantSessionPersister()
        expected = persister.current_version(
            request=_fake_request(),
            principal_id="user-1",
            active_tenant=_tenant_ctx("tenant-a"),
        )
        new_version = persister.persist(
            request=_fake_request(),
            response=_fake_response(),
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
            request=_fake_request(),
            principal_id="user-1",
            active_tenant=_tenant_ctx(),
        )
        with pytest.raises(TenantSessionChangedError):
            persister.persist(
                request=_fake_request(),
                response=_fake_response(),
                principal_id="user-1",
                previous_tenant=_tenant_ctx("tenant-a"),
                selected_tenant=_tenant_ctx("tenant-b"),
                expected_tenant_session_version="wrong-version",
            )

    def test_current_version_changes_after_persist(self) -> None:
        persister = InMemoryActiveTenantSessionPersister()
        v1 = persister.current_version(
            request=_fake_request(),
            principal_id="user-1",
            active_tenant=_tenant_ctx(),
        )
        v2 = persister.persist(
            request=_fake_request(),
            response=_fake_response(),
            principal_id="user-1",
            previous_tenant=_tenant_ctx("tenant-a"),
            selected_tenant=_tenant_ctx("tenant-b"),
            expected_tenant_session_version=v1,
        )
        v3 = persister.current_version(
            request=_fake_request(),
            principal_id="user-1",
            active_tenant=_tenant_ctx(),
        )
        assert v3 == v2
        assert v3 != v1
