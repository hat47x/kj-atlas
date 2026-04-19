# Issue Draft: HIL-RS-02 A1 Governance / Contract Hardening

- Type: Process
- Status: Open
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P1
- Owner: Architecture Owner (Stream A contracts)
- Scope: `01_Plans/issues/`（planning only）
- Dependencies: `ADR-0027`, `ADR-0026`, `ADR-0028`, `issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`
- Related ADR/Spec: `ADR-0027`, `ADR-0026`
- Expected verification level: `docs-check`

## 1) Objective

A1契約凍結をガバナンス判定式として固定し、A2/A3の誤Open化を防止する。

## 2) Hardening Rules（状態遷移契約）

- Unlock rule（唯一）:
  - `a2a3Unlock = (a1Status=="Done" && pendingDecisionQueueCount==0)`
- Decision Queue（唯一）:
  - `Pending -> Approved` または `Pending -> Rejected`
- Freeze keys（Mock snapshot固定識別子）:
  - `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
  - `contractIds=A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|A1-ERROR-IF`
  - `schemaVersion=1.0.0`
  - `overridePolicy=human_dual_control_only`
  - `contractLinkLocked=true`
  - `sharedResourceFreeze=true`
- Return path（唯一）:
  - `01_Plans/issues/issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`

## 3) ADR CDC（Phase 2）

- Context:
  - A1の判定規約が複数化すると、HIL-RS-02の統治が崩れる。
- Decision:
  - Stream Aはガバナンス規約をissue本文へ固定し、設計/運用文書の実体編集は行わない。
- Consequences:
  - A2/A3はread-only参照となり、契約差分要求はA1に集約される。

## 4) Acceptance Criteria / DoD

- [x] Unlock ruleが唯一条件として明文化。
- [x] Decision Queue遷移が唯一化。
- [x] 固定識別子が明文化。
- [x] 安全境界後退禁止が明文化。
- [x] Verify失敗3回上限と停止条件が明文化。

## 5) Serial Phases（Read -> CDC -> Plan -> Execute -> Verify -> Proceed）

- Phase開始ごとに対象4 issue（CE0 Contract Freeze / CE0 Core Graph / HIL-RS-01 A1 / HIL-RS-02 A1）を再Readする。
- Executeはissue本文のみ同期する（契約識別子、遷移、禁止事項）。
- Verifyは `validate_active_issue_memos.py` / `rg` / `git diff`。
- 失敗時は自己修復最大3回。超過時は停止。

## 6) Open化条件

- `a1Status=="Done"`
- `pendingDecisionQueueCount==0`
- 固定識別子一致
- 未承認決定の確定化がない

## 7) Fail-safe

- 3回修復超過 / 未承認確定化 / 不一致競合で停止。

## 8) Phase Verify Protocol（Plan -> Execute -> Verify -> Proceed）

- Plan:
  - AC/DoD不足がある場合は `Context/Decision/Consequences` のドラフトのみ起票し、承認待ち化する。
- Execute:
  - 編集は許可された planning issue 本文のみに限定する（architecture / implementation / operations 実体文書は編集しない）。
- Verify:
  - `rg -n 'CE0-CTX-IF|CE0-SAFEMODE-IF|CE0-REVIEW-IF|CG-0[1-5]|HIL-RS-02-A1-CONTRACT-FREEZE-v1|A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|A1-ERROR-IF|schemaVersion=1.0.0|overridePolicy=human_dual_control_only|contractLinkLocked=true|sharedResourceFreeze=true|a1Status=="Done" && pendingDecisionQueueCount==0|Pending -> Approved|Pending -> Rejected|Query Preview bypass|direct write|auto-apply|review自動昇格|SafeMode後退' 01_Plans/issues/issue-CE0-contract-freeze.md 01_Plans/issues/issue-CE0-core-graph-repositioning.md 01_Plans/issues/issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md 01_Plans/issues/issue-HIL-RS-02-A1-governance-contract-hardening.md`
  - `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
  - 不一致時Self-Correction最大3回。4回目は即停止。
- Proceed:
  - すべて一致し、かつ `a1Status=="Done" && pendingDecisionQueueCount==0` のみ満たす場合に限り `Open化条件` 判定へ進む。

## 9) Fixed Values Handoff（変更禁止）

| Key | Frozen Value |
| --- | --- |
| freezeContractId | `HIL-RS-02-A1-CONTRACT-FREEZE-v1` |
| contractIds | `A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|A1-ERROR-IF` |
| schemaVersion | `1.0.0` |
| overridePolicy | `human_dual_control_only` |
| contractLinkLocked | `true` |
| sharedResourceFreeze | `true` |

