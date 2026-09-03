"""Regression tests for route-required card preservation during IR truncation.

These tests exercise the shared projection directly and never call an LLM.
They keep the ordinary no-focus projection unchanged while proving that a route
can explicitly reserve task-required cards before the global MAX_CARDS cut.
"""

from __future__ import annotations

import pytest

from kj_atlas_api.llm_input_ir import (
    IRGenerationError,
    IRSource,
    SourceCard,
    SourceEvidenceLink,
    build_llm_input_ir,
    ir_sha256,
)


def _source(*, state: str = "confirmed") -> IRSource:
    cards = tuple(
        SourceCard(
            id=f"c{i:03d}",
            text=f"観察 c{i:03d}",
            text_reviewed=True,
        )
        for i in range(300)
    )
    evidence = (
        SourceEvidenceLink(
            id="ev-tail",
            type="contradicts",
            from_card_id="c298",
            to_card_id="c299",
            contradiction_state=state,
        ),
    )
    return IRSource(
        doc_id="required-card-scale",
        doc_version=1,
        cards=cards,
        evidence_links=evidence,
    )


def test_empty_required_set_preserves_historical_projection() -> None:
    source = _source()

    historical = build_llm_input_ir(source)
    explicit_empty = build_llm_input_ir(source, required_card_ids=())

    assert ir_sha256(explicit_empty) == ir_sha256(historical)
    assert [card["id"] for card in historical["cards"]] == [
        f"c{i:03d}" for i in range(200)
    ]
    assert "evidence_links" not in historical


def test_required_tail_pair_survives_card_truncation_with_its_evidence() -> None:
    ir = build_llm_input_ir(
        _source(state="held"),
        required_card_ids=("c298", "c299"),
    )

    projected_ids = [card["id"] for card in ir["cards"]]
    assert len(projected_ids) == 200
    assert projected_ids[:198] == [f"c{i:03d}" for i in range(198)]
    assert projected_ids[-2:] == ["c298", "c299"]
    assert ir["evidence_links"] == [
        {
            "id": "ev-tail",
            "type": "contradicts",
            "from_card_id": "c298",
            "to_card_id": "c299",
            "contradiction_state": "held",
        }
    ]
    assert ir["truncation"] == {
        "truncated": True,
        "reason_codes": ["MAX_CARDS"],
    }


def test_required_projection_is_deterministic() -> None:
    source = _source()

    first = build_llm_input_ir(source, required_card_ids=("c299", "c298"))
    second = build_llm_input_ir(source, required_card_ids=("c298", "c299"))

    assert ir_sha256(first) == ir_sha256(second)


def test_missing_required_card_fails_closed_without_echoing_the_id() -> None:
    with pytest.raises(IRGenerationError) as captured:
        build_llm_input_ir(_source(), required_card_ids=("not-in-source",))

    assert captured.value.code == "required_card_missing"
    assert "not-in-source" not in captured.value.message


def test_required_set_cannot_exceed_card_budget() -> None:
    with pytest.raises(IRGenerationError) as captured:
        build_llm_input_ir(
            _source(),
            required_card_ids=tuple(f"c{i:03d}" for i in range(201)),
        )

    assert captured.value.code == "required_card_budget_exceeded"
