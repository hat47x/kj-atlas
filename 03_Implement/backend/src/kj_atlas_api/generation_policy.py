from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class GenerationTier(str, Enum):
    EPHEMERAL = "ephemeral"
    CHECKPOINT = "checkpoint"
    GOVERNED = "governed"


class GenerationReason(str, Enum):
    AUTOSAVE = "autosave"
    MANUAL_SAVE = "manual_save"
    ROUND_CHECKPOINT = "round_checkpoint"
    BRANCH = "branch"
    MERGE = "merge"
    IMPORT = "import"
    AI_PROPOSAL = "ai_proposal"
    HUMAN_ACCEPTANCE = "human_acceptance"
    HUMAN_REVIEW = "human_review"
    SHARE = "share"
    EXPORT = "export"


class GenerationOrigin(str, Enum):
    HUMAN = "human"
    AI_PROPOSAL = "ai_proposal"
    SYSTEM = "system"
    IMPORT = "import"


_TIER_BY_REASON: dict[GenerationReason, GenerationTier] = {
    GenerationReason.AUTOSAVE: GenerationTier.EPHEMERAL,
    GenerationReason.MANUAL_SAVE: GenerationTier.CHECKPOINT,
    GenerationReason.ROUND_CHECKPOINT: GenerationTier.CHECKPOINT,
    GenerationReason.BRANCH: GenerationTier.CHECKPOINT,
    GenerationReason.MERGE: GenerationTier.CHECKPOINT,
    GenerationReason.IMPORT: GenerationTier.CHECKPOINT,
    GenerationReason.AI_PROPOSAL: GenerationTier.CHECKPOINT,
    GenerationReason.HUMAN_ACCEPTANCE: GenerationTier.CHECKPOINT,
    GenerationReason.HUMAN_REVIEW: GenerationTier.GOVERNED,
    GenerationReason.SHARE: GenerationTier.GOVERNED,
    GenerationReason.EXPORT: GenerationTier.GOVERNED,
}


class InvalidGenerationMetadata(ValueError):
    pass


@dataclass(frozen=True)
class GenerationMetadata:
    revision_id: str
    document_id: str
    content_digest: str
    parent_revision_ids: tuple[str, ...]
    reason: GenerationReason
    origin: GenerationOrigin
    created_at: str
    actor_ref: str | None = None
    ai_run_ref: str | None = None
    source_revision_id: str | None = None

    @property
    def tier(self) -> GenerationTier:
        return _TIER_BY_REASON[self.reason]

    def validate(self) -> None:
        if not self.revision_id or not self.document_id or not self.created_at:
            raise InvalidGenerationMetadata("revision, document, and creation time are required")
        if len(self.content_digest) != 64 or any(
            character not in "0123456789abcdef" for character in self.content_digest
        ):
            raise InvalidGenerationMetadata("content digest must be lowercase SHA-256")
        if len(self.parent_revision_ids) > 8 or self.revision_id in self.parent_revision_ids:
            raise InvalidGenerationMetadata("revision parents are invalid")
        if self.tier is GenerationTier.EPHEMERAL and (
            self.actor_ref is not None or self.ai_run_ref is not None
        ):
            raise InvalidGenerationMetadata("ephemeral revisions must use minimal metadata")
        if self.reason is GenerationReason.AI_PROPOSAL:
            if self.origin is not GenerationOrigin.AI_PROPOSAL or not self.ai_run_ref:
                raise InvalidGenerationMetadata("AI proposal revisions require an AI run reference")
        elif self.origin is GenerationOrigin.AI_PROPOSAL:
            raise InvalidGenerationMetadata("AI origin is reserved for proposal revisions")
        if self.reason is GenerationReason.HUMAN_ACCEPTANCE:
            if self.origin is not GenerationOrigin.HUMAN or not self.source_revision_id:
                raise InvalidGenerationMetadata(
                    "human acceptance requires a human origin and source proposal revision"
                )
        if self.reason is GenerationReason.HUMAN_REVIEW and (
            self.origin is not GenerationOrigin.HUMAN or not self.actor_ref
        ):
            raise InvalidGenerationMetadata("human review requires an opaque human actor reference")


@dataclass(frozen=True)
class GenerationRetentionPolicy:
    ephemeral_max_per_branch: int = 50
    ephemeral_max_age_days: int = 7
    delta_chain_max_depth: int = 32
    full_snapshot_delta_ratio: float = 0.7

    def validate(self) -> None:
        if self.ephemeral_max_per_branch < 1 or self.ephemeral_max_age_days < 1:
            raise InvalidGenerationMetadata("ephemeral retention bounds must be positive")
        if self.delta_chain_max_depth < 1:
            raise InvalidGenerationMetadata("delta chain depth must be positive")
        if not 0 < self.full_snapshot_delta_ratio <= 1:
            raise InvalidGenerationMetadata("snapshot delta ratio must be between zero and one")
