#!/usr/bin/env python3
"""Generate the W-type round-6 (手順計画) cards for kj-atlas self-improvement.

Round 6 posture (手順計画) turns the 具体策 (specific measures) into an ordered
implementation procedure: phasing, dependencies, and E2E sequencing.
"""
from __future__ import annotations

import json

CARDS: list[tuple[str, str]] = [
    # --- 手順の順序・フェーズ ---
    ("pr-01", "凝縮具体策（複数候補・接地/凝縮分離）を最優先フェーズにするべき（手順計画）"),
    ("pr-02", "凝縮の複数候補を前提に壁打ち具体策を第2フェーズにするべき（手順計画）"),
    ("pr-03", "凝縮の結果を階層化する多段具体策を第3フェーズにするべき（手順計画）"),
    ("pr-04", "複層キャンバスの分離（schemas.md固定）を並行フェーズで進めるべき（手順計画）"),
    ("pr-05", "探索具体策（ContextQueryV1拡張）を凝縮の前提として先行すべき（手順計画）"),
    ("pr-06", "各フェーズのE2Eをフェーズ内で固定すべき（手順計画）"),
    ("pr-07", "凝縮→壁打ち→多段の順で依存関係を尊重すべき（手順計画）"),
    ("pr-08", "探索→凝縮の順で部分集合決定を先行すべき（手順計画）"),

    # --- 凝縮具体策の手順 ---
    ("st-01", "SuggestIslandSummaryResponse に candidates を追加すべき（凝縮手順）"),
    ("st-02", "groundingIds と summaryText を別フィールドで分離すべき（凝縮手順）"),
    ("st-03", "凝縮候補の戻し検査・転置検査UIを実装すべき（凝縮手順）"),
    ("st-04", "flash/proのルーティングを凝縮操作に適用すべき（凝縮手順）"),
    ("st-05", "凝縮候補の proposal-only を維持すべき（凝縮手順）"),

    # --- 壁打ち具体策の手順 ---
    ("st2-01", "島詳細にチャットパネルを追加すべき（壁打ち手順）"),
    ("st2-02", "違和感→代替候補再生成ボタンを実装すべき（壁打ち手順）"),
    ("st2-03", "DOMAIN-EXPR-03の再提案を壁打ちへ発展すべき（壁打ち手順）"),
    ("st2-04", "壁打ちの対話履歴を保持すべき（壁打ち手順）"),
    ("st2-05", "壁打ちの収束を人間のadoptで行うべき（壁打ち手順）"),

    # --- 多段具体策の手順 ---
    ("st3-01", "parentIslandIdのCRUD APIを実装すべき（多段手順）"),
    ("st3-02", "card-groups→島の一括畳み込みを実装すべき（多段手順）"),
    ("st3-03", "一行見出しの連鎖UIを実装すべき（多段手順）"),
    ("st3-04", "インデックス図解＋ドリルダウンを実装すべき（多段手順）"),
    ("st3-05", "階層島の往復保持をE2Eで固定すべき（多段手順）"),

    # --- 複層・探索の手順 ---
    ("st4-01", "WorkingGraph/ContextProjectionGraph/Consensusの分離をschemas.mdで固定すべき（複層手順）"),
    ("st4-02", "proposal-only・SafeModeのE2Eを固定すべき（複層手順）"),
    ("st4-03", "ContextQueryV1に近傍・未読・矛盾接続の探索パラメータを追加すべき（探索手順）"),
    ("st4-04", "AIの能動的クエリ拡張導線を実装すべき（探索手順）"),

    # --- 検証・起票の手順 ---
    ("st5-01", "各具体策を三要素分析付きissueへ起票すべき（検証手順）"),
    ("st5-02", "各具体策のE2Eをverify_business_flow_e2e.shへ追加すべき（検証手順）"),
    ("st5-03", "規模耐性（20,000枚）のE2Eを追加すべき（検証手順）"),
    ("st5-04", "ADR（凝縮層・複層キャンバス）を起票すべき（検証手順）"),
    ("st5-05", "実装の検証をverify_dogfood_records.shで構造照合すべき（検証手順）"),
]

def build_round6_cards() -> list[dict]:
    return [
        {"id": cid, "text": text, "x": (i % 10) * 28, "y": (i // 10) * 16, "textReviewed": True}
        for i, (cid, text) in enumerate(CARDS)
    ]


if __name__ == "__main__":
    print(json.dumps(build_round6_cards(), ensure_ascii=False))
