# Issue Draft: FB-P2A-02-A3 Collapse/Expand操作 / 実装計画接続

- Type: Feature request
- Status: Open (Audit Hold: normalized contract pack; resumable by explicit Go/NoGo)
- Priority: P0
- Owner: Stream G（FB-P2A planning memo exclusive）
- Scope: `01_Plans/issues/` (planning memo only)
- Related Backlog: `FB-P2A-02`
- Related ADR/Spec: `ADR-0007`, `issue-FB-P2A-02-a1-interface-contract.md`, `issue-FB-P2A-02-a2-mock-validation.md`
- Expected verification level: `docs-check`

## Dependencies

- DependsOn: `01_Plans/issues/issue-FB-P2A-02-a1-interface-contract.md` / `01_Plans/issues/issue-FB-P2A-02-a2-mock-validation.md`
- Unblocks: downstream implementation lane only（no contract re-definition）
- Gate/Blocker: Ready when A1 contract lock + A2 validation ledger are complete; Blocked on contract mismatch, missing mockCase, or unresolved ownerOfFix.
## Requirement meta I/F（共通キー）

- RequirementID: `RQ-2A-02`
- RequirementStatement: A1/A2契約を逸脱せず、Collapse/Expand実装者向け引き渡し条件を固定する。
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
   - `isCollapsed` と `hidden*Ids` の更新責務を実装者向け入力契約へ分離して作業計画化。
2. **Execute**
   - `state transition -> render filter -> hit-test filter` の順で設計反映。
3. **Verify**
   - A2 mockCaseを使って遷移前後の整合をチェック。
4. **Proceed**
   - GoNoGoを満たした観点のみ次タスクへ進行。
   - 次タスク開始時はA1/A2/A3の3ファイルを再Readしてから着手する。

## Non-deviation rules

- A1契約をA3で再解釈しない。
- A2 Failケースを未解決のまま先送りしない。
- AC/DoD不足を検知した場合は、先にドラフト提案を追記して合意後に進行する。
- 実装コード・ファイルパス・関数名をA3契約本文へ持ち込まない。

## A2→A3 接続条件（確定）

- ContractLock:
  - `contractId=CTR-2A-02-COLLAPSE-EXPAND-V1`
  - `contractVersion=IslandVisibilityContractV1`
- Required input from A2:
  - `contractId=CTR-2A-02-COLLAPSE-EXPAND-V1`
  - `contractVersion=IslandVisibilityContractV1`
  - `mockCaseId in {M1,M2,M3,M4}`
  - `validationResult`
  - `ownerOfFix`
  - `evidence`
- GoNoGo判定:
  - Go: `M1/M2/M3=pass` かつ `M4=fail`、責務が確定。
  - NoGo: 判定不一致、または責務未確定。

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

- [x] A1/A2契約IDで実装計画トレースが可能。
- [x] Plan→Execute→Verify→Proceedの順序が固定される。
- [x] 実装者向けの入力契約 / 期待出力 / ロールバック条件が固定されている。
- [x] AC/DoD不足時のドラフト提案手順が明文化される。

## AC/DoD不足の事前提案I/F（合意前提）

- Required fields:
  - `gapId`
  - `gapType`（`AC` / `DoD`）
  - `phaseDetected`（`A1` / `A2` / `A3`）
  - `proposalDelta`
  - `agreementStatus`（`pending` / `agreed` / `rejected`）
- Proceed rule:
  - `agreementStatus=agreed` 以外はNoGo。

## Serial execution gate（A1→A2→A3）

- A3開始条件:
  - A2 handoff payload（`contractId`,`contractVersion`,`mockCaseId`,`validationResult`,`ownerOfFix`,`evidence`）が全件揃っている。
- A3停止条件:
  - 未定義競合を検出した場合は推測継続禁止、停止・報告。
- Self-repair上限:
  - 自己修復は最大3回。超過時は作業停止して報告。

## 実装トレース最小単位

| traceKey | source | destination |
|---|---|---|
| `RQ-2A-02` | A1 RequirementID | A3 task grouping key |
| `CTR-2A-02-COLLAPSE-EXPAND-V1` | A1 ContractID | A3 contract lock |
| `M1..M4` | A2 mockCaseId | A3 verification checklist |
| `ownerOfFix` | A2 failure routing | A3 backlog split (A1/A2/A3) |

## A3 implementation connection guard（Stream B / Phase 4）

- 着手条件（Start）:
  - `IslandVisibilityContractV1` がA1で固定され、A2ログがM1〜M4全件で存在する。
  - handoff I/F（`contractId`,`contractVersion`,`mockCaseId`,`validationResult`,`ownerOfFix`,`evidence`）に欠損なし。
- 停止条件（Stop）:
  - `M1/M2/M3=pass` かつ `M4=fail` が崩れた場合。
  - `ownerOfFix` がA2責務分離と矛盾した場合。
  - AC/DoD不足で `agreementStatus=agreed` が未達の場合。
- ロールバック条件（Rollback）:
  - A3で追加した前提・タスク分割を破棄し、A2確定ログを唯一の入力へ戻す。
  - 契約I/F変更要求はA1へ差し戻し、A3での再解釈を禁止する。

## State sync / conflict check

- Phase開始時Read対象:
  - `issue-FB-P2A-02-a1-interface-contract.md`
  - `issue-FB-P2A-02-a2-mock-validation.md`
  - `issue-FB-P2A-02-a3-implementation.md`
- Rule:
  - Phase開始ごとに上記3ファイルを再Readし、差分競合がある場合は推測継続せず停止・報告する。


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
- Self-correction は最大3回までとし、**4回目に入る前に停止・報告**する。

## Unified execution rule lock（同一ルール固定）

- strict serial: A1→A2→A3 の直列のみ許可（並列禁止）。
- CDC必須: Contract Definition Checklist（C1/C2/C3）とA1固定契約値の一致確認を必須化する。
- 各Phase開始Read: Phase開始時に A1/A2/A3 の3ファイルを再Readする。
- self-correction: 最大3回。4回目相当は停止して指示待ち。

## Validation plan

- Command:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`

## Fail-safe

- self-correction上限: 3回。
- 停止トリガ: 3回超過 / 依存不整合 / 指定外ファイル更新が必要 / ContractID衝突。
- 停止時対応: 推測継続を禁止し、停止理由と再開条件を記録して指示待ち。
