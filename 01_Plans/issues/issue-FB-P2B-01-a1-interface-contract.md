# Issue Draft: FB-P2B-01-A1 Similar-card候補提示 / インターフェース先行（型/契約）

## Edit Control (2026-04-17)

- Edit authorization scope: this file only within FB-P2B-01 A1/A2/A3 serial lane.
- Serial lock: `A1 contract freeze -> A2 mock validation -> A3 implementation handoff`.
- Out-of-scope policy: editing non-target files is prohibited; contract changes must be routed back to A1.

- Type: Feature request
- Status: Done
- Source Issue: N/A (GitHub Issues are not used in current operations)
- Priority: P0
- Owner: Stream D（FB-P2B + FB-P0 baseline lane）
- Scope: `01_Plans/issues/` (planning memo only)
- Related Backlog: `FB-P2B-01`
- Related ADR/Spec: `ADR-0007`, `ADR-0001`, `02_Architecture/schemas.md`
- Dependencies: `FB-P2B-01`
- Expected verification level: `docs-check`

## Dependencies

- DependsOn: none（A1 contract root）
- Unblocks: issue-FB-P2B-01-a2-mock-validation.md / issue-FB-P2B-01-a3-implementation.md
- Gate/Blocker: Ready when ContractID・Required fields・Invariants・ContractLinks are Fixed; Blocked when contract drift or DecisionStatus=Pending.
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

### Context
- `FB-P2B-01` のDoD（candidate group一覧 + 対象Card確認）を満たすには、候補データ契約をA1で単一正本化する必要がある。
- A2/A3で groupキーや比較キーが揺れると、mock fixture・restore期待値・UI観測条件が同時に崩れる。
- `02_Architecture/schemas.md` のID/配列/スナップショット志向に合わせ、A1は docs-only で境界型を固定する。

### Decision
- 契約ID `CTR-2B-01-CANDIDATE-GROUP-V1` をA1で凍結し、A2/A3は参照のみ許可する。
- 比較キーは `groupId` / `targetCardId` / `snapshotVersion` / `candidateCardIds[]` 順序に固定する。
- API署名は mock/stub で検証可能な `loadCandidateGroups(input) -> CandidateListViewModel` の形で定義し、候補提示以外（merge自動確定・代表カード更新）は契約外とする。

### Consequences
- A2は fixtureベースで API署名・型・比較キーを検証できる。
- A3は契約追従のみ許可され、追加フィールド・比較キー変更・確定ロジック追加要求はA1差し戻しになる。
- Gate未承認・契約矛盾・未定義競合が発生した場合、推測実装に進まず停止できる。

## 固定契約（A1成果物 / Contract Freeze）

- ContractFreeze:
  - `contractLinkLocked=true`
  - `sharedResourceFreeze=true`
  - `a2ReferenceOnly=true`
  - `a3ReferenceOnly=true`

### Domain types

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

### Mock-ready API signature（A2/A3参照専用）

- `CandidateQueryInput`:
  - `targetCardIds?: string[]`
  - `snapshotVersion: string`
- `CandidateQueryOutput`:
  - `viewModel: CandidateListViewModel`
- `MockValidationSignature`:
  - `loadCandidateGroups(input: CandidateQueryInput): CandidateQueryOutput`

### Comparison keys / deterministic rules

- Group equality key: `groupId`
- Target equality key: `targetCardId`
- Restore boundary key: `snapshotVersion`
- Ordered fields:
  - `candidateCardIds[]`
  - `groups[]`
- Out of scope:
  - merge auto-commit
  - representative card overwrite
  - scoring algorithm specification

## 実装ハンドオフ定義（Template Freeze）

### Input Contract
- A2/A3は `CTR-2B-01-CANDIDATE-GROUP-V1` を唯一参照する。
- mock入力は `CandidateQueryInput.snapshotVersion` を必須とし、`targetCardIds` は optional filter として扱う。
- fixtureは `CandidateListViewModel.totalGroupCount === groups.length` を満たす。

### Expected Output
- `loadCandidateGroups` は `CandidateQueryOutput.viewModel` を返し、`groups[]` の順序を保持する。
- 同一 `snapshotVersion` では同一 `groupId` / `targetCardId` / `candidateCardIds[]` を再現できる。
- 候補提示のみで merge state は確定しない。

