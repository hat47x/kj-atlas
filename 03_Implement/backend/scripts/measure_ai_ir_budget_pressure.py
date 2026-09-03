#!/usr/bin/env python3
"""代表300カード入力に対する、現在のIR文字数予算の圧力を決定論的に測る。

このスクリプトはtoken数を推定しない。`AI-IR-SCALE-01` で比較中の方式A
（全体上限の引上げ）について、`MAX_CARDS` だけを300へ広げても
`MAX_TEXT_CHARS` が別の上限として残ることを確認するための現状計測である。

対象は `measure_ai_route_prompt_coverage.py` と同じ300カード・30島の合成入力とする。
実provider、ネットワーク、利用者の実データは一切使わない。
"""

from __future__ import annotations

import json
import re
import unicodedata
from typing import Any

from kj_atlas_api.llm_input_ir import (
    MAX_CARDS,
    MAX_TEXT_CHARS,
    TRUNCATED_TEXT_CHARS,
)
from scripts.measure_ai_route_prompt_coverage import representative_document

_CONTROL_CHARS = re.compile(r"[\x00-\x1f\x7f]")
_WHITESPACE = re.compile(r"\s+")


def _text_norm(text: str) -> str:
    """`llm_input_ir_spec.md` §2.1と同じ文字列正規化だけを再現する。"""
    without_controls = _CONTROL_CHARS.sub("", text)
    nfkc = unicodedata.normalize("NFKC", without_controls)
    return _WHITESPACE.sub(" ", nfkc).strip()


def measure() -> dict[str, Any]:
    """現行上限と代表入力の関係を、token推定を交えずに返す。"""
    doc = representative_document(include_evidence=False)
    text_lengths = [len(_text_norm(card["text"])) for card in doc["cards"]]
    fixed_cut_lengths = [min(length, TRUNCATED_TEXT_CHARS) for length in text_lengths]

    unique_lengths = sorted(set(text_lengths))
    uniform_length = unique_lengths[0] if len(unique_lengths) == 1 else None
    text_budget_capacity = (
        MAX_TEXT_CHARS // uniform_length
        if uniform_length is not None and uniform_length > 0
        else None
    )
    minimum_cards_removed = (
        max(0, len(text_lengths) - text_budget_capacity)
        if text_budget_capacity is not None
        else None
    )

    source_text_chars = sum(text_lengths)
    after_fixed_cut_text_chars = sum(fixed_cut_lengths)
    card_cap_only_hypothesis = len(text_lengths)

    return {
        "measurement": "ai-ir-character-budget-pressure",
        "scenario": "300-cards-30-islands-ring",
        "current_limits": {
            "max_cards": MAX_CARDS,
            "max_text_chars": MAX_TEXT_CHARS,
            "per_card_fixed_cut_chars": TRUNCATED_TEXT_CHARS,
        },
        "source": {
            "cards": len(text_lengths),
            "text_chars": source_text_chars,
            "unique_card_text_lengths": unique_lengths,
        },
        "after_fixed_per_card_cut": {
            "text_chars": after_fixed_cut_text_chars,
            "changed": after_fixed_cut_text_chars != source_text_chars,
        },
        "hypothesis_max_cards_only_raised_to_source_count": {
            "max_cards": card_cap_only_hypothesis,
            "text_budget_exceeded": after_fixed_cut_text_chars > MAX_TEXT_CHARS,
            "full_card_coverage_possible_under_current_text_budget": (
                after_fixed_cut_text_chars <= MAX_TEXT_CHARS
            ),
        },
        "uniform_text_length_characterization": {
            "card_text_chars": uniform_length,
            "cards_fit_under_current_text_budget": text_budget_capacity,
            "minimum_cards_removed_to_fit_current_text_budget": minimum_cards_removed,
        },
        "interpretation_boundary": (
            "これはIRの文字数上限だけを測る結果であり、providerのtoken数ではない。"
            "正確なtoken数はmeasure_ai_route_provider_tokens.pyでprovider-reported usageを測る。"
        ),
    }


def main() -> int:
    print(json.dumps(measure(), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
