# Issue Draft: FB-P2A-02-A1 Collapse/Expand操作 / インターフェース先行（型/契約）

- Type: Feature request
- Status: Open (Audit Hold: normalized contract pack; resumable by explicit Go/NoGo)
- Priority: P0
- Owner: Stream G（FB-P2A planning memo exclusive）
- Scope: `01_Plans/issues/` (planning memo only)
- Related Backlog: `FB-P2A-02`
- Related ADR/Spec: `ADR-0007`, `ADR-0001`, `02_Architecture/architecture.md`
- Expected verification level: `docs-check`

## Dependencies

- DependsOn: none（A1 contract root）
- Unblocks: issue-FB-P2A-02-a2-mock-validation.md / issue-FB-P2A-02-a3-implementation.md
- Gate/Blocker: Ready when ContractID・Required fields・Invariants・ContractLinks are Fixed; Blocked when contract drift or DecisionStatus=Pending.
## Requirement meta I/F（共通キー）

- RequirementID: `RQ-2A-02`
- RequirementStatement: `Collapse/Expand操作` の境界I/F（型・必須項目・契約リンク）を先行固定する。
- Phase: `A1 Interface First`
- PriorityClass: Must
- GoNoGoGate: Required
- SecurityGateImpact: N/A（計画のみ）
- VerificationLevel: docs-check
- DecisionStatus: Fixed

## Phase management（Stream G）

- Phase 1: Read同期（A1/A2/A3の3点再読）
- Phase 2: A1契約明確化（CDC明文化）
- Phase 3: A2モック検証計画更新（M1..M4・責務分離）
- Phase 4: A3実装準備条件定義（GoNoGoと停止条件）
- Phase 5: Verify（記述整合・依存整合）

## Contract definition（A1成果物）

- CDC（Contract Definition Checklist）:
  - C1: ContractID / InterfaceName の固定
  - C2: Required fields / Invariants の固定
  - C3: ContractLinks（A1→A2→A3）到達性の固定

- ContractID: `CTR-2A-02-COLLAPSE-EXPAND-V1`
- InterfaceName: `IslandVisibilityContractV1`
- ContractFreeze:
  - `contractLinkLocked=true`
  - `sharedResourceFreeze=true`
- ContractLinks:
  - Upstream: `ADR-0007 FB-P2A-02`
  - Downstream-A2: `issue-FB-P2A-02-a2-mock-validation.md`
  - Downstream-A3: `issue-FB-P2A-02-a3-implementation.md`
- Required fields:
  - `island.id: string`
  - `island.isCollapsed: boolean`
  - `view.hiddenDescendantIslandIds: string[]`
  - `view.hiddenCardIds: string[]`
- Invariants:
  - `isCollapsed=true` の親配下は描画・ヒットテスト対象外。
  - `isCollapsed=false` で直近状態から復帰可能。
  - collapse/expand操作はdocument構造を破壊しない（view stateのみ変更）。
  - collapse/expand の評価は SafeMode / share-export 判定を変更しない。

## Context / Decision / Consequences（A1固定化）

### Context

- `ADR-0007` は collapse/expand で子要素が描画・ヒットテスト対象外になり、expandで復帰することを要求している。
- Stream E の担当範囲は P2A 専用 issue の契約固定・モック検証設計・実装引き渡し条件の文書化に限定される。
- 本作業では UI 実装方法や renderer 詳細を決めず、入力/出力契約だけを先に固定する必要がある。

### Decision

- ContractID を `CTR-2A-02-COLLAPSE-EXPAND-V1`、InterfaceName を `IslandVisibilityContractV1` として固定する。
- collapse/expand は `isCollapsed` と `hidden*Ids` の view 契約で表現し、document 構造変更とは分離する。
- A2/A3 は A1 契約本文を変更せず、ContractID / InterfaceName / Required fields / Invariants の一致確認のみ行う。

### Consequences

