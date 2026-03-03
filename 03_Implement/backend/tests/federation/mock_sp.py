from __future__ import annotations

import os

import httpx
from fastapi import FastAPI, HTTPException

IDP_BASE_URL = os.getenv("MOCK_IDP_BASE_URL", "http://127.0.0.1:18081")
BACKEND_BASE_URL = os.getenv("BACKEND_BASE_URL", "http://127.0.0.1:18000")

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
        "idp": IDP_BASE_URL,
        "backend": BACKEND_BASE_URL,
    }


@app.post("/sp/profile/{profile_name}/docs/{doc_id}")
def forward_put_doc(profile_name: str, doc_id: str, payload: dict) -> dict:
    with httpx.Client(timeout=10.0) as client:
        idp_resp = client.get(f"{IDP_BASE_URL}/idp/profile/{profile_name}")
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

        put_resp = client.put(f"{BACKEND_BASE_URL}/docs/{doc_id}", headers=headers, json=payload)
        get_resp = client.get(f"{BACKEND_BASE_URL}/docs/{doc_id}", headers=headers)

    return {
        "profile": profile_name,
        "provider": idp_data["provider"],
        "forwarded_headers": headers,
        "put_status": put_resp.status_code,
        "get_status": get_resp.status_code,
    }
