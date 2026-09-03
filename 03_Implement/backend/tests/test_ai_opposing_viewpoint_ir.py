"""`propose-opposing-viewpoint` のroute固有IR境界をproviderなしで固定する。"""

import pytest

from kj_atlas_api.llm_input_ir import IRGenerationError, RELATION_TYPES
from kj_atlas_api.models import Card, DocumentV1, Edge, EvidenceLink, Island, Transform
from kj_atlas_api.models_ai import ProposeOpposingViewpointRequest
from kj_atlas_api.opposing_viewpoint_ir import (
    build_opposing_viewpoint_ir_context,
    opposing_viewpoint_ir_prompt_lines,
)


_NOW = "2026-09-03T00:00:00Z"


def _payload() -> ProposeOpposingViewpointRequest:
    doc = DocumentV1(
        version=1,
        id="opposing-ir",
        createdAt=_NOW,
        updatedAt=_NOW,
        transform=Transform(panX=0, panY=0, zoom=1),
        cards=[
            Card(id="c-target", text="待ち時間が長いと利用者は離れる", x=0, y=0, textReviewed=True),
            Card(id="c-relation", text="常連利用者は長い待ち時間でも残る", x=10, y=0, textReviewed=True),
            Card(id="c-evidence", text="一部の利用者は待ち時間より品質を重視する", x=20, y=0, textReviewed=True),
            Card(id="c-unrelated", text="受付端末の色を変更した", x=30, y=0, textReviewed=True),
        ],
        edges=[
            Edge(id="r1", fromId="c-target", toId="c-relation", type="negate"),
            Edge(id="r2", fromId="c-unrelated", toId="c-relation", type="related"),
        ],
        islands=[Island(id="i1", cardIds=["c-target", "c-relation", "c-evidence"])],
        evidenceLinks=[
            EvidenceLink(
                id="ev1",
                type="contradicts",
                fromCardId="c-evidence",
                toCardId="c-target",
                contradictionState="held",
            )
        ],
    )
    return ProposeOpposingViewpointRequest(doc=doc, targetCardId="c-target")


def test_context_preserves_target_and_directly_connected_meaning() -> None:
    context = build_opposing_viewpoint_ir_context(
        _payload(), allow_unreviewed_text=False
    )

    assert context.target_card_id == "c-target"
    assert context.direct_context_card_ids == frozenset({"c-relation", "c-evidence"})
    assert "coordinates" not in context.ir

    projected_ids = {item["id"] for item in context.ir["cards"]}
    assert {"c-target", "c-relation", "c-evidence"}.issubset(projected_ids)

    relation_keys = {
        (item["from"], item["to"], item["type"])
        for item in context.ir.get("relations", [])
    }
    assert ("c-target", "c-relation", "negate") in relation_keys

    held = next(item for item in context.ir["evidence_links"] if item["id"] == "ev1")
    assert held["contradiction_state"] == "held"


def test_prompt_distinguishes_human_judgement_and_exploratory_cards() -> None:
    context = build_opposing_viewpoint_ir_context(
        _payload(), allow_unreviewed_text=False
    )
    prompt = "\n".join(opposing_viewpoint_ir_prompt_lines(context))

    assert 'id="c-relation"' in prompt
    assert 'id="c-evidence"' in prompt
    assert 'card "c-target" --negate--> card "c-relation"' in prompt
    assert "contradictionState=held" in prompt
    assert "existing HUMAN judgement" in prompt
    assert "Other cards retained by the IR for exploratory counterexample search" in prompt
    assert 'id="c-unrelated"' in prompt


