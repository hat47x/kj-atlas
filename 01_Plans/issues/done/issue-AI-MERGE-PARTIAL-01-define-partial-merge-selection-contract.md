# Issue: AI-MERGE-PARTIAL-01 `partial` の部分採用契約を定める

> 実装履歴はGit/PRを正本とし、このメモは完了境界と検証結果だけを残す。

- Type: Feature / Domain Integrity
- Status: Done
- Source Issue: `AI-MERGE-SEMANTICS-01`
- Priority: P1
- Owner: Maintainer
- Scope: `03_Implement/frontend/src/ui/MergeSuggestionsPanel.tsx`, `03_Implement/frontend/src/domain/merge_suggestion_decisions.ts`, `03_Implement/frontend/src/domain/merge_suggestion_apply.ts`, `03_Implement/frontend/src/domain/merge/decision_audit_events.ts`, `03_Implement/frontend/e2e/merge_suggestion_partial_persistence.spec.ts`, `02_Architecture/api.md`
- Related ADR/Spec: `AI-MERGE-SEMANTICS-01`, `AI-MERGE-APPLY-01`, `ADR-0068`, `ADR-0069`
- Expected verification level: `e2e`

## 完了した契約

`partial` は、提案されたsourceカードの**真部分集合を人間が明示して採用する判断**とする。

- 2枚以上、かつ候補全件未満だけを許す。全件採用は `accept` とする。
- 新規 `partial` は `selectedCardIds` を必須とし、候補集合外のIDや重複を許さない。
- 旧データで選択集合が欠落・全件同一など曖昧な場合は、推測せず実適用をfail-closedにする。
- 判断ログと監査に全候補 `cardIds` と実採用 `selectedCardIds` を分けて残す。
- 実適用は選択されたsourceだけをmergeし、非選択カードを変更しない。
- hold、既merge/canonicalization、`negate` / `contradicts`、異なる既知 `claimType` は適用直前にも再検査する。
- 判断・実適用・保存は別操作のまま維持する。再読込後も記録済みの選択集合をUIへ復元し、人間が確認してからApplyできる。
- 自由記述 `residuals` は追加せず、残差の一次記録は削除されず残るsourceカードそのものとする。

## 検証

- domain / audit / UI / i18n / API clientの回帰テスト
- frontend typecheck
- Playwrightで、3枚候補から2枚だけを選択 → 判断を保存 → 再読込 → 選択集合を再表示 → 明示適用 → 保存 → 再読込まで確認
- 非選択カードが本文・系譜とも変更されないことを確認
- `docs_check.py`、active issue validator、triage、diff check

## 完了境界

人間が明示した真部分集合が判断・監査・実merge・保存／再読込まで同じ集合として保たれ、後から適用する場合もその集合をUIで確認でき、非選択カードへ副作用を与えないことをもって完了とする。merge方式の追跡は `AI-MERGE-METHOD-TRACE-01` へ分離する。
