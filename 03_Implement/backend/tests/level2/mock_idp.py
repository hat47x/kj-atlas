from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel


app = FastAPI(title="kj-atlas mock idp")


class IssueTokenRequest(BaseModel):
    provider: str
    claims: dict[str, object]


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok", "service": "mock-idp"}


@app.post("/oidc/token")
def issue_token(request: IssueTokenRequest) -> dict[str, object]:
    return {
        "provider": request.provider,
        "id_token": {
            "iss": f"https://mock-idp.local/{request.provider}",
            **request.claims,
        },
    }
