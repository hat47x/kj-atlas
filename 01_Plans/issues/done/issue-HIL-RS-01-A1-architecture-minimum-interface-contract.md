# Issue Draft: HIL-RS-01 A1 Architecture 最小I/F契約固定（Stream D）

- Type: Process
- Status: Done
- Source Issue: N/A
- Priority: P1
- Owner: Stream H（A1 minimum interface contract only）
- Scope: 本ファイルのみ（docs-only）
- Dependencies: なし（A1最小I/Fの先行固定）
- Related ADR/Spec: `ADR-0026`, `ADR-0027`, `ADR-0028`, `ADR-0039`
- Expected verification level: `docs-check`

## A1 Done 2026-06-20

HIL-RS-01-A1 minimum interface contract is Done. Resolution per ADR-0039 Maintainer authority:

- **Contract IDs frozen**: `A1-CRITIQUE-IF`, `A1-REDIFF-IF`, `A1-ATTR-IF`, `A1-ERROR-IF`
- **safeModeDefault**: `ON` / **safeModeBoundary**: `SAFE_MODE_STRICT_ON`
- **overridePolicy**: `human_dual_control_only` → noted as `deferred` per ADR-0039 (reactivate when external contributors join)
- **pendingDecisionQueueCount**: `0` (cleared per ADR-0039 resolution of ADR-0036/0037/0038)
- **HIL-RS-02-GOV-EXCEPTION-01**: Resolved in HIL-RS-02-A1 (Done 2026-06-20)
- **A2A3_UNLOCK**: `a1Status=="Done" && pendingDecisionQueueCount==0` = satisfied → A2/A3 unblocked
- **SafeMode invariants**: Preserved per ADR-0039 NON-RELAXABLE

## Stream A Phase 1 Metadata Snapshot（2026-05-18）

| Issue | Status | Priority | Depends | Blockers | Delta vs prior run |
|---|---|---|---|---|---|
| HIL-RS-01 parent plan | In Progress | P1 | HIL-RS-01-A1, HIL-RS-02-A1 | `pendingDecisionQueueCount>0` | none |
| HIL-RS-01-A1 minimum I/F | In Progress | P1 | none | human approval pending | none |
| HIL-RS-02-A1 governance hardening | In Progress | P1 | HIL-RS-01-A1 freeze values | GOV exception held | none |
| CE0 contract freeze | Open | P1 | HIL-RS-01-A1 freeze vocabulary (read-only) | approval record pending | none |
| CE0 core-graph repositioning | Open | P1 | CE0 contract freeze | held items unresolved | none |

## Stream A Phase 2 ADR Clarification（Context / Decision / Consequences）

### Context
- Stream A の最短クリティカルパスは **A1契約凍結 → RS-02-A1統治硬化 → CE0 read-only handoff固定**。
- 承認待ち項目（Pending/held）が残る状態での下流着手は、`Pending bypass` と同義になり統治契約違反になる。

### Decision
- 依存グラフを以下に固定する（再定義禁止）。
  - `HIL-RS-01-A1` → `HIL-RS-02-A1` → `HIL-RS-01(parent Proceed Go)`
  - `HIL-RS-01-A1` → `CE0-contract-freeze` → `CE0-core-graph-repositioning`
- 要承認事項を明示し、承認前は `Proceed=Hold` を維持する。
  - `Approval Record`
  - `HIL-RS-02-GOV-EXCEPTION-01`

### Consequences
- Open化条件（Draft→Open）は「固定キーdrift=0 かつ 要承認事項がissue本文に在庫化済み」である。
- Go条件（Open→In Progress/Done）は `a1Status=="Done" && pendingDecisionQueueCount==0` を満たすまで禁止。
- 非互換変更要求は将来版隔離（`future-version backlog`）とし、現行凍結契約には混入させない。

## Stream A Phase 3 Contract Freeze Draft（Minimum I/F + Mock boundary）
- Minimum Input: `freezeContractId`, `contractIds`, `schemaVersion`, `overridePolicy`, `safeModeDefault`, `safeModeBoundary`, `pendingDecisionQueueCount`, `approvalRecord`.
- Minimum Output: `decision(Proceed|Hold|Stop)`, `executeAllowed`, `reasonCodes`, `requiredHumanActions`, `auditEventRef`.
- Error surface: `NOGO_CONTRACT_DRIFT`, `NOGO_SAFE_MODE_REGRESSION`, `NOGO_OVERRIDE_POLICY_REGRESSION`, `HOLD_PENDING_QUEUE`.
- Audit event required fields: `timestamp`, `actor`, `phase`, `inputSnapshot`, `gateResult`, `reason`, `nextAction`.
- Mock boundary（UI先行可能範囲）: `decision/executeAllowed/reasonCodes` まで。`Pending -> Approved/Rejected` の実遷移確定は不可。
- Non-compatible change policy: 新規遷移・新規固定キー・承認主体変更は `future-version` に隔離。

