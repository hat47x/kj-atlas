from __future__ import annotations

import os
import re

import httpx
from fastapi import FastAPI, HTTPException

idp_base_url = os.getenv("KJ_ATLAS_AUTH_LEVEL2_MOCK_IDP_BASE_URL", "http://127.0.0.1:18081")
backend_base_url = os.getenv("KJ_ATLAS_AUTH_LEVEL2_BACKEND_BASE_URL", "http://127.0.0.1:18000")

app = FastAPI(title="auth-level2-mock-sp")


def _norm_groups(groups: object, groups_format: str) -> str | None:
    if groups is None:
        return None
    if groups_format == "csv" and isinstance(groups, str):
        return groups
    if isinstance(groups, list):
        return ",".join(str(value) for value in groups)
    return str(groups)


@app.get("/healthz")
def healthz() -> dict:
    return {
        "ok": True,
        "idp": idp_base_url,
        "backend": backend_base_url,
    }


@app.post("/sp/profile/{profile_name}/docs/{doc_id}")
def forward_put_doc(profile_name: str, doc_id: str, payload: dict) -> dict:
    """Legacy header-forwarding mode (single-tenant / Level 1)."""
    with httpx.Client(timeout=10.0) as client:
        idp_resp = client.get(f"{idp_base_url}/idp/profile/{profile_name}")
        if idp_resp.status_code != 200:
            raise HTTPException(status_code=502, detail=f"IdP profile fetch failed: {idp_resp.text}")
        idp_data = idp_resp.json()
        claims = idp_data["claims"]
        mapping = idp_data["mapping"]

        headers: dict[str, str] = {
            "x-auth-provider": idp_data["provider"],
            "x-forwarded-user": str(claims[mapping["subject"]]),
        }

        email_key = mapping.get("email")
        if email_key and claims.get(email_key):
            headers["x-forwarded-email"] = str(claims[email_key])

        name_key = mapping.get("name")
        if name_key and claims.get(name_key):
            headers["x-forwarded-name"] = str(claims[name_key])

        groups_key = mapping.get("groups")
        groups_value = claims.get(groups_key) if groups_key else None
        normalized_groups = _norm_groups(groups_value, mapping.get("groups_format", "array"))
        if normalized_groups:
            headers["x-auth-groups"] = normalized_groups

        amr_key = mapping.get("amr")
        if amr_key and claims.get(amr_key):
            amr_value = claims[amr_key]
            headers["x-auth-amr"] = ",".join(amr_value) if isinstance(amr_value, list) else str(amr_value)

        acr_key = mapping.get("acr")
        if acr_key and claims.get(acr_key):
            headers["x-auth-acr"] = str(claims[acr_key])

        put_resp = client.put(f"{backend_base_url}/docs/{doc_id}", headers=headers, json=payload)
        get_resp = client.get(f"{backend_base_url}/docs/{doc_id}", headers=headers)

    return {
        "profile": profile_name,
        "provider": idp_data["provider"],
        "forwarded_headers": headers,
        "put_status": put_resp.status_code,
        "get_status": get_resp.status_code,
    }


# ADR-0063 D9-7: JWT bearer mode for SaaS trusted auth edge E2E.
_level2_idp_base_url = os.getenv(
    "KJ_ATLAS_AUTH_LEVEL2_MOCK_IDP_BASE_URL", "http://127.0.0.1:18081"
)


@app.post("/sp/jwt/{provider}/docs/{doc_id}")
def forward_jwt_doc(provider: str, doc_id: str, payload: dict) -> dict:
    """SaaS JWT bearer mode (direct): obtain a signed JWT from the Level 2
    mock IdP's /oidc/token and forward it to the backend."""
    with httpx.Client(timeout=10.0) as client:
        token_resp = client.post(
            f"{_level2_idp_base_url}/oidc/token",
            json={
                "provider": provider,
                "claims": {
                    "sub": payload.get("sub", "mock-subject"),
                    "tenant_ref": payload.get("tenant_ref", "mock-org"),
                    "email": payload.get("email", "mock@example.invalid"),
                },
            },
        )
        if token_resp.status_code != 200:
            raise HTTPException(
                status_code=502,
                detail=f"IdP token issuance failed: {token_resp.text}",
            )
        token_data = token_resp.json()
        access_token = token_data["access_token"]

        headers: dict[str, str] = {
            "x-kj-atlas-authorization": f"Bearer {access_token}",
        }

        put_resp = client.put(
            f"{backend_base_url}/docs/{doc_id}",
            headers=headers,
            json=payload,
        )
        get_resp = client.get(
            f"{backend_base_url}/docs/{doc_id}",
            headers=headers,
        )

    return {
        "mode": "jwt_bearer",
        "provider": provider,
        "put_status": put_resp.status_code,
        "get_status": get_resp.status_code,
        "put_body": put_resp.json() if put_resp.headers.get("content-type") == "application/json" else None,
        "get_body": get_resp.json() if get_resp.headers.get("content-type") == "application/json" else None,
    }


