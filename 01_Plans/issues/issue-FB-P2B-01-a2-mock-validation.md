# Issue Draft: FB-P2B-01-A2 Similar-card候補提示 / モック検証

- Type: Feature request
- Status: In Progress
- Source Issue: N/A (GitHub Issues are not used in current operations)
- Priority: P0
- Owner: Stream E
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

- Phase 1 Read同期（A1契約ID一致確認）:
  - Read: `issue-FB-P2B-01-a1-interface-contract.md` / `issue-FB-P2B-01-a2-mock-validation.md` / `issue-FB-P2B-01-a3-implementation.md`
  - 判定: A1 `ContractID` = A2 `DependsOnContractID` = A3 `ReferenceContractID` = `CTR-2B-01-CANDIDATE-GROUP-V1`
  - 結果: Pass

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
  - `cd 03_Implement/frontend && npm test -- src/domain/merge_candidates.test.ts src/domain/stream_b_mock_validation.test.ts`
- Output:
  - `ok: validated <N> active issue memos`
  - `vitest target suites passed`
- Self-Correction:
  - 0/3（修復ループ不要）

## Stream D execution log（2026-03-14）

- Plan:
  - A1契約ID一致を再確認し、A2の非自動確定・再読込復元条件を回帰テストで再検証する。
- Execute:
  - `src/domain/merge_candidates.test.ts` / `src/domain/stream_b_mock_validation.test.ts` を実行し、候補提示が契約準拠であることを確認。
- Verify:
  - docs-check と frontend integration test はすべて Pass。
- Proceed:
  - A3実装接続フェーズへ継続。

## Phase 4（Verify）

- 判定: Pass
- 監査メモ:
  - `CTR-2B-01-CANDIDATE-GROUP-V1` の mock 検証は deterministic fixture で再現可能。
  - 候補提示のみで canonical merge の自動確定が実行されないことを回帰テストで維持。

## Fail-safe

- Self-Correctionは最大3回。超過時は停止して人間判断依頼。

## Stream C coordination checkpoint（Phase 1-5, 2026-03-14）

### Phase 1: Read同期（状態差確認）
- 状態差: A1=`Ready`, A2=`In Progress`, A3=`In Progress`。
- 実行順はA1→A2→A3で固定。

### Phase 2: A1固定点の再確認
- 依存契約: `DependsOnContractID=CTR-2B-01-CANDIDATE-GROUP-V1`。
- 未定義項目: なし（契約境界で閉じる）。

### Phase 3: A2モック検証（実コード非依存）
- 先行固定対象:
  - APIシグネチャ: `CandidateListViewModel` 入出力
  - 型: `SimilarCandidateGroup`
  - 比較キー: `groupId`, `targetCardId`, `snapshotVersion`, group順序
- 実コード依存排除: stub/fixtureでのみ検証。

### Phase 4: A3接続準備（開始/停止条件）
- 開始条件: A2 Verifyで「契約ID一致」「非自動確定」「再読込復元」すべてPass。
- 停止条件: 契約逸脱・未定義競合・前提崩れ。

### Phase 5: 実装レーン引き渡し
- 固定条件: 契約拡張禁止、比較キー不変。
- 既知リスク: restore順序の不安定化（実装時のソート差異）。
- 回帰観点: 同一入力同一順序、候補提示のみでは確定しない。

## Stream E execution log（2026-03-14）

### Phase 1: Read Gate
- Read: `issue-FB-P2B-01/02-a1-interface-contract.md` と当該A2/A3メモを再読し、`ContractID` / `DependsOnContractID` / `ReferenceContractID` の一致を確認。
- 判定: Pass（契約ID不整合なし）。

### Phase 2-3: A2/A3
- A2: mock先行条件（非自動確定・再読込復元・順序保持）を契約境界として固定。
- A3: 契約再定義禁止のまま、frontend実装テスト観点へ接続。

### Phase 4: Verify（宣言検証）
- `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- `cd 03_Implement/frontend && npm test -- src/domain/stream_b_mock_validation.test.ts src/domain/merge_candidates.test.ts src/domain/merge_suggestion_decisions.test.ts src/ui/MergeSuggestionsPanel.test.ts`
- 判定: Pass（関連suite全件成功）。

### Phase 5: Proceed
- Go（A2/A3の宣言検証レベル要件を充足）。

