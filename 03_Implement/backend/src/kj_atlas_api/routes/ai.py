import json
import logging
import math
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException

from kj_atlas_api.llm.provider import (
    LLMRequest,
    ProviderDisabledError,
    ProviderRequestError,
    build_audit_fields,
    generate_with_fallback,
    get_provider,
)
from kj_atlas_api.models_ai import (
    CheckNarrativeRequest,
    CheckNarrativeResponse,
    GenerateNarrativeRequest,
    GenerateNarrativeResponse,
    ProposalDecisionAuditRequest,
    ProposalDecisionAuditResponse,
    ProposalEnvelope,
    ProposeIslandSummaryRequest,
    ProviderStatusResponse,
    SuggestIslandSummaryRequest,
    SuggestIslandSummaryResponse,
)
from kj_atlas_api.models import (
    Card,
    MergeSuggestion,
    SuggestLayoutRequest,
    SuggestLayoutResponse,
    SuggestMergesRequest,
    SuggestMergesResponse,
    Transform,
)
from kj_atlas_api.tenant_session_precondition import (
    require_tenant_scoped_api_precondition,
)

router = APIRouter(prefix="/ai", tags=["ai"])
logger = logging.getLogger(__name__)


def _audit_llm_trace(task: str, llm_response) -> None:
    logger.info(
        "llm_generate",
        extra={"task": task, **build_audit_fields(llm_response)},
    )


def _raise_llm_http_error(exc: ProviderDisabledError | ProviderRequestError) -> None:
    if isinstance(exc, ProviderDisabledError):
        raise HTTPException(status_code=503, detail=exc.to_contract()) from exc

    status_map = {
        "provider_timeout": 504,
        "provider_validation": 422,
        "provider_unavailable": 503,
    }
    raise HTTPException(status_code=status_map.get(exc.code, 503), detail=exc.to_contract()) from exc


def _resolve_reading_order(payload: CheckNarrativeRequest) -> list[str]:
    if payload.basedOnReadingOrder is not None:
        return payload.basedOnReadingOrder
    if payload.doc.readingOrder is not None:
        return payload.doc.readingOrder
    return []


def _validate_check_narrative_input(payload: CheckNarrativeRequest) -> None:
    if payload.narrativeText.strip() == "":
        raise HTTPException(status_code=422, detail="narrativeText must not be empty")

    if payload.basedOnReadingOrder is None:
        return

    known_ids = {card.id for card in payload.doc.cards} | {island.id for island in payload.doc.islands}
    unknown_ids = [item_id for item_id in payload.basedOnReadingOrder if item_id not in known_ids]
    if unknown_ids:
        raise HTTPException(status_code=422, detail="basedOnReadingOrder included unknown id")


def _build_narrative_check_prompt(payload: CheckNarrativeRequest) -> str:
    cards_by_id = {card.id: card for card in payload.doc.cards}
    islands_by_id = {island.id: island for island in payload.doc.islands}

    reading_order = _resolve_reading_order(payload)
    reading_order_lines: list[str] = []
    for index, item_id in enumerate(reading_order, start=1):
        if item_id in islands_by_id:
            island = islands_by_id[item_id]
            reading_order_lines.append(
                f'- {index}. island id="{island.id}", title={json.dumps(island.title or "")}, cardIds={json.dumps(island.cardIds)}'
            )
        elif item_id in cards_by_id:
            card = cards_by_id[item_id]
            reading_order_lines.append(f'- {index}. card id="{card.id}", text={json.dumps(card.text)}')
        else:
            reading_order_lines.append(f'- {index}. unknown id="{item_id}"')

    island_lines: list[str] = []
    for island in payload.doc.islands:
        island_cards = [cards_by_id[card_id] for card_id in island.cardIds if card_id in cards_by_id]
        card_texts = [card.text for card in island_cards]
        island_lines.append(
            f'- id="{island.id}", title={json.dumps(island.title or "")}, cardIds={json.dumps(island.cardIds)}, cardTexts={json.dumps(card_texts)}'
        )

    card_lines = [f'- id="{card.id}", text={json.dumps(card.text)}' for card in payload.doc.cards]

    return "\n".join(
        [
            "You are performing a best-effort narrative consistency check against a diagram.",
            "Output is advisory only. Never claim certainty or correctness.",
            "Return strict JSON only. No markdown. No text outside JSON.",
            "Identify missing key islands/cards based on reading order.",
            "Identify contradictions such as reading-order mismatch or narrative claims not supported by any card text.",
            "Identify ambiguous transitions, e.g. pronouns like it/they/this/that without a clear referent.",
            "If there are no issues, return {\"issues\":[]}.",
            "Use this exact schema:",
            '{"issues":[{"severity":"info|warn|error","message":string,"references":[{"id":string,"kind":"card|island"}]?}]}',
            "Only include references that exist in the input diagram.",
            "Narrative text:",
            payload.narrativeText,
            "Reading order:",
            *reading_order_lines,
            "Islands:",
            *island_lines,
            "Cards:",
            *card_lines,
        ]
    )


