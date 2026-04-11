# Issue Draft: FB-P2A-01-A2 Island階層モデル導入 / モック検証

- Type: Feature request
- Status: Ready (A2 Validation Planned)
- Priority: P0
- Owner: Stream D
- Scope: `01_Plans/issues/` (planning memo only)
- Related Backlog: `FB-P2A-01`
- Related ADR/Spec: `ADR-0007`, `ADR-0001`, `issue-FB-P2A-01-a1-interface-contract.md`
- Expected verification level: `docs-check`

## Requirement meta I/F（共通キー）

- RequirementID: `RQ-2A-01`
- RequirementStatement: A1で固定した `CTR-2A-01-ISLAND-HIERARCHY-V1` / `IslandHierarchyContractV1` の妥当性をモックで検証する。
- Phase: `A2 Mock Validation`
- PriorityClass（Must / Should / Could）: Must
- GoNoGoGate（Required / Optional / N/A）: Required
- SecurityGateImpact: N/A（計画のみ）
- VerificationLevel: docs-check
- DecisionStatus: Fixed

## Phase management（Stream D）

- Phase 1: Read同期（A1/A2/A3の3点再読）
- Phase 2: A1契約点検（I/F固定と契約ドリフト検知）
- Phase 3: A2モック検証計画固定（M1..M4・責務分離）
- Phase 4: A3 handoff条件固定（GoNoGoと停止条件）
- Phase 5: Verify（記述整合・依存整合）

## Contract freeze confirmation

- FixedContractRef: `issue-FB-P2A-01-a1-interface-contract.md`
- ContractID: `CTR-2A-01-ISLAND-HIERARCHY-V1`
- ContractVersion: `IslandHierarchyContractV1`
- FreezeRule: A2では Required fields / Invariants を変更しない。
- DriftCheck:
  - ContractLinks（A1→A2→A3）が全て到達可能であること。
  - Invariants（存在参照 / 循環禁止 / 正規化フォールバック / roundtrip保持）を判定表へそのまま転写すること。

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

- [x] A1契約を変更せずにモック検証ケースを定義できる。
- [x] fixture ごとに I/F シグネチャとデータ型の確認項目が明示される。
- [x] 正常系/異常系の判定基準が明示される。
- [x] 失敗時に「契約修正 / モック修正 / 実装修正」の切り分けルールが記録される。
- [x] A3へ渡す検証ログ項目（入力/期待/結果/責務）が定義される。

## A3 handoff I/F

- Handoff payload:
  - `contractId`
  - `contractVersion`
  - `mockCaseId`
  - `validationResult`
  - `ownerOfFix`
  - `evidence`

## Phase execution log（A2）

### Read sync（Phase開始時）

- `issue-FB-P2A-01-a1-interface-contract.md`
- `issue-FB-P2A-01-a2-mock-validation.md`
- `issue-FB-P2A-01-a3-implementation.md`

### Plan

- A1固定契約を変更せず、M1〜M4の判定表を準備する。
- 失敗時の責務分離（A1/A2/A3）とA3引き継ぎログ項目を固定する。

### Execute

- M1/M2/M3を正常系、M4を異常系として契約Invariantに対応付ける。
- `contractId` / `contractVersion` / `mockCaseId` / `validationResult` / `ownerOfFix` / `evidence` を引き継ぎI/Fとして定義する。

### Verify

- A1の Required fields / Invariants を変更していないことを確認する。
- 判定結果が `M1/M2/M3=pass`・`M4=fail` のGoNoGo条件へ接続可能であることを確認する。

### Proceed

- A3へ handoff payload をそのまま渡し、実装接続条件の評価へ進む。

## Validation log schema（A3引き継ぎ必須）

| field | type | description |
|---|---|---|
| `contractId` | string | `CTR-2A-01-ISLAND-HIERARCHY-V1` 固定値 |
| `contractVersion` | string | `IslandHierarchyContractV1` 固定値 |
| `mockCaseId` | enum(`M1`,`M2`,`M3`,`M4`) | モックケースID |
| `validationResult` | enum(`pass`,`fail`) | モック判定結果 |
| `ownerOfFix` | enum(`A1`,`A2`,`A3`) | 失敗時の修正責務 |
| `evidence` | string | 判定根拠（Invariant IDまたは期待値） |

## A2 validation ledger（契約監査結果）

| contractId | contractVersion | mockCaseId | validationResult | ownerOfFix | evidence |
|---|---|---|---|---|---|
| `CTR-2A-01-ISLAND-HIERARCHY-V1` | `IslandHierarchyContractV1` | `M1` | `pass` | `A3` | root island allows missing `parentIslandId` |
| `CTR-2A-01-ISLAND-HIERARCHY-V1` | `IslandHierarchyContractV1` | `M2` | `pass` | `A3` | existing parent references preserve 3-level hierarchy |
| `CTR-2A-01-ISLAND-HIERARCHY-V1` | `IslandHierarchyContractV1` | `M3` | `pass` | `A3` | invalid `parentIslandId` is normalized to `undefined` |
| `CTR-2A-01-ISLAND-HIERARCHY-V1` | `IslandHierarchyContractV1` | `M4` | `fail` | `A2` | cycle must be rejected by invariant check |

- GoNoGo result: **Go**（`M1/M2/M3=pass` かつ `M4=fail`）
- Owner routing check: 契約・fixtureが固定済みのため、A3は pass ケースを入力契約として受領し、A2 は fail ケースの検証責務を保持する。

## State sync / conflict check

- Phase開始時Read対象:
  - `issue-FB-P2A-01-a1-interface-contract.md`
  - `issue-FB-P2A-01-a2-mock-validation.md`
  - `issue-FB-P2A-01-a3-implementation.md`

## Validation plan

- Command:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`

## Fail-safe

- self-correction上限: 3回。連続失敗時はProceed禁止で停止。
- 停止トリガ: Ready条件崩壊 / 依存逆転 / 未定義競合 / ContractID不一致を検出した場合は即時停止して報告。

## Stream I normalization ledger（Phase 1-6 / Plan→Execute→Verify→Proceed）

### Phase 1 Read
- Plan: Status / Scope / DecisionStatus / Validation plan を抽出し、A1/A2/A3粒度を点検する。
- Execute:
  - Status: 既存本文の宣言値を採用。
  - Scope: `Mock Validation` に限定。
  - DecisionStatus: `Fixed`。
  - Validation command: `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`。
- Verify: 抽出項目が本メモ内で相互矛盾しないことを確認。
- Proceed: 矛盾がなければ Phase 2 へ進む。

### Phase 2 Plan
- Plan: AC/DoD不足の有無を点検し、不足時はドラフト提案I/Fで合意前提にする。
- Execute: 依存は `A1 fixed contract only` のみ許可し、実装ストリーム依存は mock I/F へ切り離す。
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

