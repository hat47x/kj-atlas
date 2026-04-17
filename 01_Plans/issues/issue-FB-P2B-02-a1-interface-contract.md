# Issue Draft: FB-P2B-02-A1 Manual assisted mergeフロー / インターフェース先行（型/契約）

- Type: Feature request
- Status: Open (Audit Hold: normalized contract pack; resumable by explicit Go/NoGo)
- Source Issue: N/A (GitHub Issues are not used in current operations)
- Priority: P0
- Owner: Stream H（audit normalization only）
- Scope: `01_Plans/issues/` (planning memo only)
- Related Backlog: `FB-P2B-02`
- Related ADR/Spec: `ADR-0007`, `ADR-0001`, `02_Architecture/schemas.md`
- Expected verification level: `docs-check`

## Dependencies

- DependsOn: none（A1 contract root）
- Unblocks: issue-FB-P2B-02-a2-mock-validation.md / issue-FB-P2B-02-a3-implementation.md
- Gate/Blocker: Ready when ContractID・Required fields・Invariants・ContractLinks are Fixed; Blocked when contract drift or DecisionStatus=Pending.
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
- Status: Open (Audit Hold: normalized contract pack; resumable by explicit Go/NoGo)
- Rule: unresolved queue item blocks Proceed; contract drift is routed back to A1 only.

### AC/DoD補完
- Added lane-level NoGo rule: no transition to next phase when queue is reopened, dependency is inverted, or contract link is missing.
- Added lane-level DoD rule: handoff payload must include `contractId`, `decision status`, `rollback trigger`, and `next owner`.

### docs-check
- Validation command: `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`.

### 次レーンhandoff
- Next lane receives reference-only contract context and may not redefine A1 contract values.

## Stream F planning整理（2026-04-12）

> 本セクションを Stream F の正規運用レイヤとして扱う。既存記述と矛盾する場合は本セクションを優先する。

### Phase 1 Read（対象9ファイル再読）
- 本ファイル群のみを対象に読み合わせを完了。
- 編集境界は planning memo のみとし、`03_Implement/**` は変更禁止。

### Phase 2 ADR CDC
- ADR追加は行わず、既存 `Context / Decision / Consequences` の整合確認に限定。
- 新規アーキ判断が必要になった場合は本レーン内で実装へ進まず停止。

### Phase 3 Plan（A1→A2→A3 直列契約）
- 依存順序を `A1 interface-contract -> A2 mock-validation -> A3 implementation` に固定。
- A2/A3で契約本文を再定義しない（参照専用）。
- 他レーン完了待ちは禁止し、本レーン内の契約順序・停止条件整備のみ実施。

### Phase 4 Execute（監査ホールド状態の整流）
- 旧 `Ready/Active` は運用語彙として使用せず、`Open (Audit Hold)` を維持。
- `Open -> In Progress` へは、契約整合・docs-check成功・担当判断の3条件を満たした時のみ遷移可。

