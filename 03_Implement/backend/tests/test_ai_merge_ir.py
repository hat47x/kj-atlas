import json
from types import SimpleNamespace

import pytest

from kj_atlas_api.llm_input_ir import IRGenerationError
from kj_atlas_api.merge_suggestion_ir import (
    ROUTE_INPUT_VERSION,
    build_merge_suggestion_ir_context,
)
from kj_atlas_api.models import (
    Card,
    CardMeta,
    DocumentV1,
    Edge,
    EvidenceLink,
    Island,
    SuggestMergesRequest,
    Transform,
)
from kj_atlas_api.routes import ai


def _card(card_id: str, text: str, **updates) -> Card:
    return Card(id=card_id, text=text, x=0, y=0, textReviewed=True, **updates)


def _payload(cards, *, edges=None, islands=None, evidence_links=None) -> SuggestMergesRequest:
    return SuggestMergesRequest(
        doc=DocumentV1(
            version=1,
            id="doc-merge-ir",
            title="merge ir",
            createdAt="2026-09-03T00:00:00Z",
            updatedAt="2026-09-03T00:00:00Z",
            transform=Transform(panX=0, panY=0, zoom=1),
            cards=cards,
            edges=edges or [],
            islands=islands or [],
            evidenceLinks=evidence_links or [],
        )
    )


def _context(payload: SuggestMergesRequest):
    return build_merge_suggestion_ir_context(payload, allow_unreviewed_text=False)


def test_merge_ir_excludes_held_already_merged_and_canonicalized_source_cards() -> None:
    payload = _payload(
        [
            _card("c1", "alpha"),
            _card("c2", "beta"),
            _card("c3", "held", holdState="held"),
            _card("c4", "represented", mergedIntoCardId="c1"),
            _card("c5", "canonicalized source", canonicalId="c1"),
        ]
    )

    context = _context(payload)

    assert context.candidate_card_ids == frozenset({"c1", "c2"})
    assert {item["id"] for item in context.document_ir["cards"]} == {"c1", "c2"}


def test_merge_ir_carries_claim_island_and_card_lineage_without_external_source_text() -> None:
    payload = _payload(
        [
            _card("old-1", "older alpha", canonicalId="c1"),
            _card("old-2", "older alpha detail", canonicalId="c1"),
            _card(
                "c1",
                "alpha",
                claimType="fact",
                repOf=["rep-old-2", "rep-old-1"],
                sources=["old-2", "old-1"],
                meta=CardMeta(source="person@example.com"),
            ),
            _card(
                "c2",
                "alpha independently observed",
                claimType="fact",
                meta=CardMeta(source="https://example.test/source-a"),
            ),
            _card("c3", "different source", meta=CardMeta(source="source-b")),
        ],
        islands=[
            Island(id="i1", cardIds=["c1", "c2"]),
            Island(id="i2", cardIds=["c1", "c3"]),
        ],
    )

    context = _context(payload)
    by_id = {
        item["id"]: item
        for item in context.inputs["mergeContext"]["candidateCards"]
    }

    assert context.inputs["routeInputVersion"] == ROUTE_INPUT_VERSION
    assert context.candidate_card_ids == frozenset({"c1", "c2", "c3"})
    assert by_id["c1"]["claimType"] == "fact"
    assert by_id["c1"]["islandIds"] == ["i1", "i2"]
    assert by_id["c1"]["lineage"]["repOf"] == ["rep-old-1", "rep-old-2"]
    assert by_id["c1"]["lineage"]["sourceCardIds"] == ["old-1", "old-2"]

    serialized = json.dumps(context.inputs, ensure_ascii=False, sort_keys=True)
    assert "person@example.com" not in serialized
    assert "https://example.test/source-a" not in serialized
    assert "source-b" not in serialized


def test_merge_ir_preserves_candidate_relations_and_contradiction_state() -> None:
    payload = _payload(
        [_card("c1", "alpha"), _card("c2", "beta"), _card("c3", "gamma")],
        edges=[
            Edge(id="e1", fromId="c1", toId="c2", fromKind="card", toKind="card", type="equivalence"),
            Edge(id="e2", fromId="c2", toId="c3", fromKind="card", toKind="card", type="negate"),
        ],
        evidence_links=[
            EvidenceLink(
                id="ev1",
                type="contradicts",
                fromCardId="c1",
                toCardId="c3",
                contradictionState="held",
            )
        ],
    )

    context = _context(payload)

    relation_keys = {
        (item["from"], item["to"], item["type"])
        for item in context.document_ir["relations"]
    }
    assert ("c1", "c2", "equivalence") in relation_keys
    assert ("c2", "c3", "negate") in relation_keys
    assert context.document_ir["evidence_links"][0]["contradiction_state"] == "held"


