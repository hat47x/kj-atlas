#!/usr/bin/env python3
"""Generate the W-type round-5 (具体策) cards for kj-atlas self-improvement.

Round 5 posture (具体策) turns the 構想 (conception) into SPECIFIC measures:
concrete API contracts, fields, UI elements, and E2E tests grounded in the
current codebase (models_ai.py, routes/ai.py, schemas.md).
"""
from __future__ import annotations

import json

CARDS: list[tuple[str, str]] = [
    # --- 凝縮操作の具体策 ---
    ("cm-01", "SuggestIslandSummaryResponse に複数候補 candidates を追加すべき（凝縮具体策）"),
    ("cm-02", "接地 groundingIds と凝縮 summaryText を別フィールドで分離すべき（凝縮具体策）"),
    ("cm-03", "凝縮候補に「志」の根拠（どのカードの何に応じたか）を付与すべき（凝縮具体策）"),
    ("cm-04", "凝縮候補の戻し検査・転置検査をUIで人間が実行できるべき（凝縮具体策）"),
    ("cm-05", "凝縮候補を代弁文（述語文）に強制し分類名を弾くべき（凝縮具体策）"),
    ("cm-06", "凝縮の複数候補を対等な代替案として返すべき（凝縮具体策）"),
    ("cm-07", "flashで複数候補の初期生成・proで深い凝縮を担うルーティングを設けるべき（凝縮具体策）"),
    ("cm-08", "凝縮候補の proposal-only を維持すべき（凝縮具体策）"),
    ("cm-09", "凝縮は複数カード→1表札の多対一圧縮として明示すべき（凝縮具体策）"),
    ("cm-10", "凝縮候補の採用で human_reviewed を人手昇格すべき（凝縮具体策）"),

    # --- 壁打ちの具体策 ---
    ("cw2-01", "凝縮専用のチャットパネルを島の詳細に追加すべき（壁打ち具体策）"),
    ("cw2-02", "壁打ちで複数候補を比較表示するUIを設けるべき（壁打ち具体策）"),
    ("cw2-03", "違和感（critique）に応じて代替候補を再生成するボタンを設けるべき（壁打ち具体策）"),
    ("cw2-04", "壁打ちの対話履歴を作業状態として保持すべき（壁打ち具体策）"),
    ("cw2-05", "壁打ちの代替候補に再解釈の根拠を付与すべき（壁打ち具体策）"),
    ("cw2-06", "DOMAIN-EXPR-03の再提案を継続的な壁打ちへ発展すべき（壁打ち具体策）"),
    ("cw2-07", "壁打ちの収束（志の確定）は人間のadoptで行うべき（壁打ち具体策）"),
    ("cw2-08", "壁打ちで無修正採用（認知的放棄）を防ぐ導線を設けるべき（壁打ち具体策）"),

    # --- 多段編成の具体策 ---
    ("hi4-01", "parentIslandId の親子関係をCRUDするAPIを設けるべき（多段具体策）"),
    ("hi4-02", "card-groupsの結果を島へ畳み込む一括操作を設けるべき（多段具体策）"),
    ("hi4-03", "一行見出し（表札）の連鎖をUIで示すべき（多段具体策）"),
    ("hi4-04", "インデックス図解（全体）と展開（細部）のドリルダウンを実装すべき（多段具体策）"),
    ("hi4-05", "多段の各段で核融合法（凝縮）を適用すべき（多段具体策）"),
    ("hi4-06", "階層島の往復保持・循環フォールバックをE2Eで固定すべき（多段具体策）"),
    ("hi4-07", "グループ約3枚・最大10グループの目安をUIで提示すべき（多段具体策）"),
    ("hi4-08", "畳み込みの履歴を可逆に保持すべき（多段具体策）"),

    # --- 複層キャンバスの具体策 ---
    ("ml3-01", "WorkingGraph/ContextProjectionGraph/Consensusの分離をschemas.mdで固定すべき（複層具体策）"),
    ("ml3-02", "AI提案がConsensus Graphを直接更新しないことをE2Eで固定すべき（複層具体策）"),
    ("ml3-03", "凝縮層が人間/AIを連動させるAPI契約を定義すべき（複層具体策）"),
    ("ml3-04", "AIはContextQueryV1で投影しWorkingGraphを直接読み書きしないべき（複層具体策）"),
    ("ml3-05", "proposal-only・human_reviewed・SafeModeを不変条件としてE2Eで固定すべき（複層具体策）"),
    ("ml3-06", "カードの境界オブジェクト（外在化）としての役割をUIで示すべき（複層具体策）"),

    # --- 選択的探索の具体策 ---
    ("sq3-01", "ContextQueryV1に島の近傍・未読・矛盾接続の探索パラメータを追加すべき（探索具体策）"),
    ("sq3-02", "AIが能動的にクエリを拡張する導線（探索リクエスト）を設けるべき（探索具体策）"),
    ("sq3-03", "選択的探索と凝縮を一体で扱うAPIを設計すべき（探索具体策）"),
    ("sq3-04", "選択的探索が20,000枚でも部分集合に留まることをE2Eで固定すべき（探索具体策）"),
    ("sq3-05", "excludedReason・queryCanonicalHashを選択的探索の監査キーとして保持すべき（探索具体策）"),
    ("sq3-06", "centrality.rank低位カードの除外を探索に活かすべき（探索具体策）"),

    # --- E2E固定の具体策 ---
    ("et-01", "凝縮（複数候補・接地/凝縮分離）のE2Eを新設すべき（E2E具体策）"),
    ("et-02", "壁打ち（対話的洗練）のE2Eを新設すべき（E2E具体策）"),
    ("et-03", "多段編成（parentIslandId畳み込み）のE2Eを新設すべき（E2E具体策）"),
    ("et-04", "選択的探索（能動的クエリ拡張）のE2Eを新設すべき（E2E具体策）"),
    ("et-05", "複層キャンバス（人間/AI棲み分け）のE2Eを新設すべき（E2E具体策）"),
    ("et-06", "各具体策を三要素分析付きのissueへ起票すべき（E2E具体策）"),
]

def build_round5_cards() -> list[dict]:
    return [
        {"id": cid, "text": text, "x": (i % 10) * 28, "y": (i // 10) * 16, "textReviewed": True}
        for i, (cid, text) in enumerate(CARDS)
    ]


if __name__ == "__main__":
    print(json.dumps(build_round5_cards(), ensure_ascii=False))
