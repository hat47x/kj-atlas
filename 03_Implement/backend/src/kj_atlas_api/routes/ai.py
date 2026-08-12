import json
import logging
import math
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from kj_atlas_api.audit import build_event
from kj_atlas_api.db import get_db
from kj_atlas_api.tenant_context import TenantContext
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
    DetectContradictionRequest,
    DetectContradictionResponse,
    ExternalAgentProposalDecisionRequest,
    ExternalAgentProposalRegistrationRequest,
    ExternalAgentProposalRegistrationResponse,
    ExternalAgentTaskRegistrationRequest,
    ExternalAgentTaskRegistrationResponse,
    GenerateNarrativeRequest,
    GenerateNarrativeResponse,
    ProposalDecisionAuditRequest,
    ProposalDecisionAuditResponse,
    ProposalEnvelope,
    ProposeIslandSummaryRequest,
    ProviderStatusResponse,
    RefineCardTextRequest,
    RefineCardTextResponse,
    SuggestCardGroupsRequest,
    SuggestCardGroupsResponse,
    SuggestDocumentTitleRequest,
    SuggestDocumentTitleResponse,
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
from kj_atlas_api.proposal_decision_repository import (
    ProposalDecisionConflict,
    ProposalNotRegistered,
    register_ai_proposal,
    register_external_agent_proposal,
    register_external_agent_task,
    record_proposal_decision as persist_proposal_decision,
)
from kj_atlas_api.routes.docs import _authorize_request, get_document_row
from kj_atlas_api.tenant_session_precondition import (
    require_tenant_scoped_api_precondition,
)

router = APIRouter(prefix="/ai", tags=["ai"])
logger = logging.getLogger(__name__)


def _audit_llm_trace(
    request: Request,
    tenant: TenantContext,
    doc_id: str,
    task: str,
    llm_response,
) -> None:
    """SEC-LLM-AUDIT-01: LLM calls are the most audit-worthy events but only
    reached the local logger. Emit them through the audit dispatcher so
    KJ_ATLAS_AUDIT_TRANSPORT=http configurations receive them. CE2-C5 /
    enterprise_architecture §04.6 fields only -- never prompt or card text."""
    from kj_atlas_api.llm.provider import routing_stage_for_task

    metadata = {
        "task": task,
        "routingStage": routing_stage_for_task(task),
        **build_audit_fields(llm_response),
    }

    logger.info("llm_generate", extra=metadata)

    dispatcher = getattr(request.app.state, "audit_dispatcher", None)
    if dispatcher is not None:
        dispatcher.emit(
            build_event(
                event_type="llm",
                tenant_id=tenant.tenant_id,
                doc_id=doc_id,
                safe_mode=False,  # LLM calls send content regardless of SafeMode (SEC-AI-SAFEMODE-01).
                metadata=metadata,
            )
        )


def _resolve_audit_tenant(request: Request, db: Session) -> TenantContext:
    """SEC-LLM-AUDIT-01: resolve the tenant for audit events without the full
    resource/access control (the LLM routes process payload docs that need not
    be persisted). Mirrors docs.py `_authorize_request`'s tenant resolution."""
    from kj_atlas_api.auth_context import resolve_identity_context
    from kj_atlas_api.saas_request_context import resolve_trusted_saas_request_session
    from kj_atlas_api.tenant_context import SingleTenantContextResolver, TenantContextResolver
    from kj_atlas_api.tenant_session_precondition import (
        require_tenant_session_request_precondition,
        tenant_session_precondition_required,
    )

    if tenant_session_precondition_required(request):
        trusted_session = resolve_trusted_saas_request_session(request=request, db=db)
        require_tenant_session_request_precondition(
            request=request,
            current_version=trusted_session.session.tenant_session_version,
        )
        return trusted_session.tenant
    identity = resolve_identity_context(db=db, request=request)
    resolver: TenantContextResolver = getattr(
        request.app.state,
        "tenant_context_resolver",
        SingleTenantContextResolver(),
    )
    return resolver.resolve(
        db=db,
        user_id=identity.user_id,
        claim=identity.verified_tenant_claim,
    )