## Stream A Phase 4-6 Execute / Verify / Proceed Rule（2026-05-18 fixed）
- Execute: AC/DoD と相互リンク整備のみ（docs-only, contract-only）。
- Verify command set: `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` / `git diff --check`.
- Self-correction cap: 最大3回。4回目相当は `Stop`。
- Proceed output partition:
  - **完了**: fixedKeyDrift=0 かつ pendingDecisionQueueCount=0 を満たしたissue
  - **要承認**: Pending/held が残るissue
  - **保留**: 依存解決待ちでOpen化条件未達のissue

## Canonical Gate Equation（A1 unlock single predicate）
- `A2A3_UNLOCK = (a1Status=="Done" && pendingDecisionQueueCount==0)`
- `Proceed=Go` は `A2A3_UNLOCK && fixedKeyDrift==0 && safeModeRetreat==false` のときのみ。
- `Proceed=Hold` は `pendingDecisionQueueCount>0`（未承認/heldを含む）。
- `Proceed=Stop` は `pendingBypassDetected || contractRedefinitionRequested || fixedKeyDrift>0 || safeModeRetreat || verifyAttempts>3`。


## Stream E Contract Gate Declaration
- 本Issueは **HIL-RS-01 A1 minimum interface contract の唯一ゲート** として扱う。
- A2/A3 を含む下流は、本Issueで固定した契約値を **read-only** 参照し、契約再定義を行わない（read-only handoff原則）。
- `Pending` 承認が1件でも残る場合は、判定を `Hold` として明記し、`executeAllowed=false` を維持する。

## Mission
A1最小I/F契約（Critique / ReDiff / Attribution / Error）を、責務境界と停止条件込みで再読可能に固定する。

## Serial Phases（固定）
1. Phase 1 Read
2. Phase 2 ADR（Context / Decision / Consequences）
3. Phase 3 Plan（AC / DoD）
4. Phase 4 Execute
5. Phase 5 Verify
6. Phase 6 Proceed

## Constraints（固定参照）
- `freezeContractId` / `schemaVersion` / `overridePolicy` / `safeModeBoundary` は**固定参照のみ**（再定義禁止）。
- `Pending` 項目の bypass は禁止。
- mock契約参照で独立遂行し、外部レーン完了待ちを前提化しない。
- A1未承認事項は「未承認のまま」扱い、確定化しない。

## Phase 1 Read
### Re-read checkpoints
- Constraints の固定語彙・固定値・再定義禁止境界を再読する。
- Serial Phases の順序逸脱がないことを再読する。
- Hold/NoGo reason code と Stop条件の適用ルールを再読する。

### Context
- A1はHIL-RS-01/02の統治契約SSOT。
- A1未固定のまま後続へ進むと、承認遷移と責務境界が分岐する。
- A1が曖昧だとA2/A3で契約再定義が発生する。

## Phase 2 ADR（C/D/C）
### Read同期
- Phase 1の固定語彙・固定値・停止条件を再読し、差分0を確認してからADR記述へ進む。
### Context
- 失敗モードは `Pending bypass` と `AI承認代行`。
- 契約曖昧性はA2/A3の差分解釈を誘発し、監査不可能性を増幅する。

### Decision
- 最小I/F・責務分界・承認ゲートを固定する。
- 固定語彙（再定義禁止）:
  - `freezeContractId`, `contractIds`, `schemaVersion`, `overridePolicy`, `contractLinkLocked`, `sharedResourceFreeze`, `safeModeDefault`, `safeModeBoundary`, `unlockRule`, `decisionQueueTransition`, `NoGo return path`
