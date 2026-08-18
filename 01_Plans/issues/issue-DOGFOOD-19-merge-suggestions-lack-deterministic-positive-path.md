# Issue: DOGFOOD-19 マージ提案（suggest-merges）に決定的正パスがなく、E2Eで統合提案を検証できない

- Type: Process / Verification gap（ドッグフーディング観察）
- Status: Done
- Source Issue: ドッグフーディング iteration 184（シナリオ114・税理士/会計事務所 実装時の実走行観察）。同じカテゴリ（業務効率）のカード対 `a1`/`a2` を含む文書で `suggest-merges` を実行しても、モックが常に `{"suggestions":[]}` を返し、**統合提案（似たカードのマージ候補）の正パスを E2E で一切検証できない**ことを再現確認した。
- Priority: P2
- Owner: Maintainer
- Scope: `03_Implement/deploy/tools/mock_local_llm.py`, `03_Implement/backend/scripts/verify_business_flow_e2e.sh`（シナリオ114）, `01_Plans/dogfood/business-flow-e2e-scenarios-2026-08-15.md`
- Related ADR/Spec: `00_Prompt/kj_technique.md` §2（束ねは訴えの類似性）, `02_Architecture/api.md`（suggest-merges 契約・suggestions スキーマ）, `01_Plans/dogfood/business-flow-e2e-scenarios-2026-08-15.md`（シナリオ11/48/66等が `"suggestions"` キーのみ assert）
- Expected verification level: `e2e`

## 課題

業務フローE2E の `suggest-merges`（島統合提案）は、シナリオ11（会議ファシリテーター）・シナリオ48（美術館）等で `"suggestions"` **キーの存在**だけを確認している。モックは常に空提案を返す:

```python
if task == "suggest_merges":
    return json.dumps({"suggestions": []})
```

したがって:

- **統合提案（似たカードのマージ候補）が実際に生成されることを E2E で一切検証できない**（正パスなし）。
- バックエンドが常に空提案を返す回帰（マージ検出が壊れる）が起きても、業務フローE2E は全部 pass する。
- kj_technique.md §2 の「訴えの類似性による束ね」の延長である統合提案（類似カードの統合）が未固定。

実機再現（iteration 184）:

```text
# 同カテゴリ（業務効率）のカード a1/a2 を含む文書で suggest-merges
# → {"suggestions":[]}（統合候補が生成されない）
```

### なぜ問題か

- **統合提案の正パスが未固定**: マージ候補が生成されることが検証されないため、統合機能の回帰が検知できない。
- **キー存在だけの検証**: `"suggestions"` キーの存在は「空でも通る」ため、実質的な検証になっていない。

## 三要素分析（ADR-0067）

| 次元 | 分析 | 他次元への制約 |
|------|------|---------------|
| **業務設計** | 定性分析者は**似たカード（訴えが類似）の統合候補**を提案として得たい。統合は人間の採否を経る（自動統合しない） | 統合提案は **proposal（read-only）** のまま。カード統合・削除は自動適用しない |
| **データ設計** | マージプロンプトは `- id="<id>", text="<text>"` のカード行を含むため、モックは**カード本文の（カテゴリ）**を抽出して「同じテーマのカード対」を決定的に提案できる | 既存の `"suggestions"` キー assert は、提案が空でなくとも成立（非後退） |
| **機能設計** | `suggest_merges` を「同じ（カテゴリ）を持つカード対をマージ候補として返す」へ変更し、シナリオ114のマージチェックで**カード対 a1/a2 を含む提案**を assert する。API契約（`SuggestMergesResponse`）は不変 | バックエンド実装・API契約は変更しない。既存シナリオ（11/48/66等）は `"suggestions"` キー assert のため非後退 |

## 対応方針

- 実施すること:
  1. `mock_local_llm.py` の `suggest_merges` で、カード本文の `（カテゴリ）` が一致するカード対を**マージ候補として提案**する（決定的正パス・最大10件）。
  2. シナリオ114（税理士・会計事務所）に **suggest-merges（統合提案）** を操作内容へ追加し、マージチェックで**同カテゴリのカード対（業務効率・a1/a2）を含む提案**を assert する。
- 実施しないこと:
  - suggest-merges の**バックエンド実装・API契約の変更**。
  - 既存シナリオ（11/48/66等）のマージアサーションの変更（`"suggestions"` キー assert・非後退）。

## 受入条件

- [x] 同カテゴリ（業務効率）のカード対 a1/a2 がマージ候補として提案される（実走行で確認）。
- [x] 既存シナリオ相当（カテゴリなしのカード対）も `"suggestions"` キーを返す（非後退・実走行で確認）。
- [x] シナリオ114のマージチェックが `"suggestions"` かつ a1/a2 を含む提案を assert し、業務フローE2E が **678/678 pass**。
- [x] `verify_dogfood_records.sh`・`docs_check.py` が pass。

## 検証計画

- `cd 03_Implement/backend && bash scripts/verify_business_flow_e2e.sh <PORT>` → 678/678（シナリオ114の TX ②統合提案がカード対 a1/a2 を提案）
- `bash 01_Plans/dogfood/verify_dogfood_records.sh` → 構造照合 pass
- `python 01_Plans/docs_check.py` → docs-check passed

## 補足

- モックのカテゴリ一致は「統合候補が生成される」ことを検証可能にする決定性表現であり、実LLMの統合提案品質とは独立（本issueは検証ハーネスの能力向上）。
- ドッグフーディング観察起点（2026-08-16・iteration 184）: 税理士事務所（業務効率のカード a1/a2）で suggest-merges を実行し、空提案が返ることを再現。統合提案の正パスがE2Eで検証不能であることを特定した。
