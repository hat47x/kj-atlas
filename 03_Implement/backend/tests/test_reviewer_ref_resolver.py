from __future__ import annotations

from kj_atlas_api.reviewer_ref import (
    ReviewerRefResolutionInput,
    build_reviewer_ref_resolver_adapter,
)


def test_user_id_adapter_resolves_user_ref() -> None:
    adapter = build_reviewer_ref_resolver_adapter(adapter_name="user_id")

    resolved = adapter.resolve(
        ReviewerRefResolutionInput(
            user_id="u-1",
            provider="oidc",
            external_uid="subject-1",
            actor_ref="actor:legacy",
        )
    )

    assert resolved.reviewer_ref == "user:u-1"
    assert resolved.owner_ref == "user:u-1"


def test_sso_subject_adapter_prefers_subject() -> None:
    adapter = build_reviewer_ref_resolver_adapter(adapter_name="sso_subject")

    resolved = adapter.resolve(
        ReviewerRefResolutionInput(
            user_id="u-1",
            provider="oidc",
            external_uid="sub-123",
            actor_ref="actor:legacy",
        )
    )

    assert resolved.reviewer_ref == "user:sso:oidc:sub-123"
    assert resolved.owner_ref == "user:sso:oidc:sub-123"


def test_sso_subject_adapter_fallback_without_auth_subject() -> None:
    adapter = build_reviewer_ref_resolver_adapter(adapter_name="sso_subject")

    resolved = adapter.resolve(
        ReviewerRefResolutionInput(
            user_id=None,
            provider=None,
            external_uid=None,
            actor_ref="actor:legacy",
        )
    )

    assert resolved.reviewer_ref == "actor:legacy"
    assert resolved.owner_ref == "actor:legacy"


def test_unknown_adapter_name_falls_back_to_user_id_profile() -> None:
    adapter = build_reviewer_ref_resolver_adapter(adapter_name="not-configured")

    resolved = adapter.resolve(
        ReviewerRefResolutionInput(
            user_id="u-9",
            provider="oidc",
            external_uid="sub-999",
            actor_ref="actor:legacy",
        )
    )

    assert resolved.reviewer_ref == "user:u-9"
    assert resolved.owner_ref == "user:u-9"
