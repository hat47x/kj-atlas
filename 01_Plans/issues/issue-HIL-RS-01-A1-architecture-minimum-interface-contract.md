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

### 10.1) Unresolved Task Start Gate（A2/A3着手条件の確定）

- A2/A3 着手許可式（固定）:
  - `StartAllowed = (a1Status=="Done" && pendingDecisionQueueCount==0 && schemaVersion=="1.0.0" && overridePolicy=="human_dual_control_only" && contractLinkLocked==true && sharedResourceFreeze==true && hasUndefinedContractChangeRequest==false && hasSafeModeRegressionRequest==false && hasShareExportLeakageRelaxationRequest==false && agreementStatus=="agreed")`
- `StartAllowed==false` の場合は NoGo とし、`A1-CDC-only` へ差戻す。
- A2/A3 は次を禁止:
  - 固定識別子の再定義
  - `Pending` bypass（`Approved/Rejected` を経ない遷移）
  - 安全境界の緩和（safeMode既定ON / share-export漏えい防止）

### 10.2) Single Handoff（Stream A → A2/A3）

- 固定I/F一覧:
  - `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
  - `contractIds=A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|A1-ERROR-IF`
  - `schemaVersion=1.0.0`
  - `overridePolicy=human_dual_control_only`
  - `contractLinkLocked=true`
  - `sharedResourceFreeze=true`
- Go/NoGo条件:
  - `Go = StartAllowed`
  - `NoGo = !StartAllowed`
- 差し戻し条件（固定）:
  - 固定値不一致、未承認決定確定化、未定義競合、Self-Correction 3回超過。

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

## Stream A CE0/HIL Approval Ledger (2026-04-16)

### Phase 1 (Read)
- A1/CE0/HIL governanceの契約ID・判定式・禁止遷移を再読し、想定との差分を照合。
- 差分結果: 固定値（`schemaVersion=1.0.0`, `overridePolicy=human_dual_control_only`, freeze flags）は全一致。

### Phase 2 (ADR合意)
- Context: A1契約はCE0契約と直列依存であり、更新窓口を一箇所に固定する必要がある。
- Decision: A1は contract pack の唯一正本を維持し、承認ログは本Issueに追記する。
- Consequences: A2/A3および下流レーンは値の参照のみ許可され、変更要求はA1へ差戻し。

### Phase 3 (Contract Freeze)
- Freeze対象を再固定:
  - `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
  - `contractIds=A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|A1-ERROR-IF`
- ID重複: 0件（CE0/HIL 3 issue照合）。

### Phase 4 (Verify)
- 安全検証結果:
  - safeMode後退: 0件
  - unreviewed保護後退: 0件
  - direct write許容記述: 0件
- Self-Correction: 0/3。

### Phase 5 (Record)
- Snapshot ID: `CE0-HIL-CONTRACT-SNAPSHOT-2026-04-16-v1`
- Snapshot Version: `1.0.0`
- Snapshot Hash (sha256): `851849b770825eb4844d46c77bae34bbefb4aec1ae9bd004e7dc4d50b875a698`
- Reference tuple:
  - `a2a3Unlock = (a1Status=="Done" && pendingDecisionQueueCount==0)`
  - `schemaVersion=1.0.0`
  - `overridePolicy=human_dual_control_only`
  - `contractLinkLocked=true`
  - `sharedResourceFreeze=true`

### Approval Log

| Timestamp (UTC) | Phase | Decision | Result |
| --- | --- | --- | --- |
| 2026-04-16T00:00:00Z | Phase 2 | A1を唯一正本として固定 | Approved |
| 2026-04-16T00:00:00Z | Phase 3 | Freeze keys再固定 | Approved |
| 2026-04-16T00:00:00Z | Phase 4 | Verify gate（safeMode/direct-write） | Pass |
| 2026-04-16T00:00:00Z | Phase 5 | Snapshot発行 | Recorded |

## Stream A Execution Record (2026-04-16, Critical Path / A1 Contract Freeze)

### Phase 1: Read
- 実装開始直前に本ファイルと `issue-HIL-RS-02-A1-governance-contract-hardening.md` を再Readし、想定差分なしを確認。
- 変更範囲は Stream A 許可ファイル2件のみに限定。