def _parse_narrative_check_response(raw_text: str, source_doc: CheckNarrativeRequest) -> CheckNarrativeResponse:
    try:
        parsed = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=422, detail="LLM response is not valid JSON") from exc

    if not isinstance(parsed, dict):
        raise HTTPException(status_code=422, detail="LLM response must be a JSON object")

    try:
        response = CheckNarrativeResponse.model_validate(parsed)
    except Exception as exc:
        raise HTTPException(status_code=422, detail="Invalid narrative check response payload") from exc

    known_card_ids = {card.id for card in source_doc.doc.cards}
    known_island_ids = {island.id for island in source_doc.doc.islands}

    for issue in response.issues:
        if not issue.references:
            continue
        for reference in issue.references:
            if reference.kind == "card" and reference.id not in known_card_ids:
                raise HTTPException(status_code=422, detail="LLM response included unknown card reference")
            if reference.kind == "island" and reference.id not in known_island_ids:
                raise HTTPException(status_code=422, detail="LLM response included unknown island reference")

    return response




def _build_island_summary_prompt(payload: SuggestIslandSummaryRequest) -> str:
    cards_by_id = {card.id: card for card in payload.doc.cards}
    island = next((item for item in payload.doc.islands if item.id == payload.islandId), None)
    if island is None:
        raise HTTPException(status_code=422, detail="islandId does not exist")

    member_cards = [cards_by_id[card_id] for card_id in island.cardIds if card_id in cards_by_id]
    if len(member_cards) == 0:
        raise HTTPException(status_code=422, detail="island has no member cards")

    card_lines = [f'- id="{card.id}", text={json.dumps(card.text)}' for card in member_cards]

    return "\n".join(
        [
            "You generate a draft island summary from evidence cards.",
            "Use only the direct member cards provided below. Ignore nested islands for this MVP.",
            "Do not add facts beyond the card texts.",
            "If evidence is weak, sparse, or contradictory, include warnings.",
            "Return strict JSON only. No markdown. No extra text.",
            "Use this exact schema:",
            '{"summaryText":string,"groundingIds":[string,...],"warnings":[string,...]?}',
            "groundingIds must contain 1-10 unique card ids chosen from the input cards.",
            "Prefer the strongest supporting card ids.",
            f'Island id="{island.id}", title={json.dumps(island.title or "")}',
            "Member cards:",
            *card_lines,
        ]
    )


def _parse_island_summary_response(
    raw_text: str,
    source_doc: SuggestIslandSummaryRequest,
) -> SuggestIslandSummaryResponse:
    try:
        parsed = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=422, detail="LLM response is not valid JSON") from exc

    if not isinstance(parsed, dict):
        raise HTTPException(status_code=422, detail="LLM response must be a JSON object")

    try:
        response = SuggestIslandSummaryResponse.model_validate(parsed)
    except Exception as exc:
        raise HTTPException(status_code=422, detail="Invalid island summary response payload") from exc

    target_island = next((item for item in source_doc.doc.islands if item.id == source_doc.islandId), None)
    if target_island is None:
        raise HTTPException(status_code=422, detail="islandId does not exist")

    member_card_ids = set(target_island.cardIds)
    grounding_ids = response.groundingIds

    if len(grounding_ids) > 10:
        raise HTTPException(status_code=422, detail="LLM response groundingIds must contain at most 10 ids")
    if len(set(grounding_ids)) != len(grounding_ids):
        raise HTTPException(status_code=422, detail="LLM response groundingIds must not contain duplicates")

    for card_id in grounding_ids:
        if card_id not in member_card_ids:
            raise HTTPException(status_code=422, detail="LLM response groundingIds included non-member card id")

    return response


