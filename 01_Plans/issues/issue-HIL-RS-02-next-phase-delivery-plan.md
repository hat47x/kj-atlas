# Issue Draft: HIL-RS-02 Next-Phase Delivery Plan（Stream G planning lane）

- Type: Process
- Status: Ready
- Lifecycle: Draft -> Ready -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P1
- Owner: Stream G Agent（A3 preflight準備レーン）
- Scope: `01_Plans/issues/issue-HIL-RS-02-next-phase-delivery-plan.md`, `01_Plans/issues/issue-HIL-RS-02-A3-operations-documentation-sync.md`
- Out of scope: allowlist外のIssue/ADR編集、`03_Implement/**`、`04_Documentation/**`、実装コード編集
- Related ADR/Spec: `ADR-0026`, `ADR-0027`, `ADR-0028`
- Dependencies (read-only): `ADR-0026`, `ADR-0028`, `issue-HIL-RS-02-A1-governance-contract-hardening.md`
- Expected verification level: `docs-check`

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

## Stream G Execution Protocol（固定）
- Required order: **Phase 1 Read → Phase 2 Plan（A1完了前提ゲート明文化）→ Phase 3 Execute（準備項目・受入条件先行定義）→ Phase 4 Verify（整合検証・修復上限3回）→ Phase 5 Stopper（A1未完了のまま実装へ進まない）**
- Verify repair limit: `<=3`（4回目相当は即停止）
- Hard stop: safeMode後退要求 / 契約ID再定義要求 / pending bypass / allowlist外編集要求

## Phase 1 Read
### Plan
- allowlist対象2ファイルを再読し、未決事項を `approval pending` / `dependency pending` / `drift risk` に分類する。
### Execute
- A1依存の未決事項を固定: `Approval Record未充足`, `A1 Done未達`, `A3 Open gate未達`。
### Verify
- 3分類が後続フェーズの判定式に接続されていること。
### Proceed
- Proceed=Yes

## Phase 2 Plan（A1完了前提のゲート明文化）
### Plan
- ADR-0027/0028と2 issue の C/D/C 粒度を揃え、A3を契約再定義ノードにしない方針を固定する。
### Execute
- Context: A1依存下でA2/A3を先行確定すると統治ドリフトを招く。
- Decision: Stream Gは「契約参照固定 + delivery里程標固定 + docs sync条件固定」に限定する。
- Consequences: **A1 DoneまでA3はDraft維持（Open化禁止）**。
### Verify
- C/D/C が2ファイルで欠落なく整合していること。
### Proceed
- Proceed=Yes（Approval Pending注記維持）

## Phase 3 Execute（準備項目・受入条件の先行定義）
### Plan
- 里程標（M1-M3）と AC/DoD を実行可能粒度で確定する。
### Execute
- M1: 契約固定値・依存式一致確認
- M2: Gate判定（Go / Hold / Stop）固定
- M3: Verify証跡（validator/unittest/diff）記録
### Verify
- AC/DoD不足提案を含め、修復サイクルが最大3回で収束可能であること。
### Proceed
- Proceed=Yes

## Phase 4 Execute
### Plan
- A3運用同期の前倒し準備を実施しつつ、A1依存はread-onlyで扱う。
### Execute
- A3運用同期準備は `用語同期`, `同期導線`, `検証ログ要件` の論点整理に限定。
- `A1 Done未達時はA3 Open化を禁止` を明示維持。
### Verify
- 実装コード/04_Documentation本体未編集、allowlist内更新のみであること。
### Proceed
- Proceed=Yes

## Phase 5 Stopper（A1未完了のまま実装へ進まない）
### Plan
- 整合検証結果を受けてStopper条件を最終固定し、A1未完了時の実装移行を遮断する。
### Execute
- Stopper-1: `A1 not done` の間は実装作業に進まない。
- Stopper-2: `fixedKeysDiff>0 || pending bypass || unrecorded approval inference || scope violation` は即Stop。
- Stopper-3: `Proceed=Hold` を継続し、Open化・In Progress化を禁止。
### Verify
- Stopper条件と受入条件（AC-1〜AC-4）が整合し、修復サイクルが3回以内で収束すること。
### Proceed
- Proceed=Hold（A1完了待ち）

## Draft解除条件（Draft -> Ready）
- [x] Scope/Out of scope が allowlist 2ファイルに限定されている。
- [x] 固定契約値（freezeContractId / schemaVersion / safeMode / decisionQueueTransition）が明示され、再定義禁止が明記されている。
- [x] A1依存を read-only とし、`A1 Done未達時はA3 Open禁止` が明記されている。
- [x] Proceed判定式（Go/Hold/Stop）が定義済みで、Current decision が Hold と整合している。
- [x] Verify 4観点（用語・役割分離・導線・固定値）が列挙されている。

## Ready定義（実行開始条件）
- [x] Plan: 里程標 M1-M3 と AC/DoD補完方針が確定。
- [x] Execute: planning記述のみを更新対象とし、実装コード/04_Documentation本体を編集しない。
- [x] Verify: docs-check（差分確認 + allowlist逸脱ゼロ）で判定可能。
- [x] Gate: `A1 not done` 前提で Proceed=Hold を維持し、Open化は人手承認ログ待ち。

## 依存切断条件（Ready維持のための独立性）
- [x] A1成果物本文を参照専用に固定し、Stream G側で契約キーを書き換えない。
- [x] A3運用同期準備は「用語同期 / 導線固定 / 検証証跡設計」の3点に限定し、A1完了を待たずに継続可能。
- [x] 依存未解消でも Stop ではなく Hold で滞留できるよう判定式を固定。

## 受入条件（Execute完了判定）
- [ ] AC-1: 2ファイルとも Status=Ready で、Draft解除条件セクションを保持。
- [ ] AC-2: Go/Hold/Stop 式が同一ロジック（fixedKeysDiff/pending bypass/A1 Done）で整合。
- [ ] AC-3: A1未完時の運用は `Hold` 固定で、Open化禁止が明示される。
- [ ] AC-4: Verify 4観点が両ファイルで欠落なく記載される。

## 検証導線（Verify手順）
1. `rg -n "Status:|Lifecycle:|Draft解除条件|Ready定義|依存切断条件|Proceed\(|Current" 01_Plans/issues/issue-HIL-RS-02-next-phase-delivery-plan.md 01_Plans/issues/issue-HIL-RS-02-A3-operations-documentation-sync.md`
2. `git diff -- 01_Plans/issues/issue-HIL-RS-02-next-phase-delivery-plan.md 01_Plans/issues/issue-HIL-RS-02-A3-operations-documentation-sync.md`
3. `git status --short` で allowlist外変更がないことを確認。

## Ready判定
- 判定: **Ready（Proceed=Hold運用）**
- 根拠: Draft解除条件充足 + A1依存をHoldへ正規化 + fixed key再定義なし。


## Stop条件（Prompt G適用）
- A1固定値不一致（`fixedKeysDiff>0`）
- 共有資源競合（`sharedResourceFreeze`違反、または共有資源の二重更新要求）
- 承認前提崩壊（pending bypass / unrecorded approval inference / dual-control破綻）
