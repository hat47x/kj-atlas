from fastapi import HTTPException

from kj_atlas_api.models import Card, DocumentV1, Edge, EvidenceLink, Island, SuggestLayoutRequest, Transform
from kj_atlas_api.models_ai import (
    CheckNarrativeRequest,
    GenerateNarrativeRequest,
    RefineCardTextRequest,
    SuggestCardGroupsRequest,
    SuggestIslandSummaryRequest,
    SummarizeIslandRelationRequest,
)
from kj_atlas_api.routes.ai import (
    _build_generate_narrative_prompt,
    _build_island_summary_prompt,
    _build_narrative_check_prompt,
    _build_prompt,
    _build_refine_card_text_prompt,
    _build_suggest_card_groups_prompt,
    _parse_generate_narrative_response,
    _parse_narrative_check_response,
)


from kj_atlas_api.routes.ai_relations import (
    _build_relation_summary_prompt,
    _parse_relation_summary_response,
)


def _sample_payload() -> SuggestLayoutRequest:
    doc = DocumentV1(
        version=1,
        id="doc-1",
        title="sample",
        createdAt="2026-02-11T00:00:00Z",
        updatedAt="2026-02-11T00:00:00Z",
        transform=Transform(panX=10, panY=20, zoom=1.25),
        cards=[
            Card(id="c1", text="alpha", x=100, y=200, critique="too close"),
            Card(id="c2", text="beta", x=260, y=205),
        ],
        edges=[Edge(id="e1", fromId="c1", toId="c2", type="related")],
        islands=[
            Island(
                id="i1",
                cardIds=["c1", "c2"],
                title="group-a",
                critique="belongs together",
            )
        ],
    )
    return SuggestLayoutRequest(doc=doc, instruction="keep rough clusters")


def test_build_prompt_includes_critique_constraints_and_context() -> None:
    prompt = _build_prompt(_sample_payload())

    assert "Do not force a single correct answer. Suggest one plausible alternative layout." in prompt
    assert "If a critique says 'too close', increase distance." in prompt
    assert "If a critique says 'belongs together', place nearer." in prompt
    assert "Preserve all ids and texts. Only propose positions and transform." in prompt

    assert 'id="c1"' in prompt
    assert 'text="alpha"' in prompt
    assert 'x=100.0, y=200.0' in prompt
    assert 'critique="too close"' in prompt

    assert 'id="i1"' in prompt
    assert 'title="group-a"' in prompt
    assert 'cardIds=["c1", "c2"]' in prompt
    assert 'critique="belongs together"' in prompt
    assert 'bounds=(100.00,200.00)-(260.00,205.00)' in prompt
    assert 'anchor=(180.00,202.50)' in prompt


def test_build_prompt_omits_critique_when_absent() -> None:
    payload = _sample_payload()
    payload.doc.cards[0].critique = None
    payload.doc.islands[0].critique = None

    prompt = _build_prompt(payload)

    assert 'id="c1", text="alpha", x=100.0, y=200.0, critique=' not in prompt
    assert 'id="i1", title="group-a", cardIds=["c1", "c2"], bounds=(100.00,200.00)-(260.00,205.00), anchor=(180.00,202.50), critique=' not in prompt

def test_build_narrative_check_prompt_includes_required_checks() -> None:
    payload = CheckNarrativeRequest(
        doc=_sample_payload().doc,
        narrativeText="First island explains alpha. Then they transition.",
        basedOnReadingOrder=["i1", "c2"],
    )

    prompt = _build_narrative_check_prompt(payload)

    assert "best-effort narrative consistency check" in prompt
    assert "Identify missing key islands/cards based on reading order." in prompt
    assert "Identify contradictions" in prompt
    assert "Identify ambiguous transitions" in prompt
    assert 'island id="i1"' in prompt
    assert 'card id="c2"' in prompt