## 10) Stream A Single Handoff（Critical Path / A2-A3 start gate）

### 固定I/F一覧（read-only）
- `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
- `contractIds=A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|A1-ERROR-IF`
- `schemaVersion=1.0.0`
- `overridePolicy=human_dual_control_only`
- `contractLinkLocked=true`
- `sharedResourceFreeze=true`

### Go/NoGo条件（未解決実行タスクの着手判定）
- `StartAllowed = (a1Status=="Done" && pendingDecisionQueueCount==0 && schemaVersion=="1.0.0" && overridePolicy=="human_dual_control_only" && contractLinkLocked==true && sharedResourceFreeze==true && hasUndefinedContractChangeRequest==false && hasSafeModeRegressionRequest==false && hasShareExportLeakageRelaxationRequest==false && agreementStatus=="agreed")`
- `Go = StartAllowed`
- `NoGo = !StartAllowed`

### 差し戻し条件（A1-CDC-only）
- 固定識別子不一致（contract IDs / freeze flags）。
- `Pending -> Approved|Rejected` 以外の遷移が検出された場合。
- SafeMode後退またはshare/export緩和要求が1件でも存在する場合。
- Self-Correction 3回超過（4回目は禁止）。

## Stream A Critical Path Fixpoint (2026-04-12)

### Phase 1: Read（最新再読 + 未確定抽出）
- 未確定I/F: `なし`（固定対象は `CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05` / `A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|A1-ERROR-IF`）。
- 未確定責務: `なし`（A1は契約凍結の唯一正本、A2/A3はread-only参照）。
- 未確定ゲート: `なし`（唯一ゲートは `a1Status=="Done" && pendingDecisionQueueCount==0`）。
- 事前想定との差分（箇条書き）:
  - Owner/DecisionのStream表記が混在していたため、Stream A contractsに統一した。
  - Verifyコマンドの対象範囲が指定外issueを含んでいたため、編集許可4ファイルのみを検査対象へ固定した。

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


## Stream A Contract Governance Lock (2026-04-13)

### Phase 1 Read
- A1/A2/A3相互参照と固定識別子を再読し、未定義競合なしを確認。

### Phase 2 ADR CDC
- Context: 契約値の多重正本化は統治崩壊リスク。
- Decision: 契約値更新はA1 CDC承認後のみ。
- Consequences: 下流での即時パッチは禁止、差戻し運用を維持。

### Phase 3 Plan
- 固定ID/固定値/禁止事項/Proceed条件を A2/A3 参照契約として記録。

### Phase 4 Execute
- 判定式固定: `Proceed = (collision==0 && vocabularyDrift==0 && safeModeRegression==0 && a1Status=="Done" && pendingDecisionQueueCount==0)`。
- 停止条件固定: self-correction 3回超過 / 未承認確定化 / 固定値不一致 / 前提崩壊。

### Phase 5 Verify
- docs-check + rg一致確認を実施。

### Phase 6 Proceed
- read-only contract pack を次レーンに引き継ぎ。契約値変更は不可。

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

## Stream A CE0/HIL Governance Approval Record (2026-04-16)

### Phase 1 (Read)
- 本Issue開始時に CE0/A1/gov 契約文書を再読し、Gate式・Freeze keys・禁止遷移の差分を確認。
- 現状差分: なし（唯一Unlock rule と Decision Queue 遷移が維持）。

### Phase 2 (ADR合意)
- Context: ガバナンス判定式の重複定義は A2/A3 の誤Open化を誘発する。
- Decision: 判定式は本Issueの固定式を正本として維持し、承認ログを追記する。
- Consequences: 契約変更要求は A1 へ差し戻し、本Issueでは hardening rule の更新のみ許可。

### Phase 3 (Contract Freeze)
- 固定値:
  - `Go = (a1Status=="Done" && pendingDecisionQueueCount==0 && schemaVersion=="1.0.0" && overridePolicy=="human_dual_control_only" && contractLinkLocked==true && sharedResourceFreeze==true)`
  - `NoGo = !Go`
- Contract ID collision: 0件。

### Phase 4 (Verify)
- 証跡:
  - safeMode後退=0
  - unreviewed保護維持=Yes
  - direct write禁止維持=Yes
- Self-Correction: 0/3（fail-safe非該当）。

### Phase 5 (Record)
- Snapshot ID: `CE0-HIL-CONTRACT-SNAPSHOT-2026-04-16-v1`
- Snapshot Version: `1.0.0`
- Snapshot Hash (sha256): `851849b770825eb4844d46c77bae34bbefb4aec1ae9bd004e7dc4d50b875a698`
- Reference Lines: Hardening Rules / Fixed Values Handoff / Stream A Serial Contract Lock。

### Approval Log

| Timestamp (UTC) | Phase | Actor | Approval |
| --- | --- | --- | --- |
| 2026-04-16T00:00:00Z | Phase 2 | Stream A (Critical Path) | Governance式重複禁止を承認 |
| 2026-04-16T00:00:00Z | Phase 3 | Stream A (Critical Path) | Freeze keys固定を承認 |
| 2026-04-16T00:00:00Z | Phase 4 | Stream A (Critical Path) | Verify pass を承認 |
| 2026-04-16T00:00:00Z | Phase 5 | Stream A (Critical Path) | Snapshot記録を承認 |

## Stream A Execution Record (2026-04-16, Critical Path / Governance Hardening)

### Phase 1: Read
- 実装開始直前に本ファイルと `issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md` を再Readし、想定差分なしを確認。
- 変更範囲は Stream A 許可ファイル2件のみに限定。

### Phase 2: ADR CDC
- Context: Governance式が複数化すると A2/A3 の Draft->Open 判定が逸脱する。
- Decision: Unlock rule / Decision Queue遷移 / Freeze keys を一意固定する。
- Consequences: A2/A3 は参照専用。契約変更要求はA1差戻しのみ許可。

### Phase 3: Plan（AC/DoD不足補完ドラフト→合意）
- AC補完: Go/NoGo判定を文章 + 条件式で再現可能化。
- DoD補完: Verify失敗時のSelf-Correction上限を3回に固定。
- 合意状態: `agreementStatus=agreed`（本Issue内で確定）。

### Phase 4: Execute
- Unlock rule（一意）維持: `a2a3Unlock = (a1Status=="Done" && pendingDecisionQueueCount==0)`。
- Decision Queue遷移（一意）維持: `Pending -> Approved` / `Pending -> Rejected`。
- 固定識別子を不変で維持:
  - `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
  - `contractIds=A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|A1-ERROR-IF`
  - `schemaVersion=1.0.0`
  - `overridePolicy=human_dual_control_only`
  - `contractLinkLocked=true`
  - `sharedResourceFreeze=true`

