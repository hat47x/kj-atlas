# Issue Draft: CE4 API/CLI/監査統合（Stream D / planning-only）

- Type: Feature request
- Status: Open
- Priority: P2
- Owner: Stream D（CE契約専任）
- Scope: `01_Plans/issues/`（docs-only / contract-only / mock-first）
- Related Backlog: `CE-4`
- Related ADR/Spec: `ADR-0028`, `ADR-0008`, `02_Architecture/schemas.md`
- Verification: `docs-check`

## Lane guard（独立性・停止条件）
- CE4は API/CLI/監査の計画I/F固定タスクであり、実装指示混入時は停止。
- CE1/CE0/CE2 契約は参照専用（CE4で再定義しない）。
- 未承認決定を確定扱いしない。
- 3回超過（再試行・再修正）または契約衝突（I/F矛盾）を検知した場合は停止。

## Phase 1 Read（契約I/F抽出）
### 同値性I/F
- 判定軸は `equivalenceKey + bundleHash`（AND）に固定。
- API/CLI/GUI の比較は上記2軸のみで評価する。

### 監査I/F
- 必須4点（欠損ゼロ方針）: `query / bundle / proposal / apply`
- `dryRun=true -> sideEffect=none` を固定。
- `sourceBundleHash=mock:<hash>` を許容し、外部依存を切断する。

## Phase 2 契約参照正規化（CE1/CE2参照固定）
- `bundleHash/sourceBundleHash` は CE1契約語彙を参照する。
- `proposal/apply` 監査導線は CE2 proposal lifecycle 語彙（`proposed/accepted/rejected/held`）と整合させる。
- 欠損を成功扱いしない（fail-closed）。

## Phase 3 Plan（AC / DoD）
### Acceptance Criteria
- [ ] API/CLI/GUI が同一入力時に同一 `equivalenceKey` かつ同一 `bundleHash` を返す
- [ ] 監査4点（`query / bundle / proposal / apply`）欠損率0%
- [ ] `dryRun=true` 実行時の副作用は常に `sideEffect=none`
- [ ] `sourceBundleHash=mock:<hash>` で同値性検証を完結できる（依存切断）

### Definition of Done
- [ ] hash種別（mock/本番）で監査フローを分岐させない
- [ ] 欠損を成功扱いしない（fail-closed）
- [ ] 計画I/Fが API/CLI/監査で同一語彙・同一判定軸を保持

## Phase 4 Verify
- `docs-check`
- 判定基準: 同値性不一致0、監査欠損0、dry-run副作用逸脱0、契約衝突0。
- 自己修復は最大3回。4回目相当は停止。

## Phase 5 Proceed（実装ストリーム向けI/F配布）
### I/F仕様書固定
- Logical operations: `context-query | context-bundle | proposal-diff | apply-dry-run`
- AuditEvent v1: `event/equivalenceKey/bundleHash/sourceBundleHash/dryRun/sideEffect`
- 実装チームへ渡す固定要件:
  1) 同値判定は `equivalenceKey + bundleHash` のみ
  2) 監査4点欠損ゼロ
  3) `mock:<hash>` 許容で依存切断
