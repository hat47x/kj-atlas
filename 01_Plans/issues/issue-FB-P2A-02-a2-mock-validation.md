# Issue Draft: FB-P2A-02-A2 Collapse/Expand操作 / モック検証

- Type: Feature request
- Status: Ready (A2 Validation Planned)
- Priority: P0
- Owner: Stream D
- Scope: `01_Plans/issues/` (planning memo only)
- Related Backlog: `FB-P2A-02`
- Related ADR/Spec: `ADR-0007`, `issue-FB-P2A-02-a1-interface-contract.md`
- Expected verification level: `docs-check`

## Requirement meta I/F（共通キー）

- RequirementID: `RQ-2A-02`
- RequirementStatement: A1で固定した `CTR-2A-02-COLLAPSE-EXPAND-V1` / `IslandVisibilityContractV1` をモックで検証する。
- Phase: `A2 Mock Validation`
- PriorityClass: Must
- GoNoGoGate: Required
- VerificationLevel: docs-check
- DecisionStatus: Fixed

## Phase management（Stream D）

- Phase 1: Read同期（A1/A2/A3の3点再読）
- Phase 2: A1契約点検（I/F固定と契約ドリフト検知）
- Phase 3: A2モック検証計画固定（M1..M4・責務分離）
- Phase 4: A3 handoff条件固定（GoNoGoと停止条件）
- Phase 5: Verify（記述整合・依存整合）

## Contract freeze confirmation

- FixedContractRef: `issue-FB-P2A-02-a1-interface-contract.md`
- ContractID: `CTR-2A-02-COLLAPSE-EXPAND-V1`
- ContractVersion: `IslandVisibilityContractV1`
- FreezeRule: A2では Required fields / Invariants を変更しない。
- DriftCheck:
  - ContractLinks（A1→A2→A3）の到達性を維持する。
  - `isCollapsed` / `hiddenDescendantIslandIds` / `hiddenCardIds` の意味を再定義しない。

## Mock validation scope

- 入力モック:
  - M1: 親island collapse（子island + cardsが非表示になる）
  - M2: expand復帰（非表示対象が復元）
  - M3: 二重collapse要求（冪等）
  - M4: 存在しないislandへのcollapse要求（拒否）
- 期待判定:
  - M1/M2/M3は契約適合（pass）。
  - M4はFail Fastで reject する（fail）。

## Fixture / signature plan（実装依存なし）

| fixtureId | fileName | mockCaseId | signature check | expected |
|---|---|---|---|---|
| `F1` | `visibility_collapse_valid.json` | `M1` | `isCollapsed: boolean`, `hidden*Ids: string[]` | pass |
| `F2` | `visibility_expand_restore_valid.json` | `M2` | restore keeps view-only mutation | pass |
| `F3` | `visibility_double_collapse_idempotent.json` | `M3` | idempotent repeated collapse | pass |
| `F4` | `visibility_missing_island_invalid.json` | `M4` | unknown island request reject | fail |

### Signature/data type checks

- `contractId: string`（固定値 `CTR-2A-02-COLLAPSE-EXPAND-V1`）
- `contractVersion: string`（固定値 `IslandVisibilityContractV1`）
- `mockCaseId: string`（`M1`〜`M4`）
- `validationResult: "pass" | "fail"`
- `ownerOfFix: "A1" | "A2" | "A3"`
- `evidence: string`

## Responsibility split（失敗時責務分離）

- 契約修正責務（A1）:
  - `hidden*Ids` 定義不足で期待挙動を一意に決められない。
- モック修正責務（A2）:
  - fixture 前提の不備、データ型の誤り、または判定期待値の誤設定。
- 実装修正責務（A3）:
  - 契約とモックは成立しているが実装引き渡し条件に落ちていない。

## Acceptance criteria

- [x] collapse/expandの正常系・異常系モックが揃う。
- [x] fixture ごとに I/F シグネチャとデータ型の確認項目が明示される。
- [x] 失敗時責務分離ルールが明文化される。
- [x] A3へ渡す検証ログ項目が定義される。

## Execution protocol（Plan→Execute→Verify→Proceed）

