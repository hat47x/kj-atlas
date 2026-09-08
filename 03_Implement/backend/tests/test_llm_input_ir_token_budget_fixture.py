"""AI-IR-PROJECTION-01 AC-10 の代表入力を、tiktoken 無しで固定する。

トークン計測そのもの（`build_report()`）は参照トークナイザを要するため CI では
回さない。ここで守るのは、その計測が意味を持つための**入力側の性質**である。

- 代表規模（300カード・30島）であること
- 切り詰めが実際に起きること（`MAX_CARDS` と `MAX_RELATIONS` の両方）
- `causal` / `negate` が島境界をまたぐこと
- `generate-narrative` の必須骨格が `MAX_CARDS` に収まること
  （収まらないと4エンドポイントを同一入力で比較できない）
- 「IR導入前」を再現するために差し引くヘッダ行が、現行プロンプトに実在すること

最後の1点が本ファイルの主眼である。AC-10 の旧値は git 履歴
（`dd690559^` ほか）から取ったもので、スクリプトはその差分を文字列として
持っている。ヘッダ文言が書き換わればその再現は静かに壊れるため、テストで
検出できるようにしておく。
"""

from __future__ import annotations

from kj_atlas_api.llm_input_ir import (
    MAX_CARDS,
    MAX_RELATIONS,
    MAX_TEXT_CHARS,
    source_from_document,
)
from kj_atlas_api.models import SuggestLayoutRequest
from kj_atlas_api.models_ai import DetectContradictionRequest
from kj_atlas_api.routes import ai
from scripts.measure_llm_input_ir_token_budget import (
    _PRE_IR_HEADER_ADDITIONS,
    _card_id,
    _pre_ir_prompt,
    build_representative_document,
)


def test_representative_document_is_ac10_scale() -> None:
    document = build_representative_document()

    assert len(document.cards) == 300
    assert len(document.islands) == 30
    assert len(document.edges) == 899
    assert len(document.evidenceLinks or []) == 30
    assert sum(1 for card in document.cards if card.holdState) == 12
    assert {card.holdState for card in document.cards if card.holdState} == {
        "held",
        "pending",
        "shelved",
    }


def test_representative_document_crosses_the_card_and_relation_caps() -> None:
    document = build_representative_document()

    assert len(document.cards) > MAX_CARDS
    assert len(document.edges) > MAX_RELATIONS

    ir = ai._suggest_layout_ir(SuggestLayoutRequest(doc=document))
    assert ir["truncation"]["truncated"] is True
    assert ir["truncation"]["reason_codes"] == ["MAX_CARDS", "MAX_RELATIONS"]
    assert len(ir["cards"]) == MAX_CARDS
    assert len(ir["relations"]) == MAX_RELATIONS


def test_text_budget_is_not_the_binding_cap_for_this_fixture() -> None:
    """本文長で上限が入れ替わることを、余白つきで固定する。

    1枚38.5文字 × 300枚 = 11,550文字。`MAX_TEXT_CHARS=12,000` に対する余白は
    450文字しかない。`AI-IR-SCALE-01` R21 の代表入力（1枚46文字）は同じ300枚で
    13,800文字となり、そちらでは文字数側が先に効く。300枚での拘束上限が
    平均カード長で切り替わる（境目は 12,000/300 = 40文字）ことの根拠になる。
    """
    document = build_representative_document()
    normalized_chars = sum(len(" ".join(card.text.split())) for card in document.cards)

    assert normalized_chars == 11_550
    assert normalized_chars < MAX_TEXT_CHARS


def test_causal_and_negate_cross_island_boundaries() -> None:
    document = build_representative_document()
    island_of = {
        card_id: island.id for island in document.islands for card_id in island.cardIds
    }
    crossing = [
        edge
        for edge in document.edges
        if edge.type in ("causal", "negate")
        and island_of.get(edge.fromId) != island_of.get(edge.toId)
    ]

    assert crossing, "代表入力に島をまたぐcausal/negateが1本も無い"
    assert {edge.type for edge in crossing} == {"causal", "negate"}


def test_narrative_required_spine_fits_the_card_budget() -> None:
    """骨格が上限を超えると `generate-narrative` は 422 で fail-closed する。

    `AI-IR-NARRATIVE-SPINE-01` が `causal` / `negate` の両端を
    `required_card_ids` として予約するため、代表入力の骨格が `MAX_CARDS` を
    超えると4エンドポイントを同一入力で比較できなくなる。
    """
    document = build_representative_document()
    required = ai._narrative_required_card_ids(source_from_document(document))

    assert len(required) == 117
    assert len(required) <= MAX_CARDS


def test_pre_ir_header_lines_still_exist_in_the_current_prompts() -> None:
    """旧プロンプト再現の前提（差し引く行が実在すること）を守る。"""
    document = build_representative_document()
    contradiction_payload = DetectContradictionRequest(
        cardA={"id": _card_id(149), "text": document.cards[149].text, "textReviewed": True},
        cardB={"id": _card_id(150), "text": document.cards[150].text, "textReviewed": True},
        doc=document,
    )
    layout_payload = SuggestLayoutRequest(doc=document)

    rendered = {
        "detect-contradiction": ai._build_detect_contradiction_prompt(contradiction_payload),
        "suggest-layout": ai._build_prompt(layout_payload),
    }
    assert set(_PRE_IR_HEADER_ADDITIONS) == set(rendered)

    for endpoint, prompt in rendered.items():
        shortened = _pre_ir_prompt(endpoint, prompt)
        assert len(shortened) < len(prompt)
        for line in _PRE_IR_HEADER_ADDITIONS[endpoint]:
            assert line in prompt
            assert line not in shortened
