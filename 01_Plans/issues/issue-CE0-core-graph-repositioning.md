# Issue Draft: CE0 Core Graph Repositioning（Stream C / CE契約群 / contract-only planning）

- Type: Process
- Status: Open
- Priority: P1
- Owner: Stream C（CE契約群）
- Scope: `01_Plans/issues/`（docs-only / contract-only / mock-first）
- Editable: `issue-CE0-core-graph-repositioning.md` のみ
- Related Backlog: `CE-0`
- Related ADR/Spec: `ADR-0028`, `02_Architecture/schemas.md`
- Verification: `docs-check`

## Lane guard
- CE0契約IDの再定義禁止（`CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`）。
- Core Graph責務境界の**契約固定のみ**を扱う（実装禁止）。
- 未承認決定は `held` 扱いで確定しない。
- 強制ワークフローは `Phase 1 Read → Phase 2 Plan → Phase 3 ADR CDC → Phase 4 Execute → Phase 5 Verify → Phase 6 Proceed`。

## Phase 1 Read（role / transition / no-go語彙確認）
### Read同期スナップショット
- Contract ID: CE0契約ID群を参照のみで利用（再定義禁止）
- No-Go語彙（CE0 canonical 5 IDs）: `preview_bypass` / `consensus_direct_write` / `auto_apply_or_publish` / `ai_review_auto_promotion` / `safemode_default_relaxation`
- Scope: graph role/transition/audit 契約固定のみ

### Graph role I/F
- `working`: 編集作業領域
- `context_projection`: read-only投影
- `consensus`: 承認済み合意領域

### Transition / No-Go
- 許可: `working -> consensus` は `patch+approval` のみ
- 禁止: direct write / auto-apply / auto-publish

### safeMode境界
- `CE0-SAFEMODE-IF` を参照し、Graph再配置タスク側で緩和しない。

## Phase 2 Plan（AC / DoDドラフト + I/F Mock Freeze）
- AC/DoDを先にドラフトし、ContextQuery / ContextBundle / Review 境界をI/Fのみ固定する。
- CE1: `context_projection` は read-only参照のみ。
- CE2: proposal lifecycle は `working` に限定、`consensus` 直更新禁止。
- CE4: 監査導線は `query/bundle/proposal/apply` を共通必須。
- CE4同値判定語彙は `equivalenceKey + bundleHash` を参照のみで利用する。
- 参照境界は `CG-01..05` 参照のみで記述し、再定義しない。

## Phase 3 ADR CDC（必要時のみ Context / Decision / Consequences を記録し承認待ち）
- 差分検知ログ: role/transition/audit語彙の揺れ、No-Go語彙不一致、SafeMode境界の逸脱。
- **Context**: Graph role/transition/audit の語彙衝突有無。
- **Decision**: `WorkingGraph / ContextProjectionGraph / Consensus Graph` へ固定。
- **Consequences**: CE1/CE2/CE4の連携時に role/transition の解釈が単一化。
- **Approval**: 差分発生時の反映状態は `held`（未承認確定禁止）。
- 衝突未検知時（role/transition/audit語彙揺れ=0 かつ No-Go不一致=0 かつ SafeMode逸脱=0）はCDCを起票しない。

## Phase 4 Execute（working / context_projection / consensus 責務固定）
### Execute方針
- 役割・遷移・監査の3層をIssue記述内で分離。
- `working -> consensus = patch+approval only` を明示。
- `context_projection` 書換を fail-closed 条件として統一。
- collision=0 / safeMode regression=0 を満たす整理を実施。
- 検証失敗時は自己修復を最大3回まで、4回目相当は停止。

## Phase 5 Verify（docs-check / 自律修復最大3回）
- `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
- `git diff --check`

### Acceptance Criteria / DoD
- [ ] `working -> consensus = patch+approval only` が全Issue一致
- [ ] `context_projection` read-only が全Issue一致
- [ ] 監査4点欠損=0
- [ ] SafeMode regression = 0

## Phase 6 Proceed（CE1 / CE2 / CE4参照境界の出力）
### Fixed contract handoff
- Contract IDs: `CG-01..05`, `CE0-SAFEMODE-IF`
- 禁止事項: direct write / auto-apply / auto-publish / safeMode緩和
- 検証条件: role/transition/audit衝突0, docs-check pass
- 参照方向固定: `CE0 -> (CE1, CE2, CE4)` の一方向のみ（下流からCE0契約の再定義禁止）。
- CE1参照境界: `context_projection` は read-only参照のみ（`consensus` への書込不可）。
- CE2参照境界: proposal lifecycle は `working` 専有、`consensus` 反映は `patch+approval` のみ。
- CE4参照境界: 監査導線は `query/bundle/proposal/apply` を必須とし、`equivalenceKey + bundleHash` は参照のみ。

## Fail-safe（即停止条件）
- Self-Correction 3回超過
- 未定義ファイル競合
- SafeMode後退の兆候
- 依存前提崩壊
- No-Go語彙衝突（`preview_bypass` / `consensus_direct_write` / `auto_apply_or_publish` / `ai_review_auto_promotion` / `safemode_default_relaxation`）