def _raise_llm_http_error(exc: ProviderDisabledError | ProviderRequestError) -> None:
    if isinstance(exc, ProviderDisabledError):
        raise HTTPException(status_code=503, detail=exc.to_contract()) from exc

    status_map = {
        "provider_timeout": 504,
        "provider_validation": 422,
        "provider_unavailable": 503,
    }
    raise HTTPException(
        status_code=status_map.get(exc.code, 503), detail=exc.to_contract()
    ) from exc


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

    known_ids = {card.id for card in payload.doc.cards} | {
        island.id for island in payload.doc.islands
    }
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
            reading_order_lines.append(
                f'- {index}. card id="{card.id}", text={json.dumps(card.text)}'
            )
        else:
            reading_order_lines.append(f'- {index}. unknown id="{item_id}"')

    island_lines: list[str] = []
    for island in payload.doc.islands:
        island_cards = [
            cards_by_id[card_id] for card_id in island.cardIds if card_id in cards_by_id
        ]
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
            'If there are no issues, return {"issues":[]}.',
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


def _parse_narrative_check_response(
    raw_text: str, source_doc: CheckNarrativeRequest
) -> CheckNarrativeResponse:
    try:
        parsed = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=422, detail="LLM response is not valid JSON") from exc

    if not isinstance(parsed, dict):
        raise HTTPException(status_code=422, detail="LLM response must be a JSON object")

    try:
        response = CheckNarrativeResponse.model_validate(parsed)
    except Exception as exc:
        raise HTTPException(
            status_code=422, detail="Invalid narrative check response payload"
        ) from exc

    known_card_ids = {card.id for card in source_doc.doc.cards}
    known_island_ids = {island.id for island in source_doc.doc.islands}

    for issue in response.issues:
        if not issue.references:
            continue
        for reference in issue.references:
            if reference.kind == "card" and reference.id not in known_card_ids:
                raise HTTPException(
                    status_code=422, detail="LLM response included unknown card reference"
                )
            if reference.kind == "island" and reference.id not in known_island_ids:
                raise HTTPException(
                    status_code=422, detail="LLM response included unknown island reference"
                )

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
        raise HTTPException(
            status_code=422, detail="Invalid island summary response payload"
        ) from exc

    target_island = next(
        (item for item in source_doc.doc.islands if item.id == source_doc.islandId), None
    )
    if target_island is None:
        raise HTTPException(status_code=422, detail="islandId does not exist")

    member_card_ids = set(target_island.cardIds)
    grounding_ids = response.groundingIds

    if len(grounding_ids) > 10:
        raise HTTPException(
            status_code=422, detail="LLM response groundingIds must contain at most 10 ids"
        )
    if len(set(grounding_ids)) != len(grounding_ids):
        raise HTTPException(
            status_code=422, detail="LLM response groundingIds must not contain duplicates"
        )

    for card_id in grounding_ids:
        if card_id not in member_card_ids:
            raise HTTPException(
                status_code=422, detail="LLM response groundingIds included non-member card id"
            )

    return response