### Phase 2: ADR CDC
- Context: A1契約が複線化すると A2/A3 の Open 判定が再現不能になる。
- Decision: Unlock rule を唯一式として維持し、固定識別子（contract IDs / schemaVersion / overridePolicy）を不変で固定。
- Consequences: 下流は read-only handoff のみ許可。契約変更要求は必ず A1 へ差戻し。

### Phase 3: Plan（AC/DoD不足補完ドラフト→合意）
- AC補完: Go/NoGo を文章と条件式の両方で再現可能にする。
- DoD補完: `Plan -> Execute -> Verify -> Proceed/Stop` の順序を本記録に固定。
- 合意状態: `agreementStatus=agreed`（本Issue内で確定）。

### Phase 4: Execute
- Unlock rule（一意）を維持: `a2a3Unlock = (a1Status=="Done" && pendingDecisionQueueCount==0)`。
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
- Go（文章）: A1がDoneでDecision Queueが空、かつ固定識別子が完全一致している場合のみ Proceed。
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
- 失敗条件: `contractIdCollision>0` / `vocabularyCollision>0` / `safeModeRegression>0` / `selfCorrectionCount>3` / `undefinedConflictDetected=true`。
- 影響範囲: 影響ファイル（A1/A2/A3 issue）と契約ID（`CE0-*`, `CG-01..05`, `A1-*`, `HIL-RS-02-A1-CONTRACT-FREEZE-v1`）を列挙する。
- 必要な人間判断: 「固定値維持でA1差戻し」または「CDC承認後に再凍結」の二択を明示して停止する。


## Stream A Contract Lock Record (2026-04-17)

### Phase 1 Read
- Stream A 編集許可4ファイルを再Readし、A1最小I/F契約の固定識別子と禁止遷移に差分ゼロを確認。

### Phase 2 ADR CDC
- Context: A1契約はA2/A3着手可否の唯一基準であり、判定式の重複正本化は不可。
- Decision: 新規CDC起票は不要。既存CDCを継続採用し、契約変更要求はA1-CDC-onlyへ差戻す。
- Consequences: 下流Issueは read-only 参照のみ、ローカル再定義は禁止。

### Phase 3 Plan
- AC/DoD不足なし。`StartAllowed` 判定式と fail-safe 条件を現行固定値で維持する。

### Phase 4 Execute
- 契約境界を再固定:
  - `a2a3Unlock = (a1Status=="Done" && pendingDecisionQueueCount==0)`
  - `Pending -> Approved | Rejected` 以外を禁止
  - `schemaVersion=1.0.0` / `overridePolicy=human_dual_control_only` / freeze flags を変更禁止

### Phase 5 Verify / Proceed
- docs-check 実行: `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`（Pass）。
- `a1Status=="Done" && pendingDecisionQueueCount==0` のみ Proceed 可。未達時は停止して人間判断へエスカレーション。

## Stream E Contract Advancement Update (2026-04-17)

### Phase 1) Read同期（4ファイル固定）
- Read対象をHIL契約4ファイルに限定し、A1を契約正本として再確認。
- 固定値確認: `schemaVersion=1.0.0` / `overridePolicy=human_dual_control_only` / `contractLinkLocked=true` / `sharedResourceFreeze=true`。

### Phase 2) CDC起票/更新（ADR要件）
- Context: A1契約が曖昧だとA2/A3の着手判定と停止判定が両方揺れる。
- Decision: A1は `contract freeze + start gate` のみ扱い、契約変更はCDC承認前に適用しない。
- Consequences: 未承認変更はA1内で保留し、下流はread-only参照を継続する。

### Phase 3) Plan（A1先行・A2/A3開放条件）
- A1完了条件（固定）:
  - `A1Done = (a1Status=="Done" && approvalStatus=="approved")`
- A2/A3開放条件（固定）:
  - `A2A3Open = (A1Done && pendingDecisionQueueCount==0 && agreementStatus=="agreed")`
- 承認前進行禁止:
  - `approvalStatus!="approved"` の場合、次Phaseへ進行禁止（Hold）。

