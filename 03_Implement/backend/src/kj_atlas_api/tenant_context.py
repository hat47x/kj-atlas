from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from kj_atlas_api.models import LOCAL_DEFAULT_TENANT_ID


TenantResolutionMethod = Literal[
    "single_tenant_adapter",
    "verified_claim",
    "trusted_host_mapping",
]


@dataclass(frozen=True, slots=True)
class TenantContext:
    tenant_id: str
    membership_id: str | None
    resolved_by: TenantResolutionMethod


LOCAL_DEFAULT_TENANT_CONTEXT = TenantContext(
    tenant_id=LOCAL_DEFAULT_TENANT_ID,
    membership_id=None,
    resolved_by="single_tenant_adapter",
)
