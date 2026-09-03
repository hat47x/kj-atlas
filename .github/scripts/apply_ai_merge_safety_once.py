from pathlib import Path
import re

AI = Path("03_Implement/backend/src/kj_atlas_api/routes/ai.py")
TEST = Path("03_Implement/backend/tests/test_ai_merge_semantics.py")

text = AI.read_text(encoding="utf-8")

new_prompt = r'''def _eligible_merge_cards(payload: SuggestMergesRequest):
    """Return cards that the AI is allowed to consider for a merge proposal.

    Hold state and an existing mergedIntoCardId are human/data decisions that
    must win over model similarity. The response parser repeats these checks as
    defense in depth in case a provider returns an id it was not shown.
    """
    return [
        card
        for card in payload.doc.cards
        if card.holdState is None and not card.mergedIntoCardId
    ]


def _build_merge_prompt(payload: SuggestMergesRequest) -> str:
    card_lines = [
        f'- id="{card.id}", text={json.dumps(card.text)}'
        for card in _eligible_merge_cards(payload)
    ]
    instruction = payload.instruction.strip() if payload.instruction else "No extra instruction"

    return "\n".join(
        [
            "You propose KJ-compatible card integrations. This is advisory only.",
            "Use one of two approaches when appropriate:",
            "- 04-step-like consolidation for near-duplicate cards whose material distinctions can all be retained.",
            "- kernel-fusion-style integration when several non-identical cards share a meaning kernel that can be stated without erasing their residual differences.",
            "Similarity alone is not enough. Sharing a topic or vocabulary is not enough.",
            "Before proposing, perform a Return check against every source card: would each source still recognise the draft as preserving what it says?",
            "Leave minority, lone, contradictory, held, or materially different cards separate.",
            "Do not invent provenance, conditions, certainty, or residual meaning that is not in the source cards.",
            "You must only propose suggestions. Do not apply merges, delete cards, or overwrite source cards.",
            "Return strict JSON only. No markdown. No explanation text outside JSON.",
            "Return at most 10 suggestions.",
            "Use this exact schema:",
            '{"suggestions":[{"groupId":string,"cardIds":[string,...],"mergedTextDraft":string,"rationale":string?}]}',
            "Each suggestion must include at least 2 cardIds.",
            "Only use card IDs from the input.",
            f"Instruction: {instruction}",
            "Cards eligible for integration consideration:",
            *(card_lines or ["- (none)"]),
        ]
    )'''

pattern = r"def _build_merge_prompt\(payload: SuggestMergesRequest\) -> str:\n.*?\n\ndef _parse_merge_suggestions"
replacement = new_prompt + "\n\n\ndef _parse_merge_suggestions"
text, count = re.subn(pattern, replacement, text, count=1, flags=re.S)
if count != 1:
    raise SystemExit(f"merge prompt block replacement count={count}")

