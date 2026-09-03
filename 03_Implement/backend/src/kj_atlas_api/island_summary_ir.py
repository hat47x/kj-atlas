"""`suggest-island-summary` に必要な意味だけをLLM入力IRから取り出す。

対象島の表札候補を考える仕事では、直接メンバーの本文だけでなく、そのカードに直接
つながる論理関係や根拠も必要になる。一方、外部の隣接カードを新しい根拠カードとして
扱ったり、文書全体を無条件にプロンプトへ広げたりしてはならない。

このモジュールは次の境界を固定する。

- 対象島の直接メンバーは必ず投影に残す。
- 直接メンバーに接続するカード間の論理関係・Evidenceの両端も、文脈として投影に残す。
- IRへ渡すsource自体を対象島とその直接隣接意味へ縮約し、無関係なカードを送らない。
- 必要なカード本文・論理関係・Evidenceが切り詰められる場合は、生成前に停止する。
- 外部の隣接カードは文脈専用であり、`groundingIds` の許可範囲を広げない。
- 座標はこの仕事では使わない。

SafeModeのroute側チェックは別に維持する。ここでのIR SafeModeは追加の防御層であり、
既存のroute guardを置き換えない。
"""

from __future__ import annotations

import json
from dataclasses import dataclass, replace

from kj_atlas_api.llm_input_ir import (
    IRGenerationError,
    RELATION_TYPES,
    SourceIsland,
    build_llm_input_ir,
    source_from_document,
)
from kj_atlas_api.models_ai import SuggestIslandSummaryRequest


@dataclass(frozen=True)
class IslandSummaryIRContext:
    """表札候補生成へ渡すIRと、grounding境界を分けて保持する。"""

    ir: dict
    target_island_id: str
    direct_member_ids: frozenset[str]
    context_only_card_ids: frozenset[str]


def _target_member_ids(payload: SuggestIslandSummaryRequest) -> frozenset[str]:
    target = next((item for item in payload.doc.islands if item.id == payload.islandId), None)
    if target is None:
        raise IRGenerationError("target_island_missing", "Target island is not present in the document")
    return frozenset(target.cardIds)


def _is_card_relation(relation) -> bool:
    return (
        relation.from_kind in (None, "card")
        and relation.to_kind in (None, "card")
        and relation.type in RELATION_TYPES
    )


def _relevant_islands(source, target_island_id: str) -> tuple[SourceIsland, ...]:
    """対象島と、その直上の親島だけを構造文脈として残す。

    親島はtargetの`parent_island_id`をIRで保持するために必要だが、その親島のカード群を
    表札候補の入力へ広げる必要はない。そのため親島はID・表札・親子関係だけを残し、
    `card_ids`と`placard_card_id`は空にして、first-match-winsの所属規則にも干渉させない。
    """

    islands_by_id = {island.id: island for island in source.islands}
    target = islands_by_id.get(target_island_id)
    if target is None:
        return ()

    islands: list[SourceIsland] = [target]
    parent_id = target.parent_island_id
    if parent_id is not None:
        parent = islands_by_id.get(parent_id)
        if parent is not None:
            islands.append(replace(parent, card_ids=(), placard_card_id=None))
    return tuple(islands)


