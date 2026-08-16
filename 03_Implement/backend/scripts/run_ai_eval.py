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

from fastapi.testclient import TestClient

from kj_atlas_api.llm.provider import (
    LLMCallMetadata,
    LLMRequest,
    LLMResponse,
    ProviderDisabledError,
    ProviderRequestError,
    generate_with_fallback,
)
from kj_atlas_api.main import app
from kj_atlas_api.models import DocumentV1

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
FIXTURE = REPO_ROOT / "03_Implement" / "backend" / "tests" / "fixtures" / "ai_eval_kj_document.json"

# Evaluation rubric (qualitative, anti-scoring)
REFINE_AXES = ("名詞止め解除", "元意味保持", "過剰言い換えなし")
SUMMARY_AXES = ("別島に載せても成立しない", "代弁性", "名詞止め解除")


def _stub_generate(req: LLMRequest) -> LLMResponse:
    """Stub provider for --dry-run (returns canned but schema-valid output).

    For suggest_island_summary, echoes the requested island's own member
    card as groundingId so the backend member-card validation passes.
    """
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
        # The prompt (built by the real route) lists member cards after
        # "Member cards:"; pick those ids as grounding so the backend's
        # member-card validation passes.
        import re as _re

        member_section = req.prompt.split("Member cards:", 1)[1] if "Member cards:" in req.prompt else req.prompt
        ids = _re.findall(r'id="([^"]+)"', member_section)
        grounding = ids[:1] if ids else ["c01"]
        return LLMResponse(
            raw_text=json.dumps(
                {"summaryText": "島の表札候補（dry-run）", "groundingIds": grounding, "warnings": []},
                ensure_ascii=False,
            ),
            metadata=metadata,
        )
    raise ProviderRequestError.validation(f"unexpected task {req.task}", metadata)


def main() -> int:
    """Run evaluation through the REAL FastAPI endpoints (TestClient).

    Uses the actual /ai/* routes so the real prompt builders
    (_build_refine_card_text_prompt etc.) are exercised — the same
    prompt instructions a production client receives.
    """
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

    # Dry-run: swap the routes' generate_with_fallback with a stub so the
    # real endpoint flow is exercised without calling the API.
    original_generate = None
    if args.dry_run:
        from kj_atlas_api.routes import ai

        original_generate = ai.generate_with_fallback
        ai.generate_with_fallback = _stub_generate

    try:
        _run_eval(client_app=app, doc=doc, refine_count=args.refine_count)
    finally:
        if original_generate is not None:
            from kj_atlas_api.routes import ai

            ai.generate_with_fallback = original_generate
    return 0


def _run_eval(client_app, doc: DocumentV1, refine_count: int) -> None:
    """Run evaluation through the real endpoints via TestClient."""
    with TestClient(client_app) as client:
        # --- refine_card_text (10 samples) via real endpoint ---
        print("\n## 評価1: refine_card_text（POST /ai/refine-card-text）")
        print("| # | 入力 | 出力 | 3軸判定 |")
        print("|---|------|------|---------|")
        passed = 0
        for i, card in enumerate(doc.cards[: refine_count], start=1):
            resp = client.post(
                "/ai/refine-card-text",
                json={"cardText": card.text, "textReviewed": True},
            )
            if resp.status_code == 200:
                body = resp.json()
                refined = body.get("refinedText", "(missing refinedText)")
                passed += 1
            else:
                refined = f"(HTTP {resp.status_code})"
            print(f"| {i} | {card.text[:30]} | {refined[:50]} | 要確認 |")
        print(f"\n成功: {passed}/{refine_count}（3軸の定性判定は人間が実施）")

        # --- suggest_island_summary (4 islands) via real endpoint ---
        print("\n## 評価2: suggest_island_summary（POST /ai/suggest-island-summary）")
        print("| # | 島 | 出力表札 | 3軸判定 |")
        print("|---|----|---------|---------|")
        summary_passed = 0
        for i, island in enumerate(doc.islands, start=1):
            resp = client.post(
                "/ai/suggest-island-summary",
                json={"doc": doc.model_dump(mode="json"), "islandId": island.id},
            )
            if resp.status_code == 200:
                body = resp.json()
                summary = body.get("summaryText", "(missing summaryText)")
                summary_passed += 1
            else:
                summary = f"(HTTP {resp.status_code})"
            print(f"| {i} | {island.id} ({len(island.cardIds)}枚) | {summary[:60]} | 要確認 |")
        print(f"\n成功: {summary_passed}/{len(doc.islands)}（3軸の定性判定は人間が実施）")

    print("\n=== 手順 ===")
    print("1. 3軸（名詞止め解除・元意味保持/代弁性・過剰言い換えなし）で定性判定")
    print("2. 結果を 01_Plans/dogfood/ai_eval_results.md のテーブルへ記録")
    print("3. 2軸以上合格で「実用可」。L2基準③は2操作以上で実用可なら達成")
    return 0


if __name__ == "__main__":
    sys.exit(main())
