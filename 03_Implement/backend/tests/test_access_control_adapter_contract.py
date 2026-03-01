from __future__ import annotations

from kj_atlas_api.access_control import (
    AccessRequest,
    AccessResource,
    AuthContext,
    build_access_control_adapter,
    resolve_access_decision,
)


def _request(*, policy_ref: str | None = None) -> AccessRequest:
    return AccessRequest(
        action="read",
        auth=AuthContext(actor_ref="user-1", roles=("admin",), groups=("group-a",), trace_id="trace-1"),
        resource=AccessResource(doc_id="doc-1", visibility="Org", policy_ref=policy_ref),
        safe_mode=False,
        read_only=False,
    )


def test_noop_adapter_keeps_compatibility_allow_by_default() -> None:
    adapter = build_access_control_adapter(adapter_name="noop")

    decision = resolve_access_decision(adapter=adapter, request=_request(policy_ref="policy-1"), fail_safe_mode="read_only")

    assert adapter.name == "noop"
    assert decision.allow is True
    assert decision.reason is None


def test_unknown_adapter_name_falls_back_to_noop() -> None:
    adapter = build_access_control_adapter(adapter_name="custom-enterprise")

    decision = resolve_access_decision(adapter=adapter, request=_request(policy_ref="policy-1"), fail_safe_mode="deny")

    assert adapter.name == "noop"
    assert decision.allow is True


def test_mock_adapter_contract_deny_and_read_only_paths() -> None:
    adapter = build_access_control_adapter(adapter_name="mock")

    deny_decision = resolve_access_decision(
        adapter=adapter,
        request=_request(policy_ref="mock:deny"),
        fail_safe_mode="read_only",
    )
    read_only_decision = resolve_access_decision(
        adapter=adapter,
        request=_request(policy_ref="mock:read_only"),
        fail_safe_mode="read_only",
    )

    assert adapter.name == "mock"
    assert deny_decision.allow is False
    assert deny_decision.reason == "mock_deny"
    assert read_only_decision.allow is True
    assert read_only_decision.read_only is True
    assert read_only_decision.reason == "mock_read_only"
