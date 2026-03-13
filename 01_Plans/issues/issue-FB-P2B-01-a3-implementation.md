# Issue Draft: FB-P2B-01-A3 Similar-card候補提示 / 実装接続

- Type: Feature request
- Status: Open
- Source Issue: N/A (GitHub Issues are not used in current operations)
- Priority: P0
- Owner: Stream B
- Scope: `01_Plans/issues/` (planning memo only)
- Related Backlog: `FB-P2B-01`
- Related ADR/Spec: `ADR-0007`, `ADR-0001`
- Expected verification level: `integration`

## Requirement meta I/F（共通キー）

- RequirementID: `RQ-2B-01`
- ReferenceContractID: `CTR-2B-01-CANDIDATE-GROUP-V1`
- RequirementStatement: A1/A2契約を逸脱せず実装接続へ引き継ぐ。
- PriorityClass（Must / Should / Could）: Must
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）:
  - 前提: A1/A2がFixedである。
  - 操作: 実装タスクを契約準拠で接続する。
  - 期待結果: candidate group一覧と対象Card確認DoDを満たす実装計画になる。
  - 除外: 契約変更の独断実施。
- GoNoGoGate（Required / Optional / N/A）: Required
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: N/A（計画のみ）
- VerificationLevel（docs-check / unit / integration / e2e）: integration
- DecisionStatus（Fixed / Pending）: Fixed
- DecisionQueueRef（未確定時の参照先）: N/A

## Phase 3（A3）: Plan → Execute → Verify → Proceed

- Plan:
  - `CTR-2B-01-CANDIDATE-GROUP-V1` を参照し、契約再定義を禁止する。
- Execute:
  - Gate-1: A1フィールド完全準拠。
  - Gate-2: A2の非自動確定条件を回帰要件化。
  - Gate-3: A2の再読込復元条件を回帰要件化。
  - Gate-4: 逸脱要求はA1差し戻し（この文書で再定義しない）。
- Verify:
  - [x] 契約IDを参照している。
  - [x] 契約再定義禁止が明記されている。
  - [x] 非自動確定と復元条件が維持されている。
- Proceed:
  - Phase 4のVerify/Handoffへ進む。

## Phase 4（Verify / Handoff）

- AC/DoD検証結果:
  - AC-2B-1（候補group一覧と対象Card確認）: **Plan上は達成見込み**（実装未着手）。
- 未達項目:
  - 実コードとテストの実行結果（A3実装作業待ち）。
- 次レーン受け渡し条件:
  - 実装レーンは `CTR-2B-01-CANDIDATE-GROUP-V1` を唯一契約として採用。
  - 契約逸脱・追加フィールド要求はA1へ戻して再承認。

## Validation plan

- 実行コマンド:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- 期待結果:
  - issue memo必須メタが整合し、検証スクリプトが成功する。

## Fail-safe

- A1契約不整合、3回超過、またはStream C/Dとの競合検知で即停止。
