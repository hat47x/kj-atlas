"""LLM input IR builder (`LLMRequest.inputs`).

Normative source: `02_Architecture/llm_input_ir_spec.md` (`ir_version` 1.2).
Decision record: `ADR-0069` (D1=B coordinates optional, D2=A five-value relation
vocabulary, D3=A `islands` distinct from `cluster_candidates`, D4=A the
projection lives on the server so SafeMode can be enforced here).

This module is deliberately free of FastAPI/SQLAlchemy imports: it is a pure,
deterministic projection so that the same document always yields the same IR
(spec AC-1 / AC-3) and so that fixtures can be regenerated without a provider.

SafeMode note (`ADR-0069` "ADR-0068 との関係", AGENTS.md §7): the review-state
check in `_enforce_safe_mode` is an ADDITIONAL layer. It does not replace the
route-level `_reject_unreviewed_cards` / `_reject_unreviewed_text` guards that
`SEC-AI-SAFEMODE-01` shipped; both must run.
"""

from __future__ import annotations

import json
import math
import re
import unicodedata
from collections import deque
from dataclasses import dataclass, field
from hashlib import sha256
from typing import Any, Iterable, Sequence

# ---------------------------------------------------------------------------
# Constants (spec §4.2, §5.1)
# ---------------------------------------------------------------------------

IR_VERSION = "1.2"

MAX_CARDS = 200
MAX_RELATIONS = 400
MAX_TEXT_CHARS = 12000
#: spec §5.2 step 4: the fixed per-card cut applied when MAX_TEXT_CHARS is hit.
TRUNCATED_TEXT_CHARS = 240

#: ADR-0048 D3 / ADR-0069 D2=A. `unknown` is deliberately absent: an
#: unclassified edge carries no structure, so it is dropped, not mapped.
RELATION_TYPES: tuple[str, ...] = ("related", "negate", "causal", "mutual", "equivalence")

#: spec §4.2 `constraints.required_sections`.
REQUIRED_SECTIONS: tuple[str, ...] = ("overall", "clusters", "contradictions")

EVIDENCE_TYPES: tuple[str, ...] = ("supports", "contradicts")
CONTRADICTION_STATES: tuple[str, ...] = ("unconfirmed", "confirmed", "held", "resolved")

#: spec §2.1 rule 8 (ir_version 1.2) / `schemas.md` §14.1 `Card.holdState`.
#: An absent value is the ordinary, active card; every listed value records that
#: a human has deliberately set the card aside (`held` = judgement withheld,
#: `pending` = not yet worked, `shelved` = moved to the shelf).
HOLD_STATES: tuple[str, ...] = ("held", "pending", "shelved")

#: spec §2.2B rule 6 / issue AI-IR-PROJECTION-01 AC-1: states a human has
#: already adjudicated. A consumer must not re-surface these as new findings.
ADJUDICATED_CONTRADICTION_STATES: frozenset[str] = frozenset({"confirmed", "held"})

#: spec §3.1 rule 6.
SPATIAL_NEIGHBOUR_K = 3

# spec §7.2
_PII_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("email", re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")),
    ("phone", re.compile(r"\+?[0-9][0-9\- ]{8,}[0-9]")),
    ("url_token", re.compile(r"[?&](token|key|secret|password)=", re.IGNORECASE)),
)

#: spec §7.2: timestamps are structurally indistinguishable from the phone
#: pattern, so they are never scanned (they are not free-form text anyway).
_META_PII_EXEMPT_KEYS: frozenset[str] = frozenset({"created_at", "updated_at"})

# spec §7.3
_FORBIDDEN_KEYS: frozenset[str] = frozenset({"attachments", "binary", "image"})
_BASE64_MAX_LEN = 1024
_BASE64_ONLY = re.compile(r"^[A-Za-z0-9+/=]+$")

#: spec §2.1 rule 2.
_CONTROL_CHARS = re.compile("[\u0000-\u001f\u007f]")
_WHITESPACE_RUN = re.compile(r"\s+")

# spec §2.4 rule 6.
_JA_RANGES = (
    (0x3040, 0x30FF),
    (0x3400, 0x4DBF),
    (0x4E00, 0x9FFF),
    (0xF900, 0xFAFF),
)
_EN_CHARS = re.compile(r"[A-Za-z]")


class IRGenerationError(Exception):
    """IR generation refused (spec §7.1 / §7.2 / §7.3, or invalid input).

    `code` is a stable machine token. `message` never reflects the offending
    input value -- `SEC-VALIDATION-LEAK-01` forbids echoing request content into
    an error, and a PII match is exactly the value that must not travel back.
    """

    def __init__(self, code: str, message: str) -> None:
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message

    def to_contract(self) -> dict[str, str]:
        return {"code": self.code, "message": self.message}


# ---------------------------------------------------------------------------
# Source shapes -- the builder's input, decoupled from the Pydantic models so a
# document-less route (detect-contradiction with two bare cards) can use it too.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SourceCard:
    id: str
    text: str
    text_reviewed: bool | None = None
    x: float | None = None
    y: float | None = None
    #: `DocumentV1.cards[*].holdState` (spec §2.1 rule 8, ir_version 1.2).
    hold_state: str | None = None


@dataclass(frozen=True)
class SourceRelation:
    from_id: str
    to_id: str
    type: str
    from_kind: str | None = None
    to_kind: str | None = None


@dataclass(frozen=True)
class SourceIsland:
    id: str
    card_ids: tuple[str, ...] = ()
    title: str | None = None
    placard_card_id: str | None = None
    parent_island_id: str | None = None
    title_reviewed: bool | None = None


@dataclass(frozen=True)
class SourceEvidenceLink:
    id: str
    type: str
    from_card_id: str
    to_card_id: str
    contradiction_state: str | None = None


