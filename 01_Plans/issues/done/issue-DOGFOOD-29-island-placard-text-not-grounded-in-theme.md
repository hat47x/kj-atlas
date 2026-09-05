# Issue: DOGFOOD-29 島要約の表札（summaryText）が島のメンバーカードのテーマを参照せず、E2Eで検証できない

- Type: Process / Verification gap（ドッグフーディング観察）
- Status: Done
- Source Issue: ドッグフーディング iteration 193（シナリオ123・自転車店 実装時の実走行観察）。`suggest-island-summary` は最も多用される操作（91回）だが、表札（`summaryText`）が**常に汎用文字列**（「メンバーカードに基づく下書き要約です」）で、**島のメンバーカードのテーマ（顧客サービス等）を参照しない**ことを再現確認した。DOGFOOD-13 で接地カード（groundingIds）は固定済みだが、表札文面が島の内容に接地していない。
- Priority: P2
- Owner: Maintainer
- Scope: `03_Implement/deploy/tools/mock_local_llm.py`, `03_Implement/backend/scripts/verify_business_flow_e2e.sh`（シナリオ123）, `01_Plans/dogfood/business-flow-e2e-scenarios-2026-08-15.md`
- Related ADR/Spec: `00_Prompt/kj_technique.md` §3（表札は代弁・戻し検査）, `00_Prompt/qualitative_card_quality_requirements.md`, `02_Architecture/api.md`（suggest-island-summary 契約）, `01_Plans/issues/done/issue-DOGFOOD-13-island-summary-grounding-capped-at-three-cards.md`（接地カードの全接地）, `01_Plans/issues/done/issue-DOGFOOD-21-narrative-text-not-grounded-in-reading-order.md`（テキスト接地の同型）
- Expected verification level: `e2e`

## 課題

業務フローE2E の `suggest-island-summary`（島要約・表札）は**最も多用される操作（91シナリオ）**だが、全シナリオが `groundingIds`（+ DOGFOOD-13 以降の全接地）だけを確認し、**表札文面（`summaryText`）が島のメンバーカード内容に接地しているか**は検証しない。モックの表札は常に同一の汎用文字列:

```python
"summaryText": "（モック）メンバーカードに基づく下書き要約です。レビュー前の暫定です。"
```

したがって:

- **表札（島の代弁文）がメンバーカードのテーマを反映しているか**を E2E で一切検証できない。
- バックエンドが表札を無関係な/汎用的な文面に劣化させる回帰（島の内容を代弁しない）が起きても、業務フローE2E は全部 pass する。
- 表札はKJ法の**核**（島を代弁する述語文・戻し検査の対象）であり、その代弁性・接地が未固定。

実機再現（iteration 193）:

```text
# 自転車店の島（顧客サービス・在庫・品揃え等のテーマ）で suggest-island-summary
# → summaryText="（モック）メンバーカードに基づく下書き要約です。レビュー前の暫定です。"
#   （島のテーマを一切参照しない）
```

### なぜ問題か

- **表札の代弁性・接地が未検証**: 表札が島の内容（メンバーカードのテーマ）を反映しないと、島の代弁として機能しない。
- **最も多用される操作の検証深度の偏り**: 接地カード（groundingIds）は固定されたが、表札文面の接地は未固定。
- **補足（技術的要因）**: 島要約プロンプトはカード文を `json.dumps`（`\uXXXX`エスケープ）で送るため、モックが `（カテゴリ）` を抽出するには**デコード**が必要。単純な文字列検索では検出できない。

## 三要素分析（ADR-0067）

| 次元 | 分析 | 他次元への制約 |
|------|------|---------------|
| **業務設計** | 定性分析者は島を**代弁する述語文（表札）**を、メンバーカードのテーマを反映して得たい。汎用文では島の代弁にならない（kj_technique.md §3） | 島要約は **proposal 相当（read-only の下書き）** のまま。自動確定しない |
| **データ設計** | 島要約プロンプトはメンバーカード行（`- id="<id>", text="<text>"`・json.dumpsエスケープ）を含むため、モックは**デコードして（カテゴリ）テーマを抽出**し表札へ埋め込むことで「島の内容への接地」を決定的に表現できる | 既存の `groundingIds` assert は、表札文面を変えても成立（非後退）。カテゴリなしのカード（scenario 1等）は従来の汎用文面 |
| **機能設計** | `suggest_island_summary` の表札を「（モック）<テーマ>をテーマとするメンバーカードに基づく下書き要約…」へ変更し、シナリオ123の島要約チェックで**表札がテーマ（顧客サービス）を参照**することを assert する。API契約（`SuggestIslandSummaryResponse`）は不変 | バックエンド実装・API契約は変更しない。既存シナリオは `groundingIds` キー assert のため非後退 |

## 対応方針

- 実施すること:
  1. `mock_local_llm.py` の `suggest_island_summary` で、プロンプトのメンバーカード行から（カテゴリ）テーマを**デコードして抽出**し表札へ埋め込む。
  2. シナリオ123（自転車店）の島要約チェックで、**表札がテーマ（顧客サービス）を参照**することを assert する。
- 実施しないこと:
  - suggest-island-summary の**バックエンド実装・API契約の変更**。
  - 既存シナリオ（1〜122）の島要約アサーションの変更（`groundingIds` キー assert・非後退）。

## 受入条件

- [x] 自転車店の島（顧客サービス等）の表札が「顧客サービス」を参照する（実走行で確認）。
- [x] カテゴリなしのカード（scenario 1相当）は従来の汎用表札（非後退・実走行で確認）。
- [x] シナリオ123の島要約チェックが `summaryText` かつテーマ参照を assert し、業務フローE2E が **741/741 pass**（並行編集によるMGシナリオの干渉がない場合）。
- [x] `verify_dogfood_records.sh`・`docs_check.py` が pass。

## 検証計画

- `cd 03_Implement/backend && bash scripts/verify_business_flow_e2e.sh <PORT>` → 741/741（シナリオ123の BK ③島要約が表札でテーマを参照）
- `bash 01_Plans/dogfood/verify_dogfood_records.sh` → 構造照合 pass
- `python 01_Plans/docs_check.py` → docs-check passed

## 補足

- モックのテーマ抽出は、島要約プロンプトがカード文を `json.dumps`（`\uXXXX`エスケープ）で送ることを考慮して**デコード**して行う。これは「表札が島の内容に接地する」ことを検証可能にする決定性表現であり、実LLMの表札品質とは独立（本issueは検証ハーネスの能力向上）。DOGFOOD-13（接地カード）の延長。
- ドッグフーディング観察起点（2026-08-16・iteration 193）: 自転車店（顧客サービス・在庫・品揃え等のテーマ）で suggest-island-summary を実行し、表札が島のテーマを一切参照しないことを再現。表札の代弁性・接地がE2Eで検証不能であることを特定した。


## 配置の整理（2026-09-05）

- 本Issueは、接地IDの存在だけでなく生成本文そのものが対象の島・テーマへ接地することをE2Eで決定的に検証できるようにした verification harness 改善として `Done` となっていた。
- `DOGFOOD-28` と `DOGFOOD-29` は、既存の grounding 保全を前提に、関係要約本文と島表札本文の意味接地をそれぞれ固定した同型の小さなまとまりとして同時に `01_Plans/issues/done/` へ移した。
- `LEGACY_DONE_AT_ROOT_BASELINE` は31から29へ縮小し、R18 identity manifestは不変の歴史境界として維持する。
- 旧rootパス引用は完全一致探索で検出し、現在の `done/` パスへ同時更新した。