- A2 は描画実装に依存せず fixture ベースで検証できる。
- A3 は view 状態遷移と非破壊性を入力契約として受け取れる。
- SafeMode / share-export の既定挙動を後退させる変更は本契約の対象外として明示固定される。

## A1 contract audit（Stream E / Phase 2）

- 契約項目確定:
  - `ContractID=CTR-2A-02-COLLAPSE-EXPAND-V1`
  - `InterfaceName=IslandVisibilityContractV1`
  - Required fields / Invariants / ContractLinks をA1固定値として維持。
- I/F境界確定:
  - A2/A3は `contractId`,`contractVersion`,`mockCaseId`,`validationResult`,`ownerOfFix`,`evidence` を共通I/Fとして使用する。
  - collapse/expandの実装方法には依存せず、入出力契約のみ固定する。
- 非目標（Non-goals）:
  - 表示アルゴリズム詳細、UIイベント設計、03_Implement配下コード変更は対象外。
  - SafeMode/share-export既定の変更は対象外。

## ADR起票要否（Phase 2判定）

- 判定: **起票不要（No ADR proposal）**
- Context:
  - `ADR-0007` で確定済みの方針をI/Fへ具体化するタスク。
- Decision:
  - A1契約監査結果をIssueへ固定し、ADR更新は実施しない。
- Consequences:
  - A2/A3の直列実行で契約ドリフトを抑止できる。
  - 方針変更が必要な差分のみADR追加トリガへ回送する。

## Acceptance criteria

- [x] ContractID / Required fields / Invariants / ContractLinksが固定される。
- [x] A2/A3は本契約の参照のみで進行可能。
- [x] SafeMode既定やshare/export既定挙動を変更しない。
- [x] collapse/expand を view state の責務として固定している。

## Execution protocol（Plan→Execute→Verify→Proceed）

1. **Plan**
   - 可視性契約（`isCollapsed` / `hiddenDescendantIslandIds` / `hiddenCardIds`）の意味境界を固定する。
   - hit-test対象外条件（collapse時）をInvariantsへ明示する。
2. **Execute**
   - `CTR-2A-02-COLLAPSE-EXPAND-V1` / `IslandVisibilityContractV1` の Required fields / Invariants / ContractLinksを文書化し、A2/A3リンクを確定する。
3. **Verify**
   - ContractLinksの到達性（A1→A2→A3）と用語整合を確認する。
4. **Proceed**
   - ACを満たした場合のみA2へ進行する。未充足時はA1内で修復する。

## Serial execution gate（A1→A2→A3）

- A1完了条件:
  - `IslandVisibilityContractV1` のRequired fields / Invariants / ContractLinksが固定済み。
- A1 Proceed条件:
  - A2/A3参照先が有効、かつ未定義競合なし。

## State sync / conflict check

- Phase開始時Read対象:
  - `issue-FB-P2A-02-a1-interface-contract.md`
  - `issue-FB-P2A-02-a2-mock-validation.md`
  - `issue-FB-P2A-02-a3-implementation.md`
- Rule:
  - Phase開始ごとに上記3ファイルを再Readし、差分競合がある場合は推測継続せず停止・報告する。

## Handoff（A2/A3参照専用）

- Fixed links:
  - `issue-FB-P2A-02-a2-mock-validation.md`
  - `issue-FB-P2A-02-a3-implementation.md`
- 変更禁止項目:
  - `ContractID=CTR-2A-02-COLLAPSE-EXPAND-V1`
  - `InterfaceName=IslandVisibilityContractV1`
  - Required fields / Invariants / ContractLinks
  - `contractLinkLocked=true` / `sharedResourceFreeze=true`
- 逸脱要求はA1へ差し戻し。


## Stream G strict serial protocol（Phase 1→5）

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

## Stream G execution override（FB-P2A A1→A2→A3）

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
- 停止トリガ: 3回超過 / 依存不整合 / 指定外ファイル更新が必要 / ContractID衝突。
- 停止時対応: 推測継続を禁止し、停止理由と再開条件を記録して指示待ち。

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
