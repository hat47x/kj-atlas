"""Deterministic characterization of route-specific projection candidates."""

from scripts.measure_ai_route_projection_candidates import measure


def test_measurement_is_deterministic() -> None:
    assert measure() == measure()


def test_grouping_candidate_restores_all_requested_and_island_memberships() -> None:
    result = measure()["groups"]
    source = result["source"]
    current = result["current_shared_ir"]
    candidate = result["route_b_candidate"]

    assert source["requested_cards"] == 300
    assert current["requested_cards_accounted_for"] < 300
    assert current["complete_island_memberships"] < 30
    assert current["tail_island_members"] < 10

    assert candidate["projected_requested_cards"] == 300
    assert candidate["groupable_candidates"] == 299
    assert candidate["withheld_held_cards"] == 1
    assert candidate["requested_cards_accounted_for"] == 300
    assert candidate["complete_island_memberships"] == 30
    assert candidate["tail_island_members"] == 10
    assert candidate["prompt"]["utf8_bytes"] > 0


def test_layout_candidate_restores_full_relative_structure() -> None:
    result = measure()["layout"]
    source = result["source"]
    current = result["current_shared_ir"]
    candidate = result["route_b_candidate"]

    assert source == {
        "cards": 300,
        "typed_card_relations": 300,
        "islands": 30,
    }
    assert current["relative_coordinates"] == 200
    assert current["typed_card_relations"] < 300
    assert current["tail_coordinates_present"] == []
    assert current["tail_required_relations_present"] == []

    assert candidate["relative_coordinates"] == 300
    assert candidate["typed_card_relations"] == 300
    assert candidate["complete_island_memberships"] == 30
    assert candidate["tail_coordinates_present"] == ["c298", "c299"]
    assert candidate["tail_required_relations_present"] == [
        ("c298", "c299", "causal"),
        ("c299", "c000", "negate"),
    ]
    assert candidate["tail_causal_visible_in_prompt"] is True
    assert candidate["tail_negate_visible_in_prompt"] is True
    assert candidate["prompt"]["utf8_bytes"] > 0


def test_measurement_does_not_claim_tokens_or_production_contract() -> None:
    result = measure()
    boundary = result["interpretation_boundary"]
    assert "No provider is called" in boundary
    assert "not token counts" in boundary
    assert "no production projection contract" in boundary