### Phase 5 Verify（docs-check）
- 検証コマンドは以下に固定する。
  - `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- 検証失敗時の自己修復は最大3回まで。

### Phase 6 Proceed
- Go条件: 契約順序整合 / 監査ホールド整流 / docs-check 成功。
- NoGo条件: 依存矛盾、未定義競合、指定外ファイル更新要求、自己修復3回超過。

### 失敗停止ルール（Stream F 固定）
- 競合検知時は即停止し、競合一覧と再開条件を記録する。
- 修復上限は3回。4回目に達する前に必ず停止報告する。

## Stream H normalization snapshot（latest）

### Phase 1 Read（Audit Hold前提確認）
- A1/A2/A3の3メモを再読し、`Status=Open (Audit Hold)` と `Priority=P0` を再確認。

### Phase 2 Plan（A1→A2→A3直列正規化）
- `A1 -> A2 -> A3` を唯一の進行順序として固定。
- A2/A3ではA1契約本文を改変せず、参照のみ許可。

### Phase 3 Execute（契約ID・用語・依存整合）
- `ContractID` と参照先契約（`DependsOnContractID` / `ReferenceContractID`）の一致を確認。
- 用語ゆれを抑制し、依存逆転要求はA1差し戻し。

### Phase 4 Verify
- `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` を実行基準に固定。
- 依存不整合・契約衝突・未定義競合があれば停止。

### Phase 5 Proceed
- Go条件: 契約整合・検証成功・停止条件未該当。


## Stream H normalization contract pack (2026-04-13)

- Scope: legacy Audit Hold群の再開性を揃えるため、状態語彙・依存順序・契約リンクを監査再現可能な最小単位へ正規化する（新規実装なし）。
- Backlog lane: `FB-P2B-02`
- Canonical contract: `CTR-2B-02-DECISION-LOG-V1`
- Serial dependency: `A1 -> A2(mock) -> A3(implementation-ready contract only)`
- Mock policy: A2/A3 はモック/fixture/stub前提で参照可能状態を維持し、実コード変更要求を発行しない。

### Resume gate (Go/NoGo)

1. `ContractID/DependsOnContractID/ReferenceContractID` の三点一致を再確認する。
2. `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` が成功する。
3. 担当レーンが `Open (Audit Hold)` から `In Progress` へ昇格する明示判断を記録する。

### Stop conditions（fail-fast）

- 契約ID不整合、依存順序逆転、未定義競合を検知した場合は即停止。
- Self-correction は最大3回。3回超過時は更新を停止し、競合一覧のみ提出する。


## Stream C serial execution update（2026-04-14）

- Stream role: `Stream C（FB-P2B A1/A2/A3）` 専属。
- Contract input policy: 他ストリーム成果物は immutable な契約入力として扱い、待ち合わせを行わない。
- Target lane: `A1 interface contract`
- Locked Contract ID: `CTR-2B-02-DECISION-LOG-V1`

### Phase 1 Read同期（差分確認）
- Plan: A1/A2/A3の3メモを再読し、`ContractID / DependsOnContractID / ReferenceContractID` の差分を確認。
- Execute: 3メモの契約キーを照合し、記法ゆれ・依存順序逆転の有無を点検。
- Verify: 差分なし（`CTR-2B-02-DECISION-LOG-V1` で一致）。
- Proceed: Phase 2へ進行。

### Phase 2 A1契約固定
- Plan: A1で固定済みの契約ID・型・比較キーを再固定し、A2/A3は参照専用で運用。
- Execute: 契約拡張要求・キー変更要求・順序非決定要求をA1差し戻し条件として明文化。
- Verify: 契約再定義禁止を維持。
- Proceed: Phase 3へ進行。

### Phase 3 A2モック検証定義
- Plan: 実コード非依存で、stub/fixtureのみの検証条件を固定。
- Execute: 非自動確定・再読込復元・順序保持（およびenum境界がある場合は4値制約）を検証条件として保持。
- Verify: A2定義はA1契約参照のみで成立。
- Proceed: Phase 4へ進行。

### Phase 4 A3接続条件固定
- Plan: A3開始条件/停止条件/差し戻し条件を契約準拠で固定。
- Execute: A3は実装接続の入口定義のみとし、契約変更は受け付けない。
- Verify: `A1 -> A2 -> A3` 直列依存を維持。
- Proceed: Phase 5へ進行。

### Phase 5 Verify
- Plan: docs-checkでメモ整合を検証し、失敗時は自己修復を最大3回まで実施。
- Execute: `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` を基準コマンドとする。
- Verify: Self-Correction counter = `0/3`（本更新時点）。
- Proceed: 3回超過時は停止して競合一覧のみ報告。

## Stream F serial execution update（2026-04-14）

- Stream role: `Stream F（FB-P2B planning memo）` 専任。
- Edit scope: `01_Plans/issues/issue-FB-P2B-01-*.md` / `01_Plans/issues/issue-FB-P2B-02-*.md` のみ。
- Immutable policy: 上記以外は編集禁止。

### Phase 1: Read
- Plan: 当該レーンの A1/A2/A3 を再読し、`ContractID / DependsOnContractID / ReferenceContractID` を照合する。
- Execute: 契約ID三点一致、依存順序 `A1 -> A2 -> A3`、Priority `P0` を確認する。
- Verify: 差分・逆順依存・契約未定義がないことを確認する。
- Proceed: Pass時のみ Phase 2 へ進行する。

### Phase 2: A1契約（CDC）
- Plan: CDC（Contract-Driven Consistency）として A1 の契約凍結を再確認する。
- Execute: 契約再定義禁止、契約拡張要求は A1 差し戻し、A2/A3 は参照専用を固定する。
- Verify: `ContractID` の変更要求がないことを確認する。
- Proceed: Pass時のみ Phase 3 へ進行する。

### Phase 3: A2 mock validation仕様
- Plan: 実コード非依存で mock/fixture/stub 前提の検証仕様を固定する。
- Execute: 非自動確定・再読込復元・順序保持（および契約で定義された enum 境界）を必須観点として扱う。
- Verify: A2仕様が A1 契約参照のみで完結していることを確認する。
- Proceed: Pass時のみ Phase 4 へ進行する。

### Phase 4: A3 implementation readiness
- Plan: A3 の開始条件/停止条件/差し戻し条件を契約準拠で固定する。
- Execute: 実装接続は readiness 定義までとし、契約変更を受け付けない。
- Verify: `A1 -> A2 -> A3` の直列依存と handoff 入力の固定を確認する。
- Proceed: Pass時のみ Phase 5 へ進行する。

### Phase 5: Verify（README lifecycle整合）
- Plan: docs-check と issue lifecycle（`Draft -> Open -> In Progress -> Done`）の整合を検証する。
- Execute: `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` を基準コマンドとして実行する。
- Verify: README の lifecycle 記述と矛盾しない状態語彙（Open/In Progress/Done）に揃っていることを確認する。
- Proceed: 整合が取れた場合のみ Go、未整合は NoGo として停止条件へ遷移する。

### 強制サイクル / フェイルセーフ
- Self-repair は最大 3 回まで（`0/3` から開始し、4回目相当は実施しない）。
- 致命条件（契約ID不整合、依存順序逆転、編集禁止領域の更新要求、README lifecycle との不整合未解消）を検知した場合は即停止する。
- 停止時は「競合一覧・停止理由・再開条件」を記録し、推測で進行しない。

## Stream A Serial Contract Lock (2026-04-16)

### Phase 1 Read（再Read + 差分抽出）
- 本ファイルを含む Stream A 管轄10ファイルを再Readし、契約ID / Gate式 / 禁止遷移を照合。
- 差分抽出結果:
  - `a1Status=="Done" && pendingDecisionQueueCount==0` を唯一ゲートとして維持。
  - `schemaVersion=1.0.0` / `overridePolicy=human_dual_control_only` / `contractLinkLocked=true` / `sharedResourceFreeze=true` を固定値として維持。
  - 契約ID衝突・依存逆転・未定義競合は 0 件。

### Phase 2 ADR CDC
- Context: A1契約固定を下流A2/A3の参照専用境界として維持する。
- Decision: 新規ADR追加は不要（既存 ADR-0026/0027/0028 と整合）。未承認決定は確定扱いしない。
- Consequences: 契約変更要求はA1へ差戻し、下流はread-only handoff値のみ利用する。

### Phase 3 Plan
- AC/DoD不足時はドラフト提案を先行し、`agreementStatus=agreed` まで Execute へ進まない。
- SSOT固定値:
  - `schemaVersion=1.0.0`
  - `overridePolicy=human_dual_control_only`
  - `contractLinkLocked=true`
  - `sharedResourceFreeze=true`
- Go/No-Go:
  - `Go = (a1Status=="Done" && pendingDecisionQueueCount==0 && schemaVersion=="1.0.0" && overridePolicy=="human_dual_control_only" && contractLinkLocked==true && sharedResourceFreeze==true)`
  - `NoGo = !Go`

### Phase 4 Execute
- 文言・契約ID・依存順序（A1→A2→A3）・停止条件を本ファイル内で同期。
- 禁止遷移を固定:
  - `Pending` bypass（`Pending -> Approved/Rejected` 以外）
  - A1未完了時の A2/A3 `Draft -> Open`
  - 未承認決定の確定扱い
- Read-only handoff:
  - `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
  - `contractIds=A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|A1-ERROR-IF`

