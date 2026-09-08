# Issue: DOGFOOD-18 タイトル提案（suggest-document-title）が文書内容に接地せず、E2Eで検証できない

- Type: Process / Verification gap（ドッグフーディング観察）
- Status: Done
- Source Issue: ドッグフーディング iteration 183（シナリオ113・書店 実装時の実走行観察）。島ラベル「書店の棚づくりと品揃え戦略」とカード本文を指定して `suggest-document-title` を実行しても、モックが常に `{"title":"（モック）タイトル候補"}` という**汎用候補**を返し、タイトル提案が**文書のテーマ（島ラベル）に接地しているか**を E2E で検証できないことを再現確認した。
- Priority: P2
- Owner: Maintainer
- Scope: `03_Implement/deploy/tools/mock_local_llm.py`, `03_Implement/backend/scripts/verify_business_flow_e2e.sh`（シナリオ113）, `01_Plans/dogfood/business-flow-e2e-scenarios-2026-08-15.md`
- Related ADR/Spec: `00_Prompt/ai_kj_execution_procedures.md`（文書タイトル提案は低〜中深度・人間が編集前提）, `02_Architecture/api.md`（suggest-document-title 契約・candidates）, `01_Plans/dogfood/business-flow-e2e-scenarios-2026-08-15.md`（シナリオ8のみがタイトル提案を固定）
- Expected verification level: `e2e`

## 課題

業務フローE2E で `suggest-document-title`（タイトル提案）を固定しているのは **シナリオ8のみ**であり、そのアサーションは `"candidates"` キーの存在だけを確認する。モックは文書内容に依らず**同一の汎用候補**を返す:

```python
if task == "suggest_document_title":
    return json.dumps({"candidates": [{"title": "（モック）タイトル候補"}]})
```

したがって:

- **タイトル提案が文書のテーマ（島ラベル・カード本文）に接地しているか**を E2E で一切検証できない。
- バックエンドがタイトルを無関係な/汎用的な候補に劣化させる回帰が起きても、業務フローE2E は全部 pass する。
- タイトル命名（KJ法の文書全体の表象）はプロダクト価値の一角であり、その接地性が未固定。

実機再現（iteration 183）:

```text
# islandTitles=["書店の棚づくりと品揃え戦略"] を送る
# → {"candidates":[{"title":"（モック）タイトル候補"}]}（文書内容と無関係な汎用候補）
```

### なぜ問題か

- **タイトルの接地（文書テーマの反映）が未検証**: タイトルが島ラベル・カード本文のどれにも接地していないと、文書全体の表象として機能しない。
- **操作カバーの偏り**: suggest-document-title はシナリオ8のみで固定されており、カバーが薄い（11呼び出し中、内容検証はなし）。

## 三要素分析（ADR-0067）

| 次元 | 分析 | 他次元への制約 |
|------|------|---------------|
| **業務設計** | 定性分析者は文書全体のテーマを一言で捉える**タイトル候補**（1〜3件・対等）を得たい。タイトルは島ラベル・カード本文に接地していなければ候補として機能しない | タイトルは **proposal（read-only）** のまま。自動確定・文書タイトルへの適用はしない |
| **データ設計** | suggest-document-title のプロンプトは `Island labels:`（島ラベル）を含むため、モックは**最初の島ラベルを候補へ埋め込む**ことで「文書テーマへの接地」を決定的に表現できる | 既存シナリオ8の `"candidates"` キー assert は、ラベル埋め込み後も成立（非後退） |
| **機能設計** | `suggest_document_title` の応答を「（モック）<島ラベル>のタイトル候補」の形へ変更し、シナリオ113のタイトルチェックで**文書テーマ（棚づくり）を参照する**ことを assert する。API契約（`SuggestDocumentTitleResponse`）は不変 | バックエンド実装・API契約は変更しない。既存シナリオ8は `"candidates"` キーのみ assert のため非後退 |

## 対応方針

- 実施すること:
  1. `mock_local_llm.py` の `suggest_document_title` で、プロンプトの `Island labels:` から**最初の島ラベルを抽出し候補タイトルへ埋め込む**。
  2. シナリオ113（書店）に **suggest-document-title（タイトル提案）** を操作内容へ追加し、タイトルチェックで**文書テーマ（棚づくり）を参照**することを assert する（操作カバーをシナリオ8のみから拡大）。
- 実施しないこと:
  - suggest-document-title の**バックエンド実装・API契約の変更**。
  - 既存シナリオ8のタイトルアサーションの変更（`"candidates"` キーのみ assert・非後退）。

## 受入条件

- [x] 島ラベル「書店の棚づくりと品揃え戦略」のタイトル候補に「棚づくり」が含まれる（実走行で確認）。
- [x] 既存シナリオ8相当（「入社手続き」）も `"candidates"` を返す（非後退・実走行で確認）。
- [x] シナリオ113のタイトルチェックが `"candidates"` かつ文書テーマ「棚づくり」を assert し、業務フローE2E が **671/671 pass**。
- [x] `verify_dogfood_records.sh`・`docs_check.py` が pass。

## 検証計画

- `cd 03_Implement/backend && bash scripts/verify_business_flow_e2e.sh <PORT>` → 671/671（シナリオ113の BK ②タイトル提案が文書テーマを参照）
- `bash 01_Plans/dogfood/verify_dogfood_records.sh` → 構造照合 pass
- `python 01_Plans/docs_check.py` → docs-check passed

## 補足

- モックの島ラベル埋め込みは「タイトルが文書テーマに接地する」ことを検証可能にする決定性表現であり、実LLMのタイトル生成品質とは独立（本issueは検証ハーネスの能力向上）。
- ドッグフーディング観察起点（2026-08-16・iteration 183）: 書店（棚づくりと在庫戦略）のタイトル提案を実行し、文書内容と無関係な汎用候補が返ることを再現。タイトルの接地（文書テーマの反映）がE2Eで検証不能であることを特定した。


## 配置の整理（2026-09-05）

- 本Issueは、文書タイトル提案を汎用候補から文書テーマへ接地し、さらに複数島の全体テーマを反映できることをE2Eで固定した verification harness 改善として `Done` となっていた。
- `DOGFOOD-18` がタイトル候補の文書テーマ接地を固定し、`DOGFOOD-26` が先頭島バイアスを解消して全島テーマへ拡張したため、suggest-document-title の成熟系列として同時に正規配置へ移した。
- `LEGACY_DONE_AT_ROOT_BASELINE` は20から18へ縮小し、R18 identity manifestは不変の歴史境界として維持する。
- 旧rootパス引用は完全一致探索で検出し、現在の `done/` パスへ同時更新した。