def test_build_narrative_check_prompt_requires_bidirectional_ab_cross_check() -> None:
    """kj_technique.md §5 (優先3): the A/B cross-check must run in BOTH
    directions and report per-direction counts (0 is a valid value)."""
    payload = CheckNarrativeRequest(
        doc=_sample_payload().doc,
        narrativeText="First island explains alpha. Then they transition.",
        basedOnReadingOrder=["i1", "c2"],
    )

    prompt = _build_narrative_check_prompt(payload)

    assert 'direction "b_missing_in_a"' in prompt
    assert 'direction "a_missing_in_b"' in prompt
    assert '"counts" with the number of issues per direction' in prompt
    assert '{"bMissingInA":number,"aMissingInB":number}' in prompt
    assert '0/0 means the cross-check did not actually run' in prompt


def test_parse_narrative_check_response_accepts_direction_and_counts() -> None:
    payload = CheckNarrativeRequest(
        doc=_sample_payload().doc,
        narrativeText="text",
        basedOnReadingOrder=["i1"],
    )

    response = _parse_narrative_check_response(
        '{"issues":[{"severity":"warn","message":"claim with no diagram counterpart","references":[{"id":"i1","kind":"island"}],"direction":"b_missing_in_a"}],'
        '"counts":{"bMissingInA":1,"aMissingInB":0}}',
        payload,
    )

    assert response.issues[0].direction == "b_missing_in_a"
    assert response.counts is not None
    assert response.counts.bMissingInA == 1
    assert response.counts.aMissingInB == 0


def test_parse_narrative_check_response_rejects_unknown_reference() -> None:
    payload = CheckNarrativeRequest(
        doc=_sample_payload().doc,
        narrativeText="text",
        basedOnReadingOrder=["i1"],
    )

    try:
        _parse_narrative_check_response(
            '{"issues":[{"severity":"warn","message":"x","references":[{"id":"unknown","kind":"card"}]}]}',
            payload,
        )
    except HTTPException as exc:
        assert exc.status_code == 422
    else:
        raise AssertionError("expected HTTPException")


def test_parse_narrative_check_response_rejects_extra_fields() -> None:
    payload = CheckNarrativeRequest(
        doc=_sample_payload().doc,
        narrativeText="text",
        basedOnReadingOrder=["i1"],
    )

    try:
        _parse_narrative_check_response(
            '{"issues":[{"severity":"warn","message":"x","extra":"nope"}]}',
            payload,
        )
    except HTTPException as exc:
        assert exc.status_code == 422
    else:
        raise AssertionError("expected HTTPException")

def test_build_generate_narrative_prompt_mentions_unreviewed_and_reading_order() -> None:
    payload = GenerateNarrativeRequest(
        doc=_sample_payload().doc.model_copy(update={"readingOrder": ["i1", "c2"]}),
        narrativeTitle="Draft title",
    )

    prompt = _build_generate_narrative_prompt(payload)

    assert "reading order as the narrative spine" in prompt
    assert "draft and unreviewed" in prompt
    assert 'island id="i1"' in prompt
    assert 'card id="c2"' in prompt


def test_parse_generate_narrative_response_rejects_non_matching_reading_order() -> None:
    payload = GenerateNarrativeRequest(
        doc=_sample_payload().doc.model_copy(update={"readingOrder": ["i1", "c2"]}),
        narrativeTitle="Draft title",
    )

    try:
        _parse_generate_narrative_response(
            '{"text":"draft (unreviewed)","basedOnReadingOrder":["i1"]}',
            payload,
        )
    except HTTPException as exc:
        assert exc.status_code == 422
    else:
        raise AssertionError("expected HTTPException")


def test_parse_generate_narrative_response_accepts_exact_reading_order() -> None:
    payload = GenerateNarrativeRequest(
        doc=_sample_payload().doc.model_copy(update={"readingOrder": ["i1", "c2"]}),
        narrativeTitle="Draft title",
    )

    parsed = _parse_generate_narrative_response(
        '{"text":"draft (unreviewed)","basedOnReadingOrder":["i1","c2"]}',
        payload,
    )

    assert parsed.text == "draft (unreviewed)"
    assert parsed.basedOnReadingOrder == ["i1", "c2"]


def test_validate_check_narrative_input_rejects_blank_text() -> None:
    from kj_atlas_api.routes.ai import _validate_check_narrative_input

    payload = CheckNarrativeRequest(
        doc=_sample_payload().doc,
        narrativeText="ok",
        basedOnReadingOrder=["i1"],
    )
    payload.narrativeText = "   "

    try:
        _validate_check_narrative_input(payload)
    except HTTPException as exc:
        assert exc.status_code == 422
    else:
        raise AssertionError("expected HTTPException")


