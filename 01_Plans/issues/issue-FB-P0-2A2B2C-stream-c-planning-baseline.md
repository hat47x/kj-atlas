# Issue Draft: FB-P0 (2A/2B/2C) Stream C planning baseline

- Type: Process
- Status: Open (Audit Hold: normalized contract pack; resumable by explicit Go/NoGo)
- Source Issue: N/A
- Priority: P0
- Owner: Stream H（audit normalization only）
- Scope: `01_Plans/issues/issue-FB-P0-2A2B2C-stream-c-planning-baseline.md` のみ
- Related Backlog: `FB-P2A-01/02`, `FB-P2B-01/02`, `FB-P2C-01`
- Related ADR/Spec: `ADR-0001`, `ADR-0007`, `ADR-0019`, `02_Architecture/island_shapes.md`, `02_Architecture/api.md`, `02_Architecture/schemas.md`
- Expected verification level: `docs-check`

---

## Baseline objective（Stream E）

- 目的: `FB-P2B-01/02 A1` と `FB-P0 baseline` の契約・実行準備を完了させる。
- 非目標: `FB-P2A*` / `HIL-RS*` / 共有統合ファイル / `03_Implement/**` の変更。
- Gate原則: Gate未承認、契約矛盾、未定義競合が出た場合は推測で強行せず即停止する。

## Phase 1: Read同期

### Plan
- Stream E編集許可ファイルのみを対象にし、共有統合ファイル・HIL系・実装コードが変更対象外であることを固定する。
- P2B A1契約（`CTR-2B-01-CANDIDATE-GROUP-V1` / `CTR-2B-02-DECISION-LOG-V1`）と P0優先度（P0）の整合を再確認する。
- 契約順序を `A1 -> A2 mock-validation -> A3 implementation` で固定する。

### Execute

| チェック項目 | 入力ソース | 判定 | 備考 |
| --- | --- | --- | --- |
| 編集境界 | Stream E 指示 | Pass | 許可3ファイルのみ編集 |
| P0優先度 | 本メモ + P2B A1メモ | Pass | すべて `Priority: P0` |
| A1契約ID整合 | `issue-FB-P2B-01/02-a1-interface-contract.md` | Pass | 参照契約ID不整合なし |
| 契約順序 | A1/A2/A3メモ | Pass | A1→A2→A3 直列 |
| 競合有無 | 管轄境界（共有/HIL/実装） | Pass | 対象外ファイルは非変更 |

### Verify
- Proceed 条件（編集境界固定 + P0優先度整合 + 契約ID整合 + 契約順序固定）を満たす。
- Stop 条件（依存矛盾 / 優先度矛盾 / 未定義競合）は現時点で非該当。

### Proceed
- Phase 2（A1契約凍結）へ進行。

---

## Phase 2: A1契約凍結

### Plan
- Stream Eのオーケストレーション方針を「Plan → Execute → Verify → Proceed」へ統一する。
- A1契約固定を前提とした A2/A3 進行順序を明文化し、契約改訂要求はA1差戻しへ限定する。
- A2/A3参照リンクをA1メモ側に固定し、baselineからも追跡できるようにする。

### Execute
- 方針固定:
  1. `Plan`: 依存・優先度・競合を先に確認
  2. `Execute`: 契約本文は改変せず、参照関係のみ更新
  3. `Verify`: 契約ID/優先度/停止条件をチェック
  4. `Proceed`: 次Phaseへ移行可否を明示
- 実行順序（P2B）:
  - `A1 interface-contract`（固定済）→ `A2 mock-validation` → `A3 implementation`
- 固定参照:
  - P2B-01: `issue-FB-P2B-01-a1-interface-contract.md` → `issue-FB-P2B-01-a2-mock-validation.md` / `issue-FB-P2B-01-a3-implementation.md`
  - P2B-02: `issue-FB-P2B-02-a1-interface-contract.md` → `issue-FB-P2B-02-a2-mock-validation.md` / `issue-FB-P2B-02-a3-implementation.md`
