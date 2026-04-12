# Issue Draft: FB-P2A-01-A1 Island階層モデル導入 / インターフェース先行（型/契約）

- Type: Feature request
- Status: Open (Audit Hold: legacy Ready normalized; not a new-start target)
- Priority: P0
- Owner: Stream F
- Scope: `01_Plans/issues/` (planning memo only)
- Related Backlog: `FB-P2A-01`
- Related ADR/Spec: `ADR-0007`, `ADR-0001`, `02_Architecture/schemas.md`
- Expected verification level: `docs-check`

## Requirement meta I/F（共通キー）

- RequirementID: `RQ-2A-01`
- RequirementStatement: `Island階層モデル導入` の境界I/F（型・必須項目・契約リンク）を先行固定する。
- Phase: `A1 Interface First`
- PriorityClass（Must / Should / Could）: Must
- GoNoGoGate（Required / Optional / N/A）: Required
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: N/A（計画のみ）
- VerificationLevel（docs-check / unit / integration / e2e）: docs-check
- DecisionStatus（Fixed / Pending）: Fixed

## Phase management（Stream D）

- Phase 1: Read同期（A1/A2/A3の3点再読）
- Phase 2: A1契約点検（I/F固定と契約ドリフト検知）
- Phase 3: A2モック検証計画固定（M1..M4・責務分離）
- Phase 4: A3 handoff条件固定（GoNoGoと停止条件）
- Phase 5: Verify（記述整合・依存整合）

## Contract definition（A1成果物）

- ContractID: `CTR-2A-01-ISLAND-HIERARCHY-V1`
- InterfaceName: `IslandHierarchyContractV1`
- ContractFreeze:
  - `contractLinkLocked=true`
  - `sharedResourceFreeze=true`
- ContractLinks:
  - Upstream: `ADR-0007 FB-P2A-01`
  - Downstream-A2: `issue-FB-P2A-01-a2-mock-validation.md`
  - Downstream-A3: `issue-FB-P2A-01-a3-implementation.md`
- Required fields:
  - `document.schemaVersion: string`
  - `island.id: string`
  - `island.cardIds: string[]`
  - `island.parentIslandId?: string`（rootは未設定許容）
- Invariants:
  - `parentIslandId` が存在する場合、参照先 island は同一 document 内に存在する。
  - `parentIslandId` のみを正本とし、子一覧は派生情報としてA1契約に含めない。
  - self-parent を含む循環参照は許可しない。
  - import 正規化では不正な `parentIslandId` を `undefined` にフォールバックできる。
  - save/load roundtrip では有効な `parentIslandId` を欠落させず往復保持する。

## Context / Decision / Consequences（A1固定化）

### Context

- `02_Architecture/schemas.md` は FB-P2A-01 の単一正本として `parentIslandId?: string` を定義している。
- Stream D の担当範囲は P2A 専用 issue の契約固定・モック検証設計・実装引き渡し条件の文書化に限定される。
- 実装コードや共有ファイルを更新せずに、A2/A3 が同一契約を参照できる状態を先に作る必要がある。

### Decision

- ContractID を `CTR-2A-01-ISLAND-HIERARCHY-V1`、InterfaceName を `IslandHierarchyContractV1` として固定する。
- 階層表現は `parentIslandId` を正本に採用し、`childIslandIds` のような派生情報は A1 契約必須項目へ含めない。
- A2/A3 は A1 契約本文を変更せず、ContractID / InterfaceName / Required fields / Invariants の一致確認のみ行う。

### Consequences

- `02_Architecture/schemas.md` と矛盾しない最小契約で A2/A3 を直列進行できる。
- 子一覧キャッシュや UI 都合の派生表現は A3 実装検討の裁量として残るが、A1 契約破壊変更は禁止される。
- SafeMode / share-export / 実装コードには影響を持ち込まない。

## A1 contract audit（Stream D / Phase 2）

- 契約項目確定:
  - `ContractID=CTR-2A-01-ISLAND-HIERARCHY-V1`
  - `InterfaceName=IslandHierarchyContractV1`
  - Required fields / Invariants / ContractLinks を固定対象として継続維持。
- I/F境界確定:
  - A2へは `contractId`,`contractVersion`,`mockCaseId`,`validationResult`,`ownerOfFix`,`evidence` を受け渡す。
  - A3は上記I/Fを受信専用で扱い、A1契約本文を再定義しない。
- 非目標（Non-goals）:
  - 永続スキーマ昇格判断、UI仕様追加、03_Implement配下の実装変更は本Issueの対象外。
  - SafeMode/share-export既定値の変更は対象外。

