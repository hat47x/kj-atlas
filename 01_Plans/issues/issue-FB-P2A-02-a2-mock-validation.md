# Issue Draft: FB-P2A-02-A2 Collapse/Expand操作 / モック検証

- Type: Feature request
- Status: Ready (A2 Validation Planned)
- Priority: P0
- Owner: Stream F
- Scope: `01_Plans/issues/` (planning memo only)
- Related Backlog: `FB-P2A-02`
- Related ADR/Spec: `ADR-0007`, `issue-FB-P2A-02-a1-interface-contract.md`
- Expected verification level: `integration`

## Requirement meta I/F（共通キー）

- RequirementID: `RQ-2A-02`
- RequirementStatement: A1で固定した `IslandVisibilityContractV1` をモックで検証する。
- Phase: `A2 Mock Validation`
- PriorityClass: Must
- GoNoGoGate: Required
- VerificationLevel: integration
- DecisionStatus: Fixed

## Mock validation scope

- 入力モック:
  - M1: 親island collapse（子island + cardsが非表示になる）
  - M2: expand復帰（非表示対象が復元）
  - M3: 二重collapse要求（冪等）
  - M4: 存在しないislandへのcollapse要求（拒否）
- 期待判定:
  - M1/M2/M3は契約適合。
  - M4はFail Fastで拒否。

## Responsibility split（失敗時責務分離）

- 契約修正責務（A1）:
  - `hidden*Ids` 定義不足で期待挙動を一意に決められない。
- モック修正責務（A2）:
  - モック前提の不備、または判定期待値の誤設定。
- 実装修正責務（A3）:
  - 契約とモックは成立しているが実装計画に落ちていない。

## Acceptance criteria

- [x] collapse/expandの正常系・異常系モックが揃う。
- [x] 失敗時責務分離ルールが明文化される。
- [x] A3へ渡す検証ログ項目が定義される。

## Execution protocol（Plan→Execute→Verify→Proceed）

1. **Plan**
   - A1契約凍結（`IslandVisibilityContractV1`）とモックケース（M1〜M4）を対応付ける。
2. **Execute**
   - M1→M2→M3→M4の順に直列検証し、各ケースで`validationResult`と`ownerOfFix`を記録する。
3. **Verify**
   - GoNoGo条件（`M1/M2/M3=pass`, `M4=fail`）および責務分離の確定を確認する。
4. **Proceed**
   - A3 handoff I/Fを満たすログのみ引き渡す。未確定項目があればA2で修復する。

## AC/DoD不足の事前提案（合意前提）

- Trigger:
  - 判定根拠（`evidence`）が不十分でA3へ引き継げない場合。
- Proposal template:
  - `gapId`
  - `blockingMockCaseId`
  - `proposalDelta`
  - `expectedImpact(A1/A2/A3)`
  - `agreementStatus`（`pending` / `agreed` / `rejected`）
- Rule:
  - `agreementStatus=agreed` になるまでA3へProceedしない。

## Serial execution gate（A1→A2→A3）

- A2開始条件:
  - A1契約が凍結済みでContractLinks到達性が有効。
- A2完了条件:
  - M1〜M4の`validationResult`と`ownerOfFix`が確定。
- A2 Proceed条件:
  - A3 handoff I/Fの必須項目が欠損なし。

## A3 handoff I/F

- Handoff payload:
  - `contractVersion`
  - `mockCaseId`
  - `validationResult`
  - `ownerOfFix`


## Contract freeze confirmation

- FixedContractRef: `issue-FB-P2A-02-a1-interface-contract.md#contract-definitiona1成果物`
- FreezeRule: A2では `IslandVisibilityContractV1` のRequired fields / Invariantsを変更しない。
- DriftCheck:
  - ContractLinks（A1→A2→A3）の到達性を維持する。
  - `isCollapsed` / `hiddenDescendantIslandIds` / `hiddenCardIds` の意味を再定義しない。

## Validation log schema（A3引き継ぎ必須）

| field | type | description |
|---|---|---|
| `contractVersion` | string | `IslandVisibilityContractV1` 固定値 |
| `mockCaseId` | string | `M1`〜`M4` |
| `validationResult` | enum(`pass`,`fail`) | モック判定結果 |
| `ownerOfFix` | enum(`A1`,`A2`,`A3`) | 失敗時の修正責務 |
| `evidence` | string | 判定根拠（表示/非表示・冪等・拒否） |

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

- 自己修復が3回連続で失敗、またはA1契約リンク切れを検出した場合は停止して指示待ち。


## A2 validation execution log（Stream C）

| contractVersion | mockCaseId | validationResult | ownerOfFix | evidence |
|---|---|---|---|---|
| IslandVisibilityContractV1 | M1 | pass | A3 | collapse hides descendants and cards |
| IslandVisibilityContractV1 | M2 | pass | A3 | expand restores hiddenDescendantIslandIds/hiddenCardIds |
| IslandVisibilityContractV1 | M3 | pass | A3 | double collapse remains idempotent |
| IslandVisibilityContractV1 | M4 | fail | A2 | fail-fast on invalid island.id (required) |

- GoNoGo result: **Go**（`M1/M2/M3=pass` かつ `M4=fail`）
- Owner routing check: pass casesは`A3`、fail case（M4）は`A2`で固定。