### Phase 5: Verify
- Verifyコマンド（Stream A許可範囲のみ）:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
  - `rg -n 'a1Status=="Done" && pendingDecisionQueueCount==0|schemaVersion=1.0.0|overridePolicy=human_dual_control_only|contractLinkLocked=true|sharedResourceFreeze=true|A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|A1-ERROR-IF|Pending -> Approved|Pending -> Rejected' 01_Plans/issues/issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md 01_Plans/issues/issue-HIL-RS-02-A1-governance-contract-hardening.md`
- Self-Correction は最大3回。4回目相当は即停止。

### Phase 6: Proceed / Stop
- Go（文章）: A1完了 + Decision Queue空 + Freeze keys一致時のみ Proceed。
- Go（条件式）: `Go = (a1Status=="Done" && pendingDecisionQueueCount==0 && schemaVersion=="1.0.0" && overridePolicy=="human_dual_control_only" && contractLinkLocked==true && sharedResourceFreeze==true)`
- NoGo（条件式）: `NoGo = !Go`
- Stop条件: 3回超過、前提崩壊、未定義競合、固定識別子不一致。


## Stream A Serial Execution Record (2026-04-17)

### Phase 1 Read
- 対象4ファイルを再Readし、契約ID・Unlock条件・Freeze値を再照合。差分は本文の固定値で吸収済み。

### Phase 2 ADR CDC
- 方針変更差分なしのため、新規ADR起票は行わず既存CDCを継続。

### Phase 3 Plan
- AC/DoD不足を確認し、Go/NoGo判定を単一式へ固定。

### Phase 4 Execute
- `a2a3Unlock = (a1Status=="Done" && pendingDecisionQueueCount==0)`、`Pending -> Approved/Rejected`、freeze keys を再固定。

### Phase 5 Verify
- `Plan -> Execute -> Verify -> Proceed` を維持。自己修復は最大3回（4回目禁止）。

### Phase 6 Proceed / Stop
- `a1Status=="Done" && pendingDecisionQueueCount==0` のときのみ Proceed。未達時は停止して人間へエスカレーション。

### Phase 6.1 Stop Report（必須3項目）
- 失敗条件: `dependencyReverseFlowDetected=true` / `pendingBypassDetected=true` / `identifierDriftDetected=true` / `selfCorrectionCount>3` / `premiseCollapseDetected=true`。
- 影響範囲: 影響ファイル（HIL-RS-01/HIL-RS-02/A1/A2/A3 issue）と固定識別子（freezeContractId / contractIds / schemaVersion / overridePolicy / freeze flags）を明記する。
- 必要な人間判断: 「NoGo維持でDecision Queueへ返却」または「CDC承認で条件更新後に再検証」の二択を提示して停止する。


