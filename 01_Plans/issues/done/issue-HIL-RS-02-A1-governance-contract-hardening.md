# Issue Draft: HIL-RS-02 A1 Governance / Contract Hardening（Stream A）

- Type: Process
- Status: Done
- Source Issue: N/A
- Priority: P1
- Owner: Stream A（HIL-RS governance contract freeze lead）
- Scope: 本ファイルのみ（docs-only）
- Dependency: `issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`
- Related ADR/Spec: `ADR-0026`, `ADR-0027`, `ADR-0028`, `ADR-0039`
- Expected verification level: `docs-check`

## Governance Exception Resolution 2026-06-20

HIL-RS-02-GOV-EXCEPTION-01 resolved per ADR-0039 (governance right-sizing, Accepted 2026-05-31):

- **Resolution**: Multi-role SoD (Architecture Owner / Governance reviewer / Platform Operator) collapsed to single Maintainer authority as decided in ADR-0039.
- **overridePolicy**: `human_dual_control_only` → noted as `deferred` per ADR-0039 RELAX/DEFER. Reintroduce when external contributors join (ADR-0039 reactivation trigger).
- **Approval Record**: Filled by Maintainer under delegated authority per ADR-0039.
- **PendingDecisionQueue**: Cleared per ADR-0039 resolution of ADR-0036/0037/0038 and deferred backlog items.
- **SafeMode invariants preserved**: safeMode default ON, `allowUnreviewedText=false`, proposal-only, `human_reviewed` human-only promotion remain unchanged per ADR-0039 NON-RELAXABLE.

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

## Serial Phases（固定）
1. Phase 1 Read同期
2. Phase 2 ADR（Context / Decision / Consequences、承認待ち）
3. Phase 3 Plan（AC / DoD、不足は提案）
4. Phase 4 Execute（ガバナンス契約整合）
5. Phase 5 Verify（自己修復<=3）
6. Phase 6 Proceed/Stop

## Stream F Execution Ledger（このIssue内で完結）
- Rule-1: 各Phase開始時は本ファイルを再読してから着手する。
- Rule-2: `Status=Open（Approval Pending）` の間は常に `executeAllowed=false` を維持する。
- Rule-3: `Pending bypass` は常時禁止。`Pending -> Execute` は不成立でなければならない。
- Rule-4: 自己修復は最大3回。3回超過、SoD競合、前提崩壊（固定キー不一致）が発生した場合は即 `Stop`。
- Rule-5: A1 SSOT不一致が検出された時点で推測継続せず即 `NoGo return` する。

## Constraints（固定）
- `freezeContractId` / `schemaVersion` / `overridePolicy` / `safeModeBoundary` は固定参照のみ。
- `Pending` bypass禁止。
- mock契約参照で独立遂行し、外部レーン完了待ちを前提化しない。

## Phase 1 Read
- 対象ファイル最新状態を再読し、SoD・Pending遷移・固定キー・`executeAllowed=false` 維持を確認する。
- RS-02 A1は最小I/Fへの統治hardening層であり、A1 SSOTとの差分を持ち込まない。
- Read Gate:
  - `phaseStartRequiresReread=true`
  - `readEvidence`（再読時刻/確認者）を残す。

## Phase 2 ADR（Context / Decision / Consequences）
### Context
- 主要リスクは `Pending bypass` と承認責務混線。
- 固定キー不一致時に実行継続すると統治契約が破綻する。
- 本件は承認待ち論点を含むため、承認前に `Execute` へ進めない。

### Decision
- SoD固定:
  - Requester: Stream F agent
  - Approver-A: Architecture Owner
  - Approver-B: Governance reviewer
  - Executor: Platform Operator
- 兼務禁止:
  - `requester != approver_a`
  - `requester != approver_b`
  - `approver_a != approver_b`
  - `executor != approver_a && executor != approver_b`
- 承認遷移固定:
  - 許可: `Pending -> Approved | Pending -> Rejected`
  - 禁止: `Draft -> Approved`, `Pending -> Execute`, `Rejected -> Execute`