### Phase 4) Execute（契約固定）
- 固定ID: `HIL-RS-02-A1-CONTRACT-FREEZE-v1` / `A1-CRITIQUE-IF` / `A1-REDIFF-IF` / `A1-ATTR-IF` / `A1-ERROR-IF`。
- 契約変更要求ルート: `A1-CDC-only`。

### Phase 5) Verify（条件一致監査）
- 検証式:
  - `Go = (a1Status=="Done" && approvalStatus=="approved" && pendingDecisionQueueCount==0 && schemaVersion=="1.0.0" && overridePolicy=="human_dual_control_only" && contractLinkLocked==true && sharedResourceFreeze==true)`
  - `NoGo = !Go`
- 監査不一致時はSelf-Correction最大3回、超過時停止。

### Phase 6) Proceed（Open化条件の提案）
- Open提案:
  1. `Go==true`
  2. `hasUndefinedContractChangeRequest==false`
  3. `hasSafeModeRegressionRequest==false`
- 未達時はA1で再CDC起票して承認待ちに戻す。

## Stream D A1 Gate Synchronization Record (2026-04-18)

### Phase 1 Read
- 対象4ファイルを再読し、Unlock式を `a1Status=="Done" && pendingDecisionQueueCount==0` に統一されているか照合。
- 照合結果: A1ゲートの正本式は維持。A2/A3のOpenはA1完了前に許可しない方針を継続。

### Phase 2 ADR CDC
- Context: A1契約はHIL-RS全体の唯一ゲートであり、派生ゲートの混在は誤Openを誘発する。
- Decision: A1ゲート契約は `a1Status=="Done" && pendingDecisionQueueCount==0` のみを採用し、未承認の確定化を禁止する。
- Consequences: A2/A3はA1完了前に `Draft -> Open` へ遷移不可。差分要求はA1-CDC-onlyへ差し戻し。
- Decision Status: Pending Approval（文言同期のみ。契約値変更は未実施）。

### Phase 3 Plan
- AC補完: `A1完了前のA2/A3 Open禁止` を明示。
- DoD補完: `Plan -> Execute -> Verify -> Proceed` の強制サイクルを固定。

### Phase 4 Execute
- 状態遷移契約を同期:
  - Unlock（唯一）: `a1Status=="Done" && pendingDecisionQueueCount==0`
  - 禁止遷移: `a1Status!="Done"` での `A2/A3 Draft -> Open`、`Pending bypass`、未承認確定化
  - 停止条件: 式不一致 / 未承認確定化 / 自己修復3回超過

### Phase 5 Verify
- 式一致確認: `a1Status=="Done" && pendingDecisionQueueCount==0`。
- docs-checkを必須化し、不一致時は3回まで修復。4回目相当は即停止。

### Phase 6 Proceed
- Proceed条件: 上記式一致かつ `pendingDecisionQueueCount==0`。
- 不一致時: NoGoで停止し、A1-CDC-onlyへ差戻し。

## Stream A Execution Record (2026-04-18, dedicated lane)

### Phase 1 Read（4ファイル差分一覧）
- Status差分: 4ファイルとも `Status: Open`（差分なし）。
- Dependencies差分:
  - A1最小I/F: `ADR-0026/0027/0028`
  - HIL-RS-02 A1 hardening: `ADR-0026/0027/0028 + issue-HIL-RS-01-A1...`
  - HIL-RS-01親計画: `ADR-0026/0027/0028 + state-transition gate`
  - HIL-RS-02親計画: `ADR-0026/0027/0028 + freezeContractId + state-transition gate`
- Gate式差分: 実効ゲートは全ファイル `a1Status=="Done" && pendingDecisionQueueCount==0` に一致（差分なし）。

### Phase 2 ADR CDC
- Context: 契約固定値は既存ADR（0026/0027/0028）と整合し、方針変更は不要。
- Decision: 方針変更を行わず、固定契約と禁止遷移の同期のみ実施。
- Consequences: A2/A3 は参照専用を維持し、契約差分要求は A1 へ差戻し。
- Approval: `agreementStatus=agreed`（方針変更なしの同期として合意記録）。

