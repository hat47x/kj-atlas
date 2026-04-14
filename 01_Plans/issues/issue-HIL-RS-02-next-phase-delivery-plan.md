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
- A2/A3 Open条件: `a1Status=="Done" && pendingDecisionQueueCount==0`
- 許可遷移: `Pending -> Approved` または `Pending -> Rejected`
- 禁止遷移: Pending bypass / A1未完了でのA2/A3 Open
- 固定識別子:
  - `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
  - `contractIds=A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|A1-ERROR-IF`
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

1. `a1Status=="Done"`
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
| `DQ-HIL-RS-02-001` | A1 completion gate | Closed | `a1Status=="Done"` is mandatory before A2/A3 Open |
| `DQ-HIL-RS-02-002` | Pending decision bypass prevention | Closed | bypass forbidden; unresolved items block Proceed |
| `DQ-HIL-RS-02-003` | Contract-ID/lock-value drift | Closed | drift => return to A1, no local override |

### Phase 3) AC/DoD不足補完
- Added explicit DoD checkpoint: Proceed requires `a1Status=="Done" && pendingDecisionQueueCount==0 && no safety downgrade request`.
- Added hold behavior: if any queue reopens, phase state must return to `Plan` and re-run CDC check.
- Locked unlock expression as the sole gate for A2/A3 Open: `a1Status=="Done" && pendingDecisionQueueCount==0`.
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
- 未確定ゲート: `なし`（唯一ゲートは `a1Status=="Done" && pendingDecisionQueueCount==0`）。

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

## Stream C Normalization Update (2026-04-12)

### Scope Contract（本ストリームの独立性）
- Stream C は計画整流化のみを行い、A1を外部完了待ちにしない。
- 本issueで固定するのは「ゲート条件明文化」と「差戻し導線固定」のみ。

### Phase Execution Record（1〜6）
1. **Phase 1 Read**: HIL-RS-01 / HIL-RS-02 / HIL-RS-02-A3 を再読。
2. **Phase 2 ADR明文化（CDC）**: CDCの追加改定不要を確認し、既存Decisionを維持。
3. **Phase 3 Plan**: AC/DoDにA1外部待ち禁止・NoGo条件を反映。
4. **Phase 4 Execute**: 状態遷移判定式を以下の単一式へ固定。
5. **Phase 5 Verify**: docs-check、`git diff --check`、キーワード差分確認を実施。
6. **Phase 6 Proceed**: 条件未充足・曖昧点は質問化して停止。

### State Transition Contract（明確化）
- `Open/Proceed Allowed := (a1Status=="Done" && pendingDecisionQueueCount==0)`
- `Hold/NoGo := (A1!=Done || pendingDecisionQueueCount>0)`
- Pending bypass は例外なく禁止。
- 契約値差分はA1へ差戻しし、A2/A3では変更しない。

### Failure-stop Rule（3回超停止）
- 自己修復ループは最大3回。
- 4回目相当は停止し、未確定論点を質問化してDecision Queueへ返却する。

## Stream B HIL Planning Update (2026-04-13)

### Phase 1) Read（対象2ファイル再読）
- Re-read対象を本メモと `issue-HIL-RS-01-next-phase-human-loop-reversible-synthesis.md` の2件に固定し、依存・Gate式・固定識別子の一致を確認。
- 依存連鎖は `A1 -> A2 -> A3` を維持し、A1契約値は参照専用とする。

### Phase 2) ADR CDC
- Context: HIL-RS-02 は A1 契約を運用へ接続する planning フェーズ。
- Decision: Open/Proceed判定を `Go = (a1Status=="Done" && pendingDecisionQueueCount==0 && schemaVersion==1.0.0 && overridePolicy==human_dual_control_only && contractLinkLocked==true && sharedResourceFreeze==true)` に一本化。
- Consequences: Gate不一致や識別子ドリフトはA1へ差し戻し、A2/A3で局所上書きしない。

### Phase 3) Plan（AC/DoD不足提案）
- AC補強: `Gate式一致`, `Pending bypass禁止`, `固定識別子一致`, `安全境界後退要求=0`。
- DoD補強: 各phaseに `入力(再読) -> 判定(CDC) -> 同期(Execute) -> 検証(Verify)` の証跡を残す。

### Phase 4) Execute（状態遷移契約同期）
- `Open/Proceed Allowed := (a1Status=="Done" && pendingDecisionQueueCount==0)`、`Hold/NoGo := (A1!=Done || pendingDecisionQueueCount>0)` を固定。
- Pending bypass と未承認確定化を禁止遷移として維持。

### Phase 5) Verify（ゲート式・固定識別子参照整合）
- 検証コマンドは `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` を正本化し、`rg` でGate式と固定値を再確認。
- 自己修復は最大3回。超過時は停止してDecision Queueへ返却。

### Phase 6) Proceed（未確定はDecision Queueへ戻す）
- Proceedは `a1Status=="Done" && pendingDecisionQueueCount==0` 成立時のみ許可。
- 前提崩れ・未定義競合・識別子不一致は推測せず停止し、Decision Queueに戻す。

### Fail-safe Contract
- 停止条件: 修復3回超過 / 識別子不一致 / 未承認確定化 / 安全境界後退要求。
- 禁止: A1契約値の再定義、Pendingの暗黙解決、A2/A3での契約値ローカル補完。


## Stream A Critical Path Update (2026-04-13)

### Phase 1 Read
- A1固定契約とQueue状態を再確認し、Proceed唯一条件を `a1Status=="Done" && pendingDecisionQueueCount==0` に確定。

### Phase 2 ADR CDC
- Context: HIL-RS-02 は A1 契約運用レーンであり、契約編集レーンではない。
- Decision: CDC未承認の契約変更は採用せず、Decision Queueへ戻す。
- Consequences: A2/A3 planning は参照専用で継続、差分はA1集約。

### Phase 3 Plan
- A2/A3 が参照する固定契約ID・固定値・禁止事項・Proceed条件を明文化。

### Phase 4 Execute
- planning文書内で `Go/NoGo` 判定式・停止条件を再固定。

### Phase 5 Verify
- docs-check と依存式一致検査を実施（3回超過で停止）。

### Phase 6 Proceed
- handoff は read-only contract pack 形式（契約ID一覧 / 判定式 / 禁止事項）で出力。
