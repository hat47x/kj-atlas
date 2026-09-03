from pathlib import Path
import re

AI = Path("03_Implement/backend/src/kj_atlas_api/routes/ai.py")
text = AI.read_text(encoding="utf-8")

import_anchor = '''from kj_atlas_api.opposing_viewpoint_ir import (
    OpposingViewpointIRContext,
    build_opposing_viewpoint_ir_context,
    opposing_viewpoint_ir_prompt_lines,
)
'''
import_replacement = import_anchor + '''from kj_atlas_api.merge_suggestion_ir import (
    MergeSuggestionIRContext,
    build_merge_suggestion_ir_context,
)
'''
if text.count(import_anchor) != 1:
    raise SystemExit(f"import anchor count={text.count(import_anchor)}")
text = text.replace(import_anchor, import_replacement, 1)

new_prompt = r'''def _build_merge_prompt(
    payload: SuggestMergesRequest,
    ir_context: MergeSuggestionIRContext | None = None,
) -> str:
    """意味保存型の統合候補promptを、productionではroute固有入力から描画する。

    ``ir_context=None`` は既存の単体テスト・補助呼出しとの互換経路である。
    production routeは常に ``MergeSuggestionIRContext`` を渡し、候補本文・構造・
    route固有metadataを ``LLMRequest.inputs`` と同じ入力から描画する。
    """
    context_lines: list[str] = []
    if ir_context is None:
        card_lines = [
            f'- id="{card.id}", text={json.dumps(card.text)}'
            for card in _eligible_merge_cards(payload)
        ]
    else:
        ir = ir_context.document_ir
        card_lines = [
            f'- id="{card["id"]}", text={json.dumps(card["text"], ensure_ascii=False)}'
            for card in ir.get("cards", [])
            if card["id"] in ir_context.candidate_card_ids
        ]

        context_lines.extend(
            [
                "Merge-specific candidate context (recorded structure, not permission to merge):",
                *[
                    "- " + json.dumps(item, ensure_ascii=False, sort_keys=True)
                    for item in ir_context.inputs["mergeContext"]["candidateCards"]
                ],
                "sourceRefs are opaque document-local equality markers only. Same ref means the recorded source string was the same; infer no person, URL, authority, truth, or content from the token itself.",
                "islandIds are context only. Different islands do not automatically forbid a merge, and the same island does not automatically permit one.",
                "lineage is recorded context. Never invent canonicalId, repOf, or merge ancestry.",
                "Logical relations between eligible candidates:",
                *(
                    [
                        f'- card "{item["from"]}" --{item["type"]}--> card "{item["to"]}"'
                        for item in ir.get("relations", [])
                    ]
                    or ["- (none)"]
                ),
                "Evidence between eligible candidates:",
                *(
                    [
                        f'- card "{item["from_card_id"]}" --evidence:{item["type"]}--> '
                        f'card "{item["to_card_id"]}"'
                        + (
                            f' (contradictionState={item["contradiction_state"]})'
                            if item.get("contradiction_state")
                            else ""
                        )
                        for item in ir.get("evidence_links", [])
                    ]
                    or ["- (none)"]
                ),
            ]
        )

    instruction = payload.instruction.strip() if payload.instruction else "No extra instruction"

    return "\n".join(
        [
            "You propose KJ-compatible card integrations. This is advisory only.",
            "Use one of two approaches when appropriate:",
            "- 04-step-like consolidation for near-duplicate cards whose material distinctions can all be retained.",
            "- kernel-fusion-style integration when several non-identical cards share a meaning kernel that can be stated without erasing their residual differences.",
            "Similarity alone is not enough. Sharing a topic or vocabulary is not enough.",
            "Before proposing, perform a Return check against every source card: would each source still recognise the draft as preserving what it says?",
            "Leave minority, lone, contradictory, held, or materially different cards separate.",
            "Do not invent provenance, conditions, certainty, or residual meaning that is not in the source cards.",
            "You must only propose suggestions. Do not apply merges, delete cards, or overwrite source cards.",
            "Return strict JSON only. No markdown. No explanation text outside JSON.",
            "Return at most 10 suggestions.",
            "Use this exact schema:",
            '{"suggestions":[{"groupId":string,"cardIds":[string,...],"mergedTextDraft":string,"rationale":string?}]}',
            "Each suggestion must include at least 2 cardIds.",
            "Only use card IDs from the input.",
            f"Instruction: {instruction}",
            "Cards eligible for integration consideration:",
            *(card_lines or ["- (none)"]),
            *context_lines,
        ]
    )'''
