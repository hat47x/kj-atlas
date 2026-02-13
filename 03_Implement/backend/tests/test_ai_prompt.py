from kj_atlas_api.models import CardV2, DocumentV2, EdgeV2, Island, SuggestLayoutRequest, Transform
from kj_atlas_api.routes.ai import _build_prompt


def _sample_payload() -> SuggestLayoutRequest:
    doc = DocumentV2(
        version=2,
        id="doc-1",
        title="sample",
        createdAt="2026-02-11T00:00:00Z",
        updatedAt="2026-02-11T00:00:00Z",
        transform=Transform(panX=10, panY=20, zoom=1.25),
        cards=[
            CardV2(id="c1", text="alpha", x=100, y=200, critique="too close"),
            CardV2(id="c2", text="beta", x=260, y=205),
        ],
        edges=[EdgeV2(id="e1", fromId="c1", toId="c2", type="related")],
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

from fastapi import HTTPException

from kj_atlas_api.models_ai import CheckNarrativeRequest
from kj_atlas_api.routes.ai import _build_narrative_check_prompt, _parse_narrative_check_response


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
