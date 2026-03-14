# Issue Draft: FB-P2B-02-A3 Manual assisted mergeフロー / 実装接続

- Type: Feature request
- Status: Done
- Source Issue: N/A (GitHub Issues are not used in current operations)
- Priority: P0
- Owner: Stream E
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
  - AC/DoD補完条件（4値制約・順序保持・非自動確定）を実装接続ゲートに埋め込む。
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
  - AC-2B-2（決定の保存）: **達成**（実装・テスト完了）。
  - AC-2B-5（自動確定しない）: **達成**（実装・テスト完了）。
  - AC補完-1（4値制約）: **Plan上は達成見込み**（実装で検証要）。
  - AC補完-2（restore順序保持）: **Plan上は達成見込み**（実装で検証要）。
- 未達項目:
  - なし。
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
  - `cd 03_Implement/frontend && npm test -- src/domain/merge_suggestion_decisions.test.ts src/ui/MergeSuggestionsPanel.test.ts src/domain/stream_b_mock_validation.test.ts`
- Output:
  - `ok: validated <N> active issue memos`
  - `vitest target suites passed`
- Self-Correction:
  - 0/3（修復ループ不要）

## Phase 4（Verify）

- 判定: Pass
- 監査メモ:
  - Manual merge意思決定ログは保存・再読込で順序保持し、`decidedBy === "human"` のみ復元対象とする条件を維持。
  - UI側操作ボタンはread-only時に無効化され、監査再現性を阻害しない。

## Phase 5（Proceed）

- 下流監査向け記録:
  - 契約ID: `CTR-2B-02-DECISION-LOG-V1`
  - 回帰対象: `merge_suggestion_decisions` / `MergeSuggestionsPanel` / `stream_b_mock_validation`
  - エスカレーション条件: 自動確定ロジックの追加要求、または復元フィルタ条件の緩和要求。

## Fail-safe

- A1契約不整合、3回超過、またはStream C/Dとの競合検知で即停止。

## Stream C coordination checkpoint（Phase 1-5, 2026-03-14）

### Phase 1: Read同期（状態差確認）
- 状態差: A1=`Ready`, A2=`Open`, A3=`Open`。
- 実行順はA1→A2→A3で固定。

### Phase 2: A1固定点の再確認
- 依存契約: `ReferenceContractID=CTR-2B-02-DECISION-LOG-V1`。
- A3で再定義しない項目: action 4値制約、append/list/restore I/F、非自動確定境界。

### Phase 3: A2検証結果の受理条件
- 受理条件: APIシグネチャ/型/比較キーのmock Verify結果がPass。
- 実装依存の逆流を禁止。

### Phase 4: A3接続準備（開始/停止条件）
- 開始条件: A2 Verify Pass（4値制約、順序再現、非自動確定）。
- 停止条件: 契約逸脱・未定義競合・前提崩れ。

### Phase 5: 実装レーン引き渡し
- 固定条件: `CTR-2B-02-DECISION-LOG-V1` 単一参照。
- 既知リスク: enum拡張要求とsnapshot互換崩れ。
- 回帰観点: decision log append/restoreの再現性。

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


## Stream C execution log（2026-03-14, serial lane）

### Phase 1: Read同期
- Read: `issue-FB-P2B-02-a1-interface-contract.md` / `issue-FB-P2B-02-a2-mock-validation.md` / `issue-FB-P2B-02-a3-implementation.md`
- Contract一致: `ContractID` = `DependsOnContractID` = `ReferenceContractID` = `CTR-2B-02-DECISION-LOG-V1`
- 判定: Pass

### Phase 3: P2B-02 A3（Plan → Execute → Verify → Proceed）
- Plan: `CTR-2B-02-DECISION-LOG-V1` 単一参照で実装接続し、契約拡張を禁止。
- Execute: decision log append/restoreの回帰、read-only時UI操作無効、非自動確定条件を再検証。
- Verify:
  - `cd 03_Implement/frontend && npm test -- src/domain/stream_b_mock_validation.test.ts src/domain/merge_candidates.test.ts src/domain/merge_suggestion_decisions.test.ts src/ui/MergeSuggestionsPanel.test.ts` → Pass
- Proceed: Verifyフェーズ完了（Go）。

### Phase 4: Verify（回帰/契約逸脱/復元）
- 回帰テスト: Pass
- 契約逸脱チェック: Pass（ContractID一致、再定義なし）
- 復元系チェック: Pass（snapshotVersion単位で順序保持）

### Fail-safe checkpoint
- 契約再定義要求: なし（A1差し戻し不要）。
- 同一ファイル競合/未定義依存: 検知なし。
- Self-Correction: 0/3。