1. **Plan**
   - A1契約凍結（`CTR-2A-02-COLLAPSE-EXPAND-V1` / `IslandVisibilityContractV1`）とモックケース（M1〜M4）を対応付ける。
2. **Execute**
   - M1→M2→M3→M4の順に直列検証し、各ケースで`validationResult`と`ownerOfFix`を記録する。
3. **Verify**
   - GoNoGo条件（`M1/M2/M3=pass`, `M4=fail`）および責務分離の確定を確認する。
4. **Proceed**
   - A3 handoff I/Fを満たすログのみ引き渡す。未確定項目があればA2で修復する。

## A2 mock validation plan（Stream D / Phase 3）

- fixture/stub分解（実装依存を分離）:
  - Fixture:
    - F1 `visibility_collapse_valid.json`（M1）
    - F2 `visibility_expand_restore_valid.json`（M2）
    - F3 `visibility_double_collapse_idempotent.json`（M3）
    - F4 `visibility_missing_island_invalid.json`（M4）
  - Stub:
    - S1 `visibility contract projector stub`
    - S2 `collapse/expand invariant evaluator stub`
- 実装依存の明示切り離し:
  - 描画エンジン、state管理実装、UI操作シーケンスには依存しない。
  - 判定軸はA1契約Invariant（表示/ヒットテスト除外、復帰可能、document非破壊）のみ。
- GoNoGo固定:
  - Go: `M1/M2/M3=pass` かつ `M4=fail`。
  - NoGo: 判定不一致、ケース欠損、責務未確定。

## A3 handoff I/F

- Handoff payload:
  - `contractId`
  - `contractVersion`
  - `mockCaseId`
  - `validationResult`
  - `ownerOfFix`
  - `evidence`

## Validation log schema（A3引き継ぎ必須）

| field | type | description |
|---|---|---|
| `contractId` | string | `CTR-2A-02-COLLAPSE-EXPAND-V1` 固定値 |
| `contractVersion` | string | `IslandVisibilityContractV1` 固定値 |
| `mockCaseId` | enum(`M1`,`M2`,`M3`,`M4`) | モックケースID |
| `validationResult` | enum(`pass`,`fail`) | モック判定結果 |
| `ownerOfFix` | enum(`A1`,`A2`,`A3`) | 失敗時の修正責務 |
| `evidence` | string | 判定根拠（表示/非表示・冪等・拒否） |

## A2 validation ledger（契約監査結果）

| contractId | contractVersion | mockCaseId | validationResult | ownerOfFix | evidence |
|---|---|---|---|---|---|
| `CTR-2A-02-COLLAPSE-EXPAND-V1` | `IslandVisibilityContractV1` | `M1` | `pass` | `A3` | collapse hides descendants and cards |
| `CTR-2A-02-COLLAPSE-EXPAND-V1` | `IslandVisibilityContractV1` | `M2` | `pass` | `A3` | expand restores `hiddenDescendantIslandIds` / `hiddenCardIds` |
| `CTR-2A-02-COLLAPSE-EXPAND-V1` | `IslandVisibilityContractV1` | `M3` | `pass` | `A3` | double collapse remains idempotent |
| `CTR-2A-02-COLLAPSE-EXPAND-V1` | `IslandVisibilityContractV1` | `M4` | `fail` | `A2` | fail-fast on unknown `island.id` request |

- GoNoGo result: **Go**（`M1/M2/M3=pass` かつ `M4=fail`）
- Owner routing check: pass casesは`A3`、fail case（M4）は`A2`で固定。

## State sync / conflict check

- Phase開始時Read対象:
  - `issue-FB-P2A-02-a1-interface-contract.md`
  - `issue-FB-P2A-02-a2-mock-validation.md`
  - `issue-FB-P2A-02-a3-implementation.md`
- Rule:
  - Phase開始ごとに上記3ファイルを再Readし、差分競合がある場合は推測継続せず停止・報告する。

## Validation plan

- Command:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`

## Fail-safe

- self-correction上限: 3回。連続失敗時はProceed禁止で停止。
- 停止トリガ: Ready条件崩壊 / 依存逆転 / 未定義競合 / ContractID不一致を検出した場合は即時停止して報告。