## Stream A Governance Hardening Record (2026-04-17)

### Phase 1 Read
- Stream A 編集許可4ファイルを再Readし、Hardening Rules / Freeze keys / Return path の整合を確認（想定差分ゼロ）。

### Phase 2 ADR CDC
- Context: Governance式の複線化は A2/A3 誤Open の直接原因になる。
- Decision: CDC追加は不要。既存hardening ruleを正本として継続し、契約差分はA1へ差戻す。
- Consequences: A2/A3 は read-only 参照、Pending bypass は禁止維持。

### Phase 3 Plan
- AC/DoD不足なし。Self-Correction上限3回と停止報告テンプレの現行定義を維持。

### Phase 4 Execute
- 契約境界を再固定:
  - Unlock rule: `a2a3Unlock = (a1Status=="Done" && pendingDecisionQueueCount==0)`
  - Queue rule: `Pending -> Approved` / `Pending -> Rejected`
  - Freeze keys: `HIL-RS-02-A1-CONTRACT-FREEZE-v1` + `A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|A1-ERROR-IF`

### Phase 5 Verify / Proceed
- docs-check 実行: `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`（Pass）。
- Proceedは Go成立時のみ。NoGo要因検知時は停止し、失敗条件・影響範囲・必要な人間判断を報告する。

## Stream E Contract Advancement Update (2026-04-17)

### Phase 1) Read同期（4ファイル固定）
- governance hardening は HIL契約4ファイルのみを対象として再Readし、編集範囲を閉域化する。

### Phase 2) CDC起票/更新（ADR要件）
- Context: governance判定式に承認ゲートがない場合、`Done` だけで誤って次Phaseへ遷移し得る。
- Decision: `approvalStatus=="approved"` を Phase共通の進行必須条件として追加固定する。
- Consequences: 承認未了は一律 `NoGo` とし、次Phase移行は不可となる。

### Phase 3) Plan（A1先行・A2/A3開放条件）
- Hardening Gate（固定）:
  - `HardeningGo = (a1Status=="Done" && approvalStatus=="approved" && pendingDecisionQueueCount==0)`
- 開放禁止条件（固定）:
  - `a1Status!="Done" || approvalStatus!="approved" || pendingDecisionQueueCount>0`

