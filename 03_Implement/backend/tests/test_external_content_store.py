from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from typing import Mapping

import pytest

from kj_atlas_api.content_store import ContentBlob
from kj_atlas_api.external_content_store import (
    ContentIntegrityError,
    ExternalContentStoreError,
    NasContentStore,
    S3ContentStore,
    S3Object,
    managed_content_locator,
)


class FakeS3Client:
    def __init__(self) -> None:
        self.objects: dict[tuple[str, str], S3Object] = {}

    def put_object(
        self, *, bucket: str, key: str, body: bytes, metadata: Mapping[str, str]
    ) -> None:
        self.objects[(bucket, key)] = S3Object(body=body, metadata=dict(metadata))

    def get_object(self, *, bucket: str, key: str) -> S3Object:
        try:
            return self.objects[(bucket, key)]
        except KeyError as error:
            raise ExternalContentStoreError("content object was not found") from error

    def delete_object(self, *, bucket: str, key: str) -> bool:
        return self.objects.pop((bucket, key), None) is not None


def test_managed_locator_is_deterministic_tenant_scoped_and_opaque() -> None:
    first = managed_content_locator(tenant_id="tenant-a", content_id="document-1")
    again = managed_content_locator(tenant_id="tenant-a", content_id="document-1")
    other_tenant = managed_content_locator(tenant_id="tenant-b", content_id="document-1")

    assert first == again
    assert first != other_tenant
    assert "tenant-a" not in first
    assert "document-1" not in first


def test_nas_store_roundtrip_integrity_atomic_publish_and_idempotent_delete(
    tmp_path: Path,
) -> None:
    store = NasContentStore(tmp_path / "nas-root")
    content = ContentBlob.from_text('{"title":"KJ法"}')
    locator = store.put(tenant_id="tenant-a", content_id="document-1", content=content)

    assert store.get(
        locator=locator,
        expected_size=content.byte_size,
        expected_digest=content.sha256_digest,
    ) == content
    assert not list((tmp_path / "nas-root").rglob("*.pending"))
    assert store.delete(locator=locator) is True
    assert store.delete(locator=locator) is False


def test_nas_store_rejects_escape_and_detects_tampering(tmp_path: Path) -> None:
    store = NasContentStore(tmp_path / "nas-root")
    content = ContentBlob.from_text("original")
    locator = store.put(tenant_id="tenant-a", content_id="document-1", content=content)

    with pytest.raises(ExternalContentStoreError, match="managed relative path"):
        store.get(locator="../secret", expected_size=1, expected_digest="0" * 64)

    stored_path = tmp_path / "nas-root" / Path(*locator.split("/"))
    stored_path.write_text("tampered", encoding="utf-8")
    with pytest.raises(ContentIntegrityError, match="integrity metadata"):
        store.get(
            locator=locator,
            expected_size=content.byte_size,
            expected_digest=content.sha256_digest,
        )


def test_s3_store_roundtrip_uses_key_not_bucket_as_locator() -> None:
    client = FakeS3Client()
    store = S3ContentStore(bucket="private-bucket", client=client)
    content = ContentBlob.from_text('{"cards":[]}')
    locator = store.put(tenant_id="tenant-a", content_id="document-1", content=content)

    assert "private-bucket" not in locator
    assert store.get(
        locator=locator,
        expected_size=content.byte_size,
        expected_digest=content.sha256_digest,
    ) == content
    assert store.delete(locator=locator) is True
    assert store.delete(locator=locator) is False


def test_s3_store_detects_db_or_object_metadata_mismatch() -> None:
    client = FakeS3Client()
    store = S3ContentStore(bucket="private-bucket", client=client)
    content = ContentBlob.from_text("original")
    locator = store.put(tenant_id="tenant-a", content_id="document-1", content=content)
    key = ("private-bucket", locator)
    client.objects[key] = replace(client.objects[key], metadata={"sha256": "0" * 64})

    with pytest.raises(ContentIntegrityError, match="DB reference"):
        store.get(
            locator=locator,
            expected_size=content.byte_size,
            expected_digest=content.sha256_digest,
        )
