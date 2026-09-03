"""表札候補生成で使う、対象島に限定したLLM入力IRの補助処理。

`AI-IR-STAGE5-SCOPE-01` では、`suggest-island-summary` をStage 5で最初に
IRへ移す経路としている。表札の戻し検査では対象島の直接メンバー全員へ戻れることが
前提になるため、単にカードIDがIRへ残るだけでは不十分である。本モジュールでは、
対象島の直接メンバーを必須カードとして投影し、その本文が一字も欠けずに保持された
ことまで確認する。

対象島の外側にある文脈は補助情報として扱う。カード間関係や根拠・矛盾リンクは、
対象島の直接メンバーに接続するものだけをプロンプト向けの文脈へ変換する。文書全体の
IRをそのまま描画して、表札候補の仕事を不必要に広げない。
"""

from __future__ import annotations

import json

from kj_atlas_api.llm_input_ir import (
    IRGenerationError,
    build_llm_input_ir,
    source_from_document,
)
from kj_atlas_api.models_ai import SuggestIslandSummaryRequest


def build_suggest_island_summary_ir(
    payload: SuggestIslandSummaryRequest,
    *,
    allow_unreviewed_text: bool,
) -> dict:
    """対象島の直接メンバーを欠落させずにLLM入力IRへ投影する。

    `required_card_ids` はカード件数による切り詰めから直接メンバーを保護するが、
    文字数上限による本文の短縮までは保証しない。そのためIR生成後に、対象島の各本文が
    元文書と完全一致することを確認する。一致しない場合は不完全な表札候補を生成せず、
    fail-closedで停止する。

    `ValueError` は既存ルートの入力エラー文言をそのまま維持するために使う。
    IR固有の拒否は `IRGenerationError` として呼出側へ返す。
    """
    cards_by_id = {card.id: card for card in payload.doc.cards}
    island = next((item for item in payload.doc.islands if item.id == payload.islandId), None)
    if island is None:
        raise ValueError("islandId does not exist")

    member_ids = tuple(card_id for card_id in island.cardIds if card_id in cards_by_id)
    if not member_ids:
        raise ValueError("island has no member cards")

    ir = build_llm_input_ir(
        source_from_document(payload.doc),
        include_coordinates=False,
        safe_mode=True,
        allow_unreviewed_text=allow_unreviewed_text,
        required_card_ids=member_ids,
    )

    projected_by_id = {card["id"]: card for card in ir.get("cards", [])}
    not_preserved = [
        card_id
        for card_id in member_ids
        if card_id not in projected_by_id
        or projected_by_id[card_id].get("text") != cards_by_id[card_id].text
    ]
    if not_preserved:
        raise IRGenerationError(
            "required_island_member_text_not_preserved",
            "Target island member text could not be preserved completely within the LLM input budget.",
        )

    return ir


def island_summary_context_lines(
    payload: SuggestIslandSummaryRequest,
    ir: dict,
) -> list[str]:
    """対象島の表札判断に必要なIR文脈だけを、プロンプト向けに描画する。

    直接メンバー本文は既存の `Member cards:` 節で扱うため、ここでは重複させない。
    島の確定構造、直接メンバーに接続するカード間関係、根拠・矛盾リンクだけを描く。
    外側の文脈がIR上限で欠けた場合は、その欠落を「関係が存在しない」と誤解しない
    よう注意書きを加える。
    """
    target_island = next(
        (item for item in ir.get("islands", []) if item["id"] == payload.islandId),
        None,
    )
    if target_island is None:
        raise IRGenerationError(
            "target_island_not_projected",
            "The target island could not be preserved in the LLM input IR.",
        )

    member_ids = set(target_island.get("card_ids", []))
    lines = [
        "Target island structure confirmed in the canvas:",
        (
            f'- id="{target_island["id"]}", '
            f'title={json.dumps(target_island.get("title") or "")}, '
            f'parentIslandId={json.dumps(target_island.get("parent_island_id"))}, '
            f'placardCardId={json.dumps(target_island.get("placard_card_id"))}, '
            f'reviewState="{target_island.get("review_state", "unreviewed")}"'
        ),
    ]

    relations = [
        relation
        for relation in ir.get("relations", [])
        if relation["from"] in member_ids or relation["to"] in member_ids
    ]
    lines.append(
        "Card relations touching a direct member (use them as logical context, not as new facts):"
    )
    if relations:
        for relation in relations:
            lines.append(
                f'- {relation["type"]}: {relation["from"]} -> {relation["to"]}'
            )
    else:
        lines.append("- (none)")

    evidence_links = [
        link
        for link in ir.get("evidence_links", [])
        if link["from_card_id"] in member_ids or link["to_card_id"] in member_ids
    ]
    lines.append(
        "Evidence and contradiction records touching a direct member. "
        "A confirmed or held contradiction is an existing human judgement, not a new discovery:"
    )
    if evidence_links:
        for link in evidence_links:
            state = link.get("contradiction_state") or "n/a"
            reviewed = link.get("contradiction_state_reviewed")
            reviewed_note = ", humanReviewed=true" if reviewed is True else ""
            lines.append(
                f'- {link["type"]}: {link["from_card_id"]} -> {link["to_card_id"]} '
                f'(contradictionState={state}{reviewed_note})'
            )
    else:
        lines.append("- (none)")

    if ir.get("truncation", {}).get("truncated"):
        reasons = ",".join(ir["truncation"].get("reason_codes", [])) or "unspecified"
        lines.append(
            "Context outside the target island may be incomplete because the IR projection "
            f"hit its size limit ({reasons}). Do not interpret an omitted outside relation "
            "as evidence that no such relation exists."
        )

    return lines
