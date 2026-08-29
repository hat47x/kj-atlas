# Issue Draft: HIL-RS-02 Next-Phase Delivery Plan（Stream H delivery planning lane）

- Type: Process
- Status: Done
- Source Issue: N/A
- Priority: P1
- Owner: Stream H Agent（delivery planning only）
- Scope: `01_Plans/issues/done/issue-HIL-RS-02-next-phase-delivery-plan.md` のみ
- Out of scope: 上記以外すべてのファイル編集、`03_Implement/**`、`04_Documentation/**`、実装コード編集
- Related ADR/Spec: `ADR-0026`, `ADR-0027`, `ADR-0028`, `ADR-0039`
- Dependencies (read-only): `issue-HIL-RS-02-A1-governance-contract-hardening.md`（Done 2026-06-20）
- Expected verification level: `docs-check`

## Done 2026-06-20
A2A3_UNLOCK satisfied: a1Status=="Done" (HIL-RS-01-A1 + HIL-RS-02-A1 both Done) && pendingDecisionQueueCount==0 (ADR-0039).
All Phases 1-6 previously ran with Proceed=Hold (A1 gate). Now A1 gate satisfied → delivery plan Done.
SafeMode invariants preserved; contract redefinition block maintained.

## Canonical Gate Equation（A1 unlock single predicate）
- `A2A3_UNLOCK = (a1Status=="Done" && pendingDecisionQueueCount==0)`
- `Proceed=Go` は `A2A3_UNLOCK && fixedKeyDrift==0 && safeModeRetreat==false` のときのみ。
- `Proceed=Hold` は `a1Status!="Done" || pendingDecisionQueueCount>0`（未承認/heldを含む）。
- `Proceed=Stop` は `pendingBypassDetected || contractRedefinitionRequested || fixedKeyDrift>0 || safeModeRetreat || verifyAttempts>3`。