- 停止ルール:
  - 契約逸脱、未定義競合、優先度逆転を検知した時点で即停止。

### Verify
- P0 orchestrator方針は既存ADRの範囲内（新規アーキ決定なし）。
- 変更は計画メモ内に閉じ、実装依存なし（Pass）。

### Proceed
- Phase 3（Mock-ready化）へ進行。

---

## Phase 3: Mock-ready化

### Plan
- `FB-P2B-01` / `FB-P2B-02` のA1契約が mock/stub のみで検証可能な状態になっているかを確認する。
- API署名・型・比較キーをP0 baseline側でも一覧化し、A2開始条件を明文化する。

### Execute

| Contract | Fixed ID | Mock-ready API signature | 比較キー | 判定 |
| --- | --- | --- | --- | --- |
| P2B-01 candidate group | `CTR-2B-01-CANDIDATE-GROUP-V1` | `loadCandidateGroups(input)` | `groupId` / `targetCardId` / `snapshotVersion` / ordered arrays | Pass |
| P2B-02 decision log | `CTR-2B-02-DECISION-LOG-V1` | `appendDecision` / `listDecisionsByGroup` / `restoreDecisionLog` | `decisionId` / `groupId` / `snapshotVersion` / append order | Pass |

- Cross-check結果:
  - Priority: 2件ともP0で一致。
  - 依存順: A1→A2→A3の直列で一致。
  - 競合: 未定義競合なし。
  - Non-goal: 自動確定ロジックは両契約とも対象外。

### Verify
- A1契約はA2/A3の単一参照点として成立（Pass）。
- mock検証の開始条件（API署名・型・比較キー固定）が明文化済み（Pass）。

### Proceed
- Phase 4（実装ハンドオフ定義）へ進行。

---

## Phase 4: 実装ハンドオフ定義

### Plan
- A3でのimplementation接続を成立させるため、Input Contract / Expected Output / Rollback Trigger のテンプレートを baselineからも参照できるようにする。
- 実装依存を排除した handoff 条件を Stream E baseline に固定する。

### Execute
- 共通 handoff テンプレート:
  - `Input Contract`: A3はA1 ContractIDのみ参照し、A2で固定した API署名・型・比較キーを変更しない。
  - `Expected Output`: 同一 `snapshotVersion` に対して deterministic な restore/reload を維持し、候補提示/decision log いずれも自動確定を起こさない。
  - `Rollback Trigger`: ContractID変更要求、比較キー変更、順序非決定、または自動確定混入要求を検知した場合はA1へ差し戻し。
- 依存境界（許可）:
  - 契約ID一致確認
  - 型・必須フィールド・比較キー
  - fixture/stubベース検証
- 依存境界（禁止）:
  - `03_Implement/**` への実コード依存
  - backend/frontend実装詳細（アルゴリズム・永続化方式）への拘束
  - 共有統合ファイルへの直接編集

### Verify
- A2はmock前提で閉じた検証が可能（Pass）。
- A3開始前に実装依存を持ち込まない条件が明文化済み（Pass）。

### Proceed
- Phase 5（Verify / Proceed）へ進行。

---

## Phase 5: Verify / Proceed

### Plan
- 本メモとP2B A1メモ間で、優先度・依存順・競合停止条件・docs-checkの整合を最終確認する。
- Self-Correction を最大3回に制限し、超過時は停止する運用を固定する。

### Execute

| 観点 | 判定 | 根拠 |
| --- | --- | --- |
| 優先度整合 | Pass | すべて P0 |
| 依存整合 | Pass | A1→A2→A3 直列固定 |
| Mock-ready整合 | Pass | API署名・型・比較キー固定 |
| 競合記述整合 | Pass | 未定義競合は即停止で統一 |
| docs-check実施計画 | Pass | `validate_active_issue_memos.py` を単一確認コマンドに固定 |
| Self-Correction上限 | Pass | 最大3回、超過時停止 |

