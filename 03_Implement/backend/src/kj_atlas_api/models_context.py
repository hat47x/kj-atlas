from __future__ import annotations

from hashlib import sha256
import json
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from kj_atlas_api.models import DocumentV2


class ContextQuery(BaseModel):
    model_config = ConfigDict(extra="forbid")

    queryId: str = Field(min_length=1)
    targetCardIds: list[str] = Field(min_length=1)
    depth: int = Field(ge=0, le=4)
    scope: Literal["selection", "document"]
    reviewedOnly: bool = True
    safeMode: bool = True


class ContextQueryValidationResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    query: ContextQuery
    preview: dict[str, object]


class ContextBundleRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    query: ContextQuery
    doc: DocumentV2


class ContextBundleCard(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    text: str | None = None
    reviewed: bool


class ContextBundle(BaseModel):
    model_config = ConfigDict(extra="forbid")

    queryId: str
    selectedCards: list[ContextBundleCard]
    excludedReasons: list[dict[str, str]]


class ContextBundleResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    bundle: ContextBundle
    bundleHash: str


def build_bundle(request: ContextBundleRequest) -> ContextBundleResponse:
    query = request.query
    cards = sorted(request.doc.cards, key=lambda item: item.id)
    include_ids = {card.id for card in cards} if query.scope == "document" else set(query.targetCardIds)

    selected_cards: list[ContextBundleCard] = []
    excluded: list[dict[str, str]] = []
    for card in cards:
        if card.id not in include_ids:
            continue

        reviewed = card.textReviewed is True
        if query.reviewedOnly and not reviewed:
            excluded.append({"cardId": card.id, "reason": "reviewed_only_filter"})
            continue

        text_value: str | None = card.text
        if query.safeMode and not reviewed:
            text_value = None
            excluded.append({"cardId": card.id, "reason": "safe_mode_unreviewed_text"})

        selected_cards.append(ContextBundleCard(id=card.id, text=text_value, reviewed=reviewed))

    excluded = sorted(excluded, key=lambda item: (item["cardId"], item["reason"]))
    bundle = ContextBundle(queryId=query.queryId, selectedCards=selected_cards, excludedReasons=excluded)

    canonical = json.dumps(bundle.model_dump(mode="json"), ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    bundle_hash = sha256(canonical.encode("utf-8")).hexdigest()
    return ContextBundleResponse(bundle=bundle, bundleHash=bundle_hash)
