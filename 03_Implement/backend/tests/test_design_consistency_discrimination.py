"""DX-DESIGN-CHECK-01 AC-3: lock the design-consistency detector's endpoint
discriminating power.

The detector's ``_canonicalize_endpoint`` currently collapses every kebab-case
``/ai/*`` route into ``/ai/{param}`` because ``_CONCRETE_ID_RE`` treats the
hyphenated segments as concrete test fixture IDs. api.md therefore "covers" all
ten ``/ai/*`` routes by documenting just one (DX-DESIGN-CHECK-01 is open).

This test asserts the routes stay DISTINCT after canonicalization, using the
LIVE regexes read from the script source -- so it tests whatever normalization
is actually in effect, and a future change is evaluated as-is.

Because the detector currently FAILS this property (the issue is open), the
test is marked xfail(strict=False). The moment a fix lands it reports XPASS;
un-xfail it and this becomes the CI guard the issue asks for.

Expected verification level: unit
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
DETECTOR_PATH = REPO_ROOT / "03_Implement" / "backend" / "scripts" / "check_design_consistency.py"

# Kebab-case single-segment POST routes on the /ai router (prefix="/ai"),
# extracted from routes/ai.py. These are exactly the ones the issue shows
# collapsing into `POST /ai/{param}`.
AI_KEBAB_ROUTES = [
    "/ai/check-narrative",
    "/ai/detect-contradiction",
    "/ai/generate-narrative",
    "/ai/refine-card-text",
    "/ai/suggest-card-groups",
    "/ai/suggest-document-title",
    "/ai/suggest-island-summary",
    "/ai/suggest-layout",
    "/ai/suggest-merges",
]


def _extract_regex(source: str, name: str) -> re.Pattern[str]:
    match = re.search(
        rf"{re.escape(name)}\s*=\s*re\.compile\(\s*r?['\"](.*?)['\"]\s*\)",
        source,
        re.DOTALL,
    )
    assert match is not None, f"could not find {name} in {DETECTOR_PATH.name}"
    return re.compile(match.group(1))


def _canonicalize_endpoint(path: str, param_token_re: re.Pattern[str], concrete_id_re: re.Pattern[str]) -> str:
    if path.startswith("/api/"):
        path = path[len("/api"):]
    normalized = param_token_re.sub("{param}", path)
    normalized = concrete_id_re.sub("{param}", normalized)
    while "{param}/{param}" in normalized:
        normalized = normalized.replace("{param}/{param}", "{param}")
    return normalized


@pytest.mark.xfail(
    strict=False,
    reason="DX-DESIGN-CHECK-01: _CONCRETE_ID_RE collapses kebab-case /ai routes into /ai/{param}",
)
def test_ai_routes_remain_distinct_after_canonicalization() -> None:
    """DX-DESIGN-CHECK-01 AC-3. Currently fails (collapses to one key); un-xfail
    when a fix lands so the detector's discriminating power is CI-locked."""
    source = DETECTOR_PATH.read_text(encoding="utf-8")
    param_token_re = _extract_regex(source, "_PARAM_TOKEN_RE")
    concrete_id_re = _extract_regex(source, "_CONCRETE_ID_RE")

    keys = {_canonicalize_endpoint(r, param_token_re, concrete_id_re) for r in AI_KEBAB_ROUTES}

    assert len(keys) == len(AI_KEBAB_ROUTES), (
        f"{len(AI_KEBAB_ROUTES) - len(keys)} route(s) collapsed: "
        f"{len(AI_KEBAB_ROUTES)} routes -> {len(keys)} canonical key(s) {sorted(keys)}"
    )
