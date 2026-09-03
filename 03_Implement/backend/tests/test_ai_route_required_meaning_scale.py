"""Route-required semantic coverage tripwires for AI-IR-SCALE-01.

The scenarios started as characterization of the 300-card baseline. When a
route-specific remediation lands, its assertions are promoted from "known loss"
to the contract that must now stay fixed, while unresolved routes keep their
characterization until their own remediation is chosen.
"""

from scripts.measure_ai_route_required_meaning import measure


def test_required_meaning_probe_is_deterministic() -> None:
    assert measure() == measure()


def test_detect_tail_pair_preserves_prior_human_adjudication_under_global_cap() -> None:
    result = measure()["scenarios"]["detect-target-tail"]

    assert result["ir"]["truncation"] == {
        "truncated": True,
        "reason_codes": ["MAX_CARDS"],
    }
    # The two cards are the explicit subject of this route. They are reserved
    # before the global centrality cut, rather than competing with unrelated
    # document cards for the ordinary top-200 slots.
    assert result["ir"]["focus_cards_present"] == ["c298", "c299"]
    # AC-1: preserving both endpoints also keeps their held contradiction
    # referentially closed, so the deterministic guard can honor the human's
    # previous judgement without asking the model again.
    assert result["ir"]["held_evidence_present"] is True
    assert result["ir"]["adjudicated_contradiction_found"] is True


def test_groups_tail_hold_is_preserved_without_claiming_full_island_coverage() -> None:
    result = measure()["scenarios"]["groups-late-islands-and-holds"]

    assert result["ir"]["truncation"] == {
        "truncated": True,
        "reason_codes": ["MAX_CARDS"],
    }
    assert result["source"]["tail_island_member_count"] == 10
    assert result["ir"]["tail_island_present"] is True
    # Only the requested card carrying the human's hold decision is reserved.
    # The other nine tail-island members remain outside the global top-200, so
    # this remediation does not pretend to solve complete island coverage.
    assert result["ir"]["tail_island_member_count"] == 1
    assert result["ir"]["held_card_present"] is True
    # AC-2: the held card must be explicitly reported as withheld and must never
    # become a grouping candidate merely because the document is large.
    assert result["grouping"]["held_card_candidate"] is False
    assert result["grouping"]["held_card_withheld"] is True
    assert result["grouping"]["tail_island_membership_visible_in_prompt"] is True


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
