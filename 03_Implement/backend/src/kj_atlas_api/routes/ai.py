import json
import math
from uuid import uuid4

from fastapi import APIRouter, HTTPException

from kj_atlas_api.llm.provider import (
    LLMRequest,
    ProviderDisabledError,
    ProviderRequestError,
    get_provider,
)
from kj_atlas_api.models import Card, SuggestLayoutRequest, SuggestLayoutResponse, Transform

router = APIRouter(prefix="/ai", tags=["ai"])


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


@router.post("/suggest-layout", response_model=SuggestLayoutResponse)
def suggest_layout(payload: SuggestLayoutRequest) -> SuggestLayoutResponse:
    provider = get_provider()
    try:
        llm_response = provider.generate(
            LLMRequest(
                task="re_layout",
                prompt=_build_prompt(payload),
            )
        )
    except ProviderDisabledError as exc:
        raise HTTPException(status_code=501, detail=str(exc)) from exc
    except ProviderRequestError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

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