def test_merge_ir_fails_closed_when_card_text_contains_pii() -> None:
    payload = _payload(
        [
            _card("c1", "連絡先は person@example.com です"),
            _card("c2", "連絡先を含まない観察です"),
        ]
    )

    with pytest.raises(IRGenerationError) as exc_info:
        _context(payload)

    assert exc_info.value.code == "pii_detected"


def test_merge_ir_fails_closed_when_required_text_would_be_truncated() -> None:
    payload = _payload([_card(f"c{i}", "x" * 2000) for i in range(7)])

    with pytest.raises(IRGenerationError) as exc_info:
        _context(payload)

    assert exc_info.value.code == "required_text_truncated"


def test_merge_ir_fails_closed_when_candidate_count_exceeds_ir_budget() -> None:
    payload = _payload([_card(f"c{i:03d}", "short") for i in range(201)])

    with pytest.raises(IRGenerationError) as exc_info:
        _context(payload)

    assert exc_info.value.code == "required_card_budget_exceeded"


def test_merge_prompt_is_rendered_from_route_input_not_live_document_text_or_external_source() -> None:
    payload = _payload(
        [
            _card(
                "c1",
                "alpha   beta",
                claimType="fact",
                sources=["old-1"],
                meta=CardMeta(source="person@example.com"),
            ),
            _card("c2", "alpha beta again", claimType="fact"),
        ],
        islands=[Island(id="i1", cardIds=["c1", "c2"])],
        edges=[Edge(id="e1", fromId="c1", toId="c2", type="equivalence")],
    )
    context = _context(payload)
    # IR構築後にDocument側だけを書き換え、最終promptが同じprovider inputsから
    # 描画されていることを確認する。
    payload.doc.cards[0].text = "RAW-MUTATED-TEXT"

    prompt = ai._build_merge_prompt(payload, context)

    assert "alpha   beta" in prompt
    assert "RAW-MUTATED-TEXT" not in prompt
    assert "claimType" in prompt
    assert "islandIds" in prompt
    assert "equivalence" in prompt
    assert "sourceCardIds" in prompt
    assert "old-1" in prompt
    assert "person@example.com" not in prompt


def test_merge_route_sends_route_specific_inputs_to_provider(monkeypatch) -> None:
    payload = _payload(
        [
            _card(
                "c1",
                "alpha",
                claimType="fact",
                sources=["old-1"],
                meta=CardMeta(source="person@example.com"),
            ),
            _card("c2", "alpha again", claimType="fact"),
        ]
    )
    captured = {}

    def fake_generate(request):
        captured["request"] = request
        return SimpleNamespace(raw_text='{"suggestions":[]}')

    monkeypatch.setattr(ai, "generate_with_fallback", fake_generate)
    monkeypatch.setattr(ai, "_resolve_audit_tenant", lambda *args, **kwargs: object())
    monkeypatch.setattr(ai, "_audit_llm_trace", lambda *args, **kwargs: None)

    response = ai.suggest_merges(payload, request=object(), db=object())

    assert response.suggestions == []
    provider_request = captured["request"]
    assert provider_request.inputs["routeInputVersion"] == ROUTE_INPUT_VERSION
    by_id = {
        item["id"]: item
        for item in provider_request.inputs["mergeContext"]["candidateCards"]
    }
    assert by_id["c1"]["lineage"]["sourceCardIds"] == ["old-1"]
    serialized = json.dumps(provider_request.inputs, ensure_ascii=False, sort_keys=True)
    assert "person@example.com" not in serialized


def test_merge_route_skips_provider_when_fewer_than_two_candidates(monkeypatch) -> None:
    payload = _payload(
        [
            _card("c1", "active"),
            _card("c2", "held", holdState="held"),
        ]
    )

    def fail_if_called(_request):
        raise AssertionError("provider must not be called")

    monkeypatch.setattr(ai, "generate_with_fallback", fail_if_called)

    response = ai.suggest_merges(payload, request=object(), db=object())

    assert response.suggestions == []


def test_merge_parser_rejects_card_outside_route_candidate_set() -> None:
    payload = _payload(
        [
            _card("c1", "active"),
            _card("c2", "active too"),
            _card("c3", "held", holdState="held"),
            _card("c4", "canonicalized source", canonicalId="c1"),
        ]
    )

    with pytest.raises(Exception) as exc_info:
        ai._parse_merge_suggestions(
            '{"suggestions":[{"groupId":"m1","cardIds":["c1","c4"],"mergedTextDraft":"draft","mergeMethod":"near_duplicate"}]}',
            payload,
            allowed_card_ids=frozenset({"c1", "c2"}),
        )

    assert getattr(exc_info.value, "status_code", None) == 422
