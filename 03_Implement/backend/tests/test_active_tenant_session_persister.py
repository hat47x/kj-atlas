"""ADR-0063 D9-6: unit tests for InMemoryActiveTenantSessionPersister."""

from __future__ import annotations

import secrets

import pytest

from kj_atlas_api import active_tenant_session
from kj_atlas_api.active_tenant_session import (
    InMemoryActiveTenantSessionPersister,
    TenantSessionChangedError,
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

    def test_persist_does_not_store_a_noncanonical_version_if_generator_regresses(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """SEC-TENANT-SESSION-01 AC-2/AC-3: persist() must validate the new
        version before storing it or setting the cookie, so a regression in
        the generator cannot permanently pin a principal to a 503 the way the
        original stored-before-validated ordering did."""
        persister = InMemoryActiveTenantSessionPersister()
        expected = persister.current_version(
            request=fake_request(),
            principal_id="user-1",
            active_tenant=_tenant_ctx("tenant-a"),
        )
        monkeypatch.setattr(active_tenant_session, "_new_session_version", lambda: "not canonical, has spaces")

        with pytest.raises(ValueError, match="not canonical"):
            persister.persist(
                request=fake_request(),
                response=fake_response(),
                principal_id="user-1",
                previous_tenant=_tenant_ctx("tenant-a"),
                selected_tenant=_tenant_ctx("tenant-b"),
                expected_tenant_session_version=expected,
            )

        # State must be exactly as it was before the failed persist -- not
        # poisoned with the rejected value, and still resolvable afterward.
        assert persister.current_version(
            request=fake_request(),
            principal_id="user-1",
            active_tenant=_tenant_ctx("tenant-a"),
        ) == expected

    def test_current_version_does_not_store_a_noncanonical_version_if_generator_regresses(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Same defect, first-session-creation path: current_version() also
        generates and stores a version, and must not persist an invalid one
        either."""
        persister = InMemoryActiveTenantSessionPersister()
        monkeypatch.setattr(active_tenant_session, "_new_session_version", lambda: "not canonical, has spaces")

        with pytest.raises(ValueError, match="not canonical"):
            persister.current_version(
                request=fake_request(),
                principal_id="user-1",
                active_tenant=_tenant_ctx("tenant-a"),
            )

        assert persister._sessions.get("user-1") is None


class TestNewSessionVersionCanonicalization:
    """SEC-TENANT-SESSION-01 AC-1: _new_session_version()'s actual output space
    (secrets.token_urlsafe's base64url alphabet, any leading character) must
    always canonicalize. This is a statistical check because the defect was
    itself only a ~3.1% failure rate, not a deterministic one."""

    def test_new_session_version_always_canonicalizes(self) -> None:
        iterations = 200_000
        failures = [
            value
            for value in (secrets.token_urlsafe(32) for _ in range(iterations))
            if active_tenant_session._TENANT_SESSION_VERSION_PATTERN.fullmatch(value) is None
        ]
        assert failures == [], f"{len(failures)}/{iterations} failed canonicalization, e.g. {failures[:5]!r}"