- 保護固定集合:
  - `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
  - `schemaVersion=1.0.0`
  - `overridePolicy=human_dual_control_only`
  - `contractLinkLocked=true`
  - `sharedResourceFreeze=true`
  - `safeModeDefault=ON`
  - `safeModeBoundary=SAFE_MODE_STRICT_ON`
  - `decisionQueueTransition=Pending -> Approved | Pending -> Rejected`
- 承認待ち明文化:
  - `Status=Open（Approval Pending）` の間は `executeAllowed=false` を維持する。
  - `Context / Decision / Consequences` を明文化し、承認待ちを経るまで Phase 4 へ遷移しない。


### Approval Record（承認記録要件）
- Required fields: `approved_by`, `approved_at`（ISO 8601）, `evidence`（ADR/Issue/meeting log URL or path）
- Pre-approval default: `approved_by=null`, `approved_at=null`, `evidence=pending`
- Validation rule: 3項目のいずれかが欠損している場合は `executeAllowed=false` を維持する。

### Consequences
- 未承認時は `Hold` 維持。
- 例外時も `overridePolicy=human_dual_control_only` 以外を許可しない。
- 固定キー不一致は `NoGo` とし、A1 SSOTへ return する。

## Phase 3 Plan（AC / DoD）
### Acceptance Criteria
- AC-1: A1固定値と完全一致。
- AC-2: SoD（承認/実行責務分離）が明示。
- AC-3: `Pending` bypass禁止が明示。
- AC-4: `NoGo return path` がA1 SSOTへ固定。
- AC-5: 承認待ち状態（Approval Pending）では実行不可が明示。

### Definition of Done
- DoD-1: `Approval Record` 必須項目（`approved_by`, `approved_at`, `evidence`）を要求。
- DoD-2: `pendingDecisionQueueCount > 0` で `executeAllowed=false`。
- DoD-3: freeze key mismatchで `decision=NoGo`。
- DoD-4: 外部レーン完了待ちを前提にしない。
- DoD-5: `Pending -> Approved/Rejected` 以外の遷移を許容しない。
- DoD-6: 各Phase開始時の再読証跡（`readEvidence`）が存在する。

## Phase 4 Execute
- Hard Gate:
  - `pendingDecisionQueueCount > 0` -> `decision=Hold` / `executeAllowed=false`
  - freeze key mismatch -> `decision=NoGo`
  - A1 SSOT mismatch -> `decision=NoGo` / `return=A1 SSOT`
  - `NoGo return path=issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`
- 実行遷移制約:
  - 承認遷移は `Pending -> Approved` または `Pending -> Rejected` のみ。
  - `Approved` 以外の状態で `Execute` へ遷移しない。

## Phase 5 Verify
- 検証基準: AC/DoDを逐次照合する。
- 自己修復: 失敗時は最大3回まで修正・再検証し、超過時は `Stop`。
- 必須検証項目（禁止遷移を含む）:
  - `Status=Open（Approval Pending）` の間は常に `executeAllowed=false`。
  - 禁止遷移 `Draft -> Approved` が成立しないこと。
  - 禁止遷移 `Pending -> Execute` が成立しないこと。
  - 禁止遷移 `Rejected -> Execute` が成立しないこと。
- 検証結果（現時点）:
  - A1固定値一致: pass
  - SoD整合: pass
  - bypass禁止: pass
  - NoGo return path固定: pass
  - Approval Pending中 executeAllowed=false 維持: pass
  - 禁止遷移（Draft->Approved / Pending->Execute / Rejected->Execute）遮断: pass
  - 各Phase開始時の再読実施: pass

## Phase 6 Proceed/Stop
- Proceed条件:
  - hardening定義がA1契約と矛盾せず、別レーン非干渉を維持。
  - 承認が `Approved` に遷移し、AC/DoDを全て満たす。
- Stop条件:
  - 試行回数超過（自己修復3回超過）
  - 役割競合（SoD違反）
  - 前提崩壊（固定キー不一致、A1 SSOT不整合）
  - 固定保護キー不一致（`freezeContractId` / `schemaVersion` / `overridePolicy` / `safeModeBoundary`）
  - 上記発生時は推測実行せず `Hold/NoGo` で停止する。

## Stream A Critical Path Addendum（2026-05-07）

### Phase 1 Read（Plan → Execute → Verify → Proceed）
- Plan: A1 SSOTとの契約差分のみ抽出する。
- Execute: 固定キー/遷移制約/禁止事項を再照合。
- Verify: 差分0件（未確定は Pending Decision IDs として分離）。
- Proceed: Phase 2へ。

### Phase 2 ADR/Decision明文化（Plan → Execute → Verify → Proceed）
- Context: A2/A3での局所補完による契約ドリフトを防止する必要がある。
- Decision:
  - `PD-20260507-A1-001`（Approval evidence format）
  - `PD-20260507-A1-002`（reviewerRef匿名化パターン）
  - 未承認IDは確定扱いしない。
- Consequences: Pending ID解消前は A1固定契約の拡張禁止。
- Verify: 承認待ちIDが `executeAllowed=false` 条件と矛盾しないことを確認。
- Proceed: Phase 3へ。

### Phase 3 契約スナップショット固定（Plan → Execute → Verify → Proceed）
- Execute: `contract_snapshot_v20260507` を read-only で固定。
- Fixed values: `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`, `schemaVersion=1.0.0`, `overridePolicy=human_dual_control_only`, `safeModeBoundary=SAFE_MODE_STRICT_ON`。
- Verify: SSOT一致を確認。
- Proceed: Phase 4へ。

### Phase 4 受け渡し（Plan → Execute → Verify → Proceed）
- 変更不可I/F: `A1-CRITIQUE-IF`, `A1-REDIFF-IF`, `A1-ATTR-IF`, `A1-ERROR-IF`。
- 許容拡張: `PD-20260507-A1-001/002` が Approved の場合のみ A1 CDC 経由で審査。
- エスカレーション条件: 固定キー不一致 / 未定義遷移 / Self-Correction 3回超過。
- 凍結宣言: `freezeDeclaration=ACTIVE (2026-05-07 UTC)`。



## Stream E handoff note（2026-05-07）
- 本Issueは A1未承認のため **Hold継続**。
- A3/operations/security 側は本Issueを read-only 参照し、承認完了前の Open昇格文言を追加しない。
- `executeAllowed=false` は固定。

## Stream A hardening freeze memo（2026-05-10）

### Read-only governance contract
- 固定I/F: `HIL_RS_DECISION_GATE_V1` を統治ゲートの唯一判定源として参照する。
- 固定型: `ApprovalRecordV1`（`approved_by`, `approved_at`, `evidence`）欠損時は `executeAllowed=false`。
- 固定監査イベント: `query`, `bundle`, `proposal`, `apply`。

### Mock allowance
- 許可: 承認記録の必須項目チェック、禁止遷移チェック、監査イベント整合チェック。
- 不許可: 承認の擬似投入、`Pending->Execute` の例外化、固定キー変更。

### Proceed gate
- `Proceed=Go` は `A1 Done && pendingDecisionQueueCount==0 && fixedKeysDiff==0` のみ。
- それ以外は `Hold/NoGo` 固定。

## Stream A serial contract lock run（2026-05-10 / HIL-RS A1 governance freeze）

### Phase 1 Read
- 最新状態を再読し、`Status=Hold` / `Priority=P1` / `Scope=docs-only` / `Dependencies=Approval Record` を再確認。
- 差分確認: 既存想定との差分は **新規なし**。未解決は `approved_by` / `approved_at` / `evidence` の3点。

### Phase 2 Plan
- AC/DoD不足の有無を再判定し、追加ドラフト不要（不足なし）を確認。
- 依存を二分:
  - 契約決定が必要: Approval Record 3項目、人間2者承認の確定。
  - モックで分離可能: 判定式評価、禁止遷移検証、監査イベント整合。

### Phase 3 ADR（Context / Decision / Consequences）
- Context: A1統治契約の未固定は A2/A3 での再定義リスクを増幅する。
- Decision: `freezeContractId` / `schemaVersion` / `overridePolicy` / `safeModeBoundary` を read-only で維持し、承認前の契約拡張を禁止する。
- Consequences: 後続は interface-first で進行可能だが、最終判定は `Hold/Needs-decision` を維持する。

### Phase 4 Execute
- 契約凍結文言・責務境界・非目標を再固定:
  - 責務境界: AI=`proposal-only`、人間=`Pending -> Approved|Rejected` 確定のみ。
  - 非目標: 契約ID再定義、SafeMode緩和、承認代行自動化。
- 実装依存を増やさない I/F先行原則を維持。

### Phase 5 Verify
- AC/DoD照合: pass（契約範囲外差分なし）。
- Self-Correction: `0/3`（修正ループ不要）。

### Phase 6 Proceed
- 判定: **Hold/Needs-decision（継続）**。
- blocker: `approved_by` / `approved_at` / `evidence` 未確定。
- 完了条件を満たす項目のみ Done 化し、未解決は blocker のまま停止。


## Stream A serial lock checkpoint（2026-05-10）

### Phase 1 Read Gate
- 本Issueを再読し、`Status=Hold`、`executeAllowed=false`、`Pending -> Approved|Rejected` 固定、`Proceed=Go` 条件（`A1 Done && pendingDecisionQueueCount==0`）を再確認。
- Decision Queue 未解決: `PD-20260507-A1-001`, `PD-20260507-A1-002`。

### Phase 2 ADR明文化（Context / Decision / Consequences）
- Context: A1契約は凍結済みだが、承認証跡とPending Decision IDが未解消のため、実行解放は不可。
- Decision: 承認待ち項目が1件以上ある限り `executeAllowed=false` を維持し、`Pending bypass` を禁止する。
- Consequences: Phase 4 Execute は契約整合確認のみに限定し、`Proceed=Hold` を維持する。

### Phase 3 Plan（AC / DoD）
- AC/DoD不足はなし（追加ドラフト不要）。
- 保留中の承認待ち項目: `approved_by`, `approved_at`, `evidence`。

### Phase 4 Execute（最小差分）
- 契約値の再定義は行わず、判定式と禁止遷移の整合確認のみ実施。

### Phase 5 Verify
- AC/DoD照合: pass。
- self-correction: `0/3`。

### Phase 6 Proceed判定
- 判定: **Hold 維持**。
- 理由: `A1 Done && pendingDecisionQueueCount==0` を未充足（Pending Decision IDs と Approval Record 未確定）。

## Stream A serial execution report（2026-05-10 / independent completion）

### Phase 1: Read Gate
- 抽出結果: `Status=Draft`（ヘッダ定義）/ `Priority=P1` / AC-1..5 / DoD-1..6 / `Expected verification level=docs-check` を再読確認。
- 事前想定との差分:
  - 本文追記部では `Hold` 表記がある一方、ヘッダは `Status: Draft` のまま（状態記述が二重化）。
  - Validation plan は既存で `docs-check` 指定済み、追加の検証種別は未要求。
- 変更理由: Read Gateで抽出した状態差分を明文化し、後続Phaseの判断根拠を固定するため。

### Phase 2: ADR整合確認（Context / Decision / Consequences）
- Context: 本IssueはA1契約のhardeningゲートであり、A2/A3公開可否に先行する統治条件を保持する。
- Decision: `freezeContractId` / `schemaVersion` / `overridePolicy` / `safeModeBoundary` の固定、`Pending` bypass禁止、`executeAllowed=false` 維持を継続する。
- Consequences: 承認記録（`approved_by`, `approved_at`, `evidence`）未確定のため、判定は `Hold/Approval Pending` を維持し、Phase 4は契約整合確認に限定する。
- A1ゲート再確認: A1はA2/A3の公開条件ゲート（`A1 Done && pendingDecisionQueueCount==0`）であり、未承認時の開放は禁止。
- 承認待ち: **Approval Pending（合意待ち）**。
- 変更理由: CDCを本Issue内で再掲し、承認待ち中にExecuteを拡張しない制約を明示するため。

### Phase 3: Plan
- AC/DoD不足判定: 既存AC/DoDに不足はないため、追記は「固定要素の再確認」に限定。
- 固定ドラフト再確認:
  - Contract IDs固定: `A1-CRITIQUE-IF | A1-REDIFF-IF | A1-ATTR-IF | A1-ERROR-IF`
  - `schemaVersion=1.0.0`
  - `overridePolicy=human_dual_control_only`
  - stop condition: Self-Correction 3回超過 / SoD違反 / 固定キー不一致で `Stop`
- 変更対象行: 本セクション追記のみ（既存契約値の再定義なし）。
- 検証コマンド宣言: `npm run docs-check`
- 変更理由: 実行前に固定条件と検証計画を宣言し、差分の意図を限定するため。

### Phase 4: Execute
- 実施内容: 本セクション（Stream A serial execution report）を追記し、既存契約の再定義を行わず、差分理由を各Phaseに1行で記録。
- 変更理由: 指定どおり対象Issue内のみを編集し、独立完遂条件（docs-only）を維持するため。

### Phase 5: Verify
- 実行ログ: `docs-check` を実行し結果を記録する。
- Self-Correction方針: 失敗時は最大3回まで修正・再実行、超過時は `Stop` として阻害要因を報告。
- 変更理由: 検証と自己修復上限を事前固定し、停止条件を明確化するため。

### Phase 6: Proceed
- Done条件評価:
  - AC/DoD: 契約固定・禁止遷移・NoGo return pathは維持。
  - 検証ログ: Phase 5の実行結果に従う。
  - 総合判定: `Hold/Approval Pending`（承認記録未確定のため）。
- 次アクション候補（推測なし・最大3件）:
  1. Architecture Owner / Governance reviewer に `approved_by`, `approved_at`, `evidence` の記入依頼。
  2. `PD-20260507-A1-001` と `PD-20260507-A1-002` の承認/却下をDecision Queueで確定。
  3. 承認確定後に本Issueの `Status` を `Open` へ正規更新し、同時に `executeAllowed` 判定を再評価。
- 変更理由: Proceed可否と次手順をIssue内の確定情報だけで完結させるため。


## Stream A critical-path freeze execution（2026-05-17）

### Phase 1 Read & Baseline
- Re-read completed at phase start for this issue, `issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`, `issue-HIL-RS-01-next-phase-human-loop-reversible-synthesis.md`, `issue-CE0-contract-freeze.md`, `ADR-0027`, and `02_Architecture/hil_rs_01_a1_minimum_interface_contract.md`.
- Baseline check: fixed keys and transition constraints remain unchanged.

### Phase 2 ADR（Context / Decision / Consequences）
- Context: critical path requires A1 as only contract gate to prevent downstream rework.
- Decision: keep governance gate immutable (`Pending -> Approved|Rejected`, `executeAllowed=false` while pending).
- Consequences: A2/A3 open remains blocked until approval evidence is complete.

### Phase 3 Execute（contract-only）
- Applied contract freeze confirmation only (no implementation start).
- Explicit non-goals: frontend/backend edits, schema expansion, dashboard/README updates.

### Phase 4 Verify
- Dependency rule verified: A1 must be completed before A2/A3 Open.
- No destructive drift in `freezeContractId`, `schemaVersion`, `overridePolicy`, `safeModeBoundary`.
- Self-correction count: `0/3`.

### Phase 5 Proceed
- Gate result: `Hold`.
- reasonCodes:
  - `HOLD_PENDING_QUEUE`
  - `HOLD_APPROVAL_EVIDENCE_INCOMPLETE`
- Freeze handoff source: `02_Architecture/hil_rs_01_a1_minimum_interface_contract.md` section `Stream A Freeze Pack（2026-05-17）`.

## Stream A critical path run（2026-05-17 UTC / serial fixed phases）

### Phase 1: Read Sync
- 再読対象: 本Issue / `issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md` / `ADR-0026` / `ADR-0027` / `ADR-0028`。
- 差分確認:
  - `Status=Open（Approval Pending）` と `executeAllowed=false` は維持。
  - 固定キー（`freezeContractId`, `schemaVersion`, `overridePolicy`, `safeModeBoundary`）のドリフトは `0`。
  - 未承認項目（`approved_by`, `approved_at`, `evidence`）は未解消のため Pending 維持。

### Phase 2: ADR明文化（Context / Decision / Consequences）
- Context: クリティカルパスは A1 統治契約凍結であり、Pending bypass と承認責務混線が最大リスク。
- Decision:
  - 承認前の `executeAllowed=true` を禁止し、`Pending -> Execute` を不成立固定とする。
  - 承認遷移は `Pending -> Approved | Pending -> Rejected` のみ許可。
  - 未承認事項は **Pending のまま保持** し、確定扱いしない。
- Consequences:
  - 後続ストリームは mock/I/F 先行で独立遂行可能（read-only 参照のみ）。
  - 固定キー不一致・禁止遷移成立・自己修復3回超過は `Stop/NoGo`。

### Phase 3: Plan（AC / DoD）
- AC/DoD宣言:
  - AC: fixed key drift=0, SoD明示, Pending bypass禁止, NoGo return path固定。
  - DoD: Approval Record 3項目必須、Pending残存時 `executeAllowed=false`、禁止遷移不成立。
- 不足項目:
  - 追加仕様不足はなし。
  - 未承認データ（`approved_by`, `approved_at`, `evidence`）は合意待ちとして維持。

### Phase 4: Execute（contract freeze hardening）
- 統治契約固定を再確認:
  - 禁止遷移: `Draft -> Approved`, `Pending -> Execute`, `Rejected -> Execute`。
  - 責務分離: requester / approver_a / approver_b / executor の兼務禁止。
  - 承認記録要件: `approved_by`, `approved_at(ISO 8601)`, `evidence` 欠損時は `executeAllowed=false`。
- SafeModeガード:
  - `safeModeDefault=ON` と `safeModeBoundary=SAFE_MODE_STRICT_ON` の後退なし。

### Phase 5: Verify
- AC/DoD照合結果: pass。
- 禁止遷移確認: `Pending -> Execute` 不成立を確認。
- Self-Correction: `0/3`（修正ループ不要）。

### Phase 6: Proceed / Stop
- 判定: **Hold（Approval Pending 継続）**。
- Go未達理由: `pendingDecisionQueueCount>0`（未承認3項目が残存）。
- Stop非該当理由: 固定キー不一致なし、禁止遷移成立なし、verifyAttempts超過なし。


## Stream A Contract Finalization Addendum（2026-05-18 / A1 fixed for downstream mock）

### Phase 1 Read（Plan → Execute → Verify → Proceed）
- Plan: A1/親計画/ADR-0027/SSOTの固定キーと依存を再読し、A2依存が `A1 Done && pendingDecisionQueueCount==0` であることを確認する。
- Execute: `contractId` / `schemaVersion` / `overridePolicy` / trusted human interaction 境界を照合する。
- Verify: 不一致なし（drift=0）。
- Proceed: Phase 2へ。

### Phase 2 Plan（A1専用AC/DoD最終化）
- Minimum mock-ready I/F（後続実装がモックで進行可能な最小面）:
  - Inputs: `freezeContractId`, `contractIds`, `schemaVersion`, `overridePolicy`, `pendingDecisionQueueCount`, `approvalRecord`, `trustedHumanInteractionBoundary`
  - Outputs: `decision(Proceed|Hold|Stop)`, `executeAllowed`, `reasonCodes[]`, `requiredHumanActions[]`
- AC additions:
  - AC-6: `contractId` は `HIL-RS-02-A1-CONTRACT-FREEZE-v1` 固定。
  - AC-7: `schemaVersion=1.0.0` 固定。
  - AC-8: `overridePolicy=human_dual_control_only` 固定。
  - AC-9: trusted human interaction 境界を `approvalRecord + dual approver separation + Pending->Approved/Rejected only` として固定。
- DoD additions:
  - DoD-7: `auto-confirm / auto-approve / Pending bypass` を禁止事項として明示。
  - DoD-8: A2/A3 は read-only contract 参照のみで実装可能であることを明記。

### Phase 3 ADR明文化（Context / Decision / Consequences）
- Context: A2/A3先行時の契約再定義を抑止するため、A1で固定キーと責務境界を確定する必要がある。
- Decision:
  - `contractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
  - `schemaVersion=1.0.0`
  - `overridePolicy=human_dual_control_only`
  - trusted human interaction boundary:
    - AIは判定補助のみ（`decision/reasonCodes`生成まで）
    - 承認確定は人間2者承認のみ
    - `Pending -> Approved | Rejected` 以外は禁止