def _build_generate_narrative_prompt(payload: GenerateNarrativeRequest) -> str:
    cards_by_id = {card.id: card for card in payload.doc.cards}
    islands_by_id = {island.id: island for island in payload.doc.islands}
    reading_order = payload.doc.readingOrder or []

    reading_order_lines: list[str] = []
    for index, entry_id in enumerate(reading_order, start=1):
        if entry_id in islands_by_id:
            island = islands_by_id[entry_id]
            island_card_texts = [
                cards_by_id[card_id].text for card_id in island.cardIds if card_id in cards_by_id
            ]
            reading_order_lines.append(
                f'- {index}. island id="{island.id}", title={json.dumps(island.title or "")}, cardIds={json.dumps(island.cardIds)}, cardTexts={json.dumps(island_card_texts)}'
            )
        elif entry_id in cards_by_id:
            card = cards_by_id[entry_id]
            reading_order_lines.append(
                f'- {index}. card id="{card.id}", text={json.dumps(card.text)}'
            )
        else:
            reading_order_lines.append(f'- {index}. unknown id="{entry_id}"')

    instruction_title = (
        payload.narrativeTitle.strip() if payload.narrativeTitle else "Untitled draft narrative"
    )

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
            f"Narrative title hint: {json.dumps(instruction_title)}",
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
        raise HTTPException(
            status_code=422, detail="Invalid generate narrative response payload"
        ) from exc

    if response.text.strip() == "":
        raise HTTPException(status_code=422, detail="Generated narrative text must not be empty")

    reading_order = source_doc.doc.readingOrder or []
    reading_order_set = set(reading_order)
    if any(item_id not in reading_order_set for item_id in response.basedOnReadingOrder):
        raise HTTPException(
            status_code=422, detail="LLM response included unknown reading-order id"
        )

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
        critique_text = f", critique={json.dumps(card.critique)}" if card.critique else ""
        card_lines.append(
            f'- id="{card.id}", text={json.dumps(card.text)}, x={card.x}, y={card.y}{critique_text}'
        )

    island_lines = []
    for island in payload.doc.islands:
        island_cards = [
            cards_by_id[card_id] for card_id in island.cardIds if card_id in cards_by_id
        ]
        if island_cards:
            x_values = [card.x for card in island_cards]
            y_values = [card.y for card in island_cards]
            bounds_text = (
                f"bounds=({min(x_values):.2f},{min(y_values):.2f})-({max(x_values):.2f},{max(y_values):.2f}), "
                f"anchor=({sum(x_values) / len(x_values):.2f},{sum(y_values) / len(y_values):.2f})"
            )
        else:
            bounds_text = "bounds=unknown, anchor=unknown"

        title_text = json.dumps(island.title) if island.title else '""'
        critique_text = f", critique={json.dumps(island.critique)}" if island.critique else ""
        island_lines.append(
            f'- id="{island.id}", title={title_text}, cardIds={json.dumps(island.cardIds)}, '
            f"{bounds_text}{critique_text}"
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


def _parse_suggestion(
    raw_text: str, source_doc: SuggestLayoutRequest
) -> tuple[Transform, list[Card], str | None]:
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
        raise HTTPException(
            status_code=422, detail="LLM response must include all cards exactly once"
        )

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
        if (
            isinstance(x, bool)
            or isinstance(y, bool)
            or not isinstance(x, (int, float))
            or not isinstance(y, (int, float))
        ):
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


def _parse_merge_suggestions(
    raw_text: str, source_doc: SuggestMergesRequest
) -> list[MergeSuggestion]:
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
        raise HTTPException(
            status_code=422, detail="LLM response included more than 10 suggestions"
        )

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
            raise HTTPException(
                status_code=422, detail="Each merge suggestion must include at least 2 cardIds"
            )

        if len(set(suggestion.cardIds)) != len(suggestion.cardIds):
            raise HTTPException(
                status_code=422, detail="Each merge suggestion cardIds must not contain duplicates"
            )

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
def suggest_layout(payload: SuggestLayoutRequest, request: Request, db: Session = Depends(get_db)) -> SuggestLayoutResponse:
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

    _audit_llm_trace(request, _resolve_audit_tenant(request, db), payload.doc.id, "re_layout", llm_response)

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
def suggest_merges(payload: SuggestMergesRequest, request: Request, db: Session = Depends(get_db)) -> SuggestMergesResponse:
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
    return SuggestMergesResponse(suggestions=suggestions)


@router.post(
    "/suggest-island-summary",
    response_model=SuggestIslandSummaryResponse,
    dependencies=[Depends(require_tenant_scoped_api_precondition)],
)
def suggest_island_summary(payload: SuggestIslandSummaryRequest, request: Request, db: Session = Depends(get_db)) -> SuggestIslandSummaryResponse:
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

    _audit_llm_trace(request, _resolve_audit_tenant(request, db), payload.doc.id, "suggest_island_summary", llm_response)

    return _parse_island_summary_response(llm_response.raw_text, payload)


@router.post(
    "/proposals/island-summary",
    response_model=ProposalEnvelope,
    dependencies=[Depends(require_tenant_scoped_api_precondition)],
)
def propose_island_summary(
    payload: ProposeIslandSummaryRequest,
    request: Request,
    db: Session = Depends(get_db),
) -> ProposalEnvelope:
    _, _, tenant = _authorize_request(
        request,
        db,
        action="write",
        doc_id=payload.doc.id,
        safe_mode=False,
        read_only=False,
    )
    if get_document_row(db, tenant=tenant, doc_id=payload.doc.id) is None:
        raise HTTPException(status_code=404, detail="Document not found")
    summary_result = suggest_island_summary(
        SuggestIslandSummaryRequest(doc=payload.doc, islandId=payload.islandId),
        request,
        db,
    )
    target_island = next(
        (item for item in payload.doc.islands if item.id == payload.islandId), None
    )
    if target_island is None:
        raise HTTPException(status_code=422, detail="islandId does not exist")
    proposal = ProposalEnvelope(
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
    try:
        register_ai_proposal(
            db,
            tenant=tenant,
            doc_id=payload.doc.id,
            proposal_id=proposal.proposalId,
            proposal_kind=proposal.type,
            source_bundle_hash=proposal.sourceBundleHash,
        )
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Proposal registration conflicted") from exc
    return proposal


def _record_proposal_decision(
    payload: ProposalDecisionAuditRequest | ExternalAgentProposalDecisionRequest,
    request: Request,
    db: Session,
    *,
    expected_origin: str,
) -> ProposalDecisionAuditResponse:
    access_request, _, tenant = _authorize_request(
        request,
        db,
        action="write",
        doc_id=payload.docId,
        safe_mode=False,
        read_only=False,
    )
    if get_document_row(db, tenant=tenant, doc_id=payload.docId) is None:
        raise HTTPException(status_code=404, detail="Document not found")
    reviewer_ref = access_request.auth.actor_ref if access_request.auth is not None else None
    if reviewer_ref is None:
        raise HTTPException(status_code=401, detail="Authenticated reviewer is required")

    def _persist():
        return persist_proposal_decision(
            db,
            tenant=tenant,
            doc_id=payload.docId,
            proposal_id=payload.proposalId,
            source_bundle_hash=payload.sourceBundleHash,
            idempotency_key=payload.idempotencyKey,
            decision=payload.decision,
            reviewer_ref=reviewer_ref,
            reason=payload.reason,
            expected_origin=expected_origin,
        )

    try:
        receipt = _persist()
        db.commit()
    except ProposalNotRegistered as exc:
        db.rollback()
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ProposalDecisionConflict as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except IntegrityError:
        db.rollback()
        try:
            receipt = _persist()
            db.commit()
        except ProposalNotRegistered as exc:
            db.rollback()
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except (IntegrityError, ProposalDecisionConflict) as exc:
            db.rollback()
            raise HTTPException(status_code=409, detail="Proposal decision conflicted") from exc
    logger.info(
        "proposal_decision_recorded",
        extra={
            "eventId": receipt.event_id,
            "proposalId": receipt.proposal_id,
            "status": receipt.status,
        },
    )
    return ProposalDecisionAuditResponse(
        recorded=True,
        eventId=receipt.event_id,
        proposalId=receipt.proposal_id,
        status=receipt.status,
        reviewState="unreviewed",
        recordedAt=receipt.recorded_at,
    )


@router.post(
    "/external-tasks/register",
    dependencies=[Depends(require_tenant_scoped_api_precondition)],
)
def register_external_task(
    payload: ExternalAgentTaskRegistrationRequest,
    request: Request,
    db: Session = Depends(get_db),
) -> ExternalAgentTaskRegistrationResponse:
    _, _, tenant = _authorize_request(
        request,
        db,
        action="write",
        doc_id=payload.docId,
        safe_mode=False,
        read_only=False,
    )
    document = get_document_row(db, tenant=tenant, doc_id=payload.docId)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    persisted_document = json.loads(document.payload_json)
    if payload.baseDocSignature != f"{document.id}:{persisted_document['updatedAt']}":
        raise HTTPException(status_code=409, detail="External task base document is stale")
    try:
        register_external_agent_task(
            db,
            tenant=tenant,
            task_id=payload.taskId,
            doc_id=payload.docId,
            base_doc_signature=payload.baseDocSignature,
            source_bundle_hash=payload.sourceBundleHash,
            query_canonical_hash=payload.queryCanonicalHash,
            task_kind=payload.taskKind,
        )
        db.commit()
    except ProposalDecisionConflict as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=409, detail="External task registration conflicted"
        ) from exc
    return ExternalAgentTaskRegistrationResponse(
        taskId=payload.taskId,
        provenanceLevel=payload.provenanceLevel,
    )


@router.post(
    "/external-proposals/register",
    dependencies=[Depends(require_tenant_scoped_api_precondition)],
)
def register_external_proposal(
    payload: ExternalAgentProposalRegistrationRequest,
    request: Request,
    db: Session = Depends(get_db),
) -> ExternalAgentProposalRegistrationResponse:
    _, _, tenant = _authorize_request(
        request,
        db,
        action="write",
        doc_id=payload.docId,
        safe_mode=False,
        read_only=False,
    )
    document = get_document_row(db, tenant=tenant, doc_id=payload.docId)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    persisted_document = json.loads(document.payload_json)
    expected_base_signature = f"{document.id}:{persisted_document['updatedAt']}"
    if payload.baseDocSignature != expected_base_signature:
        raise HTTPException(status_code=409, detail="External proposal base document is stale")
    try:
        register_external_agent_proposal(
            db,
            tenant=tenant,
            doc_id=payload.docId,
            proposal_id=payload.proposalId,
            proposal_kind=payload.proposalKind,
            source_bundle_hash=payload.sourceBundleHash,
            task_id=payload.taskId,
            base_doc_signature=payload.baseDocSignature,
            query_canonical_hash=payload.queryCanonicalHash,
            proposal_fingerprint=payload.proposalFingerprint,
        )
        db.commit()
    except ProposalDecisionConflict as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=409, detail="External proposal registration conflicted"
        ) from exc
    return ExternalAgentProposalRegistrationResponse(
        proposalId=payload.proposalId,
        provenanceLevel=payload.provenanceLevel,
    )


