# Issue Draft: CE0 Core Graph Repositioning（Stream C / CE契約専任 / contract-only planning）

- Type: Process
- Status: Open
- Priority: P1
- Owner: Stream C（CE契約専任）
- Scope: `01_Plans/issues/`（docs-only / contract-only / mock-first）
- Editable: `issue-CE0-core-graph-repositioning.md` のみ
- Related Backlog: `CE-0`
- Related ADR/Spec: `ADR-0028`, `02_Architecture/schemas.md`
- Verification: `docs-check`

## Lane guard
- Core Graph責務境界の**契約固定のみ**を扱う（実装禁止）。
- 未承認決定は `held` 扱いで確定しない。
- safeMode後退、auto-apply許容、未承認確定化を検知したら即停止。
- 強制ワークフローは `Plan → Execute → Verify → Proceed`。

## Phase 1) Read（CE0契約ID群・NoGo語彙・safeMode境界の再確認）
### Graph role I/F
- `working`: 編集作業領域
- `context_projection`: read-only投影
- `consensus`: 承認済み合意領域

### Transition / No-Go
- 許可: `working -> consensus` は `patch+approval` のみ
- 禁止: direct write / auto-apply / auto-publish

### safeMode境界
- `CE0-SAFEMODE-IF` を参照し、Graph再配置タスク側で緩和しない。

## Phase 2) Plan（CE1/CE2/CE4への参照境界を再定義なしで設計）
- CE1: `context_projection` は read-only参照のみ。
- CE2: proposal lifecycle は `working` に限定、`consensus` 直更新禁止。
- CE4: 監査導線は `query/bundle/proposal/apply` を共通必須。
- 参照境界は `CG-01..05` 参照のみで記述し、再定義しない。

## Phase 3) ADR CDC（変更時のみ Context / Decision / Consequences を明文化）
- **Context**: Graph role/transition/audit の語彙衝突有無。
- **Decision**: `WorkingGraph / ContextProjectionGraph / Consensus Graph` へ固定。
- **Consequences**: CE1/CE2/CE4の連携時に role/transition の解釈が単一化。
- 変更がない場合は「CDC更新なし」を記録して終了。

## Phase 4) Execute（collision=0 / safeMode regression=0 を満たす整理）
- 役割・遷移・監査の3層をIssue記述内で分離。
- `working -> consensus = patch+approval only` を明示。
- `context_projection` 書換を fail-closed 条件として統一。
- 検証失敗時は自己修復を最大3回まで、4回目相当は停止。

## Phase 5) Verify / Proceed（docs-check と再開条件の記録）
### Acceptance Criteria
- [ ] `working -> consensus = patch+approval only` が全Issue一致
- [ ] `context_projection` read-only が全Issue一致
- [ ] 監査4点欠損=0
- [ ] SafeMode regression = 0

### Verify
- `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
- `git diff --check`

### Proceed（再開条件）
- 再開条件1: role/transition/audit 3層が衝突ゼロで説明可能。
- 再開条件2: safeMode境界後退ゼロ。
- 再開条件3: No-Go検知時は即停止→修正→3回以内に収束。
