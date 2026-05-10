# Issue Draft: FB-P2B-02-A1 Interface Contract（Stream E / FB-P2*）

- Type: Planning
- Status: Done
- Owner: Stream E
- Scope: `01_Plans/issues/` only
- Phase: A1 Interface Contract
- DecisionStatus: Fixed
- VerificationLevel: docs-check

## Plan → Execute → Verify → Proceed
- Plan: A1として入力型・出力型・エラー契約・監査イベント名を固定する。
- Execute: A2/A3がモック可能な最小I/Fに限定して契約化する。
- Verify: A1未確定項目ゼロを確認する。
- Proceed: A2へ進行可否を判定する。

## Dependency Matrix（A1→A2→A3）
- DependsOn: none（A1 root）
- Unblocks: `issue-FB-P2B-02-a2-mock-validation.md`
- Blocked when: `DecisionStatus != Fixed`

## Interface Contract（Fixed）
- ContractID: `CTR-FB-P2B-02-V1`
- InputType:
  - `requestId: string`
  - `documentId: string`
  - `payload: object`
  - `safeMode: boolean`（default true）
- OutputType:
  - `status: "ok" | "error"`
  - `result: object | null`
  - `errors: ContractError[]`
- ContractError:
  - `code: "INVALID_INPUT" | "MISSING_REQUIRED_KEY" | "INVARIANT_VIOLATION" | "UNAUTHORIZED_TRANSITION"`
  - `message: string`
  - `fieldPath?: string`
- AuditEvents（fixed names）:
  - `audit.fb-p2b-02.request_received`
  - `audit.fb-p2b-02.validation_passed`
  - `audit.fb-p2b-02.validation_failed`
  - `audit.fb-p2b-02.handoff_emitted`

## Contract uncertainty resolved in A1
- 必須キー集合: fixed
- 異常系コード体系: fixed
- 監査イベント命名: fixed
- A2 mock point: 入出力shape/required-key/error-code/event-name のみ検証（実装非依存）

## Acceptance Criteria
- [x] 入力型・出力型・エラー契約・監査イベント名が固定されている。
- [x] A2/A3がA1参照のみで進行可能。
- [x] safeMode既定ONを弱めない。

## Definition of Done
- [x] `ContractID` と `DecisionStatus=Fixed` を記録。
- [x] 依存順 `A1 -> A2 -> A3` を明示。
- [x] A1未確定項目ゼロ。