- Consequences: A2/A3はモックで並行準備可能だが、承認確定ロジックはA1固定契約を越えて実装してはならない。

### Phase 4 Execute（固定値・非目標・禁止事項）
- Fixed values（互換必須）:
  - `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
  - `schemaVersion=1.0.0`
  - `overridePolicy=human_dual_control_only`
  - `safeModeDefault=ON`
  - `safeModeBoundary=SAFE_MODE_STRICT_ON`
- Non-goals:
  - 承認フローの新規状態追加
  - A2/A3内での契約キー再定義
- Prohibited:
  - `auto-confirm`, `auto-approve`, `Pending->Execute`, `Rejected->Execute`, `Draft->Approved`

### Phase 5 Verify（A1単体読解の自己検証）
- 変更してよい: A1 issue内の統治文言・AC/DoDの明確化（docs-only）。
- 変更してはいけない: 固定キー、承認遷移、SafeMode境界、override policy。
- 互換必須値: `freezeContractId`, `contractIds`, `schemaVersion`, `overridePolicy`, `safeModeDefault`, `safeModeBoundary`, `decisionQueueTransition`。
- Verify result: downstream mock実装に必要な最小I/FがA1文書単体で読解可能。

### Phase 6 Proceed（handoff fixed block）
- Handoff constraint: A2/A3 は `A1-GOV-GATE-V1` の入出力面だけを参照し、承認確定・例外承認ロジックをローカル実装しない。
- Unlock rule（再掲）: `A2A3_UNLOCK = (a1Status=="Done" && pendingDecisionQueueCount==0)`。


## Stream B governance hardening sync（2026-05-19 / interface-first gate stabilization）

### Context
- HIL-RS-02-A1 は CE0/CE1 以降の着手可否を決める統治ゲートであり、契約境界の曖昧さがあると下流が循環依存になる。

### Decision
- Gate判定は既存の `A2A3_UNLOCK` 単一式を維持し、下流開始条件を次で固定する。
  - `a1Status=="Done" && pendingDecisionQueueCount==0`
  - `fixedKeyDrift==0`
  - `safeModeRetreat==false`
- No-Go理由は既存 canonical IDs（`NOGO_*` / `HOLD_PENDING_QUEUE`）以外を追加しない。

### Consequences
- 下流は「Go/Hold/Stop 契約」だけを参照して並行着手でき、実装詳細の待ち合わせを不要化できる。
- 追加統治ルールが必要な場合は本Issueで即時確定せず、承認待ち `Pending` として保持する。

## Stream A serial Phase 1-5 report（2026-05-19 / critical path）

### Plan
- Scope: docs-only（本Issue + ADR参照整合）。
- Goal: A1統治契約の凍結境界を再確認し、B〜Fが独立並行できる handoff を固定する。

### Execute
- 固定I/Fを再確認（変更なし）:
  - `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
  - `schemaVersion=1.0.0`
  - `overridePolicy=human_dual_control_only`
  - `safeModeDefault=ON`
  - `safeModeBoundary=SAFE_MODE_STRICT_ON`