helper = r'''

def _validate_merge_suggestion_semantics(
    suggestions: list[MergeSuggestion], source_doc: SuggestMergesRequest
) -> None:
    """Fail closed when a provider proposes an integration that would erase
    an explicit human/data distinction.

    These are deterministic guards, not model instructions. Island membership,
    equivalence and source differences are intentionally *not* hard vetoes;
    they remain context for the later IR migration (AI-MERGE-SEMANTICS-01).
    """
    cards_by_id = {card.id: card for card in source_doc.doc.cards}
    negate_pairs = {
        frozenset((edge.fromId, edge.toId))
        for edge in source_doc.doc.edges
        if edge.fromKind == "card" and edge.toKind == "card" and edge.type == "negate"
    }
    contradiction_pairs = {
        frozenset((link.fromCardId, link.toCardId))
        for link in (source_doc.doc.evidenceLinks or [])
        if link.type == "contradicts"
    }

    seen_card_ids: set[str] = set()
    for suggestion in suggestions:
        suggestion_ids = set(suggestion.cardIds)
        if seen_card_ids & suggestion_ids:
            raise HTTPException(
                status_code=422,
                detail={
                    "code": "merge_candidate_overlap",
                    "message": "A card appeared in more than one merge suggestion",
                },
            )
        seen_card_ids.update(suggestion_ids)

        cards = [cards_by_id[card_id] for card_id in suggestion.cardIds]
        if any(card.holdState is not None for card in cards):
            raise HTTPException(
                status_code=422,
                detail={
                    "code": "merge_candidate_held",
                    "message": "A merge suggestion included a held card",
                },
            )
        if any(card.mergedIntoCardId for card in cards):
            raise HTTPException(
                status_code=422,
                detail={
                    "code": "merge_candidate_already_merged",
                    "message": "A merge suggestion included a card already merged into another card",
                },
            )

        claim_types = {card.claimType for card in cards if card.claimType is not None}
        if len(claim_types) > 1:
            raise HTTPException(
                status_code=422,
                detail={
                    "code": "merge_candidate_claim_type_conflict",
                    "message": "A merge suggestion crossed distinct claim types",
                },
            )

        for index, left_id in enumerate(suggestion.cardIds):
            for right_id in suggestion.cardIds[index + 1 :]:
                pair = frozenset((left_id, right_id))
                if pair in negate_pairs:
                    raise HTTPException(
                        status_code=422,
                        detail={
                            "code": "merge_candidate_negated",
                            "message": "A merge suggestion crossed an explicit negate relation",
                        },
                    )
                if pair in contradiction_pairs:
                    raise HTTPException(
                        status_code=422,
                        detail={
                            "code": "merge_candidate_contradicted",
                            "message": "A merge suggestion crossed contradictory evidence",
                        },
                    )
'''

needle = "\ndef _parse_merge_suggestions(\n"
if text.count(needle) != 1:
    raise SystemExit(f"parser insertion point count={text.count(needle)}")
text = text.replace(needle, helper + needle, 1)

old_return = "        parsed_suggestions.append(suggestion)\n\n    return parsed_suggestions"
new_return = "        parsed_suggestions.append(suggestion)\n\n    _validate_merge_suggestion_semantics(parsed_suggestions, source_doc)\n    return parsed_suggestions"
if text.count(old_return) != 1:
    raise SystemExit(f"parser return replacement count={text.count(old_return)}")
text = text.replace(old_return, new_return, 1)
AI.write_text(text, encoding="utf-8")