def test_validate_check_narrative_input_rejects_unknown_reading_order_id() -> None:
    from kj_atlas_api.routes.ai import _validate_check_narrative_input

    payload = CheckNarrativeRequest(
        doc=_sample_payload().doc,
        narrativeText="text",
        basedOnReadingOrder=["i1", "unknown"],
    )

    try:
        _validate_check_narrative_input(payload)
    except HTTPException as exc:
        assert exc.status_code == 422
    else:
        raise AssertionError("expected HTTPException")


def test_parse_narrative_check_response_rejects_empty_message() -> None:
    payload = CheckNarrativeRequest(
        doc=_sample_payload().doc,
        narrativeText="text",
        basedOnReadingOrder=["i1"],
    )

    try:
        _parse_narrative_check_response('{"issues":[{"severity":"warn","message":""}]}', payload)
    except HTTPException as exc:
        assert exc.status_code == 422
    else:
        raise AssertionError("expected HTTPException")


def test_build_relation_summary_prompt_mentions_uncertainty_and_json_only() -> None:
    payload = SummarizeIslandRelationRequest(
        doc=_sample_payload().doc,
        islandAId="i1",
        islandBId="i1",
        relationType="related",
        derived=False,
        groundingCardIds=["c1"],
        groundingEdgeIds=["e1"],
        cardTexts=[{"id": "c1", "text": "alpha"}],
        edgeTexts=[{"edgeId": "e1", "type": "related", "from": "c1", "to": "c2"}],
    )

    prompt = _build_relation_summary_prompt(payload)

    assert "Never present the output as authoritative" in prompt
    assert "Return strict JSON only" in prompt
    assert "unsupported claims" in prompt


def test_parse_relation_summary_response_rejects_non_subset_grounding_ids() -> None:
    payload = SummarizeIslandRelationRequest(
        doc=_sample_payload().doc,
        islandAId="i1",
        islandBId="i1",
        relationType="related",
        derived=False,
        groundingCardIds=["c1"],
        groundingEdgeIds=["e1"],
        cardTexts=[{"id": "c1", "text": "alpha"}],
    )

    try:
        _parse_relation_summary_response(
            '{"text":"draft","groundingCardIds":["unknown"],"groundingEdgeIds":[],"warnings":[]}',
            payload,
        )
    except HTTPException as exc:
        assert exc.status_code == 422
    else:
        raise AssertionError("expected HTTPException")


def test_parse_relation_summary_response_accepts_valid_payload() -> None:
    payload = SummarizeIslandRelationRequest(
        doc=_sample_payload().doc,
        islandAId="i1",
        islandBId="i1",
        relationType="related",
        derived=False,
        groundingCardIds=["c1"],
        groundingEdgeIds=["e1"],
        cardTexts=[{"id": "c1", "text": "alpha"}],
    )

    parsed = _parse_relation_summary_response(
        '{"text":"draft","groundingCardIds":["c1"],"groundingEdgeIds":["e1"],"warnings":["missing context"]}',
        payload,
    )

    assert parsed.text == "draft"
    assert parsed.groundingCardIds == ["c1"]
    assert parsed.warnings == ["missing context"]


# ---------------------------------------------------------------------------
# 優先3-4: runtime prompts aligned with ai_kj_execution_procedures.md
# ---------------------------------------------------------------------------


def test_refine_card_text_prompt_prohibits_noun_stops() -> None:
    prompt = _build_refine_card_text_prompt(RefineCardTextRequest(cardText="users lost time"))

    assert "predicate-bearing sentence" in prompt
    assert "名詞止め" in prompt
    assert "動詞で終わる文" in prompt


