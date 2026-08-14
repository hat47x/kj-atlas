from __future__ import annotations

import json
from typing import Literal
from uuid import uuid4

from sqlalchemy import delete, select, update
from sqlalchemy.orm import Session

from kj_atlas_api.content_store import (
    AppendOnlyLogContent,
    ContentBlob,
    ReplaceableBundleContent,
    VersionedDocumentContent,
)
from kj_atlas_api.generation_codec import canonical_json_bytes, encode_generation
from kj_atlas_api.generation_repository import (
    advance_revision_head,
    load_database_generation_blob,
    save_database_generation_blob,
)
from kj_atlas_api.models import (
    CanvasRevisionHeadRow,
    CanvasRevisionParentRow,
    CanvasRevisionRow,
    DocumentListItem,
    DocumentRow,
    InquiryBundleRow,
    MergeDecisionLogRow,
)
from kj_atlas_api.tenant_context import TenantContext
from kj_atlas_api.tenant_db_guard import apply_database_tenant_context


class DocumentRevisionDivergence(RuntimeError):
    pass


class DatabaseDocumentContentStore:
    def __init__(self, db: Session) -> None:
        self._db = db

    def load(self, *, tenant: TenantContext, doc_id: str) -> VersionedDocumentContent | None:
        apply_database_tenant_context(db=self._db, tenant=tenant)
        row = self._db.scalar(
            select(DocumentRow).where(
                DocumentRow.tenant_id == tenant.tenant_id,
                DocumentRow.id == doc_id,
            )
        )
        if row is None:
            return None
        restored = self._verify_revision_projection(tenant=tenant, row=row)
        content_text = row.payload_json if restored is None else restored.decode("utf-8")
        return VersionedDocumentContent(row=row, content=ContentBlob.from_text(content_text))

    def _verify_revision_projection(
        self, *, tenant: TenantContext, row: DocumentRow
    ) -> bytes | None:
        head = self._db.get(CanvasRevisionHeadRow, (tenant.tenant_id, row.id, "main"))
        if head is None:
            return None
        revision = self._db.get(CanvasRevisionRow, (tenant.tenant_id, head.revision_id))
        if revision is None:
            raise DocumentRevisionDivergence("document revision head is missing")
        restored = load_database_generation_blob(
            self._db,
            tenant=tenant,
            content_digest=revision.content_digest,
        )
        try:
            projected = canonical_json_bytes(json.loads(row.payload_json))
        except (TypeError, ValueError, json.JSONDecodeError) as error:
            raise DocumentRevisionDivergence("document projection is invalid JSON") from error
        if restored != projected:
            raise DocumentRevisionDivergence("document projection differs from revision head")
        return restored

    def _materialize_revision(
        self,
        *,
        tenant: TenantContext,
        row: DocumentRow,
        content: ContentBlob,
        created_at: str,
    ) -> None:
        try:
            value = json.loads(content.text)
        except json.JSONDecodeError as error:
            raise DocumentRevisionDivergence("document content is invalid JSON") from error
        encoded = encode_generation(value)
        head = self._db.get(CanvasRevisionHeadRow, (tenant.tenant_id, row.id, "main"))
        if head is not None:
            current_revision = self._db.get(
                CanvasRevisionRow,
                (tenant.tenant_id, head.revision_id),
            )
            if current_revision is None:
                raise DocumentRevisionDivergence("document revision head is missing")
            if current_revision.content_digest == encoded.content_digest:
                return

        save_database_generation_blob(
            self._db,
            tenant=tenant,
            blob=encoded,
            schema_version=f"document-v{row.version}",
            created_at=created_at,
        )
        self._db.flush()
        revision_id = uuid4().hex
        revision = CanvasRevisionRow(
            tenant_id=tenant.tenant_id,
            revision_id=revision_id,
            doc_id=row.id,
            content_digest=encoded.content_digest,
            generation_tier="checkpoint",
            generation_reason="manual_save",
            generation_origin="human",
            actor_ref=None,
            ai_run_ref=None,
            source_revision_id=None,
            created_at=created_at,
        )
        self._db.add(revision)
        self._db.flush()
        if head is None:
            self._db.add(
                CanvasRevisionHeadRow(
                    tenant_id=tenant.tenant_id,
                    doc_id=row.id,
                    head_name="main",
                    revision_id=revision_id,
                    head_version=1,
                    updated_at=created_at,
                )
            )
            return
        self._db.add(
            CanvasRevisionParentRow(
                tenant_id=tenant.tenant_id,
                revision_id=revision_id,
                parent_revision_id=head.revision_id,
                parent_order=0,
            )
        )
        self._db.flush()
        advance_revision_head(
            self._db,
            tenant=tenant,
            doc_id=row.id,
            head_name="main",
            expected_version=head.head_version,
            new_revision_id=revision_id,
            updated_at=created_at,
        )

    def save(
        self,
        *,
        tenant: TenantContext,
        doc_id: str,
        version: int,
        updated_at: str,
        content: ContentBlob,
        created_by: str | None = None,
    ) -> VersionedDocumentContent:
        stored = self.load(tenant=tenant, doc_id=doc_id)
        if stored is None:
            row = DocumentRow(
                tenant_id=tenant.tenant_id,
                id=doc_id,
                version=version,
                updated_at=updated_at,
                payload_json=content.text,
                # ADR-0073 D1=C / D3=A: the creator is an immutable creation-time
                # fact; nullable for migrated/legacy docs.
                created_by=created_by,
            )
            self._db.add(row)
            self._db.flush()
            self._materialize_revision(
                tenant=tenant,
                row=row,
                content=content,
                created_at=updated_at,
            )
        else:
            row = stored.row
            head = self._db.get(CanvasRevisionHeadRow, (tenant.tenant_id, doc_id, "main"))
            if row.payload_json == content.text:
                row.version = version
                row.updated_at = updated_at
                if head is None:
                    self._materialize_revision(
                        tenant=tenant,
                        row=row,
                        content=content,
                        created_at=updated_at,
                    )
                return VersionedDocumentContent(row=row, content=content)
            # Preserve the legacy projection as the initial parent before replacing it.
            if head is None:
                self._materialize_revision(
                    tenant=tenant,
                    row=row,
                    content=stored.content,
                    created_at=row.updated_at,
                )
                self._db.flush()
            row.version = version
            row.updated_at = updated_at
            row.payload_json = content.text
            self._materialize_revision(
                tenant=tenant,
                row=row,
                content=content,
                created_at=updated_at,
            )
        return VersionedDocumentContent(row=row, content=content)

    def list_documents(self, *, tenant: TenantContext) -> list[DocumentListItem]:
        """List the tenant's document metadata (第2反復: キャンバス一覧の土台).

        SafeMode-independent — only row metadata is exposed (id, title from the
        payload snapshot, creator, lifecycle state, updated_at). Never the card
        content, which the caller must fetch per-document through the normal
        SafeMode-scoped read path.
        """
        apply_database_tenant_context(db=self._db, tenant=tenant)
        rows = self._db.execute(
            select(DocumentRow).where(DocumentRow.tenant_id == tenant.tenant_id)
        ).scalars().all()
        items: list[DocumentListItem] = []
        for row in rows:
            try:
                title = json.loads(row.payload_json).get("title")
                if not isinstance(title, str):
                    title = None
            except (json.JSONDecodeError, TypeError):
                title = None
            items.append(
                DocumentListItem(
                    id=row.id,
                    title=title,
                    created_by=row.created_by,
                    lifecycle_state=row.lifecycle_state,
                    updated_at=row.updated_at,
                )
            )
        items.sort(key=lambda item: item.updated_at, reverse=True)
        return items

    def set_lifecycle_state(
        self, *, tenant: TenantContext, doc_id: str, state: Literal["active", "archived"]
    ) -> bool:
        """ADR-0073 D2=A: transition a document between active / archived.

        Tenant-scoped single UPDATE (apply_database_tenant_context + row guard).
        Returns False when the document does not exist for this tenant.
        """
        apply_database_tenant_context(db=self._db, tenant=tenant)
        result = self._db.execute(
            update(DocumentRow)
            .where(
                DocumentRow.tenant_id == tenant.tenant_id,
                DocumentRow.id == doc_id,
            )
            .values(lifecycle_state=state)
        )
        return result.rowcount > 0