def _build_generate_narrative_prompt(payload: GenerateNarrativeRequest) -> str:
    cards_by_id = {card.id: card for card in payload.doc.cards}
    islands_by_id = {island.id: island for island in payload.doc.islands}
    reading_order = payload.doc.readingOrder or []

    reading_order_lines: list[str] = []
    for index, entry_id in enumerate(reading_order, start=1):
        if entry_id in islands_by_id:
            island = islands_by_id[entry_id]
            island_card_texts = [cards_by_id[card_id].text for card_id in island.cardIds if card_id in cards_by_id]
            reading_order_lines.append(
                f'- {index}. island id="{island.id}", title={json.dumps(island.title or "")}, cardIds={json.dumps(island.cardIds)}, cardTexts={json.dumps(island_card_texts)}'
            )
        elif entry_id in cards_by_id:
            card = cards_by_id[entry_id]
            reading_order_lines.append(f'- {index}. card id="{card.id}", text={json.dumps(card.text)}')
        else:
            reading_order_lines.append(f'- {index}. unknown id="{entry_id}"')

    instruction_title = payload.narrativeTitle.strip() if payload.narrativeTitle else "Untitled draft narrative"

    return "\n".join(
        [
            "You generate a narrative draft from diagram reading order.",
            "This is advisory only. Do not claim facts, truth, or certainty.",
            "Every statement must be phrased as interpretation or possibility based on the diagram.",
            "Use reading order as the narrative spine. Follow the order exactly.",
            "For each reading-order item, describe what it appears to contain and what it might mean.",
            "Explicitly label the output as draft and unreviewed.",
            "Return strict JSON only. No markdown. No extra keys.",
            "Use this exact schema:",
            '{"text":string,"basedOnReadingOrder":[string,...],"warnings":[string,...]?}',
            "basedOnReadingOrder must include only IDs from the provided reading order and preserve that order.",
            f'Narrative title hint: {json.dumps(instruction_title)}',
            "Reading order:",
            *(reading_order_lines or ["- (empty)"]),
        ]
    )


def _parse_generate_narrative_response(
    raw_text: str, source_doc: GenerateNarrativeRequest
) -> GenerateNarrativeResponse:
    try:
        parsed = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=422, detail="LLM response is not valid JSON") from exc

    if not isinstance(parsed, dict):
        raise HTTPException(status_code=422, detail="LLM response must be a JSON object")

    try:
        response = GenerateNarrativeResponse.model_validate(parsed)
    except Exception as exc:
        raise HTTPException(status_code=422, detail="Invalid generate narrative response payload") from exc

    if response.text.strip() == "":
        raise HTTPException(status_code=422, detail="Generated narrative text must not be empty")

    reading_order = source_doc.doc.readingOrder or []
    reading_order_set = set(reading_order)
    if any(item_id not in reading_order_set for item_id in response.basedOnReadingOrder):
        raise HTTPException(status_code=422, detail="LLM response included unknown reading-order id")

    if response.basedOnReadingOrder != reading_order:
        raise HTTPException(
            status_code=422,
            detail="LLM response basedOnReadingOrder must match source reading order exactly",
        )

    return response

