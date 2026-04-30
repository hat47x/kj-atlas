# Issue Draft: FB-P2A-01-A2 Island階層モデル導入 / モック検証

- Type: Feature request
- Status: Done
- Priority: P0
- Owner: Stream A（Critical Path / FB-P2A planning memo exclusive）
- Scope: `01_Plans/issues/` (planning memo only)
- Related Backlog: `FB-P2A-01`
- Related ADR/Spec: `ADR-0007`, `ADR-0001`, `issue-FB-P2A-01-a1-interface-contract.md`
- Dependencies: `FB-P2A-01`
- Expected verification level: `docs-check`

## Dependencies

- DependsOn: `01_Plans/issues/issue-FB-P2A-01-a1-interface-contract.md`
- Unblocks: `issue-FB-P2A-01-a3-implementation.md`
- Gate/Blocker: Ready when A1 Annex lock is Fixed and mock GoNoGo is `M1/M2/M3=pass & M4=fail`; Blocked when Annex lock unresolved or ownerOfFix unresolved.

## Requirement meta I/F（共通キー）

- RequirementID: `RQ-2A-01`
- RequirementStatement: A1 Local Contract Annex（`LCA-FB-P2A-01-A1-V1`）の妥当性をモックで検証する。
- Phase: `A2 Mock Validation`
- PriorityClass（Must / Should / Could）: Must
- GoNoGoGate（Required / Optional / N/A）: Required
- SecurityGateImpact: N/A（計画のみ）
- VerificationLevel: docs-check
- DecisionStatus: Fixed

## Contract freeze confirmation（Annex参照専用）

- FixedContractRef: `issue-FB-P2A-01-a1-interface-contract.md`
- AnnexID: `LCA-FB-P2A-01-A1-V1`
- ContractID: `CTR-2A-01-ISLAND-HIERARCHY-V1`
- ContractVersion: `IslandHierarchyContractV1`
- FreezeRule: A2では Required fields / Invariants を変更しない。
- Direct reference ban: A2本文から外部I/Fへ直接参照しない（A1 Annexを介して参照）。

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
- Phase 6 Proceed: 完了条件成立時のみA3へ進行提案し、未達時は停止レポートを残す。

## Phase 1 Read result（差分抽出）

### 抽出（Status/AC/DoD/依存）
- Status: A1/A2/A3 は Open。
- AC: GoNoGo定義（M1..M4）は明確。
- DoD: A2にDoD節が未定義だったため補強対象。
- 依存: A1 Annex lock -> A2 ledger -> A3 handoff の直列依存を確認。

### 事前想定との差分
1. Stream B表記が残っていたため、Stream Aへ統一が必要。
2. A1 Annex参照専用ルールが明文化不足。
3. DoDの完了判定基準が不足。

## Mock validation scope

- 入力モック:
  - M1: root island（`parentIslandId` 欠損）
  - M2: 3階層ネスト（root→child→grandchild）
  - M3: 不正参照（存在しない `parentIslandId`）
  - M4: 循環参照（self-parent または A→B→A）
- 期待判定:
  - M1/M2は契約適合（pass）。
  - M3は import 正規化で `parentIslandId -> undefined` にフォールバックできる（pass）。
  - M4は Fail Fast で reject する（fail）。

## Fixture / signature plan（実装依存なし）

| fixtureId | fileName | mockCaseId | signature check | expected |
|---|---|---|---|---|
| `F1` | `hierarchy_root_valid.json` | `M1` | `parentIslandId?: string`, `cardIds: string[]` | pass |
| `F2` | `hierarchy_three_levels_valid.json` | `M2` | 参照先存在 + 非循環 | pass |
| `F3` | `hierarchy_missing_parent_normalized.json` | `M3` | 不正参照の正規化 | pass |
| `F4` | `hierarchy_cycle_invalid.json` | `M4` | self-parent / cycle 検出 | fail |

### Signature/data type checks

- `contractId: string`（固定値 `CTR-2A-01-ISLAND-HIERARCHY-V1`）
- `contractVersion: string`（固定値 `IslandHierarchyContractV1`）
- `mockCaseId: string`（`M1`〜`M4`）
- `validationResult: "pass" | "fail"`
- `ownerOfFix: "A1" | "A2" | "A3"`
- `evidence: string`

