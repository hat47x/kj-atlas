# Issue Draft: FB-P2A-02-A1 Collapse/Expand操作 / インターフェース先行（型/契約）

- Type: Feature request
- Status: Open (Audit Hold: normalized contract pack; resumable by explicit Go/NoGo)
- Priority: P0
- Owner: Stream B（FB-P2A planning memo exclusive）
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
- Stream B の担当範囲は FB-P2A 専用 issue の契約固定・モック検証設計・実装引き渡し条件の文書化に限定される。
- 本作業では UI 実装方法や renderer 詳細を決めず、入力/出力契約だけを先に固定する必要がある。

### Decision

- ContractID を `CTR-2A-02-COLLAPSE-EXPAND-V1`、InterfaceName を `IslandVisibilityContractV1` として固定する。
- collapse/expand は `isCollapsed` と `hidden*Ids` の view 契約で表現し、document 構造変更とは分離する。
- A2/A3 は A1 契約本文を変更せず、ContractID / InterfaceName / Required fields / Invariants の一致確認のみ行う。

### Consequences

- A2 は描画実装に依存せず fixture ベースで検証できる。
- A3 は view 状態遷移と非破壊性を入力契約として受け取れる。
- SafeMode / share-export の既定挙動を後退させる変更は本契約の対象外として明示固定される。

## A1 contract audit（Stream B / Phase 2）

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
- Self-correction は最大3回までとし、**4回目に入る前に停止・報告**する。

## Unified execution rule lock（同一ルール固定）

- strict serial: A1→A2→A3 の直列のみ許可（並列禁止）。
- CDC必須: Contract Definition Checklist（C1/C2/C3）を各Phaseで再照合する。
- 各Phase開始Read: Phase開始時に A1/A2/A3 の3ファイルを再Readする。
- self-correction: 最大3回。4回目相当は停止して指示待ち。

## Validation plan

- Command:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`

## Fail-safe

- self-correction上限: 3回。
- 停止トリガ: 3回超過 / 契約ドリフト / ownerOfFix未確定 / 指定外ファイル編集要求 / ContractID衝突。
- 指定外ファイル編集要求を検出した場合は停止する。
- 停止時対応: 推測継続を禁止し、停止理由と再開条件を記録して指示待ち。

## Phase execution record（FB-P2A-02 / Stream B）

### Phase 1 Read（再Read済み）
- A1/A2/A3 の3ファイルを再Readし、`ContractID` / 依存順序 / `DecisionStatus` を照合。
- 結果: 依存順序は `A1 -> A2 -> A3` で整合、未定義競合なし。

### Phase 2 ADR CDC
- Context: 本件は `ADR-0007` 既存方針（collapse/expand の可視性制御）を契約I/Fへ固定する作業。
- Decision: 新規ADRは起票しない（No ADR proposal）。
- Consequences: 方針変更要求が出た場合のみA1で CDC 起票し、承認まで下流作業を停止する。

### Phase 3 Plan
- Plan→Execute→Verify→Proceed の固定順序を再確認。
- AC/DoD不足は `agreementStatus=agreed` まで進行禁止。

### Phase 4 Execute
- A1契約値（`CTR-2A-02-COLLAPSE-EXPAND-V1` / `IslandVisibilityContractV1`）を変更せず固定。
- A2/A3 への handoff を read-only 参照として維持。

### Phase 5 Verify / Proceed
- `docs-check` と A1→A2→A3 のリンク整合を確認して Proceed 可否を判定。
- self-correction は最大3回。4回目相当は停止して判断待ち。
- Proceed decision: **Completed（A1→A2→A3 を Stream B 単独で完遂）**。

## Stream B execution log (2026-04-18, FB-P2A-02 A1)

### Phase 1 Read
- A1/A2/A3 の3ファイルを再Readし、`ContractID=CTR-2A-02-COLLAPSE-EXPAND-V1` と依存順序 `A1 -> A2 -> A3` を再確認。

### Phase 2 ADR-CDC
- Context: 既存 `ADR-0007` の collapse/expand 方針をI/F契約へ固定する文書タスク。
- Decision: 新規ADR起票なし（方針変更なし）。
- Consequences: 契約差分要求が出た場合はA1へ差し戻し、承認待ち中は下流停止。

### Phase 3 Plan
- AC/DoD不足ドラフト判定: **不足なし**。
- `agreementStatus=agreed`（既存AC/DoDと停止条件が揃っているため）。

### Phase 4 Execute
- A1契約固定値（ContractID / InterfaceName / Required fields / Invariants / ContractLinks）を再ロックし、A2/A3への参照整合を確認。

### Phase 5 Verify
- docs-check と依存整合を Phase 5 で実施（詳細はA3実行ログで集約）。
- self-correction 回数: 0/3。

### Phase 6 Proceed
- Proceed判定: **Pass**（A1完了、A2へ進行可）。

## Stream B fixed I/F injection lock（FB-P2A-02）

- ContractID: `CTR-2A-02-COLLAPSE-EXPAND-V1`（Fixed）
- ContractVersion: `IslandVisibilityContractV1`（Fixed）
- Required fields（Fixed）:
  - `island.id`
  - `island.isCollapsed`
  - `view.hiddenDescendantIslandIds`
  - `view.hiddenCardIds`
- GoNoGo（Fixed）: `M1/M2/M3=pass` and `M4=fail`
- Phase 5 Verify minimum checks（Fixed）:
  - `docs-check`
  - 契約リンク整合（A1→A2→A3）
  - GoNoGo一致
- Phase 6 Proceed rule（Fixed）:
  - **NoGo の場合は停止し、A1へ差し戻す。**

## Stream B delta log (2026-04-18, FB-P2A-02 A1 lane re-check)

### Phase 1 Read re-check（ContractID/DependsOn/Unblocks）
- ContractID: `CTR-2A-02-COLLAPSE-EXPAND-V1`（A1固定）
- DependsOn: `none`（A1 contract root）
- Unblocks: `issue-FB-P2A-02-a2-mock-validation.md` / `issue-FB-P2A-02-a3-implementation.md`
- 判定: **整合（A1→A2→A3 の直列依存を維持）**

### Phase 3 Plan lock（A1→A2→A3）
- 直列計画を `A1 fixed contract -> A2 mock validation -> A3 handoff` で固定。
- AC/DoD不足は検出されず、`agreementStatus=agreed` を継続。

### Phase 5 Verify / Phase 6 Proceed
- Verify最小セット: `docs-check` + ContractLinks一致（A1→A2→A3）。
- Proceed rule: 矛盾検知時は **A1へ差戻し**。

## Stream B phase closure record (2026-04-19)

### Phase 1 Read
- A1/A2/A3 を再Readし、`DependsOn` / `Unblocks` / `ContractID` の一致を確認。

### Phase 2 A1 contract freeze
- Context / Decision / Consequences を再監査し、`CTR-2A-02-COLLAPSE-EXPAND-V1` と `IslandVisibilityContractV1` を凍結値として維持。
- 契約再定義は行わず、A2/A3 は read-only 参照のみを許可。

### Phase 3 Proceed gate
- A2へ渡す固定値（Required fields / Invariants / ContractLinks）を再確認し、A1 proceed 条件を継続して満たすことを確認。
