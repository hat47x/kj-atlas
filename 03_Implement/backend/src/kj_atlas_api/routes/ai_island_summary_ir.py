from __future__ import annotations

import json
from typing import Any

from fastapi import HTTPException

from kj_atlas_api.llm_input_ir import (
    IRGenerationError,
    build_llm_input_ir,
    derived_island_relations,
    source_from_document,
)
from kj_atlas_api.models_ai import SuggestIslandSummaryRequest


def build_suggest_island_summary_ir(payload: SuggestIslandSummaryRequest) -> dict[str, Any]:
    """表札候補の生成に使う入力IRを構築する。

    表札の戻し検査では、対象島の直接メンバーを一枚でも欠くと島全体の「志」を
    確かめにくくなる。そのため、対象島の ``cardIds`` はルート固有の必須カード
    として、通常の上限処理より先に予約する。

    一つの島だけでIRのカード数・文字数予算を超える場合は、一部を黙って落として
    表札を生成せず、既存IRの ``required_card_budget_exceeded`` として失敗させる。
    SafeModeは呼出側の一次検査に加えてIR側でも維持し、二重の防御を崩さない。
    """
    island = next((item for item in payload.doc.islands if item.id == payload.islandId), None)
    if island is None:
        raise HTTPException(status_code=422, detail="islandId does not exist")

    try:
        return build_llm_input_ir(
            source_from_document(payload.doc),
            include_coordinates=False,
            safe_mode=True,
            allow_unreviewed_text=bool(payload.allowUnreviewedText),
            required_card_ids=tuple(island.cardIds),
        )
    except IRGenerationError as exc:
        raise HTTPException(status_code=422, detail=exc.to_contract()) from exc


def render_suggest_island_summary_ir_context(
    payload: SuggestIslandSummaryRequest,
    ir: dict[str, Any],
) -> str:
    """対象島の表札判断に必要なIR部分だけを、promptへ描画できる文字列にする。

    IR全体をそのまま重ねるのではなく、対象島の確定構造、対象メンバーに接続する
    カード関係と根拠リンク、カード関係から導出した島間関係だけを示す。既存promptが
    Documentから直接描画しているメンバーカード本文、利用者の違和感、明示的な
    island-to-island edgeはこの関数では重複させない。
    """
    direct_member_ids = set(
        next(
            (item.cardIds for item in payload.doc.islands if item.id == payload.islandId),
            [],
        )
    )

    target_island = next(
        (item for item in ir.get("islands", []) if item.get("id") == payload.islandId),
        None,
    )
    relations = [
        relation
        for relation in ir.get("relations", [])
        if relation.get("from") in direct_member_ids or relation.get("to") in direct_member_ids
    ]
    evidence_links = [
        link
        for link in ir.get("evidence_links", [])
        if link.get("from_card_id") in direct_member_ids
        or link.get("to_card_id") in direct_member_ids
    ]
    derived_relations = [
        relation
        for relation in derived_island_relations(ir)
        if relation.get("from_id") == payload.islandId
        or relation.get("to_id") == payload.islandId
    ]

    lines = [
        "Meaning-preservation context from the normalized input IR:",
        "- This context records human-authored structure and evidence state; do not reinterpret review state as AI approval.",
    ]
    if target_island is not None:
        lines.append(
            "- target island structure: "
            + json.dumps(target_island, ensure_ascii=False, sort_keys=True)
        )
    if relations:
        lines.append(
            "- typed card relations touching direct members: "
            + json.dumps(relations, ensure_ascii=False, sort_keys=True)
        )
    if evidence_links:
        lines.append(
            "- evidence links touching direct members (including human contradiction state): "
            + json.dumps(evidence_links, ensure_ascii=False, sort_keys=True)
        )
    if derived_relations:
        lines.append(
            "- island relations derived from card relations: "
            + json.dumps(derived_relations, ensure_ascii=False, sort_keys=True)
        )

    truncation = ir.get("truncation")
    if isinstance(truncation, dict) and truncation.get("truncated") is True:
        lines.append(
            "- surrounding IR context was truncated by the shared budget; direct members of the target island were reserved before truncation."
        )

    return "\n".join(lines)
