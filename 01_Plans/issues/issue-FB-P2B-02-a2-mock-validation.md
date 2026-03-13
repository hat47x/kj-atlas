# Issue Draft: FB-P2B-02-A2 Manual assisted mergeフロー / モック検証

- Type: Feature request
- Status: Open
- Source Issue: N/A (GitHub Issues are not used in current operations)
- Priority: P0
- Owner: Stream B
- Scope: `01_Plans/issues/` (planning memo only)
- Related Backlog: `FB-P2B-02`
- Related ADR/Spec: `ADR-0007`, `ADR-0001`
- Expected verification level: `integration`

## Requirement meta I/F（共通キー）

- RequirementID: `RQ-2B-02`
- DependsOnContractID: `CTR-2B-02-DECISION-LOG-V1`
- RequirementStatement: A1のdecision log契約をmock検証し、非自動確定・再読込復元を担保する。
- PriorityClass（Must / Should / Could）: Must
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）:
  - 前提: A1契約（`CTR-2B-02-DECISION-LOG-V1`）がFixedである。
  - 操作: 4アクションをmock appendし、restoreで復元検証する。
  - 期待結果: 自動確定なしで決定履歴が再読込で復元される。
  - 除外: 実コード変更（`03_Implement/**`）と運用文書更新（`04_Documentation/**`）。
- GoNoGoGate（Required / Optional / N/A）: Required
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: N/A（計画のみ）
- VerificationLevel（docs-check / unit / integration / e2e）: integration
- DecisionStatus（Fixed / Pending）: Fixed
- DecisionQueueRef（未確定時の参照先）: N/A

## Phase 2（A2）: Plan → Execute → Verify → Proceed

- State Sync Check（Phase開始時）:
  - Read: `issue-FB-P2B-02-a1-interface-contract.md` / `issue-FB-P2B-02-a2-mock-validation.md` / `issue-FB-P2B-02-a3-implementation.md`
  - 整合確認: A1 `ContractID` = A2 `DependsOnContractID` = A3 `ReferenceContractID` = `CTR-2B-02-DECISION-LOG-V1`
  - 判定: Pass（契約ID不整合なし）

- Plan:
  - A1契約のみ依存でmock検証条件を固定し、契約拡張は行わない。
- Execute:
  - mock append順序: `accept -> partial -> reject -> defer`。
  - 非自動確定: append時に representative確定イベントを発生させない。
  - 再読込復元: 同一 `snapshotVersion` で `restore` は同順序同内容を返す。
  - 異常系: enum外 `action` は契約違反として復元対象外。
- Verify:
  - [x] A1契約ID依存が明記されている。
  - [x] 非自動確定条件が明記されている。
  - [x] 再読込復元条件が明記されている。
  - [x] stub/fixtureで検証継続可能。
- Proceed:
  - A3へ `CTR-2B-02-DECISION-LOG-V1` を参照IDとして引き渡す。

## Validation plan

- 実行コマンド:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- 期待結果:
  - issue memo必須メタが整合し、検証スクリプトが成功する。

## Reproducible verification record

- Command:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- Output:
  - `ok: validated 2 active issue memos`
- Self-Correction:
  - 0/3（修復ループ不要）

## Fail-safe

- Self-Correctionは最大3回。超過時は停止して人間判断依頼。
