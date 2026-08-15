"""AI-MODEL-GOVERNANCE-01 R1/R3: dynamic model/provider registry.

Platform-shared assets (providers, models) plus a tenant-scoped allowlist.
Secrets are stored as references only (api_key_ref). The effective-model
resolver in llm/provider.py consults these tables when `use_registry` is on.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from kj_atlas_api.models import (
    LLMModelRegistryRow,
    LLMProviderRegistryRow,
    TenantModelAllowlistRow,
)


def register_provider(
    db: Session,
    *,
    provider_id: str,
    provider_kind: str,
    display_name: str,
    base_url: str | None = None,
    api_key_ref: str | None = None,
    lifecycle_state: str = "active",
    occurred_at: str,
) -> LLMProviderRegistryRow:
    row = LLMProviderRegistryRow(
        id=provider_id,
        provider_kind=provider_kind,
        display_name=display_name,
        base_url=base_url,
        api_key_ref=api_key_ref,
        lifecycle_state=lifecycle_state,
        created_at=occurred_at,
        updated_at=occurred_at,
    )
    db.merge(row)
    return row


def register_model(
    db: Session,
    *,
    model_id: str,
    provider_id: str,
    display_name: str,
    capabilities: str | None = None,
    lifecycle_state: str = "active",
    occurred_at: str,
) -> LLMModelRegistryRow:
    row = LLMModelRegistryRow(
        id=model_id,
        provider_id=provider_id,
        display_name=display_name,
        capabilities=capabilities,
        lifecycle_state=lifecycle_state,
        created_at=occurred_at,
        updated_at=occurred_at,
    )
    db.merge(row)
    return row


def set_model_lifecycle(db: Session, *, model_id: str, lifecycle_state: str, occurred_at: str) -> bool:
    row = db.get(LLMModelRegistryRow, model_id)
    if row is None:
        return False
    row.lifecycle_state = lifecycle_state
    row.updated_at = occurred_at
    return True


def list_providers(db: Session) -> list[LLMProviderRegistryRow]:
    return list(db.scalars(select(LLMProviderRegistryRow).order_by(LLMProviderRegistryRow.id)))


def list_models(db: Session) -> list[LLMModelRegistryRow]:
    return list(db.scalars(select(LLMModelRegistryRow).order_by(LLMModelRegistryRow.id)))


def list_tenant_allowed_model_ids(db: Session, *, tenant_id: str) -> set[str]:
    return set(
        db.scalars(
            select(TenantModelAllowlistRow.model_id).where(
                TenantModelAllowlistRow.tenant_id == tenant_id,
                TenantModelAllowlistRow.lifecycle_state == "active",
            )
        )
    )


def tenant_allowlist_effective_model_ids(db: Session, *, tenant_id: str) -> set[str] | None:
    """Return the tenant's effective allowed model ids, or None for the
    platform-default (allowlist empty = all active registered models allowed).

    R3 semantics: a non-empty allowlist is fail-closed -- only the listed models
    may be used; anything else is rejected with 403 model_not_allowed.
    """
    allowed = list_tenant_allowed_model_ids(db, tenant_id=tenant_id)
    return allowed if allowed else None


def set_tenant_model_allowlist(
    db: Session,
    *,
    tenant_id: str,
    model_ids: list[str],
    occurred_at: str,
) -> None:
    """Replace a tenant's allowlist. Empty list clears it (platform-default)."""
    existing = list(
        db.scalars(
            select(TenantModelAllowlistRow).where(TenantModelAllowlistRow.tenant_id == tenant_id)
        )
    )
    for row in existing:
        db.delete(row)
    for model_id in model_ids:
        db.add(
            TenantModelAllowlistRow(
                tenant_id=tenant_id,
                model_id=model_id,
                lifecycle_state="active",
                created_at=occurred_at,
                updated_at=occurred_at,
            )
        )
