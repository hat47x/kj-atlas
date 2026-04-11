# Issue Draft: FB-P2A-02-A2 Collapse/Expand操作 / モック検証

- Type: Feature request
- Status: Ready (A2 Validation Planned)
- Priority: P0
- Owner: Stream D
- Scope: `01_Plans/issues/` (planning memo only)
- Related Backlog: `FB-P2A-02`
- Related ADR/Spec: `ADR-0007`, `issue-FB-P2A-02-a1-interface-contract.md`
- Expected verification level: `docs-check`

## Requirement meta I/F（共通キー）

- RequirementID: `RQ-2A-02`
- RequirementStatement: A1で固定した `CTR-2A-02-COLLAPSE-EXPAND-V1` / `IslandVisibilityContractV1` をモックで検証する。
- Phase: `A2 Mock Validation`
- PriorityClass: Must
- GoNoGoGate: Required
- VerificationLevel: docs-check
- DecisionStatus: Fixed

## Phase management（Stream D）

- Phase 1: Read同期（A1/A2/A3の3点再読）
- Phase 2: A1契約点検（I/F固定と契約ドリフト検知）
- Phase 3: A2モック検証計画固定（M1..M4・責務分離）
- Phase 4: A3 handoff条件固定（GoNoGoと停止条件）
- Phase 5: Verify（記述整合・依存整合）

## Contract freeze confirmation

- FixedContractRef: `issue-FB-P2A-02-a1-interface-contract.md`
- ContractID: `CTR-2A-02-COLLAPSE-EXPAND-V1`
- ContractVersion: `IslandVisibilityContractV1`
- FreezeRule: A2では Required fields / Invariants を変更しない。
- DriftCheck:
  - ContractLinks（A1→A2→A3）の到達性を維持する。
  - `isCollapsed` / `hiddenDescendantIslandIds` / `hiddenCardIds` の意味を再定義しない。

## Mock validation scope

- 入力モック:
  - M1: 親island collapse（子island + cardsが非表示になる）
  - M2: expand復帰（非表示対象が復元）
  - M3: 二重collapse要求（冪等）
  - M4: 存在しないislandへのcollapse要求（拒否）
- 期待判定:
  - M1/M2/M3は契約適合（pass）。
  - M4はFail Fastで reject する（fail）。

## Fixture / signature plan（実装依存なし）

| fixtureId | fileName | mockCaseId | signature check | expected |
|---|---|---|---|---|
| `F1` | `visibility_collapse_valid.json` | `M1` | `isCollapsed: boolean`, `hidden*Ids: string[]` | pass |
| `F2` | `visibility_expand_restore_valid.json` | `M2` | restore keeps view-only mutation | pass |
| `F3` | `visibility_double_collapse_idempotent.json` | `M3` | idempotent repeated collapse | pass |
| `F4` | `visibility_missing_island_invalid.json` | `M4` | unknown island request reject | fail |

### Signature/data type checks

- `contractId: string`（固定値 `CTR-2A-02-COLLAPSE-EXPAND-V1`）
- `contractVersion: string`（固定値 `IslandVisibilityContractV1`）
- `mockCaseId: string`（`M1`〜`M4`）
- `validationResult: "pass" | "fail"`
- `ownerOfFix: "A1" | "A2" | "A3"`
- `evidence: string`

## Responsibility split（失敗時責務分離）

- 契約修正責務（A1）:
  - `hidden*Ids` 定義不足で期待挙動を一意に決められない。
- モック修正責務（A2）:
  - fixture 前提の不備、データ型の誤り、または判定期待値の誤設定。
- 実装修正責務（A3）:
  - 契約とモックは成立しているが実装引き渡し条件に落ちていない。

## Acceptance criteria

- [x] collapse/expandの正常系・異常系モックが揃う。
- [x] fixture ごとに I/F シグネチャとデータ型の確認項目が明示される。
- [x] 失敗時責務分離ルールが明文化される。
- [x] A3へ渡す検証ログ項目が定義される。

