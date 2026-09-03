from pathlib import Path


ai_path = Path("03_Implement/backend/src/kj_atlas_api/routes/ai.py")
text = ai_path.read_text(encoding="utf-8")

import_before = """from kj_atlas_api.island_summary_ir import (
    build_island_summary_ir_context,
    island_summary_ir_prompt_lines,
)
"""
import_after = import_before + """from kj_atlas_api.opposing_viewpoint_ir import (
    OpposingViewpointIRContext,
    build_opposing_viewpoint_ir_context,
    opposing_viewpoint_ir_prompt_lines,
)
"""
if text.count(import_before) != 1:
    raise SystemExit("opposing IR import insertion point was not unique")
text = text.replace(import_before, import_after, 1)

start = text.index("def _build_opposing_viewpoint_prompt(")
end = text.index('\n\n@router.post(\n    "/proposals/opposing-viewpoint"', start)
new_function = '''def _build_opposing_viewpoint_prompt(
    payload: ProposeOpposingViewpointRequest,
    ir_context: OpposingViewpointIRContext | None = None,
) -> str:
    """対象カードに接地したproposal-onlyの反対視点promptを組み立てる。

    ``ir_context=None`` は既存の単体テスト・補助呼出しとの互換経路であり、
    production routeは常にroute固有IRを渡す。``Target card:`` の行形式は
    DOGFOOD-17のmock/E2E接地契約なので変更しない。
    """
    target = next((card for card in payload.doc.cards if card.id == payload.targetCardId), None)
    if target is None:
        raise HTTPException(status_code=422, detail="targetCardId does not exist")

    lines = [
        "You propose an OPPOSING viewpoint or an evidence-gap note for the target card.",
        "Use only the provided cards, relations, and evidence. Do not add outside facts.",
        "The proposal is a candidate for human review -- it is never applied automatically.",
        "Ground every claim in the target and the recorded context. Distinguish an existing human judgement from a new AI proposal.",
        "If the target's evidence is missing or weak, set evidenceGap=true; recorded contradictory evidence does not by itself decide the target's truth.",
        'Return strict JSON only: {"opposingText": string, "evidenceGap": boolean, "rationale": string, "warnings": [string,...]}',
        f"Target card: {json.dumps({'id': target.id, 'text': target.text})}",
    ]
    if ir_context is not None:
        lines.extend(opposing_viewpoint_ir_prompt_lines(ir_context))
        return "\\n".join(lines)

    # 互換経路: IR文脈を明示しない補助呼出しでは従来の全文書入力を維持する。
    card_lines = "\\n".join(
        f'  - id="{card.id}", text={json.dumps(card.text)}'
        for card in payload.doc.cards
    )
    evidence_lines = "\\n".join(
        f'  - source "{link.fromCardId}" --{link.type}--> target "{link.toCardId}"'
        for link in payload.doc.evidenceLinks or []
    ) or "- (none)"
    lines.extend(["Cards:", card_lines, "Evidence links:", evidence_lines])
    return "\\n".join(lines)'''
text = text[:start] + new_function + text[end:]

route_before = '''    _reject_unreviewed_text(payload.doc, payload.allowUnreviewedText)
    model_id = payload.model or resolve_model_for_task("propose_opposing_viewpoint")
'''
route_after = '''    # SEC-AI-SAFEMODE-01/02: 既存route guardを一次防御として維持する。
    _reject_unreviewed_text(payload.doc, payload.allowUnreviewedText)
    allow_unreviewed = bool(
        payload.allowUnreviewedText is True and settings.allow_unreviewed_ai_text
    )
    try:
        ir_context = build_opposing_viewpoint_ir_context(
            payload, allow_unreviewed_text=allow_unreviewed
        )
    except IRGenerationError as exc:
        raise HTTPException(status_code=422, detail=exc.to_contract()) from exc
    prompt = _build_opposing_viewpoint_prompt(payload, ir_context)
    model_id = payload.model or resolve_model_for_task("propose_opposing_viewpoint")
'''
if text.count(route_before) != 1:
    raise SystemExit("opposing route SafeMode insertion point was not unique")
text = text.replace(route_before, route_after, 1)

request_before = '''                task="propose_opposing_viewpoint",
                prompt=_build_opposing_viewpoint_prompt(payload),
                model=model_id,
'''
request_after = '''                task="propose_opposing_viewpoint",
                prompt=prompt,
                inputs=ir_context.ir,
                model=model_id,
'''
if text.count(request_before) != 1:
    raise SystemExit("opposing LLMRequest insertion point was not unique")
text = text.replace(request_before, request_after, 1)
ai_path.write_text(text, encoding="utf-8")

coverage_path = Path("03_Implement/backend/tests/test_ai_llm_input_ir_coverage.py")
coverage = coverage_path.read_text(encoding="utf-8")
migrated_before = '''        "re_layout",
        "suggest_card_groups",
        "suggest_island_summary",
'''
migrated_after = '''        "propose_opposing_viewpoint",
        "re_layout",
        "suggest_card_groups",
        "suggest_island_summary",
'''
if coverage.count(migrated_before) != 1:
    raise SystemExit("IR_MIGRATED_TASKS insertion point was not unique")
coverage = coverage.replace(migrated_before, migrated_after, 1)
debt_before = '''        "check_narrative",
        "propose_opposing_viewpoint",
        "refine_card_text",
'''
debt_after = '''        "check_narrative",
        "refine_card_text",
'''
if coverage.count(debt_before) != 1:
    raise SystemExit("Stage 5 debt removal point was not unique")
coverage_path.write_text(coverage.replace(debt_before, debt_after, 1), encoding="utf-8")

oppose_test = Path("03_Implement/backend/tests/test_ai_oppose.py")
oppose_text = oppose_test.read_text(encoding="utf-8")
marker = "\ndef test_propose_opposing_viewpoint_rejects_unreviewed"
if oppose_text.count(marker) != 1:
    raise SystemExit("test_ai_oppose integration insertion point was not unique")
integration = r'''


def test_route_sends_target_ir_and_human_contradiction_state(tmp_path, monkeypatch) -> None:
    """production routeが対象周辺IRをpromptとLLMRequest.inputsの両方へ渡す。"""
    monkeypatch.setattr(settings, "api_key", None)
    doc = _doc()
    doc["evidenceLinks"][0]["contradictionState"] = "held"
    captured = {}

    from kj_atlas_api.llm.provider import _new_metadata

    def _fake_generate(req):
        captured["request"] = req
        return LLMResponse(
            raw_text='{"opposingText":"対象主張への別視点です。","evidenceGap":false,"rationale":"記録済み構造を参照。","warnings":[]}',
            metadata=_new_metadata(
                provider_kind="local",
                provider_name="local",
                model_id="default",
                transport="none",
            ),
        )

    monkeypatch.setattr(ai, "generate_with_fallback", _fake_generate)
    with _client(tmp_path) as client:
        _put_doc(client, doc)
        resp = client.post(
            "/ai/proposals/opposing-viewpoint",
            json={"doc": doc, "targetCardId": "c-claim"},
        )

    assert resp.status_code == 200, resp.text
    request = captured["request"]
    assert request.inputs is not None
    assert {card["id"] for card in request.inputs["cards"]} >= {"c-claim", "c-counter"}
    assert "contradictionState=held" in request.prompt
    assert "existing HUMAN judgement" in request.prompt
    assert 'Target card: {"id": "c-claim"' in request.prompt
'''
oppose_test.write_text(oppose_text.replace(marker, integration + marker, 1), encoding="utf-8")
