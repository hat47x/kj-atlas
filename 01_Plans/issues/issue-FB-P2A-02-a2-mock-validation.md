# Issue Draft: FB-P2A-02-A2 Collapse/Expand操作 / モック検証

- Type: Feature request
- Status: Open (Audit Hold: normalized contract pack; resumable by explicit Go/NoGo)
- Priority: P0
- Owner: Stream B（FB-P2A planning memo exclusive）
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

## Phase management（Stream B / FB-P2A serial lock）

- Phase 1 Read: A1/A2/A3 3点を再読し、ContractID・依存関係を照合する。
- Phase 2 ADR CDC: 方針変更がある場合のみ CDC を起票し、承認まで停止する。
- Phase 3 Plan: AC/DoD不足のドラフトを作成し、`agreementStatus=agreed` まで進行しない。
- Phase 4 Execute: A1契約固定 → A2 mock ledger固定 → A3 handoff固定を直列で実施する。
- Phase 5 Verify: docs-check + 契約リンク整合 + 自己修復上限3回を確認する。
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

## A2 mock validation plan（Stream B / Phase 4）

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

- 編集対象は FB-P2A A1/A2/A3 issue のみ（CE/HIL/03_Implement は対象外）。
- Plan→Execute→Verify→Proceed の順序を固定し、順序逆転時は停止する。
- A1契約値は read-only 参照のみ。未定義値を推測で補完しない。
- モック前提で依存を切断し、実装依存（renderer/state管理/関数名）を持ち込まない。
- 未解決・責務未確定は Proceed せず Decision Queue へ返却する。

## Stream B execution override（FB-P2A A1→A2→A3）

- 同一レーン内依存は A1→A2→A3 の**直列処理のみ**を許可する。
- 外部レーン完了待ちは禁止し、依存解決は当該レーン内で閉じる。
- 各 Phase 開始時に A1/A2/A3 の3ファイルを再Readしてから着手する。
- 実行順序は **Plan→Execute→Verify→Proceed** を固定し、順序逆転時は停止する。
- Self-correction は最大3回までとし、**4回目に入る前に停止・報告**する。

## Unified execution rule lock（同一ルール固定）

- strict serial: A1→A2→A3 の直列のみ許可（並列禁止）。
- CDC必須: Contract Definition Checklist（C1/C2/C3）とA1固定契約値の一致確認を必須化する。
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
- A1/A2/A3 の3ファイルを再Readし、依存順序 `A1 -> A2 -> A3` と ContractID 一致を確認。

### Phase 2 ADR CDC
- Context: A1契約固定済み前提での下流計画。
- Decision: 新規ADR追加なし（既存契約の運用固定）。
- Consequences: 契約変更要求はA1へ差し戻し、A2/A3で再定義しない。

### Phase 3 Plan
- Plan→Execute→Verify→Proceed の順序を固定。
- AC/DoD不足は `agreementStatus=agreed` まで進行しない。

### Phase 4 Execute
- A2: mock ledger（M1..M4）と責務分離を固定。
- A3: handoff I/F と rollback 条件を固定。

### Phase 5 Verify / Proceed
- GoNoGo条件（`M1/M2/M3=pass` かつ `M4=fail`）と docs-check を満たす場合のみ Proceed。
- self-correction は最大3回。超過時は停止して判断待ち。
- Proceed decision: **Completed（A1→A2→A3 を Stream B 単独で完遂）**。

## Stream B execution log (2026-04-18, FB-P2A-02 A2)

### Phase 1 Read
- A1/A2/A3 の3ファイルを再Readし、A1契約固定値と A2 DependsOn を照合。

### Phase 2 ADR-CDC
- Context: A1固定契約をモック検証へ適用する下流フェーズ。
- Decision: 方針変更なしのため新規ADR起票なし。
- Consequences: 契約変更要求はA1へ返却し、A2では再定義しない。

### Phase 3 Plan
- AC/DoD不足ドラフト判定: **不足なし**。
- `agreementStatus=agreed`（M1..M4、GoNoGo、責務分離、handoff payloadが定義済み）。

### Phase 4 Execute
- A2 ledger を `M1/M2/M3=pass` `M4=fail` で固定し、`ownerOfFix` と `evidence` をA3 handoff I/Fに合わせて整列。

### Phase 5 Verify
- docs-check と契約リンク整合を Phase 5 で実施（詳細はA3実行ログで集約）。
- self-correction 回数: 0/3。

### Phase 6 Proceed
- Proceed判定: **Pass**（A2完了、A3へ進行可）。

