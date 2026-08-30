"""AC-7 spot-check: `derived_island_relations()` == `getDerivedIslandEdges()`.

`AI-IR-PROJECTION-01` AC-7 (ADR-0069 D4=A) asks for the TS and Python projection
implementations to be checked for behavioural equivalence. Stages 1-3 deferred it
because no function pair existed -- the IR reprojects confirmed islands verbatim
and reimplemented neither `buildAbstractMapExport()` nor `getDerivedIslandEdges()`.
Stage 4 creates the first real pair: `/ai/suggest-layout` needs islands to reach
the model as relation sets rather than as bounding boxes, which requires
aggregating card-level relations up to island level -- exactly what
`frontend/src/domain/island_edge_aggregate.ts` `getDerivedIslandEdges()` does.

This is ONE narrow comparison on ONE shared fixture, not a framework. Neither side
executes the other: both read `fixtures/derived_island_edges_document.json` and
assert against `fixtures/derived_island_edges_expected.json`. The TS half lives at
`frontend/src/domain/island_edge_aggregate.python_equivalence.test.ts`; if either
implementation changes behaviour, its own half of the pair fails against the same
expected file, which is what makes the file a shared contract rather than two
independent goldens.

WHAT THE COMPARISON DOES NOT COVER (the fixture stays inside the overlap of the
two implementations on purpose; these are IR projection rules, not drift):

- an edge with an island endpoint never reaches the IR (spec §2.3 rule 6), so the
  TS branch that promotes a persisted island->card edge has no Python counterpart;
- an `unknown` edge type is dropped by the IR (D2=A) where TS would aggregate it;
- a repeated `(from, to, type)` triple is de-duplicated by the IR (§2.3 rule 3)
  where TS would count both occurrences in `aggregateCount`;
- a card listed by two islands is attributed to the first only (§2.2A
  FIRST-MATCH-WINS) where TS's `getIslandsForCard()` returns every match.

`derived_island_relations()`' docstring carries the same list next to the code.
"""
from __future__ import annotations

import json
from pathlib import Path

from kj_atlas_api.llm_input_ir import (
    build_llm_input_ir,
    derived_island_relations,
    source_from_document,
)
from kj_atlas_api.models import DocumentV1

FIXTURES = Path(__file__).resolve().parent / "fixtures"
DOCUMENT_FIXTURE = FIXTURES / "derived_island_edges_document.json"
EXPECTED_FIXTURE = FIXTURES / "derived_island_edges_expected.json"


def _load_document() -> DocumentV1:
    return DocumentV1.model_validate(json.loads(DOCUMENT_FIXTURE.read_text(encoding="utf-8")))


def _expected() -> list[dict]:
    return json.loads(EXPECTED_FIXTURE.read_text(encoding="utf-8"))["derivedIslandEdges"]


def _as_ts_shape(row: dict) -> dict:
    """Map one Python row onto the TS `DerivedIslandEdge` field names.

    Written out field by field rather than by a generic snake->camel helper, so a
    renamed or dropped field shows up here as an obvious edit instead of being
    silently absorbed.
    """
    return {
        "id": row["id"],
        "fromId": row["from_id"],
        "toId": row["to_id"],
        "fromKind": row["from_kind"],
        "toKind": row["to_kind"],
        "type": row["type"],
        # TS carries a literal discriminator; the Python rows are consumed inside
        # the process that built them and do not need one.
        "isDerived": True,
        "aggregateCount": row["aggregate_count"],
        "contributingEdgeIds": row["contributing_relation_ids"],
        "contributingCardIds": row["contributing_card_ids"],
    }


def _ir_from_fixture() -> dict:
    return build_llm_input_ir(
        source_from_document(_load_document()),
        include_coordinates=True,
        safe_mode=True,
        allow_unreviewed_text=False,
    )


def test_python_derivation_matches_the_shared_expected_output() -> None:
    """The Python half of the pair. The TS half asserts the same file."""
    rows = [_as_ts_shape(row) for row in derived_island_relations(_ir_from_fixture())]

    assert rows == _expected()


def test_ordering_is_by_derived_id_ascending() -> None:
    """The emitted order is part of what the two sides agree on.

    TS sorts with `localeCompare`, Python by code point. The fixture ids are
    chosen so the two orderings coincide; pinning the order here means a fixture
    edit that breaks that coincidence fails loudly instead of making the two
    halves disagree only on some machines.
    """
    ids = [row["id"] for row in derived_island_relations(_ir_from_fixture())]

    assert ids == sorted(ids)
    assert ids == [row["id"] for row in _expected()]


def test_same_island_relations_are_internalized_and_lone_pairs_ignored() -> None:
    """The two dropped cases, stated as behaviour rather than as a diff.

    `related:c1:c2` joins two cards of `isl-a` (says nothing about where islands
    go), and `related:c8:c9` joins two cards that belong to no island at all.
    """
    ir = _ir_from_fixture()
    relation_ids = {relation["id"] for relation in ir["relations"]}
    assert {"related:c1:c2", "related:c8:c9"} <= relation_ids

    contributing = {
        relation_id
        for row in derived_island_relations(ir)
        for relation_id in row["contributing_relation_ids"]
    }
    assert "related:c1:c2" not in contributing
    assert "related:c8:c9" not in contributing


def test_multiple_card_relations_between_two_islands_aggregate_into_one() -> None:
    """`causal:c1:c3` and `causal:c2:c4` are one island-level pull, not two."""
    rows = derived_island_relations(_ir_from_fixture())
    causal = [row for row in rows if row["type"] == "causal"]

    assert len(causal) == 1
    assert causal[0]["from_id"] == "isl-a"
    assert causal[0]["to_id"] == "isl-b"
    assert causal[0]["aggregate_count"] == 2
