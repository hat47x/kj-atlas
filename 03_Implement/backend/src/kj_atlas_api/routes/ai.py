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
from kj_atlas_api.models import (
    Card,
    MergeSuggestion,
    SuggestLayoutRequest,
    SuggestLayoutResponse,
    SuggestMergesRequest,
    SuggestMergesResponse,
    Transform,
)
from kj_atlas_api.models_ai import (
    GenerateNarrativeRequest,
    GenerateNarrativeResponse,
    LLMNarrativeResponse,
)

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


def _build_narrative_prompt(payload: GenerateNarrativeRequest) -> str:
    cards_by_id = {card.id: card for card in payload.doc.cards}
    islands_by_id = {island.id: island for island in payload.doc.islands}

    reading_order_lines: list[str] = []
    for index, entry_id in enumerate(payload.doc.readingOrder or [], start=1):
        card = cards_by_id.get(entry_id)
        if card is not None:
            reading_order_lines.append(f'{index}. card id="{card.id}" text={json.dumps(card.text)}')
            continue

        island = islands_by_id.get(entry_id)
        if island is not None:
            island_cards = [cards_by_id[card_id] for card_id in island.cardIds if card_id in cards_by_id]
            island_card_summaries = [json.dumps(island_card.text) for island_card in island_cards]
            reading_order_lines.append(
                (
                    f'{index}. island id="{island.id}" title={json.dumps(island.title or "")} '
                    f'containsCardIds={json.dumps(island.cardIds)} containsCardTexts={json.dumps(island_card_summaries)}'
                )
            )
            continue

        reading_order_lines.append(f'{index}. unknown id="{entry_id}"')

    narrative_title = payload.narrativeTitle.strip() if payload.narrativeTitle else "Untitled Draft Narrative"

    return "\n".join(
        [
            "You generate a draft narrative from a diagram reading order.",
            "This is unreviewed draft support text only.",
            "Do not present any claim as established fact.",
            "Use phrases such as 'may suggest', 'appears to indicate', or 'could mean'.",
            "Follow readingOrder strictly as the spine. Keep the same order.",
            "For each readingOrder item, mention what it contains and what it may mean.",
            "Include an explicit unreviewed disclaimer in text.",
            "Return JSON only, no markdown, no extra keys.",
            "Use this exact schema:",
            '{"text":string,"basedOnReadingOrder":[string,...],"warnings":[string,...]?}',
            f"Narrative title: {json.dumps(narrative_title)}",
            "Reading order items:",
            *reading_order_lines,
        ]
    )


def _parse_narrative_response(raw_text: str, source_doc: GenerateNarrativeRequest) -> GenerateNarrativeResponse:
    try:
        parsed = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=422, detail="LLM response is not valid JSON") from exc

    if not isinstance(parsed, dict):
        raise HTTPException(status_code=422, detail="LLM response must be a JSON object")

    try:
        response = LLMNarrativeResponse.model_validate(parsed)
    except Exception as exc:
        raise HTTPException(status_code=422, detail="Invalid narrative response payload") from exc

    source_reading_order = source_doc.doc.readingOrder or []
    if response.basedOnReadingOrder != source_reading_order:
        raise HTTPException(status_code=422, detail="Narrative basedOnReadingOrder must exactly match input readingOrder")

    if "unreviewed" not in response.text.lower() and "draft" not in response.text.lower():
        raise HTTPException(status_code=422, detail="Narrative text must explicitly indicate draft/unreviewed status")

    return GenerateNarrativeResponse(
        text=response.text,
        basedOnReadingOrder=response.basedOnReadingOrder,
        warnings=response.warnings,
    )


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


@router.post("/suggest-merges", response_model=SuggestMergesResponse)
def suggest_merges(payload: SuggestMergesRequest) -> SuggestMergesResponse:
    provider = get_provider()
    try:
        llm_response = provider.generate(
            LLMRequest(
                task="suggest_merges",
                prompt=_build_merge_prompt(payload),
            )
        )
    except ProviderDisabledError as exc:
        raise HTTPException(status_code=501, detail=str(exc)) from exc
    except ProviderRequestError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    suggestions = _parse_merge_suggestions(llm_response.raw_text, payload)
    return SuggestMergesResponse(suggestions=suggestions)


@router.post("/generate-narrative", response_model=GenerateNarrativeResponse)
def generate_narrative(payload: GenerateNarrativeRequest) -> GenerateNarrativeResponse:
    provider = get_provider()
    try:
        llm_response = provider.generate(
            LLMRequest(
                task="generate_narrative",
                prompt=_build_narrative_prompt(payload),
            )
        )
    except ProviderDisabledError as exc:
        raise HTTPException(status_code=501, detail=str(exc)) from exc
    except ProviderRequestError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return _parse_narrative_response(llm_response.raw_text, payload)
