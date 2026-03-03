# Issue Memo: FB-RM-MID-03 merge decision audit export

- Type: Feature
- Status: Done
- Source Issue: N/A (GitHub Issues are not used in current operations)
- Priority: P2
- Owner: TBD
- Scope: `03_Implement/frontend/src/domain/`, `03_Implement/frontend/src/export/`, `04_Documentation/operations.md`, `01_Plans/adr/ADR-0007-future-backlog.md`
- Related Backlog: `FB-RM-MID-03`, `FB-P2B-03..04`
- Related ADR/Spec: `01_Plans/adr/ADR-0001-value-to-requirements.md`, `01_Plans/adr/ADR-0007-future-backlog.md`, `01_Plans/adr/ADR-0019-e2e-verification-policy-and-compose-runbook.md`
- Expected verification level: `unit`

## 1) 課題 / Problem statement

`mergeSuggestionDecisions` は document に保持されるが、監査向けに独立して抽出する export がなかった。
そのため representative と source の追跡を外部監査フローへ連携しづらい。

## 2) 提案する解決策 / Proposed solution

- merge decision log から監査用途の最小JSONを生成する純粋関数を追加。
- bundle export に `merge_decision_audit.json` を同梱。
- 出力順序・カードID順を安定化して決定論を担保。
- 非目標: merge確定ロジック自体の変更、backend API仕様の変更。

## 3) 受入条件 / Acceptance criteria

- [x] bundle export に `merge_decision_audit.json` が含まれる。
- [x] 監査JSONが `decisionId/groupId/decisionType/actorType/decidedAt/representativeCardId/sourceCardIds` を含む。
- [x] 同一入力で同一監査JSONが生成される（決定論）。
- [x] MID-01/MID-02で追加した decision log の保存仕様を壊さない。

## 4) 実装タスク分解 / Task breakdown

- [x] T1 `merge_decision_audit.ts` を追加。
- [x] T2 `bundle_export.ts` に監査JSON出力を追加。
- [x] T3 `merge_decision_audit.test.ts` を追加。
- [x] T4 `bundle_export.test.ts` を拡張。
- [x] T5 `ADR-0007` / `operations.md` に反映。

## 5) 検証計画 / Validation plan

- 実行コマンド:
  - `npm run test -- src/domain/merge_decision_audit.test.ts src/export/bundle_export.test.ts`
  - `npm run test -- src/domain/merge_suggestion_decisions.test.ts src/domain/validate_doc.test.ts`
  - `npm run typecheck`
- 期待結果:
  - 監査JSONの構造・順序・代表/起源追跡がユニットテストで固定される。
  - 既存decision保存・検証テストが通過する。

## 6) Progress log

- 2026-02-28: テスト先行で `merge_decision_audit` の期待仕様（代表/起源追跡・時系列順）を固定。
- 2026-02-28: bundle export に `merge_decision_audit.json` を追加。
- 2026-02-28: 関連unit testと typecheck を実行し、回帰なしを確認。