def _build_prompt(payload: SuggestLayoutRequest) -> str:
    cards_by_id = {card.id: card for card in payload.doc.cards}
    card_lines = []
    for card in payload.doc.cards:
        critique_text = f', critique={json.dumps(card.critique)}' if card.critique else ""
        card_lines.append(
            f'- id="{card.id}", text={json.dumps(card.text)}, x={card.x}, y={card.y}{critique_text}'
        )

    island_lines = []
    for island in payload.doc.islands:
        island_cards = [cards_by_id[card_id] for card_id in island.cardIds if card_id in cards_by_id]
        if island_cards:
            x_values = [card.x for card in island_cards]
            y_values = [card.y for card in island_cards]
            bounds_text = (
                f'bounds=({min(x_values):.2f},{min(y_values):.2f})-({max(x_values):.2f},{max(y_values):.2f}), '
                f'anchor=({sum(x_values) / len(x_values):.2f},{sum(y_values) / len(y_values):.2f})'
            )
        else:
            bounds_text = "bounds=unknown, anchor=unknown"

        title_text = json.dumps(island.title) if island.title else '""'
        critique_text = f', critique={json.dumps(island.critique)}' if island.critique else ""
        island_lines.append(
            f'- id="{island.id}", title={title_text}, cardIds={json.dumps(island.cardIds)}, '
            f'{bounds_text}{critique_text}'
        )

    instruction = payload.instruction.strip() if payload.instruction else "No extra instruction"

    return "\n".join(
        [
            "You are generating a draft layout suggestion.",
            "Return JSON only, no markdown.",
            "Do not force a single correct answer. Suggest one plausible alternative layout.",
            "If a critique says 'too close', increase distance.",
            "If a critique says 'belongs together', place nearer.",
            "Preserve all ids and texts. Only propose positions and transform.",
            "Use this exact schema:",
            '{"transform":{"panX":number,"panY":number,"zoom":number},"cards":[{"id":string,"x":number,"y":number}],"notes":string?}',
            f"Instruction: {instruction}",
            (
                f"Current transform: panX={payload.doc.transform.panX}, "
                f"panY={payload.doc.transform.panY}, zoom={payload.doc.transform.zoom}"
            ),
            "Cards:",
            *card_lines,
            "Islands:",
            *island_lines,
        ]
    )


def _parse_suggestion(raw_text: str, source_doc: SuggestLayoutRequest) -> tuple[Transform, list[Card], str | None]:
    try:
        parsed = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=422, detail="LLM response is not valid JSON") from exc

    if not isinstance(parsed, dict):
        raise HTTPException(status_code=422, detail="LLM response must be a JSON object")

    transform_data = parsed.get("transform")
    cards_data = parsed.get("cards")
    notes_data = parsed.get("notes")

    if not isinstance(transform_data, dict):
        raise HTTPException(status_code=422, detail="LLM response missing transform")
    if not isinstance(cards_data, list):
        raise HTTPException(status_code=422, detail="LLM response missing cards")
    if notes_data is not None and not isinstance(notes_data, str):
        raise HTTPException(status_code=422, detail="LLM response notes must be a string")

    try:
        transform = Transform.model_validate(transform_data)
    except Exception as exc:  # pydantic validation error
        raise HTTPException(status_code=422, detail="Invalid transform in LLM response") from exc

    if not all(math.isfinite(value) for value in (transform.panX, transform.panY, transform.zoom)):
        raise HTTPException(status_code=422, detail="Transform values must be finite numbers")

    source_cards_by_id = {card.id: card for card in source_doc.doc.cards}
    if len(cards_data) != len(source_cards_by_id):
        raise HTTPException(status_code=422, detail="LLM response must include all cards exactly once")

    suggested_cards_by_id: dict[str, Card] = {}
    for card_item in cards_data:
        if not isinstance(card_item, dict):
            raise HTTPException(status_code=422, detail="Each card suggestion must be an object")

        card_id = card_item.get("id")
        if not isinstance(card_id, str):
            raise HTTPException(status_code=422, detail="Each card suggestion must include id")

        source_card = source_cards_by_id.get(card_id)
        if source_card is None:
            raise HTTPException(status_code=422, detail="LLM response included unknown card id")
        if card_id in suggested_cards_by_id:
            raise HTTPException(status_code=422, detail="LLM response included duplicate card id")

        x = card_item.get("x")
        y = card_item.get("y")
        if isinstance(x, bool) or isinstance(y, bool) or not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
            raise HTTPException(status_code=422, detail="Card x/y must be numbers")
        if not math.isfinite(float(x)) or not math.isfinite(float(y)):
            raise HTTPException(status_code=422, detail="Card x/y must be finite numbers")

        suggested_cards_by_id[card_id] = Card(
            id=source_card.id,
            text=source_card.text,
            x=float(x),
            y=float(y),
        )

    suggested_cards = [suggested_cards_by_id[card.id] for card in source_doc.doc.cards]
    return transform, suggested_cards, notes_data


