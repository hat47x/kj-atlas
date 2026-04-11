# Issue Draft: FB-P2A-01-A3 Island階層モデル導入 / 実装計画接続

- Type: Feature request
- Status: Ready (A3 Handoff Condition Fixed)
- Priority: P0
- Owner: Stream D
- Scope: `01_Plans/issues/` (planning memo only)
- Related Backlog: `FB-P2A-01`
- Related ADR/Spec: `ADR-0007`, `issue-FB-P2A-01-a1-interface-contract.md`, `issue-FB-P2A-01-a2-mock-validation.md`
- Expected verification level: `docs-check`

## Requirement meta I/F（共通キー）

- RequirementID: `RQ-2A-01`
- RequirementStatement: A1/A2契約を逸脱せず、実装者向け引き渡し条件を固定する。
- Phase: `A3 Implementation`
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

## A3 implementation connection guard（Stream D / Phase 4）

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

## Validation plan

- Command:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`

## Fail-safe

- self-correction上限: 3回。連続失敗時はProceed禁止で停止。
- 停止トリガ: Ready条件崩壊 / 依存逆転 / 未定義競合 / ContractID不一致を検出した場合は即時停止して報告。

## Stream D one-page handoff（Phase 5）

- 固定I/F（Fixed Interface）:
  - `contractId`,`contractVersion`,`mockCaseId`,`validationResult`,`ownerOfFix`,`evidence`
  - ContractLock: `CTR-2A-01-ISLAND-HIERARCHY-V1` / `IslandHierarchyContractV1`
- 許容差分（Allowed Delta）:
  - A3内の実装順序・検証順序・タスク粒度の調整（契約語彙と判定を変えない範囲）。
- 禁止変更（Forbidden Changes）:
  - A1 Required fields / Invariants / ContractLinks の改変。
  - GoNoGo条件（`M1/M2/M3=pass`, `M4=fail`）の変更。
  - SafeMode/share-export既定挙動を変更する差分。

## Stream I normalization ledger（Phase 1-6 / Plan→Execute→Verify→Proceed）

### Phase 1 Read
- Plan: Status / Scope / DecisionStatus / Validation plan を抽出し、A1/A2/A3粒度を点検する。
- Execute:
  - Status: 既存本文の宣言値を採用。
  - Scope: `Implementation Handoff` に限定。
  - DecisionStatus: `Fixed`。
  - Validation command: `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`。
- Verify: 抽出項目が本メモ内で相互矛盾しないことを確認。
- Proceed: 矛盾がなければ Phase 2 へ進む。

### Phase 2 Plan
- Plan: AC/DoD不足の有無を点検し、不足時はドラフト提案I/Fで合意前提にする。
- Execute: 依存は `A1/A2 payload only` のみ許可し、実装ストリーム依存は mock I/F へ切り離す。
- Verify: 待ち依存が「契約未固定」「責務未確定」に限定されることを確認。
- Proceed: 依存最小化が成立した場合のみ次Phaseへ進行。

### Phase 3 ADR CDC明文化
- Plan: ADR追加を行わず、Issue本文の Context / Decision / Consequences を判定根拠の正本にする。
- Execute:
  - Context: 上位ADR/Spec整合の範囲内で計画を固定。
  - Decision: 契約順序を `A1 -> A2 -> A3` に固定。
  - Consequences: 逸脱要求はA1差し戻し。
- Verify: 新規アーキ判断がないこと（ADR追加不要）を確認。
- Proceed: CDC固定済みとしてPhase 4へ進む。

### Phase 4 Execute
- Plan: Contract / Mock / Implementation の責務境界を再確認する。
- Execute:
  - Contract: A1固定値を変更しない。
  - Mock: A2は fixture/stub と判定ログで閉じる。
  - Implementation: A3は handoff payload の受領判定のみ扱う。
- Verify: 競合しやすい共有ファイル編集要求を含まないことを確認。
- Proceed: 境界維持が確認できたらPhase 5へ進む。

### Phase 5 Verify
- Plan: docs-check、必須メタ、参照整合を検証する。
- Execute: `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` を単一検証コマンドとして実行する。
- Verify: 失敗時は自己修復を最大3回まで実施し、超過時は停止する。
- Proceed: 検証成功時のみ Ready 判定へ進む。

### Phase 6 Proceed
- Plan: Ready化可能項目と保留項目を分離する。
- Execute:
  - Ready条件: ContractID整合・依存順序整合・停止条件明記。
  - 保留条件: 未定義競合 / AC合意未完了 / Gate未承認。
- Verify: 保留項目に stop condition と再開条件を必ず併記する。
- Proceed:
  - Ready: 実装ストリームへ引き渡し可。
  - Hold: `stop condition` 解消後に同Phaseから再開。

