"""Scale contract for narrative-required causal/negate relation identities."""

from __future__ import annotations

import pytest
from fastapi import HTTPException

from kj_atlas_api.llm_input_ir import MAX_RELATIONS, IRSource, SourceCard, SourceRelation
from kj_atlas_api.models_ai import GenerateNarrativeRequest
from kj_atlas_api.routes.ai import (
    _generate_narrative_ir,
    _narrative_required_relation_ids,
)
from scripts.measure_ai_route_prompt_coverage import representative_document


def _logical_edges(count: int, *, relation_type: str) -> list[dict[str, str]]:
    edges: list[dict[str, str]] = []
    for source_index in range(21):
        for target_index in range(21):
            if source_index == target_index:
                continue
            edges.append(
                {
                    "id": f"logic-{len(edges):03d}",
                    "fromId": f"c{source_index:03d}",
                    "toId": f"c{target_index:03d}",
                    "type": relation_type,
                }
            )
            if len(edges) == count:
                return edges
    raise AssertionError("fixture requested more unique relations than available")


def test_required_relation_ids_match_only_normalizable_narrative_spine() -> None:
    source = IRSource(
        doc_id="narrative-required-relation-boundary",
        doc_version=1,
        cards=(
            SourceCard(id="a", text="A", text_reviewed=True),
            SourceCard(id="b", text="B", text_reviewed=True),
            SourceCard(id="c", text="C", text_reviewed=True),
        ),
        relations=(
            SourceRelation(from_id="a", to_id="b", type="causal"),
            SourceRelation(from_id="b", to_id="c", type="negate"),
            SourceRelation(from_id="c", to_id="a", type="related"),
            SourceRelation(
                from_id="island-a",
                to_id="a",
                type="causal",
                from_kind="island",
                to_kind="card",
            ),
            SourceRelation(from_id="a", to_id="missing", type="negate"),
        ),
    )

    assert _narrative_required_relation_ids(source) == (
        "causal:a:b",
        "negate:b:c",
    )


def test_narrative_required_relation_survives_optional_relation_pressure() -> None:
    doc = representative_document(include_evidence=False)
    doc["edges"] = _logical_edges(MAX_RELATIONS, relation_type="related")
    doc["edges"].append(
        {
            "id": "required-tail",
            "fromId": "c298",
            "toId": "c299",
            "type": "negate",
        }
    )
    payload = GenerateNarrativeRequest.model_validate({"doc": doc})

    ir = _generate_narrative_ir(payload)
    relation_ids = {item["id"] for item in ir["relations"]}

    assert "negate:c298:c299" in relation_ids
    assert len(ir["relations"]) == MAX_RELATIONS
    assert ir["truncation"]["reason_codes"] == ["MAX_CARDS", "MAX_RELATIONS"]


def test_more_than_max_relations_of_narrative_spine_fails_closed() -> None:
    doc = representative_document(include_evidence=False)
    doc["edges"] = _logical_edges(MAX_RELATIONS + 1, relation_type="causal")
    payload = GenerateNarrativeRequest.model_validate({"doc": doc})

    with pytest.raises(HTTPException) as excinfo:
        _generate_narrative_ir(payload)

    assert excinfo.value.status_code == 422
    assert excinfo.value.detail["code"] == "required_relation_budget_exceeded"
