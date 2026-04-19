# Issue Draft: CE4 API/CLI/監査統合（Stream E execution / planning-only）

- Type: Feature request
- Status: Completed (planning I/F freeze confirmed)
- Priority: P2
- Owner: Stream G（CE4専属）
- Scope: `01_Plans/issues/`（docs-only / contract-only / mock-first）
- Related Backlog: `CE-4`
- Related ADR/Spec: `ADR-0028`, `ADR-0008`
- Verification: `docs-check`

## Lane guard（独立性・停止条件）
- 編集許可: `issue-CE4-api-cli-audit-integration.md` のみ。
- 編集禁止: その他すべてのファイル。
- 指定外編集を検知した場合は即停止。
- 3回超過（再試行・再修正）または契約衝突（I/F矛盾）を検知した場合は停止。
- CE4は API/CLI/監査の計画I/F固定タスクであり、実装指示混入時は停止。

## Phase 1 Read（契約I/F抽出）
### 同値性I/F
- 判定軸は `equivalenceKey + bundleHash`（AND）に固定。
- API/CLI/GUI の比較は上記2軸のみで評価する。

### 監査I/F
- 必須4点（欠損ゼロ方針）: `query / bundle / proposal / apply`
- `dryRun=true -> sideEffect=none` を固定。
- `sourceBundleHash=mock:<hash>` を許容し、外部依存を切断する。

## Phase 2 ADR CDC（必要時のみ）
- 条件: 現行ADR（`ADR-0028`, `ADR-0008`）と CE4 I/Fに衝突がある場合のみ実施。
- 方針: CDCは「契約固定の差分最小」に限定し、実装要件を追加しない。
- 出力: I/F整合メモ（同値性2軸・監査4点・mock hash許容）を本Issueへ追記。

## Phase 3 Plan（AC / DoD 固定）
### Acceptance Criteria（固定）
- [ ] API/CLI/GUI が同一入力時に同一 `equivalenceKey` かつ同一 `bundleHash` を返す。
- [ ] 監査4点（`query / bundle / proposal / apply`）の欠損率が0%である。
- [ ] `dryRun=true` 実行時の副作用が常に `sideEffect=none` である。
- [ ] `sourceBundleHash=mock:<hash>` で同値性検証を完結できる（依存切断）。

### Definition of Done（固定）
- [ ] hash種別（mock/本番）で監査フローを分岐させない。
- [ ] 欠損を成功扱いしない（fail-closed）。
- [ ] 計画I/Fが API/CLI/監査の3系統で同一語彙・同一判定軸を保持する。

## Phase 4 Execute（計画I/F固定のみ）
- 依存待ち（例: CE3完了待ち）を前提にせず、`mock:<hash>` 入力で契約検証を先行する。
- 実装タスクへは「固定済みI/F」を入力として渡すだけに限定する。
- 本フェーズではコード変更・他文書変更を実施しない。

## Phase 5 Verify
- `docs-check`
- 判定基準: 同値性不一致0、監査欠損0、dry-run副作用逸脱0、契約衝突0。
- フェイルセーフ: 停止条件（3回超過 / 契約衝突）に達した場合は Proceed へ進まない。

## Phase 6 Proceed（実装入力固定）
### I/F仕様書固定
- Logical operations: `context-query | context-bundle | proposal-diff | apply-dry-run`
- AuditEvent v1: `event/equivalenceKey/bundleHash/sourceBundleHash/dryRun/sideEffect`
- 実装チームへ渡す固定要件:
  1) 同値判定は `equivalenceKey + bundleHash` のみ
  2) 監査4点欠損ゼロ
  3) `mock:<hash>` 許容で依存切断

## Stream E Completion Notes (2026-04-19)

### Phase 1 Read同期 + スコープ固定
- CE4 lane を planning-only / docs-only として再固定。
- 編集対象を本Issueファイルに限定し、API/CLI実装ファイル変更は非対象とした。

### Phase 2 契約確認（CDC）
- CDC明文化:
  - 同値性: `equivalenceKey AND bundleHash`
  - 監査4点: `query/bundle/proposal/apply`（欠損はfail-closed）
  - `dryRun=true -> sideEffect=none`
  - `sourceBundleHash=mock:<hash>` 許容
- `02_Architecture/schemas.md` の CE4 `AuditEventV1` 契約と照合し、語彙衝突なしを確認。

### Phase 3 Execute（CE4 lane）
- 実装要件の追加は行わず、固定I/Fを実装入力として再提示する形に限定。
- hash種別（mock/本番）で監査フローを分岐しない方針を維持。

### Phase 4 Verify（docs-check）
- docs-check 実行結果で issue memo の整合を確認（validator + unit test）。

### Phase 5 Proceed/Stop
- Proceed 判定: ✅（同値判定軸の再定義0 / 監査欠損許容0 / 再修復回数0）
- Stop 条件（3回超過・契約衝突）は未発火。
