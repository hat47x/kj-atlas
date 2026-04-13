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
