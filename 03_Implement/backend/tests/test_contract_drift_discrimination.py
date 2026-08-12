"""DOGFOOD-METRIC-01 AC-2 / DX-DESIGN-CHECK-01 (補足): lock the contract-drift
detector's endpoint discriminating power.

check_contract_drift.py shares the same ``_CONCRETE_ID_RE`` as
check_design_consistency.py, so it too collapses every kebab-case ``/ai/*``
route into one key. This canary asserts the routes stay DISTINCT after
``_canonical`` using the LIVE regexes read from the script source.

Currently the detector FAILS this property, so the test is
xfail(strict=False). It flips to XPASS the moment a fix lands; un-xfail it
then. This is the AC-2 capability canary for the contract-drift detector.

Expected verification level: unit
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
DETECTOR_PATH = REPO_ROOT / "03_Implement" / "backend" / "scripts" / "check_contract_drift.py"

# Kebab-case single-segment POST routes on the /ai router (prefix="/ai"),
# matching test_design_consistency_discrimination.py.
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


def _canonical(path: str, param_token_re: re.Pattern[str], concrete_id_re: re.Pattern[str]) -> str:
    normalized = param_token_re.sub("{param}", path)
    normalized = concrete_id_re.sub("{param}", normalized)
    while "{param}/{param}" in normalized:
        normalized = normalized.replace("{param}/{param}", "{param}")
    return normalized


@pytest.mark.xfail(
    strict=False,
    reason="DX-DESIGN-CHECK-01: _CONCRETE_ID_RE collapses kebab-case /ai routes (check_contract_drift.py)",
)
def test_contract_drift_ai_routes_remain_distinct_after_canonicalization() -> None:
    """DOGFOOD-METRIC-01 AC-2 canary for check_contract_drift.py. Un-xfail when
    the detector's discriminating power is fixed."""
    source = DETECTOR_PATH.read_text(encoding="utf-8")
    param_token_re = _extract_regex(source, "_PARAM_TOKEN_RE")
    concrete_id_re = _extract_regex(source, "_CONCRETE_ID_RE")

    keys = {_canonical(r, param_token_re, concrete_id_re) for r in AI_KEBAB_ROUTES}

    assert len(keys) == len(AI_KEBAB_ROUTES), (
        f"{len(AI_KEBAB_ROUTES) - len(keys)} route(s) collapsed: "
        f"{len(AI_KEBAB_ROUTES)} routes -> {len(keys)} canonical key(s) {sorted(keys)}"
    )
