# Issue: DOGFOOD-22 CE4提案（propose-island-summary）の内容・接地が業務フローE2Eで未検証

- Type: Process / Verification gap（ドッグフーディング観察）
- Status: Done
- Source Issue: ドッグフーディング iteration 187（シナリオ117・ホームセンター 実装時の実走行観察）。`proposals/island-summary`（CE4提案連鎖）は業務フローE2Eで**わずか1回（scenario 9）**しか使われておらず、そのアサーションは `"status":"proposed"` の**キー存在のみ**。**提案内容（`diff.after` の要約・`diff.groundingIds` の接地）が E2E で一切検証されない**ことを確認した。
- Priority: P2
- Owner: Maintainer
- Scope: `03_Implement/backend/scripts/verify_business_flow_e2e.sh`（シナリオ117）, `01_Plans/dogfood/business-flow-e2e-scenarios-2026-08-15.md`
- Related ADR/Spec: `00_Prompt/ai_cognitive_externalization_requirements.md`（CE4・proposal 連鎖）, `02_Architecture/api.md`（proposals/island-summary 契約・diff.groundingIds）, `01_Plans/issues/issue-DOGFOOD-13-island-summary-grounding-capped-at-three-cards.md`（接地の検証深度）, `01_Plans/dogfood/business-flow-e2e-scenarios-2026-08-15.md`（scenario 9 が CE4 を固定）
- Expected verification level: `e2e`

## 課題

CE4提案連鎖（`POST /ai/proposals/island-summary`）は、AIの島要約を**proposal（status=proposed・reviewState=unreviewed）**として提示し、人間の採否（adopt/hold）を経て初めて適用される（proposal-only）。ルートは `suggest_island_summary` を内部呼び出しし、`diff.groundingIds` に**島の全メンバーカード**（接地）を載せる。

業務フローE2E の CE4 固定は **scenario 9 のみ**であり、そのアサーションは `"status":"proposed"` のキー存在だけを確認する:

```bash
case "$p9_propose" in *'"status":"proposed"'*) ... 
```

したがって:

- **CE4提案の内容（`diff.after` の要約・`diff.groundingIds` の接地）が E2E で一切検証されない**。
- バックエンドが提案の接地を落とす（`groundingIds` を空にする）回帰が起きても、業務フローE2E は全部 pass する。
- CE4提案は「AIの提案根拠（接地）を人間が確認して採否する」仕組み（CE4・proposal-only）であり、**接地は人間レビューの根拠**。その保全が未固定。

実機再現（iteration 187）:

```text
# propose-island-summary の応答: {"status":"proposed", ..., "diff":{..., "after":"...", "groundingIds":["h1","h2","h3","h4"], ...}}
# scenario 9 は status のみ検証し、groundingIds の保全を確認しない
```

### なぜ問題か

- **CE4提案の根拠（接地）が未検証**: 人間レビュアーが提案を判断する際の根拠（どのカードに基づく要約か）が、回帰で落ちても検知できない。
- **カバーが極端に薄い**: proposals/island-summary は業務フローE2Eで1回のみ（scenario 9）。提案内容の検証が皆無。

## 三要素分析（ADR-0067）

| 次元 | 分析 | 他次元への制約 |
|------|------|---------------|
| **業務設計** | 定性分析者は島の要約提案を**根拠（接地カード）付き**で受け取り、人間が確認・採否したい。接地がなければ提案の根拠を判断できない | 提案は **proposal-only**（status=proposed・reviewState=unreviewed・自動適用なし）のまま |
| **データ設計** | 提案の `diff.groundingIds` は内部 `suggest_island_summary` の接地（DOGFOOD-13 で全接地）を引き継ぐため、**島の全メンバーカード**が正 | 既存シナリオ9の `"status":"proposed"` assert は、接地 assert を追加しても成立（非後退） |
| **機能設計** | シナリオ117の CE4提案チェックで **`diff.groundingIds` が島の全カード（h1〜h4）** であることを assert する。API契約（`ProposalEnvelope`）は不変 | バックエンド実装・API契約は変更しない。モック側は `suggest_island_summary` 経由で既に全接地を返す |

## 対応方針

- 実施すること:
  1. シナリオ117（ホームセンター）に **propose-island-summary（CE4提案連鎖）** を操作内容へ追加し、CE4提案チェックで **proposal-only（`status:proposed`）かつ `diff.groundingIds` が島の全カード（h1〜h4）** であることを assert する（CE4提案の根拠の保全を固定）。
- 実施しないこと:
  - propose-island-summary の**バックエンド実装・API契約の変更**（モック側は既に全接地を返す）。
  - 既存シナリオ9のアサーションの変更（`"status":"proposed"` assert・非後退）。

## 受入条件

- [x] シナリオ117のCE4提案チェックが `status:proposed` かつ `groundingIds:["h1","h2","h3","h4"]` を assert（実走行で確認）。
- [x] 既存シナリオ9（人事・CE4提案連鎖）は非後退。
- [x] 業務フローE2E が **699/699 pass**（並行編集によるMGシナリオの干渉がない場合）。
- [x] `verify_dogfood_records.sh`・`docs_check.py` が pass。

## 検証計画

- `cd 03_Implement/backend && bash scripts/verify_business_flow_e2e.sh <PORT>` → 699/699（シナリオ117の HC ⑤CE4提案が接地を保持）
- `bash 01_Plans/dogfood/verify_dogfood_records.sh` → 構造照合 pass
- `python 01_Plans/docs_check.py` → docs-check passed

## 補足

- CE4提案の接地は内部 `suggest_island_summary`（DOGFOOD-13 で全接地）を引き継ぐため、モック側の変更は不要。本issueは**検証深度の向上**（CE4提案の根拠をE2Eで固定）。
- ドッグフーディング観察起点（2026-08-16・iteration 187）: ホームセンター（`hc-i`・4カード島）で propose-island-summary を実行し、応答に `diff.groundingIds:["h1","h2","h3","h4"]` が含まれる一方、業務フローE2E が status のみを検証して接地を確認しないことを特定した。


## 配置の整理（2026-09-05）

- 本Issueは、AI提案が根拠カードまたは入力カードを欠落させない preservation invariant を業務フローE2Eで固定し、製品API契約を変えずに `Done` となっていた。
- `DOGFOOD-22` と `DOGFOOD-23` は直接の実装依存は持たないが、CE4提案の grounding 保全と layout 提案の全カード保全という、提案結果の情報欠落を回帰から守る同型の完了記録として同時に正規配置へ移した。
- `LEGACY_DONE_AT_ROOT_BASELINE` は29から27へ縮小し、R18 identity manifestは不変の歴史境界として維持する。
- 旧rootパス引用は完全一致探索で検出し、現在の `done/` パスへ同時更新した。
