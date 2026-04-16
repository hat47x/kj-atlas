# Issue Draft: FB-P2A-02-A2 Collapse/Expand操作 / モック検証

- Type: Feature request
- Status: Open (Audit Hold: normalized contract pack; resumable by explicit Go/NoGo)
- Priority: P0
- Owner: Stream G（FB-P2A planning memo exclusive）
- Scope: `01_Plans/issues/` (planning memo only)
- Related Backlog: `FB-P2A-02`
- Related ADR/Spec: `ADR-0007`, `issue-FB-P2A-02-a1-interface-contract.md`
- Expected verification level: `docs-check`

## Dependencies

- DependsOn: `01_Plans/issues/issue-FB-P2A-02-a1-interface-contract.md`
- Unblocks: issue-FB-P2A-02-a3-implementation.md
- Gate/Blocker: Ready when A1 is Done/Fixed and mock GoNoGo is `M1/M2/M3=pass & M4=fail`; Blocked when A1 not fixed or ownerOfFix unresolved.
## Requirement meta I/F（共通キー）

- RequirementID: `RQ-2A-02`
- RequirementStatement: A1で固定した `CTR-2A-02-COLLAPSE-EXPAND-V1` / `IslandVisibilityContractV1` をモックで検証する。
- Phase: `A2 Mock Validation`
- PriorityClass: Must
- GoNoGoGate: Required
- VerificationLevel: docs-check
- DecisionStatus: Fixed

## Phase management（Stream G）

- Phase 1: Read同期（A1/A2/A3の3点再読）
- Phase 2: A1契約明確化（CDC明文化）
- Phase 3: A2モック検証計画更新（M1..M4・責務分離）
- Phase 4: A3実装準備条件定義（GoNoGoと停止条件）
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

## A2 mock validation plan（Stream B / Phase 3）

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


## Stream G strict serial protocol（Phase 1→5）

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


## Stream G lane guard（FB-P2A only）

- 編集対象は FB-P2A A2/A3 issue のみ（A1/CE/HIL/03_Implement は対象外）。
- Plan→Execute→Verify→Proceed の順序を固定し、順序逆転時は停止する。
- A1契約値は read-only 参照のみ。未定義値を推測で補完しない。
- モック前提で依存を切断し、実装依存（renderer/state管理/関数名）を持ち込まない。
- 未解決・責務未確定は Proceed せず Decision Queue へ返却する。

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