@router.post(
    "/proposals/audit",
    dependencies=[Depends(require_tenant_scoped_api_precondition)],
)
def record_proposal_decision(
    payload: ProposalDecisionAuditRequest,
    request: Request,
    db: Session = Depends(get_db),
) -> ProposalDecisionAuditResponse:
    return _record_proposal_decision(payload, request, db, expected_origin="internal")


@router.post(
    "/external-proposals/audit",
    dependencies=[Depends(require_tenant_scoped_api_precondition)],
)
def record_external_proposal_decision(
    payload: ExternalAgentProposalDecisionRequest,
    request: Request,
    db: Session = Depends(get_db),
) -> ProposalDecisionAuditResponse:
    return _record_proposal_decision(payload, request, db, expected_origin="external_agent")


@router.post(
    "/generate-narrative",
    response_model=GenerateNarrativeResponse,
    dependencies=[Depends(require_tenant_scoped_api_precondition)],
)
def generate_narrative(payload: GenerateNarrativeRequest, request: Request, db: Session = Depends(get_db)) -> GenerateNarrativeResponse:
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

    _audit_llm_trace(request, _resolve_audit_tenant(request, db), payload.doc.id, "generate_narrative", llm_response)

    return _parse_generate_narrative_response(llm_response.raw_text, payload)