## Responsibility split（失敗時責務分離）

- 契約修正責務（A1へ戻す）:
  - Required fields や Invariant 自体が不足/矛盾している。
- モック修正責務（A2内で完結）:
  - fixture 名、データ型、期待値、責務ラベルの設定誤り。
- 実装修正責務（A3へ引き継ぎ）:
  - 契約・モックは妥当だが、A3の入力契約やロールバック条件に反映されていない。

## Acceptance criteria

- [x] A1 Annex契約を変更せずにモック検証ケースを定義できる。
- [x] fixture ごとに I/F シグネチャとデータ型確認項目が明示される。
- [x] 正常系/異常系の判定基準が明示される。
- [x] 失敗時に「契約修正 / モック修正 / 実装修正」の切り分けルールが記録される。
- [x] A3へ渡す検証ログ項目（入力/期待/結果/責務）が定義される。

## Definition of Done (DoD)

- [x] `AnnexID` / `ContractID` / `ContractVersion` がA1と一致している。
- [x] M1..M4全ケースに `validationResult` と `ownerOfFix` が定義されている。
- [x] GoNoGo（`M1/M2/M3=pass` かつ `M4=fail`）がledgerで再現できる。
- [x] A2本文から外部I/F直接参照が除去されている。

## A3 handoff I/F

- Handoff payload:
  - `contractId`
  - `contractVersion`
  - `mockCaseId`
  - `validationResult`
  - `ownerOfFix`
  - `evidence`

## A2 validation ledger（契約監査結果）

| annexId | contractId | contractVersion | mockCaseId | validationResult | ownerOfFix | evidence |
|---|---|---|---|---|---|---|
| `LCA-FB-P2A-01-A1-V1` | `CTR-2A-01-ISLAND-HIERARCHY-V1` | `IslandHierarchyContractV1` | `M1` | `pass` | `A3` | root island allows missing `parentIslandId` |
| `LCA-FB-P2A-01-A1-V1` | `CTR-2A-01-ISLAND-HIERARCHY-V1` | `IslandHierarchyContractV1` | `M2` | `pass` | `A3` | existing parent references preserve 3-level hierarchy |
| `LCA-FB-P2A-01-A1-V1` | `CTR-2A-01-ISLAND-HIERARCHY-V1` | `IslandHierarchyContractV1` | `M3` | `pass` | `A3` | invalid `parentIslandId` is normalized to `undefined` |
| `LCA-FB-P2A-01-A1-V1` | `CTR-2A-01-ISLAND-HIERARCHY-V1` | `IslandHierarchyContractV1` | `M4` | `fail` | `A2` | cycle must be rejected by invariant check |

- GoNoGo result: **Go**（`M1/M2/M3=pass` かつ `M4=fail`）

## Validation plan

- Command:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`

## Fail-safe

- self-correction上限: 3回。
- 停止トリガ: 3回超過 / 契約ドリフト / ownerOfFix未確定 / 前提崩壊 / 未定義競合 / 指定外ファイル編集要求。
- 停止時対応: 推測継続を禁止し、停止理由と再開条件を記録して指示待ち。

## Stream I Done/Completed Audit (2026-04-23)
- 判定: 再オープン不要（Done/Completed/Closedの完了根拠と整合）。
- Related ADR/Spec: 参照先リンク切れなし（存在確認済み）。
- 重複Backlog整理提案: FB-P2A-01 は系列メモ複数運用（3件）。再オープンではなく、次回は親統合メモ1本＋派生メモ参照化を提案。

## Stream F execution log (2026-04-30, FB-P2A lane A2)

- Scope declaration（A2）: A1で宣言した最小3ファイルスコープを維持。追加ファイル拡散なし。
- Phase: **A2 mock-validation 完了**。
- Mock independence: A1 Annex（`LCA-FB-P2A-01-A1-V1`）のみ参照し、外部I/F待ち・外部レビュー待ちを発生させず検証可能な構成を維持。
- Validation recap: `M1/M2/M3=pass`、`M4=fail` の Go 条件を維持。
- Stop-condition check: ownerOfFix未確定 / 契約リンク欠落 / 指定外ファイル編集なし。
- Next: A3 `issue-FB-P2A-01-a3-implementation.md` へ ledger 固定値を引き渡し。