pattern = r"def _build_merge_prompt\(payload: SuggestMergesRequest\) -> str:\n.*?\n\n\ndef _validate_merge_suggestion_semantics"
replacement = new_prompt + "\n\n\ndef _validate_merge_suggestion_semantics"
text, count = re.subn(pattern, lambda _: replacement, text, count=1, flags=re.S)
if count != 1:
    raise SystemExit(f"prompt replacement count={count}")

old_parser_head = '''def _parse_merge_suggestions(
    raw_text: str, source_doc: SuggestMergesRequest
) -> list[MergeSuggestion]:
'''
new_parser_head = '''def _parse_merge_suggestions(
    raw_text: str,
    source_doc: SuggestMergesRequest,
    *,
    allowed_card_ids: set[str] | frozenset[str] | None = None,
) -> list[MergeSuggestion]:
'''
if text.count(old_parser_head) != 1:
    raise SystemExit(f"parser head count={text.count(old_parser_head)}")
text = text.replace(old_parser_head, new_parser_head, 1)

old_known = '    known_card_ids = {card.id for card in source_doc.doc.cards}\n'
new_known = '''    known_card_ids = (
        set(allowed_card_ids)
        if allowed_card_ids is not None
        else {card.id for card in source_doc.doc.cards}
    )
'''
# There are other known_card_ids assignments in this module; replace only the one
# after the merge response size check.
merge_parser_pos = text.index("def _parse_merge_suggestions(")
known_pos = text.index(old_known, merge_parser_pos)
text = text[:known_pos] + new_known + text[known_pos + len(old_known):]

route_pattern = r'''@router\.post\(
    "/suggest-merges",
    response_model=SuggestMergesResponse,
    dependencies=\[Depends\(require_tenant_scoped_api_precondition\)\],
\)
def suggest_merges\(payload: SuggestMergesRequest, request: Request, db: Session = Depends\(get_db\)\) -> SuggestMergesResponse:
.*?
    return SuggestMergesResponse\(suggestions=suggestions\)
'''
new_route = r'''@router.post(
    "/suggest-merges",
    response_model=SuggestMergesResponse,
    dependencies=[Depends(require_tenant_scoped_api_precondition)],
)
def suggest_merges(payload: SuggestMergesRequest, request: Request, db: Session = Depends(get_db)) -> SuggestMergesResponse:
    # SEC-AI-SAFEMODE-01/02: route側guardを一次防御として維持する。
    _reject_unreviewed_text(payload.doc, payload.allowUnreviewedText)

    # 候補が1枚以下なら統合という仕事自体が成立しない。providerへ不要な本文を送らない。
    if len(_eligible_merge_cards(payload)) < 2:
        return SuggestMergesResponse(suggestions=[])

    allow_unreviewed = bool(
        payload.allowUnreviewedText is True and settings.allow_unreviewed_ai_text
    )
    try:
        ir_context = build_merge_suggestion_ir_context(
            payload,
            allow_unreviewed_text=allow_unreviewed,
        )
    except IRGenerationError as exc:
        raise HTTPException(status_code=422, detail=exc.to_contract()) from exc

    try:
        llm_response = generate_with_fallback(
            LLMRequest(
                task="suggest_merges",
                prompt=_build_merge_prompt(payload, ir_context),
                inputs=ir_context.inputs,
            )
        )
    except ProviderDisabledError as exc:
        _raise_llm_http_error(exc)
    except ProviderRequestError as exc:
        _raise_llm_http_error(exc)

    _audit_llm_trace(request, _resolve_audit_tenant(request, db), payload.doc.id, "suggest_merges", llm_response)

    suggestions = _parse_merge_suggestions(
        llm_response.raw_text,
        payload,
        allowed_card_ids=ir_context.candidate_card_ids,
    )
    return SuggestMergesResponse(suggestions=suggestions)
'''
text, count = re.subn(route_pattern, lambda _: new_route, text, count=1, flags=re.S)
if count != 1:
    raise SystemExit(f"route replacement count={count}")

AI.write_text(text, encoding="utf-8")
print("suggest-merges route IR wiring applied")