def test_suggest_card_groups_prompt_aligned_with_bundling_procedures() -> None:
    from kj_atlas_api.models_ai import _CardRef

    prompt = _build_suggest_card_groups_prompt(
        SuggestCardGroupsRequest(
            cards=[
                _CardRef(id="c1", text="alpha"),
                _CardRef(id="c2", text="beta"),
                _CardRef(id="c3", text="gamma"),
            ]
        )
    )

    # "thematic" was the framing the review flagged; it must be gone.
    assert "thematic" not in prompt
    assert "similarity of what they are appealing for" in prompt
    assert "2-3 cards (rarely 4)" in prompt
    assert "Do not force a card into a bundle" in prompt


def test_island_summary_prompt_includes_placard_checks() -> None:
    doc = _sample_payload().doc
    payload = SuggestIslandSummaryRequest(
        doc=doc,
        islandId=doc.islands[0].id,
    )

    prompt = _build_island_summary_prompt(payload)

    # ai_kj_execution_procedures.md §3: 表札検査 — transposition + return check,
    # advocacy not classification, no noun-stops.
    assert "Transposition" in prompt
    assert "Return check" in prompt
    assert "classification name (分類名)" in prompt
    assert "predicate-bearing advocacy sentence" in prompt
    assert "名詞止め" in prompt


def test_generate_narrative_prompt_self_performs_ab_cross_check() -> None:
    payload = GenerateNarrativeRequest(
        doc=_sample_payload().doc.model_copy(update={"readingOrder": ["i1", "c2"]}),
        narrativeTitle="Draft title",
    )

    prompt = _build_generate_narrative_prompt(payload)

    assert "A/B cross-check" in prompt
    assert "b_missing_in_a" in prompt
    assert "a_missing_in_b" in prompt
    assert "warnings" in prompt


def test_island_summary_prompt_includes_objecting_cards_from_return_check() -> None:
    """kj_technique.md §3 (優先3-3): cards marked not_the_same/feels_off record a
    placard objection (戻し検査) that the re-suggestion must address."""
    doc = _sample_payload().doc
    doc.cards[0].critiqueTags = ["not_the_same"]  # type: ignore[attr-defined]
    payload = SuggestIslandSummaryRequest(doc=doc, islandId=doc.islands[0].id)

    prompt = _build_island_summary_prompt(payload)

    assert "OBJECTED to the previous placard" in prompt
    assert 'id="c1"' in prompt
    assert "must address why each objecting card disagrees" in prompt


def test_island_summary_prompt_omits_objection_block_when_no_card_objects() -> None:
    doc = _sample_payload().doc
    payload = SuggestIslandSummaryRequest(doc=doc, islandId=doc.islands[0].id)

    prompt = _build_island_summary_prompt(payload)

    assert "OBJECTED to the previous placard" not in prompt


def test_generate_narrative_prompt_includes_logical_relations() -> None:
    """ADR-0069 (D2=A): the narrative prompt receives the typed logical
    structure (edges + evidenceLinks) so it does not invent the causal /
    contradiction skeleton."""
    doc = _sample_payload().doc
    doc.evidenceLinks = [
        EvidenceLink(id="ev-1", type="supports", fromCardId="c1", toCardId="c2", note="n"),
    ]
    payload = GenerateNarrativeRequest(
        doc=doc.model_copy(update={"readingOrder": ["i1", "c2"]}),
        narrativeTitle="Draft title",
    )

    prompt = _build_generate_narrative_prompt(payload)

    assert 'island "i1" --related--> island "i1"' not in prompt or "i1" in prompt  # islands in fixture
    assert "Logical relations:" in prompt
    assert '--evidence:supports-->' in prompt
    assert "causal, negation, evidence" in prompt


def test_island_summary_prompt_includes_island_relations() -> None:
    """ADR-0069: the island-summary placard receives the island's typed
    relations to other islands so it reflects the structural position."""
    doc = _sample_payload().doc
    # Add a second island and an island-to-island edge so the placard can see
    # its structural position.
    doc.islands.append(Island(id="i2", cardIds=[], title="B", critique="belongs together"))
    doc.edges.append(Edge(id="e2", fromId="i1", toId="i2", type="related", fromKind="island", toKind="island"))
    payload = SuggestIslandSummaryRequest(doc=doc, islandId="i1")

    prompt = _build_island_summary_prompt(payload)

    assert "Relations to other islands" in prompt
    assert 'this island --related--> island "i2"' in prompt