class DatabaseBundleContentStore:
    def __init__(self, db: Session) -> None:
        self._db = db

    def load(self, *, tenant: TenantContext, journey_id: str) -> ReplaceableBundleContent | None:
        apply_database_tenant_context(db=self._db, tenant=tenant)
        row = self._db.scalar(
            select(InquiryBundleRow).where(
                InquiryBundleRow.tenant_id == tenant.tenant_id,
                InquiryBundleRow.journey_id == journey_id,
            )
        )
        if row is None:
            return None
        return ReplaceableBundleContent(row=row, content=ContentBlob.from_text(row.payload_json))

    def replace(
        self,
        *,
        tenant: TenantContext,
        journey_id: str,
        updated_at: str,
        content: ContentBlob,
    ) -> ReplaceableBundleContent:
        # Legacy unconditional upsert (kept for any non-CAS caller).
        stored = self.load(tenant=tenant, journey_id=journey_id)
        if stored is None:
            row = InquiryBundleRow(
                tenant_id=tenant.tenant_id,
                journey_id=journey_id,
                payload_json=content.text,
                updated_at=updated_at,
            )
            self._db.add(row)
        else:
            row = stored.row
            row.payload_json = content.text
            row.updated_at = updated_at
        return ReplaceableBundleContent(row=row, content=content)

    def create(
        self,
        *,
        tenant: TenantContext,
        journey_id: str,
        updated_at: str,
        content: ContentBlob,
    ) -> ReplaceableBundleContent:
        """DATA-INQUIRY-CONCURRENCY-01 (案A): create with revision 1. The caller
        must guarantee the row does not already exist (If-None-Match: *)."""
        apply_database_tenant_context(db=self._db, tenant=tenant)
        row = InquiryBundleRow(
            tenant_id=tenant.tenant_id,
            journey_id=journey_id,
            payload_json=content.text,
            updated_at=updated_at,
            revision=1,
        )
        self._db.add(row)
        return ReplaceableBundleContent(row=row, content=content)

    def update_cas(
        self,
        *,
        tenant: TenantContext,
        journey_id: str,
        expected_revision: int,
        updated_at: str,
        content: ContentBlob,
    ) -> bool:
        """DATA-INQUIRY-CONCURRENCY-01 (案A): atomic compare-and-swap update.
        Single UPDATE ... WHERE revision == expected, incrementing to +1, so a
        concurrent writer with the same expected_revision loses without a
        read-then-write race."""
        apply_database_tenant_context(db=self._db, tenant=tenant)
        result = self._db.execute(
            update(InquiryBundleRow)
            .where(
                InquiryBundleRow.tenant_id == tenant.tenant_id,
                InquiryBundleRow.journey_id == journey_id,
                InquiryBundleRow.revision == expected_revision,
            )
            .values(
                payload_json=content.text,
                updated_at=updated_at,
                revision=expected_revision + 1,
            )
        )
        return result.rowcount == 1

    def delete_cas(
        self,
        *,
        tenant: TenantContext,
        journey_id: str,
        expected_revision: int,
    ) -> bool:
        """DATA-INQUIRY-CONCURRENCY-01 (案A): atomic compare-and-swap delete."""
        apply_database_tenant_context(db=self._db, tenant=tenant)
        result = self._db.execute(
            delete(InquiryBundleRow).where(
                InquiryBundleRow.tenant_id == tenant.tenant_id,
                InquiryBundleRow.journey_id == journey_id,
                InquiryBundleRow.revision == expected_revision,
            )
        )
        return result.rowcount == 1

    def delete(self, *, tenant: TenantContext, journey_id: str) -> bool:
        apply_database_tenant_context(db=self._db, tenant=tenant)
        result = self._db.execute(
            delete(InquiryBundleRow).where(
                InquiryBundleRow.tenant_id == tenant.tenant_id,
                InquiryBundleRow.journey_id == journey_id,
            )
        )
        return result.rowcount == 1


