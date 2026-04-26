from __future__ import annotations

from datetime import datetime, timedelta, timezone

from kj_atlas_api.access_control import AuthContext


_AMR_MULTI_FACTOR_TOKENS = {"mfa", "otp", "totp", "webauthn", "fido2"}
_ASSURANCE_HIGH = {"3", "aal3", "high", "urn:ietf:params:acr:high"}
_ASSURANCE_SUBSTANTIAL = {"2", "aal2", "substantial", "urn:ietf:params:acr:substantial"}
_ASSURANCE_LOW = {"1", "aal1", "low", "urn:ietf:params:acr:low"}


def _split_amr(raw: str | None) -> set[str]:
    if raw is None:
        return set()
    return {part.strip().lower() for part in raw.split(",") if part.strip()}


def _parse_auth_time(raw: str | None) -> datetime | None:
    if raw is None:
        return None
    candidate = raw.strip()
    if not candidate:
        return None
    if candidate.endswith("Z"):
        candidate = f"{candidate[:-1]}+00:00"
    try:
        parsed = datetime.fromisoformat(candidate)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _normalize_assurance(raw: str | None) -> str:
    if raw is None:
        return "unknown"
    normalized = raw.strip().lower()
    if normalized in _ASSURANCE_HIGH:
        return "high"
    if normalized in _ASSURANCE_SUBSTANTIAL:
        return "substantial"
    if normalized in _ASSURANCE_LOW:
        return "low"
    return "unknown"


def _resolve_assurance_level(*, acr: str | None, aal: str | None) -> str:
    # Prefer explicit AAL when recognized, but fall back to ACR when AAL is missing/unknown.
    aal_level = _normalize_assurance(aal)
    if aal_level != "unknown":
        return aal_level
    return _normalize_assurance(acr)


def build_auth_assurance_metadata(auth: AuthContext, *, now: datetime | None = None) -> dict[str, str | bool]:
    amr_tokens = _split_amr(auth.amr)
    has_step_up = any(token in _AMR_MULTI_FACTOR_TOKENS for token in amr_tokens)

    if not amr_tokens:
        amr_class = "unknown"
    elif has_step_up or len(amr_tokens) >= 2:
        amr_class = "multi_factor"
    else:
        amr_class = "single_factor"

    auth_time = _parse_auth_time(auth.auth_time)
    current = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    if auth_time is None or auth_time > current:
        auth_age_bucket = "unknown"
    elif (current - auth_time) <= timedelta(minutes=15):
        auth_age_bucket = "fresh"
    else:
        auth_age_bucket = "stale"

    return {
        "hasStepUp": has_step_up,
        "amrClass": amr_class,
        "assuranceLevel": _resolve_assurance_level(acr=auth.acr, aal=auth.aal),
        "authAgeBucket": auth_age_bucket,
    }