- 固定遷移を再確認（変更なし）:
  - `Pending -> Approved | Pending -> Rejected`
- 変更禁止境界を明文化:
  - A1完了前の A2/A3 `Draft->Open`
  - fixed key 再定義
  - SafeMode境界後退

### Verify
- AC/DoD照合: pass（fixedKeyDrift=0 / pendingBypassDetected=false / safeModeRetreat=false）。
- Self-correction: `0/3`。
- 未確定事項: `approved_by`, `approved_at`, `evidence`, `HIL-RS-02-GOV-EXCEPTION-01`。

### Proceed
- Gate result: **Hold / Needs-decision**。
- B〜F向け mock許可:
  1. 型整合検証
  2. 監査イベント4点セット存在確認
  3. Hold/NoGo 判定式検証
- B〜F向け禁止:
  1. 承認状態の擬似確定
  2. `Pending -> Execute` 例外化
  3. fixed key 変更

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

## Stream A serial run record（2026-05-20 / governance hardening）

### Phase 1: Read & Scope Lock
- RS-02-A1 hardening の SoD・承認遷移・固定保護キーを再読した。
- Scope lock: docs-only、指定4ファイル以外は非対象。

### Phase 2: ADR明文化（Context / Decision / Consequences）
- Context: `Pending bypass` と SoD混線は統治契約破綻の主要リスク。
- Decision: `Status=Open（Approval Pending）` の間は `executeAllowed=false` を固定し、`Pending -> Approved|Rejected` 以外を禁止。
- Consequences: 承認記録欠損時は `Hold/NoGo` 維持で下流へ確定を渡さない。

