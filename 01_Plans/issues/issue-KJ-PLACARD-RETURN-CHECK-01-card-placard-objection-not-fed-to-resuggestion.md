# Issue: KJ-PLACARD-RETURN-CHECK-01 表札の戻し検査（カード→表札の異議）が再提案に反映されない

- Type: Product Invariant / AI Integration
- Status: In Progress
- Source Issue: `01_Plans/direction-review-2026-08-13.md` 優先3-3
- Priority: P2
- Owner: Maintainer
- Scope: `03_Implement/backend/src/kj_atlas_api/routes/ai.py`（`_build_island_summary_prompt`）, `03_Implement/frontend/src/ui/SidePanel.tsx`, `src/i18n/locales/*.json`
- Related ADR/Spec: `00_Prompt/kj_technique.md`（§3 表札検査・戻し検査）, `00_Prompt/ai_kj_execution_procedures.md`（§3 表札検査を自己実行）, `01_Plans/adr/ADR-0067-three-element-constraint-design-method.md`
- Expected verification level: `integration`

## 課題

方法論の表札検査は「書いた表札を島の各カードへ戻し、『あなたが言いたかったのはこれか』と照合する。1枚でも『ちがう』が返ってくるカードがあれば書き直す」（`kj_technique.md` §3）。

> `00_Prompt/ai_kj_execution_procedures.md:95-96`
> 2. 書いた表札を島の各カードへ戻し、「あなたが言いたかったのはこれか」と照合する

カードの `critiqueTags` には `not_the_same` / `feels_off` が既に存在し、UI のカード critique-tag チェックボックスで記録できる（録記は可能）。しかし**島要約の再提案プロンプトが、この異議を一切考慮していなかった**。方向性レビュー優先3-3「表札の戻し検査 — カード→表札の異議記録（既存の CRITIQUE_TAGS の not_the_same/feels_off を再利用可能）」のうち、録記は既存・フィードバックが欠落。

## 対応方針

- 実施すること（D-a・既存機構の再利用）:
  1. **prompt フィードバック**: `_build_island_summary_prompt` が、メンバーカードの `critiqueTags` に `not_the_same` / `feels_off` を持つカードを検出し、「前の表札に異議を唱えたカード」として明示。再提案は各異議に応える（または真の代弁でない）ことを指示。
  2. **UI の意図明確化**: カード critique-tag セクションに「`not_the_same` / `feels_off` は表札への異議（戻し検査）として再提案へ反映される」というヒントを追加。
  3. **テスト**: prompt が異議カードを含む場合にその旨を出力することを固定。
- 実施しないこと:
  1. 新しいデータモデルの追加（`critiqueTags` を再利用）。
  2. 戻し検査の自動トリガー（異議記録は人間の明示操作のみ。表札提案後の自動再提案は将来判断）。

## 受入条件

- [x] AC-1: メンバーカードが `not_the_same` / `feels_off` を持つとき、島要約 prompt が異議カードを明示する。
- [x] AC-2: 異議が無いとき、prompt に異議ブロックを出さない（後方互換）。
- [x] AC-3: UI に戻し検査の意図を示すヒントが表示される。

## 検証

- `python -m pytest tests/test_ai_prompt.py -q`
- `cd 03_Implement/frontend && npm run typecheck && npm run test -- src/i18n/translate.test.ts`
- `python 01_Plans/docs_check.py`

## 対応記録（2026-08-14）

D-a を実装した（既存 `critiqueTags` の再利用）。

- `_build_island_summary_prompt`: メンバーカードの `critiqueTags` に `not_the_same` / `feels_off` を含むカードを検出し、「OBJECTED to the previous placard (戻し検査)」として出力し、再提案が各異議に応えることを指示。
- `SidePanel.tsx`: カード critique-tag セクションに「表札への異議（戻し検査）として記録され、島要約の再提案に反映される」ヒントを追加（`side_panel.critique.placard_return_check_hint`）。
- テスト: `test_ai_prompt.py` に2テスト追加（異議カードの明示・無異議時の省略）。全 AC 完了。frontend 1446 tests・backend 43 tests・docs-check 通過。

これで方向性レビュー**優先3（検査の実装）の4項目すべて**（A/B照合・実行時プロンプト整合・voids・表札の戻し検査）が完了した。