def _build_merge_prompt(payload: SuggestMergesRequest) -> str:
    card_lines = [f'- id="{card.id}", text="{card.text}"' for card in payload.doc.cards]
    instruction = payload.instruction.strip() if payload.instruction else "No extra instruction"

    return "\n".join(
        [
            "You suggest potential merge candidates for similar cards.",
            "You must only propose suggestions. Do not apply merges and do not delete anything.",
            "Return strict JSON only. No markdown. No explanation text outside JSON.",
            "Return at most 10 suggestions.",
            "Use this exact schema:",
            '{"suggestions":[{"groupId":string,"cardIds":[string,...],"mergedTextDraft":string,"rationale":string?}]}',
            "Each suggestion must include at least 2 cardIds.",
            "Only use card IDs from the input.",
            f"Instruction: {instruction}",
            "Cards:",
            *card_lines,
        ]
    )


def _parse_merge_suggestions(raw_text: str, source_doc: SuggestMergesRequest) -> list[MergeSuggestion]:
    try:
        parsed = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=422, detail="LLM response is not valid JSON") from exc

    if not isinstance(parsed, dict):
        raise HTTPException(status_code=422, detail="LLM response must be a JSON object")

    suggestions_data = parsed.get("suggestions")
    if not isinstance(suggestions_data, list):
        raise HTTPException(status_code=422, detail="LLM response missing suggestions array")
    if len(suggestions_data) > 10:
        raise HTTPException(status_code=422, detail="LLM response included more than 10 suggestions")

    known_card_ids = {card.id for card in source_doc.doc.cards}
    parsed_suggestions: list[MergeSuggestion] = []
    seen_group_ids: set[str] = set()

    for item in suggestions_data:
        if not isinstance(item, dict):
            raise HTTPException(status_code=422, detail="Each merge suggestion must be an object")

        try:
            suggestion = MergeSuggestion.model_validate(item)
        except Exception as exc:
            raise HTTPException(status_code=422, detail="Invalid merge suggestion payload") from exc

        if suggestion.groupId in seen_group_ids:
            raise HTTPException(status_code=422, detail="Duplicate merge suggestion groupId")
        seen_group_ids.add(suggestion.groupId)

        if len(suggestion.cardIds) < 2:
            raise HTTPException(status_code=422, detail="Each merge suggestion must include at least 2 cardIds")

        if len(set(suggestion.cardIds)) != len(suggestion.cardIds):
            raise HTTPException(status_code=422, detail="Each merge suggestion cardIds must not contain duplicates")

        unknown_ids = [card_id for card_id in suggestion.cardIds if card_id not in known_card_ids]
        if unknown_ids:
            raise HTTPException(status_code=422, detail="LLM response included unknown card id")

        parsed_suggestions.append(suggestion)

    return parsed_suggestions


@router.get("/provider-status", response_model=ProviderStatusResponse)
def get_provider_status() -> ProviderStatusResponse:
    """PROV-VIS-01 (ADR-0050 D1): read-only echo of the configured provider
    kind for display in the View panel. No connectivity check is performed;
    "last known outcome" is tracked client-side from real AI-call results."""
    return ProviderStatusResponse(providerKind=get_provider().provider_kind)


@router.post(
    "/suggest-layout",
    response_model=SuggestLayoutResponse,
    dependencies=[Depends(require_tenant_scoped_api_precondition)],
)
def suggest_layout(payload: SuggestLayoutRequest) -> SuggestLayoutResponse:
    try:
        llm_response = generate_with_fallback(
            LLMRequest(
                task="re_layout",
                prompt=_build_prompt(payload),
            )
        )
    except ProviderDisabledError as exc:
        _raise_llm_http_error(exc)
    except ProviderRequestError as exc:
        _raise_llm_http_error(exc)

    _audit_llm_trace("re_layout", llm_response)

    transform, cards, notes = _parse_suggestion(llm_response.raw_text, payload)

    suggested_doc = payload.doc.model_copy(
        update={
            "transform": transform,
            "cards": cards,
        }
    )

    return SuggestLayoutResponse(
        suggestionId=str(uuid4()),
        suggestedDoc=suggested_doc,
        notes=notes,
    )


@router.post(
    "/suggest-merges",
    response_model=SuggestMergesResponse,
    dependencies=[Depends(require_tenant_scoped_api_precondition)],
)
def suggest_merges(payload: SuggestMergesRequest) -> SuggestMergesResponse:
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

    _audit_llm_trace("suggest_merges", llm_response)

    suggestions = _parse_merge_suggestions(llm_response.raw_text, payload)
    return SuggestMergesResponse(suggestions=suggestions)




