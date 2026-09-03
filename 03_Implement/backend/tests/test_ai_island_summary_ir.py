import pytest
from fastapi import HTTPException

from kj_atlas_api.models import Card, DocumentV1, Edge, EvidenceLink, Island, Transform
from kj_atlas_api.models_ai import SuggestIslandSummaryRequest
from kj_atlas_api.routes.ai_island_summary_ir import (
    build_suggest_island_summary_ir,
    render_suggest_island_summary_ir_context,
)


def _document(
    *,
    cards: list[Card],
    islands: list[Island],
    edges: list[Edge] | None = None,
    evidence_links: list[EvidenceLink] | None = None,
) -> DocumentV1:
    return DocumentV1(
        version=1,
        id="doc-island-summary-ir",
        title="表札候補IRの回帰入力",
        createdAt="2026-09-03T00:00:00Z",
        updatedAt="2026-09-03T00:00:00Z",
        transform=Transform(panX=0, panY=0, zoom=1),
        cards=cards,
        edges=edges or [],
        islands=islands,
        evidenceLinks=evidence_links or [],
    )


def _card(card_id: str, text: str | None = None) -> Card:
    return Card(
        id=card_id,
        text=text or f"{card_id} の観察を保持する。",
        x=0,
        y=0,
        textReviewed=True,
    )


def test_target_island_direct_members_are_reserved_before_card_truncation() -> None:
    """通常の200枚上限より後ろにある直接メンバーも、表札判断では落とさない。"""
    cards = [_card(f"c{i:03d}") for i in range(210)]
    target_ids = ["c205", "c206", "c207"]
    doc = _document(
        cards=cards,
        islands=[Island(id="target", cardIds=target_ids, title="対象島", titleReviewed=True)],
    )
    payload = SuggestIslandSummaryRequest(doc=doc, islandId="target")

    ir = build_suggest_island_summary_ir(payload)
    ir_card_ids = {card["id"] for card in ir["cards"]}

    assert set(target_ids) <= ir_card_ids
    assert ir["truncation"]["truncated"] is True
    target_ir = next(island for island in ir["islands"] if island["id"] == "target")
    assert target_ir["card_ids"] == sorted(target_ids)


def test_context_preserves_structure_relations_and_human_contradiction_state() -> None:
    """表札に必要な構造・論理関係・人間判断済みの矛盾状態をIRから描画する。"""
    cards = [_card("c1", "利用者は操作の理由を後から確かめたい。"), _card("c2", "自動要約だけでは異論が消える。"), _card("c3", "別の観察が島の外に残る。")]
    doc = _document(
        cards=cards,
        islands=[
            Island(id="parent", cardIds=[], title="親島", titleReviewed=True),
            Island(
                id="target",
                cardIds=["c1", "c2"],
                parentIslandId="parent",
                placardCardId="c1",
                title="根拠へ戻れる理解を保つ。",
                titleReviewed=True,
            ),
            Island(id="other", cardIds=["c3"], title="別島", titleReviewed=True),
        ],
        edges=[
            Edge(id="e1", fromId="c1", toId="c2", type="causal", fromKind="card", toKind="card"),
            Edge(id="e2", fromId="c2", toId="c3", type="negate", fromKind="card", toKind="card"),
        ],
        evidence_links=[
            EvidenceLink(
                id="ev1",
                type="contradicts",
                fromCardId="c2",
                toCardId="c3",
                contradictionState="confirmed",
            )
        ],
    )
    payload = SuggestIslandSummaryRequest(doc=doc, islandId="target")

    ir = build_suggest_island_summary_ir(payload)
    context = render_suggest_island_summary_ir_context(payload, ir)

    assert '"parent_island_id": "parent"' in context
    assert '"placard_card_id": "c1"' in context
    assert '"review_state": "human_reviewed"' in context
    assert '"type": "causal"' in context
    assert '"type": "negate"' in context
    assert '"contradiction_state": "confirmed"' in context
    assert '"id": "derived-island:other|target|negate"' in context


def test_more_than_ir_budget_direct_members_fails_closed() -> None:
    """一つの島がIR上限を超える場合、メンバーを黙って欠落させない。"""
    cards = [_card(f"c{i:03d}", "短い観察。") for i in range(201)]
    doc = _document(
        cards=cards,
        islands=[
            Island(
                id="target",
                cardIds=[card.id for card in cards],
                title="大きすぎる島",
                titleReviewed=True,
            )
        ],
    )
    payload = SuggestIslandSummaryRequest(doc=doc, islandId="target")

    with pytest.raises(HTTPException) as exc_info:
        build_suggest_island_summary_ir(payload)

    assert exc_info.value.status_code == 422
    assert exc_info.value.detail["code"] == "required_card_budget_exceeded"
