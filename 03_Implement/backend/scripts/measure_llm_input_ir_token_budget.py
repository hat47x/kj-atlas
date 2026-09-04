#!/usr/bin/env python3
"""AI-IR-PROJECTION-01 AC-10 の代表規模トークン計測。

300カード・30島の決定論的な文書を作り、Stage 1〜4でIR経由になった
4エンドポイントについて、IR導入前相当（`ir=None`）と現在のIR経路の
プロンプト量を同じ参照トークナイザで比較する。

ここで得るトークン数は provider の課金値ではない。モデルごとに
トークナイザが異なるため、回帰比較用の参照値として tiktoken の
`o200k_base` を用いる。UTF-8バイト数も併記し、特定providerの
トークナイザへ判断を固定しない。
"""

from __future__ import annotations

import argparse
import json
from importlib.metadata import version as package_version
from typing import Any

from kj_atlas_api.llm_input_ir import MAX_CARDS, MAX_RELATIONS, MAX_TEXT_CHARS, canonical_ir_json
from kj_atlas_api.models import DocumentV1, SuggestLayoutRequest
from kj_atlas_api.models_ai import (
    DetectContradictionRequest,
    GenerateNarrativeRequest,
    SuggestCardGroupsRequest,
)
from kj_atlas_api.routes import ai

CARD_COUNT = 300
ISLAND_COUNT = 30
CARDS_PER_ISLAND = CARD_COUNT // ISLAND_COUNT
REFERENCE_ENCODING = "o200k_base"

_THEMES = (
    "利用者の作業手順",
    "根拠への戻りやすさ",
    "異論を残す方法",
    "判断を保留する条件",
    "後から訂正する経路",
    "共同作業での責任範囲",
    "情報を外へ出す境界",
    "AI提案の採否",
    "画面上の認知負荷",
    "次に確認すべき空白",
)


def _card_id(index: int) -> str:
    return f"c{index:04d}"


