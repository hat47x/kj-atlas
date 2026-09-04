"""Test-only HTTP services for the real-browser SaaS multi-instance E2E."""

from __future__ import annotations

import argparse
import os
from datetime import datetime, timezone

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import Response

from kj_atlas_api.db import SessionLocal
from kj_atlas_api.models import (
    IdentityProviderRow,
    TenantIdentityProviderRow,
    TenantMembershipRow,
    TenantRow,
    UserIdentityRow,
    UserRow,
)

TIMESTAMP = datetime.now(timezone.utc).isoformat()

policy_app = FastAPI(title="kj-atlas SaaS E2E policy stub")


@policy_app.get("/healthz")
def policy_health() -> dict[str, str]:
    return {"status": "ok"}


@policy_app.post("/access-control")
def access_control() -> dict[str, object]:
    return {"allow": True, "readOnly": False, "reason": "saas-browser-e2e"}


@policy_app.post("/document-policy")
def document_policy() -> dict[str, str]:
    return {"policyRef": "e2e:allow"}


@policy_app.post("/capabilities")
def capabilities() -> dict[str, object]:
    return {
        "effectiveCapabilities": ["document.read"],
        "capabilityVersion": "e2e-v1",
    }


gateway_app = FastAPI(title="kj-atlas SaaS E2E deterministic gateway")

_HOP_BY_HOP = {
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailer",
    "transfer-encoding",
    "upgrade",
}


def _worker_for(path: str) -> tuple[str, str]:
    # Login and callback deliberately stay on worker 1. Every normal API call,
    # including the authenticated session lookup after callback, goes to worker 2.
    # A passing browser test therefore proves that the auth session is not held
    # only in worker-local memory.
    if path in {"session/login", "session/callback"}:
        return "worker-1", os.environ.get(
            "KJ_ATLAS_E2E_WORKER_1", "http://127.0.0.1:8001"
        )
    return "worker-2", os.environ.get(
        "KJ_ATLAS_E2E_WORKER_2", "http://127.0.0.1:8002"
    )


@gateway_app.get("/healthz")
def gateway_health() -> dict[str, str]:
    return {"status": "ok"}


@gateway_app.api_route(
    "/{path:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"],
)
async def gateway(path: str, request: Request) -> Response:
    worker_name, worker_base = _worker_for(path)
    target = f"{worker_base}/{path}"
    if request.url.query:
        target += f"?{request.url.query}"

    incoming_headers = {
        name: value
        for name, value in request.headers.items()
        if name.lower() not in _HOP_BY_HOP | {"host", "content-length"}
    }
    body = await request.body()
    async with httpx.AsyncClient(follow_redirects=False, timeout=15.0) as client:
        upstream = await client.request(
            request.method,
            target,
            content=body,
            headers=incoming_headers,
        )

    response = Response(content=upstream.content, status_code=upstream.status_code)
    for name, value in upstream.headers.multi_items():
        lowered = name.lower()
        if lowered in _HOP_BY_HOP | {
            "content-length",
            "content-encoding",
            "set-cookie",
        }:
            continue
        response.raw_headers.append((name.encode("latin-1"), value.encode("latin-1")))
    for cookie in upstream.headers.get_list("set-cookie"):
        response.raw_headers.append((b"set-cookie", cookie.encode("latin-1")))
    response.headers["X-KJ-Atlas-E2E-Upstream"] = worker_name
    return response


def seed_database() -> None:
    issuer = os.environ.get(
        "KJ_ATLAS_MOCK_IDP_BASE", "http://localhost:9100"
    ).rstrip("/")
    with SessionLocal() as db:
        if db.get(UserRow, "user-1") is not None:
            return
        db.add_all(
            [
                UserRow(
                    id="user-1",
                    display_name="Alice",
                    email="alice@mock-idp.local",
                    lifecycle_state="active",
                    created_at=TIMESTAMP,
                    updated_at=TIMESTAMP,
                ),
                TenantRow(
                    id="tenant-a",
                    display_name="Tenant A",
                    lifecycle_state="active",
                    created_at=TIMESTAMP,
                    updated_at=TIMESTAMP,
                ),
                IdentityProviderRow(
                    id="idp-1",
                    issuer=f"{issuer}/mock-client",
                    audience="kj-atlas",
                    protocol="oidc",
                    jwks_uri=f"{issuer}/jwks.json",
                    lifecycle_state="active",
                    created_at=TIMESTAMP,
                    updated_at=TIMESTAMP,
                ),
            ]
        )
        db.flush()
        db.add_all(
            [
                TenantIdentityProviderRow(
                    tenant_id="tenant-a",
                    identity_provider_id="idp-1",
                    external_tenant_ref="org-123",
                    lifecycle_state="active",
                    created_at=TIMESTAMP,
                    updated_at=TIMESTAMP,
                ),
                UserIdentityRow(
                    user_id="user-1",
                    provider="idp-1",
                    external_uid="alice",
                    identity_provider_id="idp-1",
                    subject="alice",
                    created_at=TIMESTAMP,
                ),
                TenantMembershipRow(
                    tenant_id="tenant-a",
                    user_id="user-1",
                    lifecycle_state="active",
                    created_at=TIMESTAMP,
                    updated_at=TIMESTAMP,
                ),
            ]
        )
        db.commit()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("seed",))
    args = parser.parse_args()
    if args.command == "seed":
        seed_database()


if __name__ == "__main__":
    main()
