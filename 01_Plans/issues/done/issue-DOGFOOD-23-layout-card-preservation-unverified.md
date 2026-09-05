# Issue: DOGFOOD-23 配置提案（suggest-layout）が全カードを保持することをE2Eで検証できない

- Type: Process / Verification gap（ドッグフーディング観察）
- Status: Done
- Source Issue: ドッグフーディング iteration 188（シナリオ118・百貨店 実装時の実走行観察）。`suggest-layout` は業務フローE2Eで3シナリオ（11/50/60系）が固定するが、全シナリオが `"transform"` + `"cards"` **キーの存在**だけを確認し、**配置提案が全カードを座標付きで保持しているか（カードを落とさないか）**を E2E で検証できないことを確認した。
- Priority: P2
- Owner: Maintainer
- Scope: `03_Implement/backend/scripts/verify_business_flow_e2e.sh`（シナリオ118）, `01_Plans/dogfood/business-flow-e2e-scenarios-2026-08-15.md`
- Related ADR/Spec: `00_Prompt/kj_technique.md` §3（島形成・空間配置）, `02_Architecture/api.md`（suggest-layout 契約・suggestedDoc.cards）, `01_Plans/dogfood/business-flow-e2e-scenarios-2026-08-15.md`（シナリオ11/50/60が layout を固定）
- Expected verification level: `e2e`

## 課題

業務フローE2E の `suggest-layout`（配置提案）は3シナリオ（シナリオ11・会議ファシリテーター、シナリオ50・小売EC等）が固定するが、全シナリオが `"transform"` と `"cards"` **キーの存在**だけを確認する:

```bash
case "$layout" in *'"transform"'*'"cards"'*) ... 
```

したがって:

- **配置提案が全カードを座標付きで保持しているか（カードを落とさないか）を E2E で一切検証できない**。
- バックエンドが配置中にカードを落とす（`suggestedDoc.cards` から一部が欠落する）回帰が起きても、業務フローE2E は全部 pass する。
- 配置（レイアウト）は島形成の前段として「全カードを失わずに空間へ置く」ことが核心（kj_technique.md §3）だが、その保全が未固定。

実機再現（iteration 188）:

```text
# suggest-layout の応答: {"suggestedDoc":{...,"cards":[{"id":"d1",...},{"id":"d2",...},{"id":"d3",...},{"id":"d4",...}], ...}}
# 既存シナリオは "transform"+"cards" キー存在のみを検証し、全カード保持を確認しない
```

### なぜ問題か

- **配置の保全（全カードの座標保持）が未検証**: 配置提案がカードを落とすと、その後の島形成・ナラティブの前提が崩れる。
- **検証深度の偏り**: 多用される操作（束ね89・ナラティブ84・島要約91）は深い検証が入ったが、layout（3回）はキー存在のみ。

## 三要素分析（ADR-0067）

| 次元 | 分析 | 他次元への制約 |
|------|------|---------------|
| **業務設計** | 定性分析者は**全カードを空間へ失わずに配置**する提案を得たい。配置は島形成の前段であり、カード欠落は分析の前提を壊す | 配置は **proposal 相当（read-only の提案）** のまま。カードの削除・統合は自動適用しない |
| **データ設計** | 配置応答の `suggestedDoc.cards` は全カード（座標付き）を含むため、**各カードIDが応答に存在する**ことを検証できる | 既存の `"transform"`+`"cards"` キー assert は、カードIDの存在チェックを追加しても成立（非後退） |
| **機能設計** | シナリオ118の配置チェックで **`suggestedDoc` かつ全カードID（d1〜d4）が応答に存在**することを assert する。API契約（`SuggestLayoutResponse`）は不変 | バックエンド実装・API契約は変更しない。モックは既に全カードを返す |

## 対応方針

- 実施すること:
  1. シナリオ118（百貨店）に **suggest-layout（配置提案）** を操作内容へ追加し、配置チェックで **`suggestedDoc` かつ全カードID（d1〜d4）が応答に存在**することを assert する（配置のカード保全を固定）。
- 実施しないこと:
  - suggest-layout の**バックエンド実装・API契約の変更**（モックは既に全カードを返す）。
  - 既存シナリオ（11/50/60系）のアサーションの変更（`"transform"`+`"cards"` キー assert・非後退）。

## 受入条件

- [x] シナリオ118の配置チェックが `suggestedDoc` かつ全カードID（d1〜d4）を assert（実走行で確認）。
- [x] 既存シナリオ（11/50/60系・layout）は非後退。
- [x] 業務フローE2E が **706/706 pass**（並行編集によるMGシナリオの干渉がない場合）。
- [x] `verify_dogfood_records.sh`・`docs_check.py` が pass。

## 検証計画

- `cd 03_Implement/backend && bash scripts/verify_business_flow_e2e.sh <PORT>` → 706/706（シナリオ118の DP ⑤配置提案が全カード保持）
- `bash 01_Plans/dogfood/verify_dogfood_records.sh` → 構造照合 pass
- `python 01_Plans/docs_check.py` → docs-check passed

## 補足

- 配置のカード保全（全カードIDの存在）は、モックが既に全カードを返すためモック変更は不要。本issueは**検証深度の向上**（配置提案の保全をE2Eで固定）。
- ドッグフーディング観察起点（2026-08-16・iteration 188）: 百貨店（`dep-i`・4カード島）で suggest-layout を実行し、応答に全カード（d1〜d4・座標付き）が含まれる一方、業務フローE2E が `transform`+`cards` キーのみを検証して全カード保持を確認しないことを特定した。


## 配置の整理（2026-09-05）

- 本Issueは、AI提案が根拠カードまたは入力カードを欠落させない preservation invariant を業務フローE2Eで固定し、製品API契約を変えずに `Done` となっていた。
- `DOGFOOD-22` と `DOGFOOD-23` は直接の実装依存は持たないが、CE4提案の grounding 保全と layout 提案の全カード保全という、提案結果の情報欠落を回帰から守る同型の完了記録として同時に正規配置へ移した。
- `LEGACY_DONE_AT_ROOT_BASELINE` は29から27へ縮小し、R18 identity manifestは不変の歴史境界として維持する。
- 旧rootパス引用は完全一致探索で検出し、現在の `done/` パスへ同時更新した。
