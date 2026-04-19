# Issue Draft: CE0 Core Graph Repositioning（Stream D / CE契約専任 / planning-only）

- Type: Process
- Status: Open
- Priority: P1
- Owner: Stream D（CE契約専任）
- Scope: `01_Plans/issues/`（docs-only / contract-only / mock-first）
- Related Backlog: `CE-0`
- Related ADR/Spec: `ADR-0028`, `02_Architecture/schemas.md`
- Verification: `docs-check`

## Lane guard
- 本Issueは Core Graph責務境界の**契約固定のみ**を扱う（実装禁止）。
- 未承認決定は `held` 扱いとし、確定扱いしない。
- 実装指示混入時は停止。

## Phase 1 Read（契約I/F抽出）
### Graph role I/F
- `working`: 編集作業領域
- `context_projection`: read-only投影
- `consensus`: 承認済み合意領域

### Transition I/F
- 許可: `working -> consensus` は `patch+approval` のみ
- 禁止: direct write / auto-apply

### Audit I/F
- 必須4点: `query / bundle / proposal / apply`

## Phase 2 CE0契約凍結反映
- `CG-01..05` を本Issue側で再定義せず参照に統一する。
- CE1/CE2/CE4 へ配布する Graph role / transition / audit は read-only handoff とする。

## Phase 3 Plan（AC/DoD）
### Acceptance Criteria
- [ ] `working -> consensus = patch+approval only` が全Issue一致
- [ ] `context_projection` read-only が全Issue一致
- [ ] 監査4点欠損=0
- [ ] SafeMode regression = 0

### Definition of Done
- [ ] Core/Consensus語彙の二重定義なし
- [ ] 役割・遷移・監査の3層で説明可能
- [ ] self-heal 3回以内

## Phase 4 Verify
- `docs-check`
- 遷移衝突0、語彙衝突0、safeMode後退0。

## Phase 5 Proceed（実装ストリーム向けI/F配布）
### I/F仕様書固定
- GraphRole: `working | context_projection | consensus`
- Transition: `working -> consensus via patch+approval`
- AuditEnvelope: `query/bundle/proposal/apply` 必須
