# Issue Draft: HIL-RS-01 A1 Architecture 最小I/F契約固定（Stream D）

- Type: Process
- Status: In Progress
- Lifecycle: Draft -> Open -> In Progress -> Done
- Priority: P1
- Owner: Stream H（A1 minimum interface contract only）
- Scope: 本ファイルのみ（docs-only）
- Dependencies: なし（A1最小I/Fの先行固定）
- Related ADR/Spec: `ADR-0026`, `ADR-0027`, `ADR-0028`


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
  - `unlockRule=a2a3Unlock = (a1Status=="Done" && pendingDecisionQueueCount==0)`
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
  - `unlockRule=a1Status=="Done" && pendingDecisionQueueCount==0`
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