- 固定値（凍結）:
  - `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
  - `contractIds=A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|A1-ERROR-IF`
  - `schemaVersion=1.0.0`
  - `overridePolicy=human_dual_control_only`
  - `contractLinkLocked=true`
  - `sharedResourceFreeze=true`
  - `safeModeDefault=ON`
  - `safeModeBoundary=SAFE_MODE_STRICT_ON`
  - `unlockRule=A2A3_UNLOCK`
  - `decisionQueueTransition=Pending -> Approved | Pending -> Rejected`
  - `NoGo return path=issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`
- 境界固定:
  - AIは `proposal-only`。
  - 承認遷移確定（`Pending -> Approved/Rejected`）は人間のみ。

### Consequences
- A2/A3は凍結値をread-only参照。
- 未承認時は `decision=Hold` / `executeAllowed=false`。
- A2/A3は契約再定義なしで進行可能（read-only前提）。

## Phase 3 Plan（AC / DoD）
### Read同期
- Phase 2 Decision/Consequencesを再読し、A2/A3へ波及する再定義を追加しないことを確認する。
### Acceptance Criteria
- AC-1: 固定語彙/固定値ドリフト0。
- AC-2: `Pending` bypass禁止が明示されている。
- AC-3: `NoGo return path` が一意固定。
- AC-4: 外部レーン完了待ちを前提化しない mock契約参照が明示。
- AC-5: 判定式（`a2a3Unlock`）と停止時条件が明示されている。
- AC-6: Critique/ReDiff/Attribution/Error の4契約IDが最小I/F集合として明示されている。

### Definition of Done
- DoD-1: `safeModeDefault=ON` / `safeModeBoundary=SAFE_MODE_STRICT_ON` 後退なし。
- DoD-2: `overridePolicy=human_dual_control_only` 後退なし。
- DoD-3: AI責務と人間承認責務の分離が明示。
- DoD-4: `Pending` が1件でもあれば Execute不許可。
- DoD-5: Hold/NoGo理由コードとStop条件が同一契約内で再読可能。

## Phase 4 Execute（文面整備のみ）
### Read同期
- Phase 3 AC/DoDを再読し、文面整備が契約固定の範囲内（docs-only）に留まることを確認する。
- 実施原則: **契約優先**。実装詳細は追加しない。
- Inputs: `freezeContractId`, `contractIds`, `schemaVersion`, `safeModeDefault`, `safeModeBoundary`, `pendingDecisionQueueCount`, `a1Status`
- Outputs: `executeAllowed`, `decision(Go|NoGo|Hold)`, `reasonCodes`, `requiredHumanActions`, `noGoReturnPath`
- Gate: `Pending -> Approved | Pending -> Rejected` 以外禁止。

### Responsibility Boundary（契約責務境界）
- Human Approver（2者承認）:
  - `decisionQueueTransition` の最終確定のみ実施可能。
  - `Approved/Rejected` の根拠と `requiredHumanActions` を監査可能な形で記録する。
- AI / Automation:
  - `executeAllowed` / `decision` / `reasonCodes` の算出提案のみ可能（proposal-only）。
  - `Pending` を終端状態へ遷移させる操作は禁止。
- Parent Plan / Downstream（A2/A3）:
  - A1固定値を read-only 参照する。
  - `freezeContractId` / `schemaVersion` / `safeModeBoundary` の再定義は禁止。

### Hold / NoGo Reason Codes（固定）
- `HOLD_PENDING_QUEUE`: `pendingDecisionQueueCount > 0`
- `NOGO_SAFE_MODE_REGRESSION`: `safeModeDefault!=ON` または `safeModeBoundary!=SAFE_MODE_STRICT_ON`
- `NOGO_OVERRIDE_POLICY_REGRESSION`: `overridePolicy!=human_dual_control_only`
- `NOGO_CONTRACT_DRIFT`: `freezeContractId` / `contractIds` / `schemaVersion` の不一致
- `NOGO_SHARED_RESOURCE_CONFLICT`: `sharedResourceFreeze` 違反または競合検知
- `NOGO_UNAPPROVED_A1_ASSERTION`: A1未承認事項の確定化要求を検知

### Stop Conditions（強制停止）
以下のいずれかを検知した時点で `decision=Stop` とし、以降フェーズを進めない。
1. A1未承認事項の確定化要求
2. safeMode後退前提
3. 指定外編集（本ファイル以外の変更）

## Phase 5 Verify
### Read同期
- Phase 4の入出力/Gate/責務境界を再読し、検証対象を固定してから自己照合を開始する。
### Verify Procedure（自己修復上限=3）
1. Contract Snapshot照合（固定語彙/固定値/NoGo return path）。
2. 責務境界照合（AI proposal-only / Human final approval）。
3. `Pending` 残存チェック（1件でも `executeAllowed=false`）。
4. AC/DoD照合（判定式・停止条件・4契約ID集合の明示を含む）。
5. 不一致があれば修正し再検証（最大3回）。
6. 3回で解消不能なら **致命エラーとして停止**（Phase 6 Proceedへ進まない）。

### Verification Result Template
- self-check #1: Contract drift
- self-check #2: Responsibility boundary
- self-check #3: Pending/Stop condition
- self-correction count: `x/3`

## Phase 6 Proceed
### Read同期
- Phase 5検証結果（self-correction countを含む）を再読し、3回超過時はProceed禁止を確認する。
- Proceed=Go 条件:
  - `a1Status=="Done" && pendingDecisionQueueCount==0`
  - Stop条件未検知
  - AC/DoD全件pass
- Hold 条件:
  - 承認不足、`Pending`残存、監査証跡不足
- Stop 条件:
  - 「Stop Conditions（強制停止）」に合致

### Current Record（this edit）
- decision: `Hold`
- executeAllowed: `false`
- reasonCodes:
  - `HOLD_PENDING_QUEUE`（承認待ちを想定）
- noGoReturnPath:
  - `issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`
- note:
  - 本更新は契約文面整備のみ。実装詳細の追加なし。

## Stream A（critical path）phase-locked update — 2026-05-09

### Phase 1 Read（Plan → Execute → Verify → Proceed）
- Plan: 本issue / 親計画issue / FB-P2C A1 issue / SSOT（`02_Architecture/hil_rs_01_a1_minimum_interface_contract.md`）を再読し、未確定一覧を再生成する。
- Execute: 未確定項目を次の2件で固定。
  1. `Approval Record=Pending`
  2. `HIL-RS-02-GOV-EXCEPTION-01=held`
- Verify: 固定値（`freezeContractId`, `schemaVersion`, `overridePolicy`, `safeModeDefault`, `safeModeBoundary`, `decisionQueueTransition`）のドリフト `0` を確認。
- Proceed: Phase 2へ進行。

### Phase 2 ADR/Decision明文化（Plan → Execute → Verify → Proceed）
- Context: A2/A3が参照する契約をA1以外で再定義すると、`A1 -> A2 -> A3` の依存順と監査線が破綻する。
- Decision:
  - 確定項目: 固定値群と `A2A3_OPEN_ALLOWED` 判定式は凍結維持。
  - 承認待ち項目: `Approval Record`, `HIL-RS-02-GOV-EXCEPTION-01` は Decision Queue に残し、確定扱いしない。
- Consequences:
  - `Pending -> Approved | Pending -> Rejected` 以外の遷移は禁止。
  - `pendingDecisionQueueCount>0` の間は `executeAllowed=false` を強制。
- Verify: CDC（Context/Decision/Consequences）3点が明示され、承認待ち/確定の分離が維持されることを確認。
- Proceed: Phase 3へ進行。

### Phase 3 契約固定（Plan → Execute → Verify → Proceed）
- Plan: A2/A3向け固定I/F（型、署名、判定条件、schemaVersion）を read-only で再宣言する。
- Execute（凍結宣言）:
  - Interface IDs: `A1-CRITIQUE-IF | A1-REDIFF-IF | A1-ATTR-IF | A1-ERROR-IF`
  - schemaVersion: `1.0.0`
  - Signatures: `CritiqueV1`, `ReDiffV1`, `AttributionV1`, `A1ErrorV1`
  - 判定条件: `A2A3_OPEN_ALLOWED = (a1Status=="Done" && pendingDecisionQueueCount==0 && freezeContractId=="HIL-RS-02-A1-CONTRACT-FREEZE-v1" && schemaVersion=="1.0.0" && overridePolicy=="human_dual_control_only" && contractLinkLocked==true && sharedResourceFreeze==true && safeModeDefault=="ON" && safeModeBoundary=="SAFE_MODE_STRICT_ON")`
- Verify: `Pending` 残存中のため `Go` を出していないことを確認。
- Proceed: Phase 4へ進行。

### Phase 4 受け渡し（read-only contract summary）
- Stream B/C 参照専用サマリ:
  - SSOT: `02_Architecture/hil_rs_01_a1_minimum_interface_contract.md`
  - `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
  - `schemaVersion=1.0.0`
  - `overridePolicy=human_dual_control_only`
  - `safeModeDefault=ON`
  - `safeModeBoundary=SAFE_MODE_STRICT_ON`
  - `decisionQueueTransition=Pending -> Approved | Pending -> Rejected`
  - `unlockRule=A2A3_UNLOCK`