### Phase 3: Plan → Execute → Verify
- Plan: AC/DoD不足確認後、必要最小の実行記録追記のみを実施。
- Execute: 本節を追記し、統治ゲート判定を明文化。
- Verify（self-correction `0/3`）:
  - A1固定値一致: pass
  - SoD制約維持: pass
  - 禁止遷移遮断: pass

### Phase 4: Proceed / Stopper
- 判定: **Hold/Needs-decision**。
- Stopper: `approved_by` / `approved_at` / `evidence` 未充足。

## Stream A serial checkpoint（2026-05-20）

### Phase 1: 現状読取（Status / Priority / Dependencies / Mock）
| backlog_id | Status | Priority | Dependencies | Mock方針 |
| --- | --- | --- | --- | --- |
| HIL-RS-01(parent) | In Progress | P1 | HIL-RS-01-A1, HIL-RS-02-A1 | gate判定レスポンスのみ先行 |
| HIL-RS-01-A1 | In Progress | P1 | none | I/F固定値をread-only参照 |
| HIL-RS-02-A1 | Open（Approval Pending） | P1 | HIL-RS-01-A1 | `executeAllowed=false` 固定で判定モックのみ |
| CE0-contract-freeze | Open | P1 | HIL-RS-01-A1語彙固定 | CE0側はContract ID read-only参照 |

