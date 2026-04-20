# Issue Draft: CE2 Low-Risk AI Assist（Stream B / CE契約群 / proposal-only / contract-only planning）

- Type: Feature request
- Status: Open
- Priority: P1
- Owner: Stream B（CE契約群）
- Scope: `01_Plans/issues/`（docs-only / contract-only / mock-first）
- Editable: `issue-CE2-low-risk-ai-assist.md` のみ
- Related Backlog: `CE-2`
- Related ADR/Spec: `ADR-0028`, `02_Architecture/schemas.md`
- Verification: `docs-check`

## Lane guard
- proposal lifecycle は `proposed | accepted | rejected | held` を固定し、再定義しない。
- CE2は proposal-only 契約固定のみ（実装禁止）。
- CE1/CE0契約は参照専用（CE2で再定義しない）。
- `reviewState=human_reviewed` のAI自動昇格は禁止。
- 強制ワークフローは `Phase 1 Read → Phase 2 I/F Mock Freeze → Phase 3 ADR CDC → Phase 4 Plan→Execute→Verify → Phase 5 Proceed`。

## Phase 1 Read（全対象Read: Status / Scope / Related ADR確認）
### Read同期スナップショット
- 固定語彙: `sourceBundleHash` / proposal lifecycle / `equivalenceKey + bundleHash`（CE4同値判定参照）
- No-Go語彙: `auto-apply` / AI review自動昇格 / `preview bypass` / `safeMode既定緩和`

### Contract IDs
- `CE2-PROPOSAL-IF`
- `CE2-LIFECYCLE-IF`
- `CE2-DRIFT-STOP-IF`
- `CE2-NO-AUTOAPPLY-IF`

### Proposal I/F
- 必須: `proposalId/diff/sourceBundleHash/rationale/status/reviewState`
- `status`: `proposed | accepted | rejected | held`
- `reviewState`: `unreviewed | human_reviewed`

### No-Go / safeMode境界
- auto-apply 禁止
- AIによる `human_reviewed` 自動昇格禁止
- `CE0-SAFEMODE-IF` を参照し、CE2側で緩和しない

## Phase 2 I/F Mock Freeze（ContextQuery / ContextBundle / Review 境界をI/Fのみ固定）
- CE1参照境界: `sourceBundleHash` 比較キーのみ依存。
- CE4参照境界: `proposal/apply` 監査語彙を共通化し、同値判定は `equivalenceKey + bundleHash` を参照のみで利用。
- drift検知時は `status=held` で停止。
- CE2独自のquery語彙追加は禁止（再定義防止）。

## Phase 3 ADR CDC（方針差分時のみ Context / Decision / Consequences を記録し承認待ち）
- 差分検知ログ: proposal lifecycle、`sourceBundleHash`、No-Go語彙の不一致。
- **Context**: proposal lifecycle / review遷移 / drift-stop の衝突有無。
- **Decision**: proposal-only + no-auto-apply + human-only昇格を維持。
- **Consequences**: CE4監査で proposal/apply の追跡可能性が固定化。
- **Approval**: 差分発生時の反映状態は `held`。

## Phase 4 Plan→Execute→Verify（AC/DoD補完 + docs-check自己検証）
### Plan
- lifecycleを `proposed/accepted/rejected/held` に固定。
- `held` を fail-safe停止語彙として統一。
- `sourceBundleHash === bundleHash` を参照整合キーとして明示。

### Execute
- collision=0 / safeMode regression=0 を満たす整理を実施。
- 検証失敗時は自己修復を最大3回まで、4回目相当は停止。

### Verify
- `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
- `git diff --check`

### Acceptance Criteria / DoD
- [ ] auto-apply経路0件
- [ ] AI自動昇格0件
- [ ] CE1 drift検知時は `status=held`
- [ ] `sourceBundleHash === bundleHash` 比較語彙がCE1と一致
- [ ] SafeMode regression = 0

## Phase 5 Proceed（次工程向け固定契約の出力）
### Fixed contract handoff
- Contract IDs: `CE2-PROPOSAL-IF` / `CE2-LIFECYCLE-IF` / `CE2-DRIFT-STOP-IF` / `CE2-NO-AUTOAPPLY-IF`
- 禁止事項: auto-apply / AI review昇格 / safeMode緩和
- 検証条件: lifecycle固定, drift-stop有効, docs-check pass

## Fail-safe（即停止条件）
- Self-Correction 3回超過
- 未定義ファイル競合
- SafeMode後退の兆候
- 依存前提崩壊
