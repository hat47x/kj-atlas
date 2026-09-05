"""Regression tests for route-required relation preservation under IR budgets."""

from __future__ import annotations

import pytest

from kj_atlas_api.llm_input_ir import (
    IRGenerationError,
    IRSource,
    MAX_RELATIONS,
    SourceCard,
    SourceRelation,
    build_llm_input_ir,
    relation_id,
)


def _cards(count: int = 300) -> tuple[SourceCard, ...]:
    return tuple(
        SourceCard(id=f"c{i:03d}", text=f"観察 c{i:03d}", text_reviewed=True)
        for i in range(count)
    )


def _directed_relations(count: int, *, relation_type: str = "causal") -> tuple[SourceRelation, ...]:
    relations: list[SourceRelation] = []
    for source_index in range(30):
        for target_index in range(30):
            if source_index == target_index:
                continue
            relations.append(
                SourceRelation(
                    from_id=f"c{source_index:03d}",
                    to_id=f"c{target_index:03d}",
                    type=relation_type,
                )
            )
            if len(relations) == count:
                return tuple(relations)
    raise AssertionError("fixture requested more unique relations than available")


def test_required_relation_is_reserved_before_global_relation_cut() -> None:
    causal = _directed_relations(MAX_RELATIONS + 1)
    required = SourceRelation(from_id="c298", to_id="c299", type="negate")
    source = IRSource(
        doc_id="required-relation-scale",
        doc_version=1,
        cards=_cards(),
        relations=causal + (required,),
    )
    required_id = relation_id("negate", "c298", "c299")

    historical = build_llm_input_ir(source)
    protected = build_llm_input_ir(source, required_relation_ids=(required_id,))

    assert required_id not in {item["id"] for item in historical["relations"]}
    assert required_id in {item["id"] for item in protected["relations"]}
    assert len(protected["relations"]) == MAX_RELATIONS
    assert protected["truncation"]["reason_codes"] == ["MAX_CARDS", "MAX_RELATIONS"]
    assert protected["relations"] == sorted(
        protected["relations"], key=lambda item: (item["type"], item["from"], item["to"])
    )


def test_required_relation_implicitly_reserves_both_endpoint_cards() -> None:
    star = tuple(
        SourceRelation(from_id="c000", to_id=f"c{i:03d}", type="related")
        for i in range(1, 251)
    )
    tail = SourceRelation(from_id="c298", to_id="c299", type="negate")
    source = IRSource(
        doc_id="required-relation-endpoints",
        doc_version=1,
        cards=_cards(),
        relations=star + (tail,),
    )
    required_id = relation_id("negate", "c298", "c299")

    historical = build_llm_input_ir(source)
    protected = build_llm_input_ir(source, required_relation_ids=(required_id,))

    historical_cards = {card["id"] for card in historical["cards"]}
    protected_cards = {card["id"] for card in protected["cards"]}
    assert {"c298", "c299"}.isdisjoint(historical_cards)
    assert {"c298", "c299"} <= protected_cards
    assert required_id in {item["id"] for item in protected["relations"]}


def test_missing_required_relation_fails_closed_without_echoing_the_id() -> None:
    missing_id = "negate:not-in-source:also-missing"
    with pytest.raises(IRGenerationError) as captured:
        build_llm_input_ir(
            IRSource(doc_id="missing", doc_version=1, cards=_cards(2)),
            required_relation_ids=(missing_id,),
        )

    assert captured.value.code == "required_relation_missing"
    assert missing_id not in captured.value.message


def test_required_relation_set_cannot_exceed_relation_budget() -> None:
    relations = _directed_relations(MAX_RELATIONS + 1)
    required_ids = tuple(
        relation_id(item.type, item.from_id, item.to_id) for item in relations
    )
    source = IRSource(
        doc_id="required-relation-over-budget",
        doc_version=1,
        cards=_cards(30),
        relations=relations,
    )

    with pytest.raises(IRGenerationError) as captured:
        build_llm_input_ir(source, required_relation_ids=required_ids)

    assert captured.value.code == "required_relation_budget_exceeded"