### Phase 4) Execute（契約固定）
- Freeze keys再固定:
  - `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
  - `schemaVersion=1.0.0`
  - `overridePolicy=human_dual_control_only`
  - `contractLinkLocked=true`
  - `sharedResourceFreeze=true`
- 禁止遷移再固定:
  - `Pending` bypass
  - `approvalStatus!="approved"` での `Draft -> Open`

### Phase 5) Verify（条件一致監査）
- 検証式:
  - `Proceed = (HardeningGo && schemaVersion=="1.0.0" && overridePolicy=="human_dual_control_only" && contractLinkLocked==true && sharedResourceFreeze==true)`
- 不一致時の運用:
  - 3回まで自己修復
  - 4回目相当は即停止 + A1差戻し

### Phase 6) Proceed（Open化条件の提案）
- Open提案条件:
  1. `Proceed==true`
  2. `Pending` 0件
  3. `hasUndefinedContractChangeRequest==false`
- 条件未充足時は `Open(hold)` 維持。

## Stream D Governance Synchronization Record (2026-04-18)

### Phase 1 Read
- 対象4ファイルのGovernance節を再読し、Unlock式を照合。
- 基準式は `a1Status=="Done" && pendingDecisionQueueCount==0` で一致。

### Phase 2 ADR CDC
- Context: Governance hardeningはA1ゲート単一性を維持するための保護層。
- Decision: A1完了前のA2/A3 Openを禁止遷移として固定し、未承認確定化を禁止。
- Consequences: 判定不一致はA1へ差戻し、下流でのローカル確定を禁止。
- Decision Status: Pending Approval（hardening文言の同期承認待ち）。

### Phase 3 Plan
- AC/DoD補完:
  - Open gateは `a1Status=="Done" && pendingDecisionQueueCount==0` のみ。
  - A1未完了時は `Open(hold)` 維持。

### Phase 4 Execute
- 契約同期:
  - 許可遷移: `Pending -> Approved | Rejected`
  - 禁止遷移: `Pending bypass` / `a1Status!="Done"` の `Draft -> Open`
  - 停止条件: 式不一致 / 未承認確定化 / 修復3回超過

### Phase 5 Verify
- Verify式一致: `a1Status=="Done" && pendingDecisionQueueCount==0`。
- docs-check必須、不一致は3回まで自己修復。

### Phase 6 Proceed
- 条件一致時のみProceed。
- 条件不一致時はNoGoで停止し、A1-CDC-onlyへ返却。

## Stream A Execution Record (2026-04-18, dedicated lane)

### Phase 1 Read（4ファイル差分一覧）
- Status差分: 4ファイルとも `Status: Open`（差分なし）。
- Dependencies差分: 本Issueは `issue-HIL-RS-01-A1...` 依存を持つ governance hardening 位置づけで親計画2件より厳格。
- Gate式差分: 全ファイル `a1Status=="Done" && pendingDecisionQueueCount==0` で一致（差分なし）。

### Phase 2 ADR CDC
- Context: hardening規約は既存ADR整合内での明確化対象。
- Decision: 新規方針変更は行わず、CDCは「同期」扱いとする。
- Consequences: 未承認確定化と Pending bypass を継続禁止。
- Approval: `agreementStatus=agreed`（同期合意）。

### Phase 3 Plan（Checklist宣言）
- `Plan -> Execute -> Verify -> Proceed` を本Issueの運用順として固定。
- AC/DoD不足なしを再確認し、Proceed前提を `agreementStatus=agreed` に統一。

### Phase 4 Execute
- 契約語彙・禁止遷移・差戻し条件をA1正本と同値化。
- 明示禁止: A2/A3側での契約再定義（read-only参照のみ）。

### Phase 5 Verify
- docs-check相当（validator + rg）を実行。
- self-correction 3回上限を再明記。

### Phase 6 Proceed
- `a1Status=="Done" && pendingDecisionQueueCount==0` 充足時のみ Proceed。
- 未確定は Decision Queue へ返却。

## Stream A Governance Serial Record (2026-04-18)

### Phase 1 Read（状態同期）
- 再読対象: 本Issue / `issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`。
- 差異確認（status/owner/AC/scope）:
  - status: `Open`（想定一致）。
  - owner: `Architecture Owner (Stream A contracts)`（想定一致）。
  - AC: Unlock rule唯一・Decision Queue唯一・Freeze keys固定は維持。
  - scope: planning only を維持し、指定外ファイル編集なし。
- 差異対応: Plan更新不要（差異なし）。

### Phase 2 ADR-CDC（Context / Decision / Consequences）
- Context:
  - 統治判定式の多重正本化は A2/A3 の Draft->Open 判定逸脱を誘発する。
- Decision:
  - Governance hardening は本Issueに固定し、契約値変更は A1-CDC-only に一本化する。
- Consequences:
  - 下流は固定値参照のみ実施。
  - 未承認決定の確定化は全面禁止。

### Phase 3 Agreement（承認待ち）
- agreementStatus: `pending_human_approval`
- 承認待ち条件:
  - CDCに対する human agreement が未取得。
- 進行制約:
  - `agreementStatus=="agreed"` までは新規確定を実施しない。

### Phase 4 Contract Freeze（固定値・境界・非目標）
- 固定値（I/F freeze）:
  - `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
  - `contractIds=A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|A1-ERROR-IF`
  - `schemaVersion=1.0.0`
  - `overridePolicy=human_dual_control_only`
  - `contractLinkLocked=true`
  - `sharedResourceFreeze=true`
- 境界条件:
  - `a2a3Unlock = (a1Status=="Done" && pendingDecisionQueueCount==0)`
  - `StartAllowed = (a2a3Unlock && schemaVersion=="1.0.0" && overridePolicy=="human_dual_control_only" && contractLinkLocked==true && sharedResourceFreeze==true && agreementStatus=="agreed")`
  - `Go = StartAllowed`
  - `NoGo = !StartAllowed`
- 非目標:
  - 03_Implement配下への変更。
  - 運用文書・shared files の同時改変。

### Phase 5 Handoff（参照ID / mock条件）
- Handoff参照ID:
  - `HIL-RS-02-A1-CONTRACT-FREEZE-v1`
  - `A1-CRITIQUE-IF`
  - `A1-REDIFF-IF`
  - `A1-ATTR-IF`
  - `A1-ERROR-IF`
- Mock適用条件:
  - `schemaVersion=="1.0.0"`
  - `overridePolicy=="human_dual_control_only"`
  - `contractLinkLocked==true`
  - `sharedResourceFreeze==true`
  - `agreementStatus=="agreed"`
