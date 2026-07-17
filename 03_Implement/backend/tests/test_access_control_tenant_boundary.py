from __future__ import annotations

from dataclasses import replace

import pytest

from kj_atlas_api.access_control import (
    AccessDecision,
    AccessRequest,
    AccessResource,
    AuthContext,
    resolve_access_decision,
)
from kj_atlas_api.tenant_context import TenantContext


class RecordingAdapter:
    name = "recording"

    def __init__(self) -> None:
        self.calls = 0

    def authorize(self, request: AccessRequest) -> AccessDecision:  # noqa: ARG002
        self.calls += 1
        return AccessDecision(allow=True)


@pytest.fixture
def tenant_request() -> AccessRequest:
    return AccessRequest(
        action="read",
        auth=AuthContext(actor_ref="user-1", user_id="user-1"),
        tenant=TenantContext(
            tenant_id="tenant-a",
            membership_id="membership-a",
            resolved_by="verified_claim",
        ),
        resource=AccessResource(
            doc_id="doc-1",
            tenant_id="tenant-a",
        ),
    )


@pytest.mark.parametrize(
    ("request_change", "expected_reason"),
    [
        ({"tenant": None}, "tenant_context_missing"),
        (
            {"resource": AccessResource(doc_id="doc-1")},
            "resource_tenant_missing",
        ),
        (
            {
                "resource": AccessResource(
                    doc_id="doc-1",
                    tenant_id="tenant-b",
                )
            },
            "tenant_mismatch",
        ),
    ],
)
def test_required_tenant_boundary_denies_before_adapter(
    tenant_request: AccessRequest,
    request_change: dict[str, object],
    expected_reason: str,
) -> None:
    adapter = RecordingAdapter()

    decision = resolve_access_decision(
        adapter=adapter,
        request=replace(tenant_request, **request_change),
        fail_safe_mode="read_only",
        require_tenant_scope=True,
    )

    assert decision == AccessDecision(allow=False, reason=expected_reason)
    assert adapter.calls == 0


def test_matching_tenant_boundary_allows_pdp_evaluation(
    tenant_request: AccessRequest,
) -> None:
    adapter = RecordingAdapter()

    decision = resolve_access_decision(
        adapter=adapter,
        request=tenant_request,
        fail_safe_mode="deny",
        require_tenant_scope=True,
    )

    assert decision.allow is True
    assert adapter.calls == 1


def test_compat_mode_preserves_single_tenant_adapter_contract() -> None:
    adapter = RecordingAdapter()
    request = AccessRequest(
        action="read",
        auth=AuthContext(actor_ref="user-1"),
        resource=AccessResource(doc_id="doc-1"),
    )

    decision = resolve_access_decision(
        adapter=adapter,
        request=request,
        fail_safe_mode="read_only",
    )

    assert decision.allow is True
    assert adapter.calls == 1
