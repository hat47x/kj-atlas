# Issue Draft: HIL-RS-02 A3 Operations Documentation Sync（Stream F preflight）

- Type: Process
- Status: Draft
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: `01_Plans/issues/issue-HIL-RS-02-next-phase-delivery-plan.md`
- Priority: P1
- Owner: Stream F（operations sync planning preflight lane）
- Scope: `01_Plans/issues/issue-HIL-RS-02-A3-operations-documentation-sync.md`（docs planning only）
- Out of scope: 実装変更、allowlist外Issue/ADR編集、契約再定義、`04_Documentation/**` 本体編集
- Related ADR/Spec: `ADR-0027`, `ADR-0028`, `02_Architecture/strict_mode_exception_approval_flow.md`
- Dependencies: `issue-HIL-RS-02-A1-governance-contract-hardening.md`（A1完了必須）, `ADR-0027`, `ADR-0028`
- Expected verification level: `docs-check`

## Contract Freeze Reference（read-only）
- `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
- `contractIds=A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|A1-ERROR-IF`
- `schemaVersion=1.0.0`
- `overridePolicy=human_dual_control_only`
- `contractLinkLocked=true`
- `sharedResourceFreeze=true`
- `safeModeDefault=ON`
- `safeModeBoundary=SAFE_MODE_STRICT_ON`
- `decisionQueueTransition=Pending -> Approved | Pending -> Rejected`

## Stream F Protocol
- Required order: **Read → ADR(C/D/C) → Plan → Execute → Verify → Proceed**
- Verify repair loop: `<=3`
- Hard stop: pending bypass / fixed key rewrite / safeMode後退 / scope外編集

## Read
### Plan
- 対象2ファイルを再読し、A3 roleを「運用同期準備」に限定する。
### Execute
- 未決事項: `Approval Record pending`, `A1未完`, `Open gate未達`。
### Verify
- 未決事項が gate 判定式へ接続済みであること。
### Proceed
- Proceed=Yes

## ADR（C/D/C）
### Plan
- ADR-0027統治制約とA3本文を一致させる。
### Execute
- Context: A3は契約再定義ノードではない。
- Decision: `mock I/F preparation only` を維持し、契約変更要求を拒否する。
- Consequences: **A1 DoneまではDraft固定（Open化禁止）**。
### Verify
- C/D/C欠落なし、かつ「契約再定義しない」方針が明文化済み。
### Proceed
- Proceed=Yes（Pending注記維持）

## Plan
### Plan
- A3里程標を運用同期観点で固定し、AC/DoD不足を提案する。
### Execute
- M1: 用語同期（Security Officer / System Owner / Platform Operator）
- M2: 同期導線固定（`02_Architecture -> 04_Documentation -> 01_Plans -> AGENTS.md`）
- M3: Gateログ・検証証跡の記録
### Verify
- 里程標がAC/DoDへ接続され、修復は3回以内であること。
### Proceed
- Proceed=Yes

## Execute
### Plan
- A3前倒し準備を行うが、A1依存解消までは状態遷移を行わない。
### Execute
- 変更はplanning記述のみ。`A1 Done未達時のA3 Open禁止` を明記維持。
### Verify
- allowlist内更新のみ、実装コード/04_Documentation本体は未変更であること。
### Proceed
- Proceed=Yes

## Verify
### Plan
- DOC-OPS-02横断ドリフト4観点を確認する。
### Execute
- Check-1 用語一致（3ロール）
- Check-2 2者承認 + 実行責務分離
- Check-3 相互リンク導線
- Check-4 固定値（D1-D4相当）の不変
### Verify
- 4観点に不整合がないこと。
### Proceed
- Proceed=Hold（A1完了待ち）

## Proceed（Gate）
- Go: `A1 Done && pendingDecisionQueueCount==0 && validatorPass`
- Hold: `A1 not done && fixedKeysDiff==0 && validatorPass`
- Stop: `fixedKeysDiff>0 || pending bypass || unrecorded approval inference || hard stop`
- Handover condition: `A1完了確認ログ` 追記まで Draft維持。
- Current: **Hold**