@router.post(
    "/suggest-island-summary",
    response_model=SuggestIslandSummaryResponse,
    dependencies=[Depends(require_tenant_scoped_api_precondition)],
)
def suggest_island_summary(payload: SuggestIslandSummaryRequest) -> SuggestIslandSummaryResponse:
    try:
        llm_response = generate_with_fallback(
            LLMRequest(
                task="suggest_island_summary",
                prompt=_build_island_summary_prompt(payload),
            )
        )
    except ProviderDisabledError as exc:
        _raise_llm_http_error(exc)
    except ProviderRequestError as exc:
        _raise_llm_http_error(exc)

    _audit_llm_trace("suggest_island_summary", llm_response)

    return _parse_island_summary_response(llm_response.raw_text, payload)


@router.post(
    "/proposals/island-summary",
    response_model=ProposalEnvelope,
    dependencies=[Depends(require_tenant_scoped_api_precondition)],
)
def propose_island_summary(payload: ProposeIslandSummaryRequest) -> ProposalEnvelope:
    summary_result = suggest_island_summary(SuggestIslandSummaryRequest(doc=payload.doc, islandId=payload.islandId))
    target_island = next((item for item in payload.doc.islands if item.id == payload.islandId), None)
    if target_island is None:
        raise HTTPException(status_code=422, detail="islandId does not exist")
    return ProposalEnvelope(
        proposalId=f"proposal-{uuid4()}",
        type="island_summary",
        status="proposed",
        reviewState="unreviewed",
        sourceBundleHash=payload.sourceBundleHash,
        diff={
            "entityType": "island_summary",
            "targetId": payload.islandId,
            "field": "summaryText",
            "before": target_island.summaryText,
            "after": summary_result.summaryText,
            "groundingIds": summary_result.groundingIds,
            "warnings": summary_result.warnings,
        },
        rationale="AI generated proposal only. Human decision is required before any apply.",
    )


@router.post(
    "/proposals/audit",
    dependencies=[Depends(require_tenant_scoped_api_precondition)],
)
def record_proposal_decision(payload: ProposalDecisionAuditRequest) -> ProposalDecisionAuditResponse:
    if payload.decision not in {"accepted", "rejected", "held"}:
        raise HTTPException(
            status_code=422,
            detail="decision must be one of accepted|rejected|held",
        )
    status = payload.decision
    logger.info(
        "proposal_decision_audit",
        extra={
            "proposalId": payload.proposalId,
            "decision": status,
            "actor": payload.actor,
            "reason": payload.reason or "",
        },
    )
    return ProposalDecisionAuditResponse(
        proposalId=payload.proposalId,
        status=status,
        reviewState="unreviewed",
        recordedAt="server-log",
    )


@router.post(
    "/generate-narrative",
    response_model=GenerateNarrativeResponse,
    dependencies=[Depends(require_tenant_scoped_api_precondition)],
)
def generate_narrative(payload: GenerateNarrativeRequest) -> GenerateNarrativeResponse:
    try:
        llm_response = generate_with_fallback(
            LLMRequest(
                task="generate_narrative",
                prompt=_build_generate_narrative_prompt(payload),
            )
        )
    except ProviderDisabledError as exc:
        _raise_llm_http_error(exc)
    except ProviderRequestError as exc:
        _raise_llm_http_error(exc)

    _audit_llm_trace("generate_narrative", llm_response)

    return _parse_generate_narrative_response(llm_response.raw_text, payload)

@router.post(
    "/check-narrative",
    response_model=CheckNarrativeResponse,
    dependencies=[Depends(require_tenant_scoped_api_precondition)],
)
def check_narrative(payload: CheckNarrativeRequest) -> CheckNarrativeResponse:
    _validate_check_narrative_input(payload)

    try:
        llm_response = generate_with_fallback(
            LLMRequest(
                task="check_narrative",
                prompt=_build_narrative_check_prompt(payload),
            )
        )
    except ProviderDisabledError as exc:
        _raise_llm_http_error(exc)
    except ProviderRequestError as exc:
        _raise_llm_http_error(exc)

    _audit_llm_trace("check_narrative", llm_response)

    return _parse_narrative_check_response(llm_response.raw_text, payload)
