# Issue Draft: CE4 API/CLI/監査統合（Stream D / planning-only）

- Type: Feature request
- Status: Open
- Priority: P2
- Owner: Stream D
- Scope: `01_Plans/issues/`（docs-only / contract-only / mock-first）
- Related Backlog: `CE-4`
- Related ADR/Spec: `ADR-0028`, `ADR-0008`
- Verification: `docs-check`

## Lane guard
- CE4は API/CLI/GUI 同値性と監査契約を固定する計画タスク。
- 実装指示混入時は停止。

## Phase 1 Read（契約I/F抽出）
### 同値性I/F
- 判定条件: `equivalenceKey + bundleHash`（AND）

### 監査I/F
- 必須4点: `query / bundle / proposal / apply`
- `dryRun=true -> sideEffect=none` を固定
- `sourceBundleHash=mock:<hash>` 許容

## Phase 2 Plan（AC/DoD不足ドラフト）
### AC Draft
- [ ] API/CLI/GUI 同一入力で同一 `bundleHash`
- [ ] 監査4点欠損率0%
- [ ] dry-run副作用0

### DoD Draft
- [ ] hash種別（mock/本番）で監査フロー分岐しない
- [ ] 欠損成功扱い禁止（fail-closed）

## Phase 3 Execute（依存正規化）
- CE3完了待ちを禁止し、mock入力で同値性検証を先行。
- 運用導線は参照専用I/Fとして固定。

## Phase 4 Verify
- `docs-check`
- 同値性不一致0、監査欠損0、safeMode後退0。

## Phase 5 Proceed（実装入力固定）
### I/F仕様書固定
- Logical operations: `context-query | context-bundle | proposal-diff | apply-dry-run`
- AuditEvent v1: `event/equivalenceKey/bundleHash/sourceBundleHash/dryRun/sideEffect`