TEST.write_text(r'''import pytest
from fastapi import HTTPException

from kj_atlas_api.models import (
    Card,
    DocumentV1,
    Edge,
    EvidenceLink,
    SuggestMergesRequest,
    Transform,
)
from kj_atlas_api.routes.ai import _build_merge_prompt, _parse_merge_suggestions


def _card(card_id: str, text: str, **updates) -> Card:
    return Card(id=card_id, text=text, x=0, y=0, textReviewed=True, **updates)


def _payload(cards, *, edges=None, evidence_links=None) -> SuggestMergesRequest:
    return SuggestMergesRequest(
        doc=DocumentV1(
            version=1,
            id="doc-merge",
            title="merge semantics",
            createdAt="2026-09-03T00:00:00Z",
            updatedAt="2026-09-03T00:00:00Z",
            transform=Transform(panX=0, panY=0, zoom=1),
            cards=cards,
            edges=edges or [],
            islands=[],
            evidenceLinks=evidence_links or [],
        )
    )


def _raw(*groups: tuple[str, list[str]]) -> str:
    import json

    return json.dumps(
        {
            "suggestions": [
                {
                    "groupId": group_id,
                    "cardIds": card_ids,
                    "mergedTextDraft": f"merged {group_id}",
                    "rationale": "candidate only",
                }
                for group_id, card_ids in groups
            ]
        }
    )


def _assert_code(exc_info, code: str) -> None:
    exc = exc_info.value
    assert exc.status_code == 422
    assert isinstance(exc.detail, dict)
    assert exc.detail["code"] == code


def test_merge_prompt_expresses_kj_integration_contract_and_omits_ineligible_cards() -> None:
    payload = _payload(
        [
            _card("c1", "same observation A"),
            _card("c2", "same observation B", holdState="held"),
            _card("c3", "already represented", mergedIntoCardId="c1"),
        ]
    )

    prompt = _build_merge_prompt(payload)

    assert "04-step-like consolidation" in prompt
    assert "kernel-fusion-style integration" in prompt
    assert "Return check" in prompt
    assert "Similarity alone is not enough" in prompt
    assert 'id="c1"' in prompt
    assert 'id="c2"' not in prompt
    assert 'id="c3"' not in prompt


def test_merge_parser_accepts_safe_candidate() -> None:
    payload = _payload([_card("c1", "alpha", claimType="fact"), _card("c2", "alpha again", claimType="fact")])

    result = _parse_merge_suggestions(_raw(("m1", ["c1", "c2"])), payload)

    assert [item.groupId for item in result] == ["m1"]


def test_merge_parser_rejects_held_card() -> None:
    payload = _payload([_card("c1", "alpha"), _card("c2", "beta", holdState="pending")])

    with pytest.raises(HTTPException) as exc_info:
        _parse_merge_suggestions(_raw(("m1", ["c1", "c2"])), payload)
    _assert_code(exc_info, "merge_candidate_held")


def test_merge_parser_rejects_negate_relation() -> None:
    payload = _payload(
        [_card("c1", "alpha"), _card("c2", "not alpha")],
        edges=[Edge(id="e1", fromId="c1", toId="c2", fromKind="card", toKind="card", type="negate")],
    )

    with pytest.raises(HTTPException) as exc_info:
        _parse_merge_suggestions(_raw(("m1", ["c1", "c2"])), payload)
    _assert_code(exc_info, "merge_candidate_negated")


def test_merge_parser_rejects_contradiction_evidence_even_when_unconfirmed() -> None:
    payload = _payload(
        [_card("c1", "alpha"), _card("c2", "counter observation")],
        evidence_links=[
            EvidenceLink(
                id="ev1",
                type="contradicts",
                fromCardId="c1",
                toCardId="c2",
                contradictionState="unconfirmed",
            )
        ],
    )

    with pytest.raises(HTTPException) as exc_info:
        _parse_merge_suggestions(_raw(("m1", ["c1", "c2"])), payload)
    _assert_code(exc_info, "merge_candidate_contradicted")


def test_merge_parser_rejects_distinct_known_claim_types() -> None:
    payload = _payload(
        [_card("c1", "observed", claimType="fact"), _card("c2", "possible meaning", claimType="hypothesis")]
    )

    with pytest.raises(HTTPException) as exc_info:
        _parse_merge_suggestions(_raw(("m1", ["c1", "c2"])), payload)
    _assert_code(exc_info, "merge_candidate_claim_type_conflict")


def test_merge_parser_rejects_already_merged_card() -> None:
    payload = _payload([_card("c1", "alpha"), _card("c2", "old duplicate", mergedIntoCardId="c1")])

    with pytest.raises(HTTPException) as exc_info:
        _parse_merge_suggestions(_raw(("m1", ["c1", "c2"])), payload)
    _assert_code(exc_info, "merge_candidate_already_merged")


def test_merge_parser_rejects_same_card_in_multiple_suggestions() -> None:
    payload = _payload([_card("c1", "alpha"), _card("c2", "alpha B"), _card("c3", "alpha C")])

    with pytest.raises(HTTPException) as exc_info:
        _parse_merge_suggestions(
            _raw(("m1", ["c1", "c2"]), ("m2", ["c1", "c3"])),
            payload,
        )
    _assert_code(exc_info, "merge_candidate_overlap")
''', encoding="utf-8")

print("suggest-merges safety patch applied")
