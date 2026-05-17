# Issue Draft: HIL-RS-02 A1 Governance / Contract Hardening（Stream A）

- Type: Process
- Status: Open
- Lifecycle: Draft -> Hold -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P1
- Owner: Stream A（HIL-RS governance contract freeze lead）
- Scope: 本ファイルのみ（docs-only）
- Dependency: `issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`
- Related ADR/Spec: `ADR-0026`, `ADR-0027`, `ADR-0028`
- Expected verification level: `docs-check`

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
