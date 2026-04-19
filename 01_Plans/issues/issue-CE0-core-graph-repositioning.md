# Issue Draft: CE0 Core Graph Repositioning（Stream D / planning-only）

- Type: Process
- Status: Open
- Priority: P1
- Owner: Stream D
- Scope: `01_Plans/issues/`（docs-only / contract-only / mock-first）
- Related Backlog: `CE-0`
- Related ADR/Spec: `ADR-0028`
- Verification: `docs-check`

## Lane guard
- 本Issueは Core Graph責務境界の**契約固定のみ**を扱う（実装禁止）。
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

## Phase 2 Plan（AC/DoD不足ドラフト）
### AC Draft
- [ ] `working -> consensus = patch+approval only` が全Issue一致
- [ ] `context_projection` read-only が全Issue一致
- [ ] 監査4点欠損=0

### DoD Draft
- [ ] Core/Consensus語彙の二重定義なし
- [ ] 役割・遷移・監査の3層で説明可能

## Phase 3 Execute（依存正規化）
- CE2/CE4へは参照専用I/Fを渡す（再定義禁止）。
- CE1未完でも `sourceBundleHash=mock:<hash>` 前提で整合検証を継続。

## Phase 4 Verify
- `docs-check`
- 遷移衝突0、語彙衝突0、safeMode後退0。

## Phase 5 Proceed（実装入力固定）
### I/F仕様書固定
- GraphRole: `working | context_projection | consensus`
- Transition: `working -> consensus via patch+approval`
- AuditEnvelope: `query/bundle/proposal/apply` 必須