## ADR起票要否（Phase 2判定）

- 判定: **起票不要（No ADR proposal）**
- Context:
  - 既存 `ADR-0007` と `02_Architecture/schemas.md` のDoD具体化であり、新規設計方針の導入ではない。
- Decision:
  - A1契約はIssue内固定で管理し、ADR改定は行わない。
- Consequences:
  - A2/A3は契約固定前提で直列進行可能。
  - 価値判断変更が発生した場合のみADR追加トリガへ遷移する。

## Phase execution log（A1）

### Read sync（Phase開始時）

- `issue-FB-P2A-01-a1-interface-contract.md`
- `issue-FB-P2A-01-a2-mock-validation.md`
- `issue-FB-P2A-01-a3-implementation.md`

### Plan

- `CTR-2A-01-ISLAND-HIERARCHY-V1` の固定対象（Required fields / Invariants / ContractLinks）を確定する。
- A2/A3で契約変更を禁止する freeze 条件を明記する。

### Execute

- Required fields と Invariants をA1成果物として記述し、A2/A3リンクを固定。
- SafeMode・share/export既定挙動に非影響であることを明記。

### Verify

- ContractLinks が A1→A2→A3 で到達可能であることを確認。
- A2/A3で参照する ContractID / InterfaceName が一致することを確認。

### Proceed

- A2へ引き渡す固定契約として `CTR-2A-01-ISLAND-HIERARCHY-V1` を採用し、A1を完了状態とする。

## Acceptance criteria

- [x] A1で ContractID / Required fields / Invariants / ContractLinks が固定される。
- [x] A2/A3は本契約を変更せず参照のみで進行できる。
- [x] `02_Architecture/schemas.md` と整合する（`parentIslandId` 正本、root未設定許容）。
- [x] SafeMode・share/export既定挙動を変更しないと明記される。
- [x] 契約リンク不整合がない（A1→A2→A3）。

## State sync / conflict check

- Phase開始時Read対象:
  - `issue-FB-P2A-01-a1-interface-contract.md`
  - `issue-FB-P2A-01-a2-mock-validation.md`
  - `issue-FB-P2A-01-a3-implementation.md`
- 前回コミット差分競合がある場合は、契約リンク整合を優先して修正する。

## Handoff（A2/A3参照専用）

- Fixed links:
  - `issue-FB-P2A-01-a2-mock-validation.md`
  - `issue-FB-P2A-01-a3-implementation.md`
- 変更禁止項目:
  - `ContractID=CTR-2A-01-ISLAND-HIERARCHY-V1`
  - `InterfaceName=IslandHierarchyContractV1`
  - Required fields / Invariants / ContractLinks
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

- Command:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- Expected:
  - issue memoの命名とメタ項目が検証を通過する。

## Fail-safe

- self-correction上限: 3回。連続失敗時はProceed禁止で停止。
- 停止トリガ: Ready条件崩壊 / 依存逆転 / 未定義競合 / ContractID衝突を検出した場合は即時停止して報告。

## Decision Queue整理（Stream D）

| QueueID | Topic | Status | Decision | Proceed Impact |
|---|---|---|---|---|
| DQ-FB-P2A-01-001 | ContractID固定 (`CTR-2A-01-ISLAND-HIERARCHY-V1`) | Closed | A1で固定 | A2可 |
| DQ-FB-P2A-01-002 | A2/A3で契約変更禁止 | Closed | 逸脱はA1差し戻し | A3可 |
| DQ-FB-P2A-01-003 | `parentIslandId` 正本維持 | Closed | `childIslandIds` を必須契約から除外 | A2/A3可 |
| DQ-FB-P2A-01-004 | SafeMode後退禁止の適用確認 | Closed | 契約境界で後退禁止 | A2/A3可 |

## Proceed判定（A2/A3）

- 可否: **可**
- 根拠: ContractIDと必須フィールドが固定、Decision Queueの未処理項目なし。
- 残リスク: 派生子一覧の表現方式はA3検討対象だが、A1契約変更なしで扱う。

## Stream D固定シグネチャ / 検証キー（A2/A3引き渡し）

- Fixed signature:
  - `contractLinkLocked=true`
  - `sharedResourceFreeze=true`
- Verification keys:
  - `contractId`
  - `contractVersion`（`IslandHierarchyContractV1`）
  - 必須フィールド一覧
- Rule:
  - A2/A3は上記キーの一致確認のみ実施し、契約本文は改訂しない。

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
- QueueID: `DQ-FB_P2A_01_A1_INTERFACE_CONTRACT-STREAM-G-2026-04-12`
- Status: Closed
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

