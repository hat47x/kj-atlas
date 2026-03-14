# Issue Draft: FB-P2B-01-A2 Similar-card候補提示 / モック検証

- Type: Feature request
- Status: Open
- Source Issue: N/A (GitHub Issues are not used in current operations)
- Priority: P0
- Owner: Stream C
- Scope: `01_Plans/issues/` (planning memo only)
- Related Backlog: `FB-P2B-01`
- Related ADR/Spec: `ADR-0007`, `ADR-0001`
- Expected verification level: `integration`

## Requirement meta I/F（共通キー）

- RequirementID: `RQ-2B-01`
- DependsOnContractID: `CTR-2B-01-CANDIDATE-GROUP-V1`
- RequirementStatement: A1契約に基づく候補group提示をmockで検証可能状態にする。
- PriorityClass（Must / Should / Could）: Must
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）:
  - 前提: A1契約（`CTR-2B-01-CANDIDATE-GROUP-V1`）がFixedである。
  - 操作: mock candidate groupsを投入し、表示/再読込の期待値を検証する。
  - 期待結果: 非自動確定かつ再読込復元の契約がテスト化される。
  - 除外: 実コード変更（`03_Implement/**`）と運用文書更新（`04_Documentation/**`）。
- GoNoGoGate（Required / Optional / N/A）: Required
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: N/A（計画のみ）
- VerificationLevel（docs-check / unit / integration / e2e）: integration
- DecisionStatus（Fixed / Pending）: Fixed
- DecisionQueueRef（未確定時の参照先）: N/A

## AC/DoD ドラフト（不足確認）

- AC-2B-2: mock投入で `CandidateListViewModel` の群が順序/対象Cardを保持して観測できること。
- AC-2B-3: 候補提示のみで merge state が自動確定しないこと。
- DoD-2B-2: 同一 `snapshotVersion` 入力で再読込時に同一group構造が再現されること。
- 判定: 本メモ範囲では不足なし（契約追加要求はA1へ差し戻し）。

## Phase 2（A2）: Plan → Execute → Verify → Proceed

- State Sync Check（Phase開始時の再Read）:
  - Read: `issue-FB-P2B-01-a1-interface-contract.md` / `issue-FB-P2B-01-a2-mock-validation.md` / `issue-FB-P2B-01-a3-implementation.md`
  - 整合確認: A1 `ContractID` = A2 `DependsOnContractID` = A3 `ReferenceContractID` = `CTR-2B-01-CANDIDATE-GROUP-V1`
  - 判定: Pass（契約ID不整合なし）

- Plan:
  - A1契約のみに依存し、実装に踏み込まずmock検証条件を固定する。
- Execute:
  - mock入力: `CandidateListViewModel` with 2 groups / 1 target card each。
  - 期待表示: group順序と `targetCardId` が一致。
  - 非自動確定: 候補提示のみで merge state は未確定のまま。
  - 再読込復元: 同一 `snapshotVersion` の再投入で同一group構造を返す。
- Verify:
  - [x] A1契約IDへの依存が明記されている。
  - [x] 非自動確定が明記されている。
  - [x] 再読込復元（同順序同内容）が明記されている。
  - [x] stub/fixture前提での検証継続が可能。
- Proceed:
  - A3へは `CTR-2B-01-CANDIDATE-GROUP-V1` を参照IDとして引き渡す。

## Validation plan

- 実行コマンド:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- 期待結果:
  - issue memo必須メタが整合し、検証スクリプトが成功する。

## Reproducible verification record

- Command:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- Output:
  - `ok: validated <N> active issue memos`
- Self-Correction:
  - 0/3（修復ループ不要）

## Fail-safe

- Self-Correctionは最大3回。超過時は停止して人間判断依頼。
