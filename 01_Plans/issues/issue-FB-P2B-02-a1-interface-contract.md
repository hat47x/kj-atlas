# Issue Draft: FB-P2B-02-A1 Manual assisted mergeフロー / インターフェース先行（型/契約）

- Type: Feature request
- Status: Open (Audit Hold: legacy Ready normalized; not a new-start target)
- Source Issue: N/A (GitHub Issues are not used in current operations)
- Priority: P0
- Owner: Stream J
- Scope: `01_Plans/issues/` (planning memo only)
- Related Backlog: `FB-P2B-02`
- Related ADR/Spec: `ADR-0007`, `ADR-0001`, `02_Architecture/schemas.md`
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

### Context
- `採用/部分採用/却下/後で` の意思決定を保存・再読込する契約が未固定だと、監査可能性とrestore再現性が崩れる。
- append/list/restore の境界がA2/A3で揺れると、manual assisted mergeの人間判断ログを同一条件で比較できない。
- `schemas.md` のスナップショット境界に合わせ、A1は docs-only で decision log 契約を凍結する。

### Decision
- 契約ID `CTR-2B-02-DECISION-LOG-V1` をA1で凍結し、A2/A3は参照のみ許可する。
- API署名は mock/stub で検証可能な `appendDecision(record)` / `listDecisionsByGroup(groupId)` / `restoreDecisionLog(snapshotVersion)` に固定する。
- action enum は `accept | partial | reject | defer` の4値に限定し、自動確定や代表カード更新は契約外とする。

### Consequences
- A2は4値制約・順序保持・restore境界をfixtureで直ちに検証できる。
- A3は永続化方式を実装しても契約変更できず、enum拡張や必須項目変更要求はA1差し戻しになる。
- Gate未承認・契約矛盾・未定義競合が出た場合は強行せず停止できる。

## 固定契約（A1成果物 / Contract Freeze）

- ContractFreeze:
  - `contractLinkLocked=true`
  - `sharedResourceFreeze=true`
  - `a2ReferenceOnly=true`
  - `a3ReferenceOnly=true`

### Domain types

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

### Mock-ready API signature（A2/A3参照専用）

- `AppendDecisionInput`:
  - `record: MergeDecisionRecord`
- `AppendDecisionOutput`:
  - `accepted: true`
- `RestoreDecisionInput`:
  - `snapshotVersion: string`
- `MockValidationSignature`:
  - `appendDecision(input: AppendDecisionInput): AppendDecisionOutput`
  - `listDecisionsByGroup(groupId: string): MergeDecisionRecord[]`
  - `restoreDecisionLog(input: RestoreDecisionInput): MergeDecisionRecord[]`

### Comparison keys / deterministic rules

- Decision equality key: `decisionId`
- Group boundary key: `groupId`
- Restore boundary key: `snapshotVersion`
- Ordered fields:
  - append insertion order
  - `selectedCardIds[]`
- Out of scope:
  - auto-merge execution
  - representative overwrite
  - persistence backend choice

## 実装ハンドオフ定義（Template Freeze）

### Input Contract
- A2/A3は `CTR-2B-02-DECISION-LOG-V1` を唯一参照する。
- `MergeDecisionRecord.action` は4値のみ受理する。
- `decidedBy` は人間判断ログを表す値として記録し、自動処理主体を混在させない。

### Expected Output
- `appendDecision` は追記成功のみを返し、確定イベントを副作用として起こさない。
- `restoreDecisionLog` は同一 `snapshotVersion` に対して同一順序・同一内容の `MergeDecisionRecord[]` を返す。
- `listDecisionsByGroup` は `groupId` 境界を越えて混在させない。

### Rollback Trigger
- `action` enum の追加・改名要求が出た場合。
- restore時の順序非決定や `snapshotVersion` 互換破壊が判明した場合。
- appendと同時に自動確定を走らせる要求が出た場合。

## Phase 1-5（Stream E運用: Plan → Execute → Verify → Proceed）

### Phase 1: Read同期
- Plan: 3ファイルとA2/A3参照先を読み、Gate条件と契約順序を再確認する。
- Execute:
  - Read: `issue-FB-P2B-02-a1-interface-contract.md` / `issue-FB-P2B-02-a2-mock-validation.md` / `issue-FB-P2B-02-a3-implementation.md`
  - 判定: `A1 ContractID = A2 DependsOnContractID = A3 ReferenceContractID = CTR-2B-02-DECISION-LOG-V1`（Pass）
- Verify: 依存矛盾なし、優先度はP0で一致。
- Proceed: Phase 2へ進行。

### Phase 2: A1契約凍結
- Plan: Context / Decision / Consequences を固定し、A2/A3参照専用リンクを明文化する。
- Execute:
  - 固定ルール: 契約本文改訂は禁止、逸脱要求はA1差戻し。
  - 参照リンク: `issue-FB-P2B-02-a2-mock-validation.md` / `issue-FB-P2B-02-a3-implementation.md`