## Execution protocol（Plan→Execute→Verify→Proceed）

1. **Plan**
   - A1契約凍結（`CTR-2A-02-COLLAPSE-EXPAND-V1` / `IslandVisibilityContractV1`）とモックケース（M1〜M4）を対応付ける。
2. **Execute**
   - M1→M2→M3→M4の順に直列検証し、各ケースで`validationResult`と`ownerOfFix`を記録する。
3. **Verify**
   - GoNoGo条件（`M1/M2/M3=pass`, `M4=fail`）および責務分離の確定を確認する。
4. **Proceed**
   - A3 handoff I/Fを満たすログのみ引き渡す。未確定項目があればA2で修復する。

## A2 mock validation plan（Stream D / Phase 3）

- fixture/stub分解（実装依存を分離）:
  - Fixture:
    - F1 `visibility_collapse_valid.json`（M1）
    - F2 `visibility_expand_restore_valid.json`（M2）
    - F3 `visibility_double_collapse_idempotent.json`（M3）
    - F4 `visibility_missing_island_invalid.json`（M4）
  - Stub:
    - S1 `visibility contract projector stub`
    - S2 `collapse/expand invariant evaluator stub`
- 実装依存の明示切り離し:
  - 描画エンジン、state管理実装、UI操作シーケンスには依存しない。
  - 判定軸はA1契約Invariant（表示/ヒットテスト除外、復帰可能、document非破壊）のみ。
- GoNoGo固定:
  - Go: `M1/M2/M3=pass` かつ `M4=fail`。
  - NoGo: 判定不一致、ケース欠損、責務未確定。

## A3 handoff I/F

- Handoff payload:
  - `contractId`
  - `contractVersion`
  - `mockCaseId`
  - `validationResult`
  - `ownerOfFix`
  - `evidence`

## Validation log schema（A3引き継ぎ必須）

| field | type | description |
|---|---|---|
| `contractId` | string | `CTR-2A-02-COLLAPSE-EXPAND-V1` 固定値 |
| `contractVersion` | string | `IslandVisibilityContractV1` 固定値 |
| `mockCaseId` | enum(`M1`,`M2`,`M3`,`M4`) | モックケースID |
| `validationResult` | enum(`pass`,`fail`) | モック判定結果 |
| `ownerOfFix` | enum(`A1`,`A2`,`A3`) | 失敗時の修正責務 |
| `evidence` | string | 判定根拠（表示/非表示・冪等・拒否） |

## A2 validation ledger（契約監査結果）

| contractId | contractVersion | mockCaseId | validationResult | ownerOfFix | evidence |
|---|---|---|---|---|---|
| `CTR-2A-02-COLLAPSE-EXPAND-V1` | `IslandVisibilityContractV1` | `M1` | `pass` | `A3` | collapse hides descendants and cards |
| `CTR-2A-02-COLLAPSE-EXPAND-V1` | `IslandVisibilityContractV1` | `M2` | `pass` | `A3` | expand restores `hiddenDescendantIslandIds` / `hiddenCardIds` |
| `CTR-2A-02-COLLAPSE-EXPAND-V1` | `IslandVisibilityContractV1` | `M3` | `pass` | `A3` | double collapse remains idempotent |
| `CTR-2A-02-COLLAPSE-EXPAND-V1` | `IslandVisibilityContractV1` | `M4` | `fail` | `A2` | fail-fast on unknown `island.id` request |

- GoNoGo result: **Go**（`M1/M2/M3=pass` かつ `M4=fail`）
- Owner routing check: pass casesは`A3`、fail case（M4）は`A2`で固定。

## State sync / conflict check

- Phase開始時Read対象:
  - `issue-FB-P2A-02-a1-interface-contract.md`
  - `issue-FB-P2A-02-a2-mock-validation.md`
  - `issue-FB-P2A-02-a3-implementation.md`
- Rule:
  - Phase開始ごとに上記3ファイルを再Readし、差分競合がある場合は推測継続せず停止・報告する。

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

