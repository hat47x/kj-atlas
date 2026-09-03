"""`suggest-island-summary` に必要な意味だけをLLM入力IRから取り出す。

対象島の表札候補を考える仕事では、直接メンバーの本文だけでなく、そのカードに直接
つながる論理関係や根拠も必要になる。一方、外部の隣接カードを新しい根拠カードとして
扱ったり、文書全体を無条件にプロンプトへ広げたりしてはならない。

このモジュールは次の境界を固定する。

- 対象島の直接メンバーは必ず投影に残す。
- 直接メンバーに接続するカード間の論理関係・Evidenceの両端も、文脈として投影に残す。
- 必要な論理関係やEvidenceが投影後に欠けた場合は、プロバイダーを呼ぶ前に停止できる。
- 外部の隣接カードは文脈専用であり、`groundingIds` の許可範囲を広げない。
- 座標はこの仕事では使わない。

SafeModeのroute側チェックは別に維持する。ここでのIR SafeModeは追加の防御層であり、
既存のroute guardを置き換えない。
"""

from __future__ import annotations

import json
from dataclasses import dataclass

from kj_atlas_api.llm_input_ir import (
    IRGenerationError,
    RELATION_TYPES,
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


def build_island_summary_ir_context(
    payload: SuggestIslandSummaryRequest,
    *,
    allow_unreviewed_text: bool,
) -> IslandSummaryIRContext:
    """対象島に直接関係する意味を保護してIRを構築する。

    `required_card_ids` で両端カードを保護しても、論理関係そのものは
    `MAX_RELATIONS` で切り詰められる可能性がある。そのため、構築後に対象島へ直接
    関係する論理関係とEvidenceがすべて残ったことを照合する。欠落時は入力内容を
    エラーへ反射せず、安定したcodeでfail-closedする。
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

    ir = build_llm_input_ir(
        source,
        include_coordinates=False,
        safe_mode=True,
        allow_unreviewed_text=allow_unreviewed_text,
        required_card_ids=tuple(sorted(required_ids)),
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

    projected_evidence_ids = {item["id"] for item in ir.get("evidence_links", [])}
    expected_evidence_ids = {item.id for item in relevant_evidence}
    if not expected_evidence_ids.issubset(projected_evidence_ids):
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
    lines: list[str] = []

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