@dataclass(frozen=True)
class IRSource:
    doc_id: str
    doc_version: int
    cards: tuple[SourceCard, ...]
    relations: tuple[SourceRelation, ...] = ()
    islands: tuple[SourceIsland, ...] = ()
    evidence_links: tuple[SourceEvidenceLink, ...] = ()
    #: Omitted (spec §2.4 rule 5) when the input carries no timestamps. Never
    #: filled with "now" -- that would break determinism (spec AC-3).
    created_at: str | None = None
    updated_at: str | None = None


@dataclass
class _NormalizedCard:
    id: str
    text: str
    text_norm: str
    char_len: int
    text_reviewed: bool | None
    x: float | None
    y: float | None
    hold_state: str | None = None


@dataclass
class _Truncation:
    truncated: bool = False
    reasons: set[str] = field(default_factory=set)

    def to_ir(self) -> dict[str, Any]:
        order = ("MAX_CARDS", "MAX_RELATIONS", "MAX_TEXT_CHARS")
        return {
            "truncated": self.truncated,
            "reason_codes": [code for code in order if code in self.reasons],
        }


# ---------------------------------------------------------------------------
# DocumentV1 adapter
# ---------------------------------------------------------------------------


def source_from_document(document: Any) -> IRSource:
    """Project a `DocumentV1` (or any duck-typed equivalent) onto `IRSource`.

    Nothing is rejected here; §2.3 rule 6's *exclusions* (island edges, unknown
    relation types, dangling endpoints) happen during normalization so that a
    document the server already accepts stays usable.
    """
    cards = tuple(
        SourceCard(
            id=getattr(card, "id", ""),
            text=getattr(card, "text", ""),
            text_reviewed=getattr(card, "textReviewed", None),
            x=getattr(card, "x", None),
            y=getattr(card, "y", None),
            hold_state=getattr(card, "holdState", None),
        )
        for card in getattr(document, "cards", []) or []
    )
    relations = tuple(
        SourceRelation(
            from_id=getattr(edge, "fromId", ""),
            to_id=getattr(edge, "toId", ""),
            type=getattr(edge, "type", ""),
            from_kind=getattr(edge, "fromKind", None),
            to_kind=getattr(edge, "toKind", None),
        )
        for edge in getattr(document, "edges", []) or []
    )
    islands = tuple(
        SourceIsland(
            id=getattr(island, "id", ""),
            card_ids=tuple(getattr(island, "cardIds", []) or []),
            title=getattr(island, "title", None),
            placard_card_id=getattr(island, "placardCardId", None),
            parent_island_id=getattr(island, "parentIslandId", None),
            title_reviewed=getattr(island, "titleReviewed", None),
        )
        for island in getattr(document, "islands", []) or []
    )
    evidence_links = tuple(
        SourceEvidenceLink(
            id=getattr(link, "id", ""),
            type=getattr(link, "type", ""),
            from_card_id=getattr(link, "fromCardId", ""),
            to_card_id=getattr(link, "toCardId", ""),
            contradiction_state=getattr(link, "contradictionState", None),
        )
        for link in getattr(document, "evidenceLinks", None) or []
    )
    return IRSource(
        doc_id=str(getattr(document, "id", "") or ""),
        doc_version=int(getattr(document, "version", 1) or 1),
        cards=cards,
        relations=relations,
        islands=islands,
        evidence_links=evidence_links,
        created_at=_iso_or_none(getattr(document, "createdAt", None)),
        updated_at=_iso_or_none(getattr(document, "updatedAt", None)),
    )


