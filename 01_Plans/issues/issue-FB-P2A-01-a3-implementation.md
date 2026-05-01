# Issue Draft: FB-P2A-01-A3 Island階層モデル導入 / 実装計画接続

- Type: Feature request
- Status: Done
- Priority: P0
- Owner: Stream A（Critical Path / FB-P2A planning memo exclusive）
- Scope: `01_Plans/issues/` (planning memo only)
- Related Backlog: `FB-P2A-01`
- Related ADR/Spec: `ADR-0007`, `issue-FB-P2A-01-a1-interface-contract.md`, `issue-FB-P2A-01-a2-mock-validation.md`
- Dependencies: `FB-P2A-01`
- Expected verification level: `docs-check`

## Dependencies

- DependsOn: `issue-FB-P2A-01-a1-interface-contract.md` / `issue-FB-P2A-01-a2-mock-validation.md`
- Unblocks: downstream implementation lane only（no contract re-definition）
- Gate/Blocker: Ready when A1 Annex lock + A2 validation ledger are complete; Blocked on contract mismatch, missing mockCase, or unresolved ownerOfFix.

## Requirement meta I/F（共通キー）

- RequirementID: `RQ-2A-01`
- RequirementStatement: A1 Local Contract Annex と A2 validation ledger を逸脱せず、実装者向け引き渡し条件を固定する。
- Phase: `A3 Implementation`
- PriorityClass: Must
- GoNoGoGate: Required
- VerificationLevel: docs-check
- DecisionStatus: Fixed

## Contract references（Annex only）

- AnnexID: `LCA-FB-P2A-01-A1-V1`
- ContractID: `CTR-2A-01-ISLAND-HIERARCHY-V1`
- ContractVersion: `IslandHierarchyContractV1`
- Direct reference ban: A3本文から外部I/Fを直接参照しない（A1 AnnexおよびA2 ledgerのみ参照）。

## Phase management（Stream A / FB-P2A serial lock）

## Phase 3 Plan result（agreement record）

- agreementStatus: `agreed`
- agreedAt: `2026-04-18`
- Agreement scope: AC/DoD gaps are closed and Stream A serial order (`A1 -> A2 -> A3`) is locked.
- Note: no undefined conflict found; no external lane file edits required.

## Phase 4 Execute result（strict serial）

1. A1: `ContractID / Required fields / Invariants / ContractLinks` fixed（done）
2. A2: mock ledger (`M1..M4`) fixed under A1 Annex freeze（done）
3. A3: implementation handoff contract and rollback conditions fixed（done）

## Phase 5 Verify result

