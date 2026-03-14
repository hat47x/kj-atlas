from __future__ import annotations

from datetime import datetime, timezone

from kj_atlas_api.access_control import AuthContext
from kj_atlas_api.auth_assurance import build_auth_assurance_metadata


def _ctx(*, amr: str | None = None, acr: str | None = None, aal: str | None = None, auth_time: str | None = None) -> AuthContext:
    return AuthContext(
        actor_ref="user:u-1",
        amr=amr,
        acr=acr,
        aal=aal,
        auth_time=auth_time,
    )


def test_build_auth_assurance_metadata_normalizes_multifactor_recent_high() -> None:
    metadata = build_auth_assurance_metadata(
        _ctx(
            amr="pwd,webauthn",
            aal="aal3",
            auth_time="2026-03-14T00:10:00Z",
        ),
        now=datetime(2026, 3, 14, 0, 20, 0, tzinfo=timezone.utc),
    )

    assert metadata == {
        "hasStepUp": True,
        "amrClass": "multi_factor",
        "assuranceLevel": "high",
        "authAgeBucket": "fresh",
    }


def test_build_auth_assurance_metadata_handles_unknown_and_stale() -> None:
    metadata = build_auth_assurance_metadata(
        _ctx(
            amr="pwd",
            acr="unsupported-acr",
            auth_time="2026-03-14T00:00:00Z",
        ),
        now=datetime(2026, 3, 14, 1, 0, 0, tzinfo=timezone.utc),
    )

    assert metadata == {
        "hasStepUp": False,
        "amrClass": "single_factor",
        "assuranceLevel": "unknown",
        "authAgeBucket": "stale",
    }


def test_build_auth_assurance_metadata_invalid_auth_time_is_unknown() -> None:
    metadata = build_auth_assurance_metadata(_ctx(auth_time="not-a-timestamp"))

    assert metadata["authAgeBucket"] == "unknown"