def test_tail_target_and_direct_context_are_reserved_before_card_truncation() -> None:
    cards = [
        Card(
            id=f"c{i:03d}",
            text=f"観察{i:03d}は対象の周辺事情を示す",
            x=float(i),
            y=0,
            textReviewed=True,
        )
        for i in range(300)
    ]
    doc = DocumentV1(
        version=1,
        id="opposing-ir-scale",
        createdAt=_NOW,
        updatedAt=_NOW,
        transform=Transform(panX=0, panY=0, zoom=1),
        cards=cards,
        edges=[Edge(id="r-tail", fromId="c299", toId="c298", type="negate")],
        islands=[],
        evidenceLinks=[
            EvidenceLink(
                id="ev-tail",
                type="contradicts",
                fromCardId="c297",
                toCardId="c299",
                contradictionState="confirmed",
            )
        ],
    )
    payload = ProposeOpposingViewpointRequest(doc=doc, targetCardId="c299")

    context = build_opposing_viewpoint_ir_context(payload, allow_unreviewed_text=False)
    projected_ids = {item["id"] for item in context.ir["cards"]}

    assert {"c297", "c298", "c299"}.issubset(projected_ids)
    assert context.ir["truncation"]["truncated"] is True
    prompt = "\n".join(opposing_viewpoint_ir_prompt_lines(context))
    assert "contradictionState=confirmed" in prompt
    assert 'card "c299" --negate--> card "c298"' in prompt



def test_required_target_text_truncation_fails_closed() -> None:
    cards = [
        Card(id="target", text="中" * 2000, x=0, y=0, textReviewed=True),
        *[
            Card(
                id=f"u{i}",
                text="周" * 2000,
                x=float(i + 1),
                y=0,
                textReviewed=True,
            )
            for i in range(6)
        ],
    ]
    doc = DocumentV1(
        version=1,
        id="opposing-required-text-overflow",
        createdAt=_NOW,
        updatedAt=_NOW,
        transform=Transform(panX=0, panY=0, zoom=1),
        cards=cards,
        edges=[],
        islands=[],
        evidenceLinks=[],
    )
    payload = ProposeOpposingViewpointRequest(doc=doc, targetCardId="target")

    with pytest.raises(IRGenerationError) as captured:
        build_opposing_viewpoint_ir_context(payload, allow_unreviewed_text=False)

    assert captured.value.code == "required_text_truncated"

def test_target_required_relation_overflow_fails_closed() -> None:
    relation_types = sorted(RELATION_TYPES)
    cards = [Card(id="target", text="中心の主張", x=0, y=0, textReviewed=True)]
    edges: list[Edge] = []
    edge_index = 0
    for i in range(81):
        neighbour_id = f"n{i:03d}"
        cards.append(
            Card(id=neighbour_id, text=f"反対候補{i:03d}", x=float(i + 1), y=0, textReviewed=True)
        )
        for relation_type in relation_types:
            edge_index += 1
            edges.append(
                Edge(
                    id=f"r{edge_index:04d}",
                    fromId="target",
                    toId=neighbour_id,
                    type=relation_type,
                )
            )

    assert len(edges) > 400
    doc = DocumentV1(
        version=1,
        id="opposing-relation-overflow",
        createdAt=_NOW,
        updatedAt=_NOW,
        transform=Transform(panX=0, panY=0, zoom=1),
        cards=cards,
        edges=edges,
        islands=[],
        evidenceLinks=[],
    )
    payload = ProposeOpposingViewpointRequest(doc=doc, targetCardId="target")

    with pytest.raises(IRGenerationError) as captured:
        build_opposing_viewpoint_ir_context(payload, allow_unreviewed_text=False)

    assert captured.value.code == "required_relation_missing"


def test_too_many_direct_context_cards_fail_closed() -> None:
    cards = [Card(id="target", text="中心の主張", x=0, y=0, textReviewed=True)]
    edges: list[Edge] = []
    for i in range(200):
        neighbour_id = f"n{i:03d}"
        cards.append(
            Card(id=neighbour_id, text=f"直接文脈{i:03d}", x=float(i + 1), y=0, textReviewed=True)
        )
        edges.append(
            Edge(id=f"r{i:03d}", fromId="target", toId=neighbour_id, type="related")
        )

    doc = DocumentV1(
        version=1,
        id="opposing-required-card-overflow",
        createdAt=_NOW,
        updatedAt=_NOW,
        transform=Transform(panX=0, panY=0, zoom=1),
        cards=cards,
        edges=edges,
        islands=[],
        evidenceLinks=[],
    )
    payload = ProposeOpposingViewpointRequest(doc=doc, targetCardId="target")

    with pytest.raises(IRGenerationError) as captured:
        build_opposing_viewpoint_ir_context(payload, allow_unreviewed_text=False)

    assert captured.value.code == "required_card_budget_exceeded"
