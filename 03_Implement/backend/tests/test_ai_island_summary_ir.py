"""`suggest-island-summary` のIR境界を外部プロバイダーなしで固定する。"""

from types import SimpleNamespace

import pytest

from kj_atlas_api.island_summary_ir import (
    build_island_summary_ir_context,
    island_summary_ir_prompt_lines,
)
from kj_atlas_api.llm_input_ir import IRGenerationError
from kj_atlas_api.models import Card, DocumentV1, Edge, EvidenceLink, Island, Transform
from kj_atlas_api.models_ai import SuggestIslandSummaryRequest
from kj_atlas_api.routes import ai as ai_route


def _payload() -> SuggestIslandSummaryRequest:
    doc = DocumentV1(
        version=1,
        id="summary-ir",
        createdAt="2026-09-03T00:00:00Z",
        updatedAt="2026-09-03T00:00:00Z",
        transform=Transform(panX=0, panY=0, zoom=1),
        cards=[
            Card(id="c1", text="現場では判断に時間がかかる", x=0, y=0, textReviewed=True),
            Card(id="c2", text="確認経路が複数に分かれている", x=10, y=0, textReviewed=True),
            Card(id="c3", text="一方で二重確認が事故を防ぐ", x=20, y=0, textReviewed=True),
            Card(id="c4", text="このカードは対象島と無関係", x=30, y=0, textReviewed=True),
        ],
        edges=[
            Edge(id="r1", fromId="c1", toId="c2", type="causal"),
            Edge(id="r2", fromId="c2", toId="c3", type="negate"),
            Edge(id="r3", fromId="c3", toId="c4", type="related"),
        ],
        islands=[
            Island(
                id="i1",
                cardIds=["c1", "c2"],
                title="確認の負担",
                parentIslandId="i-parent",
                placardCardId="c1",
                titleReviewed=True,
            ),
            Island(id="i-parent", cardIds=[], title="業務運用", titleReviewed=True),
        ],
        evidenceLinks=[
            EvidenceLink(
                id="ev1",
                type="contradicts",
                fromCardId="c3",
                toCardId="c2",
                contradictionState="held",
            ),
            EvidenceLink(id="ev2", type="supports", fromCardId="c3", toCardId="c4"),
        ],
    )
    return SuggestIslandSummaryRequest(doc=doc, islandId="i1")


def test_context_preserves_only_members_and_directly_adjacent_meaning() -> None:
    context = build_island_summary_ir_context(_payload(), allow_unreviewed_text=False)

    assert context.direct_member_ids == frozenset({"c1", "c2"})
    assert context.context_only_card_ids == frozenset({"c3"})
    assert "coordinates" not in context.ir

    projected_ids = {item["id"] for item in context.ir["cards"]}
    assert projected_ids == {"c1", "c2", "c3"}

    relation_keys = {
        (item["from"], item["to"], item["type"])
        for item in context.ir.get("relations", [])
    }
    assert relation_keys == {
        ("c1", "c2", "causal"),
        ("c2", "c3", "negate"),
    }

    evidence_ids = {item["id"] for item in context.ir.get("evidence_links", [])}
    assert evidence_ids == {"ev1"}

    projected_islands = {item["id"]: item for item in context.ir.get("islands", [])}
    assert set(projected_islands) == {"i1", "i-parent"}
    assert projected_islands["i-parent"]["card_ids"] == []


def test_prompt_context_marks_external_card_as_context_only_and_keeps_human_state() -> None:
    context = build_island_summary_ir_context(_payload(), allow_unreviewed_text=False)
    prompt = "\n".join(island_summary_ir_prompt_lines(context))

    assert "direct-member-only rule" in prompt
    assert "do not introduce new facts from them into the placard" in prompt
    assert "never use these IDs in groundingIds" in prompt
    assert 'id="c3"' in prompt
    assert 'card "c2" --negate--> card "c3"' in prompt
    assert "contradictionState=held" in prompt
    assert '"parentIslandId": "i-parent"' in prompt
    assert '"placardCardId": "c1"' in prompt
    assert '"reviewState": "human_reviewed"' in prompt
    assert 'id="c4"' not in prompt


