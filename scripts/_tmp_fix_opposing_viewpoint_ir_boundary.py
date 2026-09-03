from pathlib import Path


def replace_once(path: Path, before: str, after: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(before)
    if count != 1:
        raise SystemExit(
            f"{path}: expected exactly one match, found {count}: {before[:120]!r}"
        )
    path.write_text(text.replace(before, after, 1), encoding="utf-8")


helper = Path("03_Implement/backend/src/kj_atlas_api/opposing_viewpoint_ir.py")
replace_once(
    helper,
    """    ir = build_llm_input_ir(\n        source,\n        include_coordinates=False,\n        safe_mode=True,\n        allow_unreviewed_text=allow_unreviewed_text,\n        required_card_ids=tuple(sorted(required_ids)),\n    )\n\n    projected_relation_keys = {\n""",
    """    ir = build_llm_input_ir(\n        source,\n        include_coordinates=False,\n        safe_mode=True,\n        allow_unreviewed_text=allow_unreviewed_text,\n        required_card_ids=tuple(sorted(required_ids)),\n    )\n\n    # 共有IRはMAX_TEXT_CHARS超過時に保持カードすべての本文を240文字へ短縮する。\n    # 対象カードまたは直接文脈の意味を欠いた状態で反対視点を生成してはならないため、\n    # required集合を含む投影で本文短縮が起きた場合はprovider前にfail-closedにする。\n    truncation_reasons = set(ir.get(\"truncation\", {}).get(\"reason_codes\", []))\n    if \"MAX_TEXT_CHARS\" in truncation_reasons:\n        raise IRGenerationError(\n            \"required_text_truncated\",\n            \"Task-required card text exceeded the lossless IR text budget.\",\n        )\n\n    projected_card_ids = {item[\"id\"] for item in ir.get(\"cards\", [])}\n    if not required_ids.issubset(projected_card_ids):\n        raise IRGenerationError(\n            \"required_card_context_mismatch\",\n            \"Task-required card context did not fit in the IR projection.\",\n        )\n\n    projected_relation_keys = {\n""",
)

route = Path("03_Implement/backend/src/kj_atlas_api/routes/ai.py")
replace_once(
    route,
    """    lines = [\n        \"You propose an OPPOSING viewpoint or an evidence-gap note for the target card.\",\n        \"Use only the provided cards, relations, and evidence. Do not add outside facts.\",\n        \"The proposal is a candidate for human review -- it is never applied automatically.\",\n        \"Ground every claim in the target and the recorded context. Distinguish an existing human judgement from a new AI proposal.\",\n        \"If the target's evidence is missing or weak, set evidenceGap=true; recorded contradictory evidence does not by itself decide the target's truth.\",\n        'Return strict JSON only: {\"opposingText\": string, \"evidenceGap\": boolean, \"rationale\": string, \"warnings\": [string,...]}',\n        f\"Target card: {json.dumps({'id': target.id, 'text': target.text})}\",\n    ]\n    if ir_context is not None:\n        lines.extend(opposing_viewpoint_ir_prompt_lines(ir_context))\n        return \"\\n\".join(lines)\n""",
    """    target_text = target.text\n    if ir_context is not None:\n        target_ir = next(\n            (item for item in ir_context.ir.get(\"cards\", []) if item[\"id\"] == target.id),\n            None,\n        )\n        if target_ir is None:\n            raise HTTPException(\n                status_code=422,\n                detail={\n                    \"code\": \"required_card_context_mismatch\",\n                    \"message\": \"Task-required card context did not fit in the IR projection\",\n                },\n            )\n        target_text = target_ir[\"text\"]\n\n    lines = [\n        \"You propose an OPPOSING viewpoint or an evidence-gap note for the target card.\",\n        \"Use only the provided cards, relations, and evidence. Do not add outside facts.\",\n        \"The proposal is a candidate for human review -- it is never applied automatically.\",\n        \"Ground every claim in the target and the recorded context. Distinguish an existing human judgement from a new AI proposal.\",\n        \"If the target's evidence is missing or weak, set evidenceGap=true; recorded contradictory evidence does not by itself decide the target's truth.\",\n        'Return strict JSON only: {\"opposingText\": string, \"evidenceGap\": boolean, \"rationale\": string, \"warnings\": [string,...]}',\n        f\"Target card: {json.dumps({'id': target.id, 'text': target_text})}\",\n    ]\n    if ir_context is not None:\n        lines.extend(opposing_viewpoint_ir_prompt_lines(ir_context))\n        return \"\\n\".join(lines)\n""",
)

helper_test = Path("03_Implement/backend/tests/test_ai_opposing_viewpoint_ir.py")
marker = "\ndef test_target_required_relation_overflow_fails_closed() -> None:\n"
new_test = '''\n\ndef test_required_target_text_truncation_fails_closed() -> None:\n    cards = [\n        Card(id=\"target\", text=\"中\" * 2000, x=0, y=0, textReviewed=True),\n        *[\n            Card(\n                id=f\"u{i}\",\n                text=\"周\" * 2000,\n                x=float(i + 1),\n                y=0,\n                textReviewed=True,\n            )\n            for i in range(6)\n        ],\n    ]\n    doc = DocumentV1(\n        version=1,\n        id=\"opposing-required-text-overflow\",\n        createdAt=_NOW,\n        updatedAt=_NOW,\n        transform=Transform(panX=0, panY=0, zoom=1),\n        cards=cards,\n        edges=[],\n        islands=[],\n        evidenceLinks=[],\n    )\n    payload = ProposeOpposingViewpointRequest(doc=doc, targetCardId=\"target\")\n\n    with pytest.raises(IRGenerationError) as captured:\n        build_opposing_viewpoint_ir_context(payload, allow_unreviewed_text=False)\n\n    assert captured.value.code == \"required_text_truncated\"\n'''
replace_once(helper_test, marker, new_test + marker)

route_test = Path("03_Implement/backend/tests/test_ai_oppose.py")
replace_once(
    route_test,
    "from __future__ import annotations\n\nfrom collections.abc import Iterator\n",
    "from __future__ import annotations\n\nimport json\nfrom collections.abc import Iterator\n",
)
replace_once(
    route_test,
    """    doc = _doc()\n    doc[\"evidenceLinks\"][0][\"contradictionState\"] = \"held\"\n    captured = {}\n""",
    """    doc = _doc()\n    raw_target_text = \"  待ち時間が長いと\\t利用者は離れる  \"\n    doc[\"cards\"][0][\"text\"] = raw_target_text\n    doc[\"evidenceLinks\"][0][\"contradictionState\"] = \"held\"\n    captured = {}\n""",
)
replace_once(
    route_test,
    """    assert request.inputs is not None\n    assert {card[\"id\"] for card in request.inputs[\"cards\"]} >= {\"c-claim\", \"c-counter\"}\n    assert \"contradictionState=held\" in request.prompt\n    assert \"existing HUMAN judgement\" in request.prompt\n    assert 'Target card: {\"id\": \"c-claim\"' in request.prompt\n""",
    """    assert request.inputs is not None\n    assert {card[\"id\"] for card in request.inputs[\"cards\"]} >= {\"c-claim\", \"c-counter\"}\n    target_ir_text = next(\n        card[\"text\"] for card in request.inputs[\"cards\"] if card[\"id\"] == \"c-claim\"\n    )\n    assert target_ir_text == raw_target_text.replace(\"\\t\", \"\")\n    assert target_ir_text != raw_target_text\n    assert (\n        \"Target card: \" + json.dumps({\"id\": \"c-claim\", \"text\": target_ir_text})\n        in request.prompt\n    )\n    assert json.dumps({\"id\": \"c-claim\", \"text\": raw_target_text}) not in request.prompt\n    assert \"contradictionState=held\" in request.prompt\n    assert \"existing HUMAN judgement\" in request.prompt\n""",
)

print("Opposing-viewpoint IR actual-input boundary patch applied.")