- 判定: `Hold`（承認待ち2件が未解消）。


## Stream A execution sync（2026-05-09 / A1 minimum interface contract close-ready）

### Phase 1: 契約整理
- Read: Phase開始時に本Issue/親Issue/FB-P2C A1/ADR-0026を再読。
- Context: A1契約の曖昧性は `Pending bypass` と `AI承認代行` を誘発する。
- Decision（最小I/F固定）:
  - API signatures: `CritiqueV1`, `ReDiffV1`, `AttributionV1`, `A1ErrorV1`
  - Type boundary: `contractIds=A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|A1-ERROR-IF`
  - Versioning: `schemaVersion=1.0.0`（v1固定、拡張はv2のみ）
  - Compatibility: v1必須キー集合維持・unknown key=`400`・SafeMode境界後退禁止
- Consequences: A2/A3は read-only参照のみ、再定義は禁止。

### Phase 2: ADR整合
- `ADR-0026` と照合し、以下を固定契約として明示:
  - `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
  - `overridePolicy=human_dual_control_only`
  - `decisionQueueTransition=Pending -> Approved | Pending -> Rejected`
- 変更可能領域:
  - mock検証観点の説明追加
  - 運用注記（reason code補足）
- 変更不可領域:
  - contract IDs / schemaVersion / unlockRule / safeMode境界

### Phase 3: 受入条件固定（下流向け）
- AC-1: 4契約ID + 4シグネチャ + schemaVersion を同時充足。
- AC-2: `pendingDecisionQueueCount>0` では `executeAllowed=false`。
- AC-3: `A2A3_OPEN_ALLOWED` 条件以外のOpen化を禁止。
- DoD-1: Verify手順で Contract drift / Responsibility boundary / Pending gate を全pass。
- DoD-2: self-correction `0/3` から記録し、`>3` でStop。
- DoD-3: 未承認2件（`Approval Record`, `HIL-RS-02-GOV-EXCEPTION-01`）解消まで `Hold` 維持。

## Stream D execution log（2026-05-09 / HIL-RS-01-A1 minimum interface contract）

### Phase 1: Read Sync
- Status/Priority/Scope/Dependencies/固定語彙（`freezeContractId`,`schemaVersion`,`overridePolicy`,`safeModeBoundary`）を再読し、差分不一致なし（drift=0）。

### Phase 2: ADR Consensus
- Context: A1契約が曖昧な場合、A2/A3で再定義が発生し監査可能性を損なう。
- Decision: Critique/ReDiff/Attribution/Error の最小I/F集合、判定式、責務境界、Stop条件を本Issueで固定維持する。
- Consequences: 人間承認記録が `Pending` の間は `executeAllowed=false`、`decision=Hold` を継続する。

### Phase 3: Plan
- AC補完: `A2A3_OPEN_ALLOWED` 以外のOpen化禁止、`NoGo return path` 一意固定、`Pending bypass` 禁止。
- DoD補完: `proposal-only` 境界維持、2者承認責務分離、safeMode後退なし。
- 検証方法: Contract Snapshot照合→責務境界照合→Pending残存照合→AC/DoD照合。
- 停止条件: 未承認事項の確定化要求、safeMode後退前提、指定外編集検知。

### Phase 4: Execute
- 契約文面整備のみ実施（docs-only）。
- 実装コード・他Issue・他ファイルへの変更は未実施。

### Phase 5: Verify
- self-check #1 Contract drift: pass
- self-check #2 Responsibility boundary: pass
- self-check #3 Pending/Stop condition: pass（`Pending` 残存のため `executeAllowed=false`）
- self-correction count: `0/3`

### Phase 6: Proceed
- 判定: `Hold`
- 理由: `HOLD_PENDING_QUEUE`（承認記録がPendingのため）。
- executeAllowed: `false`
- noGoReturnPath: `issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`


## Stream H gate revalidation（2026-05-10 / A1 minimum interface contract read-only freeze）

### Phase 1 Read
- 最新メタ（Status/Scope/Dependencies）と Gate Declaration を再同期し、A1が唯一ゲートであることを再確認。
- `Pending` が残る限り `executeAllowed=false` を維持する方針を再確認。

### Phase 2 ADR（Context / Decision / Consequences）
- Context: 下流A2/A3で契約再定義が発生すると監査線が分岐する。
- Decision: Critique/ReDiff/Attribution/Error の最小I/F、固定語彙、固定値、責務境界、停止条件を本Issueで凍結維持（read-only handoff）。
- Consequences: `Pending -> Approved | Pending -> Rejected` 以外は不可。`Pending` 残存時は `decision=Hold` と `executeAllowed=false` を維持。

### Phase 3 Plan（AC / DoD）
- AC: 4契約ID、判定式、NoGo return path、`Pending bypass` 禁止、safeMode境界維持を再確認。
- DoD: `overridePolicy=human_dual_control_only` と `safeModeDefault=ON` / `safeModeBoundary=SAFE_MODE_STRICT_ON` の後退なしを再確認。

### Phase 4 Execute（docs-only）
- 本Issue内の契約文面のみ更新し、指定外ファイルは未編集。
- 下流向け方針を `read-only` として明文化し、再定義禁止を維持。

### Phase 5 Verify
- self-check #1 Contract drift: pass（固定語彙/固定値の差分なし）。
- self-check #2 Responsibility boundary: pass（AI proposal-only / Human final approval を維持）。
- self-check #3 Pending/Stop condition: pass（`Pending` 想定下で `Hold` / `executeAllowed=false` を維持）。
- self-correction count: `1/3`（文面同期1回で収束）。

### Phase 6 Proceed
- 判定: `Hold`
- executeAllowed: `false`
- reasonCodes:
  - `HOLD_PENDING_QUEUE`
- proceedPolicy:
  - Proceedは `a1Status=="Done" && pendingDecisionQueueCount==0` を満たすまで禁止。


## Stream A critical-path alignment update（2026-05-10）

### Phase 1 Read
- Read同期: 本issue / FB-P2C A1 issue / HIL-RS-01親計画 issue / ADR-0028。
- triage stopper check: `Status` / `Priority` 欠落なし。

### Phase 2 ADR明文化
- Context: CE-0/CE-1 契約がA1外で再定義されると、責務分離と承認ゲートが監査不能化する。
- Decision: `freezeContractId`, `schemaVersion`, `safeModeBoundary` を参照固定し、`Pending -> Approved | Pending -> Rejected` 以外を禁止。
- Consequences: AIはproposal-only、人間のみ最終承認。Pendingが残る限り `Hold` 継続。

### Phase 3 Plan（AC / DoD）
- AC: contract drift 0 / responsibility boundary drift 0 / pending bypass 0 / stop condition consistency 0。
- DoD: `a1Status=="Done" && pendingDecisionQueueCount==0` を満たすまで `executeAllowed=false` を維持。

### Phase 4-6 Execute / Verify / Proceed
- Execute: docs-onlyで契約表現を整合。
- Verify: 4観点（drift, boundary, pending gate, stop consistency）を照合。
- Proceed判定: 未解決Pendingがあるため `Hold/Needs-decision`。
## Stream A contract freeze serial run (2026-05-10 / P0 critical path)

### Phase 1: Triage Stopper確認（Plan → Read → Execute → Verify → Proceed）
- Plan:
  - 目的: triage blocker の残存有無を確認し、契約凍結の開始可否を判定する。
  - 対象ファイル: 本ファイル（docs-only）。
  - AC: triageエラー有無、CE1メタ欠落有無、依存前提の確定/未確定を明示する。
  - DoD: CE1メタ欠落が残る場合は `依存前提未確定` として記録する。
- Read:
  - 本ファイルの最新状態を再読し、契約固定値（`freezeContractId`, `schemaVersion`, `overridePolicy`, `safeModeBoundary`）との差分なしを確認。
- Execute:
  - triage stopper 判定結果を記録: `triage_error=0`。
  - CE1メタ欠落は未解消として記録: `dependency_status=依存前提未確定`。
- Verify:
  - AC/DoD照合: pass（未確定依存を明示済み）。
  - self-correction: `0/3`。
- Proceed:
  - Phase 2へ進行（依存未確定は保持したまま先行可能な docs 契約明文化のみ実施）。

### Phase 2: ADR明文化（必須）
- Context:
  - 契約凍結前に Context/Decision/Consequences を明文化しない場合、A1境界が再定義され downstream の read-only 契約参照が破綻する。
- Decision:
  - 契約境界は本runで再定義せず、既存固定値を参照専用で維持する。
  - CE1メタ欠落が残るため、`依存前提未確定` を維持し、実装判断に使用しない。
- Consequences:
  - 契約凍結文面は確定可能だが、Proceed判定は `Hold/Needs-decision` を継続する。
  - 未承認/未確定依存の推測確定は禁止。
- Verify:
  - C/D/C 3点明示を確認: pass。
- Proceed:
  - Phase 3へ進行可（docs-only）。

### Phase 3: 契約凍結文面の確定
- Interface boundary（fixed/read-only）:
  - `contractIds=A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|A1-ERROR-IF`
  - `schemaVersion=1.0.0`
  - `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