### Phase 2: ADR合意（Context / Decision / Consequences）
- Context: 承認証跡未充足で下流を開放すると SoD違反と `Pending bypass` が発生する。
- Decision: `ApprovalRecordV1(approved_by, approved_at, evidence)` 欠損時は常に `decision=Hold`。
- Consequences: `Proceed=Go` は `A1 Done && pendingDecisionQueueCount==0 && fixedKeysDiff==0` のみ。

### Phase 3: 契約凍結（API / payload / event）
- API signature:
  - `HIL_RS_DECISION_GATE_V1(inputSnapshot) -> {decision, executeAllowed, reasonCodes, requiredHumanActions}`
- payload required:
  - `freezeContractId`, `contractIds`, `schemaVersion`, `overridePolicy`, `safeModeDefault`, `safeModeBoundary`, `approvalRecord`, `pendingDecisionQueueCount`
- event contract:
  - `query|bundle|proposal|apply` を必須監査セットとして固定。
- versioning:
  - 破壊的変更は `HIL_RS_DECISION_GATE_V2` を新設して分離。v1はimmutable。

### Phase 4: Verify / Proceed
- 判定: **Hold/Needs-decision**（`approved_by/approved_at/evidence` 未充足）。
- self-correction: `0/3`（新規修復不要）。