@router.post(
    "/check-narrative",
    response_model=CheckNarrativeResponse,
    dependencies=[Depends(require_tenant_scoped_api_precondition)],
)
def check_narrative(payload: CheckNarrativeRequest, request: Request, db: Session = Depends(get_db)) -> CheckNarrativeResponse:
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

    _audit_llm_trace(request, _resolve_audit_tenant(request, db), payload.doc.id, "check_narrative", llm_response)

    return _parse_narrative_check_response(llm_response.raw_text, payload)


# ---------------------------------------------------------------------------
# ADR-0064: KJ-method card-level AI operations
# ---------------------------------------------------------------------------


def _build_refine_card_text_prompt(payload: RefineCardTextRequest) -> str:
    ctx = f"\nContext: {payload.context}" if payload.context else ""
    return (
        f"Refine the wording of this KJ-method card. "
        f"Make it clearer and more concise while preserving the original meaning. "
        f'Return JSON: {{"refinedText": "...", "reasoning": "..."}}\n'
        f"Card text: {payload.cardText}{ctx}"
    )


def _parse_refine_card_text_response(raw_text: str) -> RefineCardTextResponse:
    data = json.loads(raw_text)
    return RefineCardTextResponse(
        refinedText=str(data.get("refinedText", data.get("refined_text", ""))),
        reasoning=data.get("reasoning"),
    )


