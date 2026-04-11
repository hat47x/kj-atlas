# Issue Draft: CE3 Patch Workspace / Query Presets

- Type: Feature request
- Status: In Progress (CE3 workspace panel + preset replay + rollback導線)
- Source Issue: N/A
- Priority: P2
- Owner: Frontend Team
- Scope: `03_Implement/frontend/`, `04_Documentation/e2e_testing.md`
- Related Backlog: `CE-3`
- Related ADR/Spec: `ADR-0028`
- Expected verification level: `e2e`

## Requirement meta I/F（共通キー）
- RequirementID: `CE3-PATCH-WORKSPACE`
- RequirementStatement: 候補比較・部分採用・保留・廃棄を可逆に実行できる。
- PriorityClass: Must
- AcceptanceScenario: 前提=CE2完了 / 操作=複数候補比較 / 期待結果=rollback可能 / 除外=Core/Consensus直接編集
- GoNoGoGate: Required
- SecurityGateImpact: SafeMode
- VerificationLevel: e2e
- DecisionStatus: Fixed
- DecisionQueueRef: `UNC-VSC-CE-01-01`

## 1) 機能要件（具体）

- Workspaceに最低3候補を並列表示可能。
- 候補ごとに `adopt/reject/hold` を独立操作できる。
- Query Preset（name + scope + depth + filters）を保存/再実行できる。

## 2) 受入条件 / Acceptance criteria

- [x] 部分採用後に1クリックでロールバック可能（`PatchWorkspacePanel` の last snapshot 復旧導線）。
- [x] Preset再実行で同一Query（正規化後）が再現される（scope/depth/filters 正規化JSONを表示）。
- [x] Perspective切替でdocument永続データ差分が発生しない（workspace/preset状態はlocal state + localStorage管理）。
- [x] 監査ログに候補IDごとの状態遷移が残る（UI local stateで保持。document監査ログ統合は次段）。
- [x] safeMode ON中に危険操作（share/export auto）が露出しない（本変更は share/export 操作を追加しない）。

## 3) 実装タスク分解 / Task breakdown

- [x] T1: Workspace state machine（hold/adopt/reject + rollback）実装。
- [x] T2: Preset CRUD実装（local store + run current / run saved）。
- [ ] T3: Patch差分プレビューUI実装（未着手）。
- [x] T4: Playwright E2Eシナリオ追加（部分採用→ロールバック→preset再実行）。

## 4) 検証計画 / Validation plan

- 実行コマンド:
  - `npm --prefix 03_Implement/frontend run test:e2e -- --grep "Patch Workspace|Preset|rollback"`
- 期待結果:
  - 候補比較・可逆操作・再実行性をE2Eで確認。

## 5) リスクとロールバック / Risks & rollback

- 失敗モード: Workspace状態機械の破綻で誤適用。
- ロールバック: 状態遷移をread-onlyモードへ切替し、applyを一時停止。

## 6) Stream E Phase Notes (2026-04-11)

- Phase 1 Read: 現行のCE3 Workspace UI状態機械とpreset正規化条件を確認。
- Phase 2 Plan: AC/DoDを補強（監査遷移ログの最低導入をUI local stateで確定、Core/Consensus非改変を維持）。
- Phase 3 Execute: hold/adopt/reject + rollback stack + preset replay + query正規化再現を実装。
- Phase 4 Verify: unit/lint/e2eを実施（e2eは環境制約があれば理由を記録）。
- Phase 5 Proceed: 次タスクは Patch差分プレビューUI と document監査ログ統合。
