"""反対視点・根拠不足の提案に必要な意味をLLM入力IRから取り出す。

`propose-opposing-viewpoint` の中心は、対象カードに対する別の見方や根拠不足を
人間の検討候補として示すことである。文書全体を同じ重要度で扱うより先に、対象カード
そのものと、そこへ直接つながる論理関係・根拠・矛盾を欠落させないことが必要になる。

このモジュールは次の境界を固定する。

- 対象カードは必ず投影に残す。
- 対象カードに直接接続するカード間relation / evidenceの両端も必須文脈として残す。
- `confirmed` / `held` などの `contradictionState` は、人間が既に行った判断として渡す。
- 必要なrelation / evidenceが投影上限で欠けた場合は、存在しないものとして扱わず
  providerを呼ぶ前にfail-closedにする。
- 直接接続していないカードは、IRに残った範囲で探索用の補助文脈として扱う。
- 座標はこの仕事では使わない。

SafeModeのroute側検査は別に維持する。IR側の検査は二つ目の防御層であり、既存guardを
置き換えない。
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from kj_atlas_api.llm_input_ir import (
    IRGenerationError,
    RELATION_TYPES,
    build_llm_input_ir,
    source_from_document,
)
from kj_atlas_api.models_ai import ProposeOpposingViewpointRequest


@dataclass(frozen=True)
class OpposingViewpointIRContext:
    """反対視点提案へ渡すIRと、対象周辺の必須文脈を分けて保持する。"""

    ir: dict[str, Any]
    target_card_id: str
    direct_context_card_ids: frozenset[str]


def _is_card_relation(relation: Any) -> bool:
    return (
        relation.from_kind in (None, "card")
        and relation.to_kind in (None, "card")
        and relation.type in RELATION_TYPES
    )


def build_opposing_viewpoint_ir_context(
    payload: ProposeOpposingViewpointRequest,
    *,
    allow_unreviewed_text: bool,
) -> OpposingViewpointIRContext:
    """対象カードと直接接続する意味を保護してIRを構築する。

    `required_card_ids` は必要カードをカード件数上限から守るが、relation自体は
    `MAX_RELATIONS` の切り詰め対象になり得る。そのため、構築後に対象カードへ直接関係
    するrelation / evidenceが残ったことまで照合する。
    """

    source = source_from_document(payload.doc)
    target_id = payload.targetCardId
    if target_id not in {card.id for card in source.cards}:
        raise IRGenerationError(
            "target_card_missing",
            "The target card is not present in the document.",
        )

    required_ids = {target_id}
    relevant_relations = []
    for relation in source.relations:
        if not _is_card_relation(relation):
            continue
        if relation.from_id == target_id or relation.to_id == target_id:
            relevant_relations.append(relation)
            required_ids.add(relation.from_id)
            required_ids.add(relation.to_id)

    relevant_evidence = []
    for link in source.evidence_links:
        if link.from_card_id == target_id or link.to_card_id == target_id:
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

    # 共有IRはMAX_TEXT_CHARS超過時に保持カードすべての本文を240文字へ短縮する。
    # 対象カードまたは直接文脈の意味を欠いた状態で反対視点を生成してはならないため、
    # required集合を含む投影で本文短縮が起きた場合はprovider前にfail-closedにする。
    truncation_reasons = set(ir.get("truncation", {}).get("reason_codes", []))
    if "MAX_TEXT_CHARS" in truncation_reasons:
        raise IRGenerationError(
            "required_text_truncated",
            "Task-required card text exceeded the lossless IR text budget.",
        )

    projected_card_ids = {item["id"] for item in ir.get("cards", [])}
    if not required_ids.issubset(projected_card_ids):
        raise IRGenerationError(
            "required_card_context_mismatch",
            "Task-required card context did not fit in the IR projection.",
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
            "Task-required logical relations did not fit in the IR projection.",
        )

    # Evidenceは共有IRで(type, from, to)を意味単位として重複排除する。
    # source側のIDが複数あっても、同じ意味のリンクが一つ残れば欠落とはみなさない。
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
            "Task-required evidence did not fit in the IR projection.",
        )

    return OpposingViewpointIRContext(
        ir=ir,
        target_card_id=target_id,
        direct_context_card_ids=frozenset(required_ids - {target_id}),
    )


def opposing_viewpoint_ir_prompt_lines(context: OpposingViewpointIRContext) -> list[str]:
    """対象カード周辺の必須意味と、補助探索カードをprompt向けに描画する。"""

    ir = context.ir
    target_id = context.target_card_id
    direct_ids = context.direct_context_card_ids
    cards_by_id = {item["id"]: item for item in ir.get("cards", [])}

    lines: list[str] = []

    lines.append(
        "Cards directly connected to the target by a recorded relation or evidence link "
        "(treat these as context, not as automatically true counterarguments):"
    )
    if direct_ids:
        for card_id in sorted(direct_ids):
            card = cards_by_id.get(card_id)
            if card is not None:
                lines.append(
                    f'- id="{card_id}", text={json.dumps(card["text"], ensure_ascii=False)}'
                )
    else:
        lines.append("- (none)")

    relation_lines = []
    for relation in ir.get("relations", []):
        if relation["from"] == target_id or relation["to"] == target_id:
            relation_lines.append(
                f'- card "{relation["from"]}" --{relation["type"]}--> '
                f'card "{relation["to"]}"'
            )
    lines.append("Logical relations involving the target card:")
    lines.extend(relation_lines or ["- (none)"])

    evidence_lines = []
    for link in ir.get("evidence_links", []):
        if link["from_card_id"] != target_id and link["to_card_id"] != target_id:
            continue
        state = link.get("contradiction_state")
        suffix = f" (contradictionState={state})" if state else ""
        evidence_lines.append(
            f'- card "{link["from_card_id"]}" --evidence:{link["type"]}--> '
            f'card "{link["to_card_id"]}"{suffix}'
        )
    lines.append(
        "Evidence involving the target card. A confirmed or held contradiction is an "
        "existing HUMAN judgement; use it as recorded context, never present it as a new AI discovery:"
    )
    lines.extend(evidence_lines or ["- (none)"])

    exploratory_ids = sorted(
        card_id
        for card_id in cards_by_id
        if card_id != target_id and card_id not in direct_ids
    )
    lines.append(
        "Other cards retained by the IR for exploratory counterexample search. Their mere "
        "presence is not evidence against the target:"
    )
    if exploratory_ids:
        for card_id in exploratory_ids:
            card = cards_by_id[card_id]
            lines.append(
                f'- id="{card_id}", text={json.dumps(card["text"], ensure_ascii=False)}'
            )
    else:
        lines.append("- (none)")

    truncation = ir.get("truncation")
    if isinstance(truncation, dict) and truncation.get("truncated") is True:
        reasons = ",".join(truncation.get("reason_codes", [])) or "unspecified"
        lines.append(
            "The broader exploratory context was truncated by the shared IR budget "
            f"({reasons}). The target and its directly connected required context were "
            "protected; do not treat omitted unrelated cards as evidence that no alternative exists."
        )

    return lines
