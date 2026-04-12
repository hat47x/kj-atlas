# Issue Draft: HIL-RS-01 次フェーズ計画（Human-in-the-loop可逆統合）

- Type: Process
- Status: Open
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P1
- Owner: Plan Owner (Stream B)
- Scope: `01_Plans/issues/`（planning only）
- Dependencies: `ADR-0026`, `ADR-0027`, `ADR-0028`
- Related ADR/Spec: `ADR-0026`, `ADR-0027`, `ADR-0001`, `00_Prompt/domain.md`
- Expected verification level: `docs-check`

## 1) Goal

HIL-RS-01 を **Plan契約の単一正本（issue群）** として再整理し、A1/A2/A3 依存を「実装待ち」ではなく **状態遷移契約** で管理する。

## 2) Mock Contract Snapshot（Interface固定識別子のみ参照）

- Snapshot ID: `MOCK-CONTRACT-SNAPSHOT-HIL-RS-v1`
- Freeze Pack ID: `HIL-RS-02-A1-CONTRACT-FREEZE-v1`
- Fixed Contract IDs:
  - `A1-CRITIQUE-IF`
  - `A1-REDIFF-IF`
  - `A1-ATTR-IF`
  - `A1-ERROR-IF`
- Fixed values:
  - `schemaVersion=1.0.0`
  - `overridePolicy=human_dual_control_only`
  - `contractLinkLocked=true`
  - `sharedResourceFreeze=true`

## 3) ADR CDC（Phase 2）

- Context:
  - 本issueは `ADR-0026/0027/0028` の下位計画であり、Stream B は architecture/documentation 実体編集を行わない。
- Decision:
  - A1/A2/A3 の依存は `state-transition contract` として固定し、実装完了待ちを着手条件にしない。
- Consequences:
  - 不一致はA1へ差し戻す。A2/A3は契約再定義を行わない。

## 4) State Transition Contract（依存切断）

- Allowed:
  - `A1: Draft -> Open -> In Progress -> Done`
  - `A2/A3: Draft -> Open` は `A1==Done && pendingDecisionQueueCount==0` のときのみ
  - `DecisionQueue: Pending -> Approved | Rejected`
- Forbidden:
  - Pending bypass
  - `A1!=Done` での `A2/A3 Draft -> Open`
  - A2/A3 側での契約ID再定義

## 5) Acceptance Criteria / DoD

- [x] CDC（Context/Decision/Consequences）が明文化されている。
- [x] 依存が状態遷移契約で記述されている。
- [x] Mock Contract Snapshot の固定識別子のみを参照している。
- [x] SafeMode既定ON / share-export漏えい防止 / `human_dual_control_only` 後退禁止が明示されている。
- [x] Proceed条件（Open化条件と停止条件）が明文化されている。

## 6) Serial Phases（Plan -> Execute -> Verify -> Proceed）

### Phase 1 Read
- 対象5 issueを再Readし、Status/Scope/Dependencies/Contract IDs を再確認する。

### Phase 2 ADR CDC
- CDCを再確認し、上位ADR改定が必要なら停止（承認待ち）する。

### Phase 3 Plan
- AC/DoDと状態遷移契約の不足を補完する。

### Phase 4 Execute
- issue本文のみ同期し、依存契約・禁止遷移・差し戻し先を更新する。

### Phase 5 Verify
- `validate_active_issue_memos.py` + `rg` で整合確認。失敗時は自己修復最大3回。

### Phase 6 Proceed
- Open化条件を満たすものだけを次アクションへ進め、未確定はDecision Queueへ戻す。

## 7) Open化条件（Proceed Gate）

1. `A1==Done`
2. `pendingDecisionQueueCount==0`
3. 固定識別子（Freeze Pack/Contract IDs/schemaVersion/overridePolicy）が一致
4. 安全境界後退要求が存在しない

## 8) Fail-safe

- 停止条件:
  1. Verify失敗が3回超過
  2. 未承認決定の確定化
  3. 固定識別子の不一致
- 停止時記録:
  - 失敗条件 / 対象issue / 必要承認者 / Yes-No確認事項

## 9) Stream F update (2026-04-12, planning memo only)

### Phase 1) Read同期
- Re-read fixed scope memos: `issue-HIL-RS-01-next-phase-human-loop-reversible-synthesis.md`, `issue-HIL-RS-02-next-phase-delivery-plan.md`, `issue-HIL-RS-02-A1-governance-contract-hardening.md`, `issue-HIL-RS-02-A2-frontend-reversible-synthesis-application.md`, `issue-HIL-RS-02-A3-operations-documentation-sync.md`.
- Verified lock values remain unchanged: `schemaVersion=1.0.0`, `overridePolicy=human_dual_control_only`, `contractLinkLocked=true`, `sharedResourceFreeze=true`.

### Phase 2) A1/A2/A3依存 + Decision Queue更新
| QueueID | Topic | Status | Gate | Owner |
| --- | --- | --- | --- | --- |
| `DQ-HIL-RS-01-001` | A1 freeze pack consistency (`HIL-RS-02-A1-CONTRACT-FREEZE-v1`) | Closed | `A1==Done` | Stream F |
| `DQ-HIL-RS-01-002` | A2/A3 open precondition (`pendingDecisionQueueCount==0`) | Closed | `Pending -> Approved/Rejected` only | Stream F |
| `DQ-HIL-RS-01-003` | Safety boundary downgrade request handling | Closed | downgrade request = `Rejected` | Stream F |

