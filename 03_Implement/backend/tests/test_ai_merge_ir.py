"""`suggest-merges` のroute固有IR境界をproviderなしで固定する。"""

import json
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from kj_atlas_api.llm_input_ir import IRGenerationError, RELATION_TYPES
from kj_atlas_api.merge_ir import build_merge_ir_context, merge_ir_prompt_lines
from kj_atlas_api.models import Card, DocumentV1, Edge, EvidenceLink, Island, SuggestMergesRequest, Transform
from kj_atlas_api.routes import ai as ai_route


_NOW = "2026-09-03T00:00:00Z"


def _card(card_id: str, text: str, **updates) -> Card:
    return Card(id=card_id, text=text, x=0, y=0, textReviewed=True, **updates)


def _payload(cards, *, edges=None, evidence_links=None, islands=None) -> SuggestMergesRequest:
    return SuggestMergesRequest(
        doc=DocumentV1(
            version=1,
            id="merge-ir",
            createdAt=_NOW,
            updatedAt=_NOW,
            transform=Transform(panX=0, panY=0, zoom=1),
            cards=cards,
            edges=edges or [],
            islands=islands or [],
            evidenceLinks=evidence_links or [],
        )
    )


def test_context_preserves_merge_semantics_without_raw_sources() -> None:
    raw_source = "customer@example.com/private?token=secret"
    payload = _payload(
        [
            _card("c1", "待ち時間が長い", claimType="fact", sources=[raw_source]),
            _card("c2", "待機時間が長い", claimType="fact", sources=[raw_source]),
            _card("c3", "長いとは限らない", claimType="fact", sources=["other-record"]),
            _card("c-held", "保留中", holdState="held"),
            _card("c-merged", "統合済み", mergedIntoCardId="c1"),
        ],
        edges=[
            Edge(id="e1", fromId="c1", toId="c2", type="equivalence"),
            Edge(id="e2", fromId="c2", toId="c3", type="negate"),
        ],
        evidence_links=[
            EvidenceLink(
                id="ev1",
                type="contradicts",
                fromCardId="c3",
                toCardId="c2",
                contradictionState="held",
            )
        ],
        islands=[Island(id="i1", cardIds=["c1", "c2"]), Island(id="i2", cardIds=["c3"])],
    )

    context = build_merge_ir_context(payload, allow_unreviewed_text=False)
    inputs = context.provider_inputs()
    prompt_context = "\n".join(merge_ir_prompt_lines(context))

    assert inputs["input_contract"] == "suggest_merges_v1"
    projected = {item["id"] for item in inputs["document_ir"]["cards"]}
    assert projected == {"c1", "c2", "c3"}
    assert "c-held" not in projected
    assert "c-merged" not in projected

    meta = {item["id"]: item for item in inputs["merge_cards"]}
    assert meta["c1"]["claim_type"] == "fact"
    assert meta["c1"]["island_ids"] == ["i1"]
    assert meta["c1"]["source_refs"] == meta["c2"]["source_refs"]
    assert meta["c1"]["source_refs"] != meta["c3"]["source_refs"]

    serialized = json.dumps(inputs, ensure_ascii=False)
    assert raw_source not in serialized
    assert "other-record" not in serialized
    assert raw_source not in prompt_context
    assert "other-record" not in prompt_context
    assert "sourceRefs" in prompt_context
    assert 'card "c2" --negate--> card "c3"' in prompt_context
    assert "contradictionState=held" in prompt_context


def test_candidate_text_is_rendered_from_normalized_ir_not_raw_document() -> None:
    raw_text = "alpha\tbeta"
    payload = _payload([_card("c1", raw_text), _card("c2", "alphabeta again")])

    context = build_merge_ir_context(payload, allow_unreviewed_text=False)
    prompt = "\n".join(merge_ir_prompt_lines(context))
    normalized = next(item["text"] for item in context.document_ir["cards"] if item["id"] == "c1")

    assert normalized == "alphabeta"
    assert raw_text not in prompt
    assert json.dumps(normalized, ensure_ascii=False) in prompt


def test_large_document_marks_candidate_window_as_partial_instead_of_silent_full_evaluation() -> None:
    payload = _payload([_card(f"c{i:03d}", f"観察{i:03d}") for i in range(205)])

    context = build_merge_ir_context(payload, allow_unreviewed_text=False)
    inputs = context.provider_inputs()

    assert context.document_eligible_card_count == 205
    assert context.projected_card_count == 200
    assert context.partial_scope is True
    assert inputs["scope"]["partial"] is True
    assert inputs["scope"]["reason_codes"] == ["MAX_CARDS"]
    assert "not the whole eligible document" in "\n".join(merge_ir_prompt_lines(context))


