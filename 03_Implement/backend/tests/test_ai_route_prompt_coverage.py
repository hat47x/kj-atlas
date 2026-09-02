"""Deterministic route-level prompt coverage for AI-IR-SCALE-01.

This test does not call an LLM and does not declare the current coverage good.
It fixes the observable difference between the shared IR and the rendered prompt
before Stage 5 changes projection policy.
"""

from scripts.measure_ai_route_prompt_coverage import measure


def test_base_route_prompt_coverage_is_deterministic_and_multidimensional() -> None:
    first = measure()
    second = measure()
    assert first == second

    routes = first["scenarios"]["base"]["routes"]
    groups = routes["suggest-card-groups"]
    layout = routes["suggest-layout"]
    narrative = routes["generate-narrative"]

    # The shared projection still has the 200-card boundary measured by #2817.
    for result in routes.values():
        assert result["ir"]["cards"] == 200
        assert result["ir"]["relations"] == 199
        assert result["ir"]["truncation"] == {
            "truncated": True,
            "reason_codes": ["MAX_CARDS"],
        }
        assert result["coverage"]["visible_in_final_prompt"]["island_titles"] == 30
        assert result["prompt"]["utf8_bytes"] >= result["prompt"]["unicode_chars"]
        assert result["token_measurement"]["exact_input_tokens"] is None

    # suggest-card-groups renders candidate cards and island membership FROM the
    # truncated IR, so the missing third is visible at the actual prompt layer.
    assert groups["coverage"]["visible_in_final_prompt"]["card_texts"] == 200
    assert groups["coverage"]["visible_in_final_prompt"]["complete_island_memberships"] == 20
    assert groups["coverage"]["visible_in_final_prompt"]["typed_relations"] == 199

    # suggest-layout retains the full legacy Cards/Islands sections because its
    # output parser requires all cards, but relative coordinates and relations
    # are IR-derived.  "all cards visible" therefore does not mean full semantic
    # coverage.
    assert layout["coverage"]["visible_in_final_prompt"]["card_texts"] == 300
    assert layout["coverage"]["visible_in_final_prompt"]["complete_island_memberships"] == 30
    assert layout["coverage"]["visible_in_final_prompt"]["typed_relations"] == 199
    assert layout["coverage"]["visible_in_final_prompt"]["relative_coordinates"] == 200

    # generate-narrative keeps the document-derived reading order (including the
    # member card texts) while its typed logical structure comes from the IR.
    assert narrative["coverage"]["visible_in_final_prompt"]["card_texts"] == 300
    assert narrative["coverage"]["visible_in_final_prompt"]["complete_island_memberships"] == 30
    assert narrative["coverage"]["visible_in_final_prompt"]["typed_relations"] == 199


def test_evidence_scenario_distinguishes_inputs_from_rendered_prompt() -> None:
    routes = measure()["scenarios"]["with_evidence"]["routes"]
    groups = routes["suggest-card-groups"]
    layout = routes["suggest-layout"]
    narrative = routes["generate-narrative"]

    assert groups["coverage"]["source"]["evidence_links"] == 30
    assert layout["coverage"]["source"]["evidence_links"] == 30
    assert narrative["coverage"]["source"]["evidence_links"] == 30

    # MAX_CARDS retains the first 20 complete ten-card islands in this
    # deterministic fixture, so 20 of the 30 island-local evidence links survive
    # the shared IR selection.
    assert groups["ir"]["evidence_links"] == 20
    assert layout["ir"]["evidence_links"] == 20
    assert narrative["ir"]["evidence_links"] == 20

    # These two routes carry evidence_links on LLMRequest.inputs but their final
    # prompt builders do not render an evidence section.  The provider transport
    # sends the prompt, so that distinction must stay observable.
    assert groups["coverage"]["visible_in_final_prompt"]["evidence_links"] == 0
    assert layout["coverage"]["visible_in_final_prompt"]["evidence_links"] == 0

    # Narrative explicitly renders every evidence link that survived in the IR.
    assert narrative["coverage"]["visible_in_final_prompt"]["evidence_links"] == 20
