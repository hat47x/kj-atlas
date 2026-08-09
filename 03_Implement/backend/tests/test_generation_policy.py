from hashlib import sha256

import pytest

from kj_atlas_api.generation_policy import (
    GenerationMetadata,
    GenerationOrigin,
    GenerationReason,
    GenerationRetentionPolicy,
    GenerationTier,
    InvalidGenerationMetadata,
)


def _metadata(**overrides: object) -> GenerationMetadata:
    values: dict[str, object] = {
        "revision_id": "rev-1",
        "document_id": "doc-1",
        "content_digest": sha256(b"content").hexdigest(),
        "parent_revision_ids": ("rev-0",),
        "reason": GenerationReason.MANUAL_SAVE,
        "origin": GenerationOrigin.HUMAN,
        "created_at": "2026-08-09T00:00:00Z",
    }
    values.update(overrides)
    return GenerationMetadata(**values)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("reason", "tier"),
    [
        (GenerationReason.AUTOSAVE, GenerationTier.EPHEMERAL),
        (GenerationReason.MANUAL_SAVE, GenerationTier.CHECKPOINT),
        (GenerationReason.AI_PROPOSAL, GenerationTier.CHECKPOINT),
        (GenerationReason.HUMAN_REVIEW, GenerationTier.GOVERNED),
        (GenerationReason.SHARE, GenerationTier.GOVERNED),
    ],
)
def test_reason_determines_metadata_tier(
    reason: GenerationReason, tier: GenerationTier
) -> None:
    assert _metadata(reason=reason).tier is tier


def test_ephemeral_revision_rejects_actor_and_ai_metadata() -> None:
    metadata = _metadata(
        reason=GenerationReason.AUTOSAVE,
        origin=GenerationOrigin.SYSTEM,
        actor_ref="actor-1",
    )

    with pytest.raises(InvalidGenerationMetadata, match="minimal metadata"):
        metadata.validate()


def test_ai_proposal_requires_separate_run_reference() -> None:
    valid = _metadata(
        reason=GenerationReason.AI_PROPOSAL,
        origin=GenerationOrigin.AI_PROPOSAL,
        ai_run_ref="ai-run-1",
    )
    valid.validate()

    with pytest.raises(InvalidGenerationMetadata, match="AI run reference"):
        _metadata(
            reason=GenerationReason.AI_PROPOSAL,
            origin=GenerationOrigin.AI_PROPOSAL,
        ).validate()


def test_human_acceptance_links_proposal_without_relabeling_it_as_ai_authored() -> None:
    accepted = _metadata(
        reason=GenerationReason.HUMAN_ACCEPTANCE,
        origin=GenerationOrigin.HUMAN,
        source_revision_id="proposal-rev-1",
        actor_ref="opaque-reviewer-1",
    )

    accepted.validate()


def test_human_review_requires_opaque_actor_reference() -> None:
    with pytest.raises(InvalidGenerationMetadata, match="human actor"):
        _metadata(
            reason=GenerationReason.HUMAN_REVIEW,
            origin=GenerationOrigin.HUMAN,
        ).validate()


def test_default_retention_policy_is_bounded_and_valid() -> None:
    policy = GenerationRetentionPolicy()

    policy.validate()
    assert policy.ephemeral_max_per_branch == 50
    assert policy.delta_chain_max_depth == 32
