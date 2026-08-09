from __future__ import annotations

import os
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path, PurePosixPath
from typing import Mapping, Protocol
from uuid import uuid4

from kj_atlas_api.content_store import ContentBlob


class ExternalContentStoreError(RuntimeError):
    pass


class ContentIntegrityError(ExternalContentStoreError):
    pass


def managed_content_locator(*, tenant_id: str, content_id: str) -> str:
    if not tenant_id or not content_id:
        raise ExternalContentStoreError("tenant and content identifiers are required")
    tenant_key = sha256(tenant_id.encode("utf-8")).hexdigest()
    content_key = sha256(content_id.encode("utf-8")).hexdigest()
    return f"tenants/{tenant_key[:2]}/{tenant_key}/content/{content_key}.json"


def _validate_locator(locator: str) -> PurePosixPath:
    path = PurePosixPath(locator)
    if not locator or path.is_absolute() or ".." in path.parts or path.as_posix() != locator:
        raise ExternalContentStoreError("content locator is not a managed relative path")
    return path


def _verified_blob(data: bytes, *, expected_size: int, expected_digest: str) -> ContentBlob:
    digest = sha256(data).hexdigest()
    if len(data) != expected_size or digest != expected_digest:
        raise ContentIntegrityError("stored content does not match its integrity metadata")
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ContentIntegrityError("stored content is not valid UTF-8") from error
    return ContentBlob(text=text, byte_size=len(data), sha256_digest=digest)


class NasContentStore:
    def __init__(self, root: Path) -> None:
        self._root = root.resolve()
        self._root.mkdir(parents=True, exist_ok=True)

    def put(self, *, tenant_id: str, content_id: str, content: ContentBlob) -> str:
        locator = managed_content_locator(tenant_id=tenant_id, content_id=content_id)
        target = self._target(locator)
        target.parent.mkdir(parents=True, exist_ok=True)
        temporary = target.with_name(f".{target.name}.{uuid4().hex}.pending")
        data = content.text.encode("utf-8")
        if len(data) != content.byte_size or sha256(data).hexdigest() != content.sha256_digest:
            raise ContentIntegrityError("content blob metadata does not match its text")
        try:
            with temporary.open("xb") as stream:
                stream.write(data)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, target)
        finally:
            temporary.unlink(missing_ok=True)
        return locator

    def get(self, *, locator: str, expected_size: int, expected_digest: str) -> ContentBlob:
        target = self._target(locator)
        try:
            data = target.read_bytes()
        except FileNotFoundError as error:
            raise ExternalContentStoreError("content object was not found") from error
        return _verified_blob(
            data,
            expected_size=expected_size,
            expected_digest=expected_digest,
        )

    def delete(self, *, locator: str) -> bool:
        target = self._target(locator)
        try:
            target.unlink()
        except FileNotFoundError:
            return False
        return True

    def _target(self, locator: str) -> Path:
        relative = _validate_locator(locator)
        target = (self._root / Path(*relative.parts)).resolve()
        try:
            target.relative_to(self._root)
        except ValueError as error:
            raise ExternalContentStoreError("content locator escapes the managed root") from error
        return target


@dataclass(frozen=True)
class S3Object:
    body: bytes
    metadata: Mapping[str, str]


class S3Client(Protocol):
    def put_object(
        self, *, bucket: str, key: str, body: bytes, metadata: Mapping[str, str]
    ) -> None: ...

    def get_object(self, *, bucket: str, key: str) -> S3Object: ...

    def delete_object(self, *, bucket: str, key: str) -> bool: ...


class S3ContentStore:
    def __init__(self, *, bucket: str, client: S3Client) -> None:
        if not bucket:
            raise ExternalContentStoreError("S3 bucket is required")
        self._bucket = bucket
        self._client = client

    def put(self, *, tenant_id: str, content_id: str, content: ContentBlob) -> str:
        locator = managed_content_locator(tenant_id=tenant_id, content_id=content_id)
        data = content.text.encode("utf-8")
        if len(data) != content.byte_size or sha256(data).hexdigest() != content.sha256_digest:
            raise ContentIntegrityError("content blob metadata does not match its text")
        self._client.put_object(
            bucket=self._bucket,
            key=locator,
            body=data,
            metadata={
                "sha256": content.sha256_digest,
                "byte-size": str(content.byte_size),
            },
        )
        return locator

    def get(self, *, locator: str, expected_size: int, expected_digest: str) -> ContentBlob:
        key = _validate_locator(locator).as_posix()
        stored = self._client.get_object(bucket=self._bucket, key=key)
        if stored.metadata.get("sha256") not in {None, expected_digest}:
            raise ContentIntegrityError("S3 object metadata digest does not match the DB reference")
        return _verified_blob(
            stored.body,
            expected_size=expected_size,
            expected_digest=expected_digest,
        )

    def delete(self, *, locator: str) -> bool:
        key = _validate_locator(locator).as_posix()
        return self._client.delete_object(bucket=self._bucket, key=key)