def build_representative_document() -> DocumentV1:
    """300カード・30島の、決定論的でPIIを含まない代表文書を作る。"""
    cards: list[dict[str, Any]] = []
    for index in range(CARD_COUNT):
        theme = _THEMES[index % len(_THEMES)]
        cards.append(
            {
                "id": _card_id(index),
                "text": f"{theme}について、現場の観察と反対意見を分け、未確認事項を保留した。",
                "x": float((index % 20) * 120),
                "y": float((index // 20) * 90),
                "textReviewed": True,
            }
        )

    relation_types = ("related", "causal", "negate", "mutual", "equivalence")
    edges = [
        {
            "id": f"e{index:04d}",
            "fromId": _card_id(index),
            "toId": _card_id(index + 1),
            "type": relation_types[index % len(relation_types)],
        }
        for index in range(CARD_COUNT - 1)
    ]

    islands: list[dict[str, Any]] = []
    for island_index in range(ISLAND_COUNT):
        start = island_index * CARDS_PER_ISLAND
        members = [_card_id(index) for index in range(start, start + CARDS_PER_ISLAND)]
        islands.append(
            {
                "id": f"i{island_index:02d}",
                "cardIds": members,
                "title": f"観察群{island_index + 1}",
                "titleReviewed": True,
                "placardCardId": members[0],
                "parentIslandId": None if island_index < 10 else f"i{island_index % 10:02d}",
            }
        )

    evidence_links = [
        {
            "id": f"ev{index:03d}",
            "type": "contradicts" if index % 2 else "supports",
            "fromCardId": _card_id(index * 10),
            "toCardId": _card_id(index * 10 + 1),
            "contradictionState": "unconfirmed" if index % 2 else None,
        }
        for index in range(ISLAND_COUNT)
    ]

    return DocumentV1.model_validate(
        {
            "version": 1,
            "id": "ai-ir-ac10-representative",
            "title": "LLM投入IR代表規模計測",
            "createdAt": "2026-09-02T00:00:00Z",
            "updatedAt": "2026-09-02T00:00:00Z",
            "transform": {"panX": 0, "panY": 0, "zoom": 1},
            "cards": cards,
            "edges": edges,
            "islands": islands,
            "readingOrder": [island["id"] for island in islands],
            "narratives": [],
            "evidenceLinks": evidence_links,
        }
    )


def _text_metrics(text: str, encoding: Any) -> dict[str, int]:
    return {
        "referenceTokens": len(encoding.encode(text)),
        "utf8Bytes": len(text.encode("utf-8")),
        "unicodeChars": len(text),
    }


def _ir_metrics(ir: dict[str, Any], encoding: Any) -> dict[str, Any]:
    serialized = canonical_ir_json(ir)
    metrics: dict[str, Any] = _text_metrics(serialized, encoding)
    metrics.update(
        {
            "cards": len(ir.get("cards", [])),
            "relations": len(ir.get("relations", [])),
            "islands": len(ir.get("islands", [])),
            "coordinates": len(ir.get("coordinates", [])),
            "truncated": bool(ir.get("truncation", {}).get("truncated")),
            "reasonCodes": list(ir.get("truncation", {}).get("reason_codes", [])),
        }
    )
    return metrics


def _prompt_metrics(legacy: str, current: str, encoding: Any) -> dict[str, Any]:
    legacy_metrics = _text_metrics(legacy, encoding)
    current_metrics = _text_metrics(current, encoding)
    delta = current_metrics["referenceTokens"] - legacy_metrics["referenceTokens"]
    ratio = (
        round(current_metrics["referenceTokens"] / legacy_metrics["referenceTokens"], 4)
        if legacy_metrics["referenceTokens"]
        else None
    )
    return {
        "legacyReference": legacy_metrics,
        "irPath": current_metrics,
        "deltaReferenceTokens": delta,
        "ratioToLegacy": ratio,
    }


def build_report() -> dict[str, Any]:
    try:
        import tiktoken
    except ImportError as exc:  # pragma: no cover - 実行環境への案内
        raise SystemExit(
            "tiktoken が必要です。計測時だけ `pip install tiktoken==0.14.0` を実行してください。"
        ) from exc

    encoding = tiktoken.get_encoding(REFERENCE_ENCODING)
    document = build_representative_document()

    group_payload = SuggestCardGroupsRequest(
        cards=[
            {"id": card.id, "text": card.text, "textReviewed": True}
            for card in document.cards
        ],
        doc=document,
    )
    group_ir = ai._suggest_card_groups_ir(group_payload)
    candidate_ids, _ = ai._card_group_candidates(group_payload, group_ir)

    narrative_payload = GenerateNarrativeRequest(
        doc=document,
        narrativeTitle="代表規模の叙述",
    )
    narrative_ir = ai._generate_narrative_ir(narrative_payload)

    layout_payload = SuggestLayoutRequest(doc=document)
    layout_ir = ai._suggest_layout_ir(layout_payload)

    contradiction_payload = DetectContradictionRequest(
        cardA={
            "id": _card_id(149),
            "text": document.cards[149].text,
            "textReviewed": True,
        },
        cardB={
            "id": _card_id(150),
            "text": document.cards[150].text,
            "textReviewed": True,
        },
        doc=document,
    )
    contradiction_ir = ai._detect_contradiction_ir(contradiction_payload)

    prompts = {
        "detect-contradiction": _prompt_metrics(
            ai._build_detect_contradiction_prompt(contradiction_payload),
            ai._build_detect_contradiction_prompt(contradiction_payload, contradiction_ir),
            encoding,
        ),
        "suggest-card-groups": _prompt_metrics(
            ai._build_suggest_card_groups_prompt(group_payload),
            ai._build_suggest_card_groups_prompt(
                group_payload,
                group_ir,
                candidate_ids=candidate_ids,
            ),
            encoding,
        ),
        "generate-narrative": _prompt_metrics(
            ai._build_generate_narrative_prompt(narrative_payload),
            ai._build_generate_narrative_prompt(narrative_payload, narrative_ir),
            encoding,
        ),
        "suggest-layout": _prompt_metrics(
            ai._build_prompt(layout_payload),
            ai._build_prompt(layout_payload, layout_ir),
            encoding,
        ),
    }

    return {
        "schemaVersion": 1,
        "purpose": "AI-IR-PROJECTION-01 AC-10 reference token budget",
        "tokenizer": {
            "library": "tiktoken",
            "libraryVersion": package_version("tiktoken"),
            "encoding": REFERENCE_ENCODING,
            "meaning": "回帰比較用の参照値。providerの課金トークン数ではない。",
        },
        "representativeDocument": {
            "cards": len(document.cards),
            "islands": len(document.islands),
            "relations": len(document.edges),
            "evidenceLinks": len(document.evidenceLinks or []),
        },
        "limits": {
            "MAX_CARDS": MAX_CARDS,
            "MAX_RELATIONS": MAX_RELATIONS,
            "MAX_TEXT_CHARS": MAX_TEXT_CHARS,
        },
        "ir": {
            "withoutCoordinates": _ir_metrics(narrative_ir, encoding),
            "withCoordinates": _ir_metrics(layout_ir, encoding),
        },
        "prompts": prompts,
    }


def _print_markdown(report: dict[str, Any]) -> None:
    doc = report["representativeDocument"]
    tokenizer = report["tokenizer"]
    print("# LLM投入IR 代表規模トークン計測")
    print()
    print(
        f"- 代表文書: {doc['cards']}カード / {doc['islands']}島 / "
        f"{doc['relations']}関係 / {doc['evidenceLinks']}証拠リンク"
    )
    print(
        f"- 参照トークナイザ: {tokenizer['library']} {tokenizer['libraryVersion']} / "
        f"{tokenizer['encoding']}"
    )
    print("- 注記: 参照トークン数はproviderの課金値ではなく、同一条件での回帰比較用。")
    print()
    print("## IR本体")
    print()
    print("| 投影 | 参照トークン | UTF-8 bytes | cards | relations | islands | coordinates | truncation |")
    print("| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |")
    for label, key in (("座標なし", "withoutCoordinates"), ("座標あり", "withCoordinates")):
        row = report["ir"][key]
        reasons = ",".join(row["reasonCodes"]) or "none"
        print(
            f"| {label} | {row['referenceTokens']} | {row['utf8Bytes']} | {row['cards']} | "
            f"{row['relations']} | {row['islands']} | {row['coordinates']} | {reasons} |"
        )
    print()
    print("## 実際のプロンプト")
    print()
    print("| エンドポイント | IR導入前相当 | 現在のIR経路 | 差分 | 倍率 |")
    print("| --- | ---: | ---: | ---: | ---: |")
    for endpoint, row in report["prompts"].items():
        ratio = "-" if row["ratioToLegacy"] is None else f"{row['ratioToLegacy']:.4f}"
        print(
            f"| `{endpoint}` | {row['legacyReference']['referenceTokens']} | "
            f"{row['irPath']['referenceTokens']} | {row['deltaReferenceTokens']:+d} | {ratio} |"
        )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--format", choices=("json", "markdown"), default="markdown")
    args = parser.parse_args()

    report = build_report()
    if args.format == "json":
        print(json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2))
    else:
        _print_markdown(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
