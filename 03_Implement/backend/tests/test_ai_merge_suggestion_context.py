"""`suggest-merges` のroute固有入力契約と決定論的guardを固定する。"""

import pytest

from kj_atlas_api.llm_input_ir import IRGenerationError
from kj_atlas_api.merge_suggestion_context import (
    build_merge_suggestion_context,
    merge_suggestion_prompt,
    validate_merge_suggestion_semantics,
)
from kj_atlas_api.models import (
    Card,
    DocumentV1,
    Edge,
    EvidenceLink,
    MergeSuggestion,
    SuggestMergesRequest,
    Transform,
)


def _payload() -> SuggestMergesRequest:
    doc = DocumentV1(
        version=1,
        id="merge-context",
        createdAt="2026-09-03T00:00:00Z",
        updatedAt="2026-09-03T00:00:00Z",
        transform=Transform(panX=0, panY=0, zoom=1),
        cards=[
            Card(
                id="c1",
                text="利用者は同じ確認事項を二度入力している",
                x=0,
                y=0,
                textReviewed=True,
                claimType="fact",
                sources=["source-a"],
            ),
            Card(
                id="c2",
                text="同一の確認内容が二重入力になっている",
                x=10,
                y=0,
                textReviewed=True,
                claimType="fact",
                sources=["source-b"],
            ),
            Card(
                id="c3",
                text="二重確認は事故を防ぐために必要である",
                x=20,
                y=0,
                textReviewed=True,
                claimType="claim",
                sources=["source-c"],
            ),
            Card(
                id="c4",
                text="この論点は判断を保留している",
                x=30,
                y=0,
                textReviewed=True,
                holdState="held",
            ),
            Card(
                id="c5",
                text="過去の統合結果を表すカードである",
                x=40,
                y=0,
                textReviewed=True,
                repOf=["old-1", "old-2"],
            ),
            Card(
                id="c6",
                text="別の候補として比較できる記述である",
                x=50,
                y=0,
                textReviewed=True,
                claimType="fact",
                sources=["source-a"],
            ),
        ],
        edges=[
            Edge(id="r1", fromId="c1", toId="c2", type="equivalence"),
            Edge(id="r2", fromId="c2", toId="c3", type="negate"),
        ],
        evidenceLinks=[
            EvidenceLink(
                id="ev1",
                type="contradicts",
                fromCardId="c1",
                toCardId="c3",
                contradictionState="confirmed",
            )
        ],
    )
    return SuggestMergesRequest(doc=doc)


def _suggestion(group_id: str, *card_ids: str) -> MergeSuggestion:
    return MergeSuggestion(
        groupId=group_id,
        cardIds=list(card_ids),
        mergedTextDraft="二重入力になっている確認事項を一つにまとめられる",
        rationale="意味の重なりを確認するための提案",
    )


def test_context_excludes_held_and_lineage_cards_without_sending_raw_sources() -> None:
    context = build_merge_suggestion_context(_payload(), allow_unreviewed_text=False)

    assert context.hold_ids == frozenset({"c4"})
    assert context.lineage_ids == frozenset({"c5"})
    assert context.protected_ids == frozenset({"c4", "c5"})
    assert context.candidate_ids == frozenset({"c1", "c2", "c3", "c6"})

    cards = {item["id"]: item for item in context.inputs["cards"]}
    assert set(cards) == {"c1", "c2", "c3", "c6"}
    assert all("sources" not in item for item in cards.values())
    assert all("hold_state" not in item for item in cards.values())
    assert cards["c1"]["source_count"] == 1
    assert cards["c1"]["source_ref_digest"] == cards["c6"]["source_ref_digest"]
    assert cards["c1"]["source_ref_digest"] != cards["c2"]["source_ref_digest"]

    rendered = str(context.inputs)
    assert "source-a" not in rendered
    assert "source-b" not in rendered
    assert "source-c" not in rendered
    assert "この論点は判断を保留している" not in rendered
    assert "過去の統合結果を表すカードである" not in rendered


def test_prompt_requires_meaning_preservation_not_similarity_only() -> None:
    context = build_merge_suggestion_context(_payload(), allow_unreviewed_text=False)
    prompt = merge_suggestion_prompt(context, "重複表現を確認する")

    assert "Similarity or a shared topic alone is not enough" in prompt
    assert "near_duplicate" in prompt
    assert "kernel_fusion" in prompt
    assert "return check against every source card" in prompt
    assert "Proposal only" in prompt
    assert '"id": "c1"' in prompt
    assert '"id": "c4"' not in prompt
    assert "source-a" not in prompt


