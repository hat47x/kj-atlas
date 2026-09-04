from pathlib import Path
import re

AI = Path("03_Implement/backend/src/kj_atlas_api/routes/ai.py")
COVERAGE = Path("03_Implement/backend/tests/test_ai_llm_input_ir_coverage.py")

text = AI.read_text(encoding="utf-8")

import_needle = "from kj_atlas_api.llm_input_ir import ("
if import_needle not in text:
    raise SystemExit("llm_input_ir import anchor missing")
merge_import = (
    "from kj_atlas_api.merge_ir import (\n"
    "    MergeIRContext,\n"
    "    build_merge_ir_context,\n"
    "    merge_ir_prompt_lines,\n"
    ")\n"
)
if merge_import not in text:
    text = text.replace(import_needle, merge_import + import_needle, 1)

new_prompt = r'''def _build_merge_prompt(
    payload: SuggestMergesRequest,
    ir_context: MergeIRContext | None = None,
) -> str:
    instruction = payload.instruction.strip() if payload.instruction else "No extra instruction"
    if ir_context is None:
        context_lines = [
            "Cards eligible for integration consideration:",
            *(
                [
                    f'- id="{card.id}", text={json.dumps(card.text)}'
                    for card in _eligible_merge_cards(payload)
                ]
                or ["- (none)"]
            ),
        ]
    else:
        context_lines = merge_ir_prompt_lines(ir_context)

    return "\n".join(
        [
            "You propose KJ-compatible card integrations. This is advisory only.",
            "Use one of two approaches when appropriate:",
            "- 04-step-like consolidation for near-duplicate cards whose material distinctions can all be retained.",
            "- kernel-fusion-style integration when several non-identical cards share a meaning kernel that can be stated without erasing their residual differences.",
            "Similarity alone is not enough. Sharing a topic, vocabulary, island, or source is not enough.",
            "Before proposing, perform a Return check against every source card: would each source still recognise the draft as preserving what it says?",
            "Do not merge cards with different non-null claimType values.",
            "Do not merge cards joined by a negate relation or a contradicts evidence link.",
            "Use islandIds and sourceRefs only as context. Their sameness or difference never decides a merge by itself.",
            "Leave minority, lone, contradictory, held, or materially different cards separate.",
            "Do not invent provenance, conditions, certainty, or residual meaning that is not in the source cards.",
            "You must only propose suggestions. Do not apply merges, delete cards, or overwrite source cards.",
            "Return strict JSON only. No markdown. No explanation text outside JSON.",
            "Return at most 10 suggestions.",
            "Use this exact schema:",
            '{"suggestions":[{"groupId":string,"cardIds":[string,...],"mergedTextDraft":string,"rationale":string?}]}',
            "Each suggestion must include at least 2 cardIds.",
            "Only use card IDs from the candidate input.",
            f"Instruction: {instruction}",
            *context_lines,
        ]
    )'''

pattern = r"def _build_merge_prompt\(payload: SuggestMergesRequest\) -> str:\n.*?\n\n\ndef _validate_merge_suggestion_semantics"
replacement = new_prompt + "\n\n\ndef _validate_merge_suggestion_semantics"
text, count = re.subn(pattern, lambda _: replacement, text, count=1, flags=re.S)
if count != 1:
    raise SystemExit(f"merge prompt replacement count={count}")

old_route = r'''def suggest_merges(payload: SuggestMergesRequest, request: Request, db: Session = Depends(get_db)) -> SuggestMergesResponse:
    _reject_unreviewed_text(payload.doc, payload.allowUnreviewedText)
    try:
        llm_response = generate_with_fallback(
            LLMRequest(
                task="suggest_merges",
                prompt=_build_merge_prompt(payload),
            )
        )
    except ProviderDisabledError as exc:
        _raise_llm_http_error(exc)
    except ProviderRequestError as exc:
        _raise_llm_http_error(exc)

    _audit_llm_trace(request, _resolve_audit_tenant(request, db), payload.doc.id, "suggest_merges", llm_response)

    suggestions = _parse_merge_suggestions(llm_response.raw_text, payload)
    return SuggestMergesResponse(suggestions=suggestions)'''

new_route = r'''def suggest_merges(payload: SuggestMergesRequest, request: Request, db: Session = Depends(get_db)) -> SuggestMergesResponse:
    # SafeMode layer 1 remains the route guard. The route-specific IR repeats
    # the check independently for the provider-bound candidate window.
    _reject_unreviewed_text(payload.doc, payload.allowUnreviewedText)
    if len(_eligible_merge_cards(payload)) < 2:
        return SuggestMergesResponse(suggestions=[])

    allow_unreviewed = bool(
        payload.allowUnreviewedText is True and settings.allow_unreviewed_ai_text
    )
    try:
        ir_context = build_merge_ir_context(
            payload,
            allow_unreviewed_text=allow_unreviewed,
        )
    except IRGenerationError as exc:
        raise HTTPException(status_code=422, detail=exc.to_contract()) from exc

    try:
        llm_response = generate_with_fallback(
            LLMRequest(
                task="suggest_merges",
                prompt=_build_merge_prompt(payload, ir_context=ir_context),
                inputs=ir_context.provider_inputs(),
            )
        )
    except ProviderDisabledError as exc:
        _raise_llm_http_error(exc)
    except ProviderRequestError as exc:
        _raise_llm_http_error(exc)

    _audit_llm_trace(request, _resolve_audit_tenant(request, db), payload.doc.id, "suggest_merges", llm_response)

    suggestions = _parse_merge_suggestions(llm_response.raw_text, payload)
    return SuggestMergesResponse(suggestions=suggestions)'''

if text.count(old_route) != 1:
    raise SystemExit(f"merge route replacement count={text.count(old_route)}")
text = text.replace(old_route, new_route, 1)
AI.write_text(text, encoding="utf-8")

coverage = COVERAGE.read_text(encoding="utf-8")
old_migrated = '''        "suggest_card_groups",\n        "suggest_island_summary",'''
new_migrated = '''        "suggest_card_groups",\n        "suggest_island_summary",\n        "suggest_merges",'''
if coverage.count(old_migrated) != 1:
    raise SystemExit("migrated-task anchor missing")
coverage = coverage.replace(old_migrated, new_migrated, 1)
old_debt = '''        "suggest_document_title",\n        "suggest_merges",\n        "summarize_island_relation",'''
new_debt = '''        "suggest_document_title",\n        "summarize_island_relation",'''
if coverage.count(old_debt) != 1:
    raise SystemExit("debt-task anchor missing")
coverage = coverage.replace(old_debt, new_debt, 1)
COVERAGE.write_text(coverage, encoding="utf-8")

print("suggest-merges IR wiring applied")