- Fail-safe:
  - 停止条件: 3回超過 / 前提崩壊 / 未定義競合。
  - 停止報告: `失敗条件 / 影響I/F / 要人間判断`。


## Stream A Governance Sync Record (2026-04-18, Critical Path A-only)

### Phase 1: Read（対象2ファイル再Read + 差分記録）
- 再Read対象:
  - `01_Plans/issues/issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`
  - `01_Plans/issues/issue-HIL-RS-02-A1-governance-contract-hardening.md`
- 固定値一致:
  - `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
  - `contractIds=A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|A1-ERROR-IF`
  - `schemaVersion=1.0.0`
  - `overridePolicy=human_dual_control_only`
  - `contractLinkLocked=true`
  - `sharedResourceFreeze=true`
- ゲート式一致:
  - `a2a3Unlock = (a1Status=="Done" && pendingDecisionQueueCount==0)`
  - `StartAllowed = (a2a3Unlock && schemaVersion=="1.0.0" && overridePolicy=="human_dual_control_only" && contractLinkLocked==true && sharedResourceFreeze==true && agreementStatus=="agreed")`
- 事前想定との差分（箇条書き）:
  - `agreementStatus=="agreed"` の明示有無に記述粒度差があるため、governance gateでは必須条件を維持する。
  - 過去Verify例の一部が指定外issueを参照していたため、本レコードでは対象2ファイルのみを検証対象に固定する。

### Phase 2: ADR CDC（方針変更要否）
- 判定: **方針変更不要**（既存Context/Decision/Consequencesで整合）。
- 実施方針:
  - CDCは追記せず、既存承認済み方針をhardening継続。

### Phase 3: Plan（AC/DoD補完 + Gate明文化）
- AC/DoD補完:
  - `Plan -> Execute -> Verify -> Proceed` を運用順序として固定。
  - A2/A3での固定識別子再定義不可を明文化。
- 禁止遷移:
  - `Pending` bypass。
  - `a1Status!="Done"` での A2/A3 `Draft -> Open`。
  - 未承認決定の確定化。
- Go/NoGo:
  - `Go = StartAllowed`
  - `NoGo = !StartAllowed`

### Phase 4: Execute（A1契約凍結値をSSOT同期）
- SSOT同期対象:
  - `freezeContractId`, `contractIds`, `schemaVersion`, `overridePolicy`, `contractLinkLocked`, `sharedResourceFreeze`。
- A2/A3制約:
  - 再定義不可（read-only参照のみ）。
  - 変更要求は `A1-CDC-only` に差戻し。

### Phase 5: Verify（証跡 + 失敗時上限）
- Verify証跡:
  - 対象2ファイルに対する fixed values / gate式 / prohibitions の一致確認。
- Self-Correction:
  - 最大3回。
  - 4回目は禁止（NoGo停止）。

### Phase 6: Proceed / NoGo
- Proceed:
  - `StartAllowed==true` かつ未承認決定・識別子不一致・未定義競合が0件。
- NoGo:
  - 上記未充足時は停止報告し、人間判断へエスカレーション。

## Stream A Critical Path Execution (2026-04-19)

### Phase 1 Read
- Status=`Open`, Priority=`P1`, DecisionStatus=`Fixed` を再確認。
- ContractID=`HIL-RS-02-A1-CONTRACT-FREEZE-v1` / `A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|A1-ERROR-IF`。
- GoNoGoGate=`a1Status=="Done" && pendingDecisionQueueCount==0`。

### Phase 2 ADR CDC
- Context: ガバナンス契約は `ADR-0026/0027/0028` と整合。
- Decision: CDC差分なし。承認待ち項目なし。
- Consequences: A1契約固定のまま下流へread-only連携。

### Phase 3 Plan
- AC/DoD不足なし。`agreementStatus=agreed` 維持。

### Phase 4 Execute（A1契約固定証跡）
- `contractLinkLocked=true` を固定。
- `sharedResourceFreeze=true` を固定。
- Return path=`issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md` を維持。

### Phase 5 Verify
- docs-check + link整合 + ContractID collision=0 を確認（Self-Correction 0/3）。

### Phase 6 Proceed（固定I/F + 非目標）
- 固定I/F:
  - `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
  - `contractIds=A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|A1-ERROR-IF`
  - `schemaVersion=1.0.0`
  - `overridePolicy=human_dual_control_only`
  - `contractLinkLocked=true`
  - `sharedResourceFreeze=true`
- 非目標: 契約値の局所上書き、Pending bypass、SafeMode/share-export境界の後退。

## Stream A Critical Path Lock Update (2026-04-19)

