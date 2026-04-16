# Issue Draft: HIL-RS-01 A1 Architecture最小I/F契約固定

- Type: Process
- Status: Open
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P1
- Owner: Architecture Owner (Stream A contracts)
- Scope: `01_Plans/issues/`（planning only）
- Dependencies: `ADR-0026`, `ADR-0027`, `ADR-0028`
- Related ADR/Spec: `ADR-0026`, `ADR-0027`
- Expected verification level: `docs-check`

## 1) Objective

A1を「実装タスク」ではなく、A2/A3を制御する **最小I/F契約の状態遷移ゲート** として固定する。

## 2) Mock Contract Snapshot（固定識別子）

- Snapshot ID: `MOCK-CONTRACT-SNAPSHOT-HIL-RS-v1`
- `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
- `contractIds=A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|A1-ERROR-IF`
- `schemaVersion=1.0.0`
- `overridePolicy=human_dual_control_only`
- `contractLinkLocked=true`
- `sharedResourceFreeze=true`

## 3) ADR CDC（Phase 2）

- Context:
  - A1はHIL-RS全体の契約基準点であり、ここが曖昧だとA2/A3のOpen判定が不安定になる。
- Decision:
  - Stream AはA1の **契約識別子と遷移条件のみ** を計画文で固定し、設計実体の編集は行わない。
- Consequences:
  - 契約変更要求はA1に集約し、A2/A3はread-only参照に限定される。

## 4) State Transition Contract

- Unlock rule（唯一）:
  - `a2a3Unlock = (a1Status=="Done" && pendingDecisionQueueCount==0)`
- Decision Queue:
  - `Pending -> Approved` または `Pending -> Rejected`
- Prohibited:
  - `Pending` bypass
  - `a1Status!="Done"` での `A2/A3 Draft -> Open`
  - A2/A3 issue内での固定識別子再定義

## 5) Acceptance Criteria / DoD

- [x] CDCが明文化されている。
- [x] Unlock ruleが一意である。
- [x] 固定識別子がMock snapshotとして明示されている。
- [x] 安全境界後退禁止が明示されている。
- [x] Verify失敗時の3回上限と停止条件が明示されている。

## 6) Serial Phases（各Phase開始時に再Read）

1. Read: 対象4 issue（CE0 Contract Freeze / CE0 Core Graph / HIL-RS-01 A1 / HIL-RS-02 A1）再Read、差分抽出。
2. ADR CDC: Context/Decision/Consequences再確認。
3. Plan: AC/DoD・遷移契約不足を補完。
4. Execute: issue本文のみ更新（契約識別子/遷移/禁止事項）。
5. Verify: validator + rg、自己修復は最大3回。
6. Proceed: Open化可能項目のみ進行、残件はDecision Queueへ戻す。

## 7) Open化条件

- `a1Status=="Done"`
- `pendingDecisionQueueCount == 0`
- Fixed identifiers 完全一致
- 安全境界後退要求なし
- Go/No-Go判定式（固定）:
  - `Go = (a1Status=="Done" && pendingDecisionQueueCount==0 && schemaVersion=="1.0.0" && overridePolicy=="human_dual_control_only" && contractLinkLocked==true && sharedResourceFreeze==true)`
  - `NoGo = !Go`

## 8) Fail-safe

- 3回修復超過 / 未承認決定確定化 / 固定識別子不一致で停止。

## 9) Prohibited Transitions / Stop Conditions（凍結）

- `Pending -> Open` を `Approved/Rejected` を経ずに通過させる遷移は禁止。
- `a1Status != Done` での `A2/A3 Draft -> Open` は禁止。
- `schemaVersion != 1.0.0` / `overridePolicy != human_dual_control_only` / freeze flags不一致は即停止。
- Self-Correction は最大3回。4回目は実行禁止（停止報告へ移行）。

停止報告テンプレ（必須）:
1. 失敗条件
2. 影響契約ID
3. 必要な人間判断

## 10) Downstream Handoff（固定値一覧 / 変更禁止）

- `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
- `contractIds=A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|A1-ERROR-IF`
- `schemaVersion=1.0.0`
- `overridePolicy=human_dual_control_only`
- `contractLinkLocked=true`
- `sharedResourceFreeze=true`

