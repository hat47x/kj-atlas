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
    allowUnreviewedText: bool = False
    previewConfirmed: bool = False


class ContextQueryValidationResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    query: ContextQuery
    preview: dict[str, object]
    queryCanonicalHash: str


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
    queryCanonicalHash: str


def _canonical_bundle_hash_payload(bundle: ContextBundle) -> dict[str, object]:
    selected_cards = sorted(
        (card.model_dump(mode="json") for card in bundle.selectedCards),
        key=lambda item: item["id"],
    )
    excluded_reasons = sorted(
        bundle.excludedReasons,
        key=lambda item: (item["cardId"], item["reason"]),
    )
    return {
        "selectedCards": selected_cards,
        "excludedReasons": excluded_reasons,
    }


def _canonical_query_hash_payload(query: ContextQuery) -> dict[str, object]:
    return {
        "targetCardIds": sorted(set(query.targetCardIds)),
        "depth": query.depth,
        "scope": query.scope,
        "reviewedOnly": query.reviewedOnly,
        "safeMode": query.safeMode,
        "allowUnreviewedText": query.allowUnreviewedText,
    }


def _sha256_canonical(payload: dict[str, object]) -> str:
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return sha256(canonical.encode("utf-8")).hexdigest()


def build_bundle(request: ContextBundleRequest) -> ContextBundleResponse:
    query = request.query
    if query.safeMode and query.allowUnreviewedText:
        raise ValueError("allowUnreviewedText cannot be enabled when safeMode is true")
    if not query.previewConfirmed:
        raise ValueError("preview_required")

    query_hash = _sha256_canonical(_canonical_query_hash_payload(query))
    cards = sorted(request.doc.cards, key=lambda item: item.id)
    include_ids = {card.id for card in cards} if query.scope == "document" else set(query.targetCardIds)

    selected_cards: list[ContextBundleCard] = []
    excluded: list[dict[str, str]] = []
    for card in cards:
        if card.id not in include_ids:
            continue

        reviewed = card.textReviewed is True
        if query.reviewedOnly and not reviewed:
            excluded.append({"cardId": card.id, "reason": "unreviewed_filtered"})
            continue

        text_value: str | None = card.text
        if query.safeMode and not reviewed:
            text_value = None
            excluded.append({"cardId": card.id, "reason": "safe_mode_unreviewed_text"})

        selected_cards.append(ContextBundleCard(id=card.id, text=text_value, reviewed=reviewed))

    excluded = sorted(excluded, key=lambda item: (item["cardId"], item["reason"]))
    bundle = ContextBundle(queryId=query.queryId, selectedCards=selected_cards, excludedReasons=excluded)

    bundle_hash = _sha256_canonical(_canonical_bundle_hash_payload(bundle))
    return ContextBundleResponse(bundle=bundle, bundleHash=bundle_hash, queryCanonicalHash=query_hash)