# ADR-0064 D4-4: Full OAuth 2.0 login flow proxy.
# Orchestrates the complete OAuth authorization code grant against the
# mock IdP, obtains a JWT, and forwards the request to the backend.
# This simulates a real SAML SP / IAP → Broker → Backend flow.


@app.post("/sp/oauth-login/{provider}/docs/{doc_id}")
def forward_oauth_login_doc(provider: str, doc_id: str, payload: dict) -> dict:
    """Full OAuth login flow: POST /login → /oauth/authorize → /oauth/token
    → backend with JWT Bearer token."""
    with httpx.Client(timeout=10.0) as client:
        username = str(payload.get("username", "alice"))
        password = str(payload.get("password", "password"))
        tenant_ref = str(payload.get("tenant_ref", "org-123"))

        # Step 1: POST /login → follow redirects to /oauth/authorize
        login_resp = client.post(
            f"{_level2_idp_base_url}/login",
            data={
                "username": username,
                "password": password,
                "tenant_ref": tenant_ref,
            },
            follow_redirects=True,
        )
        if login_resp.status_code != 200:
            raise HTTPException(
                status_code=502,
                detail=f"IdP login failed: {login_resp.status_code}",
            )

        # Step 2: The final page after redirects is the consent page.
        # Extract hidden form fields and approve.
        hidden = dict(
            re.findall(r'name="(\w+)" value="([^"]*)"', login_resp.text)
        )
        hidden.pop("deny", None)
        approve_resp = client.post(
            f"{_level2_idp_base_url}/oauth/authorize",
            data=hidden,
            follow_redirects=False,
        )
        if approve_resp.status_code != 302:
            raise HTTPException(
                status_code=502,
                detail=f"IdP authorization failed: {approve_resp.status_code}",
            )

        # Step 3: Extract authorization code from redirect
        callback = approve_resp.headers.get("location", "")
        code_match = re.findall(r"code=([^&]+)", callback)
        if not code_match:
            raise HTTPException(
                status_code=502,
                detail=f"No authorization code in redirect: {callback[:100]}",
            )
        code = code_match[0]

        # Step 4: Exchange code for JWT
        token_resp = client.post(
            f"{_level2_idp_base_url}/oauth/token",
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": "http://mock-idp.local/callback",
                "client_id": "mock-client",
            },
        )
        if token_resp.status_code != 200:
            raise HTTPException(
                status_code=502,
                detail=f"IdP token exchange failed: {token_resp.status_code}",
            )
        token_data = token_resp.json()
        access_token = token_data["access_token"]

        # Step 5: Forward to backend with JWT Bearer token
        headers: dict[str, str] = {
            "x-kj-atlas-authorization": f"Bearer {access_token}",
        }

        doc_body = {
            k: v
            for k, v in payload.items()
            if k not in ("username", "password", "tenant_ref", "sub")
        }
        if not doc_body:
            doc_body = payload

        put_resp = client.put(
            f"{backend_base_url}/docs/{doc_id}",
            headers=headers,
            json=doc_body,
        )
        get_resp = client.get(
            f"{backend_base_url}/docs/{doc_id}",
            headers=headers,
        )

    return {
        "mode": "oauth_login",
        "provider": provider,
        "tenant_ref": tenant_ref,
        "subject": username,
        "put_status": put_resp.status_code,
        "get_status": get_resp.status_code,
        "put_body": put_resp.json() if put_resp.headers.get("content-type") == "application/json" else None,
        "get_body": get_resp.json() if get_resp.headers.get("content-type") == "application/json" else None,
    }