def test_required_candidate_text_truncation_fails_closed() -> None:
    payload = _payload([_card(f"c{i}", "長" * 2000) for i in range(7)])

    with pytest.raises(IRGenerationError) as captured:
        build_merge_ir_context(payload, allow_unreviewed_text=False)

    assert captured.value.code == "required_text_truncated"


def test_required_relation_overflow_fails_closed() -> None:
    cards = [_card("c000", "中心の観察")]
    edges = []
    edge_index = 0
    for i in range(1, 82):
        card_id = f"c{i:03d}"
        cards.append(_card(card_id, f"周辺の観察{i:03d}"))
        for relation_type in RELATION_TYPES:
            edges.append(
                Edge(
                    id=f"e{edge_index:04d}",
                    fromId="c000",
                    toId=card_id,
                    type=relation_type,
                )
            )
            edge_index += 1

    assert len(edges) > 400
    payload = _payload(cards, edges=edges)

    with pytest.raises(IRGenerationError) as captured:
        build_merge_ir_context(payload, allow_unreviewed_text=False)

    assert captured.value.code == "required_relation_missing"


def test_ir_safemode_independently_rejects_eligible_unreviewed_card() -> None:
    payload = _payload(
        [
            _card("c1", "reviewed"),
            Card(id="c2", text="unreviewed", x=0, y=0, textReviewed=False),
        ]
    )

    with pytest.raises(IRGenerationError) as captured:
        build_merge_ir_context(payload, allow_unreviewed_text=False)

    assert captured.value.code == "unreviewed_text_not_allowed"


def test_route_passes_route_specific_input_of_record_to_provider(monkeypatch) -> None:
    raw_text = "alpha\tbeta"
    payload = _payload(
        [
            _card("c1", raw_text, claimType="fact", sources=["source-a"]),
            _card("c2", "alphabeta again", claimType="fact", sources=["source-a"]),
        ]
    )
    captured = {}

    monkeypatch.setattr(ai_route, "_resolve_audit_tenant", lambda *_args, **_kwargs: object())
    monkeypatch.setattr(ai_route, "_audit_llm_trace", lambda *_args, **_kwargs: None)

    def _fake_generate(request):
        captured["request"] = request
        return SimpleNamespace(
            raw_text=(
                '{"suggestions":[{"groupId":"m1","cardIds":["c1","c2"],'
                '"mergedTextDraft":"alphabeta","rationale":"near duplicate"}]}'
            )
        )

    monkeypatch.setattr(ai_route, "generate_with_fallback", _fake_generate)

    response = ai_route.suggest_merges(payload, object(), object())

    request = captured["request"]
    assert request.inputs is not None
    assert request.inputs["input_contract"] == "suggest_merges_v1"
    assert request.inputs["scope"]["partial"] is False
    normalized = next(
        item["text"] for item in request.inputs["document_ir"]["cards"] if item["id"] == "c1"
    )
    assert normalized == "alphabeta"
    assert raw_text not in request.prompt
    assert json.dumps(normalized, ensure_ascii=False) in request.prompt
    assert response.suggestions[0].cardIds == ["c1", "c2"]


def test_route_does_not_call_provider_when_fewer_than_two_cards_are_eligible(monkeypatch) -> None:
    payload = _payload([_card("c1", "active"), _card("c2", "held", holdState="held")])

    def _unexpected_generate(_request):
        raise AssertionError("provider must not be called with fewer than two eligible cards")

    monkeypatch.setattr(ai_route, "generate_with_fallback", _unexpected_generate)

    response = ai_route.suggest_merges(payload, object(), object())

    assert response.suggestions == []


def test_route_converts_ir_failure_to_422_before_provider(monkeypatch) -> None:
    payload = _payload([_card(f"c{i}", "長" * 2000) for i in range(7)])

    def _unexpected_generate(_request):
        raise AssertionError("provider must not be called after IR refusal")

    monkeypatch.setattr(ai_route, "generate_with_fallback", _unexpected_generate)

    with pytest.raises(HTTPException) as captured:
        ai_route.suggest_merges(payload, object(), object())

    assert captured.value.status_code == 422
    assert captured.value.detail["code"] == "required_text_truncated"
