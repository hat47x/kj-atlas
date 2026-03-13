# Issue Draft: FB-P2B-01-A1 Similar-card候補提示 / インターフェース先行（型/契約）

- Type: Feature request
- Status: Open
- Source Issue: N/A (GitHub Issues are not used in current operations)
- Priority: P0
- Owner: Stream B
- Scope: `01_Plans/issues/` (planning memo only)
- Related Backlog: `FB-P2B-01`
- Related ADR/Spec: `ADR-0007`, `ADR-0001`
- Expected verification level: `docs-check`

## Requirement meta I/F（共通キー）

- RequirementID: `RQ-2B-01`
- ContractID: `CTR-2B-01-CANDIDATE-GROUP-V1`
- RequirementStatement: `Similar-card候補提示` の候補group構造と境界I/Fを固定する。
- PriorityClass（Must / Should / Could）: Must
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）:
  - 前提: `FB-P2B-01` を A1→A2→A3 直列で実施する。
  - 操作: A1で候補group構造・契約型・I/O境界のみ定義する。
  - 期待結果: A2/A3が参照すべき単一契約が固定される。
  - 除外: 実コード変更（`03_Implement/**`）と運用文書更新（`04_Documentation/**`）。
- GoNoGoGate（Required / Optional / N/A）: Required
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: N/A（計画のみ）
- VerificationLevel（docs-check / unit / integration / e2e）: docs-check
- DecisionStatus（Fixed / Pending）: Fixed
- DecisionQueueRef（未確定時の参照先）: N/A

## Context / Decision / Consequences

- Context:
  - `FB-P2B-01` のDoD（candidate group一覧 + 対象Card確認）を満たす前提として、候補データ契約の先行固定が必要。
  - A2/A3で再定義が起きると、検証資産の互換性が崩れる。
- Decision:
  - 契約ID `CTR-2B-01-CANDIDATE-GROUP-V1` を固定し、A2/A3はこの契約IDのみ参照する。
  - 自動確定ロジックは契約外（禁止）として扱う。
- Consequences:
  - A2はmock検証を即開始可能になる。
  - A3は契約追従のみ許可され、追加フィールド要求はA1差し戻しを必須とする。

## 固定契約（A1成果物）

- `SimilarCandidateGroup`:
  - `groupId: string`
  - `targetCardId: string`
  - `candidateCardIds: string[]`
  - `scoreSummary: { min: number; max: number; avg: number }`
  - `reasonCodes: string[]`
  - `snapshotVersion: string`
- `CandidateListViewModel`:
  - `generatedAt: string`
  - `groups: SimilarCandidateGroup[]`
  - `totalGroupCount: number`

## Phase 1（A1）: Plan → Execute → Verify → Proceed

- State Sync Check（Phase開始時）:
  - Read: `issue-FB-P2B-01-a1-interface-contract.md` / `issue-FB-P2B-01-a2-mock-validation.md` / `issue-FB-P2B-01-a3-implementation.md`
  - 整合確認: A1 `ContractID` = A2 `DependsOnContractID` = A3 `ReferenceContractID` = `CTR-2B-01-CANDIDATE-GROUP-V1`
  - 判定: Pass（契約ID不整合なし）

- Plan:
  - 候補group契約とI/O境界のみ固定し、実装要素は除外する。
- Execute:
  - 上記契約を `CTR-2B-01-CANDIDATE-GROUP-V1` として定義。
- Verify:
  - [x] 契約IDが明示されている。
  - [x] 必須フィールドが固定されている。
  - [x] 非自動確定（実装禁止）が保持されている。
- Proceed:
  - A2は本契約IDのみに依存してmock検証へ進む。

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

- A1契約不整合、またはStream C/D管轄との競合検知時は即停止し人間判断依頼。
