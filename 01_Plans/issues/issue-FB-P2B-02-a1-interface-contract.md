# Issue Draft: FB-P2B-02-A1 Manual assisted mergeフロー / インターフェース先行（型/契約）

- Type: Feature request
- Status: Ready (A1 Contract Fixed)
- Source Issue: N/A (GitHub Issues are not used in current operations)
- Priority: P0
- Owner: Stream E
- Scope: `01_Plans/issues/` (planning memo only)
- Related Backlog: `FB-P2B-02`
- Related ADR/Spec: `ADR-0007`, `ADR-0001`
- Expected verification level: `docs-check`

## Requirement meta I/F（共通キー）

- RequirementID: `RQ-2B-02`
- ContractID: `CTR-2B-02-DECISION-LOG-V1`
- RequirementStatement: decision log 永続化I/FをA1で固定する（実装禁止）。
- PriorityClass（Must / Should / Could）: Must
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）:
  - 前提: `FB-P2B-02` を A1→A2→A3 直列で実施する。
  - 操作: decision log の型・保存I/F・読込I/Fのみ定義する。
  - 期待結果: A2/A3が同一の永続化契約を参照できる。
  - 除外: 実コード変更（`03_Implement/**`）と運用文書更新（`04_Documentation/**`）。
- GoNoGoGate（Required / Optional / N/A）: Required
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: N/A（計画のみ）
- VerificationLevel（docs-check / unit / integration / e2e）: docs-check
- DecisionStatus（Fixed / Pending）: Fixed
- DecisionQueueRef（未確定時の参照先）: N/A

## Context / Decision / Consequences

- Context:
  - `採用/部分採用/却下/後で` の意思決定を保存・再読込する契約が未固定だと監査可能性が崩れる。
- Decision:
  - 契約ID `CTR-2B-02-DECISION-LOG-V1` を固定し、A2/A3はこの契約IDのみ参照する。
  - append/list/restore I/Fを固定し、自動確定は禁止する。
- Consequences:
  - A2はmock append/restore検証を即時開始できる。
  - A3は契約変更不可で、逸脱時はA1差し戻しを必須化。

## 固定契約（A1成果物）

- ContractFreeze:
  - `contractLinkLocked=true`
  - `sharedResourceFreeze=true`

- `MergeDecisionRecord`:
  - `decisionId: string`
  - `groupId: string`
  - `action: "accept" | "partial" | "reject" | "defer"`
  - `selectedCardIds: string[]`
  - `note: string`
  - `decidedBy: string`
  - `decidedAt: string`
  - `snapshotVersion: string`
- `DecisionLogStoreContract`:
  - `append(record: MergeDecisionRecord): void`
  - `listByGroup(groupId: string): MergeDecisionRecord[]`
  - `restore(snapshotVersion: string): MergeDecisionRecord[]`

## Phase 1-5（Stream E運用: Plan → Execute → Verify → Proceed）

### Phase 1: Read同期
- Plan: A1/A2/A3の契約ID参照一致と編集境界を再確認する。
- Execute:
  - Read: `issue-FB-P2B-02-a1-interface-contract.md` / `issue-FB-P2B-02-a2-mock-validation.md` / `issue-FB-P2B-02-a3-implementation.md`
  - 判定: `A1 ContractID = A2 DependsOnContractID = A3 ReferenceContractID = CTR-2B-02-DECISION-LOG-V1`（Pass）
- Verify: 依存矛盾なし、優先度はP0で一致。
- Proceed: Phase 2へ進行。

### Phase 2: P0 orchestrator方針更新
- Plan: A1固定契約の再定義禁止とA1→A2→A3直列進行を明文化する。
- Execute:
  - 固定ルール: 契約本文改訂は禁止、逸脱要求はA1差戻し。
  - 停止ルール: 依存矛盾・優先度矛盾・未定義競合検知時は即停止。
- Verify: 方針はplanning範囲に閉じ、実装依存なし（Pass）。
- Proceed: Phase 3へ進行。

### Phase 3: P2B A1契約チェック
- Plan: A2/A3に必要な最小契約点（ID/enum/I/F）を固定確認する。
- Execute:
  - `ContractID=CTR-2B-02-DECISION-LOG-V1`
  - `action` は `accept|partial|reject|defer` の4値のみ
  - `append/listByGroup/restore(snapshotVersion)` I/F固定
  - 非自動確定（human decision only）を維持
- Verify: 契約固定点はA2/A3引き渡し要件を満たす（Pass）。
- Proceed: Phase 4へ進行。

### Phase 4: モック活用前提の依存切り離し記述
- Plan: A2 mock-validationが実コード非依存で成立する境界を定義する。
- Execute:
  - 許可依存: 契約ID・enum制約・I/F署名・比較キー（`snapshotVersion`/順序）・fixture/stub。
  - 禁止依存: `03_Implement/**` 実装詳細、共有統合ファイルの編集。
- Verify: mock前提で検証が閉じることを確認（Pass）。
- Proceed: Phase 5へ進行。

### Phase 5: Verify（優先度・依存・競合記述の整合）
- Plan: 本メモ内の優先度・依存順・競合停止条件を最終確認する。
- Execute:
  - Priority: P0（Pass）
  - Dependency: A1→A2→A3（Pass）
  - Conflict rule: 未定義競合は即停止（Pass）
- Verify: フェイルセーフ条件を満たす。
- Proceed: A2/A3へ引き渡し可能。

## Handoff（A2/A3参照専用）

- Fixed links:
  - `issue-FB-P2B-02-a2-mock-validation.md`
  - `issue-FB-P2B-02-a3-implementation.md`
- 変更禁止項目:
  - `ContractID=CTR-2B-02-DECISION-LOG-V1`
  - `MergeDecisionRecord` / `DecisionLogStoreContract` の定義
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
  - 3/3（本更新で上限内）

## Fail-safe

### Stop report template（競合/前提崩れ時）

1) 失敗再現手順
2) 競合ファイル
3) 必要承認者
4) 解決のYes/No質問

- 依存矛盾・優先度矛盾・未定義競合を検知した場合は即停止し人間判断依頼。
