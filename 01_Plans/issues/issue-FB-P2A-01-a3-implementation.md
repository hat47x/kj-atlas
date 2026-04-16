# Issue Draft: FB-P2A-01-A3 Island階層モデル導入 / 実装計画接続

- Type: Feature request
- Status: Open (Audit Hold: normalized contract pack; resumable by explicit Go/NoGo)
- Priority: P0
- Owner: Stream G（FB-P2A planning memo exclusive）
- Scope: `01_Plans/issues/` (planning memo only)
- Related Backlog: `FB-P2A-01`
- Related ADR/Spec: `ADR-0007`, `issue-FB-P2A-01-a1-interface-contract.md`, `issue-FB-P2A-01-a2-mock-validation.md`
- Expected verification level: `docs-check`

## Dependencies

- DependsOn: `01_Plans/issues/issue-FB-P2A-01-a1-interface-contract.md` / `01_Plans/issues/issue-FB-P2A-01-a2-mock-validation.md`
- Unblocks: downstream implementation lane only（no contract re-definition）
- Gate/Blocker: Ready when A1 contract lock + A2 validation ledger are complete; Blocked on contract mismatch, missing mockCase, or unresolved ownerOfFix.
## Requirement meta I/F（共通キー）

- RequirementID: `RQ-2A-01`
- RequirementStatement: A1/A2契約を逸脱せず、実装者向け引き渡し条件を固定する。
- Phase: `A3 Implementation`
- PriorityClass: Must
- GoNoGoGate: Required
- VerificationLevel: docs-check
- DecisionStatus: Fixed

## Phase management（Stream G）

- Phase 1: Read同期（A1/A2/A3の3点再読）
- Phase 2: A1契約明確化（CDC明文化）
- Phase 3: A2モック検証計画更新（M1..M4・責務分離）
- Phase 4: A3実装準備条件定義（GoNoGoと停止条件）
- Phase 5: Verify（記述整合・依存整合）

## Execution protocol（Plan→Execute→Verify→Proceed）

1. **Plan**
   - A1必須項目とA2検証結果を実装者向け入力契約へマッピングする。
2. **Execute**
   - 変更順を `schema compatibility -> normalization -> persistence roundtrip` で固定する。
3. **Verify**
   - A2 handoff payloadの各ケースを実装観点で再照合する。
4. **Proceed**
   - GoNoGo判定を満たした項目のみ次タスクへ進める。

## Non-deviation rules

- A1のRequired fields/InvariantsをA3で再定義しない。
- A2でFailとなったケースを未解決のまま「既知課題」扱いで先送りしない。
- AC/DoD不足を検知した場合は、先にドラフト提案を追記してから進行する。
- 実装コード・ファイルパス・関数名をA3契約本文へ持ち込まない。

## A2→A3 接続条件（確定）

- ContractLock:
  - `contractId=CTR-2A-01-ISLAND-HIERARCHY-V1`
  - `contractVersion=IslandHierarchyContractV1`
- Required input from A2:
  - `contractId=CTR-2A-01-ISLAND-HIERARCHY-V1`
  - `contractVersion=IslandHierarchyContractV1`
  - `mockCaseId in {M1,M2,M3,M4}`
  - `validationResult`
  - `ownerOfFix`
  - `evidence`
- GoNoGo判定:
  - Go: `M1/M2/M3=pass` かつ `M4=fail` で責務が確定している。
  - NoGo: 上記を満たさない、または責務未確定。

## Implementation handoff contract（実装者向け固定条件）

### Input contract

- `contractId: string`
- `contractVersion: string`
- `mockCaseId: "M1" | "M2" | "M3" | "M4"`
- `validationResult: "pass" | "fail"`
- `ownerOfFix: "A1" | "A2" | "A3"`
- `evidence: string`

### Expected output

- `implementationReadiness: "go" | "no-go"`
- `acceptedMockCases: string[]`
- `blockedMockCases: string[]`
- `rollbackTrigger: string[]`
- `notes: string[]`

### Rollback conditions

- `contractId` または `contractVersion` がA1固定値と不一致。
- `mockCaseId` が欠損・重複・未知値を含む。
- `M1/M2/M3=pass` または `M4=fail` のGoNoGo条件が崩れる。
- `ownerOfFix` が未確定、または責務分離ルールと矛盾する。

## Acceptance criteria

- [x] A1/A2の ContractID・ケースIDを使って実装計画へトレース可能。
- [x] Plan→Execute→Verify→Proceedがチェックリスト化されている。
- [x] 実装者向けの入力契約 / 期待出力 / ロールバック条件が固定されている。
- [x] AC/DoD不足のドラフト提案手順が明文化されている。

## Phase execution log（A3）

### Read sync（Phase開始時）

- `issue-FB-P2A-01-a1-interface-contract.md`
- `issue-FB-P2A-01-a2-mock-validation.md`
- `issue-FB-P2A-01-a3-implementation.md`

### Plan

- A1契約IDとA2ケースIDを実装タスクへトレース可能にマッピングする。
- GoNoGo判定条件（M1/M2/M3 pass, M4 fail, owner確定）を前提条件として固定する。

### Execute

- 実装順序を `schema compatibility -> normalization -> persistence roundtrip` で維持する。
- A2の handoff payload を実装チェックリストへ転写する。

### Verify