### Phase 3) AC/DoD不足補完
- Added explicit NoGo condition: if `A1!=Done` **or** unresolved queue exists, A2/A3 must remain `Draft` or `Open (hold)` and cannot move to active execution.
- Added explicit rollback target: any contract drift must be routed back to A1 memo, not patched in A2/A3.
- Reconfirmed unique unlock invariant: `unlockAllowed := (A1==Done && pendingDecisionQueueCount==0)`.
- Reconfirmed forbidden path: no transition may treat `Pending` as implicitly resolved.

### Phase 4) docs-check
- Validation command is fixed to: `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`.
- If validation fails, self-correction loop max is 3; after that, stop and escalate with queue status snapshot.

### Phase 5) 次レーンhandoff
- Next lane package must include: `Snapshot ID`, `Freeze Pack ID`, queue table, and explicit Go/NoGo result.
- Handoff rule: A2/A3 lanes receive reference-only contract payload; contract value edits are prohibited.

## Stream A Critical Path Fixpoint (2026-04-12)

### Phase 1: Read（最新再読 + 未確定抽出）
- 未確定I/F: `なし`（固定対象は `CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05` / `A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|A1-ERROR-IF`）。
- 未確定責務: `なし`（A1は契約凍結の唯一正本、A2/A3はread-only参照）。
- 未確定ゲート: `なし`（唯一ゲートは `A1 Done && pendingDecisionQueueCount==0`）。

### Phase 2: ADR明文化（Context / Decision / Consequences）
- Context: 契約・統治のクリティカルパスを実装依存から切り離し、docs-checkで閉じる。
- Decision: 本メモの契約ID・凍結値・停止条件を正本として再定義禁止に固定する。
- Consequences: 差分要求はA1へ差し戻し、下流は参照専用で運用する。
- 合意記録: `DecisionStatus=Fixed` を承認済み契約として継続（本メモ内合意）。

### Phase 3: Plan（AC/DoD補強）
- AC補強: Contract ID collision=0 / 語彙collision=0 / SafeMode後退=0 を同時成立。
- DoD補強: `Plan -> Execute -> Verify -> Proceed` の順序証跡を本メモに残す。

### Phase 4: Execute（契約ID・判定条件・停止条件固定）
- 契約ID固定: `CE0-CTX-IF`, `CE0-SAFEMODE-IF`, `CE0-REVIEW-IF`, `CG-01..05`, `HIL-RS-02-A1-CONTRACT-FREEZE-v1`, `A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|A1-ERROR-IF`。
- 判定条件固定: `Go = (A1 Done && pendingDecisionQueueCount==0 && schemaVersion==1.0.0 && overridePolicy==human_dual_control_only && contractLinkLocked==true && sharedResourceFreeze==true)`。
- 停止条件固定: Query Preview bypass / direct write / auto-apply / review自動昇格 / SafeMode後退 / Self-Correction 3回超過。

### Phase 5: Verify -> Proceed
- Verify: docs-checkで契約ID整合・語彙整合・安全後退0件を確認し、不一致時はSelf-Correction最大3回まで。
- Proceed条件（1行）: `Proceed = (collision==0 && vocabularyDrift==0 && safeModeRegression==0 && A1 Done && pendingDecisionQueueCount==0)`。

### Fail-safe（停止報告テンプレ）
- 失敗条件:
- 影響範囲（ファイル/契約ID）:
- 人間判断が必要な選択肢（2案）:
  - 案1: 契約固定値を維持し、差分要求をA1へ差し戻す。
  - 案2: 契約固定値の変更を承認会議へエスカレーションし、承認後に再凍結する。

## Stream C Normalization Update (2026-04-12)

### Scope Contract（本ストリームの独立性）
- Stream C は **HIL-RS計画系issueの整流化のみ** を担当し、実装完了待ちでA1をブロックしない。
- 本ストリームで行うのは次の2点のみ。
  1. ゲート条件明文化（`A1 Done && pendingDecisionQueueCount==0`）
  2. 差戻し導線固定（契約差分は常にA1へ戻す）
- A1を「外部完了待ち」状態へ遷移させる記述は禁止。

### Phase Execution Record（1〜6）
1. **Phase 1 Read**: 対象3ファイルを再読し、固定識別子・依存・禁止遷移を再確認。
2. **Phase 2 ADR明文化（CDC）**: 既存CDCを再確認し、上位ADR改定不要を確認（issue内CDCを継続採用）。
3. **Phase 3 Plan**: AC/DoD不足として「A1外部待ち禁止」「差戻し先A1固定」を追記。
4. **Phase 4 Execute**: 状態遷移契約を `A1 Done && pendingDecisionQueueCount==0` に一本化。
5. **Phase 5 Verify**: docs-check + 差分検証を実施。失敗時は自己修復最大3回、4回目相当で停止。
6. **Phase 6 Proceed**: Go/NoGoを上記ゲート式で判定し、曖昧点は質問化して停止。

### State Transition Clarification（契約明確化）
- **Go**: `A1 Done && pendingDecisionQueueCount==0`
- **NoGo**: `A1!=Done` または `pendingDecisionQueueCount>0`
- **Rollback route**: 契約不一致・語彙ドリフト・安全境界後退の要求は **A1 issueへ差戻し**。

### Failure-stop Rule（3回超停止）
- Verify失敗の自己修復は最大3回。
- 3回超過時は作業停止し、未確定点を Yes/No 質問に分解して記録する。