> 下流レーンは上記固定値を参照のみ可。変更要求はA1へ差し戻す。

## Stream A Critical Path Fixpoint (2026-04-12)

### Phase 1: Read（最新再読 + 未確定抽出）
- 未確定I/F: `なし`（固定対象は `CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05` / `A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|A1-ERROR-IF`）。
- 未確定責務: `なし`（A1は契約凍結の唯一正本、A2/A3はread-only参照）。
- 未確定ゲート: `なし`（唯一ゲートは `a1Status=="Done" && pendingDecisionQueueCount==0`）。
- 事前想定との差分（箇条書き）:
  - Decision文の担当Stream表記が混在していたため、Stream A専任運用に統一した。
  - 禁止遷移の条件文を `a1Status!="Done"` に固定し、判定式との乖離を解消した。

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
- 判定条件固定: `Go = (a1Status=="Done" && pendingDecisionQueueCount==0 && schemaVersion==1.0.0 && overridePolicy==human_dual_control_only && contractLinkLocked==true && sharedResourceFreeze==true)`。
- 停止条件固定: Query Preview bypass / direct write / auto-apply / review自動昇格 / SafeMode後退 / Self-Correction 3回超過。

### Phase 5: Verify -> Proceed
- Verify: docs-checkで契約ID整合・語彙整合・安全後退0件を確認し、不一致時はSelf-Correction最大3回まで。
- Proceed条件（1行）: `Proceed = (collision==0 && vocabularyDrift==0 && safeModeRegression==0 && a1Status=="Done" && pendingDecisionQueueCount==0)`。

### Fail-safe（停止報告テンプレ）
- 失敗条件:
- 影響範囲（ファイル/契約ID）:
- 人間判断が必要な選択肢（2案）:
  - 案1: 契約固定値を維持し、差分要求をA1へ差し戻す。
  - 案2: 契約固定値の変更を承認会議へエスカレーションし、承認後に再凍結する。


## Stream A Phase Lock (2026-04-13)

### Plan
- A1を唯一の契約凍結点として維持し、A2/A3は参照専用とする。

### Execute
- 固定契約ID: `HIL-RS-02-A1-CONTRACT-FREEZE-v1`, `A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|A1-ERROR-IF`, `CE0-CTX-IF`, `CE0-SAFEMODE-IF`, `CE0-REVIEW-IF`, `CG-01..05`。
- 固定判定式: `Go = (a1Status=="Done" && pendingDecisionQueueCount==0 && schemaVersion==1.0.0 && overridePolicy==human_dual_control_only && contractLinkLocked==true && sharedResourceFreeze==true)`。
- 固定NoGo: `NoGo = !Go`。