def _build_suggest_card_groups_prompt(payload: SuggestCardGroupsRequest) -> str:
    cards = "\n".join(f'  - id="{c.id}", text="{c.text}"' for c in payload.cards)
    return (
        f"Group these KJ-method cards into thematic islands. "
        f'Return JSON: {{"groups": [{{"label": "...", "cardIds": ["..."], '
        f'"rationale": "..."}}]}}\nCards:\n{cards}'
    )


def _parse_suggest_card_groups_response(raw_text: str) -> SuggestCardGroupsResponse:
    data = json.loads(raw_text)
    from kj_atlas_api.models_ai import _SuggestedGroup

    return SuggestCardGroupsResponse(
        groups=[
            _SuggestedGroup(
                label=str(g.get("label", "")),
                cardIds=[str(c) for c in g.get("cardIds", g.get("card_ids", []))],
                rationale=g.get("rationale"),
            )
            for g in data.get("groups", [])
        ]
    )


def _build_detect_contradiction_prompt(payload: DetectContradictionRequest) -> str:
    return (
        f"Determine if these two KJ-method cards contradict each other. "
        f'Return JSON: {{"hasContradiction": true|false, "explanation": "..."}}\n'
        f"Card A (id={payload.cardA.id}): {payload.cardA.text}\n"
        f"Card B (id={payload.cardB.id}): {payload.cardB.text}"
    )


def _parse_detect_contradiction_response(raw_text: str) -> DetectContradictionResponse:
    data = json.loads(raw_text)
    return DetectContradictionResponse(
        hasContradiction=bool(data.get("hasContradiction", data.get("has_contradiction", False))),
        explanation=data.get("explanation"),
    )


# ---------------------------------------------------------------------------
# Card-level AI endpoints
# ---------------------------------------------------------------------------


@router.post(
    "/refine-card-text",
    response_model=RefineCardTextResponse,
    dependencies=[Depends(require_tenant_scoped_api_precondition)],
)
def refine_card_text(payload: RefineCardTextRequest, request: Request, db: Session = Depends(get_db)) -> RefineCardTextResponse:
    try:
        llm_response = generate_with_fallback(
            LLMRequest(
                task="refine_card_text",
                prompt=_build_refine_card_text_prompt(payload),
            )
        )
    except ProviderDisabledError as exc:
        _raise_llm_http_error(exc)
    except ProviderRequestError as exc:
        _raise_llm_http_error(exc)
    # RefineCardTextRequest has no document context; audit with empty doc_id.
    _audit_llm_trace(request, _resolve_audit_tenant(request, db), "(no-doc)", "refine_card_text", llm_response)
    return _parse_refine_card_text_response(llm_response.raw_text)