- Verify: 契約本文と参照導線がA1に閉じている（Pass）。
- Proceed: Phase 3へ進行。

### Phase 3: Mock-ready化
- Plan: API署名・型・比較キーをmockで検証可能に整備する。
- Execute:
  - `MockValidationSignature=appendDecision/listDecisionsByGroup/restoreDecisionLog`
  - 比較キー: `decisionId` / `groupId` / `snapshotVersion` / ordered arrays
  - 非自動確定（human decision only）を維持
- Verify: A2がfixture/stubのみで検証開始可能（Pass）。
- Proceed: Phase 4へ進行。

### Phase 4: 実装ハンドオフ定義
- Plan: Input Contract / Expected Output / Rollback Trigger をテンプレ化する。
- Execute:
  - handoff template を本メモ内に固定
  - A3はテンプレ参照のみ許可
- Verify: 実装レーンへ渡す最小境界が明文化済み（Pass）。
- Proceed: Phase 5へ進行。

### Phase 5: Verify / Proceed
- Plan: docs-check実施、3回までSelf-Correction、超過停止を確認する。
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
  - `MergeDecisionRecord` / `DecisionLogStoreContract` / mock signature群
  - 比較キー（`decisionId` / `groupId` / `snapshotVersion` / append order / `selectedCardIds[]`）
  - `contractLinkLocked=true` / `sharedResourceFreeze=true`
- 逸脱要求はA1へ差し戻し。


## Stream J serial readiness protocol（Plan→Execute→Verify→Proceed 固定）

### Phase 1 Read（Ready/P0メモ整合と未記載項目抽出）
- Phase開始Read: 当該A1/A2/A3の3メモを再読し、`Status` / `Priority(P0)` / `DecisionStatus` / `ContractID(またはDependsOnContractID)` を照合する。
- 抽出項目（不足監査）: AC未記載、DoD未記載、停止条件未記載、handoff条件未記載。
- Proceed条件: 未記載があれば本メモへ追記してから次Phaseへ進む。

### Phase 2 ADR明文化（Context / Decision / Consequences）
- Phase開始Read: `Related ADR/Spec` と当該A1契約本文を再読する。
- Plan: ADR新設ではなく、既存方針のCDC不足をIssue本文へ補完する。
- Execute: Context / Decision / Consequencesの3点を契約IDと依存順序に紐付けて固定する。
- Verify: 新規アーキ判断を持ち込んでいないことを確認する。
- Proceed条件: CDCがA1/A2/A3で矛盾しない。

### Phase 3 Plan（AC/DoD不足提案と合意）
- Phase開始Read: Acceptance criteria と Fail-safe セクションを再読する。
- Plan: 不足があれば `gapType=AC|DoD` と `agreementStatus` を明示した提案行を追加する。
- Execute: 合意前提（`agreementStatus=agreed` でのみGo）を明記する。
- Verify: AC/DoD不足が未処理のまま次Phaseへ流れていない。
- Proceed条件: 不足項目が解消済み、または保留理由と再開条件が明記済み。

### Phase 4 Execute（A1→A2→A3直列固定）
- Phase開始Read: ContractLinks / DependsOnContractID / ReferenceContractID を再照合する。
- Execute: 依存順序を `A1 -> A2 -> A3` に固定し、逆流要求はA1へ差し戻す。
- Verify: 並列前提や実装先行前提を含まない。
- Proceed条件: handoff payload と停止条件が同時に明記されている。

### Phase 5 Verify（docs-check / 依存参照 / 表記ゆれ）
- Phase開始Read: Validation plan と State sync を再読する。
- Execute: `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` を基準検証として実行する。
- Verify: 失敗時は自己修復を最大3回まで。
- 停止条件: 3回超過 / 依存不整合 / 指定外ファイル更新が必要になった場合は停止して報告する。
- Proceed条件: docs-check成功かつ参照整合が維持される。

### Phase 6 Proceed（handoff条件と次実装入口固定）
- Phase開始Read: Handoff と Proceed 判定を再読する。
- Execute: handoff固定値（ContractID、version、mockCase、ownerOfFix等）を次実装入口の必須入力として固定する。
- Verify: 次実装入口が「契約参照のみ」で開始できることを確認する。
- Proceed: Go時のみ下流へ引き渡し、NoGo時は停止条件と再開条件を併記して保留する。

## 監査整理（旧Ready/Activeの現行ライフサイクル対応）

### Phase 1: Read
- 旧表記 `Ready` / `Active` は監査対象の履歴値としてのみ扱い、現行の起票ライフサイクル（Draft -> Open -> In Progress -> Done）へ再マップした。

### Phase 2: Plan（現行ライフサイクルへのマッピング方針）
- マッピング方針: `Ready` / `Active` は **Open + Audit Hold** に統一し、新規着手キュー（In Progress）へ自動昇格させない。
- 本メモは計画整備（docs-check）に限定し、実装タスクへ接続しない。

