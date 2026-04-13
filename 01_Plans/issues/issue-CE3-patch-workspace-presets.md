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
- [x] T3: Patch差分プレビューUI実装（selected candidate の source/draft/edited + token delta 表示）。
- [x] T4: Playwright E2Eシナリオ追加（部分採用→ロールバック→preset再実行）。

## 4) 検証計画 / Validation plan

- 実行コマンド:
  - `npm --prefix 03_Implement/frontend run e2e -- --grep "Patch Workspace|Preset|rollback"`
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
- Phase 5 Proceed: 次タスクは document監査ログ統合（workspace local audit → document監査ログ連携）。

## 7) Stream C Phase Notes (2026-04-11)

- Phase 1 Read: CE3 issue / `PatchWorkspacePanel` / CE3 E2E spec を再読し、候補独立性の検証不足（単一候補のみ検証）を確認。
- Phase 2 Plan:
  - adopt/reject/hold の独立保持をUI可視化（candidate decision matrix）で明示。
  - rollbackは「直前候補のみ復旧、先行候補は維持」をE2Eで検証。
  - preset replay と audit transition 表示を既存導線のまま回帰確認。
- Phase 3 Execute:
  - `PatchWorkspacePanel` に候補ごとの decision/audit 表示を追加。
  - CE3 E2Eを multi-candidate 手順へ拡張（A採用→B却下→rollback）。
  - domain unit test に rollback独立性ケースを追加。
- Phase 4 Verify:
  - `npm --prefix 03_Implement/frontend run test -- src/domain/ce3_patch_workspace.test.ts src/ui/PatchWorkspacePanel.test.ts`
  - `npm --prefix 03_Implement/frontend run e2e -- --grep "CE3 patch workspace"`
- Phase 5 Proceed:
  - 未完了: workspace local audit を document監査ログへ昇格する統合（CE4/後続）。
  - SafeMode後退・share/export露出の追加はなし（UI導線未追加）。

## 8) Stream F Phase Notes (2026-04-11)

### Phase 1 Read（現行UI/状態機械/E2E前提）

- `PatchWorkspacePanel` の候補状態表示が `auditLog` の最新遷移を表示していることを確認。
- `ce3_patch_workspace.ts` の rollback は状態復旧のみで、rollback自体の監査遷移を残していないことを確認。
- `e2e/ce3_patch_workspace.spec.ts` は rollback後も監査遷移数を `2` のまま期待しており、rollback操作の可観測性を十分に担保していないことを確認。

### Phase 2 ADR明文化（Context / Decision / Consequences）

- Context:
  - CE3要件は「候補IDごとの状態遷移記録」を受入条件に含むが、rollback経路が監査上不可視。
  - rollback後のUIは最終状態だけを見せるため、通常遷移と復旧遷移の区別が困難。
- Decision:
  - `rollbackWorkspaceDecision` 実行時に、差分が発生した候補ごとに `reason=rollback` の監査遷移を追加する。
  - UIは候補ごとの最新遷移表示に `(rollback)` サフィックスを付与する。
  - E2Eは rollback 後の監査遷移表示/件数増加を必須確認に更新する。
- Consequences:
  - rollback操作の監査可能性が向上し、候補独立性検証時に復旧遷移を識別できる。
  - document永続データには影響せず、local state管理方針（Core/Consensus非改変）を維持できる。

### Phase 3 Plan（AC/DoD不足の補強提案）

- AC補強提案（固定）:
  - rollback操作時に対象候補の監査遷移へ `reason=rollback` が残ること。
  - CE3 E2Eで rollback 後の候補遷移表示（`(rollback)`）と監査遷移件数増加を確認すること。
- DoD補強提案（固定）:
  - domain unit + panel unit + CE3 e2e grep を通し、safeMode関連テストを追加で回して非後退を確認すること。

### Phase 4 Execute（workspace/preset/rollback直列実装）

- rollback時に差分候補を走査し、`WorkspaceAuditEntry` へ `reason: "rollback"` を追加。
- パネル表示で rollback遷移を `from→to (rollback)` として可視化。
- CE3 domain test / e2e test を更新し、rollback監査遷移の追加を期待値へ反映。

### Phase 5 Verify（unit + e2e + safeMode非後退）

- unit/e2e/safeMode関連の検証コマンドを実行（詳細ログは本Issueの更新コミットに追記）。
- 3回自己修復上限には未到達（1回でgreen）。

### Phase 6 Proceed（境界・未解決UI課題・次手）

- 変更境界:
  - `03_Implement/frontend/**`（CE3 domain/ui/e2e）
  - `04_Documentation/e2e_testing.md`（CE3節）
  - 本issue進捗記録のみ更新。
- 未解決UI課題:
  - rollback監査は現状local stateのみで、document監査ログ統合は未実装。
  - Preset削除/上書きなど運用UIは後続検討。
