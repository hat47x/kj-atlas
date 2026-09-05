# Issue: DOGFOOD-13 モックの島要約接地が3カードで打ち切られ、4カード以上の島をE2Eで固定できない

- Type: Process / Verification gap（ドッグフーディング観察）
- Status: Done
- Source Issue: ドッグフーディング iteration 178（シナリオ108・自治体/廃棄物処理 実装時の実走行観察）。4カード島 `wm-i` の島要約を実行すると `groundingIds` が `["w1","w2","w3"]` に**打ち切られ**、`w4` が接地されないことを再現確認した。
- Priority: P2
- Owner: Maintainer
- Scope: `03_Implement/deploy/tools/mock_local_llm.py`, `03_Implement/backend/scripts/verify_business_flow_e2e.sh`（シナリオ108）, `01_Plans/dogfood/business-flow-e2e-scenarios-2026-08-15.md`
- Related ADR/Spec: `01_Plans/issues/done/issue-DOGFOOD-12-check-narrative-positive-path-hardcodes-island-i1.md`（同じくモックの暗黙制約）, `02_Architecture/api.md`（suggest-island-summary 契約・groundingIds）, `00_Prompt/kj_technique.md` §3（表札作成・接地）
- Expected verification level: `e2e`

## 課題

`mock_local_llm.py` の `suggest_island_summary` は、接地（`groundingIds`）を**最初の3カード**に打ち切っている:

```python
grounding = member_ids[:3] if member_ids else []
```

島要約のプロンプトは**対象島のメンバーカードのみ**を含む（`routes/ai.py` の `_build_island_summary_prompt` が `member_cards` のみを `card_lines` にする）。したがって:

- **4カード以上の島**では、モックが `["w1","w2","w3"]` を返し、`w4` が接地されない。
- 業務フローE2E の島要約チェックは `"groundingIds":["..."]` を厳密に照合するため、**4カード以上の島を full grounding で固定できない**。
- 実地の KJ 分析では1島に4〜8枚のカードが普通であり、これは**ドキュメント化されていない暗黙の3カード制約**。3カード以下で揃えた既存シナリオ（1〜107）はこの制約を回避していたにすぎない。

実機再現（iteration 178）:

```text
# 4カード島 wm-i = [w1,w2,w3,w4] で島要約 → groundingIds:["w1","w2","w3"]（w4欠落）
```

### なぜ問題か

- **E2E の接地検証がデータ規模に依存（DOGFOOD-11/12 と同じ盲点）**: 接地セマンティクス（「島の全メンバーに接地して表札を書く」）を実物大の島（4枚以上）で固定できない。
- **シナリオ追加の摩擦**: 業態拡大イテレーションで現実的なカード枚数の島を使うと、島要約の full grounding アサーションが失敗する。この制約はどこにも書かれていない。

## 三要素分析（ADR-0067）

| 次元 | 分析 | 他次元への制約 |
|------|------|---------------|
| **業務設計** | 定性分析者は1島に複数枚（実地では4枚以上）のカードを束ね、表札を**島の全メンバーに接地して**書く。接地は部分集合でなく**全メンバー**が正しい | 島要約は **proposal 相当（read-only の下書き）** のまま。表札の自動確定・適用はしない |
| **データ設計** | 島要約プロンプトは対象島のメンバーカードのみを含むため、モックは**全メンバー**を `groundingIds` にできる（他の島のカードが混入しない） | 既存の3カード島（シナリオ1〜107）は全メンバー接地でも同じ応答になるため非後退 |
| **機能設計** | `suggest_island_summary` の `member_ids[:3]` を `member_ids`（全接地）へ変更。API契約（`SuggestIslandSummaryResponse`）は不変 | 既存の島要約アサーション（`groundingIds:[...3枚...]`）は3カード島で同一応答のため非後退 |

## 対応方針

- 実施すること:
  1. `mock_local_llm.py` の `suggest_island_summary` で**全メンバーカードを接地**する（`member_ids[:3]` → `member_ids`）。
  2. シナリオ108（自治体・廃棄物処理）の**4カード島**（`wm-i`）で島要約の full grounding（`["w1","w2","w3","w4"]`）を固定し、実物大の島で接地セマンティクスを業務フローE2E で検証する。
  3. **打ち切り接地を固定していた既存2シナリオを是正**する — WS（新規事業WS・島`ws-i`4カード）と SP（スポーツチーム運営・ファン声分析・島`sp-i`4カード）の島要約アサーションが `["…3枚"]` を固定していたため、full grounding（4枚）へ更新する（モックの3枚打ち切りに合わせていた誤った固定の是正）。
- 実施しないこと:
  - suggest-island-summary の**バックエンド実装・API契約の変更**。
  - 3カード以下の島（既存シナリオの大多数）の島要約アサーションの変更（full grounding でも同一応答のため不要）。

## 受入条件

- [x] 4カード島で `groundingIds` が `["w1","w2","w3","w4"]`（全接地）を返す（実走行で確認）。
- [x] 3カード島（既存シナリオの大多数）は `groundingIds` が従来どおり全メンバー（=3枚）を返す（非後退）。
- [x] 打ち切り接地を固定していた既存2シナリオ（WS・SP・4カード島）を full grounding アサーションへ是正し、業務フローE2E 全体が **636/636 pass**。
- [x] シナリオ108の島要約チェックが `"groundingIds":["w1","w2","w3","w4"]` を assert。
- [x] `verify_dogfood_records.sh`・`docs_check.py` が pass。

## 検証計画

- `cd 03_Implement/backend && bash scripts/verify_business_flow_e2e.sh <PORT>` → 636/636（シナリオ108の WM ②島要約が4カード全接地）
- `bash 01_Plans/dogfood/verify_dogfood_records.sh` → 構造照合 pass
- `python 01_Plans/docs_check.py` → docs-check passed

## 補足

- モックの接地は「プロンプトに含まれるメンバーカード全枚」を返すだけなので、実LLM利用時の接地品質とは独立（本issueは検証ハーネスの能力向上）。
- ドッグフーディング観察起点（2026-08-16・iteration 178）: 廃棄物処理（4カード島 `wm-i`）の島要約を実行し、`w4` が接地から欠落することを再現。島要約の full grounding を実物大の島で固定できず、モックの3カード打ち切りが原因と特定した。


## 配置の整理（2026-09-05）

- 本Issueは、`suggest-island-summary` のモック接地が先頭3カードへ暗黙に打ち切られていた制約を除去し、4カード以上の島でも全メンバー接地をE2Eで固定できるようにした verification harness 改善として `Done` となっていた。
- 後続の `DOGFOOD-33` 以降は複数候補・壁打ち・履歴永続化という機能契約進化を扱うため、本Issueはその系列へ混ぜず、接地検証ハーネスの完了記録として単独で正規配置へ移した。
- `LEGACY_DONE_AT_ROOT_BASELINE` は18から17へ縮小し、R18 identity manifestは不変の歴史境界として維持する。
- 旧rootパス引用は完全一致探索で検出し、現在の `done/` パスへ同時更新した。
