import json
import logging
import math
from typing import Literal
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from kj_atlas_api.audit import build_event
from kj_atlas_api.db import get_db
from kj_atlas_api.settings import settings
from kj_atlas_api.tenant_context import TenantContext
from kj_atlas_api.llm.provider import (
    LLMRequest,
    ProviderDisabledError,
    ProviderRequestError,
    build_audit_fields,
    generate_with_fallback,
    get_provider,
    resolve_model_for_task,
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
    OpposingViewpointProposal,
    ProposalDecisionAuditRequest,
    ProposalDecisionAuditResponse,
    ProposalEnvelope,
    ProposeIslandSummaryRequest,
    ProposeOpposingViewpointRequest,
    ProposalStatusItem,
    ProposalStatusResponse,
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
    AIProposalDecisionStateRow,
    AIProposalRow,
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

_PROVIDER_KIND_ALIASES = {
    "local_http": "local",
    "large_scale": "large-scale",
    "external": "large-scale",
}


def _canonical_provider_kind(raw_kind: str) -> str:
    normalized = raw_kind.strip().lower()
    return _PROVIDER_KIND_ALIASES.get(normalized, normalized)


def _provider_matches_runtime(provider_kind: str) -> bool:
    return _canonical_provider_kind(provider_kind) == _canonical_provider_kind(get_provider().provider_kind)


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


def _assert_model_allowed(request: Request, db: Session, model_id: str) -> None:
    """AI-MODEL-GOVERNANCE-01 R3 + AI-MODEL-GOVERNANCE-02: enforce the tenant
    model allowlist AND that the model is an active registered model.

    - A non-empty allowlist is fail-closed: a requested/resolved model outside
      it is rejected with 403 model_not_allowed before any LLM call.
    - Empty allowlist = platform-default: "all active registered models allowed".
      AI-MODEL-GOVERNANCE-02 closes the gap where the platform-default was a
      no-op, letting unregistered / disabled model ids reach the LLM provider.
      An id that is not an active registered model (active provider included)
      is rejected with 403 model_not_registered."""
    from kj_atlas_api.model_registry_repository import (
        list_models,
        list_providers,
        tenant_allowlist_effective_model_ids,
    )

    tenant = _resolve_audit_tenant(request, db)
    effective = tenant_allowlist_effective_model_ids(db, tenant_id=tenant.tenant_id)
    if effective is not None and model_id not in effective:
        # R4: a model_not_allowed violation is a governance-relevant event --
        # structured-log it (with the request id already attached by the logging
        # substrate) so an operator can investigate repeated denials per tenant.
        logger.warning(
            "model_not_allowed",
            extra={
                "tenantId": tenant.tenant_id,
                "modelId": model_id,
                "allowedModels": ",".join(sorted(effective)),
            },
        )
        raise HTTPException(
            status_code=403,
            detail={
                "code": "model_not_allowed",
                "message": f"Model '{model_id}' is not in the tenant's allowed model set.",
                "allowedModels": sorted(effective),
            },
        )

    # AI-MODEL-GOVERNANCE-02: the registry is the source of truth for what is
    # callable. Even under platform-default (empty allowlist), a model id that
    # is not an active registered model (active provider included) must fail
    # closed before any LLM call. Distinguishes "tenant-restricted" (above)
    # from "does not exist / disabled" (here) for operator triage.
    active_providers = [row for row in list_providers(db) if row.lifecycle_state == "active"]
    active_provider_ids = {row.id for row in active_providers}
    runtime_provider_ids = {row.id for row in active_providers if _provider_matches_runtime(row.provider_kind)}
    models_by_id = {row.id: row for row in list_models(db)}
    active_registered_ids = {
        row.id
        for row in models_by_id.values()
        if row.lifecycle_state == "active" and row.provider_id in active_provider_ids
    }
    if model_id not in active_registered_ids:
        logger.warning(
            "model_not_registered",
            extra={
                "tenantId": tenant.tenant_id,
                "modelId": model_id,
            },
        )
        raise HTTPException(
            status_code=403,
            detail={
                "code": "model_not_registered",
                "message": f"Model '{model_id}' is not an active registered model.",
            },
        )

    model = models_by_id[model_id]
    if model.provider_id not in runtime_provider_ids:
        logger.warning(
            "model_provider_unavailable",
            extra={
                "tenantId": tenant.tenant_id,
                "modelId": model_id,
                "providerId": model.provider_id,
                "runtimeProviderKind": get_provider().provider_kind,
            },
        )
        raise HTTPException(
            status_code=503,
            detail={
                "code": "model_provider_unavailable",
                "message": "The model's registered provider is not available in this runtime.",
            },
        )


def _reject_unreviewed_text(document, allow_unreviewed_text: bool | None) -> None:
    """SEC-AI-SAFEMODE-01 (ADR-0068 D2=B): reject a document with unreviewed
    card text unless the caller explicitly requests relaxation AND the profile
    permits it. None (unspecified) is fail-closed — the request is rejected."""
    if allow_unreviewed_text is True and settings.allow_unreviewed_ai_text:
        return
    if any(card.textReviewed is not True for card in document.cards):
        raise HTTPException(
            status_code=422,
            detail={
                "code": "unreviewed_text_not_allowed",
                "message": "Document contains unreviewed card text, which cannot be sent to the LLM under SafeMode.",
            },
        )


def _reject_unreviewed_cards(cards, allow_unreviewed_text: bool | None) -> None:
    """SEC-AI-SAFEMODE-02: the no-document AI routes take card text directly, so
    the review state travels with the request (`textReviewed`). Reject any card
    whose text is not certified reviewed unless the caller explicitly requests
    relaxation AND the profile permits it. Defaults False (fail-closed), so an
    unspecified `textReviewed` is treated as unreviewed — the request is
    rejected — matching ADR-0068 D3=A (unspecified = SafeMode ON)."""
    if allow_unreviewed_text is True and settings.allow_unreviewed_ai_text:
        return
    if any(getattr(card, "textReviewed", False) is not True for card in cards):
        raise HTTPException(
            status_code=422,
            detail={
                "code": "unreviewed_text_not_allowed",
                "message": "Request contains unreviewed card text, which cannot be sent to the LLM under SafeMode.",
            },
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
            # kj_technique.md §5: the A/B cross-check must run in BOTH directions,
            # and the report must carry per-direction counts (報告は件数で).
            "Perform the A/B cross-check in both directions (kj_technique.md §5):",
            '  - direction "b_missing_in_a": narrative claims that have no counterpart in the diagram (either remove the claim or add it to the diagram).',
            '  - direction "a_missing_in_b": diagram islands that the narrative never mentions (ask why they cannot be told).',
            'Every A/B mismatch issue must set its "direction" to one of the two values.',
            'Report "counts" with the number of issues per direction (0 is a valid value; a 0/0 means the cross-check did not actually run).',
            'If there are no issues at all, return {"issues":[],"counts":{"bMissingInA":0,"aMissingInB":0}}.',
            "Use this exact schema:",
            '{"issues":[{"severity":"info|warn|error","message":string,"references":[{"id":string,"kind":"card|island"}]?,"direction":"b_missing_in_a|a_missing_in_b"?}],"counts":{"bMissingInA":number,"aMissingInB":number}?}',
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

    # 戻し検査 (kj_technique.md §3, 優先3-3): cards that OBJECTED to the previous
    # placard carry critiqueTags not_the_same / feels_off (recorded via the UI's
    # card critique-tag controls). The re-suggestion must address each objection.
    objecting_cards = [
        card
        for card in member_cards
        if card.critiqueTags
        and any(tag in card.critiqueTags for tag in ("not_the_same", "feels_off"))
    ]

    lines = [
        "You write the placard (表札) for this island as a draft island summary.",
        "Use only the direct member cards provided below. Ignore nested islands for this MVP.",
        "Do not add facts beyond the card texts.",
        # ai_kj_execution_procedures.md §3: the summaryText is advocacy for the
        # island (代弁), not a classification name; never a noun-phrase stop.
        "summaryText must be a predicate-bearing advocacy sentence (述語を伴う代弁文), never a classification name (分類名) or noun-phrase stop (名詞止め).",
        # 表札検査: transposition check + return check (kj_technique.md §3).
        "Perform the placard checks before answering:",
        "  1. Transposition: if you placed this placard on a DIFFERENT island, would it still hold? If yes, it is a classification name — fail and rewrite.",
        "  2. Return check: read the placard back to each member card — 'is this what you meant to say?'. If even one card says 'no', rewrite.",
    ]
    if objecting_cards:
        objecting_lines = [f'    - id="{card.id}", text={json.dumps(card.text)}' for card in objecting_cards]
        lines.extend(
            [
                "The following member cards OBJECTED to the previous placard (戻し検査):",
                *objecting_lines,
                "The new placard must address why each objecting card disagrees, or the summary is not a true advocacy for the island.",
            ]
        )
    # ADR-0069: the placard should reflect the island's position in the logical
    # structure — its typed relations to OTHER islands (causal / negation / ...).
    island_relations: list[str] = []
    for edge in payload.doc.edges:
        if edge.fromKind != "island" or edge.toKind != "island":
            continue
        if edge.fromId == island.id:
            island_relations.append(f'this island --{edge.type}--> island "{edge.toId}"')
        elif edge.toId == island.id:
            island_relations.append(f'island "{edge.fromId}" --{edge.type}--> this island')
    lines.extend(
        [
            "If evidence is weak, sparse, or contradictory, include warnings.",
            "Return strict JSON only. No markdown. No extra text.",
            "Use this exact schema:",
            '{"summaryText":string,"groundingIds":[string,...],"warnings":[string,...]?}',
            "groundingIds must contain 1-10 unique card ids chosen from the input cards.",
            "Prefer the strongest supporting card ids.",
            f'Island id="{island.id}", title={json.dumps(island.title or "")}',
            "Relations to other islands (the placard may reflect them):",
            *(island_relations or ["- (none)"]),
            "Member cards:",
            *card_lines,
        ]
    )
    return "\n".join(lines)


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

    # ADR-0069 (D2=A): the narrative's spine is the logical structure — pass the
    # typed relations (edges + evidenceLinks) so the draft uses the causal /
    # contradiction vocabulary instead of inventing it.
    relation_lines: list[str] = []
    for edge in payload.doc.edges:
        if edge.fromKind == "island" and edge.toKind == "island":
            relation_lines.append(
                f'island "{edge.fromId}" --{edge.type}--> island "{edge.toId}"'
            )
    for link in payload.doc.evidenceLinks or []:
        relation_lines.append(
            f'card "{link.fromCardId}" --evidence:{link.type}--> card "{link.toCardId}"'
        )

    return "\n".join(
        [
            "You generate a narrative draft from diagram reading order.",
            "This is advisory only. Do not claim facts, truth, or certainty.",
            "Every statement must be phrased as interpretation or possibility based on the diagram.",
            "Use reading order as the narrative spine. Follow the order exactly.",
            "For each reading-order item, describe what it appears to contain and what it might mean.",
            "Explicitly label the output as draft and unreviewed.",
            "Use the typed relations below as the logical skeleton (causal, negation, evidence).",
            "Logical relations:",
            *(relation_lines or ["- (none)"]),
            # ai_kj_execution_procedures.md §7: self-perform the A/B照合 and report
            # the mismatches as warnings so the 3+ threshold can be evaluated.
            "Self-perform the A/B cross-check (kj_technique.md §5) and report each mismatch as a warning:",
            "  - 'b_missing_in_a': a statement in the narrative with no counterpart in the diagram.",
            "  - 'a_missing_in_b': a diagram island that the narrative never mentions.",
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


class AvailableModelItem(BaseModel):
    id: str
    displayName: str
    providerId: str
    capabilities: str | None = None


class AvailableModelsResponse(BaseModel):
    models: list[AvailableModelItem]
    unavailableReason: Literal[
        "no_active_models",
        "provider_unavailable",
        "tenant_policy_excludes_all",
        "no_user_selectable_models",
    ] | None = None


def _is_user_selectable_model(capabilities: str | None) -> bool:
    """AI-MODEL-GOVERNANCE-01 MMR-04: a model is user-selectable for the D5
    per-operation selectors only if it serves an intermediate/generate tier.
    final_judgement-only models (check_narrative / detect_contradiction etc.) are
    fixed by admin policy and must NOT be offered for user selection."""
    if not capabilities:
        return True
    lower = capabilities.strip().lower()
    if "intermediate" in lower or "generate" in lower:
        return True
    if "final_judgement" in lower:
        return False
    return True


@router.get(
    "/available-models",
    response_model=AvailableModelsResponse,
    dependencies=[Depends(require_tenant_scoped_api_precondition)],
)
def get_available_models(request: Request, db: Session = Depends(get_db)) -> AvailableModelsResponse:
    """AI-MODEL-GOVERNANCE-01 R2: the active registered models this tenant is
    allowed to use (registry active models intersected with the tenant allowlist;
    empty allowlist = platform-default = all active registered models). The UI
    model selector offers exactly this set -- user-selectable (intermediate/
    generate) models only, never final_judgement-only ones (MMR-04) and never
    disabled models or provider secrets."""
    from kj_atlas_api.model_registry_repository import (
        list_models,
        list_providers,
        tenant_allowlist_effective_model_ids,
    )

    tenant = _resolve_audit_tenant(request, db)
    active_models = [row for row in list_models(db) if row.lifecycle_state == "active"]
    active_provider_ids = {
        row.id
        for row in list_providers(db)
        if row.lifecycle_state == "active" and _provider_matches_runtime(row.provider_kind)
    }
    effective = tenant_allowlist_effective_model_ids(db, tenant_id=tenant.tenant_id)
    runtime_models = [row for row in active_models if row.provider_id in active_provider_ids]
    allowed = runtime_models
    if effective is not None:
        allowed = [row for row in allowed if row.id in effective]
    selectable = [row for row in allowed if _is_user_selectable_model(row.capabilities)]

    unavailable_reason = None
    if not active_models:
        unavailable_reason = "no_active_models"
    elif not runtime_models:
        unavailable_reason = "provider_unavailable"
    elif effective is not None and not allowed:
        unavailable_reason = "tenant_policy_excludes_all"
    elif not selectable:
        unavailable_reason = "no_user_selectable_models"

    return AvailableModelsResponse(
        models=[
            AvailableModelItem(
                id=row.id,
                displayName=row.display_name,
                providerId=row.provider_id,
                capabilities=row.capabilities,
            )
            for row in selectable
        ],
        unavailableReason=unavailable_reason,
    )


@router.get("/provider-status", response_model=ProviderStatusResponse)
def get_provider_status() -> ProviderStatusResponse:
    """PROV-VIS-01 (ADR-0050 D1): read-only echo of the configured provider
    kind for display in the View panel. No connectivity check is performed;
    "last known outcome" is tracked client-side from real AI-call results.
    OPS-LLM-COST-01 (段階2): also reports the in-process LLM call counts."""
    from kj_atlas_api.llm.provider import llm_call_counts, llm_token_usage

    return ProviderStatusResponse(
        providerKind=get_provider().provider_kind,
        callCounts=llm_call_counts(),
        tokenUsage=llm_token_usage(),
    )


@router.post(
    "/suggest-layout",
    response_model=SuggestLayoutResponse,
    dependencies=[Depends(require_tenant_scoped_api_precondition)],
)
def suggest_layout(payload: SuggestLayoutRequest, request: Request, db: Session = Depends(get_db)) -> SuggestLayoutResponse:
    _reject_unreviewed_text(payload.doc, payload.allowUnreviewedText)
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
    return SuggestMergesResponse(suggestions=suggestions)


@router.post(
    "/suggest-island-summary",
    response_model=SuggestIslandSummaryResponse,
    dependencies=[Depends(require_tenant_scoped_api_precondition)],
)
def suggest_island_summary(payload: SuggestIslandSummaryRequest, request: Request, db: Session = Depends(get_db)) -> SuggestIslandSummaryResponse:
    _reject_unreviewed_text(payload.doc, payload.allowUnreviewedText)
    _assert_model_allowed(request, db, payload.model or resolve_model_for_task("suggest_island_summary"))
    try:
        llm_response = generate_with_fallback(
            LLMRequest(
                task="suggest_island_summary",
                prompt=_build_island_summary_prompt(payload),
                model=payload.model,
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
        SuggestIslandSummaryRequest(
            doc=payload.doc,
            islandId=payload.islandId,
            allowUnreviewedText=payload.allowUnreviewedText,
            model=payload.model,
        ),
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


def _build_opposing_viewpoint_prompt(payload: ProposeOpposingViewpointRequest) -> str:
    """AI-OPPOSE-01 (M4): prompt the model to propose an opposing viewpoint or
    evidence gap for a target card, using the doc's contradiction / evidence
    structure. proposal-only -- the model never decides; the human does."""
    target = next((card for card in payload.doc.cards if card.id == payload.targetCardId), None)
    if target is None:
        raise HTTPException(status_code=422, detail="targetCardId does not exist")
    card_lines = "\n".join(f'  - id="{card.id}", text={json.dumps(card.text)}' for card in payload.doc.cards)
    evidence_lines = "\n".join(
        f'  - source "{link.fromCardId}" --{link.type}--> target "{link.toCardId}"'
        for link in payload.doc.evidenceLinks or []
    ) or "- (none)"
    return "\n".join(
        [
            "You propose an OPPOSING viewpoint or an evidence-gap note for the target card.",
            "Use only the provided cards and evidence links. Do not add outside facts.",
            "The proposal is a candidate for human review -- it is never applied automatically.",
            "Ground every claim in the card text. If the target's evidence is missing or weak, set evidenceGap=true.",
            'Return strict JSON only: {"opposingText": string, "evidenceGap": boolean, "rationale": string, "warnings": [string,...]}',
            f"Target card: {json.dumps({'id': target.id, 'text': target.text})}",
            "Cards:",
            card_lines,
            "Evidence links:",
            evidence_lines,
        ]
    )


@router.post(
    "/proposals/opposing-viewpoint",
    response_model=OpposingViewpointProposal,
    dependencies=[Depends(require_tenant_scoped_api_precondition)],
)
def propose_opposing_viewpoint(
    payload: ProposeOpposingViewpointRequest,
    request: Request,
    db: Session = Depends(get_db),
) -> OpposingViewpointProposal:
    """AI-OPPOSE-01 (M4): proposal-only opposing-viewpoint / evidence-gap
    proposal for a target card, derived from the doc's contradiction and
    evidence structure. Never auto-applied (status stays "proposed")."""
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
    if next((card for card in payload.doc.cards if card.id == payload.targetCardId), None) is None:
        raise HTTPException(status_code=422, detail="targetCardId does not exist")
    _reject_unreviewed_text(payload.doc, payload.allowUnreviewedText)
    _assert_model_allowed(request, db, payload.model or resolve_model_for_task("propose_opposing_viewpoint"))

    try:
        llm_response = generate_with_fallback(
            LLMRequest(
                task="propose_opposing_viewpoint",
                prompt=_build_opposing_viewpoint_prompt(payload),
                model=payload.model,
            )
        )
    except ProviderDisabledError as exc:
        _raise_llm_http_error(exc)
    except ProviderRequestError as exc:
        _raise_llm_http_error(exc)

    try:
        data = json.loads(llm_response.raw_text)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=422, detail="LLM response is not valid JSON") from exc
    proposal = OpposingViewpointProposal(
        proposalId=f"proposal-{uuid4()}",
        targetCardId=payload.targetCardId,
        opposingText=str(data.get("opposingText", data.get("opposing_text", ""))),
        evidenceGap=bool(data.get("evidenceGap", data.get("evidence_gap", False))),
        rationale=str(data.get("rationale", "")),
        warnings=[str(w) for w in (data.get("warnings") or [])],
    )
    if not proposal.opposingText:
        raise HTTPException(status_code=422, detail="LLM response missing opposingText")
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


@router.get(
    "/proposals/status",
    response_model=ProposalStatusResponse,
    dependencies=[Depends(require_tenant_scoped_api_precondition)],
)
def get_proposal_status(
    docId: str,
    request: Request,
    db: Session = Depends(get_db),
) -> ProposalStatusResponse:
    """CE4 read-only proposal lifecycle status for a document.

    Lets a generative-AI (via MCP or API) verify that a proposal is still
    proposal-only or was decided by a human (accepted/rejected/held) --
    traceability without mutating anything. Read-only by contract
    (`action="read"`): no proposal or decision is written here.
    """
    _, _, tenant = _authorize_request(
        request,
        db,
        action="read",
        doc_id=docId,
        safe_mode=False,
        read_only=True,
    )
    proposals = (
        db.query(AIProposalRow)
        .filter_by(tenant_id=tenant.tenant_id, doc_id=docId)
        .order_by(AIProposalRow.created_at.asc(), AIProposalRow.proposal_id.asc())
        .all()
    )
    decisions = {
        row.proposal_id: row
        for row in db.query(AIProposalDecisionStateRow)
        .filter_by(tenant_id=tenant.tenant_id, doc_id=docId)
        .all()
    }
    return ProposalStatusResponse(
        docId=docId,
        proposals=[
            ProposalStatusItem(
                proposalId=row.proposal_id,
                proposalKind=row.proposal_kind,
                origin=row.origin,
                status=decisions[row.proposal_id].status if row.proposal_id in decisions else "proposed",
                sourceBundleHash=row.source_bundle_hash,
                createdAt=row.created_at,
                decidedAt=decisions[row.proposal_id].updated_at if row.proposal_id in decisions else None,
            )
            for row in proposals
        ],
    )


@router.post(
    "/generate-narrative",
    response_model=GenerateNarrativeResponse,
    dependencies=[Depends(require_tenant_scoped_api_precondition)],
)
def generate_narrative(payload: GenerateNarrativeRequest, request: Request, db: Session = Depends(get_db)) -> GenerateNarrativeResponse:
    _reject_unreviewed_text(payload.doc, payload.allowUnreviewedText)
    _assert_model_allowed(request, db, payload.model or resolve_model_for_task("generate_narrative"))
    try:
        llm_response = generate_with_fallback(
            LLMRequest(
                task="generate_narrative",
                prompt=_build_generate_narrative_prompt(payload),
                model=payload.model,
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
    _reject_unreviewed_text(payload.doc, payload.allowUnreviewedText)

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
        # ai_kj_execution_procedures.md §1: 名詞止め禁止 — a card must be a
        # predicate-bearing sentence, never a bare noun-phrase stop.
        f"Output must be a predicate-bearing sentence (動詞で終わる文), never a noun-phrase stop (名詞止め). "
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
        # ai_kj_execution_procedures.md §2: bundle by the similarity of what the
        # cards are APPEALING for (訴えの類似性), not by classification; first
        # level bundles are 2-3 cards (rarely 4); never force a lone card in.
        f"Group these KJ-method cards into islands. "
        f"Bundle cards by the similarity of what they are appealing for, not by classification labels. "
        f"Each first-level bundle is 2-3 cards (rarely 4). Do not force a card into a bundle it does not belong to. "
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
    _assert_model_allowed(request, db, payload.model or resolve_model_for_task("refine_card_text"))
    _reject_unreviewed_cards([payload], payload.allowUnreviewedText)
    try:
        llm_response = generate_with_fallback(
            LLMRequest(
                task="refine_card_text",
                prompt=_build_refine_card_text_prompt(payload),
                model=payload.model,
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
    _assert_model_allowed(request, db, payload.model or resolve_model_for_task("suggest_card_groups"))
    _reject_unreviewed_cards(payload.cards, payload.allowUnreviewedText)
    try:
        llm_response = generate_with_fallback(
            LLMRequest(
                task="suggest_card_groups",
                prompt=_build_suggest_card_groups_prompt(payload),
                model=payload.model,
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
    _reject_unreviewed_cards([payload.cardA, payload.cardB], payload.allowUnreviewedText)
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
    _assert_model_allowed(request, db, payload.model or resolve_model_for_task("suggest_document_title"))
    _reject_unreviewed_cards([payload], payload.allowUnreviewedText)
    try:
        llm_response = generate_with_fallback(
            LLMRequest(
                task="suggest_document_title",
                prompt=_build_suggest_document_title_prompt(payload),
                temperature=0.4,
                max_tokens=300,
                model=payload.model,
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
