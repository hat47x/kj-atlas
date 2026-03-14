# Issue Draft: FB-P2B-02-A1 Manual assisted mergeフロー / インターフェース先行（型/契約）

- Type: Feature request
- Status: Ready (A1 Contract Fixed)
- Source Issue: N/A (GitHub Issues are not used in current operations)
- Priority: P0
- Owner: Stream C
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

## Phase 1（A1）: Plan → Execute → Verify → Proceed

- State Sync Check（Phase開始時）:
  - Read: `issue-FB-P2B-02-a1-interface-contract.md` / `issue-FB-P2B-02-a2-mock-validation.md` / `issue-FB-P2B-02-a3-implementation.md`
  - 整合確認: A1 `ContractID` = A2 `DependsOnContractID` = A3 `ReferenceContractID` = `CTR-2B-02-DECISION-LOG-V1`
  - 判定: Pass（契約ID不整合なし）

- Plan:
  - decision log契約のみを固定し、実装項目を除外する。
  - AC/DoD不足を補完するため、A2/A3が再利用可能な最小I/F整合条件を明文化する。
- Execute:
  - 上記契約を `CTR-2B-02-DECISION-LOG-V1` として定義。
  - 補完提案（A1時点で固定）:
    - AC補完-1: `action` は `accept|partial|reject|defer` の4値以外を受理しない。
    - AC補完-2: `restore(snapshotVersion)` は同一 `snapshotVersion` に対して決定順序を保持する。
    - DoD補完-1: A2/A3は契約拡張を行わず、本契約ID参照のみで進行する。
- Verify:
  - [x] 4アクション enum が固定されている。
  - [x] append/list/restore I/F が固定されている。
  - [x] 非自動確定が契約境界として維持されている。
  - [x] AC/DoD補完条件がA2/A3へ引き渡し可能な形で定義されている。
- Proceed:
  - A2は契約IDを唯一参照してmock検証へ進む。

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
  - 0/3（修復ループ不要）

## Fail-safe

- A1契約不整合、またはStream C/D管轄競合検知時は即停止し人間判断依頼。

## Stream C coordination checkpoint（Phase 1-5, 2026-03-14）

### Phase 1: Read同期（状態差確認）
- 状態差: A1=`Ready`, A2=`Open`, A3=`Open`。
- 実行順: **A1固定点確認 → A2 mock検証 → A3接続準備**。

### Phase 2: A1固定点の確認
- A2/A3依存項目のみ抽出済み:
  - `ContractID=CTR-2B-02-DECISION-LOG-V1`
  - `action` 4値制約（`accept|partial|reject|defer`）
  - `append/list/restore(snapshotVersion)` I/F
  - 非自動確定（human decision only）
- 未定義項目: なし（ADR合意待ち不要）。

### Phase 3: A2モック検証の前提
- 検証境界を APIシグネチャ/型/比較キー（順序・snapshotVersion）に限定。
- 実コード依存を排除し、fixtureで閉じる。

### Phase 4: A3接続準備（開始/停止条件）
- 開始条件: A2で4値制約・順序保持・非自動確定をVerify済み。
- 停止条件: 契約逸脱、未定義競合、前提崩れ。

### Phase 5: 実装レーン引き渡し
- 固定条件: 4値制約と契約ID不変。
- 既知リスク: action enum拡張要求による互換破壊。
- 回帰観点: restore順序再現、enum外action除外。


## Decision Queue整理（Stream A view）

| QueueID | Topic | Status | Decision | Proceed Impact |
|---|---|---|---|---|
| DQ-FB-P2B-02-001 | ContractID固定 (`CTR-2B-02-MANUAL-MERGE-V1`) | Closed | A1で固定 | A2可 |
| DQ-FB-P2B-02-002 | 手動承認境界（auto-merge禁止） | Closed | 契約に明記して禁止 | A3可 |
| DQ-FB-P2B-02-003 | 競合解消の停止条件 | Closed | 未定義競合は即停止 | A2/A3可 |

## Proceed判定（A2/A3）

- 可否: **可**
- 根拠: 契約IDとmanual merge境界が固定、Decision Queue残件なし。
- 残リスク: 競合種類の分類粒度差。分類追加要求はA1差し戻しで統制。