### Rollback Trigger
- `ContractID` の変更要求が出た場合。
- `candidateCardIds[]` または `groups[]` の順序非決定が判明した場合。
- merge自動確定や代表カード更新を同一タスクへ混在させる要求が出た場合。

## Phase 1-5（Stream E運用: Plan → Execute → Verify → Proceed）

### Phase 1: Read同期
- Plan: 3ファイルとA2/A3参照先を読み、Gate条件と契約順序を再確認する。
- Execute:
  - Read: `issue-FB-P2B-01-a1-interface-contract.md` / `issue-FB-P2B-01-a2-mock-validation.md` / `issue-FB-P2B-01-a3-implementation.md`
  - 判定: `A1 ContractID = A2 DependsOnContractID = A3 ReferenceContractID = CTR-2B-01-CANDIDATE-GROUP-V1`（Pass）
- Verify: 依存矛盾なし、優先度はP0で一致。
- Proceed: Phase 2へ進行。

### Phase 2: A1契約凍結
- Plan: Context / Decision / Consequences を固定し、A2/A3参照専用リンクを明文化する。
- Execute:
  - 固定ルール: 契約本文改訂は禁止、逸脱要求はA1差戻し。
  - 参照リンク: `issue-FB-P2B-01-a2-mock-validation.md` / `issue-FB-P2B-01-a3-implementation.md`
- Verify: 契約本文と参照導線がA1に閉じている（Pass）。
- Proceed: Phase 3へ進行。

### Phase 3: Mock-ready化
- Plan: API署名・型・比較キーをmockで検証可能に整備する。
- Execute:
  - `MockValidationSignature=loadCandidateGroups(input: CandidateQueryInput): CandidateQueryOutput`
  - 比較キー: `groupId` / `targetCardId` / `snapshotVersion` / ordered arrays
  - 非自動確定（候補提示のみ）を維持
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
  - `issue-FB-P2B-01-a2-mock-validation.md`
  - `issue-FB-P2B-01-a3-implementation.md`
- 変更禁止項目:
  - `ContractID=CTR-2B-01-CANDIDATE-GROUP-V1`
  - `SimilarCandidateGroup` / `CandidateListViewModel` / `CandidateQueryInput` / `CandidateQueryOutput`
  - 比較キー（`groupId` / `targetCardId` / `snapshotVersion` / ordered arrays）
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

## Stream D serial execution update（2026-04-17）

- Stream role: `Stream D（FB-P2B-01 A1/A2/A3）` 専属。
- Edit scope: `issue-FB-P2B-01-a1/a2/a3` の3メモのみ。
- Working rule: `Plan -> Execute -> Verify -> Proceed` を固定し、契約不整合は即停止。

### Phase 1: Read同期
- Plan: A1/A2/A3を再読し、契約リンク整合（`ContractID/DependsOnContractID/ReferenceContractID`）を再確認する。
- Execute: `CTR-2B-01-CANDIDATE-GROUP-V1` の三点一致と依存順序 `A1 -> A2 -> A3` を照合。
- Verify: 差分なし（Pass）。
- Proceed: Phase 2へ進行。

### Phase 2: ADR CDC（必要時のみ）
- Plan: 新規ADRは作成せず、既存A1契約のCDC（Context/Decision/Consequences）整合だけを確認する。
- Execute: A1契約凍結・A2/A3参照専用・契約変更はA1差戻しの3条件を再固定。
- Verify: 契約再定義要求なし（Pass）。
- Proceed: Phase 3へ進行。

### Phase 3: Plan（AC/DoD合意）
- Plan: A1 AC/DoDの不足有無を確認し、未定義依存がないことを確認する。
- Execute: AC-2B-1 / DoD-2B-1 と停止条件（契約不整合・未定義依存・3回超過停止）を維持。
- Verify: 不足なし（Pass）。
- Proceed: Phase 4へ進行。

### Phase 4: Execute（A1契約）
- Plan: A1は契約固定点として、A2/A3への入力境界のみを提供する。
- Execute: `CTR-2B-01-CANDIDATE-GROUP-V1`、型定義、比較キー、ordered arrays を固定維持。
- Verify: A2/A3が参照専用で利用可能（Pass）。
- Proceed: Phase 5へ進行。