def _iso_or_none(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        return value or None
    isoformat = getattr(value, "isoformat", None)
    if callable(isoformat):
        return str(isoformat())
    return str(value)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def build_llm_input_ir(
    source: IRSource,
    *,
    include_coordinates: bool = False,
    safe_mode: bool = True,
    allow_unreviewed_text: bool = False,
    required_card_ids: Sequence[str] = (),
) -> dict[str, Any]:
    """Build `LLMRequest.inputs` per `llm_input_ir_spec.md` §2-§7.

    `include_coordinates` implements ADR-0069 D1=B: the caller declares whether
    this endpoint needs relative placement (§2.2.1). Only `suggest-layout` does.

    `required_card_ids` is an input-only route contract. A caller may name cards
    whose meaning is indispensable for that operation; those cards are reserved
    before deterministic size truncation. The ids are not serialized into the
    IR, and an empty sequence preserves the historical projection byte-for-byte.
    """
    # spec §7.1 -- checked first so a relaxed-SafeMode caller never even reaches
    # normalization. `constraints.safe_mode` is `const true`; there is no IR
    # that declares SafeMode off.
    if safe_mode is not True:
        raise IRGenerationError(
            "safe_mode_required",
            "IR generation requires safe_mode=true (llm_input_ir_spec.md 7.1).",
        )

    cards = _normalize_cards(source.cards)
    _enforce_safe_mode(cards, allow_unreviewed_text=allow_unreviewed_text)

    meta = _build_meta(source, cards)
    # spec §7.2: run BEFORE truncation. Checking only the truncated IR would let
    # a PII string past whenever it sat beyond the 240-character cut.
    _enforce_pii_minimization(cards, meta)

    card_ids = {card.id for card in cards}
    required = frozenset(required_card_ids)
    if not required <= card_ids:
        raise IRGenerationError(
            "required_card_missing",
            "A route-required card is not present in the normalized IR source.",
        )
    if len(required) > MAX_CARDS:
        raise IRGenerationError(
            "required_card_budget_exceeded",
            "The route-required card set exceeds the IR card budget.",
        )

    relations = _normalize_relations(source.relations, card_ids)
    islands = _normalize_islands(source.islands, card_ids)
    evidence_links = _normalize_evidence_links(source.evidence_links, card_ids)

    # spec §5.2 rule 6: the drop order uses ranks computed once, on the full
    # set, before any truncation.
    rank_by_card = _rank_by_card(cards, relations)
    cards, relations, islands, evidence_links, truncation = _apply_truncation(
        cards,
        relations,
        islands,
        evidence_links,
        rank_by_card,
        required_card_ids=required,
    )

    ir: dict[str, Any] = {"ir_version": IR_VERSION}
    ir["cards"] = [_card_to_ir(card) for card in cards]
    if include_coordinates:
        coordinates = _normalize_coordinates(cards)
        if coordinates:
            ir["coordinates"] = coordinates
    ir["relations"] = [dict(relation) for relation in relations]
    if islands:
        ir["islands"] = islands
    if evidence_links:
        ir["evidence_links"] = evidence_links

    # spec §5.2 step 1: cluster candidates are the first thing dropped, being
    # the only optional derived block.
    if not truncation.truncated:
        clusters = _cluster_candidates(
            cards, relations, spatial=include_coordinates
        )
        if clusters:
            ir["cluster_candidates"] = clusters

    ir["graph_summary"] = _graph_summary(cards, relations)
    ir["constraints"] = {
        "safe_mode": True,
        "structured_text_only": True,
        "required_sections": list(REQUIRED_SECTIONS),
    }
    ir["meta"] = meta
    ir["truncation"] = truncation.to_ir()

    # spec §7.3 -- last, so it sees exactly what will be serialized.
    _enforce_structured_text_only(ir)
    return ir


# ---------------------------------------------------------------------------
# §2 normalization
# ---------------------------------------------------------------------------


def _normalize_cards(source_cards: Sequence[SourceCard]) -> list[_NormalizedCard]:
    if not source_cards:
        raise IRGenerationError(
            "empty_cards", "IR generation requires at least one card."
        )

    seen: set[str] = set()
    normalized: list[_NormalizedCard] = []
    for card in source_cards:
        card_id = card.id
        if not isinstance(card_id, str) or card_id == "":
            raise IRGenerationError("invalid_card_id", "Card id must be a non-empty string.")
        if card_id in seen:  # spec §2.1 rule 5
            raise IRGenerationError(
                "duplicate_card_id", "The same card id appeared more than once."
            )
        seen.add(card_id)

        text = _CONTROL_CHARS.sub("", card.text or "")
        text_norm = _WHITESPACE_RUN.sub(" ", unicodedata.normalize("NFKC", text)).strip()
        if text == "" or text_norm == "":
            raise IRGenerationError(
                "empty_card_text",
                "Card text normalized to an empty string, which the IR schema forbids.",
            )
        normalized.append(
            _NormalizedCard(
                id=card_id,
                text=text,
                text_norm=text_norm,
                char_len=len(text_norm),
                text_reviewed=card.text_reviewed,
                x=card.x,
                y=card.y,
                # spec §2.1 rule 8: an unknown value is dropped rather than
                # rejected, the same way an unknown relation type is (§2.3
                # rule 6) -- a foreign hold state carries no structure the IR
                # can use, but it must not make the document un-projectable.
                hold_state=card.hold_state if card.hold_state in HOLD_STATES else None,
            )
        )
    normalized.sort(key=lambda card: card.id)
    return normalized


def _card_to_ir(card: _NormalizedCard) -> dict[str, Any]:
    """spec §2.1. `hold_state` is emitted only when the card carries one.

    Absent means the ordinary active card, which is the overwhelming majority;
    writing `"hold_state": null` on every card would cost tokens on every
    request to say nothing, and §2.1 rule 8 fixes the omission as the encoding
    of "active" (unlike `islands`, where §2.2A requires explicit nulls because
    an absent title and an untitled island are different states).
    """
    ir_card: dict[str, Any] = {
        "id": card.id,
        "text": card.text,
        "text_norm": card.text_norm,
        "char_len": card.char_len,
    }
    if card.hold_state is not None:
        ir_card["hold_state"] = card.hold_state
    return ir_card


def _normalize_coordinates(cards: Sequence[_NormalizedCard]) -> list[dict[str, Any]]:
    placed = [card for card in cards if _is_finite(card.x) and _is_finite(card.y)]
    if not placed:
        return []
    for card in cards:
        # A card carrying a non-finite coordinate is an input error, not a card
        # that merely lacks placement (spec §2.2 rule 1).
        if (card.x is not None and not _is_finite(card.x)) or (
            card.y is not None and not _is_finite(card.y)
        ):
            raise IRGenerationError(
                "invalid_coordinate", "Coordinates must be finite numbers (no NaN/Inf)."
            )

    cx = sum(float(card.x) for card in placed) / len(placed)
    cy = sum(float(card.y) for card in placed) / len(placed)
    coordinates: list[dict[str, Any]] = []
    for card in placed:
        x = round(float(card.x) - cx, 3)
        y = round(float(card.y) - cy, 3)
        coordinates.append(
            {
                "card_id": card.id,
                "x": x,
                "y": y,
                "radius": round(math.sqrt(x * x + y * y), 3),
                "angle_deg": round(math.degrees(math.atan2(y, x)), 3),
            }
        )
    coordinates.sort(key=lambda item: item["card_id"])
    return coordinates


def _is_finite(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def _normalize_relations(
    source_relations: Sequence[SourceRelation], card_ids: set[str]
) -> list[dict[str, str]]:
    seen: set[tuple[str, str, str]] = set()
    relations: list[dict[str, str]] = []
    for relation in source_relations:
        # spec §2.3 rule 6: exclusions (not rejections).
        if relation.from_kind == "island" or relation.to_kind == "island":
            continue
        if relation.type not in RELATION_TYPES:
            continue
        if relation.from_id not in card_ids or relation.to_id not in card_ids:
            continue
        # spec §2.3 rule 4
        if relation.from_id == relation.to_id and relation.type != "negate":
            raise IRGenerationError(
                "invalid_self_loop",
                "A self-loop relation is only allowed for the negate type.",
            )
        key = (relation.from_id, relation.to_id, relation.type)
        if key in seen:  # spec §2.3 rule 3
            continue
        seen.add(key)
        relations.append(
            {
                "id": relation_id(relation.type, relation.from_id, relation.to_id),
                "from": relation.from_id,
                "to": relation.to_id,
                "type": relation.type,
            }
        )
    relations.sort(key=lambda item: (item["type"], item["from"], item["to"]))
    return relations


def relation_id(relation_type: str, from_id: str, to_id: str) -> str:
    """spec §1: `"<type>:<fromId>:<toId>"`."""
    return f"{relation_type}:{from_id}:{to_id}"


def _normalize_islands(
    source_islands: Sequence[SourceIsland], card_ids: set[str]
) -> list[dict[str, Any]]:
    """spec §2.2A. Card->island uniqueness is FIRST-MATCH-WINS.

    `issue-DOMAIN-ISLAND-MEMBERSHIP-01` established this as the interim
    read-side rule (it is what `getIslandsForCard()` already does). A card that
    appears in several islands' `cardIds` is attributed to the first island in
    document order; later islands simply do not list it.
    """
    seen_ids: set[str] = set()
    claimed: set[str] = set()
    island_ids = {island.id for island in source_islands if island.id}
    islands: list[dict[str, Any]] = []
    for island in source_islands:
        if not island.id:
            raise IRGenerationError("invalid_island_id", "Island id must be a non-empty string.")
        if island.id in seen_ids:
            raise IRGenerationError(
                "duplicate_island_id", "The same island id appeared more than once."
            )
        seen_ids.add(island.id)

        members: list[str] = []
        for card_id in island.card_ids:
            if card_id not in card_ids or card_id in claimed:
                continue
            claimed.add(card_id)
            members.append(card_id)
        members.sort()

        parent = island.parent_island_id
        if parent is not None and (parent not in island_ids or parent == island.id):
            parent = None
        placard = island.placard_card_id
        if placard is not None and placard not in members:
            placard = None

        islands.append(
            {
                "id": island.id,
                "card_ids": members,
                "title": island.title,
                "placard_card_id": placard,
                "parent_island_id": parent,
                # spec §2.2A rule 6 / CE0-REVIEW-IF: only a human sets this.
                "review_state": "human_reviewed" if island.title_reviewed is True else "unreviewed",
            }
        )
    islands.sort(key=lambda item: item["id"])
    return islands


def _normalize_evidence_links(
    source_links: Sequence[SourceEvidenceLink], card_ids: set[str]
) -> list[dict[str, Any]]:
    """spec §2.2B. `note` is deliberately not projected (PII minimization)."""
    seen: set[tuple[str, str, str]] = set()
    links: list[dict[str, Any]] = []
    for link in source_links:
        if link.type not in EVIDENCE_TYPES:
            continue
        if link.from_card_id not in card_ids or link.to_card_id not in card_ids:
            continue
        key = (link.type, link.from_card_id, link.to_card_id)
        if key in seen:
            continue
        seen.add(key)
        state = link.contradiction_state
        if link.type != "contradicts" or state not in CONTRADICTION_STATES:
            state = None
        links.append(
            {
                "id": link.id,
                "type": link.type,
                "from_card_id": link.from_card_id,
                "to_card_id": link.to_card_id,
                "contradiction_state": state,
            }
        )
    links.sort(key=lambda item: (item["type"], item["from_card_id"], item["to_card_id"]))
    return links


def _build_meta(source: IRSource, cards: Sequence[_NormalizedCard]) -> dict[str, Any]:
    doc_id = source.doc_id or "(no-document)"
    doc_version = source.doc_version if isinstance(source.doc_version, int) else 1
    if doc_version < 1:
        doc_version = 1
    meta: dict[str, Any] = {
        "doc_id": doc_id,
        "doc_version": doc_version,
        "safe_mode": True,  # spec §7.1: const true.
        "language": _detect_language(cards),
    }
    # spec §2.4 rule 5: omit rather than invent a timestamp.
    if source.created_at:
        meta["created_at"] = source.created_at
    if source.updated_at:
        meta["updated_at"] = source.updated_at
    return meta


def _detect_language(cards: Sequence[_NormalizedCard]) -> str:
    joined = "".join(card.text_norm for card in cards)
    has_ja = any(
        any(low <= ord(char) <= high for low, high in _JA_RANGES) for char in joined
    )
    has_en = bool(_EN_CHARS.search(joined))
    if has_ja and has_en:
        return "mixed"
    if has_ja:
        return "ja"
    if has_en:
        return "en"
    return "unknown"


# ---------------------------------------------------------------------------
# §7 safety checks
# ---------------------------------------------------------------------------


def _enforce_safe_mode(
    cards: Sequence[_NormalizedCard], *, allow_unreviewed_text: bool
) -> None:
    """Second, independent SafeMode layer (spec §7.1, ADR-0069 defense-in-depth).

    The route-level `_reject_unreviewed_cards` / `_reject_unreviewed_text`
    guards from `SEC-AI-SAFEMODE-01` still run first and MUST NOT be removed.
    This check exists so the IR itself refuses to carry unreviewed text even if
    a future caller forgets the route guard.
    """
    if allow_unreviewed_text:
        return
    if any(card.text_reviewed is not True for card in cards):
        raise IRGenerationError(
            "unreviewed_text_not_allowed",
            "The IR cannot carry unreviewed card text under SafeMode.",
        )


def _enforce_pii_minimization(
    cards: Sequence[_NormalizedCard], meta: dict[str, Any]
) -> None:
    """spec §7.2.

    Card prose is checked against all three patterns. `meta` is checked against
    the email / url_token patterns only: the phone pattern is a digit-run
    matcher, and every ISO-8601 timestamp (`2026-01-01T00:00:00Z`) and many
    identifiers match it, which would make ordinary documents un-projectable.
    Ids elsewhere in the IR are exempt for the same reason.
    """
    for card in cards:
        for value in (card.text, card.text_norm):
            for label, pattern in _PII_PATTERNS:
                if pattern.search(value):
                    raise IRGenerationError(
                        "pii_detected",
                        f"Card text matched the {label} pattern; the IR refuses to carry it.",
                    )

    for key, value in meta.items():
        if key in _META_PII_EXEMPT_KEYS or not isinstance(value, str):
            continue
        for label, pattern in _PII_PATTERNS:
            if label == "phone":
                continue
            if pattern.search(value):
                raise IRGenerationError(
                    "pii_detected",
                    f"Metadata matched the {label} pattern; the IR refuses to carry it.",
                )


def _enforce_structured_text_only(node: Any, *, _depth: int = 0) -> None:
    """spec §7.3, applied recursively to the assembled IR."""
    if isinstance(node, dict):
        for key, value in node.items():
            if not isinstance(key, str):
                raise IRGenerationError(
                    "structured_text_only_violation", "Object keys must be strings."
                )
            if key.lower() in _FORBIDDEN_KEYS:
                raise IRGenerationError(
                    "structured_text_only_violation",
                    f"The key '{key}' is not allowed in the IR (binary/attachment surface).",
                )
            _enforce_structured_text_only(value, _depth=_depth + 1)
        return
    if isinstance(node, list):
        for item in node:
            _enforce_structured_text_only(item, _depth=_depth + 1)
        return
    if isinstance(node, str):
        if len(node) > _BASE64_MAX_LEN and _BASE64_ONLY.fullmatch(node):
            raise IRGenerationError(
                "structured_text_only_violation",
                "A value looks like embedded base64 binary, which the IR forbids.",
            )
        return
    if node is None or isinstance(node, (bool, int)):
        return
    if isinstance(node, float):
        if not math.isfinite(node):
            raise IRGenerationError(
                "structured_text_only_violation", "Numbers must be finite JSON values."
            )
        return
    raise IRGenerationError(
        "structured_text_only_violation",
        "The IR may only contain string/number/boolean/array/object/null values.",
    )


# ---------------------------------------------------------------------------
# §3 non-LLM preprocessing
# ---------------------------------------------------------------------------


def _undirected_adjacency(
    card_ids: Sequence[str], relations: Iterable[dict[str, str]]
) -> dict[str, list[str]]:
    """spec §3.2 rule 5: multi-edges collapse to one, self-loops are ignored."""
    pairs: set[tuple[str, str]] = set()
    for relation in relations:
        a, b = relation["from"], relation["to"]
        if a == b:
            continue
        pairs.add((a, b) if a <= b else (b, a))
    adjacency: dict[str, set[str]] = {card_id: set() for card_id in card_ids}
    for a, b in pairs:
        adjacency[a].add(b)
        adjacency[b].add(a)
    return {card_id: sorted(neighbours) for card_id, neighbours in adjacency.items()}


def _betweenness(card_ids: Sequence[str], adjacency: dict[str, list[str]]) -> dict[str, float]:
    """Brandes, unnormalized, undirected (spec §3.2 rule 7)."""
    scores = {card_id: 0.0 for card_id in card_ids}
    for source in card_ids:
        stack: list[str] = []
        predecessors: dict[str, list[str]] = {card_id: [] for card_id in card_ids}
        sigma = {card_id: 0.0 for card_id in card_ids}
        sigma[source] = 1.0
        distance = {card_id: -1 for card_id in card_ids}
        distance[source] = 0
        queue: deque[str] = deque([source])
        while queue:
            v = queue.popleft()
            stack.append(v)
            for w in adjacency[v]:
                if distance[w] < 0:
                    distance[w] = distance[v] + 1
                    queue.append(w)
                if distance[w] == distance[v] + 1:
                    sigma[w] += sigma[v]
                    predecessors[w].append(v)
        delta = {card_id: 0.0 for card_id in card_ids}
        while stack:
            w = stack.pop()
            for v in predecessors[w]:
                delta[v] += (sigma[v] / sigma[w]) * (1.0 + delta[w])
            if w != source:
                scores[w] += delta[w]
    # Every unordered pair was traversed from both endpoints.
    return {card_id: value / 2.0 for card_id, value in scores.items()}


def _centrality(
    cards: Sequence[_NormalizedCard], relations: Sequence[dict[str, str]]
) -> list[dict[str, Any]]:
    card_ids = [card.id for card in cards]
    adjacency = _undirected_adjacency(card_ids, relations)
    betweenness = _betweenness(card_ids, adjacency)
    rows = [
        {
            "card_id": card_id,
            "degree": len(adjacency[card_id]),
            "betweenness": round(betweenness[card_id], 4),
        }
        for card_id in card_ids
    ]
    rows.sort(key=lambda row: (-row["betweenness"], -row["degree"], row["card_id"]))
    for index, row in enumerate(rows, start=1):
        row["rank"] = index
    return rows


def _rank_by_card(
    cards: Sequence[_NormalizedCard], relations: Sequence[dict[str, str]]
) -> dict[str, int]:
    return {row["card_id"]: row["rank"] for row in _centrality(cards, relations)}


def _components(
    card_ids: Sequence[str], adjacency: dict[str, list[str]]
) -> list[list[str]]:
    visited: set[str] = set()
    components: list[list[str]] = []
    for card_id in card_ids:
        if card_id in visited:
            continue
        members: list[str] = []
        queue: deque[str] = deque([card_id])
        visited.add(card_id)
        while queue:
            current = queue.popleft()
            members.append(current)
            for neighbour in adjacency[current]:
                if neighbour not in visited:
                    visited.add(neighbour)
                    queue.append(neighbour)
        components.append(sorted(members))
    components.sort(key=lambda members: members[0])
    return components


def _connected_components(
    cards: Sequence[_NormalizedCard], relations: Sequence[dict[str, str]]
) -> list[dict[str, Any]]:
    card_ids = [card.id for card in cards]
    adjacency = _undirected_adjacency(card_ids, relations)
    rows: list[dict[str, Any]] = []
    for index, members in enumerate(_components(card_ids, adjacency), start=1):
        member_set = set(members)
        edge_count = sum(
            1
            for relation in relations
            if relation["from"] in member_set and relation["to"] in member_set
        )
        rows.append(
            {
                "component_id": f"cmp-{index:03d}",
                "card_ids": members,
                "edge_count": edge_count,
            }
        )
    return rows


def _contradiction_subgraphs(
    cards: Sequence[_NormalizedCard], relations: Sequence[dict[str, str]]
) -> list[dict[str, Any]]:
    card_ids = [card.id for card in cards]
    adjacency = _undirected_adjacency(card_ids, relations)
    negations = [relation for relation in relations if relation["type"] == "negate"]
    rows: list[dict[str, Any]] = []
    index = 0
    for members in _components(card_ids, adjacency):
        member_set = set(members)
        inner = [
            relation
            for relation in negations
            if relation["from"] in member_set and relation["to"] in member_set
        ]
        if not inner:
            continue
        index += 1
        inner.sort(key=lambda relation: (relation["from"], relation["to"]))
        touched = sorted({relation["from"] for relation in inner} | {r["to"] for r in inner})
        rows.append(
            {
                "subgraph_id": f"neg-{index:03d}",
                "card_ids": touched,
                "negation_edges": [relation["id"] for relation in inner],
                # spec §3.4 rule 2: template only, never an LLM summary.
                "summary": f"{len(inner)} negation edges across {len(touched)} cards",
            }
        )
    return rows


def _graph_summary(
    cards: Sequence[_NormalizedCard], relations: Sequence[dict[str, str]]
) -> dict[str, Any]:
    return {
        "centrality": _centrality(cards, relations),
        "connected_components": _connected_components(cards, relations),
        "contradiction_subgraphs": _contradiction_subgraphs(cards, relations),
    }


def _spatial_pairs(cards: Sequence[_NormalizedCard]) -> set[tuple[str, str]]:
    """spec §3.1 rule 6: k=3 nearest neighbours, ties broken by card_id asc."""
    placed = [card for card in cards if _is_finite(card.x) and _is_finite(card.y)]
    pairs: set[tuple[str, str]] = set()
    for card in placed:
        others = [other for other in placed if other.id != card.id]
        others.sort(
            key=lambda other: (
                math.dist((float(card.x), float(card.y)), (float(other.x), float(other.y))),
                other.id,
            )
        )
        for neighbour in others[:SPATIAL_NEIGHBOUR_K]:
            a, b = card.id, neighbour.id
            pairs.add((a, b) if a <= b else (b, a))
    return pairs


def _cluster_candidates(
    cards: Sequence[_NormalizedCard],
    relations: Sequence[dict[str, str]],
    *,
    spatial: bool,
) -> list[dict[str, Any]]:
    card_ids = [card.id for card in cards]
    by_basis: list[tuple[str, set[tuple[str, str]]]] = []

    relation_pairs = {
        (relation["from"], relation["to"])
        if relation["from"] <= relation["to"]
        else (relation["to"], relation["from"])
        for relation in relations
        if relation["type"] in ("related", "causal") and relation["from"] != relation["to"]
    }
    by_basis.append(("relation", relation_pairs))
    if spatial:
        by_basis.append(("spatial", _spatial_pairs(cards)))

    # basis -> card_ids tuple -> (score). `relation` is inserted first so rule 3
    # ("relation wins") falls out of a plain first-write-wins merge.
    merged: dict[tuple[str, ...], dict[str, Any]] = {}
    for basis, pairs in by_basis:
        adjacency: dict[str, set[str]] = {card_id: set() for card_id in card_ids}
        for a, b in pairs:
            adjacency[a].add(b)
            adjacency[b].add(a)
        sorted_adjacency = {k: sorted(v) for k, v in adjacency.items()}
        for members in _components(card_ids, sorted_adjacency):
            if len(members) < 2:
                continue
            key = tuple(members)
            if key in merged:
                continue
            member_set = set(members)
            internal = sum(1 for a, b in pairs if a in member_set and b in member_set)
            boundary = sum(
                1
                for a, b in pairs
                if (a in member_set) != (b in member_set)
            )
            n = len(members)
            density = round(internal / (n * (n - 1) / 2), 6) if n >= 2 else 0.0
            cohesion = (
                round(internal / (internal + boundary), 6) if (internal + boundary) else 0.0
            )
            merged[key] = {
                "card_ids": list(members),
                "basis": basis,
                "score": round(min(1.0, density + cohesion) / 2, 4),
            }

    ordered = sorted(merged.values(), key=lambda item: item["card_ids"])
    return [
        {
            "cluster_id": f"cc-{index:04d}",
            "card_ids": item["card_ids"],
            "basis": item["basis"],
            "score": item["score"],
        }
        for index, item in enumerate(ordered, start=1)
    ]


# ---------------------------------------------------------------------------
# §5 deterministic truncation
# ---------------------------------------------------------------------------


def _apply_truncation(
    cards: list[_NormalizedCard],
    relations: list[dict[str, str]],
    islands: list[dict[str, Any]],
    evidence_links: list[dict[str, Any]],
    rank_by_card: dict[str, int],
    *,
    required_card_ids: frozenset[str] = frozenset(),
) -> tuple[
    list[_NormalizedCard],
    list[dict[str, str]],
    list[dict[str, Any]],
    list[dict[str, Any]],
    _Truncation,
]:
    truncation = _Truncation()
    over_cards = len(cards) > MAX_CARDS
    over_relations = len(relations) > MAX_RELATIONS
    over_text = sum(card.char_len for card in cards) > MAX_TEXT_CHARS
    if not (over_cards or over_relations or over_text):
        return cards, relations, islands, evidence_links, truncation

    truncation.truncated = True  # step 1: cluster_candidates are dropped.

    if over_cards:  # step 2
        # Route-required cards are input semantics, not importance inferred by
        # the projection. Reserve them first, then fill the remaining budget by
        # the historical centrality order. With no required ids this is exactly
        # the former `rank <= MAX_CARDS` selection.
        keep = set(required_card_ids)
        ranked_ids = sorted(rank_by_card, key=lambda card_id: (rank_by_card[card_id], card_id))
        for card_id in ranked_ids:
            if len(keep) >= MAX_CARDS:
                break
            keep.add(card_id)
        cards = [card for card in cards if card.id in keep]
        relations, islands, evidence_links = _prune_references(
            keep, relations, islands, evidence_links
        )
        truncation.reasons.add("MAX_CARDS")

    if len(relations) > MAX_RELATIONS:  # step 3b
        relations = relations[:MAX_RELATIONS]
        truncation.reasons.add("MAX_RELATIONS")

    if sum(card.char_len for card in cards) > MAX_TEXT_CHARS:  # step 4
        for card in cards:
            card.text_norm = card.text_norm[:TRUNCATED_TEXT_CHARS]
            card.text = card.text_norm
            card.char_len = len(card.text_norm)
        truncation.reasons.add("MAX_TEXT_CHARS")

        # step 5: 240 chars per card can still exceed the budget. Route-required
        # cards are not eligible victims; discard only non-required cards from
        # the least central end. Without required ids this preserves the former
        # ordering and minimum-one-card rule.
        while len(cards) > 1 and sum(card.char_len for card in cards) > MAX_TEXT_CHARS:
            candidates = [card for card in cards if card.id not in required_card_ids]
            if not candidates:
                raise IRGenerationError(
                    "required_card_budget_exceeded",
                    "Route-required cards alone exceed the IR text budget.",
                )
            victim = max(
                candidates,
                key=lambda card: (rank_by_card.get(card.id, 1), card.id),
            )
            cards = [card for card in cards if card.id != victim.id]
            keep = {card.id for card in cards}
            relations, islands, evidence_links = _prune_references(
                keep, relations, islands, evidence_links
            )

        if sum(card.char_len for card in cards) > MAX_TEXT_CHARS:
            raise IRGenerationError(
                "required_card_budget_exceeded",
                "Route-required cards cannot fit within the IR text budget.",
            )

    return cards, relations, islands, evidence_links, truncation


def _prune_references(
    keep: set[str],
    relations: list[dict[str, str]],
    islands: list[dict[str, Any]],
    evidence_links: list[dict[str, Any]],
) -> tuple[list[dict[str, str]], list[dict[str, Any]], list[dict[str, Any]]]:
    """spec §5.2 rule 7: keep the IR referentially closed after a card drop."""
    relations = [
        relation
        for relation in relations
        if relation["from"] in keep and relation["to"] in keep
    ]
    pruned_islands: list[dict[str, Any]] = []
    for island in islands:
        members = [card_id for card_id in island["card_ids"] if card_id in keep]
        placard = island["placard_card_id"]
        pruned_islands.append(
            {
                **island,
                "card_ids": members,
                "placard_card_id": placard if placard in members else None,
            }
        )
    evidence_links = [
        link
        for link in evidence_links
        if link["from_card_id"] in keep and link["to_card_id"] in keep
    ]
    return relations, pruned_islands, evidence_links


# ---------------------------------------------------------------------------
# §6 fixture support
# ---------------------------------------------------------------------------


def canonical_ir_json(ir: dict[str, Any]) -> str:
    """Canonical JSON per spec §6.1 (key order, UTF-8, no whitespace)."""
    return json.dumps(ir, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def ir_sha256(ir: dict[str, Any]) -> str:
    return sha256(canonical_ir_json(ir).encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Consumer helpers
# ---------------------------------------------------------------------------


def adjudicated_contradiction(
    ir: dict[str, Any], card_a_id: str, card_b_id: str
) -> dict[str, Any] | None:
    """Return the human-adjudicated contradiction between two cards, if any.

    spec §2.2B rule 6 / issue `AI-IR-PROJECTION-01` AC-1: a `contradicts`
    evidence link already marked `confirmed` or `held` records a decision the
    human has made. Re-proposing it is the exact behaviour ADR-0069 set out to
    remove, so the consumer suppresses it instead of asking the model again.
    """
    pair = {card_a_id, card_b_id}
    for link in ir.get("evidence_links", []):
        if link["type"] != "contradicts":
            continue
        if {link["from_card_id"], link["to_card_id"]} != pair:
            continue
        if link["contradiction_state"] in ADJUDICATED_CONTRADICTION_STATES:
            return link
    return None


def held_card_ids(ir: dict[str, Any]) -> list[str]:
    """Card ids the human has set aside (spec §2.1 rule 8), ascending.

    `AI-IR-PROJECTION-01` AC-2: a card carrying ANY `hold_state` is one whose
    disposition the human has deliberately not settled. Proposing it as a member
    of a NEW group overrides that decision, which is precisely the behaviour
    `ADR-0069` set out to remove. All three values count -- `held` (judgement
    withheld), `pending` (not yet worked) and `shelved` (moved off the canvas)
    each say "not now", and none of them says "bundle me".
    """
    return sorted(card["id"] for card in ir.get("cards", []) if card.get("hold_state"))


def derived_island_relations(ir: dict[str, Any]) -> list[dict[str, Any]]:
    """Aggregate the IR's card-level `relations` up to island level.

    The Python counterpart of the frontend's `getDerivedIslandEdges()`. `AI-IR-PROJECTION-01` AC-7 asked for a TS<->Python
    equivalence check on the projection layer; this is the function pair it now
    has (`tests/test_derived_island_relations_ts_equivalence.py` and
    `frontend/src/domain/island_edge_aggregate.python_equivalence.test.ts` share
    one fixture and one expected output).

    Why it lives here and not in the IR itself: spec §2.3 rule 6 keeps island
    endpoints OUT of `relations` on purpose, so an island-level relation is a
    CONSUMER's view of `relations` x `islands`, not a stored field. Deriving it
    here changes no schema and needs no `ir_version` bump.

    Equivalence with the TS function holds on documents where:

    - every edge is card-to-card (an edge with an island endpoint never reaches
      the IR at all, so the "persisted island edge" branch of the TS function
      has no input here -- the TS function skips island->island edges too, but
      it does promote a persisted island->card edge, which this one cannot see);
    - every edge type is one of the five canvas values (`unknown` is dropped by
      §2.3 rule 6, where TS would aggregate it);
    - no `(from, to, type)` triple is duplicated (§2.3 rule 3 de-duplicates
      before this function runs, where TS counts both occurrences);
    - a card belongs to at most one island (§2.2A applies FIRST-MATCH-WINS,
      where TS's `getIslandsForCard()` returns every match).

    Those are exactly the projection differences the IR introduces by design;
    they are boundary conditions of the comparison, not drift.
    """
    island_by_card: dict[str, str] = {}
    for island in ir.get("islands", []):
        for card_id in island["card_ids"]:
            island_by_card.setdefault(card_id, island["id"])

    card_ids = {card["id"] for card in ir.get("cards", [])}
    aggregate: dict[str, dict[str, Any]] = {}

    def _contribute(
        key: str, from_id: str, to_id: str, to_kind: str, relation: dict[str, str]
    ) -> None:
        entry = aggregate.get(key)
        if entry is None:
            entry = {
                "id": key,
                "from_id": from_id,
                "to_id": to_id,
                "from_kind": "island",
                "to_kind": to_kind,
                "type": relation["type"],
                "contributing_relation_ids": [],
                "contributing_card_ids": [],
            }
            aggregate[key] = entry
        entry["contributing_relation_ids"].append(relation["id"])
        # Both endpoints are cards: §2.3 rule 6 already removed every relation
        # with an island endpoint before this point.
        for endpoint in (relation["from"], relation["to"]):
            if endpoint not in entry["contributing_card_ids"]:
                entry["contributing_card_ids"].append(endpoint)

    for relation in ir.get("relations", []):
        from_island = island_by_card.get(relation["from"])
        to_island = island_by_card.get(relation["to"])

        if from_island is None and to_island is None:
            # Lone wolf <-> lone wolf: no island relation to escalate to.
            continue

        if from_island is not None and to_island is not None:
            if from_island == to_island:
                # Internal to one island; it says nothing about island layout.
                continue
            a, b = (from_island, to_island) if from_island <= to_island else (to_island, from_island)
            _contribute(f"derived-island:{a}|{b}|{relation['type']}", a, b, "island", relation)
            continue

        # Exactly one side sits in an island; the other is a lone-wolf card.
        # ADR-0048 D2 round 5: that relation is promoted to the island's placard.
        island_id = from_island if from_island is not None else to_island
        lone_card_id = relation["to"] if from_island is not None else relation["from"]
        if lone_card_id not in card_ids:
            continue
        _contribute(
            f"derived-card:{island_id}|{lone_card_id}|{relation['type']}",
            str(island_id),
            lone_card_id,
            "card",
            relation,
        )

    rows = sorted(aggregate.values(), key=lambda row: row["id"])
    for row in rows:
        row["aggregate_count"] = len(row["contributing_relation_ids"])
    return rows


def validate_llm_input_ir(ir: dict[str, Any]) -> None:
    """Structural assertions the spec §4.2 schema makes machine-checkable.

    Kept dependency-free (no jsonschema) and limited to the invariants that
    matter for safety and reproducibility; the full schema lives in the spec.
    """
    if ir.get("ir_version") != IR_VERSION:
        raise IRGenerationError("ir_version_mismatch", "Unexpected ir_version.")
    for key in ("cards", "relations", "graph_summary", "constraints", "meta"):
        if key not in ir:
            raise IRGenerationError("ir_schema_violation", f"Required key '{key}' is missing.")
    known = {
        "ir_version",
        "cards",
        "coordinates",
        "relations",
        "islands",
        "evidence_links",
        "cluster_candidates",
        "graph_summary",
        "constraints",
        "meta",
        "truncation",
    }
    unknown = set(ir) - known
    if unknown:
        raise IRGenerationError(
            "ir_schema_violation", "The IR carries keys outside the closed schema."
        )
    if not ir["cards"]:
        raise IRGenerationError("ir_schema_violation", "The IR must carry at least one card.")
    if ir["constraints"].get("safe_mode") is not True:
        raise IRGenerationError("safe_mode_required", "constraints.safe_mode must be true.")
    if ir["constraints"].get("structured_text_only") is not True:
        raise IRGenerationError(
            "ir_schema_violation", "constraints.structured_text_only must be true."
        )
    if list(ir["constraints"].get("required_sections", [])) != list(REQUIRED_SECTIONS):
        raise IRGenerationError(
            "ir_schema_violation", "constraints.required_sections is not the fixed triple."
        )
    if ir["meta"].get("safe_mode") is not True:
        raise IRGenerationError("safe_mode_required", "meta.safe_mode must be true.")
    card_ids = {card["id"] for card in ir["cards"]}
    for card in ir["cards"]:
        if "hold_state" in card and card["hold_state"] not in HOLD_STATES:
            raise IRGenerationError(
                "ir_schema_violation", "Unknown hold_state value in the IR."
            )
    for relation in ir["relations"]:
        if relation["type"] not in RELATION_TYPES:
            raise IRGenerationError("ir_schema_violation", "Unknown relation type in the IR.")
        if relation["from"] not in card_ids or relation["to"] not in card_ids:
            raise IRGenerationError("ir_schema_violation", "A relation references a missing card.")
    for island in ir.get("islands", []):
        for card_id in island["card_ids"]:
            if card_id not in card_ids:
                raise IRGenerationError(
                    "ir_schema_violation", "An island references a missing card."
                )
    for link in ir.get("evidence_links", []):
        if link["from_card_id"] not in card_ids or link["to_card_id"] not in card_ids:
            raise IRGenerationError(
                "ir_schema_violation", "An evidence link references a missing card."
            )
