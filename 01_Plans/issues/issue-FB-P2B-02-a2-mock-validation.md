# Issue Draft: FB-P2B-02-A2 Manual assisted mergeフロー / モック検証

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
  - AC/DoD補完の適用として、非自動確定・順序復元・異常系除外の3条件を検証観点に固定する。
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
  - [x] AC/DoD補完（4値制約・順序保持・契約拡張禁止）がA3入力条件として明記されている。
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
  - `cd 03_Implement/frontend && npm test -- src/domain/stream_b_mock_validation.test.ts src/domain/merge_suggestion_decisions.test.ts`
- Output:
  - `ok: validated <N> active issue memos`
  - `vitest target suites passed`
- Self-Correction:
  - 0/3（修復ループ不要）

## Phase 4（Verify）

- 判定: Pass
- 監査メモ:
  - `CTR-2B-02-DECISION-LOG-V1` の append順序（accept→partial→reject→defer）と restore再現性をfixtureで固定。
  - enum外 action を復元対象外にする契約境界をテストで確認。

## Phase 5（Proceed）

- 下流監査向け記録:
  - 契約ID: `CTR-2B-02-DECISION-LOG-V1`
  - 回帰対象: `stream_b_mock_validation` / `merge_suggestion_decisions`
  - エスカレーション条件: action enum拡張要求、または snapshotVersionの互換破壊。

## Fail-safe

- Self-Correctionは最大3回。超過時は停止して人間判断依頼。

## Stream C coordination checkpoint（Phase 1-5, 2026-03-14）

### Phase 1: Read同期（状態差確認）
- 状態差: A1=`Ready`, A2=`Open`, A3=`Open`。
- 実行順はA1→A2→A3で固定。

### Phase 2: A1固定点の再確認
- 依存契約: `DependsOnContractID=CTR-2B-02-DECISION-LOG-V1`。
- 未定義項目: なし。

### Phase 3: A2モック検証（実コード非依存）
- 先行固定対象:
  - APIシグネチャ: `append/list/restore`
  - 型: `MergeDecisionRecord`
  - 比較キー: `snapshotVersion`, append順序, `action` enum
- 実コード依存排除: stub/fixtureで検証。

### Phase 4: A3接続準備（開始/停止条件）
- 開始条件: A2 Verifyで4値制約・順序保持・非自動確定がPass。
- 停止条件: 契約逸脱・未定義競合・前提崩れ。

### Phase 5: 実装レーン引き渡し
- 固定条件: enum追加はA1差し戻し。
- 既知リスク: restore時の順序逆転。
- 回帰観点: append→restoreの同順序再現、enum外除外。

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

### Phase 3: P2B-02 A2（Plan → Execute → Verify → Proceed）
- Plan: mock先行で append/list/restore I/F と action 4値制約、順序保持、非自動確定を固定。
- Execute: `accept -> partial -> reject -> defer` の順でfixture検証し、enum外action除外を確認。
- Verify:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` → Pass
  - `cd 03_Implement/frontend && npm test -- src/domain/stream_b_mock_validation.test.ts src/domain/merge_suggestion_decisions.test.ts` → Pass
- Proceed: A3接続へ進行。

### Fail-safe checkpoint
- 契約再定義要求: なし（A1差し戻し不要）。
- 同一ファイル競合/未定義依存: 検知なし。
- Self-Correction: 0/3。
