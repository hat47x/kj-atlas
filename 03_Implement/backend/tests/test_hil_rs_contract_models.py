from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from kj_atlas_api.models import CritiqueInput, ReproposalDiff, ReviewAttribution


def _now() -> datetime:
    return datetime.now(timezone.utc)


def test_critique_input_requires_schema_version_1_0_0() -> None:
    with pytest.raises(ValidationError):
        CritiqueInput(
            schemaVersion="2.0.0",
            critiqueId="crit-1",
            targetRef="card:c1",
            critiqueType="too_close",
            createdAt=_now(),
            iteration=1,
        )


def test_reproposal_diff_op_requires_before_or_after() -> None:
    with pytest.raises(ValidationError):
        ReproposalDiff(
            proposalId="p1",
            basedOnIteration=1,
            traceKey="crit-1:p1",
            diffOps=[
                {
                    "opId": "op-1",
                    "opType": "move",
                    "targetRef": "card:c1",
                }
            ],
        )


def test_review_attribution_requires_review_fields_for_human_reviewed() -> None:
    with pytest.raises(ValidationError):
        ReviewAttribution(
            schemaVersion="1.0.0",
            reviewState="human_reviewed",
            auditRecordedAt=_now(),
        )


def test_review_attribution_allows_unreviewed_without_reviewer_ref() -> None:
    validated = ReviewAttribution(
        schemaVersion="1.0.0",
        reviewState="unreviewed",
        auditRecordedAt=_now(),
    )
    assert validated.reviewerRef is None
    assert validated.reviewedAt is None


def test_critique_input_rejects_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        CritiqueInput(
            schemaVersion="1.0.0",
            critiqueId="crit-2",
            targetRef="card:c2",
            critiqueType="too_far",
            createdAt=_now(),
            iteration=2,
            unexpectedField="not-allowed",
        )


def test_reproposal_diff_rejects_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        ReproposalDiff(
            proposalId="p2",
            basedOnIteration=2,
            traceKey="crit-2:p2",
            diffOps=[
                {
                    "opId": "op-2",
                    "opType": "add",
                    "targetRef": "card:c2",
                    "after": {"x": 10, "y": 20},
                }
            ],
            unexpectedField="not-allowed",
        )


def test_review_attribution_rejects_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        ReviewAttribution(
            schemaVersion="1.0.0",
            reviewState="unreviewed",
            auditRecordedAt=_now(),
            unexpectedField="not-allowed",
        )


def test_critique_input_rejects_unknown_target_ref_kind() -> None:
    with pytest.raises(ValidationError):
        CritiqueInput(
            schemaVersion="1.0.0",
            critiqueId="crit-3",
            targetRef="island:i1",
            critiqueType="feels_off",
            createdAt=_now(),
            iteration=1,
        )


def test_review_attribution_rejects_email_like_reviewer_ref() -> None:
    with pytest.raises(ValidationError):
        ReviewAttribution(
            schemaVersion="1.0.0",
            reviewState="human_reviewed",
            reviewedAt=_now(),
            reviewerRef="alice@example.com",
            auditRecordedAt=_now(),
        )

def test_review_attribution_defaults_override_policy() -> None:
    validated = ReviewAttribution(
        schemaVersion="1.0.0",
        reviewState="unreviewed",
        auditRecordedAt=_now(),
    )
    assert validated.overridePolicy == "human_dual_control_only"


def test_review_attribution_rejects_email_like_owner_ref() -> None:
    with pytest.raises(ValidationError):
        ReviewAttribution(
            schemaVersion="1.0.0",
            reviewState="human_reviewed",
            reviewedAt=_now(),
            reviewerRef="user:u-1",
            ownerRef="owner@example.com",
            auditRecordedAt=_now(),
        )