### Verify
- フェイルセーフ（依存矛盾/優先度矛盾/未定義競合で停止）を満たす。
- Stream Eの更新範囲は許可3ファイル内に限定されている。

### Proceed
- Stream E baseline更新を完了。A2/A3はA1固定契約を参照して継続可能。

---

## ADRルール適用記録

- 判定: **ADR更新不要**。
- 理由: 本更新は既存契約の参照整合・mock-ready化・handoffテンプレ整理であり、上位設計の新規決定を追加していない。
- 追跡: 契約ID変更、優先度変更、依存順序変更が発生した場合のみ `Context / Decision / Consequences` を先に作成し承認待ちへ移行。

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
  - `ok: validated <N> active issue memos`

## Self-Correction Log（最大3回）

1. 修正1: Phase構成をユーザー指定の5段（Read同期〜Verify/Proceed）へ再統一。
2. 修正2: P2B A1メモの mock-ready API署名・比較キー・handoffテンプレ参照をbaselineへ反映。
3. 修正3: フェイルセーフ停止条件（Gate未承認・契約矛盾・未定義競合・3回超過停止）を全Phaseへ統一適用。

> 上限超過時停止ルール: Self-Correction が 3 回を超える場合は更新を停止し、競合一覧を提出する。

## Stream I normalization ledger（Phase 1-6 / Plan→Execute→Verify→Proceed）

### Phase 1 Read
- Plan: Status / Scope / DecisionStatus / Validation plan を抽出し、A1/A2/A3粒度を点検する。
- Execute:
  - Status: 既存本文の宣言値を採用。
  - Scope: `baseline orchestration` に限定。
  - DecisionStatus: `N/A`。
  - Validation command: `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`。
- Verify: 抽出項目が本メモ内で相互矛盾しないことを確認。
- Proceed: 矛盾がなければ Phase 2 へ進む。

### Phase 2 Plan
- Plan: AC/DoD不足の有無を点検し、不足時はドラフト提案I/Fで合意前提にする。
- Execute: 依存は `FB-P2A-01/02, FB-P2B-01/02` のみ許可し、実装ストリーム依存は mock I/F へ切り離す。
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

## Stream G update (2026-04-12, planning memo only)

### Phase 1) Read同期
- Re-read baseline + incomplete P2A/P2B memos and confirmed serial order remains `A1 -> A2 -> A3` for each backlog lane.

### Phase 2) A1/A2/A3依存 + Decision Queue更新
| Lane | QueueID | Topic | Status | Proceed Impact |
| --- | --- | --- | --- | --- |
| `FB-P2A-01` | `DQ-FB-P2A-01-READINESS` | A1 fixed contract consumption by A2/A3 | Closed | A2/A3 proceed allowed |
| `FB-P2A-02` | `DQ-FB-P2A-02-READINESS` | A1 fixed contract consumption by A2/A3 | Closed | A2/A3 proceed allowed |
| `FB-P2B-01` | `DQ-FB-P2B-01-A1-FIXED` | A1 fixed contract guard | Closed | Downstream keeps reference-only mode |
| `FB-P2B-02` | `DQ-FB-P2B-02-A1-FIXED` | A1 fixed contract guard | Closed | Downstream keeps reference-only mode |

### Phase 3) AC/DoD不足補完
- Added common NoGo: unresolved queue / contract drift / undefined conflict => immediate stop.
- Added common DoD: each lane must keep `Priority=P0`, explicit stop trigger, and handoff payload fields.

### Phase 4) docs-check
- Baseline validator command remains: `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`.

### Phase 5) 次レーンhandoff
- Handoff checklist fixed for all lanes: `ContractID`, `DecisionQueue snapshot`, `Go/NoGo`, `Rollback Trigger`, `next owner`.

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
- 9ファイルを再読し、`Status=Open (Audit Hold)` と `Priority=P0` を確認。
- 対象依存を `A1 -> A2 -> A3` の直列に限定し、並列実行前提を禁止。