- Non-goals（fixed）:
  1. 契約IDの追加/改名/削除
  2. `schemaVersion` 改版
  3. SafeMode境界（`safeModeDefault=ON`, `safeModeBoundary=SAFE_MODE_STRICT_ON`）の緩和
  4. Pending bypass（`Pending -> Approved | Pending -> Rejected` 以外）
- Verify:
  - インターフェース境界と非目標を明記: pass。
- Proceed:
  - Phase 4へ進行。

### Phase 4: 依存切断宣言
- 契約版数:
  - `HIL-RS-02-A1-CONTRACT-FREEZE-v1` / `schemaVersion=1.0.0`
- 後方互換ルール:
  - v1固定キー集合は互換維持必須、unknown key は `400`。
- 破壊的変更禁止条件:
  - A1再起票と人間承認記録（`approved_by`, `approved_at`, `evidence`）が揃うまで禁止。
- Stream分離:
  - 他ストリームは read-only 参照のみ。契約再定義・判定代行を禁止。
- Verify:
  - 依存切断3要素（契約版数/互換/破壊的変更禁止）を明記: pass。

### Phase 5: 完了判定
- AC/DoD:
  - AC pass（Phase 1-4の明示要件充足）。
  - DoD pass（docs-only契約凍結文面として完了）。
