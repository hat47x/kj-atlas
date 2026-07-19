from __future__ import annotations

import logging
from typing import Protocol, cast

from fastapi import HTTPException, Request
from sqlalchemy.orm import Session

from kj_atlas_api.access_control import (
    AccessAction,
    AccessResource,
    Visibility,
    normalize_policy_ref,
    parse_visibility,
)
from kj_atlas_api.document_access_metadata_repository import (
    get_document_access_metadata_row,
)
from kj_atlas_api.document_repository import get_document_row
from kj_atlas_api.tenant_context import TenantContext

logger = logging.getLogger(__name__)

INVALID_POLICY_BINDING_CHARACTER = {chr(value) for value in range(32)} | {chr(127)}


def _canonical_policy_binding_value(value: str | None) -> str | None:
    normalized = normalize_policy_ref(value)
    if normalized is None or any(
        character in INVALID_POLICY_BINDING_CHARACTER for character in normalized
    ):
        return None
    return normalized


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


class DocumentPolicyBindingResolver(Protocol):
    """Resolve a non-secret binding id to a transient external policy reference."""

    def resolve(
        self,
        *,
        tenant: TenantContext,
        binding_id: str,
        policy_version: str,
    ) -> str | None:
        ...


class UnavailableDocumentPolicyBindingResolver:
    def resolve(
        self,
        *,
        tenant: TenantContext,  # noqa: ARG002
        binding_id: str,  # noqa: ARG002
        policy_version: str,  # noqa: ARG002
    ) -> str | None:
        return None


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

    Raw policy references are never loaded from client headers or persisted in
    the application database. Stored binding ids are resolved transiently by a
    trusted runtime adapter. Missing metadata/bindings fail closed.
    """

    def __init__(
        self,
        *,
        policy_binding_resolver: DocumentPolicyBindingResolver | None = None,
    ) -> None:
        self._policy_binding_resolver = (
            policy_binding_resolver or UnavailableDocumentPolicyBindingResolver()
        )

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
        metadata = None
        if row is not None:
            metadata = get_document_access_metadata_row(
                db,
                tenant=tenant,
                doc_id=doc_id,
            )
        if metadata is None:
            return AccessResource(
                doc_id=doc_id,
                visibility="Restricted",
                policy_ref=None,
                tenant_id=resource_tenant_id,
            )

        parsed_visibility = parse_visibility(metadata.visibility)
        if parsed_visibility is None:
            return AccessResource(
                doc_id=doc_id,
                visibility="Restricted",
                policy_ref=None,
                tenant_id=resource_tenant_id,
            )

        policy_ref = None
        binding_id = _canonical_policy_binding_value(metadata.policy_binding_id)
        policy_version = _canonical_policy_binding_value(metadata.policy_version)
        if binding_id is not None and policy_version is not None:
            try:
                policy_ref = _canonical_policy_binding_value(
                    self._policy_binding_resolver.resolve(
                        tenant=tenant,
                        binding_id=binding_id,
                        policy_version=policy_version,
                    )
                )
            except Exception:
                logger.warning(
                    "policy binding resolution failed for doc_id=%s tenant_id=%s; "
                    "falling back to no policy_ref",
                    doc_id,
                    resource_tenant_id,
                    exc_info=True,
                )
                policy_ref = None
        return AccessResource(
            doc_id=doc_id,
            visibility=cast(Visibility, parsed_visibility),
            policy_ref=policy_ref,
            tenant_id=resource_tenant_id,
        )
