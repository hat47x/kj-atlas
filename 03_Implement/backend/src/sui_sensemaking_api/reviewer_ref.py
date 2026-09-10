from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class ReviewerRefResolutionInput:
    user_id: str | None
    provider: str | None
    external_uid: str | None
    actor_ref: str | None


@dataclass(frozen=True)
class ReviewerRefResolution:
    reviewer_ref: str | None
    owner_ref: str | None


class ReviewerRefResolverAdapter(Protocol):
    name: str

    def resolve(self, request: ReviewerRefResolutionInput) -> ReviewerRefResolution:
        ...


class UserIdReviewerRefResolverAdapter:
    name = "user_id"

    def resolve(self, request: ReviewerRefResolutionInput) -> ReviewerRefResolution:
        if request.user_id:
            ref = f"user:{request.user_id}"
            return ReviewerRefResolution(reviewer_ref=ref, owner_ref=ref)
        return ReviewerRefResolution(reviewer_ref=request.actor_ref, owner_ref=request.actor_ref)


class SsoSubjectReviewerRefResolverAdapter:
    name = "sso_subject"

    def __init__(self) -> None:
        self._fallback = UserIdReviewerRefResolverAdapter()

    def resolve(self, request: ReviewerRefResolutionInput) -> ReviewerRefResolution:
        if request.provider and request.external_uid:
            ref = f"user:sso:{request.provider}:{request.external_uid}"
            return ReviewerRefResolution(reviewer_ref=ref, owner_ref=ref)
        return self._fallback.resolve(request)


def build_reviewer_ref_resolver_adapter(*, adapter_name: str) -> ReviewerRefResolverAdapter:
    if adapter_name == "user_id":
        return UserIdReviewerRefResolverAdapter()
    if adapter_name == "sso_subject":
        return SsoSubjectReviewerRefResolverAdapter()
    return UserIdReviewerRefResolverAdapter()
