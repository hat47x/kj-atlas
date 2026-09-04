"""AC-7 spot-check: `derived_island_relations()` vs `getDerivedIslandEdges()`.

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

THE FIFTH DIFFERENCE IS OF A DIFFERENT KIND -- not a condition on the input but a
deliberate behavioural divergence, and here the PYTHON side is the correct one:

- `causal` is the one DIRECTED edge type (DOMAIN-KJ-01, `02_Architecture/schemas.md`
  §3.3.1: 無方向種別はペアを正規化してよいが、`causal` はペア正規化を行わず方向を
  保存する). `derived_island_relations()` obeys that -- both in the rendered pair
  and in the aggregation key, so `A --causal--> B` and `B --causal--> A` stay two
  rows. `getDerivedIslandEdges()` does not: its `normalizeUndirectedIslands()` call
  has no type exemption, so it reverses roughly half of all causal island pairs
  (island ids are `crypto.randomUUID()` values; lexical order says nothing about
  cause/effect order) and collapses opposite directions into one aggregate.
  That is a PRE-EXISTING TS bug -- it predates this rollout and was found
  incidentally by Stage 4's adversarial review -- filed as
  `01_Plans/issues/issue-DOMAIN-KJ-CAUSAL-DIRECTION-01-derived-island-edge-causal-pair-normalization.md`
  and deliberately NOT fixed from here. The working counter-example already in the
  frontend is `src/export/abstract_map_export.ts`, which special-cases `causal` out
  of its own `normalizePair()` with the same citation.

  Consequence for this file: the expected fixture carries TWO arrays.
  `derivedIslandEdges` is the contract-correct output this test asserts;
  `tsCurrentDerivedIslandEdges` pins what TS produces today, and the TS half
  asserts that one plus the invariant that the two differ on causal rows ONLY.
  When the TS issue is fixed, the second array is deleted and both halves go back
  to asserting the first.

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
    """The contract-correct rows -- what schemas.md §3.3.1 says the output is."""
    return json.loads(EXPECTED_FIXTURE.read_text(encoding="utf-8"))["derivedIslandEdges"]


def _ts_current() -> list[dict]:
    """What `getDerivedIslandEdges()` produces TODAY (see the module docstring).

    Pinned so the divergence is enumerated rather than merely asserted; the TS
    half of the pair holds itself to this array.
    """
    return json.loads(EXPECTED_FIXTURE.read_text(encoding="utf-8"))[
        "tsCurrentDerivedIslandEdges"
    ]


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
    halves disagree only on some machines. (The causal divergence changes WHICH
    ids exist on each side, not how either side orders the ids it has.)
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
    """`causal:c1:c3` and `causal:c2:c4` are one island-level pull, not two.

    Aggregation still happens WITHIN a direction; what §3.3.1 forbids is
    aggregating ACROSS directions (see the next two tests).
    """
    rows = derived_island_relations(_ir_from_fixture())
    a_to_b = [
        row for row in rows if row["type"] == "causal" and row["from_id"] == "isl-a"
    ]

    assert len(a_to_b) == 1
    assert a_to_b[0]["to_id"] == "isl-b"
    assert a_to_b[0]["aggregate_count"] == 2
    assert a_to_b[0]["contributing_relation_ids"] == ["causal:c1:c3", "causal:c2:c4"]


# ---------------------------------------------------------------------------
# DOMAIN-KJ-01 (schemas.md §3.3.1): causal direction. The one place the two
# implementations are MEANT to differ -- see the module docstring.
# ---------------------------------------------------------------------------


def test_causal_pair_is_not_lexically_normalized() -> None:
    """`causal:c7:c1` runs isl-b (cause) -> isl-a (effect).

    Lexically `isl-a` sorts first, so a pair-normalizing implementation emits it
    as `isl-a --causal--> isl-b`: the exact reversal §3.3.1 forbids. The fixture
    is built so the naive order and the causal order disagree, because in real
    documents island ids are `crypto.randomUUID()` values and the two orders
    agree only by chance (~half the time) -- which is why the bug shipped
    undetected until Stage 4's adversarial review.
    """
    rows = derived_island_relations(_ir_from_fixture())
    row = next(row for row in rows if row["id"] == "derived-island:isl-b|isl-a|causal")

    assert (row["from_id"], row["to_id"]) == ("isl-b", "isl-a")
    assert row["contributing_relation_ids"] == ["causal:c7:c1"]
    # c7 (isl-b) is the cause; c1 (isl-a) is the effect. Order preserved.
    assert row["contributing_card_ids"] == ["c7", "c1"]


def test_opposite_causal_directions_do_not_collapse_into_one_row() -> None:
    """The aggregation KEY is exempted too, not only the rendered pair.

    `A --causal--> B` and `B --causal--> A` are two different claims. Keying both
    by the normalized pair would fold them into a single row and lose one of them
    -- silently, since `aggregate_count` would simply grow.
    """
    rows = derived_island_relations(_ir_from_fixture())
    causal = [row for row in rows if row["type"] == "causal"]

    assert [(row["from_id"], row["to_id"]) for row in causal] == [
        ("isl-a", "isl-b"),
        ("isl-b", "isl-a"),
    ]
    assert [row["aggregate_count"] for row in causal] == [2, 1]


def test_undirected_types_still_normalize_their_pair() -> None:
    """§3.3.1 allows it for them, and the TS side agrees on those rows.

    `negate:c3:c5` runs c3 (isl-b) -> c5 (isl-c) and stays `isl-b|isl-c`; had it
    run the other way it would still be keyed `isl-b|isl-c`, because for an
    undirected type the two orders ARE the same relation.
    """
    rows = derived_island_relations(_ir_from_fixture())
    non_causal = [row for row in rows if row["type"] != "causal"]

    assert [row["id"] for row in non_causal] == [
        "derived-card:isl-c|c9|related",
        "derived-island:isl-b|isl-c|negate",
    ]
    negate = next(row for row in non_causal if row["type"] == "negate")
    assert (negate["from_id"], negate["to_id"]) == ("isl-b", "isl-c")
    # The key is the normalized pair, so the id and the endpoints agree.
    assert negate["id"] == f'derived-island:{negate["from_id"]}|{negate["to_id"]}|negate'


def test_the_divergence_from_the_ts_implementation_is_confined_to_causal() -> None:
    """States the known TS divergence as a bounded fact, not a vague caveat.

    The Python side is right (§3.3.1); `getDerivedIslandEdges()` normalizes every
    type, so it reverses the isl-b -> isl-a pair AND merges all three causal edges
    into one aggregate of 3. Filed as issue `DOMAIN-KJ-CAUSAL-DIRECTION-01`. Every
    NON-causal row must still match exactly -- if this test starts failing on a
    non-causal row, the two implementations have genuinely drifted and the fixture
    is no longer describing one known bug.
    """
    rows = [_as_ts_shape(row) for row in derived_island_relations(_ir_from_fixture())]
    ts_current = _ts_current()

    def _non_causal(source: list[dict]) -> list[dict]:
        return [row for row in source if row["type"] != "causal"]

    assert _non_causal(rows) == _non_causal(ts_current)
    assert rows != ts_current

    ts_causal = [row for row in ts_current if row["type"] == "causal"]
    assert len(ts_causal) == 1
    assert (ts_causal[0]["fromId"], ts_causal[0]["toId"]) == ("isl-a", "isl-b")
    assert ts_causal[0]["aggregateCount"] == 3
