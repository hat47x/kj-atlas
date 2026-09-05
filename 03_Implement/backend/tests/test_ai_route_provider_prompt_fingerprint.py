from __future__ import annotations

import re

from scripts import analyze_ai_route_provider_measurement as analysis
from scripts import measure_ai_route_provider_tokens as token_measure


_SHA256 = re.compile(r"^[0-9a-f]{64}$")


def test_dry_run_records_exact_sha256_for_every_canonical_prompt() -> None:
    requests = token_measure.build_representative_requests(
        "named-model",
        include_groups_a2=True,
        include_layout_c=True,
    )
    report = token_measure.measure(
        model="named-model",
        expected_provider="named-provider",
        execute=False,
        include_groups_a2=True,
        include_layout_c=True,
    )

    assert report["prompt_fingerprint"] == {
        "algorithm": "sha256",
        "encoding": "utf-8",
    }
    assert len(report["routes"]) == 38
    for name, request in requests.items():
        fingerprint = report["routes"][name]["prompt"]["sha256"]
        assert _SHA256.fullmatch(fingerprint)
        assert fingerprint == token_measure._prompt_sha256(request.prompt)


def test_prompt_fingerprint_is_identity_only_not_a_token_estimate() -> None:
    report = token_measure.measure(
        model="named-model",
        expected_provider="named-provider",
        execute=False,
    )
    row = report["routes"]["suggest-card-groups"]

    assert isinstance(row["prompt"]["utf8_bytes"], int)
    assert isinstance(row["prompt"]["sha256"], str)
    assert row["provider_reported"]["input_tokens"] is None
    assert row["prompt"]["sha256"] != str(row["prompt"]["utf8_bytes"])


def test_one_character_prompt_change_changes_fingerprint() -> None:
    request = token_measure.build_representative_requests("named-model")[
        "suggest-layout-route-b"
    ]

    original = token_measure._prompt_sha256(request.prompt)
    changed = token_measure._prompt_sha256(request.prompt + "x")

    assert original != changed


def test_analyzer_and_measurement_harness_share_fingerprint_contract() -> None:
    assert analysis.PROMPT_FINGERPRINT == {
        "algorithm": "sha256",
        "encoding": "utf-8",
    }
