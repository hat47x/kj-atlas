# Issue Draft: FB-P2A-02-A3 Implementation Plan（Stream E / FB-P2*）

- Type: Planning
- Status: Done
- Priority: P2
- Owner: Stream E
- Scope: `01_Plans/issues/` only
- Phase: A3 Implementation Plan

## Plan → Execute → Verify → Proceed
- Plan: A2合格を着手条件として実装手順を小粒度化する。
- Execute: 実装Stream向けに競合候補ファイルとハンドオフを定義する。
- Verify: A1/A2依存を満たすことを確認する。
- Proceed: shared resource更新は依頼のみ（自編集禁止）でクローズする。

## Dependencies
- DependsOn:
  - `issue-FB-P2A-02-a1-interface-contract.md`
  - `issue-FB-P2A-02-a2-mock-validation.md`
- Entry condition: A2 `MV-01..04` pass
- NoGo: A2未達 / 契約ID不一致 / 未確定項目再発

## Implementation steps (for downstream stream)
1. 契約型の受け口を追加（A1 ContractID準拠）
2. 必須キー検証とエラーコード写像を実装
3. 監査イベント4点を実装
4. A2最小ケースの自動テストを接続
5. 回帰確認後にhandoff完了

## Potential conflict file candidates（列挙のみ・本Streamでは未編集）
- `03_Implement/frontend/src/domain/**`
- `03_Implement/backend/src/kj_atlas_api/routes/**`
- `03_Implement/backend/src/kj_atlas_api/models*.py`
- `03_Implement/frontend/tests/**`
- `03_Implement/backend/tests/**`

## Handoff package to implementation stream
- `contractId: CTR-FB-P2A-02-V1`
- `mockValidationResult: pass|fail`
- `evidence: string`
- `requiredAuditEvents: [4 names fixed in A1]`
- `rollbackTriggers: [contract_mismatch, missing_required_key, invariant_violation, audit_missing]`

## Acceptance Criteria
- [x] A2合格をA3着手条件として明記。
- [x] 実装ステップを小粒度で定義。
- [x] 競合しうる実装ファイル候補を列挙。
- [x] 実装Stream向けハンドオフを記録。

## Definition of Done
- [x] A1/A2/A3依存順が崩れていない。
- [x] shared resourceの直接編集を行っていない。
- [x] 本Streamが03_Implement実コードに非干渉である。


## Stream H classification（2026-06-13）

- Phase: A3 Implementation Plan.
- Classification: Hold for implementation stream: this memo is an implementation plan only, not permission for Stream H to edit code.
- Mock-first dependency handling: Dependency is cut by A1+A2; implementation may start only in a downstream stream after A2 pass evidence.
- Scope lock: Stream H does not edit `03_Implement/`, shared architecture files, or documentation; conflict-prone files remain handoff candidates only.
- Stop condition: contract mismatch, missing A2 mock evidence, SafeMode default weakening, or any request to start implementation inside this planning stream.
