# Issue Draft: HIL-RS-02 Next-Phase Delivery Plan（Stream E docs planning）

- Type: Process
- Status: Draft
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P1
- Owner: Stream E Agent（delivery plan + A3 ops sync docs planning）
- Scope: `01_Plans/issues/issue-HIL-RS-02-next-phase-delivery-plan.md`, `01_Plans/issues/issue-HIL-RS-02-A3-operations-documentation-sync.md`
- Out of scope: allowlist以外のIssue/ADR編集、`03_Implement/**`、`04_Documentation/**`、実装コード編集
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

## Stream E Serial Protocol（固定）
- Serial phases: **Phase 1 Read → Phase 2 ADR整合（C/D/C）→ Phase 3 Workflow（Plan→Execute→Verify→Proceed）→ Phase 4 Cross-doc drift check → Phase 5 Stopper**
- Mandatory discipline per phase: **Plan → Execute → Verify → Proceed**
- Verify repair limit: `<=3`（4回目相当は即停止）
- Hard stop: safeMode後退要求 / 契約ID再定義要求 / pending bypass / allowlist外編集要求

## Phase 1: Read（A1依存状態の再確認）
### Plan
- 両対象ファイルを各Phase開始時に再読し、未決事項を `Approval pending` / `dependency pending` / `drift risk` に分類する。

### Execute
- 未決事項を次で固定:
  1. `Approval Record` の未充足（`approved_by`, `approved_at`, `evidence`）
  2. `A1 Done` 未達時は A3 Open不可
  3. 固定キー差分検知時は即 `No-Go`

### Verify
- 3分類がPhase 2以降の判定式に反映されること。

### Proceed
- **Proceed=Yes**（未決事項は管理可能）

## Phase 2: ADR整合（Context / Decision / Consequences）
### Plan
- ADR-0027 と issue 2件の C/D/C 記述粒度を揃え、A3は契約再定義しない方針を明文化する。

### Execute
- Context: A1依存下でA2/A3の先行確定は統治ドリフトを生む。
- Decision: Stream Eは「契約参照固定 + delivery里程標固定 + docs sync条件固定」に限定し、**A3は契約再定義ノードではない**。
- Consequences: A1完了前は Conditional 維持、Open化先行を禁止。

### Verify
- Context/Decision/Consequences が2ファイルで欠落なく整合すること。

### Proceed
- **Proceed=Yes（Approval Pending注記を維持）**

## Phase 3: Workflow（Plan→Execute→Verify→Proceed）
### Plan
- 里程標（M1-M3）と AC/DoD を実行可能粒度で確定し、不足があれば提案する。

### Execute
- M1: 契約固定値・依存式の一致確認
- M2: Gate判定（Go / Conditional / No-Go）の文書固定
- M3: Verify証跡（validator/unittest/diff）記録

### Verify
- AC/DoD 不足提案を含め、修復サイクルを最大3回で収束させる。

### Proceed
- **Proceed=Yes（3回超過時はStop）**

## Phase 4: Cross-doc drift check（DOC-OPS-02）
### Plan
- 横断ドリフト検知4観点を固定し、同期順序を明記する。

### Execute
- Check-1: 用語一致（`Security Officer` / `System Owner` / `Platform Operator`）
- Check-2: 2者承認 + 実行責務分離
- Check-3: 相互リンク導線
- Check-4: 固定値不変（D1〜D4相当）

### Verify
- 4観点に矛盾がないこと。

### Proceed
- **Proceed=Conditional**（A1完了待ち）


## Boundary Definition（C/D/C境界の固定）
- Delivery plan boundary: 里程標・Gate判定・承認ログ要件の**計画定義のみ**を扱う。
- A3 planning boundary: 運用文書同期の準備に限定し、**契約再定義ノードにしない**。
- Prohibited: A1契約の再定義、未記録承認の推測補完、A1未完了時のOpen化。

## Approval Log Requirements（記録必須要件）
- `approved_by`: 人間承認者ID（Security Officer/System Ownerのいずれか、2者承認時は両者）。
- `approved_at`: ISO8601 UTC timestamp。
- `evidence`: issue/PR/meeting log の参照URIまたはID。
- `decision`: `Approved` / `Rejected`（`Pending`のまま推測で確定しない）。
- 欠損時判定: いずれか欠損は `Hold`、推測補完は禁止。

## Verification Record（Proceed/Hold/Stop + self-correction）
- self-correction loop upper bound: `<=3`（4回目相当は `Stop`）。
- Proceed: `A1 Done && pendingDecisionQueueCount==0 && fixedKeysDiff==0`
- Hold: `A1 not done && fixedKeysDiff==0`
- Stop: `fixedKeysDiff>0 || pending bypass || unrecorded approval inference || scope violation`
- Current: `Hold`（A1完了待ち）。

## Phase 5: Stopper（前提崩れ時停止）
### Plan
- A1依存・固定キー・pending queue を最終ゲートとして判定する。

### Execute
- Stop条件:
  - A1未完了で A3 Open化を強行する要求
  - 前提崩れ（依存未充足 / 固定キー改変 / hard stop発火）

### Verify
- `Go / Conditional / No-Go` の判定式が維持されること。

### Proceed
- Go: `A1 Done && pendingDecisionQueueCount==0 && fixedKeysDiff==0`
- Hold: `A1 not done && fixedKeysDiff==0`
- Stop: 上記以外（hard stop含む）
- **Current decision: Hold（A1依存未解消のため）**