### Phase 5: Verify / Proceed
- Plan: docs-checkでメモ整合を確認し、失敗時は自己修復を最大3回まで許可する。
- Execute: `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- Verify: Pass（Self-Correction: `0/3`）。
- Proceed: A2 mock validation lane へ引き渡し可能。
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
- QueueID: `DQ-FB_P2B_01_A1_INTERFACE_CONTRACT-STREAM-G-2026-04-12`
- Status: Done (2026-04-19 Stream C serial completion: A1→A2→A3 closed)
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
- Backlog lane: `FB-P2B-01`
- Canonical contract: `CTR-2B-01-CANDIDATE-GROUP-V1`
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
- Locked Contract ID: `CTR-2B-01-CANDIDATE-GROUP-V1`

### Phase 1 Read同期（差分確認）
- Plan: A1/A2/A3の3メモを再読し、`ContractID / DependsOnContractID / ReferenceContractID` の差分を確認。
- Execute: 3メモの契約キーを照合し、記法ゆれ・依存順序逆転の有無を点検。
- Verify: 差分なし（`CTR-2B-01-CANDIDATE-GROUP-V1` で一致）。
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

## Stream H execution update（2026-04-16 / FB-P2B-01 A1）

### Phase 1 Read
- 先頭Read: `issue-FB-P2B-01-a1-interface-contract.md` / `issue-FB-P2B-01-a2-mock-validation.md` / `issue-FB-P2B-01-a3-implementation.md`
- 判定: `ContractID=CTR-2B-01-CANDIDATE-GROUP-V1` を三点照合の基準として固定。

### Phase 2 Plan
- A1は契約凍結のみを扱い、A2/A3へ参照専用で引き渡す。

### Phase 3 Execute
- 契約ID・必須フィールド・比較キーを維持し、契約拡張要求は差し戻し対象とする。

### Phase 4 Verify
- 直列依存 `A1 -> A2 -> A3` と Gate条件を確認する。

### Phase 5 Proceed
- Go条件: 契約整合が維持され、停止条件に非該当。
- Stop条件: 契約不整合/未定義競合/3回失敗で停止。

## Stream C serial execution update（2026-04-16 / P2B-01 A1）

### Phase 1: Read同期（6ファイル）
- Read: `issue-FB-P2B-01-a1/a2/a3-*.md` + `issue-FB-P2B-02-a1/a2/a3-*.md`
- Verify: `CTR-2B-01-CANDIDATE-GROUP-V1` / `CTR-2B-02-DECISION-LOG-V1` のA1/A2/A3参照がそれぞれ一致（Pass）。

### Phase 2: A1契約（CDC）整理
- Decision: `CTR-2B-01-CANDIDATE-GROUP-V1` を CDC の単一正本として維持し、A2/A3は参照専用。
- Consequences: 契約拡張・比較キー変更・順序非決定要求はA1差し戻し。

### Phase 3-4: 接続条件
- A2 mock固定: `loadCandidateGroups` の非自動確定・順序保持・snapshot復元。
- A3接続固定: `A1 -> A2 -> A3` 直列、契約再定義禁止。

### Phase 5: Verify / Proceed
- Verify command: `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- Self-repair: `0/3`（未実施）。
- Proceed: Go（未定義依存 / 契約ドリフト / 指定外編集要求は未検知）。

## Stream D execution update（2026-04-17）

- Stream role: `Stream D（FB-P2B + FB-P0 baseline専属）`
- Workflow lock: `Plan -> Execute -> Verify -> Proceed`
- Serial lock: `A1 contract freeze -> A2 mock validation -> A3 implementation handoff`
- Fail-safe: Gate未承認 / 契約矛盾 / 未定義競合 / Self-Correction 3回超過で即停止

### Phase 1 Read
- Plan: P0優先度、A1→A2→A3順序、編集境界を確認する。
- Execute: 本メモの契約IDと関連A1/A2/A3リンクを再照合した。
- Verify: 契約順序と優先度に矛盾なし（Pass）。
- Proceed: Phase 2へ進行。

### Phase 2 ADR CDC
- Plan: 変更が方針に触れる場合のみ `Context / Decision / Consequences` を追加し承認待ちにする。
- Execute: 本更新は契約リンク固定と検証導線の整理に限定。
- Verify: 新規ADR判断なし（Pass）。
- Proceed: Phase 3へ進行。

