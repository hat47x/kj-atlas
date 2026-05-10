# Issue Plan: HIL-RS-01 次フェーズ実行計画（Human-in-the-loop / Reversible Synthesis, Stream D）

- Type: Process
- Status: In Progress
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P1
- Owner: Stream A（contract freeze and minimum interface agreement）
- Scope: 本ファイルのみ（docs-only）
- Dependencies:
  - `issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`
  - `issue-HIL-RS-02-A1-governance-contract-hardening.md`
- ADR Reference (read-only): `01_Plans/adr/ADR-0026-next-phase-human-in-the-loop-reversible-synthesis.md`
- Related ADR/Spec: `01_Plans/adr/ADR-0026-next-phase-human-in-the-loop-reversible-synthesis.md`, `01_Plans/adr/ADR-0027-hil-rs-02-next-phase-execution-plan.md`, `01_Plans/adr/ADR-0028-ai-cognitive-externalization-phase-plan.md`
- Expected verification level: `docs-check`

## Serial Phases（固定）
1. Phase 1 Read Sync（issue + ADR）
2. Phase 2 ADR明文化（Context / Decision / Consequences）
3. Phase 3 Plan（AC / DoD不足補完提案）
4. Phase 4 Execute（docs-only）
5. Phase 5 Verify（最大3回自己修復）
6. Phase 6 Proceed / Stop

## Constraints（固定）
- `freezeContractId` / `schemaVersion` / `overridePolicy` / `safeModeBoundary` は固定参照のみ（再定義禁止）。
- `Pending` bypass禁止。
- mock契約参照で独立遂行（外部レーン完了待ち前提を置かない）。
- SafeMode既定ONと厳格境界（`safeModeDefault=ON`, `safeModeBoundary=SAFE_MODE_STRICT_ON`）の後退禁止。
- 親計画として **A1/RS-02 A1参照整合を維持** し、契約語彙を再定義しない。

## Phase 1 Read Sync
- 親計画はA1契約（最小I/F + hardening）の参照ノードであり、再定義ノードではない。
- `ADR-0026` の Context / Decision / Consequences を再読し、以下を同期対象として固定する。

## Phase 2 ADR明文化（Context / Decision / Consequences）
### Context
- `ADR-0026` は、次フェーズを「保留維持・可逆・Human-in-the-loop反復」を価値アンカーにした契約先行計画として確定している。
- 親計画で契約値やゲート条件を再定義すると、A1→A2/A3 の依存順序と統治境界が崩れる。

