"""`suggest-merges` のためのroute固有入力契約と決定論的guard。

`AI-MERGE-SEMANTICS-01` と `ADR-0069 D5=A` に基づき、merge提案では
「似ている」ことより、統合しても意味を失わないことを優先する。

このモジュールはgeneric Document IRを土台にしつつ、generic IRがまだ持たない
`claimType`、merge系譜、sourceの差をroute固有の構造化入力へ補う。プロバイダーへ
Document生値を直接渡すための迂回路は作らない。
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from hashlib import sha256
from itertools import combinations
from typing import Any, Iterable

from kj_atlas_api.llm_input_ir import (
    IRGenerationError,
    build_llm_input_ir,
    source_from_document,
)
from kj_atlas_api.models import MergeSuggestion, SuggestMergesRequest


MERGE_CONTEXT_VERSION = "merge-suggestion-context.v1"


@dataclass(frozen=True)
class MergeSuggestionContext:
    """プロバイダーへ渡せるmerge候補と、後段guardに必要な構造を保持する。"""

    inputs: dict[str, Any]
    candidate_ids: frozenset[str]
    protected_ids: frozenset[str]
    hold_ids: frozenset[str]
    lineage_ids: frozenset[str]
    claim_types: dict[str, str | None]
    negate_pairs: frozenset[frozenset[str]]
    contradiction_pairs: frozenset[frozenset[str]]


def _source_ref_digest(values: list[str] | None) -> str | None:
    """source本文を送らず、source集合が同じかどうかだけ比較可能にする。"""

    if not values:
        return None
    canonical = json.dumps(sorted(set(values)), ensure_ascii=False, separators=(",", ":"))
    return sha256(canonical.encode("utf-8")).hexdigest()


def _has_merge_lineage(card: Any) -> bool:
    return bool(card.mergedIntoCardId or card.canonicalId or card.repOf)


def _pair(a: str, b: str) -> frozenset[str]:
    return frozenset((a, b))


def build_merge_suggestion_context(
    payload: SuggestMergesRequest,
    *,
    allow_unreviewed_text: bool,
) -> MergeSuggestionContext:
    """Document全体を意味欠落なく投影し、安全に比較できる候補だけを抽出する。

    現段階では、文書の一部だけを見てmerge候補を出す選択規則をまだ採択していない。
    そのためgeneric IRがcard/relation/text上限に達した場合は、見えていない差異を
    無視して統合を提案せずfail-closedにする。代表規模での候補選択は別途scale
    evidenceを得てから扱う。
    """

    ir = build_llm_input_ir(
        source_from_document(payload.doc),
        include_coordinates=False,
        safe_mode=True,
        allow_unreviewed_text=allow_unreviewed_text,
    )

    truncation = ir.get("truncation", {})
    if truncation.get("truncated"):
        raise IRGenerationError(
            "merge_context_truncated",
            "The merge-suggestion context did not fit in the deterministic projection.",
        )

    cards_by_id = {card.id: card for card in payload.doc.cards}
    ir_cards_by_id = {card["id"]: card for card in ir.get("cards", [])}
    if set(ir_cards_by_id) != set(cards_by_id):
        raise IRGenerationError(
            "merge_card_context_mismatch",
            "The merge-suggestion card context does not match the document.",
        )

    hold_ids = frozenset(
        card_id
        for card_id, item in ir_cards_by_id.items()
        if item.get("hold_state") is not None
    )
    lineage_ids = frozenset(
        card_id for card_id, card in cards_by_id.items() if _has_merge_lineage(card)
    )
    protected_ids = hold_ids | lineage_ids
    candidate_ids = frozenset(set(cards_by_id) - set(protected_ids))

    claim_types = {card_id: card.claimType for card_id, card in cards_by_id.items()}

    island_by_card: dict[str, str] = {}
    for island in ir.get("islands", []):
        for card_id in island.get("card_ids", []):
            island_by_card.setdefault(card_id, island["id"])

    negate_pairs = frozenset(
        _pair(item["from"], item["to"])
        for item in ir.get("relations", [])
        if item.get("type") == "negate"
    )
    contradiction_pairs = frozenset(
        _pair(item["from_card_id"], item["to_card_id"])
        for item in ir.get("evidence_links", [])
        if item.get("type") == "contradicts"
    )

    candidate_cards: list[dict[str, Any]] = []
    for card_id in sorted(candidate_ids):
        source_card = cards_by_id[card_id]
        ir_card = ir_cards_by_id[card_id]
        candidate_cards.append(
            {
                "id": card_id,
                "text": ir_card["text"],
                "claim_type": source_card.claimType,
                "island_id": island_by_card.get(card_id),
                "source_count": len(set(source_card.sources or [])),
                "source_ref_digest": _source_ref_digest(source_card.sources),
            }
        )

    candidate_relations = [
        item
        for item in ir.get("relations", [])
        if item["from"] in candidate_ids and item["to"] in candidate_ids
    ]
    candidate_evidence = [
        item
        for item in ir.get("evidence_links", [])
        if item["from_card_id"] in candidate_ids and item["to_card_id"] in candidate_ids
    ]

    inputs = {
        "contract": MERGE_CONTEXT_VERSION,
        "cards": candidate_cards,
        "relations": candidate_relations,
        "evidence_links": candidate_evidence,
        "constraints": {
            "proposal_only": True,
            "source_cards_are_retained": True,
            "candidate_ids": sorted(candidate_ids),
            "max_suggestions": 10,
            "min_cards_per_suggestion": 2,
        },
    }

    return MergeSuggestionContext(
        inputs=inputs,
        candidate_ids=candidate_ids,
        protected_ids=protected_ids,
        hold_ids=hold_ids,
        lineage_ids=lineage_ids,
        claim_types=claim_types,
        negate_pairs=negate_pairs,
        contradiction_pairs=contradiction_pairs,
    )


def merge_suggestion_prompt(context: MergeSuggestionContext, instruction: str | None) -> str:
    """route固有入力だけから、04ステップ／核融合法の意味保存promptを描画する。"""

    extra = instruction.strip() if instruction else "No extra instruction"
    card_lines = [
        "- " + json.dumps(item, ensure_ascii=False, sort_keys=True)
        for item in context.inputs["cards"]
    ]
    relation_lines = [
        "- " + json.dumps(item, ensure_ascii=False, sort_keys=True)
        for item in context.inputs["relations"]
    ] or ["- (none)"]
    evidence_lines = [
        "- " + json.dumps(item, ensure_ascii=False, sort_keys=True)
        for item in context.inputs["evidence_links"]
    ] or ["- (none)"]

    return "\n".join(
        [
            "You propose possible consolidations of KJ-method cards. Proposal only: never apply, delete, or overwrite source cards.",
            "Similarity or a shared topic alone is not enough to merge cards.",
            "Use near_duplicate when the cards express substantially the same appeal and every material condition can be preserved.",
            "Use kernel_fusion only when a shared meaning kernel can be stated while preserving each source card's material differences as residuals.",
            "Perform a return check against every source card before proposing: the draft must still be something each source card could say.",
            "Leave minority, lone, contradictory, held, lineage-protected, or materially different cards separate.",
            "Different known claim types must remain separate. A missing claim type is uncertainty, not proof of sameness.",
            "equivalence may support consolidation but never decides it by itself; related is weaker context only.",
            "Different source_ref_digest values mean the source sets differ. Preserve that distinction; do not invent source details.",
            "Return strict JSON only. No markdown or text outside JSON.",
            "Return at most 10 suggestions and never use one card in more than one suggestion.",
            "Use this schema:",
            '{"suggestions":[{"groupId":string,"cardIds":[string,...],"mergedTextDraft":string,"rationale":string?,"mergeMethod":"near_duplicate|kernel_fusion"?,"residuals":[string,...]?}]}',
            "Each suggestion must contain at least 2 unique cardIds chosen only from Candidate cards.",
            f"Instruction: {extra}",
            "Candidate cards:",
            *card_lines,
            "Relations among candidate cards:",
            *relation_lines,
            "Evidence among candidate cards:",
            *evidence_lines,
        ]
    )


def validate_merge_suggestion_semantics(
    suggestions: Iterable[MergeSuggestion],
    context: MergeSuggestionContext,
) -> None:
    """LLM出力が人間の保留・対立・認識位置・系譜を越えていないか検査する。"""

    used_card_ids: set[str] = set()

    for suggestion in suggestions:
        ids = list(suggestion.cardIds)
        selected = set(ids)

        if not selected <= context.candidate_ids:
            if selected & context.hold_ids:
                code = "merge_contains_held_card"
                message = "A merge suggestion included a card held by a human."
            elif selected & context.lineage_ids:
                code = "merge_contains_lineage_card"
                message = "A merge suggestion included a card already participating in merge lineage."
            else:
                code = "merge_contains_protected_card"
                message = "A merge suggestion included a card outside the allowed candidate set."
            raise IRGenerationError(code, message)

        overlap = used_card_ids & selected
        if overlap:
            raise IRGenerationError(
                "merge_candidate_overlap",
                "A card appeared in more than one merge suggestion.",
            )
        used_card_ids.update(selected)

        known_claim_types = {
            context.claim_types[card_id]
            for card_id in selected
            if context.claim_types.get(card_id) is not None
        }
        if len(known_claim_types) > 1:
            raise IRGenerationError(
                "merge_claim_type_conflict",
                "A merge suggestion crossed different known claim types.",
            )

        for a, b in combinations(sorted(selected), 2):
            pair = _pair(a, b)
            if pair in context.negate_pairs:
                raise IRGenerationError(
                    "merge_negation_conflict",
                    "A merge suggestion crossed an explicit negation relation.",
                )
            if pair in context.contradiction_pairs:
                raise IRGenerationError(
                    "merge_contradiction_conflict",
                    "A merge suggestion crossed contradiction evidence.",
                )