### Phase 3 Plan
- Plan: mock-ready API署名・比較キー・rollback条件をA1契約に対して固定する。
- Execute: DependsOn/Reference契約IDを単一参照点として保持。
- Verify: A2/A3が契約参照のみで継続可能（Pass）。
- Proceed: Phase 4へ進行。

### Phase 4 Execute
- Plan: baselineとP2B A1/A2/A3間の契約リンクを固定する。
- Execute: 逆流要求はA1差し戻し、A2/A3で契約再定義を禁止。
- Verify: 契約矛盾・未定義競合なし（Pass）。
- Proceed: Phase 5へ進行。

### Phase 5 Verify
- Plan: docs-check、依存矛盾0、競合0、修復3回上限を確認する。
- Execute: `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` を基準検証とする。
- Verify: fail-safeを満たさない場合は即停止。
- Proceed: Stream Dレーンの契約更新を維持。

## Stream C serial execution update（2026-04-17 / FB-P2B-01 A1）

- Stream role: `Stream C（FB-P2B-01 A1→A2→A3）` 専属。
- Edit scope: `issue-FB-P2B-01-a1-interface-contract.md` / `issue-FB-P2B-01-a2-mock-validation.md` / `issue-FB-P2B-01-a3-implementation.md` の3件のみ。
- Independence rule: 外部契約に依存しない。必要契約はA1でローカル明文化する。

### Phase 1 Read（毎回）
- Read: A1/A2/A3の3メモを再読し、契約キー一致を確認。
- Verify: `ContractID=CTR-2B-01-CANDIDATE-GROUP-V1` がA1/A2/A3で一致（Pass）。

### Phase 2 ADR CDC（必要時）
- Context: 本更新は既存契約の固定運用であり、新規ADR起票は不要。
- Decision: CDCはA1契約に従属し、A2/A3で再定義しない。
- Consequences: 契約変更要求はA1へ差し戻し。

### Phase 3 Plan（AC/DoD提案）
- AC/DoDは既存 `AC-2B-1` / `DoD-2B-1` を継続適用。
- 追加提案: なし（不足検知なし）。

### Phase 4 Execute（A1→A2→A3）
- A1担当: 契約型・比較キー・ordered arraysを固定。
- Handoff: A2/A3はA1契約参照のみで実行。