- `contractId=CTR-2A-01-ISLAND-HIERARCHY-V1` / `contractVersion=IslandHierarchyContractV1` を契約ロックとして再確認する。
- `ownerOfFix` 未確定ケースが残っていないことを検証する。

### Proceed

- Go判定成立時のみ次タスクへ進行し、NoGo時はA1/A2/A3責務へ即時返却する。

## 実装トレース最小単位

| traceKey | source | destination |
|---|---|---|
| `RQ-2A-01` | A1 RequirementID | A3 task grouping key |
| `CTR-2A-01-ISLAND-HIERARCHY-V1` | A1 ContractID | A3 contract lock |
| `M1..M4` | A2 mockCaseId | A3 verification checklist |
| `ownerOfFix` | A2 failure routing | A3 backlog split (A1/A2/A3) |

## A3 implementation connection guard（Stream B / Phase 4）

- 着手条件（Start）:
  - A1契約ロックが有効。
  - A2 handoff payload（`contractId`,`contractVersion`,`mockCaseId`,`validationResult`,`ownerOfFix`,`evidence`）が M1〜M4 で全件揃う。
- 停止条件（Stop）:
  - `contractId` / `contractVersion` 不一致、mockCase 重複/欠損、`ownerOfFix`未確定を検出した場合は推測継続せず停止。
  - AC/DoD不足が検出され、`agreementStatus=agreed` になる前。
- ロールバック条件（Rollback）:
  - GoNoGo不成立時はA3側の追加前提を破棄し、A2責務分離結果へ巻き戻す。
  - 契約ドリフト検出時はA1固定契約へ差し戻し、A3で契約再定義しない。

## State sync / conflict check

- Phase開始時Read対象:
  - `issue-FB-P2A-01-a1-interface-contract.md`
  - `issue-FB-P2A-01-a2-mock-validation.md`
  - `issue-FB-P2A-01-a3-implementation.md`


## Stream G strict serial protocol（Phase 1→5）

### Phase 1 Read
- 対象ファイル（A1/A2/A3の3点）を**Phase開始時に必ず再Read**する。
- 照合項目: `Status` / `Priority(P0)` / `DecisionStatus` / `ContractID(またはDependsOnContractID)`。
- 不足監査: AC/DoD/停止条件/handoff条件。

### Phase 2 A1契約明確化（CDC明文化）
- Plan: A1契約（ContractID / Required fields / Invariants / ContractLinks）を**read-only参照**で固定対象として再確認する。
- Execute: 契約本文の再定義は行わず、固定I/Fの一致確認のみ実施する。
- Verify: A1→A2→A3依存の逆転・並列前提・契約ドリフトがないことを確認する。
- Proceed: A1固定が崩れた場合は停止し、A1へ差し戻す（契約値の推測補完は禁止）。

### Phase 3 A2モック検証計画更新
- Plan: M1..M4（正常/異常）と責務分離（A1/A2/A3）を再確認する。
- Execute: handoff payload（`contractId`,`contractVersion`,`mockCaseId`,`validationResult`,`ownerOfFix`,`evidence`）を固定入力として扱う。
- Verify: GoNoGo条件（`M1/M2/M3=pass` かつ `M4=fail`）の整合を確認する。
- Proceed: 判定不一致または責務未確定時は停止し、Decision Queueへ返却してA2へ差し戻す。

### Phase 4 A3実装準備条件定義
- Plan: 実装入口は契約参照のみで開始できる条件を確認する。
- Execute: Plan→Execute→Verify→Proceed を固定順序で適用し、実装先行を禁止する。
- Verify: AC/DoD不足を検知した場合は `gapType` と `agreementStatus` を用いたドラフト提案を先行し、`agreementStatus=agreed` まで実行しない。
- Proceed: 合意済み条件と停止条件が同時に満たされる場合のみ下流へ引き渡し、未解決はDecision Queueへ返却する。

### Phase 5 Verify
- docs-check: `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- 依存参照整合・表記ゆれ・契約ID衝突を確認する。
- Self-Correction は最大3回。4回目相当は**停止して指示待ち**とする。


## Stream G lane guard（FB-P2A only）

- 編集対象は FB-P2A A2/A3 issue のみ（A1/CE/HIL/03_Implement は対象外）。
- Plan→Execute→Verify→Proceed の順序を固定し、順序逆転時は停止する。
- A1契約値は read-only 参照のみ。未定義値を推測で補完しない。
- モック前提で依存を切断し、実装依存（renderer/state管理/関数名）を持ち込まない。
- 未解決・責務未確定は Proceed せず Decision Queue へ返却する。

## Stream G execution override（FB-P2A A1→A2→A3）

- 同一レーン内依存は A1→A2→A3 の**直列処理のみ**を許可する。
- 外部レーン完了待ちは禁止し、依存解決は当該レーン内で閉じる。
- 各 Phase 開始時に A1/A2/A3 の3ファイルを再Readしてから着手する。
- 実行順序は **Plan→Execute→Verify→Proceed** を固定し、順序逆転時は停止する。
- Self-correction は最大3回とし、3回失敗で停止・報告する。

## Validation plan

- Command:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`

## Fail-safe

- self-correction上限: 3回。
- 停止トリガ: 3回超過 / 依存不整合 / 指定外ファイル更新が必要 / ContractID衝突。
- 停止時対応: 推測継続を禁止し、停止理由と再開条件を記録して指示待ち。
