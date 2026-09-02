"""Representative-scale contract for AI-IR-PROJECTION-01 AC-10.

This is intentionally a deterministic projection test, not an external-LLM
benchmark.  It fixes what the current IR boundary does to a 300-card / 30-island
source before Stage 5 expands adoption to more AI routes.
"""

from scripts.measure_llm_input_ir_scale import measure


def test_representative_scale_exposes_current_max_cards_loss() -> None:
    report = measure(include_coordinates=False)

    assert report["source"] == {
        "cards": 300,
        "islands": 30,
        "relations": 300,
        "text_chars": report["source"]["text_chars"],
    }
    assert report["source"]["text_chars"] > 0

    # MAX_CARDS=200 is a projection boundary, not the request contract.  At the
    # representative 300-card scale it necessarily removes one third of the
    # source before a migrated route renders its prompt.
    assert report["projected"]["cards"] == 200
    assert report["projected"]["dropped_cards"] == 100
    assert report["truncation"] == {
        "truncated": True,
        "reason_codes": ["MAX_CARDS"],
    }

    # Islands themselves survive (§2.2A rule 7), but the ten islands whose
    # members were all outside the retained 200-card set become empty.  This is
    # semantically observable information loss even though referential
    # integrity remains valid.
    assert report["projected"]["islands"] == 30
    assert report["projected"]["empty_islands"] == 10
    assert report["projected"]["empty_island_ids"] == [f"i{i:02d}" for i in range(20, 30)]

    # The ring loses the edge crossing c199 -> c200 and the closing edge
    # c299 -> c000 together with the dropped nodes.
    assert report["projected"]["relations"] == 199
    assert report["projected"]["coordinates"] == 0
    assert report["serialized"]["unicode_chars"] > 0
    assert report["serialized"]["utf8_bytes"] >= report["serialized"]["unicode_chars"]
    assert report["token_measurement"]["exact_input_tokens"] is None
    assert report["token_measurement"]["status"] == "provider-reported-usage-required"


def test_representative_scale_heaviest_projection_is_deterministic() -> None:
    first = measure(include_coordinates=True)
    second = measure(include_coordinates=True)

    assert first == second
    assert first["projected"]["cards"] == 200
    assert first["projected"]["coordinates"] == 200
    assert first["projected"]["dropped_cards"] == 100
    assert first["truncation"]["reason_codes"] == ["MAX_CARDS"]
    assert first["serialized"]["utf8_bytes"] > 0