- Traceability:
  - triage（Phase1）→ ADR（Phase2）→ freeze（Phase3）→ dependency cut（Phase4）を同一runで記録。
- 未解決論点:
  - `CE1メタ欠落`（依存前提未確定）
  - `Approval Record=Pending`
  - `HIL-RS-02-GOV-EXCEPTION-01=held`
- Final decision:
  - `Hold/Needs-decision`（未解決論点が解消するまでGo不可）。

## Stream A contract freeze clarification（2026-05-10）

### Read-only contract（固定）
- API signature set:
  - `CritiqueV1(input: CritiqueInputV1): CritiqueResultV1`
  - `ReDiffV1(input: ReDiffInputV1): ReDiffResultV1`
  - `AttributionV1(input: AttributionInputV1): AttributionResultV1`
  - `A1ErrorV1(input: A1ErrorInputV1): A1ErrorResultV1`
- Minimal shared types:
  - `ApprovalRecordV1{approved_by, approved_at, evidence}`
  - `GateDecisionV1{decision, executeAllowed, reasonCodes}`
  - `DecisionQueueTransitionV1{Pending->Approved|Pending->Rejected}`
- Audit events（必須）: `query`, `bundle`, `proposal`, `apply`。

### Mock usage boundary
- 許可: スキーマ適合テスト、reason code 出力確認、`Pending` 時 `executeAllowed=false` 検証。
- 禁止: 承認状態の擬似確定、`freezeContractId/schemaVersion/contractIds` 書換、SafeMode境界緩和。