## Fixed Guardrails（変更禁止）
- `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
- `schemaVersion=1.0.0`
- `overridePolicy=human_dual_control_only`
- `contractLinkLocked=true`
- `sharedResourceFreeze=true`
- `safeModeDefault=ON`
- `safeModeBoundary=SAFE_MODE_STRICT_ON`
- `decisionQueueTransition=Pending -> Approved | Pending -> Rejected`
- `NoGo return path = issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`

## Stream H Execution Protocol（固定）
- Required order: **Phase 1 Read → Phase 2 ADR → Phase 3 Plan → Phase 4 Execute → Phase 5 Verify → Phase 6 Proceed/Stop**（直列、並列禁止）
- Every phase rule: 各Phaseは先頭で必ず Read同期（依存・固定値・A1状態確認）を行ってから次へ進む。
- A1 gate rule: **A1未完了時は Proceed=Hold を維持し、確定化・強行Proceedを禁止する。**
- Verify repair limit: `<=3`（3回で収束しない場合は `Stop`）
- Hard stop: safeMode後退要求 / 契約ID再定義要求 / pending bypass / allowlist外編集要求 / Verify上限超過

## Phase 1 Read（基準固定）
### Plan
- `ADR-0026/0027/0028` と A1依存を再読し、判断材料を `approval pending` / `dependency pending` / `drift risk` に分類する。
### Execute
- A1依存の現状を `A1 not done` 前提で固定し、後続Phaseのゲート前提へ接続する。
### Verify
- 3分類が後続Phase 2〜6の判定式に接続され、A1完了前提の誤記がないこと。
### Proceed/Stop
- Proceed=Hold（A1完了待ち）

## Phase 2 ADR（参照固定）
### Plan
- delivery plan本文の判断根拠を `ADR-0026/0027/0028` に明示リンクし、契約再定義を行わない方針を固定する。
### Execute
- Decision: Stream Hは「delivery planning only」「契約参照固定」「A1 read-only（Pending参照のみ）」の3点を維持する。
### Verify
- ADR参照が欠落なく記載され、A1未完了下での確定化文言（Open化許可・承認済み扱い）が存在しないこと。
### Proceed/Stop
- Proceed=Hold

## Phase 3 Plan（マイルストーン定義）
### Plan
- M1〜M3を計画文書内で定義し、実装着手条件と分離する。
### Execute
- M1: 固定契約値とA1依存式の一致確認
- M2: Gate判定（Go/Hold/Stop）をA1依存で固定
- M3: Verify証跡（diff/status/docs-check）を記録
### Verify
- 各マイルストーンが「計画整備のみ」の範囲に収まり、他ファイル編集を要求しないこと。
### Proceed/Stop
- Proceed=Hold

## Phase 4 Execute（計画書反映）
### Plan
- AC/DoDをA1未完了運用に整合させ、Hold継続を前提化する。
### Execute
- AC群へ「A1 not done時はHold維持」「A1確定前のOpen/In Progress化禁止」を明記する。
### Verify
- AC/DoDがGo条件と矛盾せず、A1完了前の強行遷移条件を含まないこと。
### Proceed/Stop
- Proceed=Hold

## Phase 5 Verify（検証運用）
### Plan
- Verify手順を3回上限で運用する規則に更新し、超過時Stopを明示する。
### Execute
- Verify trial counter を `1..3` に固定し、`trial=4` は実施せず即Stopとする。
### Verify
- 本文に「Verify 3回上限、超過時Stop」が明記され、例外条項がないこと。
### Proceed/Stop
- Proceed=Hold

## Phase 6 Proceed/Stop（最終ゲート固定）
### Plan
- A1未完了時の最終判定をHold固定で閉じ、強行Proceed経路を除去する。
### Execute
- Stopper-1: `A1 not done` の間は `Proceed=Hold` 維持。
- Stopper-2: `fixedKeysDiff>0 || pending bypass || unrecorded approval inference || scope violation` は即Stop。
- Stopper-3: `verifyAttempts>3` は即Stop。
### Verify
- Hold/Stop判定がPhase 1〜5と矛盾せず、GoはA1完了時のみ可能であること。
### Proceed/Stop
- Proceed=Hold（A1完了待ち）

## Draft解除条件（Draft -> Open/Hold）
- [x] Scope が単一ファイル（本ファイル）のみに限定されている。
- [x] 固定契約値（freezeContractId / schemaVersion / safeMode / decisionQueueTransition）が明示され、再定義禁止が明記されている。
- [x] A1依存を read-only とし、`A1 not done => Proceed=Hold` が明記されている。
- [x] Phase 1..6 直列と、毎Phase Read同期が定義されている。
- [x] Verify 3回上限と超過時Stopが明記されている。
- [x] ADR-0026/0027/0028 の明文化参照がある。

## Open/Hold定義（実行開始条件）
- [x] Plan: M1-M3 / AC / Stopper が計画文書として確定。
- [x] Execute: 編集対象は本ファイルのみ。
- [x] Verify: docs-check（差分確認 + allowlist逸脱ゼロ）で判定可能。
- [x] Gate: `A1 not done` 前提で Proceed=Hold を維持。

## 受入条件（Delivery Planning完了判定）
- [x] AC-1: 本ファイルが `Status=Open` を維持する（A1未完了時は `Proceed=Hold`）。
- [x] AC-2: Go/Hold/Stop 判定が A1依存・固定値・pending bypass 条件で整合する。
- [x] AC-3: A1未完時運用が `Hold` 固定で、強行Proceed禁止が明示される。
- [x] AC-4: Phase 1..6直列 + 毎Phase Read同期が明示される。
- [x] AC-5: Verify 3回上限と超過時Stopが明示される。
- [x] AC-6: A1未確定項目は Pending参照のみで、確定化しない。

## 検証導線（Verify手順）
1. `rg -n "Status:|Scope:|Related ADR|Phase 1|Phase 2|Phase 3|Phase 4|Phase 5|Phase 6|Proceed=|verifyAttempts|A1 not done|Pending参照" 01_Plans/issues/issue-HIL-RS-02-next-phase-delivery-plan.md`
2. `git diff -- 01_Plans/issues/issue-HIL-RS-02-next-phase-delivery-plan.md`
3. `git status --short` で単一ファイル変更のみを確認。


## Stream H 完結性チェック（他ストリーム非依存）
- [x] 本ファイル単体でマイルストーン/DoD/Stopperが読解可能。
- [x] 実装コード・他Issue編集を前提条件にしない。
- [x] A1依存は read-only 判定式参照のみ（値更新・契約再定義なし）。
- [x] 外部依存が必須化した場合は Proceed=Stop とし、確認要求を起票して停止する。

## Open/Hold判定
- 判定: **Open/Hold（Proceed=Hold運用）**
- 根拠: A1依存Hold固定 + Phase 1..6直列化 + ADR明文化 + Verify上限3回固定。

## Stop条件
- A1固定値不一致（`fixedKeysDiff>0`）
- 承認前提崩壊（pending bypass / unrecorded approval inference / dual-control破綻）
- allowlist外編集
- `verifyAttempts>3`

## Stream A contract-first gate note（2026-05-10）

### Dependency order lock（Stream H non-blocking note）
- 固定順序: `A1 -> A2 -> A3`。
- delivery plan は A1完了まで `Proceed=Hold` を維持し、A2/A3へ `Go` を伝播しない。

### Contract freeze reference（read-only）
- API signatures: `HIL_RS_DECISION_GATE_V1`, `HIL_RS_PATCH_PROPOSAL_V1`, `HIL_RS_APPLY_JUDGEMENT_V1`
- Minimal types: `ApprovalRecordV1`, `GateStatusV1`, `DecisionQueueTransitionV1`
- Audit events: `query|bundle|proposal|apply`

### AC/DoD addendum
- AC-7: A1未完了時に `Open/In Progress` 昇格条件を生成しない。
- DoD-7: mock検証は型・イベント・Hold判定まで、承認確定や契約再定義を含まない。

## Stream H Program orchestration addendum (2026-05-20)

### Integration judgement matrix (Pass / Conditional / Fail)
| 対象 | 判定 | 根拠 | 是正条件 |
|---|---|---|---|
| A1契約固定とHold運用 | Pass | `A1 not done => Proceed=Hold` と固定キーが文書化済み | 継続監査のみ |
| 依存切断（A2/A3 mock先行） | Conditional | 並行準備は可能だが、Go最終判定証跡が未統合 | Program Gateログへ candidate別の証跡統合 |
| MVP Exit統合判定 | Conditional | 判定式とテンプレは定義済み、最新入力の埋め込みが不足 | `PRODUCT-QA-01`/`ENV-CONFIG-DRIFT-01` 最新結果を反映 |

### Critical path update
1. `A1 contract freeze consistency`（継続監査）
2. `PRODUCT-QA-01 gate record refresh`（必須）
3. `ENV-CONFIG-DRIFT-01 E-gate refresh`（必須）
4. `MVP-EXIT Program Gate Decision`（Go/Conditional/No-Go確定）

### Stop/Resume contract
- Stop:
  - 証跡なしでGo判定を確定しようとする。
  - allowlist外編集要求。
  - Verify 3回超過。
- Resume:
  - 最新Gate証跡（candidate/date/reviewer/final decision/escalation）が揃う。
  - Conditional項目の owner/due/re-decision date が記録済み。


## Stream H release-readiness execution note（2026-05-20）

### Phase 1: Read（Readyストリーム出口条件）
- Read対象を `A1固定契約`, `MVP-EXIT Program Gate`, `ENV E-gates` の3系列に限定する。
- 各系列で `date/reviewer/final decision/escalation` を最小証跡キーとして採取する。

### Phase 2: 統合判定フレーム定義
- Delivery plan側の統合判定入力は `Proceed=Hold/Stop` の妥当性検査に限定する。
- `Go` 判定は A1完了 + Program Gate証跡完備の両方が揃った場合のみ許可。

### Phase 3: Plan→Execute→Verify（依存を作らない範囲）
- Plan: 判定式とStopperの固定。
- Execute: 本ファイル内でHold/Stop条件を明文化し、外部ファイル更新を要求しない。
- Verify: allowlist逸脱ゼロ、判定式ドリフトゼロ、Verify上限3回ルール維持。

### Phase 4: Stopper（外部ファイル要求時）
- `PRODUCT-QA-01` または `ENV-CONFIG-DRIFT-01` 本文更新が必須になった時点で `Proceed=Stop`。
- `A1 not done` なのに Goを確定しようとする要求は `pending bypass` として即Stop。

## Stream D delivery plan consolidation（2026-06-13）

### Ordered lane plan
1. A1: 最小I/F契約を Approval Record 付きで Done-ready にする。
2. RS-02-A1: A1固定値を再定義せず、承認例外・held items・future-version隔離を硬化する。
3. A2: Frontend Streamへ read-only contract と Stop条件だけを handoff する。
4. A3: Docs Streamへ同期対象・Open化条件・Stop条件だけを handoff する。
5. Parent Proceed: `pendingDecisionQueueCount==0` と A1/RS-02-A1 の証跡が揃った後にだけ Go 判定する。

### Non-dependent handoff policy
- A2/A3 は他Streamの完了待ちを要求せず、参照契約・mock境界・Stop条件を受け取るだけで準備可能にする。
- mock活用は型、イベント、Hold判定、`executeAllowed=false` の確認に限定する。
- 実装完了や運用文書本文の同期完了を、本delivery plan自体の完了条件にしない。

### Stop conditions
- `Approval Record=Pending` のまま Proceed Go を出す。
- `pendingDecisionQueueCount>0` を無視する。
- A1固定キー、rollbackRef、audit events、riskLabels を下流で再定義する。
- SafeMode後退、auto-apply、AIによる `human_reviewed` 昇格を許可する。
- verifyAttempts が3回を超える。

### Proceed judgement
- 現時点の判定: **Open/Hold**。
- 理由: A1 Done と queue zero の証跡が未成立。A2/A3へは handoff のみ可能で、Go伝播は不可。
