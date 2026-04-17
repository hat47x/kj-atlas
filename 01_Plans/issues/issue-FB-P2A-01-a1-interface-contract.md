# Issue Draft: FB-P2A-01-A1 Island階層モデル導入 / インターフェース先行（型/契約）

- Type: Feature request
- Status: Open (Audit Hold: normalized contract pack; resumable by explicit Go/NoGo)
- Priority: P0
- Owner: Stream B（FB-P2A planning memo exclusive）
- Scope: `01_Plans/issues/` (planning memo only)
- Related Backlog: `FB-P2A-01`
- Related ADR/Spec: `ADR-0007`, `ADR-0001`, `02_Architecture/schemas.md`
- Expected verification level: `docs-check`

## Dependencies

- DependsOn: none（A1 contract root）
- Unblocks: issue-FB-P2A-01-a2-mock-validation.md / issue-FB-P2A-01-a3-implementation.md
- Gate/Blocker: Ready when ContractID・Required fields・Invariants・ContractLinks are Fixed; Blocked when contract drift or DecisionStatus=Pending.
## Requirement meta I/F（共通キー）

- RequirementID: `RQ-2A-01`
- RequirementStatement: `Island階層モデル導入` の境界I/F（型・必須項目・契約リンク）を先行固定する。
- Phase: `A1 Interface First`
- PriorityClass（Must / Should / Could）: Must
- GoNoGoGate（Required / Optional / N/A）: Required
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: N/A（計画のみ）
- VerificationLevel（docs-check / unit / integration / e2e）: docs-check
- DecisionStatus（Fixed / Pending）: Fixed

## Phase management（Stream B / FB-P2A serial lock）

- Phase 1 Read: A1/A2/A3 3点を再読し、ContractID・依存関係を照合する。
- Phase 2 ADR CDC: 方針変更がある場合のみ CDC を起票し、承認まで停止する。
- Phase 3 Plan: AC/DoD不足のドラフトを作成し、`agreementStatus=agreed` まで進行しない。
- Phase 4 Execute: A1契約固定 → A2 mock ledger固定 → A3 handoff固定を直列で実施する。
- Phase 5 Verify: docs-check + 契約リンク整合 + 自己修復上限3回を確認する。
## Contract definition（A1成果物）

- CDC（Contract Definition Checklist）:
  - C1: ContractID / InterfaceName の固定
  - C2: Required fields / Invariants の固定
  - C3: ContractLinks（A1→A2→A3）到達性の固定

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
- Stream B の担当範囲は FB-P2A 専用 issue の契約固定・モック検証設計・実装引き渡し条件の文書化に限定される。
- 実装コードや共有ファイルを更新せずに、A2/A3 が同一契約を参照できる状態を先に作る必要がある。

### Decision

- ContractID を `CTR-2A-01-ISLAND-HIERARCHY-V1`、InterfaceName を `IslandHierarchyContractV1` として固定する。
- 階層表現は `parentIslandId` を正本に採用し、`childIslandIds` のような派生情報は A1 契約必須項目へ含めない。
- A2/A3 は A1 契約本文を変更せず、ContractID / InterfaceName / Required fields / Invariants の一致確認のみ行う。

### Consequences

- `02_Architecture/schemas.md` と矛盾しない最小契約で A2/A3 を直列進行できる。
- 子一覧キャッシュや UI 都合の派生表現は A3 実装検討の裁量として残るが、A1 契約破壊変更は禁止される。
- SafeMode / share-export / 実装コードには影響を持ち込まない。

## A1 contract audit（Stream B / Phase 2）

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

## Serial completion marker（A1 segment）

- Phase 1（Read/CDC）: Completed
- Phase 2（Execute/Verify）: Completed
- Next gate: A2 Phase 3 へ直列引き渡し（A1契約はread-only固定）

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


## Stream B strict serial protocol（Phase 1→5）

### Phase 1 Read
- 対象ファイル（A1/A2/A3の3点）を**Phase開始時に必ず再Read**する。
- 照合項目: `Status` / `Priority(P0)` / `DecisionStatus` / `ContractID(またはDependsOnContractID)`。
- 不足監査: AC/DoD/停止条件/handoff条件。

### Phase 2 A1契約明確化（CDC明文化）
- Plan: A1契約（ContractID / Required fields / Invariants / ContractLinks）を固定対象として再確認する。
- Execute: 契約本文の再定義は行わず、固定I/Fの一致確認のみ実施する。
- Verify: A1→A2→A3依存の逆転・並列前提・契約ドリフトがないことを確認する。
- Proceed: A1固定が崩れた場合は停止し、A1へ差し戻す。

