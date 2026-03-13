# Issue Draft: FB-P2B-02-A3 Manual assisted mergeフロー / 実装接続

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
- ReferenceContractID: `CTR-2B-02-DECISION-LOG-V1`
- RequirementStatement: A1/A2契約を維持したまま実装接続へ進む。
- PriorityClass（Must / Should / Could）: Must
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）:
  - 前提: A1/A2がFixedである。
  - 操作: decision log実装タスクを契約にマッピングする。
  - 期待結果: `採用/部分採用/却下/後で` が保存可能で自動確定しない。
  - 除外: 契約を実装都合で変更する行為。
- GoNoGoGate（Required / Optional / N/A）: Required
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: N/A（計画のみ）
- VerificationLevel（docs-check / unit / integration / e2e）: integration
- DecisionStatus（Fixed / Pending）: Fixed
- DecisionQueueRef（未確定時の参照先）: N/A

## Phase 3（A3）: Plan → Execute → Verify → Proceed

- State Sync Check（Phase開始時）:
  - Read: `issue-FB-P2B-02-a1-interface-contract.md` / `issue-FB-P2B-02-a2-mock-validation.md` / `issue-FB-P2B-02-a3-implementation.md`
  - 整合確認: A1 `ContractID` = A2 `DependsOnContractID` = A3 `ReferenceContractID` = `CTR-2B-02-DECISION-LOG-V1`
  - 判定: Pass（契約ID不整合なし）

- Plan:
  - `CTR-2B-02-DECISION-LOG-V1` を参照し、契約再定義を禁止する。
- Execute:
  - Gate-1: `MergeDecisionRecord` 必須項目を全保持。
  - Gate-2: A2の非自動確定条件を回帰要件化。
  - Gate-3: A2のrestore順序一致条件を回帰要件化。
  - Gate-4: 逸脱要求はA1差し戻し（本A3で再定義しない）。
- Verify:
  - [x] 契約ID参照が明記されている。
  - [x] 契約再定義禁止が明記されている。
  - [x] 非自動確定と再読込復元が保持されている。
- Proceed:
  - Phase 4のVerify/Handoffへ進む。

## Phase 4（Verify / Handoff）

- AC/DoD検証結果:
  - AC-2B-2（決定の保存）: **Plan上は達成見込み**（実装未着手）。
  - AC-2B-5（自動確定しない）: **Plan上は達成見込み**（実装未着手）。
- 未達項目:
  - 実コード上のappend/list/restoreと回帰テスト結果。
- 次レーン受け渡し条件:
  - 実装レーンは `CTR-2B-02-DECISION-LOG-V1` を唯一契約として採用。
  - enum拡張/必須項目変更要求はA1へ差し戻して再承認。

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

- A1契約不整合、3回超過、またはStream C/Dとの競合検知で即停止。