def build_island_summary_ir_context(
    payload: SuggestIslandSummaryRequest,
    *,
    allow_unreviewed_text: bool,
) -> IslandSummaryIRContext:
    """対象島に直接関係する意味だけでIRを構築する。

    `required_card_ids`だけで必要カードを保護しても、共有IRは文書中の他カードを追加で
    選び得る。そこで先にsourceを、対象島の直接メンバー、そこへ直接つながるカード間の
    論理関係・Evidence、その両端カード、対象島と直上親島へ縮約する。

    表札候補ではカード本文の限定・留保・語感自体が意味になるため、共有IRの
    `MAX_TEXT_CHARS`処理でrequired card本文が240文字へ短縮された状態は利用しない。
    論理関係についても`MAX_RELATIONS`で欠落し得るため、構築後に必要意味がすべて
    残ったことを照合する。欠落時は入力内容をエラーへ反射せず、安定したcodeで
    fail-closedする。
    """

    source = source_from_document(payload.doc)
    direct_member_ids = _target_member_ids(payload)
    required_ids = set(direct_member_ids)

    relevant_relations = []
    for relation in source.relations:
        if not _is_card_relation(relation):
            continue
        if relation.from_id in direct_member_ids or relation.to_id in direct_member_ids:
            relevant_relations.append(relation)
            required_ids.add(relation.from_id)
            required_ids.add(relation.to_id)

    relevant_evidence = []
    for link in source.evidence_links:
        if link.from_card_id in direct_member_ids or link.to_card_id in direct_member_ids:
            relevant_evidence.append(link)
            required_ids.add(link.from_card_id)
            required_ids.add(link.to_card_id)

    reduced_source = replace(
        source,
        cards=tuple(card for card in source.cards if card.id in required_ids),
        relations=tuple(relevant_relations),
        islands=_relevant_islands(source, payload.islandId),
        evidence_links=tuple(relevant_evidence),
    )

    ir = build_llm_input_ir(
        reduced_source,
        include_coordinates=False,
        safe_mode=True,
        allow_unreviewed_text=allow_unreviewed_text,
        required_card_ids=tuple(sorted(required_ids)),
    )

    truncation_reasons = set(ir.get("truncation", {}).get("reason_codes", []))
    if "MAX_TEXT_CHARS" in truncation_reasons:
        raise IRGenerationError(
            "required_text_truncated",
            "Task-required card text exceeded the lossless IR text budget",
        )

    projected_card_ids = {item["id"] for item in ir.get("cards", [])}
    if projected_card_ids != required_ids:
        raise IRGenerationError(
            "required_card_context_mismatch",
            "Task-required card context did not fit in the IR projection",
        )

    projected_relation_keys = {
        (item["from"], item["to"], item["type"])
        for item in ir.get("relations", [])
    }
    expected_relation_keys = {
        (item.from_id, item.to_id, item.type)
        for item in relevant_relations
    }
    if not expected_relation_keys.issubset(projected_relation_keys):
        raise IRGenerationError(
            "required_relation_missing",
            "Task-required logical relations did not fit in the IR projection",
        )

    # Evidenceは共有IR側で(type, from, to)を正規化キーとして重複排除する。
    # ここでも同じ意味単位で比較し、重複したsource IDの存在を欠落と誤判定しない。
    projected_evidence_keys = {
        (item["type"], item["from_card_id"], item["to_card_id"])
        for item in ir.get("evidence_links", [])
    }
    expected_evidence_keys = {
        (item.type, item.from_card_id, item.to_card_id)
        for item in relevant_evidence
    }
    if not expected_evidence_keys.issubset(projected_evidence_keys):
        raise IRGenerationError(
            "required_evidence_missing",
            "Task-required evidence did not fit in the IR projection",
        )

    return IslandSummaryIRContext(
        ir=ir,
        target_island_id=payload.islandId,
        direct_member_ids=direct_member_ids,
        context_only_card_ids=frozenset(required_ids - set(direct_member_ids)),
    )


def island_summary_ir_prompt_lines(context: IslandSummaryIRContext) -> list[str]:
    """IRのうち対象島へ直接関係する構造だけを、人が読めるプロンプト文脈へ描画する。"""

    ir = context.ir
    direct_ids = context.direct_member_ids
    context_ids = context.context_only_card_ids
    lines: list[str] = [
        "The direct-member-only rule above still governs the placard itself and groundingIds.",
        "Use any adjacent cards below only to interpret recorded relations/evidence; do not introduce new facts from them into the placard.",
    ]

    target_structure = next(
        (item for item in ir.get("islands", []) if item.get("id") == context.target_island_id),
        None,
    )
    if target_structure is not None:
        lines.extend(
            [
                "Confirmed structure of the target island:",
                "- "
                + json.dumps(
                    {
                        "parentIslandId": target_structure.get("parent_island_id"),
                        "placardCardId": target_structure.get("placard_card_id"),
                        "reviewState": target_structure.get("review_state"),
                    },
                    ensure_ascii=False,
                    sort_keys=True,
                ),
            ]
        )

    cards_by_id = {item["id"]: item for item in ir.get("cards", [])}
    if context_ids:
        lines.append(
            "Adjacent cards used only as relation/evidence context; never use these IDs in groundingIds:"
        )
        for card_id in sorted(context_ids):
            card = cards_by_id.get(card_id)
            if card is not None:
                lines.append(f'- id="{card_id}", text={json.dumps(card["text"], ensure_ascii=False)}')

    relation_lines = []
    for relation in ir.get("relations", []):
        if relation["from"] in direct_ids or relation["to"] in direct_ids:
            relation_lines.append(
                f'- card "{relation["from"]}" --{relation["type"]}--> card "{relation["to"]}"'
            )
    lines.append("Logical relations involving direct member cards:")
    lines.extend(relation_lines or ["- (none)"])

    evidence_lines = []
    for link in ir.get("evidence_links", []):
        if link["from_card_id"] not in direct_ids and link["to_card_id"] not in direct_ids:
            continue
        state = link.get("contradiction_state")
        suffix = f" (contradictionState={state})" if state else ""
        evidence_lines.append(
            f'- card "{link["from_card_id"]}" --evidence:{link["type"]}--> '
            f'card "{link["to_card_id"]}"{suffix}'
        )
    lines.append("Evidence involving direct member cards:")
    lines.extend(evidence_lines or ["- (none)"])

    return lines
