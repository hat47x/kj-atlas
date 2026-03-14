# Issue Draft: FB-P2B-01-A1 Similar-card候補提示 / インターフェース先行（型/契約）

- Type: Feature request
- Status: Ready (A1 Contract Fixed)
- Source Issue: N/A (GitHub Issues are not used in current operations)
- Priority: P0
- Owner: Stream C
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

## AC/DoD ドラフト（不足確認）

- AC-2B-1: candidate group一覧と対象Card確認を成立させるための入出力型が固定されていること。
- DoD-2B-1: A2/A3が契約再定義せず `CTR-2B-01-CANDIDATE-GROUP-V1` を参照できること。
- 判定: 本メモ範囲では不足なし（追加要求が出た場合はA1へ差し戻し）。

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

- ContractFreeze:
  - `contractLinkLocked=true`
  - `sharedResourceFreeze=true`


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

- State Sync Check（Phase開始時の再Read）:
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

## Handoff（A2/A3参照専用）

- Fixed links:
  - `issue-FB-P2B-01-a2-mock-validation.md`
  - `issue-FB-P2B-01-a3-implementation.md`
- 変更禁止項目:
  - `ContractID=CTR-2B-01-CANDIDATE-GROUP-V1`
  - `SimilarCandidateGroup` / `CandidateListViewModel` のフィールド定義
  - `contractLinkLocked=true` / `sharedResourceFreeze=true`
- 逸脱要求はA1へ差し戻し。

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

### Stop report template（競合/前提崩れ時）

1) 失敗再現手順
2) 競合ファイル
3) 必要承認者
4) 解決のYes/No質問

- A1契約不整合、またはStream C/D管轄との競合検知時は即停止し人間判断依頼。

## Stream C coordination checkpoint（Phase 1-5, 2026-03-14）

### Phase 1: Read同期（状態差確認）
- 状態差: A1=`Ready`, A2=`In Progress`, A3=`In Progress`。
- 実行順: **A1固定点確認 → A2 mock検証 → A3接続準備**（直列固定）。

### Phase 2: A1固定点の確認
- A2/A3依存項目のみ抽出済み:
  - `ContractID=CTR-2B-01-CANDIDATE-GROUP-V1`
  - `SimilarCandidateGroup` / `CandidateListViewModel` 必須フィールド
  - 非自動確定（候補提示のみで確定しない）
- 未定義項目: なし（ADR合意待ち不要）。

### Phase 3: A2モック検証の前提
- 検証境界を **APIシグネチャ/型/比較キー** に限定する。
- 実コード依存は持ち込まない（stub/fixtureのみ）。

### Phase 4: A3接続準備（開始/停止条件）
- 開始条件: A2が `CTR-2B-01-CANDIDATE-GROUP-V1` 依存・非自動確定・再読込復元をVerify済み。
- 停止条件: 契約逸脱、未定義競合、前提崩れを検知した時点で即停止。

### Phase 5: 実装レーン引き渡し
- 固定条件: 契約ID不変、フィールド追加はA1差し戻し。
- 既知リスク: tie時順序キーの実装側解釈ブレ。
- 回帰観点: 同一 `snapshotVersion` の順序再現性 / 非自動確定維持。


## Decision Queue整理（Stream A view）

| QueueID | Topic | Status | Decision | Proceed Impact |
|---|---|---|---|---|
| DQ-FB-P2B-01-001 | ContractID固定 (`CTR-2B-01-CANDIDATE-GROUP-V1`) | Closed | A1で固定 | A2可 |
| DQ-FB-P2B-01-002 | 非自動確定（候補提示のみ） | Closed | 契約外操作として禁止 | A3可 |
| DQ-FB-P2B-01-003 | snapshot再現性キー固定 | Closed | `snapshotVersion` を比較キー化 | A2/A3可 |

## Proceed判定（A2/A3）

- 可否: **可**
- 根拠: 契約ID/必須フィールド/非目標（自動確定禁止）を固定済み。
- 残リスク: 同点候補の順序決定ロジックの実装解釈差。A2のfixture順序期待値で拘束。



## Stream A固定シグネチャ / 検証キー（A2/A3引き渡し）

- Fixed signature:
  - `contractLinkLocked=true`
  - `sharedResourceFreeze=true`
- Verification keys:
  - `ContractID`（または `InterfaceName`）
  - `schemaVersion`（定義がある契約）
  - 必須フィールド一覧
- Rule:
  - A2/A3は上記キーの一致確認のみ実施し、契約本文は改訂しない。
