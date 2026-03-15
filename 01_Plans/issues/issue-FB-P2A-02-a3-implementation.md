# Issue Draft: FB-P2A-02-A3 Collapse/Expand操作 / 実装計画接続

- Type: Feature request
- Status: Ready (A3 Handoff Condition Fixed)
- Priority: P0
- Owner: Stream D
- Scope: `01_Plans/issues/` (planning memo only)
- Related Backlog: `FB-P2A-02`
- Related ADR/Spec: `ADR-0007`, `issue-FB-P2A-02-a1-interface-contract.md`, `issue-FB-P2A-02-a2-mock-validation.md`
- Expected verification level: `integration`

## Requirement meta I/F（共通キー）

- RequirementID: `RQ-2A-02`
- RequirementStatement: A1/A2契約を逸脱せず、Collapse/Expand実装計画へ接続する。
- Phase: `A3 Implementation`
- PriorityClass: Must
- GoNoGoGate: Required
- VerificationLevel: integration
- DecisionStatus: Fixed

## Phase management（Stream D）

- Phase 1: Read同期（A1/A2/A3の3点再読）
- Phase 2: A1契約点検（I/F固定と契約ドリフト検知）
- Phase 3: A2モック検証計画固定（M1..M4・責務分離）
- Phase 4: A3 handoff条件固定（GoNoGoと停止条件）
- Phase 5: Verify（記述整合・依存整合）


## Execution protocol（Plan→Execute→Verify→Proceed）

1. **Plan**
   - `isCollapsed` と `hidden*Ids` の更新責務を分離して作業計画化。
2. **Execute**
   - `state transition -> render filter -> hit-test filter` の順で設計反映。
3. **Verify**
   - A2 mockCaseを使って遷移前後の整合をチェック。
4. **Proceed**
   - GoNoGoを満たした観点のみ次タスクへ進行。
   - 次タスク開始時はA1/A2/A3の3ファイルを再Readしてから着手する。

## Non-deviation rules

- A1契約をA3で再解釈しない。
- A2 Failケースを未解決のまま先送りしない。
- AC/DoD不足を検知した場合は、先にドラフト提案を追記して合意後に進行する。

## Acceptance criteria

- [x] A1/A2契約IDで実装計画トレースが可能。
- [x] Plan→Execute→Verify→Proceedの順序が固定される。
- [x] AC/DoD不足時のドラフト提案手順が明文化される。



## AC/DoD不足の事前提案I/F（合意前提）

- Required fields:
  - `gapId`
  - `gapType`（`AC` / `DoD`）
  - `phaseDetected`（`A1` / `A2` / `A3`）
  - `proposalDelta`
  - `agreementStatus`（`pending` / `agreed` / `rejected`）
- Proceed rule:
  - `agreementStatus=agreed` 以外はNoGo。

## Serial execution gate（A1→A2→A3）

- A3開始条件:
  - A2 handoff payload（`contractVersion`,`mockCaseId`,`validationResult`,`ownerOfFix`）が全件揃っている。
- A3停止条件:
  - 未定義競合を検出した場合は推測継続禁止、停止・報告。
- Self-repair上限:
  - 自己修復は最大3回。超過時は作業停止して報告。

## A2→A3 接続条件（確定）

- ContractLock: `IslandVisibilityContractV1`（A1定義から変更禁止）
- Required input from A2:
  - `contractVersion=IslandVisibilityContractV1`
  - `mockCaseId in {M1,M2,M3,M4}`
  - `validationResult`
  - `ownerOfFix`
- GoNoGo判定:
  - Go: `M1/M2/M3=pass` かつ `M4=fail`、責務が確定。
  - NoGo: 判定不一致、または責務未確定。

## 実装トレース最小単位

| traceKey | source | destination |
|---|---|---|
| `RQ-2A-02` | A1 RequirementID | A3 task grouping key |
| `M1..M4` | A2 mockCaseId | A3 verification checklist |
| `ownerOfFix` | A2 failure routing | A3 backlog split (A1/A2/A3) |

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

- 停止トリガ: Ready条件崩壊 / 依存逆転 / 未定義競合を検出した場合は即時停止して報告。

- 自己修復が3回連続で失敗、またはA1/A2契約リンク不整合を検出した場合は停止して指示待ち。


## A3 implementation trace（Stream D）

### Plan
- `RQ-2A-02` をキーに、A2 handoff log (`M1..M4`) を `evaluateIslandVisibilityA3GoNoGoStreamD` に投入する検証を固定。
- A3開始条件として「重複mockCase禁止」「contractVersion固定」「ownerOfFix整合」を追加。

### Execute
- `frontend/src/domain/p2a_stream_d/island_visibility_stream_d.ts` にて、以下のFail Fast判定を実装。
  - duplicate mock case 検知
  - contractVersion不整合検知
  - `M1/M2/M3 ownerOfFix=A3` 強制
  - `M4 ownerOfFix!=A3` 強制
- `frontend/src/domain/p2a_stream_d/island_visibility_stream_d.test.ts` にNoGoケースを追加。

### Verify
- `evaluateIslandVisibilityA3GoNoGoStreamD` のGo条件は維持（`M1/M2/M3=pass`, `M4=fail`）。
- 追加NoGo条件がテストで再現可能。

### Proceed
- A2→A3接続I/F（`contractVersion`,`mockCaseId`,`validationResult`,`ownerOfFix`）で欠損なし。
- 未定義依存なし、A1契約 (`IslandVisibilityContractV1`) の再解釈なし。


## A3 implementation connection guard（Stream D / Phase 4）

- 着手条件（Start）:
  - `IslandVisibilityContractV1` がA1で固定され、A2ログがM1〜M4全件で存在する。
  - handoff I/F（`contractVersion`,`mockCaseId`,`validationResult`,`ownerOfFix`,`evidence`）に欠損なし。
- 停止条件（Stop）:
  - `M1/M2/M3=pass` かつ `M4=fail` が崩れた場合。
  - `ownerOfFix` がA2責務分離と矛盾した場合。
  - AC/DoD不足で `agreementStatus=agreed` が未達の場合。
- ロールバック条件（Rollback）:
  - A3で追加した前提・タスク分割を破棄し、A2確定ログを唯一の入力へ戻す。
  - 契約I/F変更要求はA1へ差し戻し、A3での再解釈を禁止する。

## Stream D one-page handoff（Phase 5）

- 固定I/F（Fixed Interface）:
  - `contractVersion`,`mockCaseId`,`validationResult`,`ownerOfFix`,`evidence`
  - ContractLock: `IslandVisibilityContractV1`
- 許容差分（Allowed Delta）:
  - A3内の実装順序・タスク分割・検証手順の最適化（契約意味を変えない範囲）。
- 禁止変更（Forbidden Changes）:
  - A1 Required fields / Invariants / ContractLinks の改変。
  - GoNoGo条件（`M1/M2/M3=pass`, `M4=fail`）の変更。
  - SafeMode/share-export既定挙動に影響する仕様変更。
