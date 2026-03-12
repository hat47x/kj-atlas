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
