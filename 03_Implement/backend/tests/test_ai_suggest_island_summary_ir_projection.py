"""`suggest-island-summary` のStage 5 IR投影を固定する回帰テスト。

表札候補は対象島の直接メンバー全員へ戻せることが前提である。したがって、
カード件数や文字数の上限によって直接メンバー本文が欠けた状態を、通常の候補生成として
扱わない。また、表札の論理的位置や警告判断に必要な関係・根拠・既決矛盾だけを、
対象島に接続する文脈として取り出せることを確認する。
"""

from __future__ import annotations

import pytest

from kj_atlas_api import llm_input_ir
from kj_atlas_api.island_summary_ir import (
    build_suggest_island_summary_ir,
    island_summary_context_lines,
)
from kj_atlas_api.llm_input_ir import IRGenerationError, IR_VERSION, MAX_CARDS
from kj_atlas_api.models_ai import SuggestIslandSummaryRequest


def _request(*, member_texts: list[str] | None = None) -> SuggestIslandSummaryRequest:
    texts = member_texts or [
        "利用者は急いで結論へ進むより、違和感を残して考え続けたい",
        "少数の異論が消えると、後から判断の経路へ戻れなくなる",
    ]
    member_cards = [
        {
            "id": f"m-{index}",
            "text": text,
            "x": index * 40,
            "y": 0,
            "textReviewed": True,
        }
        for index, text in enumerate(texts, start=1)
    ]
    other_cards = [
        {
            "id": "outside-1",
            "text": "外側には別の観点があり、対象島の訴えと緊張関係にある",
            "x": 200,
            "y": 0,
            "textReviewed": True,
        },
        {
            "id": "outside-2",
            "text": "対象島とは無関係な別の論点",
            "x": 240,
            "y": 0,
            "textReviewed": True,
        },
    ]
    member_ids = [card["id"] for card in member_cards]
    return SuggestIslandSummaryRequest.model_validate(
        {
            "doc": {
                "version": 1,
                "id": "island-summary-ir-doc",
                "createdAt": "2026-09-03T00:00:00Z",
                "updatedAt": "2026-09-03T00:00:00Z",
                "transform": {"panX": 0, "panY": 0, "zoom": 1},
                "cards": [*member_cards, *other_cards],
                "edges": [
                    {
                        "id": "rel-member",
                        "fromId": member_ids[0],
                        "toId": "outside-1",
                        "type": "negate",
                    },
                    {
                        "id": "rel-unrelated",
                        "fromId": "outside-1",
                        "toId": "outside-2",
                        "type": "related",
                    },
                ],
                "islands": [
                    {
                        "id": "parent",
                        "cardIds": [],
                        "title": "上位の論点",
                        "titleReviewed": True,
                    },
                    {
                        "id": "target",
                        "cardIds": member_ids,
                        "title": "急いで閉じずに判断の経路を残す",
                        "titleReviewed": True,
                        "parentIslandId": "parent",
                        "placardCardId": member_ids[0],
                    },
                ],
                "evidenceLinks": [
                    {
                        "id": "ev-member",
                        "type": "contradicts",
                        "fromCardId": member_ids[1],
                        "toCardId": "outside-1",
                        "contradictionState": "confirmed",
                    },
                    {
                        "id": "ev-unrelated",
                        "type": "supports",
                        "fromCardId": "outside-1",
                        "toCardId": "outside-2",
                    },
                ],
            },
            "islandId": "target",
        }
    )


def test_direct_member_text_and_island_structure_are_preserved() -> None:
    payload = _request()
    ir = build_suggest_island_summary_ir(payload, allow_unreviewed_text=False)

    assert ir["ir_version"] == IR_VERSION
    assert "coordinates" not in ir

    source_by_id = {card.id: card.text for card in payload.doc.cards}
    projected_by_id = {card["id"]: card["text"] for card in ir["cards"]}
    target = next(island for island in ir["islands"] if island["id"] == "target")

    assert target["card_ids"] == ["m-1", "m-2"]
    assert target["parent_island_id"] == "parent"
    assert target["placard_card_id"] == "m-1"
    assert target["review_state"] == "human_reviewed"
    for card_id in target["card_ids"]:
        assert projected_by_id[card_id] == source_by_id[card_id]


def test_context_is_scoped_to_relations_and_evidence_touching_members() -> None:
    payload = _request()
    ir = build_suggest_island_summary_ir(payload, allow_unreviewed_text=False)
    context = "\n".join(island_summary_context_lines(payload, ir))

    assert "parentIslandId=\"parent\"" in context
    assert "placardCardId=\"m-1\"" in context
    assert "reviewState=\"human_reviewed\"" in context
    assert "negate: m-1 -> outside-1" in context
    assert "contradicts: m-2 -> outside-1 (contradictionState=confirmed" in context

    assert "related: outside-1 -> outside-2" not in context
    assert "supports: outside-1 -> outside-2" not in context


def test_more_direct_members_than_card_budget_fails_closed() -> None:
    texts = [f"直接メンバー{index}の観察" for index in range(MAX_CARDS + 1)]
    payload = _request(member_texts=texts)

    with pytest.raises(IRGenerationError) as exc_info:
        build_suggest_island_summary_ir(payload, allow_unreviewed_text=False)

    assert exc_info.value.code == "required_cards_over_budget"


def test_direct_member_text_truncation_fails_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    payload = _request(
        member_texts=[
            "対象島の第一の直接メンバー本文を完全に保持する必要がある",
            "対象島の第二の直接メンバー本文も完全に保持する必要がある",
        ]
    )
    monkeypatch.setattr(llm_input_ir, "MAX_TEXT_CHARS", 12)

    with pytest.raises(IRGenerationError) as exc_info:
        build_suggest_island_summary_ir(payload, allow_unreviewed_text=False)

    assert exc_info.value.code == "required_island_member_text_not_preserved"


def test_ir_safemode_remains_an_independent_second_layer() -> None:
    payload = _request()
    payload.doc.cards[0].textReviewed = False

    with pytest.raises(IRGenerationError) as exc_info:
        build_suggest_island_summary_ir(payload, allow_unreviewed_text=False)

    assert exc_info.value.code == "unreviewed_text_not_allowed"


def test_missing_or_empty_target_keeps_existing_input_errors() -> None:
    payload = _request()
    payload.islandId = "missing"
    with pytest.raises(ValueError, match="islandId does not exist"):
        build_suggest_island_summary_ir(payload, allow_unreviewed_text=False)

    payload = _request()
    target = next(island for island in payload.doc.islands if island.id == "target")
    target.cardIds = []
    with pytest.raises(ValueError, match="island has no member cards"):
        build_suggest_island_summary_ir(payload, allow_unreviewed_text=False)
