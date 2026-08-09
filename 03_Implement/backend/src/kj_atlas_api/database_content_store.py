from __future__ import annotations

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from kj_atlas_api.content_store import (
    AppendOnlyLogContent,
    ContentBlob,
    ReplaceableBundleContent,
    VersionedDocumentContent,
)
from kj_atlas_api.models import DocumentRow, InquiryBundleRow, MergeDecisionLogRow
from kj_atlas_api.tenant_context import TenantContext
from kj_atlas_api.tenant_db_guard import apply_database_tenant_context


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
        return VersionedDocumentContent(row=row, content=ContentBlob.from_text(row.payload_json))

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
        else:
            row = stored.row
            row.version = version
            row.updated_at = updated_at
            row.payload_json = content.text
        return VersionedDocumentContent(row=row, content=content)


class DatabaseBundleContentStore:
    def __init__(self, db: Session) -> None:
        self._db = db

    def load(
        self, *, tenant: TenantContext, journey_id: str
    ) -> ReplaceableBundleContent | None:
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
            clauses=(MergeDecisionLogRow.doc_id == doc_id, MergeDecisionLogRow.group_id == group_id),
        )
        return [AppendOnlyLogContent(row=row, content=ContentBlob.from_text(row.payload_json)) for row in rows]

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
        return [AppendOnlyLogContent(row=row, content=ContentBlob.from_text(row.payload_json)) for row in rows]

    def _list(self, *, tenant: TenantContext, clauses: tuple[object, ...]) -> list[MergeDecisionLogRow]:
        apply_database_tenant_context(db=self._db, tenant=tenant)
        return list(
            self._db.scalars(
                select(MergeDecisionLogRow)
                .where(MergeDecisionLogRow.tenant_id == tenant.tenant_id, *clauses)
                .order_by(MergeDecisionLogRow.id.asc())
            ).all()
        )