### Proceed gate（A1専用）
- `Go`: `a1Status=="Done" && pendingDecisionQueueCount==0 && fixedKeyDrift==0`
- それ以外: `Hold/NoGo`（推測で `Go` を作らない）。

## Stream A synchronization note（2026-05-17 UTC / governance freeze alignment）

### Read Sync
- 再読対象: 本Issue と `issue-HIL-RS-02-A1-governance-contract-hardening.md`。
- 整合結果:
  - 最小I/F固定値（`freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`, `schemaVersion=1.0.0`, `overridePolicy=human_dual_control_only`, `safeModeBoundary=SAFE_MODE_STRICT_ON`）は差分0。
  - 判定式 `A2A3_UNLOCK = (a1Status=="Done" && pendingDecisionQueueCount==0)` を継続採用。

### Contract guardrail reaffirmation
- `Pending bypass` は禁止。
- `Pending -> Approved | Pending -> Rejected` 以外の遷移は禁止。
- Approval Pending 中は `executeAllowed=false` を維持。
- NoGo return path は本Issue（A1 SSOT）へ固定。

### Proceed state
- 判定: **Hold/Needs-decision 継続**。
- 理由: Approval Record（`approved_by`, `approved_at`, `evidence`）未確定のため Go 条件未達。


## Stream B proceed note（2026-05-19 / A1 interface freeze as downstream contract anchor）