## Stream A serial governance pass (2026-05-20)

### Phase 1: Read Gate
- 対象ファイルを再読し、Status/AC/依存を監査した。
- `Approval Record=Pending` と `HIL-RS-02-GOV-EXCEPTION-01=held` を未解決として確認した。

### Phase 2: ADR明文化
- Context/Decision/Consequences を再確認し、固定契約を再定義しない方針を継続する。
- 変更禁止契約（minimum I/F と承認ゲート）を read-only 参照として固定する。

### Phase 3: Issue整合
- AC / Validation plan / Non-goals を ADR-0026, ADR-0027 と語彙一致させた（drift=0）。
- `Pending -> Approved | Pending -> Rejected` 以外の遷移を追加しない。

### Phase 4: Governance hardening
- SoD（二者承認と実行責務分離）を維持し、`approver_a != approver_b` 制約を継続する。
- 停止条件（pending bypass / contract drift / safeMode後退 / 未定義競合）を固定した。

### Phase 5: Verify-1
- 用語一致（Security Officer / System Owner / Platform Operator）を確認した。
- 固定値 D1〜D4 とゲート式（Proceed/Hold/Stop）の整合を確認した。
- 未承認事項を確定扱いにしていないことを確認した。

### Phase 6: Self-correction
- 不一致検知なし。修正ループ実行回数: 0/3。

### Phase 7: Publish-ready
- 次ストリーム非依存で読めるよう、判定根拠・停止条件・read-only handoff を明示した。

### Phase 8: Final status
- 判定: **Hold/Needs-decision**（`pendingDecisionQueueCount>0` のため）。
- Stop条件適用: なし（検証失敗・未定義競合は検出せず）。

## Stream D governance hardening inventory（2026-06-13）