### Decision
- 本issueは `ADR-0026` の実行メモとして、以下を**参照専用**で運用する。
  - `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
  - `schemaVersion=1.0.0`
  - `overridePolicy=human_dual_control_only`
  - `safeModeDefault=ON`
  - `safeModeBoundary=SAFE_MODE_STRICT_ON`
  - `decisionQueueTransition=Pending -> Approved | Pending -> Rejected`
- 実行順序は `Plan -> Architecture -> Implement -> Documentation` の契約先行を維持する（ADR-0026 D2）。
- 非目標は `ADR-0026` D3を継承し、以下を導入しない。
  - LLM Provider全面再設計
  - 単一正解を示唆する採点/ランキングUI
  - SafeMode既定ONの緩和
- Gate運用は `ADR-0026` D4 と整合させる。
  - `Go`: `a1Status=="Done" && pendingDecisionQueueCount==0`
  - `Hold`: `pendingDecisionQueueCount>0`
  - `NoGo/Stop`: SafeMode後退 / 固定キーdrift / 上位層矛盾 / 共有リソース競合

### Consequences
- `Pending` が残る限り `Proceed=Hold/Needs-decision` を維持し、推測確定しない。
- A2/A3への受け渡しは read-only contract summary のみとする。
- 停止条件に該当した場合は、上位層（00〜02）を先に修正提案してから再開する。

## Phase 3 Plan（AC / DoD不足補完提案）
### Acceptance Criteria
- AC-1: `ADR-0026` の Context/Decision/Consequences と本issueの記述に矛盾がない。
- AC-2: 固定参照値（`freezeContractId`, `schemaVersion`, `overridePolicy`, `safeMode*`, `decisionQueueTransition`）の drift=0。
- AC-3: `Pending` bypassなし（`Pending -> Approved | Rejected` 以外の遷移を追加しない）。
- AC-4: A2/A3非干渉（編集・判定代行なし）。
- AC-5: `NoGo return path` を A1契約issue に一意固定する。

### Definition of Done
- DoD-1: `safeModeDefault=ON` / `safeModeBoundary=SAFE_MODE_STRICT_ON` の後退なし。
- DoD-2: `overridePolicy=human_dual_control_only` の後退なし。
- DoD-3: 人間承認責務分離を維持（AIは判定補助のみ）。
- DoD-4: `pendingDecisionQueueCount>0` の間は `Hold/Needs-decision` のみ。
- DoD-5: Verifyで不一致が出た場合、最小修正→再検証を最大3回まで実施し、未解消ならStop。

## Phase 4 Execute（docs-only）
- 実施内容は文書整合のみ（契約再定義・実装変更なし）。
- 反映順序: A1固定参照値確認 → hardening参照確認 → 親計画整合反映。

## Phase 5 Verify（自己修復上限=3）
1. A1固定参照値との一致確認（drift=0）。
2. hardening参照（SoD/承認遷移固定）の一致確認。
3. `ADR-0026` D1〜D4との整合確認。
4. 非干渉確認（A2/A3への編集・判定代行なし）。
5. 不一致時は最小修正して再検証（最大3回）。
6. 3回で解消不能なら**致命エラーとして停止**（Proceed禁止）。

## Phase 6 Proceed / Stop
- Proceed条件:
  - `a1Status=="Done" && pendingDecisionQueueCount==0`
  - 固定参照値drift=0
  - SafeMode後退なし
- Hold条件:
  - `pendingDecisionQueueCount>0`
- Stop条件:
  - SafeMode境界後退 / overridePolicy後退 / fixed key drift / 上位層矛盾 / 共有リソース競合
  - `Pending` bypass要求 / 契約再定義要求 / 未定義競合の発生（推測解決せず停止）

## Proceed/Hold/Stop Audit Fix（判定監査の固定化）

### Audit Inputs（read-only）
- `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
- `schemaVersion=1.0.0`
- `overridePolicy=human_dual_control_only`
- `safeModeBoundary=SAFE_MODE_STRICT_ON`
- `decisionQueueTransition=Pending -> Approved | Pending -> Rejected`
- `approvalRecord`（`approved_by`, `approved_at`, `evidence`）

### Gate Equation（固定・再定義禁止）
- `Proceed = (a1Status=="Done" && pendingDecisionQueueCount==0 && fixedKeyDrift==0 && safeModeRetreat==false && undefinedConflictDetected==false)`
- `Hold = (pendingDecisionQueueCount>0 && stopSignalDetected==false)`
- `Stop = (pendingBypassDetected || contractRedefinitionRequested || undefinedConflictDetected || safeModeRetreat || fixedKeyDrift>0 || upperLayerConflict || sharedResourceConflict)`

### Audit Evidence（必須記録）
- 記録単位: `timestamp`, `actor`, `phase`, `inputSnapshot`, `gateResult`, `reason`, `nextAction`。
- `gateResult` は `Proceed | Hold | Stop` の3値以外を許可しない。
- `Hold` / `Stop` は `reason` を1件以上必須化する。

## Current Decision Queue Snapshot（2026-05-09）
- `Approval Record=Pending`
- `HIL-RS-02-GOV-EXCEPTION-01=held`
- 判定: **Hold/Needs-decision**（Proceed条件未充足）

