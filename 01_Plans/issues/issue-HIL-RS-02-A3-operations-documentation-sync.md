# Issue Draft: HIL-RS-02 A3 Operations Documentation Sync（Stream C）

- Type: Process
- Status: Draft
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: `01_Plans/issues/issue-HIL-RS-02-next-phase-delivery-plan.md`
- Priority: P1
- Owner: Stream C（operations sync lane）
- Scope: `01_Plans/issues/issue-HIL-RS-02-A3-operations-documentation-sync.md`（docs planning only）
- Out of scope: 実装変更、allowlist外Issue/ADR編集
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

## Stream C Execution Discipline
- Per phase mandatory: **Plan → Execute → Verify → Proceed**
- Self-correction: `<=3`
- Hard stop: pending bypass / fixed key rewrite / safeMode後退 / scope外編集

## Phase 1: Read
### Plan
- A3の役割を「運用同期準備」に限定し、未決事項を抽出する。
### Execute
- 未決事項: `Approval Record pending`, `A1未完`, `Open gate未達`。
### Verify
- 未決事項を gate 判定式へ接続済みであること。
### Proceed
- Proceed=Yes

## Phase 2: ADR整合（C/D/C）
### Plan
- ADR-0027の統治制約とA3本文を一致させる。
### Execute
- Context: A3は契約再定義ノードではない。
- Decision: mock I/F preparation only を維持。
- Consequences: A1完了前は Draft維持、Open化不可。
### Verify
- C/D/C 欠落なし。
### Proceed
- Proceed=Yes（Pending注記維持）

## Phase 3: Delivery里程標
### Plan
- A3側の里程標を運用同期観点で固定。
### Execute
- M1: 用語同期（Security Officer / System Owner / Platform Operator）
- M2: 同期導線固定（02_Architecture → 04_Documentation → 01_Plans → AGENTS.md）
- M3: Gateログ・検証証跡の記録
### Verify
- 里程標がAC/DoDに接続されること。
### Proceed
- Proceed=Yes

## Phase 4: 運用文書同期条件（責務分離・リンク）
### Plan
- AUTH-OPS-03 / DOC-OPS-02 の横断ドリフト観点を固定する。
### Execute
- Check-1 用語一致（3ロール）
- Check-2 2者承認 + 実行責務分離
- Check-3 相互リンク導線
- Check-4 固定値（D1-D4相当）の不変
### Verify
- 4観点に不整合がないこと。
### Proceed
- Proceed=Conditional（A1完了待ち）

## Phase 5: Verify（AC/DoD + conflict zero）
### Plan
- docs-check と allowlist差分確認を実施。
### Execute
- `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- `python3 -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
- `rg -n "^- Scope:|^- Dependencies:|^- Expected verification level:" 01_Plans/issues/issue-HIL-RS-02-A3-operations-documentation-sync.md`
- `git diff --check`
### Verify
- AC:
  - AC-1: 5フェーズ定義あり
  - AC-2: Plan/Execute/Verify/Proceedを全フェーズで保持
  - AC-3: Open gateがA1依存で固定
  - AC-4: hard stop と self-correction 条件明記
- DoD:
  - DoD-1: docs-only
  - DoD-2: fixed keys drift=0
  - DoD-3: NoGo return path固定
  - DoD-4: conflict zero（allowlist外差分なし）
### Proceed
- Go: `A1 Done && pendingDecisionQueueCount==0 && validatorPass`
- Conditional: `A1 not done && fixedKeysDiff==0 && validatorPass`
- No-Go: 上記以外（hard stop含む）
- **Current: Conditional**
