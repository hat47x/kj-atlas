from fastapi import HTTPException

from kj_atlas_api.models import Card, DocumentV1, Edge, Island, SuggestLayoutRequest, Transform
from kj_atlas_api.models_ai import CheckNarrativeRequest, GenerateNarrativeRequest, SummarizeIslandRelationRequest
from kj_atlas_api.routes.ai import (
    _build_generate_narrative_prompt,
    _build_narrative_check_prompt,
    _build_prompt,
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
