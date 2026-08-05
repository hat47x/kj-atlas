# Issue Draft: FB-P2C-01-A1 Interface Contract（Stream E / FB-P2*）

- Type: Planning
- Status: Done
- Priority: P2
- Owner: Stream E
- Scope: `01_Plans/issues/` only
- Phase: A1 Interface Contract

## Dependencies
- DependsOn: N/A
- Unblocks: `issue-FB-P2C-01-a2-mock-validation.md`, `issue-FB-P2C-01-a3-implementation.md`
- Gate: N/A


## Plan → Execute → Verify → Proceed
- Plan: A1として入力型・出力型・エラー契約・監査イベント名を固定する。
- Execute: A2/A3がモック可能な最小I/Fに限定して契約化する。
- Verify: A1未確定項目ゼロを確認する。
- Proceed: A2へ進行可否を判定する。

## Dependency Matrix（A1→A2→A3）
- DependsOn: none（A1 root）
- Unblocks: `issue-FB-P2C-01-a2-mock-validation.md`
- Blocked when: `DecisionStatus != Fixed`

## Interface Contract（Fixed）
- ContractID: `CTR-FB-P2C-01-V1`
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
  - `audit.fb-p2c-01.request_received`
  - `audit.fb-p2c-01.validation_passed`
  - `audit.fb-p2c-01.validation_failed`
  - `audit.fb-p2c-01.handoff_emitted`

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


## Stream H classification（2026-06-13）

- Phase: A1 Interface Contract.
- Classification: Open-ready / Done: I/F signature, inputs, outputs, errors, audit events, and AC are fixed; A2 may proceed without implementation files.
- Mock-first dependency handling: Dependency is cut at the contract boundary; downstream work must not alter A1 without reopening this memo.
- Scope lock: Stream H does not edit `03_Implement/`, shared architecture files, or documentation; conflict-prone files remain handoff candidates only.
- Stop condition: contract mismatch, missing A2 mock evidence, SafeMode default weakening, or any request to start implementation inside this planning stream.
