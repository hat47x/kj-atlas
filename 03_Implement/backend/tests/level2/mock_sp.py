from __future__ import annotations

import json
from collections.abc import Mapping

from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from pydantic import BaseModel


def _as_text(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _parse_groups(claims: Mapping[str, object], key: str, fmt: str) -> str | None:
    raw = claims.get(key)
    if raw is None:
        return None

    if fmt == "json":
        return json.dumps(raw)

    if isinstance(raw, list):
        values = [str(item).strip() for item in raw if str(item).strip()]
        if fmt == "space":
            return " ".join(values)
        return ",".join(values)

    text = str(raw).strip()
    if not text:
        return None
    if fmt == "space":
        return " ".join([part for part in text.replace(",", " ").split() if part])
    return text


class FederationProxyRequest(BaseModel):
    provider: str
    claims: dict[str, object]
    profile: dict[str, object]
    document_id: str
    payload: dict[str, object]


class MockSpRuntime:
    def __init__(self, *, backend_app, idp_app):
        self._backend_client = TestClient(backend_app)
        self._idp_client = TestClient(idp_app)
        self.app = FastAPI(title="kj-atlas mock sp")
        self.app.post("/proxy/docs")(self.proxy_docs)
        self.app.get("/healthz")(self.healthz)

    def healthz(self) -> dict[str, str]:
        return {"status": "ok", "service": "mock-sp"}

    def proxy_docs(self, request: FederationProxyRequest) -> dict[str, object]:
        token_resp = self._idp_client.post(
            "/oidc/token",
            json={"provider": request.provider, "claims": request.claims},
        )
        if token_resp.status_code != 200:
            raise HTTPException(status_code=502, detail="mock-idp token issue failed")

        token_claims = token_resp.json().get("id_token", {})
        profile = request.profile
        header_map = profile.get("headerMap", {})
        claim_map = profile.get("claimMap", {})

        subject_claim = str(claim_map.get("subject", "sub"))
        email_claim = str(claim_map.get("email", "email"))
        name_claim = str(claim_map.get("name", "name"))
        groups_claim = str(claim_map.get("groups", "groups"))
        amr_claim = str(claim_map.get("amr", "amr"))
        acr_claim = str(claim_map.get("acr", "acr"))

        groups_format = str(profile.get("groupsFormat", "csv"))
        include_amr = bool(profile.get("includeAmrAcr", True))

        headers: dict[str, str] = {}
        subject_header = _as_text(header_map.get("user"))
        if subject_header is None:
            raise HTTPException(status_code=400, detail="profile.headerMap.user is required")

        subject_value = _as_text(token_claims.get(subject_claim))
        if subject_value is None:
            raise HTTPException(status_code=400, detail=f"missing subject claim: {subject_claim}")
        headers[subject_header] = subject_value

        provider_header = _as_text(header_map.get("provider"))
        if provider_header:
            headers[provider_header] = request.provider

        email_header = _as_text(header_map.get("email"))
        email_value = _as_text(token_claims.get(email_claim))
        if email_header and email_value:
            headers[email_header] = email_value

        name_header = _as_text(header_map.get("name"))
        name_value = _as_text(token_claims.get(name_claim))
        if name_header and name_value:
            headers[name_header] = name_value

        groups_header = _as_text(header_map.get("groups"))
        groups_value = _parse_groups(token_claims, groups_claim, groups_format)
        if groups_header and groups_value:
            headers[groups_header] = groups_value

        if include_amr:
            amr_header = _as_text(header_map.get("amr"))
            amr_value = _as_text(token_claims.get(amr_claim))
            if amr_header and amr_value:
                headers[amr_header] = amr_value

            acr_header = _as_text(header_map.get("acr"))
            acr_value = _as_text(token_claims.get(acr_claim))
            if acr_header and acr_value:
                headers[acr_header] = acr_value

        put_resp = self._backend_client.put(
            f"/docs/{request.document_id}",
            json=request.payload,
            headers=headers,
        )
        get_resp = self._backend_client.get(f"/docs/{request.document_id}", headers=headers)

        return {
            "token": token_claims,
            "forwardedHeaders": headers,
            "putStatus": put_resp.status_code,
            "getStatus": get_resp.status_code,
            "getBody": get_resp.json() if get_resp.headers.get("content-type", "").startswith("application/json") else None,
        }