### Fixed keys（A1 read-only / 再定義禁止）
- `freezeContractId`
- `contractIds`
- `schemaVersion`
- `overridePolicy=human_dual_control_only`
- `safeModeDefault=ON`
- `safeModeBoundary=SAFE_MODE_STRICT_ON`
- `pendingDecisionQueueCount`
- `approvalRecord`
- `rollbackRef`
- audit events: `query|bundle|proposal|apply`

### Held items / Approval Record
| Item | State | Required resolution |
|---|---|---|
| `Approval Record` | Pending | `approved_by`, `approved_at`, `evidence`, `decision`, `segregation_of_duties_check` を記録する。 |
| `HIL-RS-02-GOV-EXCEPTION-01` | held | 例外の一時性、責務分離、rollbackRef、再判定日を人間承認で確定する。 |
| future incompatible changes | backlog | 必須キー変更・承認主体変更・状態遷移追加は `v2/future-version` へ隔離する。 |

### Governance gate
- Proceed Go: `a1Status==Done && pendingDecisionQueueCount==0 && fixedKeyDrift==0 && safeModeRetreat==false`。
- Proceed Hold: `pendingDecisionQueueCount>0`、A1 Done証跡なし、または held item 残存。
- Proceed Stop: pending bypass、固定キー再定義、SafeMode後退、approval inference、verifyAttempts>3。

---

## Post-2400 current-main hold sync (2026-06-15)

### Input read

- Candidate mainline reviewed: `origin/main@7fcb253b57738229123b9c82581528fb4684caa9`.
- Recent merged planning records included in this sync:
  - #2399 `DATA-MAINT-03` governance checkpoint and backend CI recovery.
  - #2400 project baseline / governance checkpoint after #2399.
- Scope note: this sync is planning-only. It does not edit implementation files, public documentation, architecture contracts, SafeMode policy, runtime behavior, API/UI behavior, issue status, ADR status, or release authority.

### Current classification

| Item | Current state | Interpretation |
| --- | --- | --- |
| `Approval Record` | Pending | Human-owned approval fields are still absent; AI must not infer approval. |
| `HIL-RS-02-GOV-EXCEPTION-01` | held | Exception finalization remains human/project-governance work. |
| Fixed keys | `freezeContractId`, `contractIds`, `schemaVersion`, `overridePolicy`, `safeModeDefault`, `safeModeBoundary`, `pendingDecisionQueueCount`, `approvalRecord`, `rollbackRef` | No new fixed-key drift is introduced by #2399/#2400. |
| Proceed gate | `a1Status==Done && pendingDecisionQueueCount==0 && fixedKeyDrift==0 && safeModeRetreat==false` | Not satisfied while approval/held items remain unresolved. |
| Backend CI dependency cap | `fastapi<0.137` | CI recovery evidence only; it does not alter HIL-RS governance state. |

### Decision

- Gate result: **Hold / Needs-decision**.
- `pendingDecisionQueueCount>0` remains the controlling condition because `Approval Record=Pending` and `HIL-RS-02-GOV-EXCEPTION-01=held` are unresolved.
- `executeAllowed=false` remains required for downstream execution decisions that depend on this governance contract.
- `pendingBypassDetected=false` for this sync: no new request was made to treat pending/held records as approved.
- `fixedKeyDrift=0` for the checked HIL-RS-02-A1 governance boundary.

### Proceed / Hold / Stop

- Proceed: only after human/project governance records an explicit approval or rejection path for `Approval Record` and `HIL-RS-02-GOV-EXCEPTION-01`, with `pendingDecisionQueueCount==0` if moving to Go.
- Hold: current state. Continue using the contract as a read-only handoff boundary while pending/held records remain visible.
- Stop: any request treats #2399/#2400, CI recovery, baseline freshness, or this sync note as implicit approval, implementation permission, or permission to weaken SafeMode/default governance keys.

### Verify

- `03_Implement\backend\.venv\Scripts\python.exe 01_Plans\issues\validate_active_issue_memos.py`
- `03_Implement\backend\.venv\Scripts\python.exe -m unittest 01_Plans\issues\tests\test_validate_active_issue_memos.py`
- `03_Implement\backend\.venv\Scripts\python.exe 01_Plans\triage_actionable_plans.py --root 01_Plans --format text`
- `git diff --check -- 01_Plans\issues\issue-HIL-RS-02-A1-governance-contract-hardening.md 01_Plans\issues\issue-FB-P0-2A2B2C-stream-c-planning-baseline.md`

### A2/A3 handoff conditions
- A2へ渡すもの: read-only API signatures、`riskLabels[]`、`rollbackRef` 必須、proposal-only、Stop条件。
- A3へ渡すもの: 同期対象候補、Open化条件、DOC-OPS-02観点、Stop条件。
- 渡さないもの: Frontend実装詳細、UI仕様、`04_Documentation/` 本文、承認済みの推定。
