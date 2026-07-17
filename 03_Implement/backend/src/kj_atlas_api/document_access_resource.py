from __future__ import annotations

from typing import Protocol

from fastapi import HTTPException, Request
from sqlalchemy.orm import Session

from kj_atlas_api.access_control import (
    AccessAction,
    AccessResource,
    normalize_policy_ref,
    parse_visibility,
)
from kj_atlas_api.document_repository import get_document_row
from kj_atlas_api.tenant_context import TenantContext


class DocumentAccessResourceResolver(Protocol):
    def resolve(
        self,
        *,
        db: Session,
        request: Request,
        tenant: TenantContext,
        action: AccessAction,
        doc_id: str,
    ) -> AccessResource:
        ...


class SingleTenantHeaderResourceResolver:
    """Preserve the existing single-tenant access-control header contract."""

    def resolve(
        self,
        *,
        db: Session,  # noqa: ARG002
        request: Request,
        tenant: TenantContext,
        action: AccessAction,  # noqa: ARG002
        doc_id: str,
    ) -> AccessResource:
        return AccessResource(
            doc_id=doc_id,
            visibility=parse_visibility(request.headers.get("x-doc-visibility")),
            policy_ref=normalize_policy_ref(request.headers.get("x-policy-ref")),
            tenant_id=tenant.tenant_id,
        )


class ServerOwnedDocumentResourceResolver:
    """Resolve document scope without trusting public policy headers.

    This resolver is reserved for the future SaaS profile. Until a server-owned
    policy metadata store exists, resources default to Restricted with no policy
    reference so deny-mode access control fails closed.
    """

    def resolve(
        self,
        *,
        db: Session,
        request: Request,  # noqa: ARG002
        tenant: TenantContext,
        action: AccessAction,
        doc_id: str,
    ) -> AccessResource:
        row = get_document_row(db, tenant=tenant, doc_id=doc_id)
        if row is None and action != "write":
            raise HTTPException(status_code=404, detail="Document not found")

        resource_tenant_id = tenant.tenant_id if row is None else row.tenant_id
        return AccessResource(
            doc_id=doc_id,
            visibility="Restricted",
            policy_ref=None,
            tenant_id=resource_tenant_id,
        )
