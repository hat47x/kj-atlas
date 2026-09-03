"""Characterization tripwires for AI-IR-SCALE-01 route-required meaning.

These assertions deliberately describe the CURRENT projection at 300-card
scale.  They are not acceptance criteria for the final remediation.  Keeping
this baseline makes the eventual fix reviewable: a change should move the
specific route-required dimensions, not merely increase a global count.
"""

from scripts.measure_ai_route_required_meaning import measure


def test_required_meaning_probe_is_deterministic() -> None:
    assert measure() == measure()


def test_detect_tail_pair_loses_prior_human_adjudication_under_global_cap() -> None:
    result = measure()["scenarios"]["detect-target-tail"]

    assert result["ir"]["truncation"] == {
        "truncated": True,
        "reason_codes": ["MAX_CARDS"],
    }
    # The two cards are the explicit subject of the route, yet the shared
    # centrality selection removes them because the 300-card ring ties and IDs
    # c000..c199 win the deterministic tiebreak.
    assert result["ir"]["focus_cards_present"] == []
    # More importantly for AC-1, the already-held contradiction between the
    # explicit pair is pruned with its endpoints, so the deterministic guard can
    # no longer recognize the human's previous judgement.
    assert result["ir"]["held_evidence_present"] is False
    assert result["ir"]["adjudicated_contradiction_found"] is False


def test_groups_tail_island_becomes_empty_and_tail_hold_leaves_projected_set() -> None:
    result = measure()["scenarios"]["groups-late-islands-and-holds"]

    assert result["ir"]["truncation"] == {
        "truncated": True,
        "reason_codes": ["MAX_CARDS"],
    }
    assert result["source"]["tail_island_member_count"] == 10
    assert result["ir"]["tail_island_present"] is True
    assert result["ir"]["tail_island_member_count"] == 0
    assert result["ir"]["held_card_present"] is False
    # The card is neither proposed nor reported as withheld: it disappeared at
    # projection time.  The response's generic `truncated` flag is therefore the
    # only remaining signal that the requested set is incomplete.
    assert result["grouping"]["held_card_candidate"] is False
    assert result["grouping"]["held_card_withheld"] is False


def test_narrative_tail_causal_and_negate_skeleton_is_pruned() -> None:
    result = measure()["scenarios"]["narrative-late-causal-negate"]

    assert result["source"]["reading_order_contains_tail_island"] is True
    assert result["ir"]["truncation"] == {
        "truncated": True,
        "reason_codes": ["MAX_CARDS"],
    }
    # AC-3 says causal/negate are the narrative skeleton.  The reading-order
    # item still exists through the document-derived path, while its late-card
    # logical joints disappear from the IR.
    assert result["ir"]["required_relations_present"] == []
    assert result["prompt"]["tail_island_visible"] is True
    assert result["prompt"]["causal_visible"] is False
    assert result["prompt"]["negate_visible"] is False


def test_layout_tail_cards_remain_but_their_relative_structure_is_pruned() -> None:
    result = measure()["scenarios"]["layout-late-structure"]

    assert result["ir"]["truncation"] == {
        "truncated": True,
        "reason_codes": ["MAX_CARDS"],
    }
    # The output contract keeps all cards in the legacy Cards section, but the
    # layout-specific IR context for the late cards is missing.
    assert result["prompt"]["tail_card_a_visible_in_legacy_cards"] is True
    assert result["prompt"]["tail_card_b_visible_in_legacy_cards"] is True
    assert result["ir"]["focus_coordinates_present"] == []
    assert result["ir"]["required_relations_present"] == []
    assert result["prompt"]["tail_relative_coordinate_a_visible"] is False
    assert result["prompt"]["tail_relative_coordinate_b_visible"] is False
    assert result["prompt"]["causal_visible"] is False
    assert result["prompt"]["negate_visible"] is False
