from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from typing import Protocol

from kj_atlas_api.models import DocumentRow, InquiryBundleRow, MergeDecisionLogRow
from kj_atlas_api.tenant_context import TenantContext


@dataclass(frozen=True)
class ContentBlob:
    text: str
    byte_size: int
    sha256_digest: str

    @classmethod
    def from_text(cls, text: str) -> ContentBlob:
        encoded = text.encode("utf-8")
        return cls(text=text, byte_size=len(encoded), sha256_digest=sha256(encoded).hexdigest())


@dataclass(frozen=True)
class VersionedDocumentContent:
    row: DocumentRow
    content: ContentBlob


@dataclass(frozen=True)
class ReplaceableBundleContent:
    row: InquiryBundleRow
    content: ContentBlob


@dataclass(frozen=True)
class AppendOnlyLogContent:
    row: MergeDecisionLogRow
    content: ContentBlob


class VersionedDocumentContentStore(Protocol):
    def load(self, *, tenant: TenantContext, doc_id: str) -> VersionedDocumentContent | None: ...

    def save(
        self,
        *,
        tenant: TenantContext,
        doc_id: str,
        version: int,
        updated_at: str,
        content: ContentBlob,
    ) -> VersionedDocumentContent: ...


class ReplaceableBundleContentStore(Protocol):
    def load(
        self, *, tenant: TenantContext, journey_id: str
    ) -> ReplaceableBundleContent | None: ...

    def replace(
        self,
        *,
        tenant: TenantContext,
        journey_id: str,
        updated_at: str,
        content: ContentBlob,
    ) -> ReplaceableBundleContent: ...

    def delete(self, *, tenant: TenantContext, journey_id: str) -> bool: ...


class AppendOnlyLogContentStore(Protocol):
    def append(
        self,
        *,
        tenant: TenantContext,
        doc_id: str,
        decision_id: str,
        group_id: str,
        snapshot_version: str,
        decided_at: str,
        content: ContentBlob,
    ) -> AppendOnlyLogContent: ...

    def list_by_group(
        self, *, tenant: TenantContext, doc_id: str, group_id: str
    ) -> list[AppendOnlyLogContent]: ...

    def list_by_snapshot(
        self, *, tenant: TenantContext, doc_id: str, snapshot_version: str
    ) -> list[AppendOnlyLogContent]: ...