### Phase 3 A2モック検証計画更新
- Plan: M1..M4（正常/異常）と責務分離（A1/A2/A3）を再確認する。
- Execute: handoff payload（`contractId`,`contractVersion`,`mockCaseId`,`validationResult`,`ownerOfFix`,`evidence`）を固定入力として扱う。
- Verify: GoNoGo条件（`M1/M2/M3=pass` かつ `M4=fail`）の整合を確認する。
- Proceed: 判定不一致または責務未確定時は停止し、A2へ差し戻す。

### Phase 4 A3実装準備条件定義
- Plan: 実装入口は契約参照のみで開始できる条件を確認する。
- Execute: Plan→Execute→Verify→Proceed を固定順序で適用し、実装先行を禁止する。
- Verify: AC/DoD不足を検知した場合は `gapType` と `agreementStatus` を用いたドラフト提案を先行し、`agreementStatus=agreed` まで実行しない。
- Proceed: 合意済み条件と停止条件が同時に満たされる場合のみ下流へ引き渡す。

### Phase 5 Verify
- docs-check: `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- 依存参照整合・表記ゆれ・契約ID衝突を確認する。
- Self-Correction は最大3回。4回目相当は**停止して指示待ち**とする。

## Stream B execution override（FB-P2A A1→A2→A3）

- 同一レーン内依存は A1→A2→A3 の**直列処理のみ**を許可する。
- 外部レーン完了待ちは禁止し、依存解決は当該レーン内で閉じる。
- 各 Phase 開始時に A1/A2/A3 の3ファイルを再Readしてから着手する。
- 実行順序は **Plan→Execute→Verify→Proceed** を固定し、順序逆転時は停止する。
- Self-correction は最大3回とし、3回失敗で停止・報告する。

## Validation plan

- Command:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`

## Fail-safe

- self-correction上限: 3回。
- 停止トリガ: 3回超過 / 契約ドリフト / ownerOfFix未確定 / 指定外ファイル編集要求 / ContractID衝突。
- 指定外ファイル編集要求を検出した場合は停止する。
- 停止時対応: 推測継続を禁止し、停止理由と再開条件を記録して指示待ち。

## Stream B Serial Contract Lock (2026-04-16)

### Phase 1 Read（再Read + 差分抽出）
- 本ファイルを含む Stream B 管轄3ファイルを再Readし、契約ID / Gate式 / 禁止遷移を照合。
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

### Phase 5 Proceed
- 再開条件: `NoGo` 要因（未承認決定、識別子不一致、依存逆転）を解消し、再VerifyがPassすること。
- 差戻し先: `issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`（A1契約正本）。
- Decision Queue未解決項目は `Pending` のまま保持し、確定扱いしない。

### Fail-safe（停止報告テンプレ）
1. 失敗条件
2. 影響ファイル・契約ID
3. 人間判断が必要な選択肢（2案）
   - 案1: 既存固定値を維持してA1へ差戻し
   - 案2: 承認会議で固定値変更を決定後に再凍結

## Stream B Phase 1-2 completion snapshot（2026-04-16）

### Phase 1 Read（Plan→Execute→Verify→Proceed）
- Plan: A1/A2/A3 の3ファイルを再読し、`ContractID`・依存・Gate状態の照合観点を固定。
- Execute: `CTR-2A-01-ISLAND-HIERARCHY-V1` / `IslandHierarchyContractV1`、`DependsOn`、`GoNoGo` 定義を再照合。
- Verify: 契約ID衝突なし、依存逆転なし、DecisionStatus は3ファイルとも `Fixed` を確認。
- Proceed: A1契約を read-only 正本として Phase 2 へ進行。

### Phase 2 A1（Context / Decision / Consequences）
- Context: A1契約は `parentIslandId` 正本モデルとA1→A2→A3直列依存を固定する前提で維持する。
- Decision: A1契約本文の再定義は行わず、CDC（ContractID/Required fields/Invariants/ContractLinks）を承認待ち固定値として扱う。
- Consequences: A2/A3 は契約推測補完を禁止し、差分は検証手順・引継ぎ明確化のみに限定される。
- Approval state: `Pending human confirmation`（値の推測補完は未実施）。
