# Issue Draft: CE0 Core Graph Repositioning（Stream B / CE契約群 / contract-only planning）

- Type: Process
- Status: Open
- Priority: P1
- Owner: Stream B（CE契約群）
- Scope: `01_Plans/issues/`（docs-only / contract-only / mock-first）
- Editable: `issue-CE0-core-graph-repositioning.md` のみ
- Related Backlog: `CE-0`
- Related ADR/Spec: `ADR-0028`, `02_Architecture/schemas.md`
- Verification: `docs-check`

## Lane guard
- Core Graph責務境界の**契約固定のみ**を扱う（実装禁止）。
- 未承認決定は `held` 扱いで確定しない。
- 強制ワークフローは `Phase 1 Read → Phase 2 I/F Mock Freeze → Phase 3 ADR CDC → Phase 4 Plan→Execute→Verify → Phase 5 Proceed`。

## Phase 1 Read（全対象Read: Status / Scope / Related ADR確認）
### Graph role I/F
- `working`: 編集作業領域
- `context_projection`: read-only投影
- `consensus`: 承認済み合意領域

### Transition / No-Go
- 許可: `working -> consensus` は `patch+approval` のみ
- 禁止: direct write / auto-apply / auto-publish

### safeMode境界
- `CE0-SAFEMODE-IF` を参照し、Graph再配置タスク側で緩和しない。

## Phase 2 I/F Mock Freeze（ContextQuery / ContextBundle / Review 境界をI/Fのみ固定）
- CE1: `context_projection` は read-only参照のみ。
- CE2: proposal lifecycle は `working` に限定、`consensus` 直更新禁止。
- CE4: 監査導線は `query/bundle/proposal/apply` を共通必須。
- 参照境界は `CG-01..05` 参照のみで記述し、再定義しない。

## Phase 3 ADR CDC（方針差分時のみ Context / Decision / Consequences を記録し承認待ち）
- **Context**: Graph role/transition/audit の語彙衝突有無。
- **Decision**: `WorkingGraph / ContextProjectionGraph / Consensus Graph` へ固定。
- **Consequences**: CE1/CE2/CE4の連携時に role/transition の解釈が単一化。
- **Approval**: 差分発生時の反映状態は `held`。

## Phase 4 Plan→Execute→Verify（AC/DoD補完 + docs-check自己検証）
### Plan
- 役割・遷移・監査の3層をIssue記述内で分離。
- `working -> consensus = patch+approval only` を明示。
- `context_projection` 書換を fail-closed 条件として統一。

### Execute
- collision=0 / safeMode regression=0 を満たす整理を実施。
- 検証失敗時は自己修復を最大3回まで、4回目相当は停止。

### Verify
- `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
- `git diff --check`

### Acceptance Criteria / DoD
- [ ] `working -> consensus = patch+approval only` が全Issue一致
- [ ] `context_projection` read-only が全Issue一致
- [ ] 監査4点欠損=0
- [ ] SafeMode regression = 0

## Phase 5 Proceed（次工程向け固定契約の出力）
### Fixed contract handoff
- Contract IDs: `CG-01..05`, `CE0-SAFEMODE-IF`
- 禁止事項: direct write / auto-apply / auto-publish / safeMode緩和
- 検証条件: role/transition/audit衝突0, docs-check pass

## Fail-safe（即停止条件）
- Self-Correction 3回超過
- 未定義ファイル競合
- SafeMode後退の兆候
- 依存前提崩壊