### Phase 5 Verify
- `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- `rg -n "a1Status=="Done" && pendingDecisionQueueCount==0|schemaVersion=1.0.0|overridePolicy=human_dual_control_only|contractLinkLocked=true|sharedResourceFreeze=true|Pending -> Approved|Pending -> Rejected" 01_Plans/issues/issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md 01_Plans/issues/issue-HIL-RS-02-A1-governance-contract-hardening.md 01_Plans/issues/issue-HIL-RS-02-next-phase-delivery-plan.md 01_Plans/issues/issue-HIL-RS-01-next-phase-human-loop-reversible-synthesis.md`
- Self-Correctionは最大3回。4回目相当は即停止。

### Phase 6 Proceed
- 再開条件: `NoGo` 要因（未承認決定、識別子不一致、依存逆転）を解消し、再VerifyがPassすること。
- 差戻し先: `issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`（A1契約正本）。
- Decision Queue未解決項目は `Pending` のまま保持し、確定扱いしない。

### Fail-safe（停止報告テンプレ）
1. 失敗条件
2. 影響ファイル・契約ID
3. 人間判断が必要な選択肢（2案）
   - 案1: 既存固定値を維持してA1へ差戻し
   - 案2: 承認会議で固定値変更を決定後に再凍結

## Stream H execution update（2026-04-16 / FB-P2B-02 A1）

### Phase 1 Read
- 先頭Read: `issue-FB-P2B-02-a1-interface-contract.md` / `issue-FB-P2B-02-a2-mock-validation.md` / `issue-FB-P2B-02-a3-implementation.md`
- 判定: `CTR-2B-02-DECISION-LOG-V1` の三点一致を基準固定。

### Phase 2 Plan
- A1契約凍結を維持し、A2/A3は参照専用で直列進行する。

### Phase 3 Execute
- action 4値制約・append/list/restore I/F・非自動確定境界を変更禁止で維持する。

### Phase 4 Verify
- `A1 -> A2 -> A3` 依存逆転なしを確認する。

### Phase 5 Proceed
- self-correctionは最大3回、超過時は停止。

## Stream C serial execution update（2026-04-16 / P2B-02 A1）

### Phase 1: Read同期（6ファイル）
- Read: `issue-FB-P2B-01-a1/a2/a3-*.md` + `issue-FB-P2B-02-a1/a2/a3-*.md`
- Verify: `CTR-2B-02-DECISION-LOG-V1` のA1/A2/A3契約キー一致を確認（Pass）。

### Phase 2: A1契約（CDC）整理
- Decision: `CTR-2B-02-DECISION-LOG-V1` を単一正本として維持。
- CDC freeze: `append/list/restore` 署名と action 4値制約を固定。

### Phase 3-4: 接続条件
- A2 mock固定: append順序・非自動確定・snapshot復元を前提化。
- A3接続固定: 契約参照のみ、enum拡張・必須項目変更はA1差し戻し。

### Phase 5: Verify / Proceed
- Verify command: `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- Self-repair: `0/3`（未実施）。
- Proceed: Go（停止条件の発火なし）。


## Stream F CDC fixed-cycle update（2026-04-17）

- Fixed rule: `CDC -> Plan -> Execute -> Verify -> Proceed`
- Repair cap: Self-correction is limited to 3 attempts; stop on the 4th equivalent attempt.

### CDC
- Contract lock re-check: `ContractID=CTR-2B-02-DECISION-LOG-V1` remains immutable.
- Serial dependency re-check: `A1 -> A2 -> A3` only.
- Drift guard: no enum extension, no required-field change, no contract-link rewrite.

### Plan
- Keep A1 as the single source of truth for decision-log interface contract.
- Limit scope to docs-only normalization in `01_Plans/issues/`.

### Execute
- Reassert A1 fixed set (`MergeDecisionRecord`, `DecisionLogStoreContract`, mock signatures).
- Reassert rollback triggers (enum change / nondeterministic restore / auto-apply request).

### Verify
- Verification command: `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`.
- Pass criteria: contract metadata consistency without introducing new unresolved keys.

### Proceed
- Go only when CDC and docs-check both pass.
- If failed, perform self-correction up to 3 times and stop with blocker list when exceeded.
