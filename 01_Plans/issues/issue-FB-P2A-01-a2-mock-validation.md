# Issue Draft: FB-P2A-01-A2 Island階層モデル導入 / モック検証

- Type: Feature request
- Status: Open (Audit Hold: normalized contract pack; resumable by explicit Go/NoGo)
- Priority: P0
- Owner: Stream B（FB-P2A planning memo exclusive）
- Scope: `01_Plans/issues/` (planning memo only)
- Related Backlog: `FB-P2A-01`
- Related ADR/Spec: `ADR-0007`, `ADR-0001`, `issue-FB-P2A-01-a1-interface-contract.md`
- Expected verification level: `docs-check`

## Dependencies

- DependsOn: `01_Plans/issues/issue-FB-P2A-01-a1-interface-contract.md`
- Unblocks: issue-FB-P2A-01-a3-implementation.md
- Gate/Blocker: Ready when A1 is Done/Fixed and mock GoNoGo is `M1/M2/M3=pass & M4=fail`; Blocked when A1 not fixed or ownerOfFix unresolved.
## Requirement meta I/F（共通キー）

- RequirementID: `RQ-2A-01`
- RequirementStatement: A1で固定した `CTR-2A-01-ISLAND-HIERARCHY-V1` / `IslandHierarchyContractV1` の妥当性をモックで検証する。
- Phase: `A2 Mock Validation`
- PriorityClass（Must / Should / Could）: Must
- GoNoGoGate（Required / Optional / N/A）: Required
- SecurityGateImpact: N/A（計画のみ）
- VerificationLevel: docs-check
- DecisionStatus: Fixed

## Phase management（Stream B）

- Phase 1: Read同期（A1/A2/A3の3点再読）
- Phase 2: A1契約明確化（CDC明文化）
- Phase 3: A2モック検証計画更新（M1..M4・責務分離）
- Phase 4: A3実装準備条件定義（GoNoGoと停止条件）
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


## Stream B strict serial protocol（Phase 1→5）

### Phase 1 Read
- 対象ファイル（A1/A2/A3の3点）を**Phase開始時に必ず再Read**する。
- 照合項目: `Status` / `Priority(P0)` / `DecisionStatus` / `ContractID(またはDependsOnContractID)`。
- 不足監査: AC/DoD/停止条件/handoff条件。

### Phase 2 A1契約明確化（CDC明文化）
- Plan: A1契約（ContractID / Required fields / Invariants / ContractLinks）を**read-only参照**で固定対象として再確認する。
- Execute: 契約本文の再定義は行わず、固定I/Fの一致確認のみ実施する。
- Verify: A1→A2→A3依存の逆転・並列前提・契約ドリフトがないことを確認する。
- Proceed: A1固定が崩れた場合は停止し、A1へ差し戻す（契約値の推測補完は禁止）。

### Phase 3 A2モック検証計画更新
- Plan: M1..M4（正常/異常）と責務分離（A1/A2/A3）を再確認する。
- Execute: handoff payload（`contractId`,`contractVersion`,`mockCaseId`,`validationResult`,`ownerOfFix`,`evidence`）を固定入力として扱う。
- Verify: GoNoGo条件（`M1/M2/M3=pass` かつ `M4=fail`）の整合を確認する。
- Proceed: 判定不一致または責務未確定時は停止し、Decision Queueへ返却してA2へ差し戻す。

### Phase 4 A3実装準備条件定義
- Plan: 実装入口は契約参照のみで開始できる条件を確認する。
- Execute: Plan→Execute→Verify→Proceed を固定順序で適用し、実装先行を禁止する。
- Verify: AC/DoD不足を検知した場合は `gapType` と `agreementStatus` を用いたドラフト提案を先行し、`agreementStatus=agreed` まで実行しない。
- Proceed: 合意済み条件と停止条件が同時に満たされる場合のみ下流へ引き渡し、未解決はDecision Queueへ返却する。

### Phase 5 Verify
- docs-check: `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- 依存参照整合・表記ゆれ・契約ID衝突を確認する。
- Self-Correction は最大3回。4回目相当は**停止して指示待ち**とする。


## Stream B lane guard（FB-P2A only）

- 編集対象は FB-P2A A2/A3 issue のみ（A1/CE/HIL/03_Implement は対象外）。
- Plan→Execute→Verify→Proceed の順序を固定し、順序逆転時は停止する。
- A1契約値は read-only 参照のみ。未定義値を推測で補完しない。
- モック前提で依存を切断し、実装依存（renderer/state管理/関数名）を持ち込まない。
- 未解決・責務未確定は Proceed せず Decision Queue へ返却する。

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
- 停止トリガ: 3回超過 / 依存不整合 / 指定外ファイル更新が必要 / ContractID衝突。
- 停止時対応: 推測継続を禁止し、停止理由と再開条件を記録して指示待ち。

## Stream B Phase 3 completion snapshot（2026-04-16）

### Phase 3 A2（Plan→Execute→Verify→Proceed）
- Plan: モック検証仕様 `M1..M4` と責務分離ルール、handoff payload の固定項目を再確認。
- Execute: `M1/M2/M3=pass`・`M4=fail` を GoNoGo 判定式として維持し、payload を `contractId/contractVersion/mockCaseId/validationResult/ownerOfFix/evidence` で固定。
- Verify: A1契約（Required fields/Invariants）への変更を行っていないこと、A3接続に必要な入力が全ケースで定義済みであることを確認。
- Proceed: A3へは payload を read-only で受け渡し、判定不一致時はA2差戻しを継続する。

