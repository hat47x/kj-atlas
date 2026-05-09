# Issue Draft: HIL-RS-02 Next-Phase Delivery Plan（Stream F planning lane）

- Type: Process
- Status: Ready
- Lifecycle: Draft -> Ready -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P1
- Owner: Stream F Agent（delivery plan 計画整理専任）
- Scope: `01_Plans/issues/issue-HIL-RS-02-next-phase-delivery-plan.md` のみ
- Out of scope: 上記以外すべてのファイル編集、`03_Implement/**`、`04_Documentation/**`、実装コード編集
- Related ADR/Spec（明文化必須）: `ADR-0026`, `ADR-0027`, `ADR-0028`
- Dependencies (read-only): `issue-HIL-RS-02-A1-governance-contract-hardening.md`（A1）
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

## Stream F Execution Protocol（固定）
- Required order: **Phase 1 Read同期 → Phase 2 Plan同期 → Phase 3 Plan同期 → Phase 4 Plan同期 → Phase 5 Plan同期 → Phase 6 Stop同期**（直列、並列禁止）
- Every phase rule: 各Phaseは先頭で必ず Read同期（依存・固定値・A1状態確認）を行ってから Plan/Execute/Verify に進む。
- A1 gate rule: **A1未完了時は Proceed=Hold を維持し、強行Proceedは禁止。**
- Verify repair limit: `<=3`（3回で収束しない場合は `Stop`）
- Hard stop: safeMode後退要求 / 契約ID再定義要求 / pending bypass / allowlist外編集要求 / Verify上限超過

## Phase 1 Read同期（基準固定）
### Plan
- `ADR-0026/0027/0028` と A1依存を再読し、判断材料を `approval pending` / `dependency pending` / `drift risk` に分類する。
### Execute
- A1依存の現状を `A1 not done` 前提で固定し、以降Phaseのゲート前提へ接続する。
### Verify
- 3分類が後続Phase 2〜6の判定式に接続され、A1完了前提の誤記がないこと。
### Proceed
- Proceed=Hold（A1完了待ち）

## Phase 2 Plan同期（ADR整列）
### Plan
- delivery plan本文の判断根拠を `ADR-0026/0027/0028` に明示リンクし、契約再定義を行わない方針を固定する。
### Execute
- Decision: Stream Fは「計画整理のみ」「契約参照固定」「A1 read-only」の3点を維持する。
### Verify
- ADR参照が欠落なく記載され、A1未完了下でのOpen化許可文が存在しないこと。
### Proceed
- Proceed=Hold

## Phase 3 Plan同期（マイルストーン定義）
### Plan
- M1〜M3を計画文書内で定義し、実装着手条件と分離する。
### Execute
- M1: 固定契約値とA1依存式の一致確認
- M2: Gate判定（Go/Hold/Stop）をA1依存で固定
- M3: Verify証跡（diff/status/docs-check）を記録
### Verify
- 各マイルストーンが「計画整理のみ」の範囲に収まり、他ファイル編集を要求しないこと。
### Proceed
- Proceed=Hold

## Phase 4 Plan同期（受入条件/DoD整備）
### Plan
- AC/DoDをA1未完了運用に整合させ、Hold継続を前提化する。
### Execute
- AC群へ「A1 not done時はHold維持」「Open/In Progress化禁止」を明記。
### Verify
- AC/DoDがGo条件と矛盾せず、A1完了前の強行遷移条件を含まないこと。
### Proceed
- Proceed=Hold

## Phase 5 Plan同期（検証運用）
### Plan
- Verify手順を3回上限で運用する規則に更新し、超過時Stopを明示する。
### Execute
- Verify trial counter を `1..3` に固定し、`trial=4` は実施せず即Stopとする。
### Verify
- 本文に「Verify 3回上限、超過時Stop」が明記され、例外条項がないこと。
### Proceed
- Proceed=Hold

## Phase 6 Stop同期（最終ゲート固定）
### Plan
- A1未完了時の最終判定をHold固定で閉じ、強行Proceed経路を除去する。
### Execute
- Stopper-1: `A1 not done` の間は `Proceed=Hold` 維持。
- Stopper-2: `fixedKeysDiff>0 || pending bypass || unrecorded approval inference || scope violation` は即Stop。
- Stopper-3: `verifyAttempts>3` は即Stop。
### Verify
- Hold/Stop判定がPhase 1〜5と矛盾せず、GoはA1完了時のみ可能であること。
### Proceed
- Proceed=Hold（A1完了待ち）

## Draft解除条件（Draft -> Ready）
- [x] Scope が単一ファイル（本ファイル）のみに限定されている。
- [x] 固定契約値（freezeContractId / schemaVersion / safeMode / decisionQueueTransition）が明示され、再定義禁止が明記されている。
- [x] A1依存を read-only とし、`A1 not done => Proceed=Hold` が明記されている。
- [x] Phase 1..6 直列と、毎Phase Read同期が定義されている。
- [x] Verify 3回上限と超過時Stopが明記されている。
- [x] ADR-0026/0027/0028 の明文化参照がある。

## Ready定義（実行開始条件）
- [x] Plan: M1-M3 / AC / Stopper が計画文書として確定。
- [x] Execute: 編集対象は本ファイルのみ。
- [x] Verify: docs-check（差分確認 + allowlist逸脱ゼロ）で判定可能。
- [x] Gate: `A1 not done` 前提で Proceed=Hold を維持。

## 受入条件（Execute完了判定）
- [x] AC-1: 本ファイルが Status=Ready を維持する。
- [x] AC-2: Go/Hold/Stop 判定が A1依存・固定値・pending bypass 条件で整合する。
- [x] AC-3: A1未完時運用が `Hold` 固定で、強行Proceed禁止が明示される。
- [x] AC-4: Phase 1..6直列 + 毎Phase Read同期が明示される。
- [x] AC-5: Verify 3回上限と超過時Stopが明示される。

## 検証導線（Verify手順）
1. `rg -n "Status:|Scope:|Related ADR|Phase 1|Phase 2|Phase 3|Phase 4|Phase 5|Phase 6|Proceed=|verifyAttempts|A1 not done" 01_Plans/issues/issue-HIL-RS-02-next-phase-delivery-plan.md`
2. `git diff -- 01_Plans/issues/issue-HIL-RS-02-next-phase-delivery-plan.md`
3. `git status --short` で単一ファイル変更のみを確認。

## Ready判定
- 判定: **Ready（Proceed=Hold運用）**
- 根拠: A1依存Hold固定 + Phase 1..6直列化 + ADR明文化 + Verify上限3回固定。

## Stop条件
- A1固定値不一致（`fixedKeysDiff>0`）
- 承認前提崩壊（pending bypass / unrecorded approval inference / dual-control破綻）
- allowlist外編集
- `verifyAttempts>3`