def test_guard_rejects_held_card() -> None:
    context = build_merge_suggestion_context(_payload(), allow_unreviewed_text=False)

    with pytest.raises(IRGenerationError) as captured:
        validate_merge_suggestion_semantics([_suggestion("g1", "c1", "c4")], context)

    assert captured.value.code == "merge_contains_held_card"


def test_guard_rejects_existing_merge_lineage() -> None:
    context = build_merge_suggestion_context(_payload(), allow_unreviewed_text=False)

    with pytest.raises(IRGenerationError) as captured:
        validate_merge_suggestion_semantics([_suggestion("g1", "c1", "c5")], context)

    assert captured.value.code == "merge_contains_lineage_card"


def test_guard_rejects_explicit_negation() -> None:
    context = build_merge_suggestion_context(_payload(), allow_unreviewed_text=False)

    with pytest.raises(IRGenerationError) as captured:
        validate_merge_suggestion_semantics([_suggestion("g1", "c2", "c3")], context)

    assert captured.value.code == "merge_claim_type_conflict"

    # claimTypeを同じにしても、明示的なnegate関係そのものがhard vetoになる。
    payload = _payload()
    cards = [
        card.model_copy(update={"claimType": "fact"}) if card.id == "c3" else card
        for card in payload.doc.cards
    ]
    context = build_merge_suggestion_context(
        payload.model_copy(update={"doc": payload.doc.model_copy(update={"cards": cards})}),
        allow_unreviewed_text=False,
    )
    with pytest.raises(IRGenerationError) as captured:
        validate_merge_suggestion_semantics([_suggestion("g1", "c2", "c3")], context)

    assert captured.value.code == "merge_negation_conflict"


def test_guard_rejects_contradiction_evidence() -> None:
    payload = _payload()
    cards = [
        card.model_copy(update={"claimType": "fact"}) if card.id == "c3" else card
        for card in payload.doc.cards
    ]
    context = build_merge_suggestion_context(
        payload.model_copy(update={"doc": payload.doc.model_copy(update={"cards": cards})}),
        allow_unreviewed_text=False,
    )

    with pytest.raises(IRGenerationError) as captured:
        validate_merge_suggestion_semantics([_suggestion("g1", "c1", "c3")], context)

    assert captured.value.code == "merge_contradiction_conflict"


def test_guard_rejects_different_known_claim_types() -> None:
    context = build_merge_suggestion_context(_payload(), allow_unreviewed_text=False)

    with pytest.raises(IRGenerationError) as captured:
        validate_merge_suggestion_semantics([_suggestion("g1", "c1", "c3")], context)

    assert captured.value.code == "merge_claim_type_conflict"


def test_guard_rejects_card_used_by_multiple_suggestions() -> None:
    context = build_merge_suggestion_context(_payload(), allow_unreviewed_text=False)

    with pytest.raises(IRGenerationError) as captured:
        validate_merge_suggestion_semantics(
            [
                _suggestion("g1", "c1", "c2"),
                _suggestion("g2", "c1", "c6"),
            ],
            context,
        )

    assert captured.value.code == "merge_candidate_overlap"


def test_context_fails_closed_when_generic_ir_is_truncated() -> None:
    cards = [
        Card(
            id=f"c{i:03d}",
            text=f"比較対象カード{i:03d}",
            x=float(i),
            y=0,
            textReviewed=True,
        )
        for i in range(201)
    ]
    payload = SuggestMergesRequest(
        doc=DocumentV1(
            version=1,
            id="merge-overflow",
            createdAt="2026-09-03T00:00:00Z",
            updatedAt="2026-09-03T00:00:00Z",
            transform=Transform(panX=0, panY=0, zoom=1),
            cards=cards,
        )
    )

    with pytest.raises(IRGenerationError) as captured:
        build_merge_suggestion_context(payload, allow_unreviewed_text=False)

    assert captured.value.code == "merge_context_truncated"


def test_context_ir_safemode_rejects_unreviewed_text() -> None:
    payload = _payload()
    cards = [
        card.model_copy(update={"textReviewed": False}) if card.id == "c1" else card
        for card in payload.doc.cards
    ]
    unreviewed = payload.model_copy(
        update={"doc": payload.doc.model_copy(update={"cards": cards})}
    )

    with pytest.raises(IRGenerationError) as captured:
        build_merge_suggestion_context(unreviewed, allow_unreviewed_text=False)

    assert captured.value.code == "unreviewed_text_not_allowed"
