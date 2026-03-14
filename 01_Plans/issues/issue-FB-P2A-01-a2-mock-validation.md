# Issue Draft: FB-P2A-01-A2 Island階層モデル導入 / モック検証

- Type: Feature request
- Status: Ready (A2 Validation Planned)
- Priority: P0
- Owner: Stream E
- Scope: `01_Plans/issues/` (planning memo only)
- Related Backlog: `FB-P2A-01`
- Related ADR/Spec: `ADR-0007`, `ADR-0001`, `issue-FB-P2A-01-a1-interface-contract.md`
- Expected verification level: `integration`

## Requirement meta I/F（共通キー）

- RequirementID: `RQ-2A-01`
- RequirementStatement: A1で固定した `IslandHierarchyContractV1` の妥当性をモックで検証する。
- Phase: `A2 Mock Validation`
- PriorityClass（Must / Should / Could）: Must
- GoNoGoGate（Required / Optional / N/A）: Required
- SecurityGateImpact: N/A（計画のみ）
- VerificationLevel: integration
- DecisionStatus: Fixed

## Mock validation scope

- 入力モック:
  - M1: root island（`parentIslandId=null`）
  - M2: 3階層ネスト（root→child→grandchild）
  - M3: 不正参照（存在しない`parentIslandId`）
  - M4: 循環参照（A→B→A）
- 期待判定:
  - M1/M2は契約適合。
  - M3/M4はFail Fastで拒否。

## Responsibility split（失敗時責務分離）

- 契約修正責務（A1へ戻す）:
  - Required fieldsやInvariant自体が不足/矛盾している。
- モック修正責務（A2内で完結）:
  - モックデータが契約条件を満たしていない、またはテスト観点漏れ。
- 実装修正責務（A3へ引き継ぎ）:
  - 契約・モックは妥当だが、実装計画に反映されていない。

## Acceptance criteria

- [x] A1契約を変更せずにモック検証ケースを定義できる。
- [x] 正常系/異常系の判定基準が明示される。
- [x] 失敗時に「契約修正 or モック修正」の切り分けルールが記録される。
- [x] A3へ渡す検証ログ項目（入力/期待/結果/責務）が定義される。

## A3 handoff I/F

- Handoff payload:
  - `contractVersion`
  - `mockCaseId`
  - `validationResult`
  - `ownerOfFix`（`A1` / `A2` / `A3`）


## Phase execution log（A2）

### Read sync（Phase開始時）

- `issue-FB-P2A-01-a1-interface-contract.md`
- `issue-FB-P2A-01-a2-mock-validation.md`
- `issue-FB-P2A-01-a3-implementation.md`

### Plan

- A1固定契約を変更せず、M1〜M4の判定表を準備する。
- 失敗時の責務分離（A1/A2/A3）とA3引き継ぎログ項目を固定する。

### Execute

- M1/M2を正常系、M3/M4を異常系として契約Invariantに対応付ける。
- `contractVersion` / `mockCaseId` / `validationResult` / `ownerOfFix` を引き継ぎI/Fとして定義する。

### Verify

- A1の Required fields / Invariants を変更していないことを確認する。
- 判定結果が `M1/M2=pass`・`M3/M4=fail` のGoNoGo条件へ接続可能であることを確認する。

### Proceed

- A3へ handoff payload をそのまま渡し、実装接続条件の評価へ進む。

## ADR change handling

- ADR change involved: **No**（A2は契約の妥当性検証のみで、ADR改定は不要）
- C/D/C + approval: **N/A**

## Contract freeze confirmation

- FixedContractRef: `issue-FB-P2A-01-a1-interface-contract.md#contract-definitiona1成果物`
- FreezeRule: A2では `IslandHierarchyContractV1` のRequired fields / Invariantsを変更しない。
- DriftCheck:
  - ContractLinks（A1→A2→A3）が全て到達可能であること。
  - Invariants（存在参照 / DAG / roundtrip不変）を判定表にそのまま転写すること。

## Validation log schema（A3引き継ぎ必須）

| field | type | description |
|---|---|---|
| `contractVersion` | string | `IslandHierarchyContractV1` 固定値 |
| `mockCaseId` | string | `M1`〜`M4` |
| `validationResult` | enum(`pass`,`fail`) | モック判定結果 |
| `ownerOfFix` | enum(`A1`,`A2`,`A3`) | 失敗時の修正責務 |
| `evidence` | string | 判定根拠（Invariant IDまたは期待値） |

## State sync / conflict check

- Phase開始時Read対象:
  - `issue-FB-P2A-01-a1-interface-contract.md`
  - `issue-FB-P2A-01-a2-mock-validation.md`
  - `issue-FB-P2A-01-a3-implementation.md`

## Validation plan

- Command:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`

## Fail-safe

- 自己修復が3回連続で失敗、またはA1契約リンク切れを検出した場合は停止して指示待ち。


### Stream B execution note（A2 mock validation）

- 実装配置: `03_Implement/frontend/src/domain/contracts/island_hierarchy_handoff.ts`
- テスト配置: `03_Implement/frontend/src/domain/contracts/island_hierarchy_handoff.test.ts`
- M1/M2=pass, M3/M4=fail を handoff log (`contractVersion` / `mockCaseId` / `validationResult` / `ownerOfFix` / `evidence`) で固定。
- A1契約 (`IslandHierarchyContractV1`) の Required fields / Invariants は変更していない。