## Read-only handoff summary（固定参照）
- `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
- `contractIds=A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|A1-ERROR-IF`
- `schemaVersion=1.0.0`
- `overridePolicy=human_dual_control_only`
- `safeModeDefault=ON`
- `safeModeBoundary=SAFE_MODE_STRICT_ON`
- `decisionQueueTransition=Pending -> Approved | Pending -> Rejected`
- `unlock precondition=a1Status=="Done" && pendingDecisionQueueCount==0`


## Stream A serial execution record（2026-05-09 / critical-path parent plan sync）

### Phase 1: Read同期
- 対象: 本Issue / `ADR-0026` / `issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md` / `issue-FB-P0-2A2B2C-stream-c-planning-baseline.md` / `issue-FB-P2C-01-a1-interface-contract.md`。
- 差分サマリ:
  - HIL系: `Status=In Progress`, `Priority=P1`
  - FB系: `Status=Open`, `Priority=P0`
  - 依存順: `A1 -> A2 -> A3`（変更なし）
- 不一致ログ: 優先度はFBが高いが、契約ゲートはHIL-A1完了条件に従うため、優先度のみではProceed不可。

### Phase 2: ADR明文化
- Context: 親計画は契約固定値の再定義を禁止し、A1契約を唯一ゲートとして扱う必要がある。
- Decision: 承認待ち（`Approval Record=Pending`, `HIL-RS-02-GOV-EXCEPTION-01=held`）を保持したまま、`Hold/Needs-decision` を継続する。
- Consequences: `pendingDecisionQueueCount==0` になるまでは、A2/A3のGo判定を行わない。

### Phase 3: Plan（変更対象行と理由）
- 変更対象: 本節追記のみ。
- 理由: AC/DoDの欠落はなく、直列プロトコルの実行証跡追加だけが最小変更であるため。

### Phase 4-6: Execute / Verify / Proceed
- Execute: docs-onlyで追記。
- Verify: 固定キー・判定ゲート・NoGo条件の語彙一致を確認（drift=0）。
- Proceed: `Hold/Needs-decision`。


## Stream A CE-0/CE-1 and A1 gate sync（2026-05-10）

### Phase 1 Read
- 対象再読: 本issue / A1最小I/F issue / FB-P2C A1 issue / ADR-0028。
- triage stopper check: `Status` / `Priority` 欠落なし。

### Phase 2 ADR明文化
- Context: 親計画で契約語彙を再定義すると A1ゲートが崩れ、下流の安全解放条件が失効する。
- Decision: CE-0/CE-1対象は A1固定値を参照専用で固定（`freezeContractId`, `schemaVersion`, `safeModeBoundary` など）。承認遷移は `Pending -> Approved | Pending -> Rejected` のみ許可。
- Consequences: pendingDecisionQueueCount>0 の間は `Hold` 維持、A2/A3はread-only handoffのみ。

### Phase 3 Plan（AC / DoD）
- AC: safeMode後退0 / contract drift 0 / pending bypass禁止 / read-only handoff成立。
- DoD: Go条件（`a1Status=="Done" && pendingDecisionQueueCount==0 && drift==0`）以外でProceedしない。

### Phase 4-6 Execute / Verify / Proceed
- Execute: docs-only整合調整のみ。
- Verify: contract drift / responsibility boundary / pending queue gate / stop consistency を自己照合。
- Current decision: `Hold/Needs-decision`。
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

## Stream A serial gate lock（2026-05-10）

### A1 -> A2 -> A3 dependency lock
- 固定依存順: `A1(Contract Freeze) -> A2(Implementation Planning) -> A3(Operations Sync)`。
- ルール: `a1Status!="Done"` の間、A2/A3 は `Open/In Progress` 判定を生成しない（準備メモのみ許可）。

### AC/DoD gap closing
- AC-6: `A1 -> A2 -> A3` の順序違反が 0 件であること。
- AC-7: `Approval Record` 欠損時に `Proceed=Hold` を必須化すること。
- DoD-6: モック検証の許可範囲（型適合・監査イベント検証）と禁止範囲（状態確定・契約再定義）を明文化していること。

### Contract freeze snapshot（read-only）
- API signatures: `HIL_RS_DECISION_GATE_V1`, `HIL_RS_PATCH_PROPOSAL_V1`, `HIL_RS_APPLY_JUDGEMENT_V1`。
- Minimal types: `ApprovalRecordV1`, `GateStatusV1`, `DecisionQueueTransitionV1`。
- Audit events: `query|bundle|proposal|apply`。
- Current gate: `Hold/Needs-decision`（`Approval Record=Pending` のため）。