def test_route_passes_only_reduced_ir_and_context_to_provider(monkeypatch) -> None:
    payload = _payload().model_copy(update={"model": "model-test"})
    captured = {}

    monkeypatch.setattr(ai_route, "_assert_model_allowed", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(ai_route, "_resolve_audit_tenant", lambda *_args, **_kwargs: object())
    monkeypatch.setattr(ai_route, "_audit_llm_trace", lambda *_args, **_kwargs: None)

    def _fake_generate(request):
        captured["request"] = request
        return SimpleNamespace(
            raw_text=(
                '{"candidates":[{"summaryText":"確認負担を減らしつつ安全性を保つ必要がある",'
                '"groundingIds":["c1","c2"]}],"warnings":[]}'
            )
        )

    monkeypatch.setattr(ai_route, "generate_with_fallback", _fake_generate)

    response = ai_route.suggest_island_summary(payload, object(), object())

    llm_request = captured["request"]
    assert llm_request.inputs is not None
    assert {item["id"] for item in llm_request.inputs["cards"]} == {"c1", "c2", "c3"}
    assert 'id="c3"' in llm_request.prompt
    assert 'id="c4"' not in llm_request.prompt
    assert response.candidates[0].groundingIds == ["c1", "c2"]


def test_missing_target_island_fails_closed() -> None:
    payload = _payload().model_copy(update={"islandId": "missing"})

    with pytest.raises(IRGenerationError) as captured:
        build_island_summary_ir_context(payload, allow_unreviewed_text=False)

    assert captured.value.code == "target_island_missing"
    assert "missing" not in captured.value.message


def test_required_card_text_truncation_fails_closed() -> None:
    payload = _payload()
    cards = [
        Card(
            id=f"c{i}",
            text=(f"カード{i}の意味を保持する。" + "あ" * 1970),
            x=float(i),
            y=0,
            textReviewed=True,
        )
        for i in range(1, 8)
    ]
    doc = payload.doc.model_copy(
        update={
            "cards": cards,
            "edges": [],
            "islands": [
                Island(
                    id="i1",
                    cardIds=[card.id for card in cards],
                    titleReviewed=True,
                )
            ],
            "evidenceLinks": [],
        }
    )
    oversized = SuggestIslandSummaryRequest(doc=doc, islandId="i1")

    with pytest.raises(IRGenerationError) as captured:
        build_island_summary_ir_context(oversized, allow_unreviewed_text=False)

    assert captured.value.code == "required_text_truncated"


def test_target_relevant_relation_overflow_fails_closed() -> None:
    payload = _payload()
    cards = [
        Card(id="c0", text="対象島の中心カード", x=0, y=0, textReviewed=True),
        *[
            Card(id=f"c{i}", text=f"隣接カード{i}", x=float(i), y=0, textReviewed=True)
            for i in range(1, 82)
        ],
    ]
    relation_types = ("related", "negate", "causal", "mutual", "equivalence")
    edges = []
    edge_index = 0
    for neighbor in range(1, 82):
        for relation_type in relation_types:
            if edge_index == 401:
                break
            edges.append(
                Edge(
                    id=f"r{edge_index}",
                    fromId="c0",
                    toId=f"c{neighbor}",
                    type=relation_type,
                )
            )
            edge_index += 1
        if edge_index == 401:
            break

    doc = payload.doc.model_copy(
        update={
            "cards": cards,
            "edges": edges,
            "islands": [Island(id="i1", cardIds=["c0"], titleReviewed=True)],
            "evidenceLinks": [],
        }
    )
    overflow = SuggestIslandSummaryRequest(doc=doc, islandId="i1")

    with pytest.raises(IRGenerationError) as captured:
        build_island_summary_ir_context(overflow, allow_unreviewed_text=False)

    assert captured.value.code == "required_relation_missing"
