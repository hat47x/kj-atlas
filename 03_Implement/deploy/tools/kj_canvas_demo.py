#!/usr/bin/env python3
"""KJ Canvas Demo — 人間と生成AIのコラボレーション実演.

複数LLMモデルを組み合わせたKJ法キャンバスの一連の操作を実演します。

Usage:
    # モックLLMで高速デモ（GPU不要）
    python3 kj_canvas_demo.py

    # 実LLMでデモ（Ollama起動済みであること）
    python3 openai_compatible_adapter.py --port 8001 &
    python3 kj_canvas_demo.py --real

    # DeepSeek v4 multi-modelデモ
    python3 openai_compatible_adapter.py --port 8001 \
      --backends "deepseek-v4-flash@https://api.deepseek.com/v1:sk-xxx,deepseek-v4-pro@https://api.deepseek.com/v1:sk-xxx" \
      --default-model deepseek-v4-flash &
    python3 kj_canvas_demo.py --real
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from typing import Any

import httpx

MOCK_URL = "http://localhost:8001/generate"
TASKS = [
    "refine_card_text",
    "suggest_card_groups",
    "detect_contradiction",
    "assess_card_importance",
    "re_layout",
    "suggest_merges",
    "suggest_island_summary",
    "summarize_island_relation",
    "generate_narrative",
    "check_narrative",
]

# ---- Mock LLM management ----


def _start_mock():
    subprocess.Popen(
        [sys.executable,
         "/mnt/d/GIT/kj-atlas/03_Implement/deploy/tools/mock_local_llm.py",
         "--host", "127.0.0.1", "--port", "8001"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    for _ in range(20):
        time.sleep(0.1)
        try:
            httpx.get("http://localhost:8001/", timeout=0.5)
            return
        except Exception:
            pass


# ---- LLM call ----


def call_llm(task: str, prompt: str, model: str = "mock",
             temperature: float = 0.2) -> dict[str, Any]:
    r = httpx.post(MOCK_URL, json={
        "task": task, "prompt": prompt,
        "temperature": temperature, "max_tokens": 500, "model": model,
    }, timeout=130)
    r.raise_for_status()
    return json.loads(r.json()["text"])


# ---- Demo phases ----


def demo_phase(label: str):
    print(f"\n{'='*60}")
    print(f"  {label}")
    print(f"{'='*60}")


def phase1_card_creation():
    """6枚のカードを作成し、AIが文面を改善。"""
    demo_phase("Phase 1: カード作成 → AI文面改善")
    cards = [
        "システムはユーザが閉じるときに自動でデータを保存するべき",
        "外部の人と共有するためにPDF出力が必要",
        "編集の安全のためにUndo機能が重要",
        "情報を見つけるために全文検索が必要",
        "夜間作業のためにダークモードが欲しい",
        "チーム作業のためにリアルタイム共同編集が必須",
    ]
    refined = []
    for i, text in enumerate(cards):
        data = call_llm("refine_card_text",
                        f"Card text: {text}\nContext: プロダクト要件KJセッション。")
        refined.append(data["refinedText"])
        print(f"  [{i+1}] {text[:40]}... → {data['refinedText'][:50]}...")
    return refined


def phase2_grouping(cards: list[str]):
    """カードをグループ化して島を作る。"""
    demo_phase("Phase 2: カードグルーピング → 島形成")
    card_list = [{"id": f"c{i}", "text": t} for i, t in enumerate(cards)]
    prompt = "\n".join(f'- id="{c["id"]}", text="{c["text"]}"' for c in card_list)
    for model in ["mock", "deepseek-v4-flash"]:
        data = call_llm("suggest_card_groups", prompt, model=model)
        groups = data.get("groups", [])
        print(f"  model={model}: {len(groups)} groups")
        for g in groups:
            print(f"    - {g['label']}: {g['cardIds']}")
        if model == "mock":
            break  # Only test multi-model if real LLM available


def phase3_contradiction():
    """矛盾検出。"""
    demo_phase("Phase 3: 矛盾検出")
    pairs = [
        ("データはサーバにのみ保存する", "データはオフラインでも使える必要がある"),
        ("SSOで認証する", "ゲストはログインなしでアクセス可能"),
    ]
    for a, b in pairs:
        data = call_llm("detect_contradiction",
                        f"Card A: {a}\nCard B: {b}")
        status = "⚡矛盾あり" if data["hasContradiction"] else "✓ 矛盾なし"
        print(f"  「{a[:30]}...」 vs 「{b[:30]}...」 → {status}")


def phase4_importance():
    """重要度評価。"""
    demo_phase("Phase 4: 重要度評価 → 優先順位付け")
    cards = [
        ("p1", "セキュリティ監査ログ"),
        ("p2", "ダークモード配色"),
        ("p3", "リアルタイム同期"),
        ("p4", "PNG形式出力"),
        ("p5", "二要素認証"),
    ]
    prompt = "\n".join(f'- id="{i}", text="{t}"' for i, t in cards)
    data = call_llm("assess_card_importance", prompt)
    for a in data["assessments"]:
        bar = {"high": "■■■", "medium": "■■□", "low": "■□□"}.get(a["importance"], "???")
        print(f"  {bar} {a['cardId']}: {a.get('rationale', '')[:50]}")


def phase5_layout_and_merges():
    """レイアウト提案と統合候補。"""
    demo_phase("Phase 5: レイアウト + 統合候補")
    prompt = (
        '- id="a", text="自動保存"\n'
        '- id="b", text="閉じるとき自動保存"\n'
        '- id="c", text="PDF出力"\n'
        '- id="d", text="PNG出力"'
    )
    layout = call_llm("re_layout", prompt)
    print(f"  Layout: {len(layout.get('cards', []))} cards placed")

    merges = call_llm("suggest_merges", prompt)
    print(f"  Merges: {len(merges.get('suggestions', []))} suggestions")


def phase6_narrative():
    """ナラティブ生成 + 検証。"""
    demo_phase("Phase 6: ナラティブ生成 + 品質チェック")
    prompt = '- 1. card id="a"\n- 2. card id="b"'
    narrative = call_llm("generate_narrative", prompt)
    text = narrative.get("text", "")
    print(f"  Narrative: {text[:80]}...")

    check = call_llm("check_narrative",
                     f'Narrative: {text}\nCards: a, b')
    issues = check.get("issues", [])
    print(f"  Issues found: {len(issues)}")


def phase7_island_relation():
    """島の要約と関係性。"""
    demo_phase("Phase 7: 島の要約 + 島間関係")
    summary = call_llm("suggest_island_summary",
                       '- id="a", text="自動保存でデータ損失防止"\n'
                       '- id="b", text="出力で共有を可能に"')
    print(f"  Summary: {summary.get('summaryText', '')[:60]}...")

    relation = call_llm("summarize_island_relation",
                        "Relation between data safety and sharing. Return JSON.")
    print(f"  Relation: {relation.get('text', '')[:60]}...")


def main():
    parser = argparse.ArgumentParser(description="KJ Canvas Demo")
    parser.add_argument("--real", action="store_true",
                        help="Use real LLM (requires adapter on port 8001)")
    args = parser.parse_args()

    print("╔══════════════════════════════════════════════════════╗")
    print("║   KJ法キャンバス — 人間×生成AI コラボレーション    ║")
    print("╚══════════════════════════════════════════════════════╝")

    if not args.real:
        _start_mock()
        print("\n  Mode: Mock LLM (高速デモ)")
        print("  全10タスクを決定論的スタブで実演します")
    else:
        print("\n  Mode: 実LLM (adapter on port 8001)")
        print("  複数モデルを組み合わせた本格デモ")

    # Run all 7 phases
    cards = phase1_card_creation()
    phase2_grouping(cards)
    phase3_contradiction()
    phase4_importance()
    phase5_layout_and_merges()
    phase6_narrative()
    phase7_island_relation()

    demo_phase("完了")
    print(f"  {len(TASKS)} AIタスクすべて完了")
    print("  人間のKJ法作業をAIが支援する一連の流れを実証しました")
    print()


if __name__ == "__main__":
    main()