@router.post(
    "/suggest-card-groups",
    response_model=SuggestCardGroupsResponse,
    dependencies=[Depends(require_tenant_scoped_api_precondition)],
)
def suggest_card_groups(payload: SuggestCardGroupsRequest, request: Request, db: Session = Depends(get_db)) -> SuggestCardGroupsResponse:
    try:
        llm_response = generate_with_fallback(
            LLMRequest(
                task="suggest_card_groups",
                prompt=_build_suggest_card_groups_prompt(payload),
            )
        )
    except ProviderDisabledError as exc:
        _raise_llm_http_error(exc)
    except ProviderRequestError as exc:
        _raise_llm_http_error(exc)
    # SuggestCardGroupsRequest has no document context; audit with empty doc_id.
    _audit_llm_trace(request, _resolve_audit_tenant(request, db), "(no-doc)", "suggest_card_groups", llm_response)
    return _parse_suggest_card_groups_response(llm_response.raw_text)


@router.post(
    "/detect-contradiction",
    response_model=DetectContradictionResponse,
    dependencies=[Depends(require_tenant_scoped_api_precondition)],
)
def detect_contradiction(payload: DetectContradictionRequest, request: Request, db: Session = Depends(get_db)) -> DetectContradictionResponse:
    try:
        llm_response = generate_with_fallback(
            LLMRequest(
                task="detect_contradiction",
                prompt=_build_detect_contradiction_prompt(payload),
            )
        )
    except ProviderDisabledError as exc:
        _raise_llm_http_error(exc)
    except ProviderRequestError as exc:
        _raise_llm_http_error(exc)
    # DetectContradictionRequest has no document context; audit with empty doc_id.
    _audit_llm_trace(request, _resolve_audit_tenant(request, db), "(no-doc)", "detect_contradiction", llm_response)
    return _parse_detect_contradiction_response(llm_response.raw_text)


@router.post(
    "/suggest-document-title",
    response_model=SuggestDocumentTitleResponse,
    dependencies=[Depends(require_tenant_scoped_api_precondition)],
)
def suggest_document_title(payload: SuggestDocumentTitleRequest, request: Request, db: Session = Depends(get_db)) -> SuggestDocumentTitleResponse:
    try:
        llm_response = generate_with_fallback(
            LLMRequest(
                task="suggest_document_title",
                prompt=_build_suggest_document_title_prompt(payload),
                temperature=0.4,
                max_tokens=300,
            )
        )
    except ProviderDisabledError as exc:
        _raise_llm_http_error(exc)
    except ProviderRequestError as exc:
        _raise_llm_http_error(exc)
    # SuggestDocumentTitleRequest has no document context; audit with empty doc_id.
    _audit_llm_trace(request, _resolve_audit_tenant(request, db), "(no-doc)", "suggest_document_title", llm_response)
    return _parse_suggest_document_title_response(llm_response.raw_text)


def _build_suggest_document_title_prompt(payload: SuggestDocumentTitleRequest) -> str:
    islands = (
        "\n".join(f"  - {t}" for t in payload.islandTitles[:20])
        if payload.islandTitles
        else "(none)"
    )
    cards = "\n".join(f"  - {t}" for t in payload.cardTexts[:30]) if payload.cardTexts else "(none)"
    current = f'\nCurrent title: "{payload.currentTitle}"' if payload.currentTitle else ""
    return (
        f"Suggest 1-3 short document titles (each max 80 chars, in Japanese) that "
        f"capture the overall theme of this KJ-method canvas. "
        f"The document contains these island labels and card texts. "
        f"Do NOT rank or score the candidates — present them as equal alternatives.{current}\n"
        f"Island labels:\n{islands}\n"
        f"Sample card texts:\n{cards}\n"
        f'Return JSON: {{"candidates": [{{"title": "..."}}]}}'
    )


def _parse_suggest_document_title_response(raw_text: str) -> SuggestDocumentTitleResponse:
    data = json.loads(raw_text)
    from kj_atlas_api.models_ai import _DocumentTitleCandidate

    candidates_raw = data.get("candidates", [])
    if not isinstance(candidates_raw, list) or len(candidates_raw) == 0:
        raise ValueError("suggest_document_title response had no candidates")
    candidates = [
        _DocumentTitleCandidate(title=str(c.get("title", ""))[:500]) for c in candidates_raw[:3]
    ]
    if not candidates:
        raise ValueError("suggest_document_title response had empty candidates")
    return SuggestDocumentTitleResponse(candidates=candidates)