- 次手:
  - CE4で local監査遷移を document監査ログへ昇格し、export/import監査整合まで拡張する。

## 9) Stream C Phase Notes (2026-04-12)

- Phase 1 Read:
  - CE3 issue / `PatchWorkspacePanel` / `ce3_patch_workspace` / CE3 E2E spec を再読し、候補独立性・rollback監査表示・preset replay が Core/Consensus 非改変で閉じていることを再確認。
- Phase 2 Plan:
  - AC/DoD は維持し、Verify の再現性を補強するため CE3 節に Playwright 事前セットアップ手順を明示する。
  - Verify 失敗時は「browser install → deps install → 再実行」の順で最大3回まで自己修復する方針を固定。
- Phase 3 Execute:
  - `04_Documentation/e2e_testing.md` の CE3 セクションに Playwright `install/install-deps` の事前実行コマンドを追加。
- Phase 4 Verify:
  - unit: `npm --prefix 03_Implement/frontend run test -- src/domain/ce3_patch_workspace.test.ts src/ui/PatchWorkspacePanel.test.ts src/domain/view/presets.test.ts` を pass。
  - e2e 1回目: browser binary 不足で fail。
  - 修復1: `npm --prefix 03_Implement/frontend exec playwright install chromium` を実行。
  - e2e 2回目: `libatk-1.0.so.0` 不足で fail。
  - 修復2: `npm --prefix 03_Implement/frontend exec playwright install-deps chromium` を実行。
  - e2e 3回目: `npm --prefix 03_Implement/frontend run e2e -- --grep "CE3 patch workspace|Patch Workspace|Preset|rollback"` を pass。
- Phase 5 Proceed:
  - 未完了: local audit log を document 監査ログへ昇格する CE4 連携は未着手。
  - フェイルセーフ判定: 契約逸脱なし、未定義競合なし、自己修復2回で収束（3回上限未満）。

## 10) Stream D Phase Notes (2026-04-12)

### Phase 1 Read（現状UI/テスト再読）

- `PatchWorkspacePanel` / CE3 domain / CE3 E2E spec を再読し、候補独立操作・rollback監査表示・preset replay が local state + localStorage で完結することを確認。
- 受入条件「Workspaceに最低3候補を並列表示可能」に対して、既存E2E fixture が2候補のみ検証である点をギャップとして特定。

### Phase 2 Plan（CDC明文化 + AC補完）

- Context:
  - CE3要件は「最低3候補の並列表示可能性」を求めるが、E2Eが2候補固定のため回帰検知が弱い。
- Decision:
  - CE3 E2E fixture に第3候補（gamma）を追加し、`ce3-candidate-count` と selector option 件数の両方で3候補を検証する。
  - A採用/B却下後に第3候補が `hold` 維持であることを確認し、候補独立性を補強する。
  - `04_Documentation/e2e_testing.md` の CE3観点に「最低3候補同時表示」確認を追記する。
- Consequences:
  - CE3受入条件との整合性が上がり、候補数退行（2候補以下への後退）をE2Eで検知できる。
  - Core/Consensus 直接編集は発生せず、SafeMode 境界への影響もない。

### Phase 3 Execute（workspace/preset/rollback）

- `03_Implement/frontend/e2e/ce3_patch_workspace.spec.ts`
  - suggest-merges fixture を3候補化（alpha/beta/gamma）。
  - test document に `c5` を追加。
  - 候補件数期待値を `(3)` / option `3` 件へ更新。
  - A採用/B却下後に第3候補が `hold` 維持することを追加検証。
- `04_Documentation/e2e_testing.md`
  - CE3必須観点へ「最低3候補同時表示」チェックを追記。

### Phase 4 Verify（unit/e2e/lint、失敗時3回まで修復）

- frontend unit（ce3 domain/ui/view preset）を実行し pass。
- CE3 e2e grep 実行し pass（自己修復 0 回）。

### Phase 5 Proceed（未完了課題を次手へ）

- 未完了: local audit log の document 監査ログ統合（CE4連携）は継続課題。
- 停止条件確認:
  - SafeMode後退なし。
  - 契約逸脱なし（Core/Consensus 非改変）。
  - 未定義競合なし。

## 11) Stream D Follow-up Notes (2026-04-12)

### Phase 1 Read（差分再同期）

- `ce3_patch_workspace.test.ts` / `PatchWorkspacePanel.test.ts` / `ce3_patch_workspace.spec.ts` を再読し、3候補要件はE2Eで担保済みだが unit 側の候補独立性検証が2候補中心であることを確認。

### Phase 2 Plan（AC/DoD補強提案）

- AC補強提案:
  - domain unitで「3候補時に rollback が最新候補のみへ作用し、未操作候補は hold 維持」を固定化する。
- DoD補強提案:
  - Panel unitで候補件数表示 `(3)` の退行を検知できる最小アサーションを追加する。

