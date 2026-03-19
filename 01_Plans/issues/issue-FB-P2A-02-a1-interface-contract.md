# Issue Draft: FB-P2A-02-A1 Collapse/Expand操作 / インターフェース先行（型/契約）

- Type: Feature request
- Status: Ready (A1 Contract Fixed)
- Priority: P0
- Owner: Stream D
- Scope: `01_Plans/issues/` (planning memo only)
- Related Backlog: `FB-P2A-02`
- Related ADR/Spec: `ADR-0007`, `ADR-0001`, `02_Architecture/architecture.md`
- Expected verification level: `docs-check`

## Requirement meta I/F（共通キー）

- RequirementID: `RQ-2A-02`
- RequirementStatement: `Collapse/Expand操作` の境界I/F（型・必須項目・契約リンク）を先行固定する。
- Phase: `A1 Interface First`
- PriorityClass: Must
- GoNoGoGate: Required
- SecurityGateImpact: N/A（計画のみ）
- VerificationLevel: docs-check
- DecisionStatus: Fixed

## Phase management（Stream D）

- Phase 1: Read同期（A1/A2/A3の3点再読）
- Phase 2: A1契約点検（I/F固定と契約ドリフト検知）
- Phase 3: A2モック検証計画固定（M1..M4・責務分離）
- Phase 4: A3 handoff条件固定（GoNoGoと停止条件）
- Phase 5: Verify（記述整合・依存整合）

## Contract definition（A1成果物）

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
- Stream D の担当範囲は P2A 専用 issue の契約固定・モック検証設計・実装引き渡し条件の文書化に限定される。
- 本作業では UI 実装方法や renderer 詳細を決めず、入力/出力契約だけを先に固定する必要がある。

### Decision

- ContractID を `CTR-2A-02-COLLAPSE-EXPAND-V1`、InterfaceName を `IslandVisibilityContractV1` として固定する。
- collapse/expand は `isCollapsed` と `hidden*Ids` の view 契約で表現し、document 構造変更とは分離する。
- A2/A3 は A1 契約本文を変更せず、ContractID / InterfaceName / Required fields / Invariants の一致確認のみ行う。

### Consequences

- A2 は描画実装に依存せず fixture ベースで検証できる。
- A3 は view 状態遷移と非破壊性を入力契約として受け取れる。
- SafeMode / share-export の既定挙動を後退させる変更は本契約の対象外として明示固定される。

## A1 contract audit（Stream D / Phase 2）

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

## Validation plan

- Command:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`

## Fail-safe

- self-correction上限: 3回。連続失敗時はProceed禁止で停止。
- 停止トリガ: Ready条件崩壊 / 依存逆転 / 未定義競合 / ContractID衝突を検出した場合は即時停止して報告。

## Decision Queue整理（Stream D）

| QueueID | Topic | Status | Decision | Proceed Impact |
|---|---|---|---|---|
| DQ-FB-P2A-02-001 | ContractID固定 (`CTR-2A-02-COLLAPSE-EXPAND-V1`) | Closed | A1で固定 | A2可 |
| DQ-FB-P2A-02-002 | 判定順（expand/collapseの優先条件） | Closed | A1定義順を固定 | A3可 |
| DQ-FB-P2A-02-003 | view state非破壊性 | Closed | document構造変更を禁止 | A2/A3可 |
| DQ-FB-P2A-02-004 | 逸脱時の差し戻し経路 | Closed | A1のみ受付 | A2/A3可 |

## Proceed判定（A2/A3）

- 可否: **可**
- 根拠: 契約ID・判定順・停止条件をA1メモで固定済み。
- 残リスク: 境界ケース追加はA2 fixture 拡張で対応し、契約改定は行わない。

## Stream D固定シグネチャ / 検証キー（A2/A3引き渡し）

- Fixed signature:
  - `contractLinkLocked=true`
  - `sharedResourceFreeze=true`
- Verification keys:
  - `contractId`
  - `contractVersion`（`IslandVisibilityContractV1`）
  - 必須フィールド一覧
- Rule:
  - A2/A3は上記キーの一致確認のみ実施し、契約本文は改訂しない。
