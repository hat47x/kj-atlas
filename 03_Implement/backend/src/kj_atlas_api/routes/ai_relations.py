import json
import logging

from fastapi import APIRouter, Depends, HTTPException

from kj_atlas_api.llm.provider import (
    LLMRequest,
    ProviderDisabledError,
    ProviderRequestError,
    build_audit_fields,
    generate_with_fallback,
)
from kj_atlas_api.models_ai import SummarizeIslandRelationRequest, SummarizeIslandRelationResponse
from kj_atlas_api.tenant_session_precondition import (
    require_tenant_scoped_api_precondition,
)

router = APIRouter(prefix="/ai", tags=["ai"])
logger = logging.getLogger(__name__)


def _raise_llm_http_error(exc: ProviderDisabledError | ProviderRequestError) -> None:
    if isinstance(exc, ProviderDisabledError):
        raise HTTPException(status_code=503, detail=exc.to_contract()) from exc

    status_map = {
        "provider_timeout": 504,
        "provider_validation": 422,
        "provider_unavailable": 503,
    }
    raise HTTPException(status_code=status_map.get(exc.code, 503), detail=exc.to_contract()) from exc


def _validate_relation_summary_input(payload: SummarizeIslandRelationRequest) -> None:
    island_ids = {island.id for island in payload.doc.islands}
    if payload.islandAId not in island_ids or payload.islandBId not in island_ids:
        raise HTTPException(status_code=422, detail="islandAId/islandBId must exist in document islands")

    doc_card_ids = {card.id for card in payload.doc.cards}
    unknown_grounding_cards = [card_id for card_id in payload.groundingCardIds if card_id not in doc_card_ids]
    if unknown_grounding_cards:
        raise HTTPException(status_code=422, detail="groundingCardIds must exist in document cards")

    doc_edge_ids = {edge.id for edge in payload.doc.edges}
    unknown_grounding_edges = [edge_id for edge_id in payload.groundingEdgeIds if edge_id not in doc_edge_ids]
    if unknown_grounding_edges:
        raise HTTPException(status_code=422, detail="groundingEdgeIds must exist in document edges")

    provided_card_text_ids = {item.id for item in payload.cardTexts}
    missing_grounding_cards = [card_id for card_id in payload.groundingCardIds if card_id not in provided_card_text_ids]
    if missing_grounding_cards:
        raise HTTPException(status_code=422, detail="cardTexts must include all groundingCardIds")


def _build_relation_summary_prompt(payload: SummarizeIslandRelationRequest) -> str:
    edge_texts = payload.edgeTexts or []
    card_lines = [f'- id="{item.id}", text={json.dumps(item.text)}' for item in payload.cardTexts]
    edge_lines = [
        f'- edgeId="{item.edgeId}", type="{item.type}", from="{item.from_}", to="{item.to}"' for item in edge_texts
    ]

    return "\n".join(
        [
            "You generate an island relation summary draft.",
            "Never present the output as authoritative or certain.",
            "Use neutral wording and explicitly state uncertainty when evidence is weak or contradictory.",
            "Use ONLY the provided cardTexts and edgeTexts.",
            "Avoid factual claims not present in provided texts.",
            "If context is missing, add a warning that context may be incomplete.",
            "If you detect contradictions, add warning messages.",
            "If the summary appears to include unsupported claims, add warning messages.",
            "Return strict JSON only. No markdown. No extra keys.",
            "Use this exact schema:",
            '{"text":string,"groundingCardIds":[string,...],"groundingEdgeIds":[string,...],"warnings":[string,...]}',
            "groundingCardIds must be a subset of allowed groundingCardIds.",
            "groundingEdgeIds must be a subset of allowed groundingEdgeIds.",
            f'islandAId="{payload.islandAId}", islandBId="{payload.islandBId}", relationType="{payload.relationType}", derived={str(payload.derived).lower()}',
            f"allowed groundingCardIds={json.dumps(payload.groundingCardIds)}",
            f"allowed groundingEdgeIds={json.dumps(payload.groundingEdgeIds)}",
            "cardTexts:",
            *(card_lines or ["- (none)"]),
            "edgeTexts:",
            *(edge_lines or ["- (none)"]),
        ]
    )


def _parse_relation_summary_response(
    raw_text: str, source_payload: SummarizeIslandRelationRequest
) -> SummarizeIslandRelationResponse:
    try:
        parsed = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=422, detail="LLM response is not valid JSON") from exc

    if not isinstance(parsed, dict):
        raise HTTPException(status_code=422, detail="LLM response must be a JSON object")

    try:
        response = SummarizeIslandRelationResponse.model_validate(parsed)
    except Exception as exc:
        raise HTTPException(status_code=422, detail="Invalid relation summary response payload") from exc

    if response.text.strip() == "":
        raise HTTPException(status_code=422, detail="Summary text must not be empty")

    allowed_card_ids = set(source_payload.groundingCardIds)
    if any(card_id not in allowed_card_ids for card_id in response.groundingCardIds):
        raise HTTPException(status_code=422, detail="LLM response groundingCardIds must be a subset of input groundingCardIds")

    allowed_edge_ids = set(source_payload.groundingEdgeIds)
    if any(edge_id not in allowed_edge_ids for edge_id in response.groundingEdgeIds):
        raise HTTPException(status_code=422, detail="LLM response groundingEdgeIds must be a subset of input groundingEdgeIds")

    return response


@router.post(
    "/summarize-island-relation",
    response_model=SummarizeIslandRelationResponse,
    dependencies=[Depends(require_tenant_scoped_api_precondition)],
)
def summarize_island_relation(payload: SummarizeIslandRelationRequest) -> SummarizeIslandRelationResponse:
    _validate_relation_summary_input(payload)

    try:
        llm_response = generate_with_fallback(
            LLMRequest(task="summarize_island_relation", prompt=_build_relation_summary_prompt(payload))
        )
    except ProviderDisabledError as exc:
        _raise_llm_http_error(exc)
    except ProviderRequestError as exc:
        _raise_llm_http_error(exc)

    logger.info(
        "llm_generate",
        extra={"task": "summarize_island_relation", **build_audit_fields(llm_response)},
    )

    return _parse_relation_summary_response(llm_response.raw_text, payload)
