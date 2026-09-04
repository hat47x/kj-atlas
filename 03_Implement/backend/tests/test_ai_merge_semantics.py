import json

import pytest
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


def _raw(*groups: tuple[str, list[str]], merge_method: str = "near_duplicate") -> str:
    return json.dumps(
        {
            "suggestions": [
                {
                    "groupId": group_id,
                    "cardIds": card_ids,
                    "mergedTextDraft": f"merged {group_id}",
                    "mergeMethod": merge_method,
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
    assert 'mergeMethod="near_duplicate"' in prompt
    assert 'mergeMethod="kernel_fusion"' in prompt
    assert '"mergeMethod":"near_duplicate|kernel_fusion"' in prompt
    assert "Return check" in prompt
    assert "Similarity alone is not enough" in prompt
    assert 'id="c1"' in prompt
    assert 'id="c2"' not in prompt
    assert 'id="c3"' not in prompt


def test_merge_parser_accepts_both_merge_methods_without_collapsing_them() -> None:
    payload = _payload(
        [
            _card("c1", "alpha", claimType="fact"),
            _card("c2", "alpha again", claimType="fact"),
            _card("c3", "alpha detail", claimType="fact"),
            _card("c4", "shared meaning", claimType="fact"),
        ]
    )

    near_duplicate = _parse_merge_suggestions(
        _raw(("m1", ["c1", "c2"]), merge_method="near_duplicate"), payload
    )
    kernel_fusion = _parse_merge_suggestions(
        _raw(("m2", ["c3", "c4"]), merge_method="kernel_fusion"), payload
    )

    assert near_duplicate[0].mergeMethod == "near_duplicate"
    assert kernel_fusion[0].mergeMethod == "kernel_fusion"


def test_merge_parser_rejects_missing_merge_method() -> None:
    payload = _payload([_card("c1", "alpha"), _card("c2", "alpha again")])
    raw = json.dumps(
        {
            "suggestions": [
                {
                    "groupId": "m1",
                    "cardIds": ["c1", "c2"],
                    "mergedTextDraft": "merged",
                }
            ]
        }
    )

    with pytest.raises(HTTPException) as exc_info:
        _parse_merge_suggestions(raw, payload)

    assert exc_info.value.status_code == 422
    assert exc_info.value.detail == "Invalid merge suggestion payload"


def test_merge_parser_rejects_unknown_merge_method() -> None:
    payload = _payload([_card("c1", "alpha"), _card("c2", "alpha again")])

    with pytest.raises(HTTPException) as exc_info:
        _parse_merge_suggestions(
            _raw(("m1", ["c1", "c2"]), merge_method="semantic_similarity"), payload
        )

    assert exc_info.value.status_code == 422
    assert exc_info.value.detail == "Invalid merge suggestion payload"


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
