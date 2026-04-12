# Issue Draft: FB-P2A-02-A3 Collapse/Expand操作 / 実装計画接続

- Type: Feature request
- Status: Open (Audit Hold: legacy Ready normalized; not a new-start target)
- Priority: P0
- Owner: Stream J
- Scope: `01_Plans/issues/` (planning memo only)
- Related Backlog: `FB-P2A-02`
- Related ADR/Spec: `ADR-0007`, `issue-FB-P2A-02-a1-interface-contract.md`, `issue-FB-P2A-02-a2-mock-validation.md`
- Expected verification level: `docs-check`

## Requirement meta I/F（共通キー）

- RequirementID: `RQ-2A-02`
- RequirementStatement: A1/A2契約を逸脱せず、Collapse/Expand実装者向け引き渡し条件を固定する。
- Phase: `A3 Implementation`
- PriorityClass: Must
- GoNoGoGate: Required
- VerificationLevel: docs-check
- DecisionStatus: Fixed

## Phase management（Stream D）

- Phase 1: Read同期（A1/A2/A3の3点再読）
- Phase 2: A1契約点検（I/F固定と契約ドリフト検知）
- Phase 3: A2モック検証計画固定（M1..M4・責務分離）
- Phase 4: A3 handoff条件固定（GoNoGoと停止条件）
- Phase 5: Verify（記述整合・依存整合）

## Execution protocol（Plan→Execute→Verify→Proceed）

1. **Plan**
   - `isCollapsed` と `hidden*Ids` の更新責務を実装者向け入力契約へ分離して作業計画化。
2. **Execute**
   - `state transition -> render filter -> hit-test filter` の順で設計反映。
3. **Verify**
   - A2 mockCaseを使って遷移前後の整合をチェック。
4. **Proceed**
   - GoNoGoを満たした観点のみ次タスクへ進行。
   - 次タスク開始時はA1/A2/A3の3ファイルを再Readしてから着手する。

## Non-deviation rules

- A1契約をA3で再解釈しない。
- A2 Failケースを未解決のまま先送りしない。
- AC/DoD不足を検知した場合は、先にドラフト提案を追記して合意後に進行する。
- 実装コード・ファイルパス・関数名をA3契約本文へ持ち込まない。

## A2→A3 接続条件（確定）

- ContractLock:
  - `contractId=CTR-2A-02-COLLAPSE-EXPAND-V1`
  - `contractVersion=IslandVisibilityContractV1`
- Required input from A2:
  - `contractId=CTR-2A-02-COLLAPSE-EXPAND-V1`
  - `contractVersion=IslandVisibilityContractV1`
  - `mockCaseId in {M1,M2,M3,M4}`
  - `validationResult`
  - `ownerOfFix`
  - `evidence`
- GoNoGo判定:
  - Go: `M1/M2/M3=pass` かつ `M4=fail`、責務が確定。
  - NoGo: 判定不一致、または責務未確定。

## Implementation handoff contract（実装者向け固定条件）

### Input contract

- `contractId: string`
- `contractVersion: string`
- `mockCaseId: "M1" | "M2" | "M3" | "M4"`
- `validationResult: "pass" | "fail"`
- `ownerOfFix: "A1" | "A2" | "A3"`
- `evidence: string`

### Expected output

- `implementationReadiness: "go" | "no-go"`
- `acceptedMockCases: string[]`
- `blockedMockCases: string[]`
- `rollbackTrigger: string[]`
- `notes: string[]`

### Rollback conditions

- `contractId` または `contractVersion` がA1固定値と不一致。
- `mockCaseId` が欠損・重複・未知値を含む。
- `M1/M2/M3=pass` または `M4=fail` のGoNoGo条件が崩れる。
- `ownerOfFix` が未確定、または責務分離ルールと矛盾する。

## Acceptance criteria

- [x] A1/A2契約IDで実装計画トレースが可能。
- [x] Plan→Execute→Verify→Proceedの順序が固定される。
- [x] 実装者向けの入力契約 / 期待出力 / ロールバック条件が固定されている。
- [x] AC/DoD不足時のドラフト提案手順が明文化される。

## AC/DoD不足の事前提案I/F（合意前提）

- Required fields:
  - `gapId`
  - `gapType`（`AC` / `DoD`）
  - `phaseDetected`（`A1` / `A2` / `A3`）
  - `proposalDelta`
  - `agreementStatus`（`pending` / `agreed` / `rejected`）
- Proceed rule:
  - `agreementStatus=agreed` 以外はNoGo。

## Serial execution gate（A1→A2→A3）

