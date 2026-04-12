# Issue Draft: HIL-RS-02 次フェーズ実行計画

- Type: Process
- Status: Open
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P1
- Owner: Plan Owner (Stream B)
- Scope: `01_Plans/issues/`（planning only）
- Dependencies: `ADR-0027`, `ADR-0026`, `ADR-0028`, `issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`
- Related ADR/Spec: `ADR-0027`, `ADR-0026`, `00_Prompt/domain.md`
- Expected verification level: `docs-check`

## 1) Objective

議論→決定→文書化→同期サイクルを、A1契約固定を前提に **状態遷移契約で運用可能** な計画として固定する。

## 2) Governance Baseline（Mock Contract Snapshot参照）

- Snapshot ID: `MOCK-CONTRACT-SNAPSHOT-HIL-RS-v1`
- A2/A3 Open条件: `A1 Done && pendingDecisionQueueCount==0`
- 許可遷移: `Pending -> Approved|Rejected`
- 禁止遷移: Pending bypass / A1未完了でのA2/A3 Open
- 固定識別子:
  - `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
  - `schemaVersion=1.0.0`
  - `overridePolicy=human_dual_control_only`
  - `contractLinkLocked=true`
  - `sharedResourceFreeze=true`

## 3) ADR CDC（Phase 2）

- Context:
  - HIL-RS-02はA1契約を運用へ接続するフェーズ。
- Decision:
  - 依存は状態遷移として記述し、A1/A2/A3の実装待ちで計画を停止しない。
- Consequences:
  - 契約差分はA1へ集約。A2/A3では契約値を変更しない。

## 4) Acceptance Criteria / DoD

- [x] CDCが明文化されている。
- [x] Gate条件が機械判定可能な式で示されている。
- [x] Decision Queueの許可/禁止遷移が明示されている。
- [x] 安全境界（SafeMode/share-export/human_dual_control_only）後退禁止が明示されている。
- [x] Proceed（Open化）条件と停止条件が明示されている。

## 5) Serial Phases（各Phase開始時に対象再Read）

### Phase 1 Read
- 対象5 issueのStatus/Dependencies/識別子を再確認。

### Phase 2 ADR CDC
- Context/Decision/Consequencesを確認。上位ADR改定必要時は停止。

### Phase 3 Plan
- AC/DoD不足を補完し、遷移契約を固定。

### Phase 4 Execute
- issue本文に契約・禁止遷移・差し戻し先を同期。

### Phase 5 Verify
- validator + rg + diff確認。自己修復は最大3回。

### Phase 6 Proceed
- Open化条件を満たす項目のみ進行。未確定はDecision Queueへ戻す。

## 6) Open化条件（明文化）

1. `A1 Done`
2. `pendingDecisionQueueCount==0`
3. Mock snapshot固定識別子が一致
4. 安全境界の後退要求がない

## 7) Fail-safe

- 停止トリガー: 3回修復超過 / 未承認確定化 / 識別子不一致。

## 8) Stream F update (2026-04-12, planning memo only)

### Phase 1) Read同期
- Re-read HIL-RS-02 parent/child memos and confirmed dependency chain remains `A1 -> A2 -> A3`.

### Phase 2) A1/A2/A3依存 + Decision Queue更新
| QueueID | Topic | Status | Resolution |
| --- | --- | --- | --- |
| `DQ-HIL-RS-02-001` | A1 completion gate | Closed | `A1 Done` is mandatory before A2/A3 Open |
| `DQ-HIL-RS-02-002` | Pending decision bypass prevention | Closed | bypass forbidden; unresolved items block Proceed |
| `DQ-HIL-RS-02-003` | Contract-ID/lock-value drift | Closed | drift => return to A1, no local override |

### Phase 3) AC/DoD不足補完
- Added explicit DoD checkpoint: Proceed requires `A1 Done && pendingDecisionQueueCount==0 && no safety downgrade request`.
- Added hold behavior: if any queue reopens, phase state must return to `Plan` and re-run CDC check.
- Locked unlock expression as the sole gate for A2/A3 Open: `A1 Done && pendingDecisionQueueCount==0`.
- Locked decision progression: unresolved `Pending` items block Proceed without exception (pending bypass prohibited).

### Phase 4) docs-check
- Single source command: `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`.
- Retry policy fixed: max 3 corrections then stop.

### Phase 5) 次レーンhandoff
- Handoff payload (planning) = `{freezeContractId, schemaVersion, overridePolicy, queueSnapshot, proceedDecision}`.
- A2/A3 lanes are limited to consume payload; they cannot mutate freeze contract values.

## Stream A Critical Path Fixpoint (2026-04-12)

### Phase 1: Read（最新再読 + 未確定抽出）
- 未確定I/F: `なし`（固定対象は `CE0-CTX-IF` / `CE0-SAFEMODE-IF` / `CE0-REVIEW-IF` / `CG-01..05` / `A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|A1-ERROR-IF`）。
- 未確定責務: `なし`（A1は契約凍結の唯一正本、A2/A3はread-only参照）。
- 未確定ゲート: `なし`（唯一ゲートは `A1 Done && pendingDecisionQueueCount==0`）。

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
- 判定条件固定: `Go = (A1 Done && pendingDecisionQueueCount==0 && schemaVersion==1.0.0 && overridePolicy==human_dual_control_only && contractLinkLocked==true && sharedResourceFreeze==true)`。
- 停止条件固定: Query Preview bypass / direct write / auto-apply / review自動昇格 / SafeMode後退 / Self-Correction 3回超過。

### Phase 5: Verify -> Proceed
- Verify: docs-checkで契約ID整合・語彙整合・安全後退0件を確認し、不一致時はSelf-Correction最大3回まで。
- Proceed条件（1行）: `Proceed = (collision==0 && vocabularyDrift==0 && safeModeRegression==0 && A1 Done && pendingDecisionQueueCount==0)`。

### Fail-safe（停止報告テンプレ）
- 失敗条件:
- 影響範囲（ファイル/契約ID）:
- 人間判断が必要な選択肢（2案）:
  - 案1: 契約固定値を維持し、差分要求をA1へ差し戻す。
  - 案2: 契約固定値の変更を承認会議へエスカレーションし、承認後に再凍結する。
