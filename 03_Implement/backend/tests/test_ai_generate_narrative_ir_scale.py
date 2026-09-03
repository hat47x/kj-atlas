"""`generate-narrative` の因果・対立骨格を代表規模で守るための回帰テスト。"""

from __future__ import annotations

import pytest
from fastapi import HTTPException

from kj_atlas_api.llm_input_ir import (
    IRSource,
    MAX_CARDS,
    SourceCard,
    SourceRelation,
)
from kj_atlas_api.models_ai import GenerateNarrativeRequest
from kj_atlas_api.routes.ai import (
    _build_generate_narrative_prompt,
    _generate_narrative_ir,
    _narrative_required_card_ids,
)
from scripts.measure_ai_route_prompt_coverage import representative_document


def _late_spine_document() -> dict:
    doc = representative_document(include_evidence=False)
    for edge in doc["edges"]:
        if edge["id"] == "e298":
            edge["type"] = "causal"
        elif edge["id"] == "e299":
            edge["type"] = "negate"
    return doc


def test_tail_causal_and_negate_survive_the_global_card_cut() -> None:
    """300カードでも、AC-3の論理骨格をIRと読み順上の双方に残す。"""
    payload = GenerateNarrativeRequest.model_validate({"doc": _late_spine_document()})

    ir = _generate_narrative_ir(payload)
    prompt = _build_generate_narrative_prompt(payload, ir)
    relations = {
        (item["from"], item["to"], item["type"]) for item in ir["relations"]
    }

    assert len(ir["cards"]) == MAX_CARDS
    assert ir["truncation"] == {
        "truncated": True,
        "reason_codes": ["MAX_CARDS"],
    }
    assert ("c298", "c299", "causal") in relations
    assert ("c299", "c000", "negate") in relations

    # `Logical relations` に見えるだけでなく、読み順上の関節としても残す。
    assert 'card "c298" --causal--> card "c299"' in prompt
    assert 'card "c299" --negate--> card "c000"' in prompt
    assert (
        '- within reading-order 30: card "c298" --causal--> card "c299"'
        in prompt
    )
    assert (
        '- reading-order 30 -> reading-order 1: card "c299" --negate--> card "c000"'
        in prompt
    )
    # 読み順は従来どおりDocument由来で保持する。
    assert '- 30. island id="i29"' in prompt


def test_required_spine_ids_exclude_non_spine_and_non_normalizable_relations() -> None:
    """required集合を `causal` / `negate` の正規化可能なカード端点に限定する。"""
    source = IRSource(
        doc_id="narrative-required-boundary",
        doc_version=1,
        cards=(
            SourceCard(id="a", text="A", text_reviewed=True),
            SourceCard(id="b", text="B", text_reviewed=True),
            SourceCard(id="c", text="C", text_reviewed=True),
        ),
        relations=(
            SourceRelation(from_id="a", to_id="b", type="causal"),
            SourceRelation(from_id="b", to_id="c", type="negate"),
            # 補助関係だけを理由にrequiredへ昇格しない。
            SourceRelation(from_id="c", to_id="a", type="related"),
            # 島を端点に持つ辺はIR §2.3の正規化対象外。
            SourceRelation(
                from_id="island-a",
                to_id="a",
                type="causal",
                from_kind="island",
                to_kind="card",
            ),
            # 存在しないカードを参照する辺もrequired集合へ入れない。
            SourceRelation(from_id="a", to_id="missing", type="negate"),
        ),
    )

    assert _narrative_required_card_ids(source) == ("a", "b", "c")


def test_required_spine_ids_are_independent_of_source_relation_order() -> None:
    """source relationの並び順が変わってもrequired集合を変えない。"""
    cards = (
        SourceCard(id="a", text="A", text_reviewed=True),
        SourceCard(id="b", text="B", text_reviewed=True),
        SourceCard(id="c", text="C", text_reviewed=True),
    )
    relations = (
        SourceRelation(from_id="b", to_id="c", type="negate"),
        SourceRelation(from_id="a", to_id="b", type="causal"),
    )

    forward = IRSource(
        doc_id="order-forward",
        doc_version=1,
        cards=cards,
        relations=relations,
    )
    reverse = IRSource(
        doc_id="order-reverse",
        doc_version=1,
        cards=cards,
        relations=tuple(reversed(relations)),
    )

    assert _narrative_required_card_ids(forward) == ("a", "b", "c")
    assert _narrative_required_card_ids(reverse) == ("a", "b", "c")


def test_more_than_max_cards_of_spine_endpoints_fails_closed() -> None:
    """必須骨格だけで上限を超えるときは、不完全な文章生成へ進まない。"""
    doc = representative_document(include_evidence=False)
    # e000..e199 を causal にすると c000..c200 の201枚がrequiredになる。
    for edge in doc["edges"][:MAX_CARDS]:
        edge["type"] = "causal"
    payload = GenerateNarrativeRequest.model_validate({"doc": doc})

    with pytest.raises(HTTPException) as excinfo:
        _generate_narrative_ir(payload)

    assert excinfo.value.status_code == 422
    assert excinfo.value.detail["code"] == "required_card_budget_exceeded"