- docs-check target: `01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- verificationFocus: AC/DoD consistency, dependency alignment, contract drift absence
- selfCorrectionCount: `0/3`（no retry needed）

## Phase 6 Proceed decision

- proceedDecision: `ready-to-transition`
- nextStatusProposal: `FB-P2A-01 planning serial complete (Stream A)`
- stopConditionCheck: clear（no blocker）


- Phase 1 Read: A1/A2/A3 3点を再読し、Status/AC/DoD/依存を抽出する。
- Phase 2 ADR CDC: 方針変更がある場合のみ CDC を起票し、承認完了まで停止する。
- Phase 3 Plan: AC/DoD不足ドラフトを作成し、`agreementStatus=agreed` まで進行しない。
- Phase 4 Execute: A1契約固定 → A2 mock ledger固定 → A3 handoff固定を直列実施する。
- Phase 5 Verify: docs-check + 契約リンク整合 + 自己修復上限3回を確認する。
- Phase 6 Proceed: 完了条件成立時のみ次ステータス提案し、未達時は停止レポートを残す。

## Phase 1 Read result（差分抽出）

### 抽出（Status/AC/DoD/依存）
- Status: A1/A2/A3は Open。
- AC: 入力契約/期待出力/rollback条件は定義済み。
- DoD: 明示不足のためA3側にDoDを追加。
- 依存: A1 Annex lock と A2 ledger 完了がA3開始条件。

### 事前想定との差分
1. Stream B表記が残っていたため、Stream A専属に不一致。
2. A1 Annex経由参照の明示が不足。
3. DoDの定量的完了条件が不足。

## Execution protocol（Plan→Execute→Verify→Proceed）

1. **Plan**
   - A1 Annex必須項目とA2検証結果を実装者向け入力契約へマッピングする。
2. **Execute**
   - 変更順を `schema compatibility -> normalization -> persistence roundtrip` で固定する。
3. **Verify**
   - A2 handoff payloadの各ケースを実装観点で再照合する。
4. **Proceed**
   - GoNoGo判定を満たした項目のみ次タスクへ進める。

## Non-deviation rules

- A1 AnnexのRequired fields/InvariantsをA3で再定義しない。
- A2でFailとなったケースを未解決のまま先送りしない。
- AC/DoD不足検知時は、先にドラフト提案を追記してから進行する。
- 実装コード・ファイルパス・関数名をA3契約本文へ持ち込まない。

## A2→A3 接続条件（確定）

- ContractLock:
  - `annexId=LCA-FB-P2A-01-A1-V1`
  - `contractId=CTR-2A-01-ISLAND-HIERARCHY-V1`
  - `contractVersion=IslandHierarchyContractV1`
- Required input from A2:
  - `contractId=CTR-2A-01-ISLAND-HIERARCHY-V1`
  - `contractVersion=IslandHierarchyContractV1`
  - `mockCaseId in {M1,M2,M3,M4}`
  - `validationResult`
  - `ownerOfFix`
  - `evidence`
- GoNoGo判定:
  - Go: `M1/M2/M3=pass` かつ `M4=fail` で責務が確定している。
  - NoGo: 上記を満たさない、または責務未確定。

## Implementation handoff contract（実装者向け固定条件）

### Input contract

- `annexId: string`
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

- `annexId` / `contractId` / `contractVersion` がA1固定値と不一致。
- `mockCaseId` が欠損・重複・未知値を含む。
- `M1/M2/M3=pass` または `M4=fail` のGoNoGo条件が崩れる。
- `ownerOfFix` が未確定、または責務分離ルールと矛盾する。

## Acceptance criteria

- [x] A1 AnnexID / ContractID と A2ケースIDで実装計画へトレース可能。
- [x] Plan→Execute→Verify→Proceed がチェックリスト化されている。
- [x] 実装者向け入力契約 / 期待出力 / ロールバック条件が固定されている。
- [x] AC/DoD不足のドラフト提案手順が明文化されている。

## Definition of Done (DoD)

- [x] A1 Annex値とA2 ledger値がA3入力契約に完全転写されている。
- [x] GoNoGo判定条件が機械判読可能な形で記録されている。
- [x] NoGo時の返却先（A1/A2/A3責務）が定義されている。
- [x] A3本文から外部I/F直接参照が除去されている。

## Validation plan

- Command:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`

## Fail-safe

- self-correction上限: 3回。
- 停止トリガ: 3回超過 / 契約ドリフト / ownerOfFix未確定 / 前提崩壊 / 未定義競合 / 指定外ファイル編集要求。
- 停止時対応: 推測継続を禁止し、停止理由・再開条件・未達項目を記録して指示待ち。

## Stream I Done/Completed Audit (2026-04-23)
- 判定: 再オープン不要（Done/Completed/Closedの完了根拠と整合）。
- Related ADR/Spec: 参照先リンク切れなし（存在確認済み）。
- 重複Backlog整理提案: FB-P2A-01 は系列メモ複数運用（3件）。再オープンではなく、次回は親統合メモ1本＋派生メモ参照化を提案。

## Stream F execution log (2026-04-30, FB-P2A lane A3 + verify)

- Scope declaration（A3）: 最小3ファイルのみ更新を維持。実装領域への拡散なし（planning memo sync のみ）。
- Phase: **A3 implementation 接続完了**（A1/A2固定契約を参照した実装入力I/Fを維持）。
- Verify: `validate_active_issue_memos.py` 実行で issue メモ整合を確認。
- Issue同期: FB-P2A lane（A1→A2→A3）の直列実行記録を3ファイルへ反映し、依存順と停止条件を再固定。
- Proceed: 依存切断方針（A1後は mock 独立進行、外部待ち禁止）を継続条件として明記済み。

## Stream D serial execution record (2026-05-01, FB-P2A-01)

### Phase 1: Read同期
- A1/A2/A3 を再読し、依存 (`A1 -> A2 -> A3`)・AC/DoD・Gate状態を確認。

### Phase 2: ADR/CDC
- 契約変更要否を評価。既存契約の固定値運用で完結するため **CDC起票不要**。

### Phase 3: Plan
- A1完了条件: Contract/Annex固定 + `DecisionStatus=Fixed`。
- A2完了条件: mock ledger が GoNoGo 条件を満たす。
- A3着手条件: A1/A2完了と契約ドリフトなし。

### Phase 4: Execute
- A1固定 → A2モック検証 → A3実装接続の順序を再確認（逆行なし）。

### Phase 5: Verify
- 契約整合 / モック整合 / 実装整合を点検し、Self-Correction は `0/3`。

### Phase 6: Proceed
- Decision: **Go**。次セットへ直列進行可能。