### Phase 3 Execute（Frontend tests only）

- `03_Implement/frontend/src/domain/ce3_patch_workspace.test.ts`
  - 3候補（alpha/beta/gamma）シナリオを追加し、A採用→B却下→rollback後の gamma hold 維持と rollback監査対象の限定（betaのみ）を検証。
- `03_Implement/frontend/src/ui/PatchWorkspacePanel.test.ts`
  - render fixture を3候補化し、candidate count `(3)` 表示の回帰検知を追加。

### Phase 4 Verify（test/lint）

- `npm --prefix 03_Implement/frontend run test -- src/domain/ce3_patch_workspace.test.ts src/ui/PatchWorkspacePanel.test.ts` を実行して pass。
- `npm --prefix 03_Implement/frontend run lint` を実行して pass。

### Phase 5 Proceed（未達/既知制約）

- 未達なし（本スコープ内AC/DoD補強は完了）。
- 既知制約:
  - local audit log の document監査ログ統合（CE4連携）は未着手で継続課題。

## 12) Stream D Verification Closure Notes (2026-04-12)

### Phase 1 Read（対象ファイル再読）

- `issue-CE3-patch-workspace-presets.md` / `ce3_patch_workspace.ts` / `PatchWorkspacePanel.tsx` / `ce3_patch_workspace.spec.ts` / `04_Documentation/e2e_testing.md` を再読し、CE3要件（workspace/preset/rollback）が local state + localStorage 境界で完結していることを再確認。
- 受入条件のうち「3候補並列」「rollback監査遷移」「preset正規化再現」を検証対象として再固定。

### Phase 2 ADR明文化（Context / Decision / Consequences）

- Context:
  - CE3実装自体は揃っているが、環境差分（Playwright browser/deps不足）で Verify が失敗しうる。
- Decision:
  - Verify は `unit -> e2e` の順で実行し、失敗時は `playwright install chromium` / `playwright install-deps chromium` の順で最大3回まで自己修復する。
- Consequences:
  - CE3の機能退行と実行環境欠落を切り分け可能になり、3回上限フェイルセーフを維持したまま検証完了可否を判断できる。

### Phase 3 Plan（AC/DoD不足確認）

- AC追加なし（既存ACでCE3検証可能）。
- DoD運用補強:
  - unit（domain/ui/presets）pass
  - CE3 e2e grep pass
  - 修復回数が3回未満で収束

### Phase 4 Execute（workspace/preset/rollback）

- 実装変更は不要と判断（既存CE3実装を保持）。
- Verify対象のみ実行。

### Phase 5 Verify（unit/e2e + 失敗時修復）

- unit: 1回で pass。
- e2e: 1回目 browser binary不足で fail → 修復1（install chromium）。
- e2e: 2回目 OS library不足で fail → 修復2（install-deps chromium）。
- e2e: 3回目 pass。
- フェイルセーフ判定: 自己修復2回で収束（上限3回未満）。

### Phase 6 Proceed

- CE3の実装検証は完了（workspace/preset/rollback のACを再確認）。
- 継続課題（範囲外）: local audit log の document監査ログ統合（CE4連携）。

## 13) Stream E execution record (2026-04-13)

### Phase 1 Read

- CE3要件・CE3 E2E観点・DOC-OPS-05関連Issueを再読し、今回の変更範囲を `03_Implement/frontend/`（verify実行）と docs/issue 更新に限定。

### Phase 2 Plan

- Verifyは `unit -> e2e` で実行。
- e2e失敗時は `playwright install chromium` → `playwright install-deps chromium` → e2e再実行の順で最大3回自己修復。
- Core/Consensus 非改変、SafeMode境界非後退を維持。

### Phase 3 Execute

- CE3 Verify を実行し、Playwright依存不足による失敗を2段階で自己修復。
- CE3 E2E手順へ自己修復順序を `04_Documentation/e2e_testing.md` に明記。

### Phase 4 Verify

- `npm --prefix 03_Implement/frontend run test -- src/domain/ce3_patch_workspace.test.ts src/ui/PatchWorkspacePanel.test.ts src/domain/view/presets.test.ts` → pass
- 1回目 `npm --prefix 03_Implement/frontend run e2e -- --grep "CE3 patch workspace|Patch Workspace|Preset|rollback"` → fail（browser binary不足）
- 修復1 `npm --prefix 03_Implement/frontend exec playwright install chromium` → pass
- 2回目 e2e → fail（`libatk-1.0.so.0` 不足）
- 修復2 `npm --prefix 03_Implement/frontend exec playwright install-deps chromium` → pass
- 3回目 e2e → pass

### Phase 5 Proceed

- 自己修復2回で収束（上限3回未満）。
- 未完了の後続は CE4（local監査ログの document監査ログ統合）のまま据え置き。
