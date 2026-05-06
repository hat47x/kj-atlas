# Issue Draft: HIL-RS-02 Next-Phase Delivery Plan（Stream F planning lane）

- Type: Process
- Status: Draft
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P1
- Owner: Stream F Agent（delivery plan + A3 ops sync preflight）
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

## Stream F Execution Protocol（固定）
- Required order: **Read → ADR(C/D/C) → Plan → Execute → Verify → Proceed**
- Verify repair limit: `<=3`（4回目相当は即停止）
- Hard stop: safeMode後退要求 / 契約ID再定義要求 / pending bypass / allowlist外編集要求

## Phase-Read
### Plan
- allowlist対象2ファイルを再読し、未決事項を `approval pending` / `dependency pending` / `drift risk` に分類する。
### Execute
- A1依存の未決事項を固定: `Approval Record未充足`, `A1 Done未達`, `A3 Open gate未達`。
### Verify
- 3分類が後続フェーズの判定式に接続されていること。
### Proceed
- Proceed=Yes

## Phase-ADR（Context / Decision / Consequences）
### Plan
- ADR-0027/0028と2 issue の C/D/C 粒度を揃え、A3を契約再定義ノードにしない方針を固定する。
### Execute
- Context: A1依存下でA2/A3を先行確定すると統治ドリフトを招く。
- Decision: Stream Fは「契約参照固定 + delivery里程標固定 + docs sync条件固定」に限定する。
- Consequences: **A1 DoneまでA3はDraft維持（Open化禁止）**。
### Verify
- C/D/C が2ファイルで欠落なく整合していること。
### Proceed
- Proceed=Yes（Approval Pending注記維持）

## Phase-Plan
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

## Phase-Execute
### Plan
- A3運用同期の前倒し準備を実施しつつ、A1依存はread-onlyで扱う。
### Execute
- A3準備は `用語同期`, `同期導線`, `検証ログ要件` の論点整理に限定。
- `A1 Done未達時はA3 Open化を禁止` を明示維持。
### Verify
- 実装コード/04_Documentation本体未編集、allowlist内更新のみであること。
### Proceed
- Proceed=Yes

## Phase-Verify
### Plan
- DOC-OPS-02の4観点で横断ドリフトを検証する。
### Execute
- Check-1: 用語一致（Security Officer / System Owner / Platform Operator）
- Check-2: 2者承認 + 実行責務分離
- Check-3: 相互リンク導線（`02_Architecture -> 04_Documentation -> 01_Plans -> AGENTS.md`）
- Check-4: 固定値不変（D1〜D4相当）
### Verify
- 4観点に矛盾がないこと。
### Proceed
- Proceed=Hold（A1完了待ち）

## Phase-Proceed（Gate）
- Proceed(Go): `A1 Done && pendingDecisionQueueCount==0 && fixedKeysDiff==0`
- Proceed(Hold): `A1 not done && fixedKeysDiff==0`
- Proceed(Stop): `fixedKeysDiff>0 || pending bypass || unrecorded approval inference || scope violation`
- Current decision: **Hold**（A1依存未解消）