## Stream B fixed I/F injection lock（FB-P2A-02）

- ContractID: `CTR-2A-02-COLLAPSE-EXPAND-V1`（Fixed）
- ContractVersion: `IslandVisibilityContractV1`（Fixed）
- Required fields（A1準拠 / Fixed）:
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

## Stream B delta log (2026-04-18, FB-P2A-02 A2 lane re-check)

### Phase 1 Read re-check（ContractID/DependsOn/Unblocks）
- DependsOnContractID: `CTR-2A-02-COLLAPSE-EXPAND-V1`
- DependsOn: `issue-FB-P2A-02-a1-interface-contract.md`
- Unblocks: `issue-FB-P2A-02-a3-implementation.md`
- 判定: **整合（A1固定契約を参照してA3へ単方向handoff）**

### Phase 4 Execute lock（A2 mock criteria）
- 判定基準を固定: `M1/M2/M3=pass` かつ `M4=fail`。
- handoff payload 固定: `contractId`,`contractVersion`,`mockCaseId`,`validationResult`,`ownerOfFix`,`evidence`。

### Phase 5 Verify / Phase 6 Proceed
- Verify最小セット: `docs-check` + GoNoGo一致 + ContractLinks一致。
- Proceed rule: GoNoGo不一致または責務未確定時は **A1へ差戻し**。

## Stream B phase closure record (2026-04-19)

### Phase 1 Read
- A1/A2/A3 を再Readし、A1契約値（ContractID / ContractVersion / Invariants）を参照専用で照合。

### Phase 3 A2 mock verification
- A1契約のみを参照して M1..M4 判定を再確認。
- 判定: `M1/M2/M3=pass` かつ `M4=fail` を維持し、GoNoGo は **Go** のまま固定。
- `ownerOfFix` は M4=`A2`、他ケース=`A3` で未確定項目なし。

### Phase 4 handoff prep
- A3 handoff payload（`contractId`,`contractVersion`,`mockCaseId`,`validationResult`,`ownerOfFix`,`evidence`）を固定入力として再確認。

### Phase 3 Plan
- A1固定契約を read-only 前提として M1..M4 の検証順序と GoNoGo 条件（`M1/M2/M3=pass` かつ `M4=fail`）を固定。
- AC/DoD不足判定: 不足なし（`agreementStatus=agreed`）。

## Stream B execution log (2026-04-19, FB-P2A-02 A2 revalidation)

### Phase 1 (A2) Read
- A1/A2/A3 の3ファイルを再Readし、DependsOn がA1固定契約を参照していることを確認。

### Phase 2 (A2) Execute
- A1契約本文を変更せず、A2 mock validation plan / ledger / handoff payload を固定値として維持。

### Phase 3 (A2) Verify
- GoNoGo条件を再検証: `M1/M2/M3=pass` かつ `M4=fail`。
- `ownerOfFix` の責務分離（A1/A2/A3）が未確定でないことを確認。

### Phase 4 (Cross Verify)
- A1→A2→A3 の契約リンクと handoff I/F（`contractId`,`contractVersion`,`mockCaseId`,`validationResult`,`ownerOfFix`,`evidence`）の連結を再確認。
- 依存逆転・契約再定義は検出なし。

### Phase 5 (Proceed)
- A2の引き渡し条件を満たすため A3 Proceed 可。
- 未解決・判定不一致が発生した場合は **A1 または Decision Queue へ差し戻し** とする。


## Stream B execution log (2026-04-19, FB-P2A-02 A2 refresh)

### Phase 1 Read同期
- A1/A2/A3 の3ファイルを再Readし、A1固定契約値と A2 DependsOn を再照合。
- 差分前提: `ContractID`/`ContractVersion`/GoNoGo (`M1/M2/M3=pass`, `M4=fail`) に競合なし。

### Phase 3 A2モック検証
- fixture/stub 前提を再確認し、実装依存を持ち込まない条件を維持。
- 検証ログI/Fを固定: `contractId`,`contractVersion`,`mockCaseId`,`validationResult`,`ownerOfFix`,`evidence`。

### Phase 5 Verify（A1→A2因果証跡）
- A1 Invariants が A2 判定基準（非表示・復帰・冪等・不正要求拒否）へ写像されることを確認。
- A2 ledger が A3 の `implementationReadiness` 判定入力として利用可能であることを確認。
- self-correction 使用回数: `0/3`。

### Phase 6 Proceed
- Proceed判定: `Pass`（A3 handoff 可能）。
