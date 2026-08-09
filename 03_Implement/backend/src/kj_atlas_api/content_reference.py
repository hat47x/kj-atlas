from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ContentStorageBackend(str, Enum):
    DATABASE = "database"
    NAS = "nas"
    S3 = "s3"


class ContentStorageState(str, Enum):
    PENDING = "pending"
    READY = "ready"
    DELETING = "deleting"
    FAILED = "failed"


_ALLOWED_TRANSITIONS: dict[ContentStorageState, frozenset[ContentStorageState]] = {
    ContentStorageState.PENDING: frozenset(
        {ContentStorageState.READY, ContentStorageState.FAILED}
    ),
    ContentStorageState.READY: frozenset(
        {ContentStorageState.DELETING, ContentStorageState.FAILED}
    ),
    ContentStorageState.DELETING: frozenset(
        {ContentStorageState.FAILED}
    ),
    ContentStorageState.FAILED: frozenset(
        {ContentStorageState.PENDING, ContentStorageState.DELETING}
    ),
}


class InvalidContentReference(ValueError):
    pass


@dataclass(frozen=True)
class ContentObjectReference:
    content_id: str
    tenant_id: str
    backend: ContentStorageBackend
    locator: str | None
    state: ContentStorageState
    byte_size: int
    sha256_digest: str
    schema_version: str

    def __post_init__(self) -> None:
        if self.backend is ContentStorageBackend.DATABASE and self.locator is not None:
            raise InvalidContentReference("database content must not have an external locator")
        if self.backend is not ContentStorageBackend.DATABASE and not self.locator:
            raise InvalidContentReference("external content requires a managed locator")
        if self.byte_size < 0:
            raise InvalidContentReference("content byte size must not be negative")
        if len(self.sha256_digest) != 64 or any(
            character not in "0123456789abcdef" for character in self.sha256_digest
        ):
            raise InvalidContentReference("content digest must be lowercase SHA-256")
        if not self.schema_version:
            raise InvalidContentReference("content schema version is required")


def require_content_state_transition(
    current: ContentStorageState, target: ContentStorageState
) -> None:
    if target not in _ALLOWED_TRANSITIONS[current]:
        raise InvalidContentReference(
            f"content state transition is not allowed: {current.value} -> {target.value}"
        )