### Phase 2 Plan（A1→A2→A3直列正規化）
- P2A-01: `CTR-2A-01-ISLAND-HIERARCHY-V1`
- P2A-02: `CTR-2A-02-COLLAPSE-EXPAND-V1`
- P2B-01: `CTR-2B-01-CANDIDATE-GROUP-V1`
- P2B-02: `CTR-2B-02-DECISION-LOG-V1`
- A2/A3はA1契約の参照専用（契約本文改変禁止）で固定。

### Phase 3 Execute（契約ID・用語・依存整合）
- 用語を `ContractID / DependsOnContractID / ReferenceContractID` に統一。
- 依存逆転・契約ID衝突・未定義競合は即停止で統一。

### Phase 4 Verify
- `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` を共通検証コマンドとして維持。
- self-correction は最大3回、超過時停止。

### Phase 5 Proceed
- 再開は「契約整合 + docs-check成功 + 担当明示」の3条件が満たされた場合のみ。


## Stream H normalization contract pack (2026-04-13)

- Scope: legacy Audit Hold群の再開性を揃えるため、状態語彙・依存順序・契約リンクを監査再現可能な最小単位へ正規化する（新規実装なし）。
- Backlog lane: `FB-P2A-01/02`, `FB-P2B-01/02`, `FB-P2C-01`
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

## Stream H execution update（2026-04-16 / FB-P2B baseline監査）

- Scope lock: baseline は契約整合監査のみに限定し、実装・共有統合ファイル・他レーン仕様は変更しない。
- Serial rule: `FB-P2B-01` / `FB-P2B-02` ともに `A1 -> A2 -> A3` を直列固定し、逆順・並列着手を禁止。
- Phase start rule: 各Phase先頭で `A1/A2/A3` と本baselineを再Readして契約キー整合を確認する。
- Fail-safe: 契約不整合・未定義競合・停止条件該当時は即停止し、self-correctionは最大3回まで。


## Stream C serial update (2026-04-17)

### Phase 1) Read（Scope / AC確認）
- Scope を再確認し、本Issueは **issueメモ更新のみ** に限定する。
- AC/DoD・VerificationLevel・GoNoGoGate・DecisionStatus の整合を確認した。
- 禁止事項確認: 実装コードおよび Stream C/G 専有の `04_Documentation/e2e_testing.md` / `04_Documentation/security.md` / `04_Documentation/operations.md` には非接触。

### Phase 2) ADR CDC（方針変更時のみ）
- 判定: **追加ADR不要**。
- 理由: 本更新は計画メモのAC/DoD整備と検証手順の明確化に限定し、上位方針・アーキテクチャ決定を変更しない。

### Phase 3) Plan（AC/DoD不足の先行合意）
- 先行合意（本Issue共通）:
  - AC-C1: Scope / Non-goal / Verification を本文内で追跡可能にする。
  - AC-C2: Proceed条件とStop条件を本文に明示する。
  - DoD-C1: `docs-check + diff` の実行結果を記録する。
  - DoD-C2: 自己修復は最大3回。4回目相当は停止して競合報告に切り替える。

### Phase 4) Execute（直列更新）
- 本Issueを直列レーンの1件として更新し、他Issue同時編集は実施しない。
- 変更はメモ本文の運用記録・判定条件の追記に限定した。

### Phase 5) Verify（docs-check + diff、最大3回修復）
- 検証コマンド（共通）:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
  - `git diff --check`
- 検証ポリシー: 不一致時は当該Issueのみ最大3回まで自己修復し、超過時は即停止。

### Phase 6) Proceed（次Issueへ）
- 判定: **Proceed可能**（致命競合なし）。
- 次Issueへ進む前提: 同一ルール（Scope固定 / docs-check / 3回上限）をそのまま適用する。