- A3開始条件:
  - A2 handoff payload（`contractId`,`contractVersion`,`mockCaseId`,`validationResult`,`ownerOfFix`,`evidence`）が全件揃っている。
- A3停止条件:
  - 未定義競合を検出した場合は推測継続禁止、停止・報告。
- Self-repair上限:
  - 自己修復は最大3回。超過時は作業停止して報告。

## 実装トレース最小単位

| traceKey | source | destination |
|---|---|---|
| `RQ-2A-02` | A1 RequirementID | A3 task grouping key |
| `CTR-2A-02-COLLAPSE-EXPAND-V1` | A1 ContractID | A3 contract lock |
| `M1..M4` | A2 mockCaseId | A3 verification checklist |
| `ownerOfFix` | A2 failure routing | A3 backlog split (A1/A2/A3) |

## A3 implementation connection guard（Stream D / Phase 4）

- 着手条件（Start）:
  - `IslandVisibilityContractV1` がA1で固定され、A2ログがM1〜M4全件で存在する。
  - handoff I/F（`contractId`,`contractVersion`,`mockCaseId`,`validationResult`,`ownerOfFix`,`evidence`）に欠損なし。
- 停止条件（Stop）:
  - `M1/M2/M3=pass` かつ `M4=fail` が崩れた場合。
  - `ownerOfFix` がA2責務分離と矛盾した場合。
  - AC/DoD不足で `agreementStatus=agreed` が未達の場合。
- ロールバック条件（Rollback）:
  - A3で追加した前提・タスク分割を破棄し、A2確定ログを唯一の入力へ戻す。
  - 契約I/F変更要求はA1へ差し戻し、A3での再解釈を禁止する。

## State sync / conflict check

- Phase開始時Read対象:
  - `issue-FB-P2A-02-a1-interface-contract.md`
  - `issue-FB-P2A-02-a2-mock-validation.md`
  - `issue-FB-P2A-02-a3-implementation.md`
- Rule:
  - Phase開始ごとに上記3ファイルを再Readし、差分競合がある場合は推測継続せず停止・報告する。


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

- Command:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`

## Fail-safe

- 停止トリガ: Ready条件崩壊 / 依存逆転 / 未定義競合 / ContractID不一致を検出した場合は即時停止して報告。

## Stream D one-page handoff（Phase 5）

- 固定I/F（Fixed Interface）:
  - `contractId`,`contractVersion`,`mockCaseId`,`validationResult`,`ownerOfFix`,`evidence`
  - ContractLock: `CTR-2A-02-COLLAPSE-EXPAND-V1` / `IslandVisibilityContractV1`
- 許容差分（Allowed Delta）:
  - A3内の実装順序・タスク分割・検証手順の最適化（契約意味を変えない範囲）。
- 禁止変更（Forbidden Changes）:
  - A1 Required fields / Invariants / ContractLinks の改変。
  - GoNoGo条件（`M1/M2/M3=pass`, `M4=fail`）の変更。
  - SafeMode/share-export既定挙動に影響する仕様変更。

## Stream I normalization ledger（Phase 1-6 / Plan→Execute→Verify→Proceed）

### Phase 1 Read
- Plan: Status / Scope / DecisionStatus / Validation plan を抽出し、A1/A2/A3粒度を点検する。
- Execute:
  - Status: 既存本文の宣言値を採用。
  - Scope: `Implementation Handoff` に限定。
  - DecisionStatus: `Fixed`。
  - Validation command: `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`。
- Verify: 抽出項目が本メモ内で相互矛盾しないことを確認。
- Proceed: 矛盾がなければ Phase 2 へ進む。

### Phase 2 Plan
- Plan: AC/DoD不足の有無を点検し、不足時はドラフト提案I/Fで合意前提にする。
- Execute: 依存は `A1/A2 payload only` のみ許可し、実装ストリーム依存は mock I/F へ切り離す。
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
- QueueID: `DQ-FB_P2A_02_A3_IMPLEMENTATION-STREAM-G-2026-04-12`
- Status: Closed
- Rule: unresolved queue item blocks Proceed; contract drift is routed back to A1 only.

### AC/DoD補完
- Added lane-level NoGo rule: no transition to next phase when queue is reopened, dependency is inverted, or contract link is missing.
- Added lane-level DoD rule: handoff payload must include `contractId`, `decision status`, `rollback trigger`, and `next owner`.

### docs-check
- Validation command: `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`.

### 次レーンhandoff
- Next lane receives reference-only contract context and may not redefine A1 contract values.