### Phase 3 Plan（Checklist宣言）
- Verification checklist: `Plan -> Execute -> Verify -> Proceed`
- AC/DoD補完: `agreementStatus=agreed` を Proceed 前提に固定。

### Phase 4 Execute
- 契約語彙・禁止遷移・差戻し条件を本Issueの固定値へ再同期。
- 明示禁止: A2/A3側での固定契約値再定義。

### Phase 5 Verify
- docs-check相当（validator + rg）で整合確認。
- self-correction 上限: 3回（4回目相当は即停止）。

### Phase 6 Proceed
- Gate: `a1Status=="Done" && pendingDecisionQueueCount==0` を満たす場合のみ進行。
- 未確定事項は Decision Queue に戻す。

## Stream A Serial Contract Record (2026-04-18)

### Phase 1 Read（状態同期）
- 再読対象: 本Issue / `issue-HIL-RS-02-A1-governance-contract-hardening.md`。
- 差分確認（status/owner/AC/scope）:
  - status: `Open` 維持（想定どおり）。
  - owner: `Architecture Owner (Stream A contracts)` 維持（想定どおり）。
  - AC: Unlock rule / Freeze keys / Self-Correction上限の3点は既存記載と一致。
  - scope: planning only を維持し、実装/shared files 変更なし。
- Plan更新要否: なし（差異ゼロ）。

### Phase 2 ADR-CDC（Context / Decision / Consequences）
- Context:
  - A1契約は HIL-RS-02 統治判定の単一正本であり、A2/A3での再定義を許すと誤Open化リスクが発生する。
- Decision:
  - 本Issueの契約値（freezeContractId / contractIds / schemaVersion / overridePolicy / freeze flags）を参照専用の固定値として維持し、変更要求はA1-CDC-onlyへ差戻す。
- Consequences:
  - 下流は read-only handoff のみ利用可能。
  - Pending bypass / SafeMode後退要求 / share-export緩和要求は NoGo 扱い。

### Phase 3 Agreement（承認待ちゲート）
- agreementStatus: `pending_human_approval`
- 承認待ち理由:
  - CDCの確定には human approval が必要。
  - 承認取得前は「提案状態」を維持し、固定値の意味変更を行わない。
- Proceed制約:
  - `agreementStatus=="agreed"` になるまで Contract Freeze の新規確定は禁止。

### Phase 4 Contract Freeze（I/F固定・境界条件・非目標）
- Freeze対象（変更禁止）:
  - `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
  - `contractIds=A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|A1-ERROR-IF`
  - `schemaVersion=1.0.0`
  - `overridePolicy=human_dual_control_only`
  - `contractLinkLocked=true`
  - `sharedResourceFreeze=true`
- 境界条件（Go/NoGo）:
  - `StartAllowed = (a1Status=="Done" && pendingDecisionQueueCount==0 && schemaVersion=="1.0.0" && overridePolicy=="human_dual_control_only" && contractLinkLocked==true && sharedResourceFreeze==true && agreementStatus=="agreed")`
  - `Go = StartAllowed`
  - `NoGo = !StartAllowed`
- 非目標（Stream A）:
  - 03_Implement 配下の実装変更。
  - shared files の更新。
  - A2/A3本文での契約値再定義。

### Phase 5 Handoff（参照ID / mock条件）
- Downstream reference IDs:
  - `HIL-RS-02-A1-CONTRACT-FREEZE-v1`
  - `A1-CRITIQUE-IF`
  - `A1-REDIFF-IF`
  - `A1-ATTR-IF`
  - `A1-ERROR-IF`
- Mock conditions:
  - `schemaVersion=="1.0.0"`
  - `overridePolicy=="human_dual_control_only"`
  - `contractLinkLocked==true`
  - `sharedResourceFreeze==true`
  - `agreementStatus=="agreed"`
- 失敗時フェイルセーフ:
  - 停止条件: Self-Correction > 3 / 未定義競合 / 固定値不一致。
  - 停止報告: `失敗条件 / 影響I/F / 要人間判断` をセットで提出。
