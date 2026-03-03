from __future__ import annotations

from fastapi import FastAPI, HTTPException

from .profile_loader import load_profile, profile_names

app = FastAPI(title="auth-level2-mock-idp")


@app.get("/healthz")
def healthz() -> dict:
    return {"ok": True, "profiles": profile_names()}


@app.get("/idp/profile/{profile_name}")
def idp_profile(profile_name: str) -> dict:
    try:
        profile = load_profile(profile_name)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=f"Unknown profile: {profile_name}") from exc
    return {
        "profile": profile["profile"],
        "provider": profile["provider"],
        "claims": profile["idp"]["claims"],
        "mapping": profile["mapping"],
    }
