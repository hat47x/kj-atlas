from __future__ import annotations

from typing import Literal, TypeAlias


TenantSessionBootstrapMode: TypeAlias = Literal[
    "single-tenant",
    "tenant-session-required",
]


def resolve_tenant_session_bootstrap_mode(
    runtime_profile: str,
) -> TenantSessionBootstrapMode:
    if runtime_profile in {
        "local-dev",
        "evaluation",
        "enterprise-production",
    }:
        return "single-tenant"
    if runtime_profile == "saas-multitenant":
        return "tenant-session-required"
    raise RuntimeError("Unsupported runtime profile for tenant session bootstrap")
