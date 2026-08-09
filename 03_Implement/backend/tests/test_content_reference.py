from hashlib import sha256

import pytest

from kj_atlas_api.content_reference import (
    ContentObjectReference,
    ContentStorageBackend,
    ContentStorageState,
    InvalidContentReference,
    require_content_state_transition,
)


def _reference(
    *, backend: ContentStorageBackend, locator: str | None
) -> ContentObjectReference:
    return ContentObjectReference(
        content_id="content-1",
        tenant_id="tenant-a",
        backend=backend,
        locator=locator,
        state=ContentStorageState.PENDING,
        byte_size=3,
        sha256_digest=sha256(b"KJ").hexdigest(),
        schema_version="document-v1",
    )


def test_database_content_has_no_external_locator() -> None:
    assert _reference(backend=ContentStorageBackend.DATABASE, locator=None).locator is None

    with pytest.raises(InvalidContentReference, match="must not have"):
        _reference(backend=ContentStorageBackend.DATABASE, locator="/not-used")


@pytest.mark.parametrize("backend", [ContentStorageBackend.NAS, ContentStorageBackend.S3])
def test_external_content_requires_a_managed_locator(backend: ContentStorageBackend) -> None:
    assert _reference(backend=backend, locator="tenant-a/content-1").locator

    with pytest.raises(InvalidContentReference, match="requires a managed locator"):
        _reference(backend=backend, locator=None)


@pytest.mark.parametrize(
    ("current", "target"),
    [
        (ContentStorageState.PENDING, ContentStorageState.READY),
        (ContentStorageState.PENDING, ContentStorageState.FAILED),
        (ContentStorageState.READY, ContentStorageState.DELETING),
        (ContentStorageState.FAILED, ContentStorageState.PENDING),
        (ContentStorageState.FAILED, ContentStorageState.DELETING),
    ],
)
def test_valid_content_state_transitions(
    current: ContentStorageState, target: ContentStorageState
) -> None:
    require_content_state_transition(current, target)


@pytest.mark.parametrize(
    ("current", "target"),
    [
        (ContentStorageState.PENDING, ContentStorageState.DELETING),
        (ContentStorageState.READY, ContentStorageState.PENDING),
        (ContentStorageState.DELETING, ContentStorageState.READY),
    ],
)
def test_invalid_content_state_transitions_fail_closed(
    current: ContentStorageState, target: ContentStorageState
) -> None:
    with pytest.raises(InvalidContentReference, match="not allowed"):
        require_content_state_transition(current, target)
