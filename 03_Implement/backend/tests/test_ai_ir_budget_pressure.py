from __future__ import annotations

from kj_atlas_api.llm_input_ir import (
    MAX_CARDS,
    MAX_TEXT_CHARS,
    TRUNCATED_TEXT_CHARS,
)
from scripts.measure_ai_ir_budget_pressure import measure


def test_representative_input_exceeds_both_card_and_text_budgets() -> None:
    result = measure()

    assert result["source"]["cards"] == 300
    assert result["current_limits"] == {
        "max_cards": MAX_CARDS,
        "max_text_chars": MAX_TEXT_CHARS,
        "per_card_fixed_cut_chars": TRUNCATED_TEXT_CHARS,
    }
    assert result["source"]["cards"] > MAX_CARDS
    assert result["source"]["text_chars"] > MAX_TEXT_CHARS


def test_fixed_240_character_cut_does_not_help_this_representative_input() -> None:
    result = measure()

    # 代表カードは1枚46文字であり、240文字への固定切り詰めより短い。
    # したがってMAX_TEXT_CHARS超過時にこの段階を通っても文字数は減らない。
    assert result["source"]["unique_card_text_lengths"] == [46]
    assert result["after_fixed_per_card_cut"] == {
        "text_chars": 13_800,
        "changed": False,
    }


def test_raising_only_max_cards_to_300_cannot_preserve_all_300_cards() -> None:
    result = measure()
    hypothesis = result["hypothesis_max_cards_only_raised_to_source_count"]

    assert hypothesis["max_cards"] == 300
    assert hypothesis["text_budget_exceeded"] is True
    assert hypothesis["full_card_coverage_possible_under_current_text_budget"] is False


def test_uniform_representative_text_budget_would_fit_only_260_cards() -> None:
    result = measure()["uniform_text_length_characterization"]

    # 46文字 × 260枚 = 11,960文字で収まるが、261枚では12,006文字となる。
    assert result == {
        "card_text_chars": 46,
        "cards_fit_under_current_text_budget": 260,
        "minimum_cards_removed_to_fit_current_text_budget": 40,
    }


def test_measurement_does_not_claim_provider_token_usage() -> None:
    result = measure()

    assert "token" not in result["measurement"]
    assert "providerのtoken数ではない" in result["interpretation_boundary"]
