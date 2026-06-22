# Issue Draft: FB-P2C-01-A2 Mock Validation（Stream E / FB-P2*）

- Type: Planning
- Status: Done
- Priority: P2
- Owner: Stream E
- Scope: `01_Plans/issues/` only
- Phase: A2 Mock Validation
- DecisionStatus: Fixed
- VerificationLevel: docs-check

## Plan → Execute → Verify → Proceed
- Plan: A1契約 (`CTR-FB-P2C-01-V1`) への適合性をモックで検証する。
- Execute: 成功系/異常系/必須キー欠落系の最小ケースを定義する。
- Verify: 型整合・必須キー・異常系・監査イベントをAC化し判定する。
- Proceed: A3着手条件（A2 pass）を記録する。

## Dependencies
- DependsOn: `issue-FB-P2C-01-a1-interface-contract.md`
- Unblocks: `issue-FB-P2C-01-a3-implementation.md`
- Gate: A1 `DecisionStatus=Fixed`

## Mock Validation Contract
- ContractID: `CTR-FB-P2C-01-V1`
- Required mock checks:
  1. Type conformity（input/output shape）
  2. Required key presence（`requestId/documentId/payload/safeMode`）
  3. Error mapping（`MISSING_REQUIRED_KEY` / `INVARIANT_VIOLATION`）
  4. Audit event emission（A1固定4イベント名）

## Minimal test set (implementation-agnostic)
- `MV-01`: valid request -> `status="ok"`
- `MV-02`: missing required key -> `status="error"` + `MISSING_REQUIRED_KEY`
- `MV-03`: invariant break -> `status="error"` + `INVARIANT_VIOLATION`
- `MV-04`: verify audit event names exactly match A1 fixed set

## Acceptance Criteria
- [x] 契約適合（型整合・必須キー・異常系）を最小テストで定義。
- [x] A1契約値を変更しない。
- [x] A3入力に必要な検証結果キーを固定。

## Definition of Done
- [x] A2 pass criteria を明文化（MV-01..04）。
- [x] A3への handoff keys を固定（`mockCaseId/result/evidence`）。
- [x] 失敗時の差戻し先を定義（A1=契約不備、A2=モック不備）。


## Stream H classification（2026-06-13）

- Phase: A2 Mock Validation.
- Classification: Open-ready / Done: mock dataset/checks cover success, missing-key, invariant/error mapping, and audit-event-name verification.
- Mock-first dependency handling: Dependency is mock-first; A3 remains blocked if A2 evidence is absent or contract ID mismatches.
- Scope lock: Stream H does not edit `03_Implement/`, shared architecture files, or documentation; conflict-prone files remain handoff candidates only.
- Stop condition: contract mismatch, missing A2 mock evidence, SafeMode default weakening, or any request to start implementation inside this planning stream.
