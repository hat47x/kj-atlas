# Issue Draft: CE4 API/CLI/監査統合（Stream E / CE4専任 / contract-only planning）

- Type: Feature request
- Status: Open
- Priority: P2
- Owner: Stream E（CE4専任）
- Scope: `01_Plans/issues/`（docs-only / contract-only / mock-first）
- Editable: `issue-CE4-api-cli-audit-integration.md` のみ
- Related Backlog: `CE-4`
- Related ADR/Spec: `ADR-0028`, `ADR-0008`, `02_Architecture/schemas.md`
- Verification: `docs-check`

## Lane guard（独立性・停止条件）
- CE4はCE0 SSOT + CE1/CE2 read-only handoff を参照し、契約語彙を再定義しない。
- CE4は API/CLI/監査の契約I/F固定のみ（実装禁止）。
- CE1/CE0/CE2契約は参照専用（CE4で再定義しない）。
- 検証失敗時の自己修復は最大3回、4回目相当は停止。
- 強制ワークフローは `Phase 1 Read → Phase 2 I/F Mock Freeze → Phase 3 ADR CDC → Phase 4 Execute+Verify → Phase 5 Proceed`。

## Phase 1 Read（equivalenceKey+bundleHash / audit4点 / fail-closed 前提確認）
### Read同期スナップショット
- 固定語彙: `equivalenceKey + bundleHash` / `sourceBundleHash` / proposal lifecycle
- Scope: API/CLI/監査I/F契約固定のみ（実装禁止）
- No-Go語彙: 監査欠損成功扱い / 語彙再定義 / safeMode既定緩和

### 同値性I/F（CE1参照語彙のみ）
- 判定軸は `equivalenceKey + bundleHash`（AND）に固定。
- `queryCanonicalHash` は CE1 参照語彙として受理し、CE4で意味再定義しない。

### 監査I/F（CE2参照語彙のみ）
- 必須4点: `query / bundle / proposal / apply`。
- `dryRun=true -> sideEffect=none` を固定。
- `sourceBundleHash=mock:<hash>` を同値検証に利用し、依存切断を維持。

### No-Go / safeMode境界
- 監査欠損の成功扱い禁止（fail-closed）。
- `CE0-SAFEMODE-IF` を参照し、CE4側で緩和しない。

## Phase 2 I/F Mock Freeze（CE1/CE2参照語彙のみで固定）
### Contract IDs（CE4固定I/F）
- `CE4-EQUIVALENCE-IF`
- `CE4-AUDIT-CHAIN-IF`
- `CE4-DRYRUN-SAFETY-IF`
- `CE4-MOCK-HASH-IF`

### Freeze boundary
- CE1参照境界: `bundleHash/sourceBundleHash/queryCanonicalHash/equivalenceKey` 語彙のみ依存。
- CE2参照境界: proposal lifecycle（`proposed/accepted/rejected/held`）と `proposal/apply` 監査語彙のみ依存。
- CE4内で hash語彙・状態語彙を再定義しない。
- `mock:<hash>` と本番hashで監査フローを分岐させない（同一fail-closed）。

## Phase 3 ADR CDC（必要時のみ Context / Decision / Consequences）
- 差分検知ログ対象: `equivalenceKey + bundleHash` 判定軸、`sourceBundleHash` 語彙、proposal lifecycle の不一致。
- **Context**: API/CLI/GUI間の同値判定・監査語彙衝突有無。
- **Decision**: `equivalenceKey + bundleHash` 固定、監査4点必須、fail-closed維持。
- **Consequences**: CE1/CE2参照境界の一意化、監査欠損時の停止一貫性を確保。
- **Approval**: 差分発生時の反映状態は `held`。

## Phase 4 Execute+Verify（AC/DoD補完 → 合意 → docs-check）
### Execute（contract-only）
- 公開I/Fを `context-query/context-bundle/proposal-diff/apply-dry-run` に整理。
- AuditEvent v1 語彙を固定: `event/equivalenceKey/bundleHash/sourceBundleHash/dryRun/sideEffect`。
- 判定規則を3点で固定:
  1) 同値判定は `equivalenceKey + bundleHash` のみ
  2) 監査4点欠損ゼロ（`query/bundle/proposal/apply`）
  3) 欠損は fail-closed

### Consensus（合意条件）
- CE1語彙参照: `equivalenceKey/bundleHash/sourceBundleHash/queryCanonicalHash` を再定義せず利用。
- CE2語彙参照: `proposed/accepted/rejected/held` + `proposal/apply` を再定義せず利用。
- Stopper合意: 監査欠損成功扱い・safeMode緩和・自己修復4回目相当・未定義競合で停止。

### Verify（docs-check）
- `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
- `git diff --check`

### Acceptance Criteria / DoD
- [x] API/CLI/GUI が同一入力時に同一 `equivalenceKey` かつ同一 `bundleHash`
- [x] 監査4点（`query / bundle / proposal / apply`）欠損率0%
- [x] `dryRun=true` 時の副作用は常に `sideEffect=none`
- [x] `sourceBundleHash=mock:<hash>` で同値性検証を完結可能
- [x] SafeMode regression = 0（`CE0-SAFEMODE-IF` 参照、緩和なし）

## Phase 5 Proceed（read-only contract handoff）
### Fixed contract handoff
- Contract IDs: `CE4-EQUIVALENCE-IF` / `CE4-AUDIT-CHAIN-IF` / `CE4-DRYRUN-SAFETY-IF` / `CE4-MOCK-HASH-IF`
- Read-only参照: CE1語彙（`equivalenceKey/bundleHash/sourceBundleHash/queryCanonicalHash`）+ CE2語彙（proposal lifecycle + `proposal/apply`）
- 禁止事項: 監査欠損成功扱い / 語彙再定義 / safeMode緩和
- 検証条件: 同値判定軸固定, 監査4点必須, docs-check pass

## Fail-safe（即停止条件）
- Self-Correction 3回超過
- 未定義ファイル競合
- SafeMode後退の兆候
- 依存前提崩壊