### Verify
- `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- `rg -n "a1Status=="Done" && pendingDecisionQueueCount==0|schemaVersion=1.0.0|overridePolicy=human_dual_control_only|contractLinkLocked=true|sharedResourceFreeze=true|Pending -> Approved|Pending -> Rejected" 01_Plans/issues/issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md 01_Plans/issues/issue-HIL-RS-02-A1-governance-contract-hardening.md`

### Proceed
- 下流引継ぎは read-only contract pack のみ許可。
- A2/A3 における契約再定義要求は常にA1へ差戻し。

## 11) Read-only Artifact（Phase 4: mock I/F snapshot 公開）

A1契約を下流へ引き渡す際は、次の read-only artifact を固定値として公開する。

| Contract ID | Signature (type) | 禁止事項 |
| --- | --- | --- |
| `A1-CRITIQUE-IF` | `CritiqueV1(critiqueId, targetRef, critiqueType, createdAt, iteration, comment?, constraintHints?)` | 必須キー削除 / review自動昇格 / 生ID保存 |
| `A1-REDIFF-IF` | `ReDiffV1(proposalId, basedOnIteration, diffOps[], traceKey, rationale?)` | `traceKey`欠落 / 非可逆差分 / SafeMode禁止操作の暗黙実行 |
| `A1-ATTR-IF` | `AttributionV1(reviewState, reviewedAt, reviewerRef, auditRecordedAt, reviewContext?, ownerRef?)` | `overridePolicy`緩和 / AIのみで`human_reviewed`昇格 |
| `A1-ERROR-IF` | `A1ErrorV1(errorCode, message, contractId, retryable, occurredAt)` | 未承認`errorCode`追加 / PII埋め込み |

- Artifact属性: `readOnly=true`, `mutationAllowed=false`, `changeRequestRoute=A1-CDC-only`。
- 有効条件: `freezeContractId=="HIL-RS-02-A1-CONTRACT-FREEZE-v1" && schemaVersion=="1.0.0"`。

## Stream A Serial Contract Lock (2026-04-16)

### Phase 1 Read（再Read + 差分抽出）
- 本ファイルを含む Stream A 管轄10ファイルを再Readし、契約ID / Gate式 / 禁止遷移を照合。
- 差分抽出結果:
  - `a1Status=="Done" && pendingDecisionQueueCount==0` を唯一ゲートとして維持。
  - `schemaVersion=1.0.0` / `overridePolicy=human_dual_control_only` / `contractLinkLocked=true` / `sharedResourceFreeze=true` を固定値として維持。
  - 契約ID衝突・依存逆転・未定義競合は 0 件。

### Phase 2 ADR CDC
- Context: A1契約固定を下流A2/A3の参照専用境界として維持する。
- Decision: 新規ADR追加は不要（既存 ADR-0026/0027/0028 と整合）。未承認決定は確定扱いしない。
- Consequences: 契約変更要求はA1へ差戻し、下流はread-only handoff値のみ利用する。

### Phase 3 Plan
- AC/DoD不足時はドラフト提案を先行し、`agreementStatus=agreed` まで Execute へ進まない。
- SSOT固定値:
  - `schemaVersion=1.0.0`
  - `overridePolicy=human_dual_control_only`
  - `contractLinkLocked=true`
  - `sharedResourceFreeze=true`
- Go/No-Go:
  - `Go = (a1Status=="Done" && pendingDecisionQueueCount==0 && schemaVersion=="1.0.0" && overridePolicy=="human_dual_control_only" && contractLinkLocked==true && sharedResourceFreeze==true)`
  - `NoGo = !Go`

### Phase 4 Execute
- 文言・契約ID・依存順序（A1→A2→A3）・停止条件を本ファイル内で同期。
- 禁止遷移を固定:
  - `Pending` bypass（`Pending -> Approved/Rejected` 以外）
  - A1未完了時の A2/A3 `Draft -> Open`
  - 未承認決定の確定扱い
- Read-only handoff:
  - `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
  - `contractIds=A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|A1-ERROR-IF`

### Phase 5 Verify
- `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- `rg -n "a1Status=="Done" && pendingDecisionQueueCount==0|schemaVersion=1.0.0|overridePolicy=human_dual_control_only|contractLinkLocked=true|sharedResourceFreeze=true|Pending -> Approved|Pending -> Rejected" 01_Plans/issues/issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md 01_Plans/issues/issue-HIL-RS-02-A1-governance-contract-hardening.md 01_Plans/issues/issue-HIL-RS-02-next-phase-delivery-plan.md 01_Plans/issues/issue-HIL-RS-01-next-phase-human-loop-reversible-synthesis.md`
- Self-Correctionは最大3回。4回目相当は即停止。

### Phase 6 Proceed
- 再開条件: `NoGo` 要因（未承認決定、識別子不一致、依存逆転）を解消し、再VerifyがPassすること。
- 差戻し先: `issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`（A1契約正本）。
- Decision Queue未解決項目は `Pending` のまま保持し、確定扱いしない。

### Fail-safe（停止報告テンプレ）
1. 失敗条件
2. 影響ファイル・契約ID
3. 人間判断が必要な選択肢（2案）
   - 案1: 既存固定値を維持してA1へ差戻し
   - 案2: 承認会議で固定値変更を決定後に再凍結