### Phase 3: Execute（Status語彙と再開条件の統一記述）
- Status語彙を `Open` に統一し、注記で `Audit Hold`（着手対象外）を固定した。
- 再開条件（共通）:
  1. 依存するA1→A2→A3契約整合が再確認済み。
  2. `validate_active_issue_memos.py` の検証が成功。
  3. 担当ストリームが In Progress へ昇格する明示判断を記録。

### Phase 4: Verify（README運用ルール整合）
- `01_Plans/issues/README.md` のライフサイクル定義（Draft/Open/In Progress/Done）に合わせ、旧語彙は運用ステータスとして使用しない。

### Phase 5: Proceed（再開候補 / 保留候補）
- 再開候補: 依存整合・検証成功・担当明示の3条件を満たした時点で `Open -> In Progress` を検討。
- 保留候補: 上記条件のいずれか未達、または未定義競合がある場合は `Open (Audit Hold)` を維持。

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
  - 0/3（本更新時点。3回超過時は停止）

## Fail-safe

### Stop report template（競合/前提崩れ時）

1) 失敗再現手順
2) 競合ファイル
3) 必要承認者
4) 解決のYes/No質問

- Gate未承認、契約矛盾、未定義競合を検知した場合は即停止し人間判断依頼。

## Stream I normalization ledger（Phase 1-6 / Plan→Execute→Verify→Proceed）

### Phase 1 Read
- Plan: Status / Scope / DecisionStatus / Validation plan を抽出し、A1/A2/A3粒度を点検する。
- Execute:
  - Status: 既存本文の宣言値を採用。
  - Scope: `Contract` に限定。
  - DecisionStatus: `Fixed`。
  - Validation command: `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`。
- Verify: 抽出項目が本メモ内で相互矛盾しないことを確認。
- Proceed: 矛盾がなければ Phase 2 へ進む。

### Phase 2 Plan
- Plan: AC/DoD不足の有無を点検し、不足時はドラフト提案I/Fで合意前提にする。
- Execute: 依存は `A1 -> A2 -> A3` のみ許可し、実装ストリーム依存は mock I/F へ切り離す。
- Verify: 待ち依存が「契約未固定」「責務未確定」に限定されることを確認。
- Proceed: 依存最小化が成立した場合のみ次Phaseへ進行。

### Phase 3 ADR CDC明文化
- Plan: ADR追加を行わず、Issue本文の Context / Decision / Consequences を判定根拠の正本にする。
- Execute:
  - Context: 上位ADR/Spec整合の範囲内で計画を固定。
  - Decision: 契約順序を `A1 -> A2 -> A3` に固定。
  - Consequences: 逸脱要求はA1差し戻し。
- Verify: 新規アーキ判断がないこと（ADR追加不要）を確認。
- Proceed: CDC固定済みとしてPhase 4へ進む。

### Phase 4 Execute
- Plan: Contract / Mock / Implementation の責務境界を再確認する。
- Execute:
  - Contract: A1固定値を変更しない。
  - Mock: A2は fixture/stub と判定ログで閉じる。
  - Implementation: A3は handoff payload の受領判定のみ扱う。
- Verify: 競合しやすい共有ファイル編集要求を含まないことを確認。
- Proceed: 境界維持が確認できたらPhase 5へ進む。

### Phase 5 Verify
- Plan: docs-check、必須メタ、参照整合を検証する。
- Execute: `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` を単一検証コマンドとして実行する。
- Verify: 失敗時は自己修復を最大3回まで実施し、超過時は停止する。
- Proceed: 検証成功時のみ Ready 判定へ進む。

### Phase 6 Proceed
- Plan: Ready化可能項目と保留項目を分離する。
- Execute:
  - Ready条件: ContractID整合・依存順序整合・停止条件明記。
  - 保留条件: 未定義競合 / AC合意未完了 / Gate未承認。
- Verify: 保留項目に stop condition と再開条件を必ず併記する。
- Proceed:
  - Ready: 実装ストリームへ引き渡し可。
  - Hold: `stop condition` 解消後に同Phaseから再開。

## Stream G handoff sync (2026-04-12)

### Read同期
- Re-read sibling A1/A2/A3 memos in the same backlog lane and reconfirmed serial dependency `A1 -> A2 -> A3`.

### Dependency / Decision Queue
- QueueID: `DQ-FB_P2B_02_A1_INTERFACE_CONTRACT-STREAM-G-2026-04-12`
- Status: Closed
- Rule: unresolved queue item blocks Proceed; contract drift is routed back to A1 only.

### AC/DoD補完
- Added lane-level NoGo rule: no transition to next phase when queue is reopened, dependency is inverted, or contract link is missing.
- Added lane-level DoD rule: handoff payload must include `contractId`, `decision status`, `rollback trigger`, and `next owner`.

### docs-check
- Validation command: `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`.

### 次レーンhandoff
- Next lane receives reference-only contract context and may not redefine A1 contract values.

