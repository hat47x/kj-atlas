from __future__ import annotations

import json
from uuid import uuid4

from sqlalchemy import delete, select
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
    ) -> VersionedDocumentContent:
        stored = self.load(tenant=tenant, doc_id=doc_id)
        if stored is None:
            row = DocumentRow(
                tenant_id=tenant.tenant_id,
                id=doc_id,
                version=version,
                updated_at=updated_at,
                payload_json=content.text,
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
