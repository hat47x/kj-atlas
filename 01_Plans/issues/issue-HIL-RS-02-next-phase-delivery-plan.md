# Issue Draft: HIL-RS-02 次フェーズ実行計画

- Type: Process
- Status: Open
- Lifecycle: Draft -> Open -> In Progress -> Done
- Priority: P1
- Source Issue: N/A
- Owner: Architecture Owner (Stream A contracts)
- Scope: `01_Plans/issues/`（planning only）
- Dependencies: `ADR-0027`, `ADR-0026`, `ADR-0028`, `A1 -> A2 -> A3`
- Related ADR/Spec: `ADR-0027`, `ADR-0026`, `00_Prompt/domain.md`
- Expected verification level: `docs-check`

## 1) Objective

HIL-RS-02 を、A1 契約凍結を前提にした実行計画として固定する。

## 2) Governance Baseline（read-only snapshot）

- `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
- `contractIds=A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|A1-ERROR-IF`
- `schemaVersion=1.0.0`
- `overridePolicy=human_dual_control_only`
- `contractLinkLocked=true`
- `sharedResourceFreeze=true`
- `safeModeDefault=ON`
- `unlockRule=a2a3Unlock = (a1Status=="Done" && pendingDecisionQueueCount==0)`
- `decisionQueueTransition=Pending -> Approved | Pending -> Rejected`

## 3) Serial Phase Protocol（強制）

各Phaseは **開始時に対象5ファイルを再読** し、`Plan -> Execute -> Verify -> Proceed` を順に実施する。

### Phase 1: Read & Baseline（2026-04-21）
- Plan: `Status / Priority / Dependencies / AC / DoD` 比較軸を固定。
- Execute: 5ファイルの固定値・依存順序・停止条件を照合。
- Verify: `DiffCount=0`。
- Proceed: 差分検知時は Plan 更新を先行。

### Phase 2: Plan（合意済み）
- Plan: `A1 -> A2 -> A3`、unlockRule、decisionQueueTransition、NoGo return path を SSOT へ収束。
- Execute: ACにDecision Queue固定遷移、DoDにA1差戻し固定、Verifyに依存矛盾ゼロを明示。
- Verify: 判定式・語彙の揺れがない。
- Proceed: CDC必要時は Phase 3。

### Phase 3: ADR CDC Gate
- Plan: ADR改訂要否を判定。
- Execute: 契約整合化のみでADR変更なし。
- Verify: 承認待ちCDCなし。
- Proceed: Phase 4。

### Phase 4: Execute
- Plan: 契約ID・凍結キー・停止条件を統一。
- Execute: A1唯一ゲート、Pending bypass禁止、NoGo時A1差戻しを統一記述。
- Verify: AC diff check=0、DoD consistency=OK。
- Proceed: Phase 5。

### Phase 5: Verify
- Plan: docs-check観点を固定。
- Execute: `docs-check` と `git diff --check`。
- Verify: 失敗時self-correctionは最大3回。
- Proceed: Pass時のみ Phase 6。

### Phase 6: Proceed（handoff）
- handoff固定値: `freezeContractId / contractIds / schemaVersion / overridePolicy / contractLinkLocked / sharedResourceFreeze / safeModeDefault`
- handoff禁止遷移: `A1!=Done で A2/A3 Open` / `Pending bypass` / `NoGo時のA1以外差し戻し`
- handoff差戻し先: `issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`

## 4) Acceptance Criteria / DoD

### Acceptance Criteria

- `schemaVersion / overridePolicy / unlockRule / decisionQueueTransition / safeModeDefault` の差分が 0 件。
- A2/A3 開放条件が `A1 Done + pendingDecisionQueueCount==0` で固定。
- Decision Queue が `Pending -> Approved | Pending -> Rejected` に固定。

### DoD

- Go/No-Go 判定式が単一化される。
- 差し戻し先が A1 に固定される。
- 未承認事項は `Pending/held` のまま維持される。

## 5) A2/A3 Start Rule（固定）

- `A2A3StartAllowed = (a1Status=="Done" && pendingDecisionQueueCount==0 && schemaVersion=="1.0.0" && overridePolicy=="human_dual_control_only" && contractLinkLocked==true && sharedResourceFreeze==true && validatorPass==true)`
- `Go = A2A3StartAllowed`
- `A1未完了時A2/A3 Open禁止 = (a1Status!="Done") => Open禁止`
- `NoGo = !A2A3StartAllowed`
- `NoGo return path = issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`

## 6) ADR Rule

- ADR追加/改訂が必要な場合のみ、実装前に `Context / Decision / Consequences` を Draft 起案。
- 人間承認が明示されるまで確定扱い禁止。
- 現時点判定: 契約整合化のみのため新規 ADR 起案なし。

## 7) Stop Conditions / Fail-safe

- 固定値ドリフト検出
- `Pending bypass` 要求
- Self-Correction 3回超過
- 前提崩壊 / 未定義競合
- 指定外ファイル編集要求または検知

## 8) Stream A Phase Execution Log（2026-04-21）

### Phase 1: Read（Plan -> Execute -> Verify -> Proceed）

- Plan:
  - 対象5ファイル（RS-01 umbrella/A1、RS-02 umbrella/A1/A3）を再読し、`Context / Decision / Consequences` と固定I/Fの未整合を抽出する。
- Execute:
  - 5ファイルの契約キー（`freezeContractId / contractIds / schemaVersion / overridePolicy / contractLinkLocked / sharedResourceFreeze / safeModeDefault / unlockRule / decisionQueueTransition`）を照合。
  - `A1 -> A2 -> A3` 依存順序と `A1!=Done で A2/A3 Open禁止` の記述有無を確認。
- Verify:
  - 固定I/F（Freeze Pack ID / Contract IDs / schemaVersion / overridePolicy）の文書間差分は **0件**。
  - 未整合（文脈整合）を1件検出:
    1. `issue-HIL-RS-02-A2-frontend-reversible-synthesis-application.md` は `Status: Done` だが、A1は `Open` のため、統治契約（A1完了前のA2/A3 Open禁止）との解釈差分が残る。
- Proceed:
  - 固定キーの再定義は不要。追加意思決定が必要なため Phase 2 へ進行。

### Phase 2: ADR明文化（追加意思決定が必要な項目のみ）

#### ADR Draft（Pending）: `HIL-RS-02-GOV-EXCEPTION-01`

- Context:
  - 契約は `A1 -> A2 -> A3` と `A1!=Done で A2/A3 Open禁止` を固定している。
  - 一方で現況は A1=`Open`、A2=`Done` であり、記録上は契約順序と整合しない。
- Decision（Pending / 未確定）:
  - A2完了扱いを「契約確定前の先行実施（grandfathered）」として許容するか、A1完了まで `Done -> Open(hold)` へ戻すかを人間Deciderが判定する。
- Consequences:
  - 許容する場合: 実績連続性は維持されるが、将来の統治判定に例外運用が残る。
  - 戻す場合: 契約一貫性は向上するが、進捗指標と履歴差分の調整コストが発生する。

### Phase 3: 契約凍結照合（Freeze）

- Freeze Pack ID: `HIL-RS-02-A1-CONTRACT-FREEZE-v1`（一致）
- Contract IDs: `A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|A1-ERROR-IF`（一致）
- `schemaVersion=1.0.0`（一致）
- `overridePolicy=human_dual_control_only`（一致）
- 結果: 固定I/F差分 **0件**（契約値は凍結維持）。

### Phase 4: 検証（docs-check + 参照整合）

- 実行:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
  - `python3 -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `git diff --check`
- Self-Correction:
  - 0回（失敗なし）。

### Phase 5: Proceed 判定

- 状態宣言: **Needs-decision**
- 失敗条件:
  - `HIL-RS-02-GOV-EXCEPTION-01` 未判定のまま A3 を `Draft -> Open` へ遷移させること。
- 影響I/F:
  - `A1 -> A2 -> A3` 開放判定式
  - `NoGo return path = issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`
- 必要な人間判断:
  1. A2の現 `Done` を例外承認するか（grandfathered）。
  2. 例外不承認の場合、A2ステータスを `Open(hold)` 相当へ戻すか。

## 9) Decision Queue（Pending）

- `HIL-RS-02-GOV-EXCEPTION-01`
  - Status: Pending
  - Owner: Project Maintainers（Deciders）
  - Due: 次回 HIL-RS 合同レビュー
  - Blocking:
    - A3 `Draft -> Open` 判定
    - HIL-RS-02 の Ready 宣言
