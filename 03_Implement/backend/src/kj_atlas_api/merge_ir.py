"""Route-specific input projection for ``POST /ai/suggest-merges``.

The generic document IR remains the normalization / SafeMode / structural
projection layer.  Merge judgement needs a few additional semantics that do
not belong in the generic IR schema: claim type, island membership, provenance
identity, and existing representation lineage.  This module adds only that
route-local context and never sends raw ``Card.sources`` strings to a provider.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, replace
from typing import Any

from kj_atlas_api.llm_input_ir import (
    IRGenerationError,
    IRSource,
    build_llm_input_ir,
    source_from_document,
)
from kj_atlas_api.models import SuggestMergesRequest


MERGE_INPUT_CONTRACT = "suggest_merges_v1"


@dataclass(frozen=True)
class MergeIRContext:
    document_ir: dict[str, Any]
    merge_cards: tuple[dict[str, Any], ...]
    document_eligible_card_count: int
    projected_card_count: int

    @property
    def partial_scope(self) -> bool:
        return self.projected_card_count < self.document_eligible_card_count

    def provider_inputs(self) -> dict[str, Any]:
        """The auditable input-of-record corresponding to the rendered prompt.

        ``source_refs`` below are opaque request-local aliases.  The reverse
        mapping to raw ``Card.sources`` values is deliberately not serialized.
        """
        return {
            "input_contract": MERGE_INPUT_CONTRACT,
            "document_ir": self.document_ir,
            "merge_cards": [dict(item) for item in self.merge_cards],
            "scope": {
                "document_eligible_card_count": self.document_eligible_card_count,
                "projected_card_count": self.projected_card_count,
                "partial": self.partial_scope,
                "reason_codes": ["MAX_CARDS"] if self.partial_scope else [],
            },
        }


def _eligible_card_ids(payload: SuggestMergesRequest) -> frozenset[str]:
    return frozenset(
        card.id
        for card in payload.doc.cards
        if card.holdState is None and not card.mergedIntoCardId
    )


def _subset_source(source: IRSource, keep_ids: frozenset[str]) -> IRSource:
    """Keep a referentially closed card subgraph plus relevant island ancestry."""
    cards = tuple(card for card in source.cards if card.id in keep_ids)
    relations = tuple(
        relation
        for relation in source.relations
        if relation.from_id in keep_ids and relation.to_id in keep_ids
    )
    evidence_links = tuple(
        link
        for link in source.evidence_links
        if link.from_card_id in keep_ids and link.to_card_id in keep_ids
    )

    island_by_id = {island.id: island for island in source.islands}
    relevant_island_ids = {
        island.id for island in source.islands if any(card_id in keep_ids for card_id in island.card_ids)
    }
    frontier = list(relevant_island_ids)
    while frontier:
        island = island_by_id.get(frontier.pop())
        if island is None or island.parent_island_id is None:
            continue
        parent_id = island.parent_island_id
        if parent_id in island_by_id and parent_id not in relevant_island_ids:
            relevant_island_ids.add(parent_id)
            frontier.append(parent_id)

    islands = tuple(
        replace(
            island,
            card_ids=tuple(card_id for card_id in island.card_ids if card_id in keep_ids),
            placard_card_id=(
                island.placard_card_id if island.placard_card_id in keep_ids else None
            ),
        )
        for island in source.islands
        if island.id in relevant_island_ids
    )

    return IRSource(
        doc_id=source.doc_id,
        doc_version=source.doc_version,
        cards=cards,
        relations=relations,
        islands=islands,
        evidence_links=evidence_links,
        created_at=source.created_at,
        updated_at=source.updated_at,
    )


def _opaque_source_refs(payload: SuggestMergesRequest, card_ids: frozenset[str]) -> dict[str, tuple[str, ...]]:
    """Preserve only source identity equality, never raw source values.

    Aliases are deterministic inside one request/document.  Their numbering has
    no semantic meaning and there is intentionally no reverse mapping in the
    returned context.
    """
    cards = sorted((card for card in payload.doc.cards if card.id in card_ids), key=lambda c: c.id)
    alias_by_source: dict[str, str] = {}
    next_index = 1
    refs_by_card: dict[str, tuple[str, ...]] = {}
    for card in cards:
        refs: list[str] = []
        for source in card.sources:
            alias = alias_by_source.get(source)
            if alias is None:
                alias = f"src-{next_index:04d}"
                alias_by_source[source] = alias
                next_index += 1
            if alias not in refs:
                refs.append(alias)
        refs_by_card[card.id] = tuple(refs)
    return refs_by_card


def _island_ids_by_card(payload: SuggestMergesRequest, card_ids: frozenset[str]) -> dict[str, tuple[str, ...]]:
    result: dict[str, list[str]] = {card_id: [] for card_id in card_ids}
    for island in payload.doc.islands:
        for card_id in island.cardIds:
            if card_id in result and island.id not in result[card_id]:
                result[card_id].append(island.id)
    return {card_id: tuple(ids) for card_id, ids in result.items()}


def build_merge_ir_context(
    payload: SuggestMergesRequest,
    *,
    allow_unreviewed_text: bool,
) -> MergeIRContext:
    """Build the merge candidate window and fail closed on meaning loss.

    Documents larger than the generic IR card budget are deliberately evaluated
    as a deterministic candidate window.  That scope reduction is explicit in
    ``provider_inputs().scope``.  Once the window is chosen, every selected card
    becomes route-required; text or relation truncation is no longer acceptable.
    """
    eligible_ids = _eligible_card_ids(payload)
    if len(eligible_ids) < 2:
        raise IRGenerationError(
            "insufficient_merge_candidates",
            "At least two eligible cards are required before merge suggestions can be requested.",
        )

    source = source_from_document(payload.doc)
    eligible_source = _subset_source(source, eligible_ids)

    discovery_ir = build_llm_input_ir(
        eligible_source,
        include_coordinates=False,
        safe_mode=True,
        allow_unreviewed_text=allow_unreviewed_text,
    )
    projected_ids = frozenset(item["id"] for item in discovery_ir.get("cards", []))
    if len(projected_ids) < 2:
        raise IRGenerationError(
            "insufficient_merge_candidates",
            "The IR candidate window contains fewer than two merge-eligible cards.",
        )

    selected_source = _subset_source(eligible_source, projected_ids)
    final_ir = build_llm_input_ir(
        selected_source,
        include_coordinates=False,
        safe_mode=True,
        allow_unreviewed_text=allow_unreviewed_text,
        required_card_ids=tuple(sorted(projected_ids)),
    )
    reasons = set(final_ir.get("truncation", {}).get("reason_codes", []))
    if "MAX_TEXT_CHARS" in reasons:
        raise IRGenerationError(
            "required_text_truncated",
            "Task-required merge candidate text did not fit in the IR text budget.",
        )
    if "MAX_RELATIONS" in reasons:
        raise IRGenerationError(
            "required_relation_missing",
            "Task-required merge candidate relations did not fit in the IR relation budget.",
        )

    final_ids = frozenset(item["id"] for item in final_ir.get("cards", []))
    if final_ids != projected_ids:
        raise IRGenerationError(
            "required_card_context_mismatch",
            "Task-required merge candidate cards did not survive the final IR projection.",
        )

    card_by_id = {card.id: card for card in payload.doc.cards}
    source_refs = _opaque_source_refs(payload, projected_ids)
    island_ids = _island_ids_by_card(payload, projected_ids)
    merge_cards = tuple(
        {
            "id": card_id,
            "claim_type": card_by_id[card_id].claimType,
            "island_ids": list(island_ids.get(card_id, ())),
            "source_refs": list(source_refs.get(card_id, ())),
            "rep_of": card_by_id[card_id].repOf,
            "canonical_id": card_by_id[card_id].canonicalId,
        }
        for card_id in sorted(projected_ids)
    )

    return MergeIRContext(
        document_ir=final_ir,
        merge_cards=merge_cards,
        document_eligible_card_count=len(eligible_ids),
        projected_card_count=len(projected_ids),
    )


def merge_ir_prompt_lines(context: MergeIRContext) -> list[str]:
    """Render only normalized/projected document meaning into the provider prompt."""
    ir = context.document_ir
    meta_by_id = {item["id"]: item for item in context.merge_cards}
    lines = [
        "Merge input context (route-specific projection):",
        "Source refs are opaque request-local provenance aliases. They only show whether cards share a recorded source; they do not reveal source content.",
    ]
    if context.partial_scope:
        lines.append(
            "Scope warning: this is a deterministic candidate window, not the whole eligible document. Cards outside this window were not evaluated for merging."
        )

    lines.append("Candidate cards:")
    for card in ir.get("cards", []):
        meta = meta_by_id[card["id"]]
        lines.append(
            "- "
            + json.dumps(
                {
                    "id": card["id"],
                    "text": card["text"],
                    "claimType": meta["claim_type"],
                    "islandIds": meta["island_ids"],
                    "sourceRefs": meta["source_refs"],
                    "repOf": meta["rep_of"],
                    "canonicalId": meta["canonical_id"],
                },
                ensure_ascii=False,
                sort_keys=True,
            )
        )

    lines.append("Logical relations between candidate cards:")
    relation_lines = [
        f'- card "{item["from"]}" --{item["type"]}--> card "{item["to"]}"'
        for item in ir.get("relations", [])
    ]
    lines.extend(relation_lines or ["- (none)"])

    lines.append("Evidence links between candidate cards:")
    evidence_lines = []
    for item in ir.get("evidence_links", []):
        state = item.get("contradiction_state")
        suffix = f" (contradictionState={state})" if state else ""
        evidence_lines.append(
            f'- card "{item["from_card_id"]}" --evidence:{item["type"]}--> '
            f'card "{item["to_card_id"]}"{suffix}'
        )
    lines.extend(evidence_lines or ["- (none)"])
    return lines
