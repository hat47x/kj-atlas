"""Unit tests for the LLM input IR builder (`llm_input_ir_spec.md` 1.2).

Covers the narrowed AC-4 / AC-5 / AC-6 / AC-8 of `AI-IR-PROJECTION-01`:
SafeMode refusal, PII + structured-text refusal, deterministic truncation, and
the `ir_version` / fixture regression.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from kj_atlas_api.llm_input_ir import (
    IR_VERSION,
    MAX_CARDS,
    MAX_RELATIONS,
    MAX_TEXT_CHARS,
    IRGenerationError,
    IRSource,
    SourceCard,
    SourceEvidenceLink,
    SourceIsland,
    SourceRelation,
    adjudicated_contradiction,
    build_llm_input_ir,
    canonical_ir_json,
    held_card_ids,
    ir_sha256,
    source_from_document,
    validate_llm_input_ir,
)
from kj_atlas_api.models import DocumentV1

FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures"
DOCUMENT_FIXTURE = FIXTURE_DIR / "llm_input_ir_document.json"
EXPECTED_FIXTURE = FIXTURE_DIR / "llm_input_ir_expected.json"


def _card(
    card_id: str,
    text: str = "alpha",
    *,
    reviewed: bool | None = True,
    x=None,
    y=None,
    hold_state: str | None = None,
):
    return SourceCard(
        id=card_id, text=text, text_reviewed=reviewed, x=x, y=y, hold_state=hold_state
    )


def _source(cards, **kwargs) -> IRSource:
    return IRSource(doc_id="doc-1", doc_version=1, cards=tuple(cards), **kwargs)


# ---------------------------------------------------------------------------
# AC-8 (narrowed): ir_version and the D1/D3 schema shape
# ---------------------------------------------------------------------------


def test_ir_version_is_1_2() -> None:
    ir = build_llm_input_ir(_source([_card("c1"), _card("c2", "beta")]))
    assert IR_VERSION == "1.2"
    assert ir["ir_version"] == "1.2"
    validate_llm_input_ir(ir)


def test_coordinates_are_optional_and_declared_per_endpoint() -> None:
    """ADR-0069 D1=B: `coordinates` is only emitted when the caller asks."""
    cards = [_card("c1", x=10, y=10), _card("c2", "beta", x=-10, y=-10)]

    without = build_llm_input_ir(_source(cards), include_coordinates=False)
    assert "coordinates" not in without

    with_coords = build_llm_input_ir(_source(cards), include_coordinates=True)
    assert [item["card_id"] for item in with_coords["coordinates"]] == ["c1", "c2"]
    # spec §2.2 rule 2: centroid-relative, never the raw absolute position.
    assert with_coords["coordinates"][0]["x"] == 10.0
    assert with_coords["coordinates"][0]["radius"] == pytest.approx(14.142, abs=1e-3)


def test_islands_are_a_distinct_field_from_cluster_candidates() -> None:
    """ADR-0069 D3=A: confirmed islands and machine candidates never mix."""
    ir = build_llm_input_ir(
        _source(
            [_card("c1"), _card("c2", "beta"), _card("c3", "gamma")],
            relations=(SourceRelation(from_id="c1", to_id="c2", type="related"),),
            islands=(
                SourceIsland(
                    id="i1",
                    card_ids=("c1", "c2"),
                    title="T",
                    placard_card_id="c1",
                    title_reviewed=True,
                ),
            ),
        )
    )
    assert ir["islands"] == [
        {
            "id": "i1",
            "card_ids": ["c1", "c2"],
            "title": "T",
            "placard_card_id": "c1",
            "parent_island_id": None,
            "review_state": "human_reviewed",
        }
    ]
    assert [c["card_ids"] for c in ir["cluster_candidates"]] == [["c1", "c2"]]
    assert ir["cluster_candidates"][0]["basis"] == "relation"
    assert "review_state" not in ir["cluster_candidates"][0]


def test_island_membership_is_first_match_wins() -> None:
    """DOMAIN-ISLAND-MEMBERSHIP-01: a duplicated card goes to the FIRST island."""
    ir = build_llm_input_ir(
        _source(
            [_card("c1"), _card("c2", "beta")],
            islands=(
                SourceIsland(id="i-first", card_ids=("c1", "c2")),
                SourceIsland(id="i-second", card_ids=("c1",)),
            ),
        )
    )
    by_id = {island["id"]: island for island in ir["islands"]}
    assert by_id["i-first"]["card_ids"] == ["c1", "c2"]
    assert by_id["i-second"]["card_ids"] == []


def test_island_review_state_is_never_promoted_by_the_projection() -> None:
    ir = build_llm_input_ir(
        _source(
            [_card("c1")],
            islands=(SourceIsland(id="i1", card_ids=("c1",), title_reviewed=False),),
        )
    )
    assert ir["islands"][0]["review_state"] == "unreviewed"


# ---------------------------------------------------------------------------
# AC-2 (builder half): `cards[*].hold_state` -- spec §2.1 rule 8, ir_version 1.2
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("state", ["held", "pending", "shelved"])
def test_hold_state_is_projected_for_every_documented_value(state: str) -> None:
    ir = build_llm_input_ir(_source([_card("c1", hold_state=state), _card("c2", "beta")]))
    by_id = {card["id"]: card for card in ir["cards"]}
    assert by_id["c1"]["hold_state"] == state
    validate_llm_input_ir(ir)


def test_hold_state_key_is_omitted_for_an_active_card() -> None:
    """spec §2.1 rule 8: absence encodes "not held"; no `null` is written."""
    ir = build_llm_input_ir(_source([_card("c1"), _card("c2", "beta")]))
    assert all("hold_state" not in card for card in ir["cards"])


def test_unknown_hold_state_is_dropped_not_rejected() -> None:
    """Same treatment as an unknown relation type (§2.3 rule 6): a foreign value
    must not make an otherwise valid document un-projectable."""
    ir = build_llm_input_ir(
        _source([_card("c1", hold_state="frozen"), _card("c2", "beta")])
    )
    assert all("hold_state" not in card for card in ir["cards"])


def test_hold_state_is_read_from_the_document_adapter() -> None:
    document = DocumentV1.model_validate(
        {
            "version": 1,
            "id": "doc-hold",
            "createdAt": "2026-08-30T00:00:00Z",
            "updatedAt": "2026-08-30T00:00:00Z",
            "transform": {"panX": 0, "panY": 0, "zoom": 1},
            "cards": [
                {"id": "c1", "text": "alpha", "x": 0, "y": 0, "textReviewed": True,
                 "holdState": "shelved"},
                {"id": "c2", "text": "beta", "x": 1, "y": 1, "textReviewed": True},
            ],
            "edges": [],
            "islands": [],
        }
    )
    ir = build_llm_input_ir(source_from_document(document))
    assert held_card_ids(ir) == ["c1"]


def test_held_card_ids_covers_all_three_values_and_sorts() -> None:
    ir = build_llm_input_ir(
        _source(
            [
                _card("c3", hold_state="shelved"),
                _card("c1", "beta", hold_state="held"),
                _card("c2", "gamma", hold_state="pending"),
                _card("c4", "delta"),
            ]
        )
    )
    assert held_card_ids(ir) == ["c1", "c2", "c3"]


def test_hold_state_does_not_affect_the_derived_structure() -> None:
    """§7.4 (1.2): a hold state is a human's current reading, not structure, so
    it must not move centrality, components, clusters or the truncation order."""
    cards = [_card("c1", x=0, y=0), _card("c2", "beta", x=10, y=0)]
    relations = (SourceRelation(from_id="c1", to_id="c2", type="related"),)
    plain = build_llm_input_ir(_source(cards, relations=relations))
    held = build_llm_input_ir(
        _source(
            [_card("c1", x=0, y=0, hold_state="held"), _card("c2", "beta", x=10, y=0)],
            relations=relations,
        )
    )
    assert plain["graph_summary"] == held["graph_summary"]
    assert plain.get("cluster_candidates") == held.get("cluster_candidates")
    assert plain["relations"] == held["relations"]


def test_validate_rejects_a_hand_built_ir_with_an_unknown_hold_state() -> None:
    ir = build_llm_input_ir(_source([_card("c1"), _card("c2", "beta")]))
    ir["cards"][0]["hold_state"] = "archived"
    with pytest.raises(IRGenerationError) as exc:
        validate_llm_input_ir(ir)
    assert exc.value.code == "ir_schema_violation"


def test_relation_vocabulary_is_the_canvas_five(monkeypatch: pytest.MonkeyPatch) -> None:
    """ADR-0069 D2=A: five values; `unknown` and island edges are dropped."""
    ir = build_llm_input_ir(
        _source(
            [_card("c1"), _card("c2", "beta")],
            relations=(
                SourceRelation(from_id="c1", to_id="c2", type="causal"),
                SourceRelation(from_id="c1", to_id="c2", type="unknown"),
                SourceRelation(
                    from_id="c1", to_id="c2", type="related", from_kind="island"
                ),
                # duplicate of the first (spec §2.3 rule 3)
                SourceRelation(from_id="c1", to_id="c2", type="causal"),
            ),
        )
    )
    assert ir["relations"] == [
        {"id": "causal:c1:c2", "from": "c1", "to": "c2", "type": "causal"}
    ]


def test_evidence_links_carry_contradiction_state_but_not_notes() -> None:
    ir = build_llm_input_ir(
        _source(
            [_card("c1"), _card("c2", "beta")],
            evidence_links=(
                SourceEvidenceLink(
                    id="ev1",
                    type="contradicts",
                    from_card_id="c1",
                    to_card_id="c2",
                    contradiction_state="held",
                ),
            ),
        )
    )
    assert ir["evidence_links"] == [
        {
            "id": "ev1",
            "type": "contradicts",
            "from_card_id": "c1",
            "to_card_id": "c2",
            "contradiction_state": "held",
        }
    ]
    assert "note" not in canonical_ir_json(ir)
    assert adjudicated_contradiction(ir, "c1", "c2")["id"] == "ev1"
    assert adjudicated_contradiction(ir, "c1", "unknown-card") is None


@pytest.mark.parametrize("state", ["unconfirmed", "resolved", None])
def test_unadjudicated_states_are_not_suppressed(state: str | None) -> None:
    ir = build_llm_input_ir(
        _source(
            [_card("c1"), _card("c2", "beta")],
            evidence_links=(
                SourceEvidenceLink(
                    id="ev1",
                    type="contradicts",
                    from_card_id="c1",
                    to_card_id="c2",
                    contradiction_state=state,
                ),
            ),
        )
    )
    assert adjudicated_contradiction(ir, "c1", "c2") is None


def test_meta_omits_timestamps_when_the_input_has_none() -> None:
    """spec §2.4 rule 5: never fill a timestamp with `now` -- it breaks AC-3."""
    ir = build_llm_input_ir(_source([_card("c1")]))
    assert "created_at" not in ir["meta"]
    assert ir["meta"]["safe_mode"] is True


def test_graph_summary_is_referentially_closed() -> None:
    ir = build_llm_input_ir(
        _source(
            [_card("c1"), _card("c2", "beta"), _card("c3", "gamma")],
            relations=(SourceRelation(from_id="c1", to_id="c2", type="negate"),),
        )
    )
    card_ids = {card["id"] for card in ir["cards"]}
    summary = ir["graph_summary"]
    assert {row["card_id"] for row in summary["centrality"]} == card_ids
    assert summary["contradiction_subgraphs"] == [
        {
            "subgraph_id": "neg-001",
            "card_ids": ["c1", "c2"],
            "negation_edges": ["negate:c1:c2"],
            "summary": "1 negation edges across 2 cards",
        }
    ]
    # the isolated card still gets its own component (spec §3.3 rule 5)
    assert [row["component_id"] for row in summary["connected_components"]] == [
        "cmp-001",
        "cmp-002",
    ]


# ---------------------------------------------------------------------------
# AC-4: SafeMode refusal at IR generation (spec §7.1)
# ---------------------------------------------------------------------------


def test_ir_generation_fails_when_safe_mode_is_not_true() -> None:
    with pytest.raises(IRGenerationError) as excinfo:
        build_llm_input_ir(_source([_card("c1")]), safe_mode=False)
    assert excinfo.value.code == "safe_mode_required"


def test_ir_never_declares_safe_mode_off() -> None:
    ir = build_llm_input_ir(_source([_card("c1")]))
    assert ir["constraints"]["safe_mode"] is True
    assert ir["meta"]["safe_mode"] is True
    broken = json.loads(canonical_ir_json(ir))
    broken["constraints"]["safe_mode"] = False
    with pytest.raises(IRGenerationError) as excinfo:
        validate_llm_input_ir(broken)
    assert excinfo.value.code == "safe_mode_required"


def test_builder_rejects_unreviewed_text_independently_of_the_route() -> None:
    """Second SafeMode layer (ADR-0069): the builder checks review state itself.

    This is ADDITIVE to `routes/ai.py::_reject_unreviewed_cards`; see
    `test_ai_detect_contradiction_ir.py` for the proof that layer 1 still fires.
    """
    with pytest.raises(IRGenerationError) as excinfo:
        build_llm_input_ir(_source([_card("c1", reviewed=None)]))
    assert excinfo.value.code == "unreviewed_text_not_allowed"

    with pytest.raises(IRGenerationError):
        build_llm_input_ir(_source([_card("c1", reviewed=False)]))

    relaxed = build_llm_input_ir(
        _source([_card("c1", reviewed=False)]), allow_unreviewed_text=True
    )
    # Relaxation covers review state only; safe_mode itself stays const true.
    assert relaxed["constraints"]["safe_mode"] is True


# ---------------------------------------------------------------------------
# AC-5: PII minimization (§7.2) and structured-text-only (§7.3)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "text",
    [
        "contact me at someone@example.com please",
        "call +81 90-1234-5678 today",
        "see https://example.com/x?token=abcdef",
        "https://example.com/x?SECRET=zzz",
    ],
)
def test_pii_in_card_text_fails_ir_generation(text: str) -> None:
    with pytest.raises(IRGenerationError) as excinfo:
        build_llm_input_ir(_source([_card("c1", text)]))
    assert excinfo.value.code == "pii_detected"


def test_pii_error_does_not_reflect_the_offending_value() -> None:
    """SEC-VALIDATION-LEAK-01: the very value we refuse must not travel back."""
    secret = "leak-me@example.com"
    with pytest.raises(IRGenerationError) as excinfo:
        build_llm_input_ir(_source([_card("c1", f"reach {secret} now")]))
    assert secret not in excinfo.value.message
    assert secret not in str(excinfo.value)
    assert "email" in excinfo.value.message


def test_pii_check_exempts_ids_and_timestamps() -> None:
    """A UUID-ish id or an ISO timestamp matches the phone pattern; exempting
    them is what keeps ordinary documents projectable (spec §7.2)."""
    ir = build_llm_input_ir(
        _source(
            [_card("0123-4567-8901-2345", "alpha")],
            created_at="2026-01-01T00:00:00Z",
            updated_at="2026-01-02T00:00:00Z",
        )
    )
    assert ir["cards"][0]["id"] == "0123-4567-8901-2345"
    assert ir["meta"]["created_at"] == "2026-01-01T00:00:00Z"


def test_metadata_email_still_fails() -> None:
    source = IRSource(doc_id="owner@example.com", doc_version=1, cards=(_card("c1"),))
    with pytest.raises(IRGenerationError) as excinfo:
        build_llm_input_ir(source)
    assert excinfo.value.code == "pii_detected"


def test_base64_pseudo_binary_is_rejected() -> None:
    blob = "QUJD" * 300  # 1200 chars, base64 alphabet only
    with pytest.raises(IRGenerationError) as excinfo:
        build_llm_input_ir(_source([_card("c1", blob)]))
    assert excinfo.value.code == "structured_text_only_violation"


def test_forbidden_key_names_are_rejected() -> None:
    ir = build_llm_input_ir(_source([_card("c1")]))
    from kj_atlas_api.llm_input_ir import _enforce_structured_text_only

    for key in ("attachments", "binary", "image", "IMAGE"):
        poisoned = json.loads(canonical_ir_json(ir))
        poisoned[key] = "x"
        with pytest.raises(IRGenerationError) as excinfo:
            _enforce_structured_text_only(poisoned)
        assert excinfo.value.code == "structured_text_only_violation"

    # spec §7.3: exact match only -- `imageUrl` must NOT be caught.
    allowed = json.loads(canonical_ir_json(ir))
    allowed["imageUrl"] = "x"
    _enforce_structured_text_only(allowed)


def test_structured_text_only_flag_is_declared() -> None:
    ir = build_llm_input_ir(_source([_card("c1")]))
    assert ir["constraints"]["structured_text_only"] is True


# ---------------------------------------------------------------------------
# AC-6: deterministic truncation (§5)
# ---------------------------------------------------------------------------


def _oversized_source(card_count: int, text: str = "alpha") -> IRSource:
    cards = [_card(f"c{index:04d}", f"{text}-{index}") for index in range(card_count)]
    relations = [
        SourceRelation(from_id=f"c{index:04d}", to_id=f"c{index + 1:04d}", type="related")
        for index in range(card_count - 1)
    ]
    return _source(cards, relations=tuple(relations))


def test_truncation_is_deterministic_for_the_same_input() -> None:
    source = _oversized_source(MAX_CARDS + 60)
    first = build_llm_input_ir(source)
    second = build_llm_input_ir(source)
    assert canonical_ir_json(first) == canonical_ir_json(second)
    assert ir_sha256(first) == ir_sha256(second)
    assert first["truncation"]["truncated"] is True
    assert "MAX_CARDS" in first["truncation"]["reason_codes"]
    assert len(first["cards"]) == MAX_CARDS


def test_truncation_is_independent_of_input_card_order() -> None:
    source = _oversized_source(MAX_CARDS + 60)
    shuffled = IRSource(
        doc_id=source.doc_id,
        doc_version=source.doc_version,
        cards=tuple(reversed(source.cards)),
        relations=tuple(reversed(source.relations)),
    )
    assert ir_sha256(build_llm_input_ir(source)) == ir_sha256(build_llm_input_ir(shuffled))


def test_truncation_keeps_the_ir_referentially_closed() -> None:
    source = _oversized_source(MAX_CARDS + 40)
    islands = (SourceIsland(id="i1", card_ids=tuple(c.id for c in source.cards)),)
    middle = len(source.cards) // 2
    evidence = tuple(
        SourceEvidenceLink(
            id=f"ev{index}",
            type="contradicts",
            from_card_id=source.cards[index].id,
            to_card_id=source.cards[index + 1].id,
            contradiction_state="unconfirmed",
        )
        # The path graph's centre survives truncation, so at least one link must
        # remain -- an empty list would make the closure assertion vacuous.
        for index in range(middle - 5, middle + 5)
    ) + (
        SourceEvidenceLink(
            id="ev-dropped",
            type="contradicts",
            from_card_id=source.cards[0].id,
            to_card_id=source.cards[1].id,
            contradiction_state="unconfirmed",
        ),
    )
    ir = build_llm_input_ir(
        IRSource(
            doc_id="doc-1",
            doc_version=1,
            cards=source.cards,
            relations=source.relations,
            islands=islands,
            evidence_links=evidence,
        )
    )
    card_ids = {card["id"] for card in ir["cards"]}
    assert len(card_ids) == MAX_CARDS
    for relation in ir["relations"]:
        assert relation["from"] in card_ids and relation["to"] in card_ids
    for island in ir["islands"]:
        assert set(island["card_ids"]) <= card_ids
    assert ir["evidence_links"], "the surviving centre should keep some links"
    for link in ir["evidence_links"]:
        assert {link["from_card_id"], link["to_card_id"]} <= card_ids
    assert "ev-dropped" not in {link["id"] for link in ir["evidence_links"]}
    # spec §5.2 step 1: the optional derived block goes first.
    assert "cluster_candidates" not in ir


def test_text_budget_truncation_records_its_reason_and_actually_fits() -> None:
    long_text = "あ" * 900
    cards = [_card(f"c{index:03d}", f"{long_text}{index}") for index in range(40)]
    ir = build_llm_input_ir(_source(cards))
    assert ir["truncation"]["truncated"] is True
    assert "MAX_TEXT_CHARS" in ir["truncation"]["reason_codes"]
    assert sum(card["char_len"] for card in ir["cards"]) <= MAX_TEXT_CHARS
    for card in ir["cards"]:
        assert card["char_len"] == len(card["text_norm"]) <= 240


def test_relation_budget_truncation() -> None:
    cards = [_card(f"c{index:03d}", f"alpha-{index}") for index in range(40)]
    relations = tuple(
        SourceRelation(from_id=f"c{a:03d}", to_id=f"c{b:03d}", type="related")
        for a in range(40)
        for b in range(40)
        if a < b
    )
    assert len(relations) > MAX_RELATIONS
    ir = build_llm_input_ir(_source(cards, relations=relations))
    assert len(ir["relations"]) == MAX_RELATIONS
    assert "MAX_RELATIONS" in ir["truncation"]["reason_codes"]
    assert ir["relations"] == sorted(
        ir["relations"], key=lambda item: (item["type"], item["from"], item["to"])
    )


def test_reason_codes_have_a_fixed_order() -> None:
    ir = build_llm_input_ir(_source([_card("c1")]))
    assert ir["truncation"] == {"truncated": False, "reason_codes": []}


# ---------------------------------------------------------------------------
# Input validation (spec §2)
# ---------------------------------------------------------------------------


def test_duplicate_card_id_is_rejected() -> None:
    with pytest.raises(IRGenerationError) as excinfo:
        build_llm_input_ir(_source([_card("c1"), _card("c1", "beta")]))
    assert excinfo.value.code == "duplicate_card_id"


def test_non_negate_self_loop_is_rejected() -> None:
    with pytest.raises(IRGenerationError) as excinfo:
        build_llm_input_ir(
            _source(
                [_card("c1")],
                relations=(SourceRelation(from_id="c1", to_id="c1", type="related"),),
            )
        )
    assert excinfo.value.code == "invalid_self_loop"


def test_control_characters_are_stripped() -> None:
    raw = "al" + chr(1) + "pha" + chr(127) + "  b"
    ir = build_llm_input_ir(_source([_card("c1", raw)]))
    assert ir["cards"][0]["text"] == "alpha  b"
    assert ir["cards"][0]["text_norm"] == "alpha b"


def test_empty_card_list_is_rejected() -> None:
    with pytest.raises(IRGenerationError) as excinfo:
        build_llm_input_ir(_source([]))
    assert excinfo.value.code == "empty_cards"


# ---------------------------------------------------------------------------
# AC-8 (narrowed): the spec §6 fixture round trip
# ---------------------------------------------------------------------------


def test_fixture_is_reproducible_from_the_document_alone() -> None:
    """spec §6 / AC-1 + AC-4: the IR is derivable from the document with no LLM."""
    document = DocumentV1.model_validate(
        json.loads(DOCUMENT_FIXTURE.read_text(encoding="utf-8"))
    )
    expected = json.loads(EXPECTED_FIXTURE.read_text(encoding="utf-8"))

    ir = build_llm_input_ir(source_from_document(document), include_coordinates=False)
    validate_llm_input_ir(ir)

    assert expected["irVersion"] == IR_VERSION
    assert ir == expected["ir"]
    assert ir_sha256(ir) == expected["sha256"]


def test_fixture_generator_reports_no_drift() -> None:
    import subprocess
    import sys

    backend_root = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [sys.executable, str(backend_root / "scripts" / "generate_llm_input_ir_fixture.py"), "--check"],
        capture_output=True,
        text=True,
        cwd=str(backend_root),
    )
    assert result.returncode == 0, result.stderr
