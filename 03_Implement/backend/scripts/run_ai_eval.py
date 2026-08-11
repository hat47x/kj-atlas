#!/usr/bin/env python3
"""Run the KJ-operation quality evaluation for issue-AI-EVAL-01 (L2 criterion ③).

Executes the DeepSeek real-API evaluation once KJ_ATLAS_DEEPSEEK_API_KEY
is set. With --dry-run it uses a stub provider to verify the pipeline.

Usage:
  # Pipeline check without API key (stub provider)
  python run_ai_eval.py --dry-run

  # Real-API evaluation (requires KJ_ATLAS_DEEPSEEK_API_KEY)
  export KJ_ATLAS_LLM_PROVIDER=deepseek
  export KJ_ATLAS_DEEPSEEK_API_KEY=<key>
  python run_ai_eval.py

Output: results printed to stdout in the ai_eval_results.md table format.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from kj_atlas_api.llm.provider import (
    LLMCallMetadata,
    LLMRequest,
    LLMResponse,
    ProviderDisabledError,
    ProviderRequestError,
    generate_with_fallback,
)
from kj_atlas_api.models_ai import (
    RefineCardTextRequest,
    SuggestIslandSummaryRequest,
)
from kj_atlas_api.models import DocumentV1

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
FIXTURE = REPO_ROOT / "03_Implement" / "backend" / "tests" / "fixtures" / "ai_eval_kj_document.json"

# Evaluation rubric (qualitative, anti-scoring)
REFINE_AXES = ("名詞止め解除", "元意味保持", "過剰言い換えなし")
SUMMARY_AXES = ("別島に載せても成立しない", "代弁性", "名詞止め解除")


def _stub_generate(req: LLMRequest) -> LLMResponse:
    """Stub provider for --dry-run (returns canned but schema-valid output)."""
    metadata = LLMCallMetadata(
        provider_kind="deepseek",
        provider_name="deepseek",
        model_id="deepseek-chat",
        transport="http",
        requested_at="2026-08-12T00:00:00Z",
        trace_id="llm-eval-dryrun",
    )
    if req.task == "refine_card_text":
        return LLMResponse(raw_text='{"refinedText": "改善されたカード文（dry-run）", "reasoning": "dry-run"}', metadata=metadata)
    if req.task == "suggest_island_summary":
        return LLMResponse(
            raw_text='{"summaryText": "島の表札候補（dry-run）", "groundingIds": ["c01"], "warnings": []}',
            metadata=metadata,
        )
    raise ProviderRequestError.validation(f"unexpected task {req.task}", metadata)


def _generate(req: LLMRequest, dry_run: bool) -> LLMResponse:
    if dry_run:
        return _stub_generate(req)
    try:
        return generate_with_fallback(req)
    except (ProviderDisabledError, ProviderRequestError) as exc:
        print(f"  ERROR: {exc}", file=sys.stderr)
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description="KJ-operation quality evaluation (AI-EVAL-01)")
    parser.add_argument("--dry-run", action="store_true", help="Use stub provider (no API key needed)")
    parser.add_argument("--refine-count", type=int, default=10, help="Number of cards to refine (default 10)")
    args = parser.parse_args()

    if not FIXTURE.exists():
        print(f"Error: fixture not found: {FIXTURE}", file=sys.stderr)
        return 1

    doc = DocumentV1.model_validate(json.loads(FIXTURE.read_text(encoding="utf-8")))
    mode = "DRY-RUN (stub)" if args.dry_run else "REAL-API (DeepSeek)"
    print(f"=== AI Evaluation ({mode}) ===")
    print(f"Document: {doc.id} ({len(doc.cards)} cards, {len(doc.islands)} islands)")

    # --- refine_card_text (10 samples) ---
    print("\n## 評価1: refine_card_text")
    print("| # | 入力 | 出力 | 3軸判定 |")
    print("|---|------|------|---------|")
    passed = 0
    for i, card in enumerate(doc.cards[: args.refine_count], start=1):
        req = RefineCardTextRequest(cardText=card.text)
        try:
            resp = _generate(LLMRequest(task="refine_card_text", prompt=card.text), args.dry_run)
            import json as _json

            parsed = _json.loads(resp.raw_text)
            refined = parsed.get("refinedText", "(parse failed)")
        except Exception as exc:  # noqa: BLE001 - evaluation continues per sample
            refined = f"(error: {exc})"
        print(f"| {i} | {card.text[:30]} | {refined[:50]} | 要確認 |")
        if refined and not refined.startswith("("):
            passed += 1

    print(f"\n合格数: {passed}/{args.refine_count}（3軸の定性判定は人間が実施）")

    # --- suggest_island_summary (4 islands) ---
    print("\n## 評価2: suggest_island_summary")
    print("| # | 島 | 出力表札 | 3軸判定 |")
    print("|---|----|---------|---------|")
    summary_passed = 0
    for i, island in enumerate(doc.islands, start=1):
        req = SuggestIslandSummaryRequest(doc=doc, islandId=island.id)
        try:
            resp = _generate(LLMRequest(task="suggest_island_summary", prompt=req.model_dump_json()), args.dry_run)
            import json as _json

            parsed = _json.loads(resp.raw_text)
            summary = parsed.get("summaryText", "(parse failed)")
        except Exception as exc:  # noqa: BLE001
            summary = f"(error: {exc})"
        print(f"| {i} | {island.id} ({len(island.cardIds)}枚) | {summary[:50]} | 要確認 |")
        if summary and not summary.startswith("("):
            summary_passed += 1

    print(f"\n合格数: {summary_passed}/{len(doc.islands)}（3軸の定性判定は人間が実施）")

    print("\n=== 手順 ===")
    print("1. 3軸（名詞止め解除・元意味保持/代弁性・過剰言い換えなし）で定性判定")
    print("2. 結果を 01_Plans/dogfood/ai_eval_results.md のテーブルへ記録")
    print("3. 2軸以上合格で「実用可」。L2基準③は2操作以上で実用可なら達成")
    return 0


if __name__ == "__main__":
    sys.exit(main())