### Phase 5 Verify（Self-Correction <=3）
- Verify command: `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- Self-Correction policy: 最大3回。4回目相当は停止。

### Phase 6 Proceed
- Proceed条件: 契約一致・依存順序維持・停止条件非該当。
- Stop template（推測継続禁止）:
  - 原因: 契約不整合 / 未定義競合 / 検証3回超過
  - 影響: A2/A3へのhandoff停止
  - 要承認事項: 契約変更要否（A1再凍結の承認）


## Stream C serial execution update（2026-04-18 / FB-P2B-01 A1）

### Phase 1 Read（4ファイル再読）
- 再読対象: baseline + A1 + A2 + A3（固定4ファイル）。
- 契約照合: A1 `ContractID` / A2 `DependsOnContractID` / A3 `ReferenceContractID` = `CTR-2B-01-CANDIDATE-GROUP-V1`（一致）。
- 依存照合: `A1 -> A2 -> A3`（維持）。

### Phase 2 ADR CDC（必要時のみ）
- 判定: **不要**（契約変更要求なし、Context/Decision/Consequencesの追記不要）。

### Phase 3 Plan（直列前提の固定）
- A1で固定する範囲を再確認:
  - Contract ID / Domain types / API signature / deterministic keys。
- A2/A3への制約:
  - 参照専用（再定義禁止）
  - 逸脱要求はA1差し戻し。

### Phase 4 Execute（契約凍結の再反映）
- A1契約凍結を同日更新として記録し、A2/A3へ同一契約IDで引き渡し可能状態を維持。

### Phase 5 Verify（docs-check + 参照一致）
- `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` 実行対象に含めて確認。
- 判定: 契約ID参照の不整合なし。
- Self-Correction: 0/3。

### Phase 6 Proceed
- Go（A1固定契約を維持したままA2/A3へ進行可能）。
- Fail-safe: 契約ドリフト / 未定義競合 / 修復3回超過で停止。

## Stream C serial lock update（2026-04-18）

- Stream role: `Stream C` 専任。
- Fixed ContractID: `CTR-2B-01-CANDIDATE-GROUP-V1`
- Serial lock: `A1 freeze -> A2 mock -> A3 handoff`
- Non-goal: `03_Implement/**` 編集禁止。

### Phase 1 Read
- A1/A2/A3の3メモを再読し、`ContractID` 整合を確認。
- 判定: `A1 ContractID = A2 DependsOnContractID = A3 ReferenceContractID = CTR-2B-01-CANDIDATE-GROUP-V1`（Pass）。

### Phase 2 ADR CDC
- 契約変更が必要な場合のみ CDC（Context/Decision/Consequences）を明文化する。
- 承認取得まで停止し、A1以外で契約再定義しない。

### Phase 3 Plan
- AC/DoD不足は `draft proposal -> agreementStatus=agreed` でのみGo。
- 合意未了の不足がある場合は次Phaseへ進まない。

### Phase 4 Execute
- A1は契約固定点として `ContractID/型/比較キー/順序` を維持。
- 契約再定義要求はA1差し戻し。

### Phase 5 Verify
- `docs-check` + ContractID整合 + 非自動確定ルール維持を確認。
- self-correctionは最大3回。4回目修復に入る前に停止。

### Phase 6 Proceed
- 実装レーンへの受け渡しは `read-only contract handoff` のみ許可。
- Fail-safe: 契約逸脱 / 優先度逆転 / 未定義競合 / 4回目修復要求で停止。



## Stream D update (2026-04-18): Phase 1-5 authoritative ledger

> このセクションを Stream D の最新運用記録として扱う。旧ログと矛盾する場合は本セクションを優先する。

### Phase 1) Read
- Plan: A1/A2/A3 と baseline を再読し、`ContractID/DependsOnContractID/ReferenceContractID` の一致を確認する。
- Execute: `CTR-2B-01-CANDIDATE-GROUP-V1` の三点一致、`Priority=P0`、依存順序 `A1 -> A2 -> A3` を確認した。
- Verify: 不整合なし（Pass）。
- Proceed: Phase 2 へ進行。

### Phase 2) A1契約整備
- Plan: A1は契約単一正本として固定し、A2/A3を参照専用にする。
- Execute: 以下を固定した。
  - ContractID: `CTR-2B-01-CANDIDATE-GROUP-V1`
  - 比較キー: `groupId / targetCardId / snapshotVersion / ordered arrays`
  - 非目標: 自動確定・契約再定義
- Verify: 契約境界が A1 に閉じている（Pass）。
- Proceed: Phase 3 へ進行。

### Phase 3) A2モック検証条件整備
- Plan: mock/stub のみで検証可能な条件をA1側に明文化する。
- Execute: `loadCandidateGroups(input)` と deterministic restore 条件、非自動確定条件を A2 参照要件として固定した。
- Verify: A2が実装非依存で開始可能（Pass）。
- Proceed: Phase 4 へ進行。

### Phase 4) A3実装条件整備
- Plan: A3開始条件・停止条件・差し戻し条件を A1基準で固定する。
- Execute: 契約逸脱要求はA1差し戻し、A3での契約追加禁止を明記した。
- Verify: A3 handoff の判定境界が明確（Pass）。
- Proceed: Phase 5 へ進行。

### Phase 5) Baseline統合前提
- Plan: baseline 側へ優先順位と直列実行条件を引き渡す。
- Execute: `P0` 優先、`A1 -> A2 -> A3`、未定義競合時停止、Self-Correction上限3回を共有した。
- Verify: baseline統合に必要な固定値が揃っている（Pass）。
- Proceed: Stream D baseline統合フェーズへ引き渡し。

### CDC / 停止条件
- CDC（Contract-Driven Consistency）追加要求が発生した場合は **承認取得まで停止** する。
- Self-Correction は最大3回。4回目相当は停止して競合一覧のみ記録する。


## Stream D strict serial lock update（2026-04-18 / FB-P2B-01 A1）

- Scope lock: 本更新は `issue-FB-P2B-01-a1/a2/a3` + baseline の4ファイル参照同期のみ。
- Workflow lock: `Plan -> Execute -> Verify -> Proceed` を固定し、A1を契約SSOTとして維持する。

### Phase 1: Read
- 4ファイル再Readで契約ID・優先度・順序を照合。
- 判定: `ContractID=CTR-2B-01-CANDIDATE-GROUP-V1`、Priority=`P0`、順序=`A1 -> A2 -> A3`（Pass）。

### Phase 2: ADR CDC（契約意味変更時のみ）
- CDC起票条件: ContractIDの意味、比較キー意味、非自動確定ルール意味が変わる場合のみ。
- 本更新判定: 契約意味変更なしのため CDC追加なし（承認待ちなし）。

### Phase 3: Plan
- A1 AC/DoD不足ドラフト判定: 既存 `AC-2B-1` / `DoD-2B-1` で充足、追加ドラフト不要。
- 下流固定条件: A2/A3は参照専用（契約再定義禁止）。

### Phase 4: Execute
- P2B契約ID単一参照点を `CTR-2B-01-CANDIDATE-GROUP-V1` に固定維持。
- baseline側への同期は参照関係のみ（契約本文の再定義禁止）。

### Phase 5: Verify
- Validator: `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`。
- 契約ID整合: `A1 ContractID == A2 DependsOnContractID == A3 ReferenceContractID`。
- Self-Correction上限: 最大3回（4回目相当で停止）。

### Phase 6: Proceed
- Go条件: 参照整合=OK、競合=0、優先度逆転=0。
- Fail-safe停止条件: 依存矛盾 / 契約ドリフト / 未定義競合 / 修復4回目相当。


## Stream C exclusive completion update（2026-04-19）

- Scope lock: edited only `issue-FB-P2B-01-a1-interface-contract.md` / `issue-FB-P2B-01-a2-mock-validation.md` / `issue-FB-P2B-01-a3-implementation.md`。
- Fail-safe precheck: `ContractID/DependsOnContractID/ReferenceContractID` 一致、依存順序 `A1 -> A2 -> A3`、指定外編集要求なし。

### Phase 1 Read
- Phase開始時再Read: 上記3ファイルを再読。
- Plan: 契約ID・依存順序・停止条件を照合する。
- Execute: `CTR-2B-01-CANDIDATE-GROUP-V1` 三点一致を確認。
- Verify: 不一致なし（Pass）。
- Proceed: Phase 2へ。

### Phase 2 A1固定
- Phase開始時再Read: 上記3ファイルを再読。
- Plan: A1契約を再凍結し、方針変更なしを確認する。
- Execute: `SimilarCandidateGroup` / `CandidateListViewModel` / 比較キー固定を再確認。
- Verify: 既存方針に変更なし（ADR更新不要、承認待ち事項なし）。
- Proceed: Phase 3へ。

### Phase 3 A2モック
- Phase開始時再Read: 上記3ファイルを再読。
- Plan: mock/fixture前提で順序保持・非自動確定・再読込復元を保持する。
- Execute: A2の検証条件をA1契約参照のみで再固定。
- Verify: 契約拡張要求なし、依存逆転なし（Pass）。
- Proceed: Phase 4へ。

### Phase 4 A3接続
- Phase開始時再Read: 上記3ファイルを再読。
- Plan: A3を契約参照専用ハンドオフとして閉じる。
- Execute: A3開始条件/停止条件/差し戻し条件をA1/A2整合のまま確定。
- Verify: 実装先行・契約再定義の混入なし（Pass）。
- Proceed: Phase 5へ。

### Phase 5 Verify
- Phase開始時再Read: 上記3ファイルを再読。
- Plan: docs-checkで整合を確認し、必要時のみ自己修復（最大3回）。
- Execute: `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` を実行。
- Verify: Pass（self-correction 0/3）。
- Proceed: FB-P2B-01 A1→A2→A3 を Stream C 単独で完遂としてクローズ。

## Stream I Done/Completed Audit (2026-04-23)
- 判定: 再オープン不要（Done/Completed/Closedの完了根拠と整合）。
- Related ADR/Spec: 参照先リンク切れなし（存在確認済み）。
- 重複Backlog整理提案: FB-P2B-01 は系列メモ複数運用（3件）。再オープンではなく、次回は親統合メモ1本＋派生メモ参照化を提案。

## Stream C completion checkpoint（2026-05-03）

- Phase flow: Plan → Execute → Verify → Proceed を A1→A2→A3 直列で完了。
- Contract consistency: A1/A2/A3 の ContractID 参照は不整合なし。
- Fail-safe: 契約逸脱・未定義競合は未検知、Self-Correction は 0/3。
- Proceed decision: Go（次レーンへ引き渡し可能）。

