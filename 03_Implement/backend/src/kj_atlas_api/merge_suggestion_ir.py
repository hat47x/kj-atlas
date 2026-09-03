"""`suggest-merges` に必要な意味を、共有LLM入力IRとroute固有文脈へ投影する。

カード統合では本文の近さだけでなく、認識上の位置づけ、島での扱われ方、論理関係、
根拠・矛盾、既存の表現系譜が「まとめてよいか」を左右する。一方、これらをすべて
共有IRの恒久スキーマへ追加すると、他のAI経路までmerge固有の意味へ結び付けてしまう。

そこで本モジュールは、共有IRを正規化・SafeMode・上限管理の基底として再利用し、
その外側に `suggest-merges` 専用の構造化文脈を重ねる。

- hold中、`mergedIntoCardId` を持つカード、`canonicalId` を持つcanonicalization元カードは
  候補集合から除外する。
- 候補カードは全件をroute-requiredとして保護し、件数・本文・relationが欠ける場合は
  不完全な集合で統合を提案せずfail-closedにする。
- `claimType`、全島所属、`canonicalId` / `repOf` / `sources` のmerge系譜を
  route固有文脈として渡す。
- `Card.sources` は外部出典ではなく、このカードへ統合された元カードIDであるため、
  `lineage.sourceCardIds` としてカードIDの対応を保つ。外部元記録を指す
  `Card.meta.source` はproviderへ送らない。
- 座標は統合可否には使わない。

SafeModeのroute側チェックは別に維持する。本モジュールのIR生成は第二の防御層であり、
既存guardを置き換えない。
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any

from kj_atlas_api.llm_input_ir import (
    IRGenerationError,
    RELATION_TYPES,
    SourceIsland,
    build_llm_input_ir,
    source_from_document,
)
from kj_atlas_api.models import SuggestMergesRequest


ROUTE_INPUT_VERSION = "suggest-merges-2"


@dataclass(frozen=True)
class MergeSuggestionIRContext:
    """providerへ渡す構造化入力と候補集合を保持する。"""

    document_ir: dict[str, Any]
    inputs: dict[str, Any]
    candidate_card_ids: frozenset[str]


def eligible_merge_card_ids(payload: SuggestMergesRequest) -> frozenset[str]:
    """人間の保留判断と既存merge/canonicalization結果を尊重した候補ID集合を返す。"""

    return frozenset(
        card.id
        for card in payload.doc.cards
        if card.holdState is None
        and not card.mergedIntoCardId
        and not card.canonicalId
    )


def _is_card_relation(relation: Any) -> bool:
    return (
        relation.from_kind in (None, "card")
        and relation.to_kind in (None, "card")
        and relation.type in RELATION_TYPES
    )


def _reduced_islands(source, candidate_ids: frozenset[str]) -> tuple[SourceIsland, ...]:
    """候補カードの所属だけを共有IRへ残し、島本文は送らない。"""

    islands: list[SourceIsland] = []
    for island in source.islands:
        members = tuple(card_id for card_id in island.card_ids if card_id in candidate_ids)
        if not members:
            continue
        islands.append(
            replace(
                island,
                card_ids=members,
                title=None,
                placard_card_id=None,
                parent_island_id=None,
                title_reviewed=None,
            )
        )
    return tuple(islands)


def _merge_context(payload: SuggestMergesRequest, candidate_ids: frozenset[str]) -> dict[str, Any]:
    island_ids_by_card: dict[str, list[str]] = {card_id: [] for card_id in candidate_ids}
    for island in payload.doc.islands:
        for card_id in island.cardIds:
            if card_id in island_ids_by_card:
                island_ids_by_card[card_id].append(island.id)

    cards = []
    for card in sorted(
        (item for item in payload.doc.cards if item.id in candidate_ids),
        key=lambda item: item.id,
    ):
        cards.append(
            {
                "id": card.id,
                "claimType": card.claimType,
                "holdState": card.holdState,
                "islandIds": sorted(set(island_ids_by_card[card.id])),
                "lineage": {
                    "mergedIntoCardId": card.mergedIntoCardId,
                    "canonicalId": card.canonicalId,
                    "repOf": sorted(set(card.repOf or [])),
                    "sourceCardIds": sorted(set(card.sources or [])),
                },
            }
        )
    return {"candidateCards": cards}


def build_merge_suggestion_ir_context(
    payload: SuggestMergesRequest,
    *,
    allow_unreviewed_text: bool,
) -> MergeSuggestionIRContext:
    """全候補について意味を欠落させない `suggest-merges` 入力を構築する。"""

    candidate_ids = eligible_merge_card_ids(payload)
    if len(candidate_ids) < 2:
        raise IRGenerationError(
            "insufficient_merge_candidates",
            "At least two eligible cards are required for merge suggestion generation.",
        )

    source = source_from_document(payload.doc)
    relevant_relations = tuple(
        relation
        for relation in source.relations
        if _is_card_relation(relation)
        and relation.from_id in candidate_ids
        and relation.to_id in candidate_ids
    )
    relevant_evidence = tuple(
        link
        for link in source.evidence_links
        if link.from_card_id in candidate_ids and link.to_card_id in candidate_ids
    )
    reduced_source = replace(
        source,
        cards=tuple(card for card in source.cards if card.id in candidate_ids),
        relations=relevant_relations,
        islands=_reduced_islands(source, candidate_ids),
        evidence_links=relevant_evidence,
    )

    document_ir = build_llm_input_ir(
        reduced_source,
        include_coordinates=False,
        safe_mode=True,
        allow_unreviewed_text=allow_unreviewed_text,
        required_card_ids=tuple(sorted(candidate_ids)),
    )

    truncation_reasons = set(document_ir.get("truncation", {}).get("reason_codes", []))
    if "MAX_TEXT_CHARS" in truncation_reasons:
        raise IRGenerationError(
            "required_text_truncated",
            "Merge-candidate card text exceeded the lossless IR text budget.",
        )

    projected_card_ids = {item["id"] for item in document_ir.get("cards", [])}
    if projected_card_ids != set(candidate_ids):
        raise IRGenerationError(
            "required_card_context_mismatch",
            "The complete merge-candidate set did not fit in the IR projection.",
        )

    expected_relation_keys = {
        (item.from_id, item.to_id, item.type) for item in relevant_relations
    }
    projected_relation_keys = {
        (item["from"], item["to"], item["type"])
        for item in document_ir.get("relations", [])
    }
    if not expected_relation_keys.issubset(projected_relation_keys):
        raise IRGenerationError(
            "required_relation_missing",
            "A relation between merge candidates did not fit in the IR projection.",
        )

    expected_evidence_keys = {
        (item.type, item.from_card_id, item.to_card_id) for item in relevant_evidence
    }
    projected_evidence_keys = {
        (item["type"], item["from_card_id"], item["to_card_id"])
        for item in document_ir.get("evidence_links", [])
    }
    if not expected_evidence_keys.issubset(projected_evidence_keys):
        raise IRGenerationError(
            "required_evidence_missing",
            "Evidence between merge candidates did not fit in the IR projection.",
        )

    merge_context = _merge_context(payload, candidate_ids)
    inputs: dict[str, Any] = {
        "routeInputVersion": ROUTE_INPUT_VERSION,
        "documentIR": document_ir,
        "mergeContext": merge_context,
    }
    return MergeSuggestionIRContext(
        document_ir=document_ir,
        inputs=inputs,
        candidate_card_ids=candidate_ids,
    )