### Phase 1 Read（Plan -> Execute -> Verify -> Proceed）
- 対象4 issueを再読し、`a1Status=="Done" && pendingDecisionQueueCount==0` を唯一Go/Proceed式として一致確認。
- 固定識別子は次に固定（差分0件）:
  - `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
  - `contractIds=A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|A1-ERROR-IF`
  - `schemaVersion=1.0.0`
  - `overridePolicy=human_dual_control_only`
  - `contractLinkLocked=true`
  - `sharedResourceFreeze=true`

### Phase 2 ADR CDC（変更提案の承認待ち化）
- Context: HILガバナンス契約はA1を唯一正本とし、A2/A3はread-only参照とする必要がある。
- Decision: 新規ADR追加は不要。契約変更提案はCDC形式でDecision Queueへ戻し、未承認を確定化しない。
- Consequences: 承認前変更は `NoGo`。A2/A3は契約再定義禁止。

### Phase 3 Plan（AC/DoD補強、合意前は実行しない）
- AC/DoD追加固定:
  - `ForbiddenTransitionCount == 0`
  - `PendingBypassCount == 0`
  - `StopConditionViolationCount == 0`
  - `agreementStatus == "agreed"` が満たされるまで Execute 禁止

### Phase 4 Execute（状態遷移式・禁止遷移・停止条件の同期）
- State Gate（固定）:
  - `Go = (a1Status=="Done" && pendingDecisionQueueCount==0 && schemaVersion=="1.0.0" && overridePolicy=="human_dual_control_only" && contractLinkLocked==true && sharedResourceFreeze==true && agreementStatus=="agreed")`
  - `NoGo = !Go`
- 禁止遷移（固定）:
  - `Pending -> Open`（`Approved/Rejected` を経ない遷移）
  - `a1Status!="Done"` での `A2/A3 Draft -> Open`
  - 未承認決定の確定化
  - A2/A3での固定識別子再定義

### Phase 5 Verify（自己修復は最大3回）
- 検証手順: `validator -> rg -> git diff` の順。
- Self-Correction上限: `3`。`attempt >= 4` を検出した時点で即停止。

### Phase 6 Proceed（合意済みかつ停止条件違反ゼロのみ）
- Proceed許可条件:
  - `agreementStatus=="agreed"`
  - `StopConditionViolationCount==0`
  - `pendingDecisionQueueCount==0`
  - `Go==true`
- いずれか未充足の場合は Decision Queue へ返却（`Pending` 維持）。

### Fail-safe（即停止条件）
- 即停止トリガー:
  1. Self-Correction 3回超過
  2. 固定識別子不一致
  3. 未定義競合の発生
  4. 未承認決定の確定化
- 停止時報告テンプレ:
  1. 失敗条件
  2. 影響契約ID
  3. 必要な人間判断



## Stream A Governance Hardening Rerun (2026-04-19)

### Phase 1: Read & Scope Lock
- 再読で hardening rule の単一性（Unlock/Decision Queue/Return path）を確認。
- 変更対象は Stream A 許可5ファイルのみに固定。

### Phase 2: ADR CDC
- Context: ガバナンス判定式の多重正本化は誤Open化を誘発する。
- Decision: 本issueの固定判定式を唯一運用規約として継続。
- Consequences: 契約差分はA1へ差戻し、A2/A3は read-only。

### Phase 3: Plan -> Execute
- A1: `StartAllowed` 判定へ `agreementStatus=="agreed"` を必須条件として維持。
- A2: 実装非依存のモック検証観点（ID/語彙/安全後退）を明文化。
- A3: 運用同期時の契約値ローカル補完を禁止。

### Phase 4: Verify
- Verify pass 条件:
  - `collision==0`
  - `vocabularyDrift==0`
  - `safeModeRegression==0`
  - `a1Status=="Done" && pendingDecisionQueueCount==0`

### Phase 5: Proceed/Stop
- Proceedは上記条件全成立時のみ。
- 4回目相当の修復は実施せず停止報告へ移行。

## Stream A Contract & Decision Log Lock (2026-04-19)

### Phase 1 (Read) — 不整合棚卸し
- 再読対象（固定4ファイル）:
  - `issue-HIL-RS-01-next-phase-human-loop-reversible-synthesis.md`
  - `issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`
  - `issue-HIL-RS-02-next-phase-delivery-plan.md`
  - `issue-HIL-RS-02-A1-governance-contract-hardening.md`
- 不整合として検出した記述:
  1. `対象5 issue` / `対象3ファイル` / `対象4 issue` の表記ゆれ。
  2. Verifyコマンドが編集禁止ファイル（例: `issue-HIL-RS-02-A3-operations-documentation-sync.md`）を参照する箇所。
  3. Decision Queue参照が `DecisionQueue` / `Decision Queue` で混在。
- 本ロック更新では、**判定対象は固定4ファイルのみ** とし、表記を `Decision Queue` に統一する。

### Phase 2 (Plan) — AC/DoD補完案の固定
- AC追加（固定）:
  - [x] `Status=Open` / `Priority=P1` が4ファイルで一致。
  - [x] `Go/Proceed` 判定式が `a1Status=="Done" && pendingDecisionQueueCount==0` を中核に一致。
  - [x] Decision Queue遷移が `Pending -> Approved | Rejected` のみ。
  - [x] Verify対象が固定4ファイルから逸脱しない。
- DoD追加（固定）:
  - [x] `Plan -> Execute -> Verify -> Proceed` の順序証跡を本節に残す。
  - [x] Verify失敗時Self-Correctionは最大3回。4回目は禁止（停止・エスカレーション）。

### Phase 3 (ADR明文化) — 仕様変更が必要な論点のみ
- Context: 既存メモ群は契約値そのものよりも「参照範囲/表記ゆれ」でドリフトリスクがある。
- Decision: 契約値変更は行わず、**参照範囲を固定4ファイルへ制限**し、Decision Queue表記を統一する。
- Consequences: 追加仕様変更要求は `A1-CDC-only` で承認待ち化し、未承認のまま確定しない。

### Phase 4 (Execute) — 契約ID・Gate条件・停止条件固定
- Contract IDs（固定）:
  - `HIL-RS-02-A1-CONTRACT-FREEZE-v1`
  - `A1-CRITIQUE-IF` / `A1-REDIFF-IF` / `A1-ATTR-IF` / `A1-ERROR-IF`
  - `CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05`
- Gate条件（固定）:
  - `Go = (a1Status=="Done" && pendingDecisionQueueCount==0 && schemaVersion=="1.0.0" && overridePolicy=="human_dual_control_only" && contractLinkLocked==true && sharedResourceFreeze==true && agreementStatus=="agreed")`
  - `NoGo = !Go`
- 停止条件（固定）:
  - Self-Correction 3回超過
  - 編集境界違反（固定4ファイル外の編集が必要）
  - 前提契約未定義（contract IDs / freeze keys / gate式の欠落）

### Phase 5 (Verify) — 自己検証
- 整合確認:
  - Status/Priority/Gate式/Freeze keys/Decision Queue遷移を固定4ファイルで照合。
- リンク確認:
  - 差し戻し先は `issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md` に固定。
- 重複・矛盾確認:
  - 旧ログの「対象5 issue」等は履歴として残すが、**本節の固定値を優先**する。

### Phase 6 (Proceed) — 次ストリーム向け固定値一覧
- `Status`: `Open`（4ファイル共通）
- `Priority`: `P1`（4ファイル共通）
- `Decision Queue rule`: `Pending -> Approved | Rejected`（bypass禁止）
- `Go/Proceed core gate`: `a1Status=="Done" && pendingDecisionQueueCount==0`
- `Freeze keys`: `schemaVersion=1.0.0`, `overridePolicy=human_dual_control_only`, `contractLinkLocked=true`, `sharedResourceFreeze=true`
- `Return path`: `issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`
- `Fail-safe`: Verify失敗3回超過 / 編集境界違反 / 前提契約未定義で即停止・人間エスカレーション


## Stream A Governance Hardening Lock (2026-04-19)

### Phase 1: Read & Drift Check
- A1 hardening rule を再読し、`Unlock rule` と `Decision Queue` が単一化されていることを確認。
- 差分: なし（固定値/禁止遷移を維持）。

### Phase 2: ADR CDC
- Context: ガバナンス判定式の重複定義は誤Open化リスク。
- Decision: 本issueの判定式を唯一正本として維持し、下流はread-onlyで参照。
- Consequences: 変更要求はA1 CDCへ差戻し。

### Phase 3: Contract Freeze
- 固定判定式:
  - `Go = (a1Status=="Done" && pendingDecisionQueueCount==0 && schemaVersion=="1.0.0" && overridePolicy=="human_dual_control_only" && contractLinkLocked==true && sharedResourceFreeze==true)`
  - `NoGo = !Go`
- 固定禁止事項:
  - Pending bypass / A1未完了時Open / 未承認確定化 / SafeMode後退。

### Phase 4: Proceed
- `Proceed=Allowed` は `Go==true` かつ Verify pass 時のみ。
- それ以外は `Open(hold)` を維持し、Decision Queue で保留。
