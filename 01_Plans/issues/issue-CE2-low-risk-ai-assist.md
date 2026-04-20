# Issue Draft: CE2 Low-Risk AI Assist（Stream C / proposal-only / contract-only planning）

- Type: Feature request
- Status: Open
- Priority: P1
- Owner: Stream C（CE契約専任）
- Scope: `01_Plans/issues/`（docs-only / contract-only / mock-first）
- Editable: `issue-CE2-low-risk-ai-assist.md` のみ
- Related Backlog: `CE-2`
- Related ADR/Spec: `ADR-0028`, `02_Architecture/schemas.md`
- Verification: `docs-check`

## Lane guard
- CE2は proposal-only 契約固定のみ（実装禁止）。
- CE1/CE0契約は参照専用（CE2で再定義しない）。
- `reviewState=human_reviewed` のAI自動昇格は禁止。
- safeMode後退、auto-apply許容、未承認確定化を検知したら即停止。
- 強制ワークフローは `Plan → Execute → Verify → Proceed`。

## Phase 1) Read（CE0契約ID群・NoGo語彙・safeMode境界の再確認）
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

## Phase 2) Plan（CE1/CE2/CE4への参照境界を再定義なしで設計）
- CE1参照境界: `sourceBundleHash` 比較キーのみ依存。
- CE4参照境界: `proposal/apply` 監査語彙を共通化。
- drift検知時は `status=held` で停止。
- CE2独自のquery語彙追加は禁止（再定義防止）。

## Phase 3) ADR CDC（変更時のみ Context / Decision / Consequences を明文化）
- **Context**: proposal lifecycle / review遷移 / drift-stop の衝突有無。
- **Decision**: proposal-only + no-auto-apply + human-only昇格を維持。
- **Consequences**: CE4監査で proposal/apply の追跡可能性が固定化。
- 変更がない場合は CDC更新なし。

## Phase 4) Execute（collision=0 / safeMode regression=0 を満たす整理）
- lifecycleを `proposed/accepted/rejected/held` に固定。
- `held` を fail-safe停止語彙として統一。
- `sourceBundleHash === bundleHash` を参照整合キーとして明示。
- 検証失敗時は自己修復を最大3回まで、4回目相当は停止。

## Phase 5) Verify / Proceed（docs-check と再開条件の記録）
### Acceptance Criteria
- [ ] auto-apply経路0件
- [ ] AI自動昇格0件
- [ ] CE1 drift検知時は `status=held`
- [ ] `sourceBundleHash === bundleHash` 比較語彙がCE1と一致
- [ ] SafeMode regression = 0

### Verify
- `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
- `git diff --check`

### Proceed（再開条件）
- 再開条件1: proposal語彙が単一正本で衝突ゼロ。
- 再開条件2: no-auto-apply / human-only昇格制約を維持。
- 再開条件3: fail-safe検知時は停止→修正→3回以内に自己修復。
