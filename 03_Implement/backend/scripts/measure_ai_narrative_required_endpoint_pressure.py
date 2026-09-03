#!/usr/bin/env python3
"""`generate-narrative` の論理骨格を保護するときの数値境界を測る。

`AI-IR-SCALE-01` では、叙述に必要な `causal` / `negate` の両端のカードだけを
`required_card_ids` で保護する方式Bを候補としている。ただし、この方式が安全に
成立するかは、論理関係の件数だけでは決まらない。少なくとも次の三つを分けて見る
必要がある。

- 論理骨格が参照する一意なカード数が `MAX_CARDS` に収まるか。
- 保持すべき論理関係の数が `MAX_RELATIONS` に収まるか。
- R21と同じ「1枚46文字」の代表値を置いた場合に `MAX_TEXT_CHARS` に収まるか。

このスクリプトは外部LLMやプロバイダーを呼ばず、トークン数も推定しない。実際の
カード本文は長さが異なるため、`representative_text_chars` はR21の合成入力との
比較にだけ使う。また、全ての数値上限に収まっても、それだけで方式Bを採用してよい
とは判断しない。必要な論理関係を確実に保護する実装、意味上の完全性、SafeMode等は
別に検証する必要がある。
"""

from __future__ import annotations

import json
from dataclasses import dataclass

from kj_atlas_api.llm_input_ir import MAX_CARDS, MAX_RELATIONS, MAX_TEXT_CHARS

REPRESENTATIVE_CARD_CHARS = 46


@dataclass(frozen=True)
class LogicalRelation:
    from_id: str
    to_id: str
    type: str


def _disjoint_pairs(pair_count: int) -> list[LogicalRelation]:
    relations: list[LogicalRelation] = []
    for index in range(pair_count):
        relation_type = "causal" if index % 2 == 0 else "negate"
        relations.append(
            LogicalRelation(
                from_id=f"c{index * 2:03d}",
                to_id=f"c{index * 2 + 1:03d}",
                type=relation_type,
            )
        )
    return relations


def _chain(card_count: int) -> list[LogicalRelation]:
    return [
        LogicalRelation(
            from_id=f"c{index:03d}",
            to_id=f"c{index + 1:03d}",
            type="causal" if index % 2 == 0 else "negate",
        )
        for index in range(card_count - 1)
    ]


def _dense_relations(card_count: int, relation_count: int) -> list[LogicalRelation]:
    """同じedgeを重複させず、指定件数まで決定論的に論理関係を生成する。"""

    relations: list[LogicalRelation] = []
    for offset in range(1, card_count):
        for source in range(card_count):
            target = (source + offset) % card_count
            relation_type = "causal" if len(relations) % 2 == 0 else "negate"
            relations.append(
                LogicalRelation(
                    from_id=f"c{source:03d}",
                    to_id=f"c{target:03d}",
                    type=relation_type,
                )
            )
            if len(relations) == relation_count:
                return relations
    raise ValueError("指定した `relation_count` は決定論的に生成できる関係数を超えています")


def _summarize(name: str, relations: list[LogicalRelation]) -> dict[str, object]:
    endpoint_ids = sorted(
        {relation.from_id for relation in relations} | {relation.to_id for relation in relations}
    )
    representative_text_chars = len(endpoint_ids) * REPRESENTATIVE_CARD_CHARS
    cards_fit = len(endpoint_ids) <= MAX_CARDS
    relations_fit = len(relations) <= MAX_RELATIONS
    text_fit = representative_text_chars <= MAX_TEXT_CHARS

    return {
        "name": name,
        "logical_relation_count": len(relations),
        "required_endpoint_card_count": len(endpoint_ids),
        "representative_text_chars": representative_text_chars,
        "required_cards_fit": cards_fit,
        "required_relations_fit": relations_fit,
        "representative_text_fit": text_fit,
        "within_current_numeric_caps": cards_fit and relations_fit and text_fit,
    }


def measure() -> dict[str, object]:
    scenarios = [
        _summarize("sparse-10-joints", _disjoint_pairs(10)),
        _summarize("card-cap-boundary-100-disjoint-joints", _disjoint_pairs(100)),
        _summarize("card-cap-exceeded-101-disjoint-joints", _disjoint_pairs(101)),
        _summarize("relation-cap-exceeded-with-200-endpoints", _dense_relations(200, 401)),
        _summarize("document-wide-300-card-chain", _chain(300)),
    ]

    return {
        "measurement": "ai-narrative-required-endpoint-pressure",
        "token_estimation": False,
        "representative_card_chars": REPRESENTATIVE_CARD_CHARS,
        "limits": {
            "MAX_CARDS": MAX_CARDS,
            "MAX_RELATIONS": MAX_RELATIONS,
            "MAX_TEXT_CHARS": MAX_TEXT_CHARS,
        },
        "scenarios": scenarios,
        "interpretation": [
            "必須となる端点カードが少数なら、カード上限の観点では方式Bは成立し得る。",
            "一意な端点カードがMAX_CARDSを超える場合、required_card_idsだけでは方式Bを成立させられない。",
            "端点カードがMAX_CARDS内でも、保持すべき論理関係がMAX_RELATIONSを超える場合がある。",
            "R21と同じ1枚46文字の代表値では、300枚を全体にまたぐ連鎖はMAX_TEXT_CHARSも超える。",
            "数値上限内に収まることだけでは方式B採用の十分条件にならず、プロバイダーの実トークン測定と意味保存の検証は引き続き必要である。",
        ],
    }


def main() -> int:
    print(json.dumps(measure(), ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
