# Issue Draft: CE4 API/CLI/監査統合（Stream B / CE契約群 / contract-only planning）

- Type: Feature request
- Status: Open
- Priority: P2
- Owner: Stream B（CE契約群）
- Scope: `01_Plans/issues/`（docs-only / contract-only / mock-first）
- Editable: `issue-CE4-api-cli-audit-integration.md` のみ
- Related Backlog: `CE-4`
- Related ADR/Spec: `ADR-0028`, `ADR-0008`, `02_Architecture/schemas.md`
- Verification: `docs-check`

## Lane guard（独立性・停止条件）
- CE4は API/CLI/監査の計画I/F固定のみ（実装禁止）。
- CE1/CE0/CE2契約は参照専用（CE4で再定義しない）。
- 検証失敗時の自己修復は最大3回、4回目相当は停止。
- 強制ワークフローは `Phase 1 Read → Phase 2 I/F Mock Freeze → Phase 3 ADR CDC → Phase 4 Plan→Execute→Verify → Phase 5 Proceed`。

## Phase 1 Read（全対象Read: Status / Scope / Related ADR確認）
### 同値性I/F
- 判定軸は `equivalenceKey + bundleHash`（AND）に固定。

### 監査I/F
- 必須4点: `query / bundle / proposal / apply`
- `dryRun=true -> sideEffect=none` 固定。
- `sourceBundleHash=mock:<hash>` を許容（依存切断）。

### No-Go / safeMode境界
- 監査欠損の成功扱い禁止（fail-closed）。
- `CE0-SAFEMODE-IF` を参照し、CE4側で緩和しない。

## Phase 2 I/F Mock Freeze（ContextQuery / ContextBundle / Review 境界をI/Fのみ固定）
- CE1参照境界: `bundleHash/sourceBundleHash/queryCanonicalHash` 語彙のみ依存。
- CE2参照境界: lifecycle（`proposed/accepted/rejected/held`）と `proposal/apply` 監査語彙のみ依存。
- CE4内で hash語彙・状態語彙を再定義しない。
- `mock:<hash>` と本番hashで監査フローを分岐させない。

## Phase 3 ADR CDC（方針差分時のみ Context / Decision / Consequences を記録し承認待ち）
- **Context**: API/CLI/GUI間の同値判定・監査語彙衝突有無。
- **Decision**: `equivalenceKey + bundleHash` 固定、監査4点必須、fail-closed維持。
- **Consequences**: CE1/CE2参照境界の一意化、監査欠損時の停止一貫性を確保。
- **Approval**: 差分発生時の反映状態は `held`。

## Phase 4 Plan→Execute→Verify（AC/DoD補完 + docs-check自己検証）
### Plan
- 公開I/Fを `context-query/context-bundle/proposal-diff/apply-dry-run` に整理。
- AuditEvent v1 語彙を固定: `event/equivalenceKey/bundleHash/sourceBundleHash/dryRun/sideEffect`。
- 判定規則を3点で固定:
  1) 同値判定は `equivalenceKey + bundleHash` のみ
  2) 監査4点欠損ゼロ
  3) 欠損は fail-closed

### Execute
- collision=0 / safeMode regression=0 を満たす整理を実施。
- 検証失敗時は自己修復を最大3回まで、4回目相当は停止。

### Verify
- `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
- `git diff --check`

### Acceptance Criteria / DoD
- [ ] API/CLI/GUI が同一入力時に同一 `equivalenceKey` かつ同一 `bundleHash`
- [ ] 監査4点（`query / bundle / proposal / apply`）欠損率0%
- [ ] `dryRun=true` 時の副作用は常に `sideEffect=none`
- [ ] `sourceBundleHash=mock:<hash>` で同値性検証を完結可能
- [ ] SafeMode regression = 0

## Phase 5 Proceed（次工程向け固定契約の出力）
### Fixed contract handoff
- Contract IDs: CE4監査I/F + CE1/CE2参照語彙
- 禁止事項: 監査欠損成功扱い / 語彙再定義 / safeMode緩和
- 検証条件: 同値判定軸固定, 監査4点必須, docs-check pass

## Fail-safe（即停止条件）
- Self-Correction 3回超過
- 未定義ファイル競合
- SafeMode後退の兆候
- 依存前提崩壊