class DatabaseAppendOnlyLogContentStore:
    def __init__(self, db: Session) -> None:
        self._db = db

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
    ) -> AppendOnlyLogContent:
        apply_database_tenant_context(db=self._db, tenant=tenant)
        row = MergeDecisionLogRow(
            tenant_id=tenant.tenant_id,
            doc_id=doc_id,
            decision_id=decision_id,
            group_id=group_id,
            snapshot_version=snapshot_version,
            decided_at=decided_at,
            payload_json=content.text,
        )
        self._db.add(row)
        return AppendOnlyLogContent(row=row, content=content)

    def list_by_group(
        self, *, tenant: TenantContext, doc_id: str, group_id: str
    ) -> list[AppendOnlyLogContent]:
        rows = self._list(
            tenant=tenant,
            clauses=(
                MergeDecisionLogRow.doc_id == doc_id,
                MergeDecisionLogRow.group_id == group_id,
            ),
        )
        return [
            AppendOnlyLogContent(row=row, content=ContentBlob.from_text(row.payload_json))
            for row in rows
        ]

    def list_by_snapshot(
        self, *, tenant: TenantContext, doc_id: str, snapshot_version: str
    ) -> list[AppendOnlyLogContent]:
        rows = self._list(
            tenant=tenant,
            clauses=(
                MergeDecisionLogRow.doc_id == doc_id,
                MergeDecisionLogRow.snapshot_version == snapshot_version,
            ),
        )
        return [
            AppendOnlyLogContent(row=row, content=ContentBlob.from_text(row.payload_json))
            for row in rows
        ]

    def _list(
        self, *, tenant: TenantContext, clauses: tuple[object, ...]
    ) -> list[MergeDecisionLogRow]:
        apply_database_tenant_context(db=self._db, tenant=tenant)
        return list(
            self._db.scalars(
                select(MergeDecisionLogRow)
                .where(MergeDecisionLogRow.tenant_id == tenant.tenant_id, *clauses)
                .order_by(MergeDecisionLogRow.id.asc())
            ).all()
        )
