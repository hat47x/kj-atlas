# Issue Draft: CE4 API/CLI/監査統合（Stream C / contract-only planning）

- Type: Feature request
- Status: Open
- Priority: P2
- Owner: Stream C（CE契約専任）
- Scope: `01_Plans/issues/`（docs-only / contract-only / mock-first）
- Editable: `issue-CE4-api-cli-audit-integration.md` のみ
- Related Backlog: `CE-4`
- Related ADR/Spec: `ADR-0028`, `ADR-0008`, `02_Architecture/schemas.md`
- Verification: `docs-check`

## Lane guard（独立性・停止条件）
- CE4は API/CLI/監査の計画I/F固定のみ（実装禁止）。
- CE1/CE0/CE2契約は参照専用（CE4で再定義しない）。
- safeMode後退、auto-apply許容、未承認確定化を検知したら即停止。
- 検証失敗時の自己修復は最大3回、4回目相当は停止。
- 強制ワークフローは `Plan → Execute → Verify → Proceed`。

## Phase 1) Read（CE0契約ID群・NoGo語彙・safeMode境界の再確認）
### 同値性I/F
- 判定軸は `equivalenceKey + bundleHash`（AND）に固定。

### 監査I/F
- 必須4点: `query / bundle / proposal / apply`
- `dryRun=true -> sideEffect=none` 固定。
- `sourceBundleHash=mock:<hash>` を許容（依存切断）。

### No-Go / safeMode境界
- 監査欠損の成功扱い禁止（fail-closed）。
- `CE0-SAFEMODE-IF` を参照し、CE4側で緩和しない。

## Phase 2) Plan（CE1/CE2/CE4への参照境界を再定義なしで設計）
- CE1参照境界: `bundleHash/sourceBundleHash/queryCanonicalHash` 語彙のみ依存。
- CE2参照境界: lifecycle（`proposed/accepted/rejected/held`）と `proposal/apply` 監査語彙のみ依存。
- CE4内で hash語彙・状態語彙を再定義しない。
- `mock:<hash>` と本番hashで監査フローを分岐させない。

## Phase 3) ADR CDC（変更時のみ Context / Decision / Consequences を明文化）
- **Context**: API/CLI/GUI間の同値判定・監査語彙衝突有無。
- **Decision**: `equivalenceKey + bundleHash` 固定、監査4点必須、fail-closed維持。
- **Consequences**: CE1/CE2参照境界の一意化、監査欠損時の停止一貫性を確保。
- 変更がない場合は CDC更新なし。

## Phase 4) Execute（collision=0 / safeMode regression=0 を満たす整理）
- 公開I/Fを `context-query/context-bundle/proposal-diff/apply-dry-run` に整理。
- AuditEvent v1 語彙を固定: `event/equivalenceKey/bundleHash/sourceBundleHash/dryRun/sideEffect`。
- 判定規則を3点で固定:
  1) 同値判定は `equivalenceKey + bundleHash` のみ
  2) 監査4点欠損ゼロ
  3) 欠損は fail-closed

## Phase 5) Verify / Proceed（docs-check と再開条件の記録）
### Acceptance Criteria
- [ ] API/CLI/GUI が同一入力時に同一 `equivalenceKey` かつ同一 `bundleHash`
- [ ] 監査4点（`query / bundle / proposal / apply`）欠損率0%
- [ ] `dryRun=true` 時の副作用は常に `sideEffect=none`
- [ ] `sourceBundleHash=mock:<hash>` で同値性検証を完結可能
- [ ] SafeMode regression = 0

### Verify
- `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
- `git diff --check`

### Proceed（再開条件）
- 再開条件1: 同値判定軸と監査語彙が衝突ゼロ。
- 再開条件2: hash種別（mock/本番）で監査フロー非分岐を維持。
- 再開条件3: fail-safe検知時は停止→修正→3回以内に自己修復。