### Contract anchor for downstream
- A1 固定契約は下流の唯一アンカーとして以下を維持する。
  - `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
  - `contractIds=A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|A1-ERROR-IF`
  - `schemaVersion=1.0.0`
  - `overridePolicy=human_dual_control_only`
  - `safeModeBoundary=SAFE_MODE_STRICT_ON`

### Mock-first cut line
- 下流がモックで利用できる境界は `executeAllowed/decision/reasonCodes/noGoReturnPath` まで。
- `Pending -> Approved/Rejected` の確定遷移は人間承認のみで、AI/自動化は proposal-only。

### Backward compatibility rule
- 既存固定キーの変更は non-backward-compatible とみなし、A1 本線では受け付けず `future-version backlog` へ隔離する。

## Stream A Contract Freeze Checkpoint（2026-05-19, Plan → Execute → Verify → Proceed）

### Phase 1: Contract Baseline Read
- 現行AC/DoD/依存/非目標を再読し、対象3 issue 間で契約語彙を照合した。
- Baseline差分（事前想定との差分）:
  - `Approval Record` は依然 `Pending`、`HIL-RS-02-GOV-EXCEPTION-01` は `held` のままで、Go条件未達。
  - `A2A3_UNLOCK = (a1Status=="Done" && pendingDecisionQueueCount==0)` は3 issueで一致し、driftなし。
  - `freezeContractId/schemaVersion/overridePolicy/safeModeBoundary` は固定値一致（再定義なし）。

### Phase 2: ADR明文化（Context / Decision / Consequences）
- Context: 承認未了状態での下流着手は `Pending bypass` となり契約違反。
- Decision: HIL-RS最小I/Fは read-only contract とし、承認前は仕様拡張・実装遷移を禁止。
- Consequences: `Proceed=Hold` を維持し、契約変更要求は A1 SSOT へ差し戻す。

### Phase 3: Issue Contract Freeze
- AC/DoD/Stop条件の同期ポリシーを固定:
  - AC: fixed key drift=0 / Pending bypass禁止 / A2-A3非干渉。
  - DoD: `safeModeDefault=ON`・`safeModeBoundary=SAFE_MODE_STRICT_ON`・`overridePolicy=human_dual_control_only` の後退禁止。
  - Stop: fixed key drift、SafeMode後退、未定義競合、self-correction>3。
- 明示制約: **承認前は read-only contract**（編集は契約文面整合のみ、実装系変更禁止）。

### Phase 4: Verify
- 用語整合チェック: `Security Officer` / `System Owner` / `Platform Operator` の役割語彙を維持。
- 未解決依存チェック: `Approval Record=Pending` のため `Proceed=Hold` が唯一許可判定。
- 矛盾チェック: fixed identifiers と gate equation に矛盾なし。

### Proceed
- 判定: **Hold/Needs-decision（承認待ち継続）**。
- 次アクション: 承認記録 (`approved_by`, `approved_at`, `evidence`) 充足後にのみ Go 再判定。

## Stream A serial run record（2026-05-20 / A1 contract gate）

### Phase 1: Read & Scope Lock
- A1最小I/F契約の固定語彙・固定値・禁止遷移を再読した。
- Scope lock: 本ファイル更新のみ、実装変更なし（docs-only）。

### Phase 2: ADR明文化（Context / Decision / Consequences）
- Context: A1を再定義可能にすると A2/A3の契約分岐が再発する。
- Decision: `freezeContractId` / `schemaVersion` / `overridePolicy` / `safeModeBoundary` を read-only 維持。
- Consequences: 承認待ち中は `decision=Hold`, `executeAllowed=false` を継続する。

### Phase 3: Plan → Execute → Verify
- Plan: AC/DoD不足の補完対象有無を確認。
- Execute: AC/DoDは既存で充足、追記は実行記録のみに限定。
- Verify（self-correction `0/3`）:
  - fixed-key drift: `0`
  - `Pending -> Execute` 禁止: pass
  - NoGo return path固定: pass

### Phase 4: Proceed / Stopper
- 判定: **Hold**（承認待ち）。
- Stopper: `Approval Record` 未充足。

## Stream D minimum interface contract inventory（2026-06-13）

### Contract inputs（mock検証可能な署名のみ）
| Signature | Required input | Notes |
|---|---|---|
| `HIL_RS_DECISION_GATE_V1` | `issueId`, `phase`, `approvalRecord`, `pendingDecisionQueueCount`, `policySnapshot` | Go/Hold/Stop 判定だけを返す。承認確定は行わない。 |
| `HIL_RS_PATCH_PROPOSAL_V1` | `sourceBundleHash`, `proposalId`, `actor`, `contextBundleRef` | AI候補は proposal-only。Core/Consensus Graph 直接更新は禁止。 |
| `HIL_RS_APPLY_JUDGEMENT_V1` | `proposalId`, `humanDecision`, `approvedBy`, `approvalRecord` | 人間判断後の適用判定契約。AIによる `human_reviewed` 昇格は禁止。 |

### Contract outputs
| Signature | Required output | Notes |
|---|---|---|
| `HIL_RS_DECISION_GATE_V1` | `gateStatus`, `held[]`, `reasonCodes[]`, `executeAllowed` | `Pending` 残存時は `executeAllowed=false`。 |
| `HIL_RS_PATCH_PROPOSAL_V1` | `patchDraft`, `riskLabels[]`, `auditEventRef` | `riskLabels[]` は `safe_mode`, `approval_pending`, `rollback_required` を表現可能にする。 |
| `HIL_RS_APPLY_JUDGEMENT_V1` | `applyResult`, `rollbackRef`, `auditEventRef` | `rollbackRef` 欠損時は No-Go。 |

### Audit events and rollback
- Required audit events: `query`, `bundle`, `proposal`, `apply`。
- `apply` は人間承認後のイベントであり、AI候補生成段階で発火済みとして扱わない。
- `rollbackRef` は採用/保留/破棄のどれでも後から辿れる参照を要求する。実装方式は未確定のまま下流へ渡す。

### Proceed classification
- 現時点の判定: **approval pending**。
- Done-ready条件: `Approval Record` 完備、`fixedKeyDrift==0`、`pendingDecisionQueueCount==0`、SafeMode後退なし。
- Hold条件: Approval Record Pending、または `Pending -> Execute` の推測遷移が必要になった場合。
