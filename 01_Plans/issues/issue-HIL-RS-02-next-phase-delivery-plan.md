# Issue Draft: HIL-RS-02 次フェーズ実行計画

- Type: Process
- Status: Open
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P1
- Owner: Plan Owner (Stream B)
- Scope: `01_Plans/issues/`（planning only）
- Dependencies: `ADR-0027`, `ADR-0026`, `ADR-0028`, `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`, `state-transition gate (a1Status=="Done" && pendingDecisionQueueCount==0)`
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

### 6.1) A2/A3 着手条件（A1 freeze I/F固定参照）

- `StartAllowed = (a1Status=="Done" && pendingDecisionQueueCount==0 && schemaVersion=="1.0.0" && overridePolicy=="human_dual_control_only" && contractLinkLocked==true && sharedResourceFreeze==true && hasUndefinedContractChangeRequest==false && hasSafeModeRegressionRequest==false && hasShareExportLeakageRelaxationRequest==false && agreementStatus=="agreed")`
- `Go = StartAllowed`
- `NoGo = !StartAllowed`
- `NoGo` 時は実行着手せず、`issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md` へ差し戻す。

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

## Stream A Serial Contract Lock (2026-04-16)

### Phase 1 Read（再Read + 差分抽出）
- 本ファイルを含む Stream A 管轄10ファイルを再Readし、契約ID / Gate式 / 禁止遷移を照合。
- 差分抽出結果:
  - `a1Status=="Done" && pendingDecisionQueueCount==0` を唯一ゲートとして維持。
  - `schemaVersion=1.0.0` / `overridePolicy=human_dual_control_only` / `contractLinkLocked=true` / `sharedResourceFreeze=true` を固定値として維持。
  - 契約ID衝突・依存逆転・未定義競合は 0 件。

### Phase 2 ADR CDC
- Context: A1契約固定を下流A2/A3の参照専用境界として維持する。
- Decision: 新規ADR追加は不要（既存 ADR-0026/0027/0028 と整合）。未承認決定は確定扱いしない。
- Consequences: 契約変更要求はA1へ差戻し、下流はread-only handoff値のみ利用する。

### Phase 3 Plan
- AC/DoD不足時はドラフト提案を先行し、`agreementStatus=agreed` まで Execute へ進まない。
- SSOT固定値:
  - `schemaVersion=1.0.0`
  - `overridePolicy=human_dual_control_only`
  - `contractLinkLocked=true`
  - `sharedResourceFreeze=true`
- Go/No-Go:
  - `Go = (a1Status=="Done" && pendingDecisionQueueCount==0 && schemaVersion=="1.0.0" && overridePolicy=="human_dual_control_only" && contractLinkLocked==true && sharedResourceFreeze==true)`
  - `NoGo = !Go`

### Phase 4 Execute
- 文言・契約ID・依存順序（A1→A2→A3）・停止条件を本ファイル内で同期。
- 禁止遷移を固定:
  - `Pending` bypass（`Pending -> Approved/Rejected` 以外）
  - A1未完了時の A2/A3 `Draft -> Open`
  - 未承認決定の確定扱い
- Read-only handoff:
  - `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
  - `contractIds=A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|A1-ERROR-IF`

### Phase 5 Verify
- `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- `rg -n "a1Status=="Done" && pendingDecisionQueueCount==0|schemaVersion=1.0.0|overridePolicy=human_dual_control_only|contractLinkLocked=true|sharedResourceFreeze=true|Pending -> Approved|Pending -> Rejected" 01_Plans/issues/issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md 01_Plans/issues/issue-HIL-RS-02-A1-governance-contract-hardening.md 01_Plans/issues/issue-HIL-RS-02-next-phase-delivery-plan.md 01_Plans/issues/issue-HIL-RS-01-next-phase-human-loop-reversible-synthesis.md`
- Self-Correctionは最大3回。4回目相当は即停止。

### Phase 6 Proceed
- 再開条件: `NoGo` 要因（未承認決定、識別子不一致、依存逆転）を解消し、再VerifyがPassすること。
- 差戻し先: `issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`（A1契約正本）。
- Decision Queue未解決項目は `Pending` のまま保持し、確定扱いしない。

### Fail-safe（停止報告テンプレ）
1. 失敗条件
2. 影響ファイル・契約ID
3. 人間判断が必要な選択肢（2案）
   - 案1: 既存固定値を維持してA1へ差戻し
   - 案2: 承認会議で固定値変更を決定後に再凍結

## Stream B HIL Umbrella Planning Update (2026-04-16)

### Phase 1 Read（対象3ファイル再Read）
- Phase開始時の再Read対象を次の3ファイルに固定。
  1. `issue-HIL-RS-01-next-phase-human-loop-reversible-synthesis.md`
  2. `issue-HIL-RS-02-next-phase-delivery-plan.md`
  3. `issue-HIL-RS-02-A3-operations-documentation-sync.md`
- 依存連鎖 `A1 -> A2 -> A3`、Go/NoGo式、固定識別子の一致を再確認。

### Phase 2 ADR CDC（先行明文化）
- Context: 本issueは HIL-RS-02 の umbrella execution planning を扱い、契約値の編集権限を持たない。
- Decision: Open/Proceedは `a1Status=="Done" && pendingDecisionQueueCount==0` を最低条件とし、固定値一致（`schemaVersion=1.0.0`, `overridePolicy=human_dual_control_only`, `contractLinkLocked=true`, `sharedResourceFreeze=true`）を必須化。
- Consequences: 固定値ドリフト、未承認確定化、Pending bypass は即NoGoとしてDecision Queueへ返却する。

### Phase 3 Plan
- AC/DoD不足時はドラフト案を先に記録し、合意完了まで Execute を保留。
- Planチェック項目: `3-file reread`, `CDC先行`, `禁止遷移明文化`, `Self-repair<=3`。

### Phase 4 Execute
- 本issueの状態遷移契約を3ファイルで参照できる文言に同期。
- A2/A3での契約再定義禁止・Pending bypass禁止・A1差戻し導線を固定。

### Phase 5 Verify
- `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- `rg -n "Stream B HIL Umbrella Planning Update \(2026-04-16\)|A1 -> A2 -> A3|a1Status==\"Done\" && pendingDecisionQueueCount==0|schemaVersion=1.0.0|overridePolicy=human_dual_control_only|contractLinkLocked=true|sharedResourceFreeze=true|Pending bypass|Self-repair<=3" 01_Plans/issues/issue-HIL-RS-01-next-phase-human-loop-reversible-synthesis.md 01_Plans/issues/issue-HIL-RS-02-next-phase-delivery-plan.md 01_Plans/issues/issue-HIL-RS-02-A3-operations-documentation-sync.md`
- Verify失敗時は自己修復最大3回。超過時は停止。

### Phase 6 Proceed
- Proceedは Verify pass かつ Go式成立時のみ許可。
- 不成立時は `Draft/Open(hold)` を維持し、Decision Queueへ差し戻す。


## Stream A Governance Queue Fixpoint v1.1（2026-04-16）

### Phase 1 Read Sync
- Plan: A1正本とHIL-RS-01/02のGate式・固定識別子を再照合。
- Execute: `a1Status=="Done" && pendingDecisionQueueCount==0` を唯一ゲートとして再確認。
- Verify: Freeze Pack要素（Contract IDs / `schemaVersion` / `overridePolicy` / SSOT）差分なし。
- Proceed: A2/A3は参照専用のまま継続。

### Phase 2 Plan（Decision Queue証跡化）
| Queue ID | Decision topic | Required evidence | Status rule |
| --- | --- | --- | --- |
| `DQ-HIL-RS-02-CDC` | 契約変更要求 | CDC（Context/Decision/Consequences）と互換評価 | 承認まで `Pending` |
| `DQ-HIL-RS-02-SAFE` | SafeMode後退要求 | 回帰再現手順と漏えい境界評価 | 原則 `Rejected` |
| `DQ-HIL-RS-02-SHARE` | share/export緩和要求 | 監査要件と代替案比較 | 承認なしは `Pending` 維持 |

### Phase 3 ADR/Decision（Context / Decision / Consequences）
- Context: delivery planning が契約再定義を内包すると統治境界が崩れる。
- Decision: HIL-RS-02は固定仕様参照のみを許可し、決定待ちは Queue へ戻す。
- Consequences: 未承認項目の確定化は禁止。NoGo時は停止報告を必須化。

### Phase 4 Contract Freeze（参照専用パック配布）
- Pack Version: `HIL-RS-02-A1-CONTRACT-FREEZE-v1.1`
- 変更禁止:
  - `Pending bypass`
  - `A1未完了でのA2/A3 Open`
  - `overridePolicy` 緩和
  - `schemaVersion` の独自更新

### Phase 5 Verify & Proceed
- Verify commands: docs-check + gate式rg確認。
- Proceed: `Go`成立時のみ。未確定は `Pending` 維持で人間判断待ち。


## Stream B Serial Contract Alignment (2026-04-17)

### Phase 1 Read（Dependencies / State Transition / Fail-safe 再読）
- 再読対象を本メモと `issue-HIL-RS-01-next-phase-human-loop-reversible-synthesis.md` の2件に固定し、依存・遷移・停止条件の同値性を点検。
- 点検結果: `Dependencies` の主語を「特定ファイル待ち」から「凍結契約 + 状態遷移ゲート」へ統一する必要を確認。

### Phase 2 ADR CDC（変更明文化・承認待ち）
- Context: HIL-RS-02 は契約運用レーンであり、契約編集レーンではない。
- Decision: `Dependencies` を `freezeContractId + state-transition gate` で表現し、着手可否は `Go/NoGo` 契約式のみで判定する。
- Consequences: 参照ファイルは read-only 導線として扱い、依存判定は状態遷移契約を正本とする。
- Decision Status: `Pending Approval`（CDC承認待ち）。

### Phase 3 Plan（AC/DoD不足提案）
- AC提案: `dependencyExpressionDrift=0`, `gateExpressionDrift=0`, `freezeIdentifierDrift=0`, `pendingBypass=0`, `safetyDowngradeRequest=0`。
- DoD提案: Verifyで `docs-check + rg + diff` の3点を必須化し、証跡を本issueへ残す。
- 合意状態: `agreementStatus=pending_approval`（承認前は `Draft/Open(hold)` を維持）。

### Phase 4 Execute（依存記述の契約統一）
- `Dependencies` を `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1` と `state-transition gate` の契約記述へ統一。
- `Go/NoGo` 式、禁止遷移、A1差戻し導線は既存契約を維持（再定義禁止）。

### Phase 5 Verify（docs-check + diff整合）
- `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- `rg -n "Dependencies:|state-transition gate|a1Status=="Done" && pendingDecisionQueueCount==0|Fail-safe" 01_Plans/issues/issue-HIL-RS-01-next-phase-human-loop-reversible-synthesis.md 01_Plans/issues/issue-HIL-RS-02-next-phase-delivery-plan.md`
- 自己修復上限は3回。4回目相当は停止。

### Phase 6 Proceed（未解決の返却）
- 未承認・未定義競合・前提崩れは Decision Queue へ返却し、推測で確定しない。
- Proceedは `a1Status=="Done" && pendingDecisionQueueCount==0` 成立時のみ許可。


## Stream A Delivery Gate Record (2026-04-17)

### Phase 1 Read
- Stream A 管轄4ファイルを再読し、A1→A2/A3依存が `a1Status=="Done" && pendingDecisionQueueCount==0` に一本化されていることを確認。

### Phase 2 ADR CDC
- Context: Delivery planning は契約編集ではなく、A1固定契約の参照運用である必要がある。
- Decision: CDC追加は不要。未定義競合は推測修正せず Decision Queue へ返却する。
- Consequences: A2/A3の開始判定は固定識別子一致 + queue解消を必須条件として維持。

### Phase 3 Plan
- AC/DoD不足なし。Go/NoGoと停止条件の既存条項を維持。

### Phase 4 Execute
- Go/NoGo境界を再固定:
  - `Go = (a1Status=="Done" && pendingDecisionQueueCount==0 && schemaVersion=="1.0.0" && overridePolicy=="human_dual_control_only" && contractLinkLocked==true && sharedResourceFreeze==true)`
  - `NoGo = !Go`
  - 停止条件: Self-Correction 3回超過 / 固定識別子不一致 / 未承認確定化

### Phase 5 Verify / Proceed
- docs-check 実行: `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`（Pass）。
- Proceedは `Go` 成立時のみ許可。未達はA1差戻し + Decision Queue継続。

## Stream E Contract Advancement Update (2026-04-17)

### Phase 1) Read同期（4ファイル固定）
- HIL-RS契約4ファイルのみを再Readし、delivery planが契約優先順序（A1→A2→A3）を維持していることを確認。

### Phase 2) CDC起票/更新（ADR要件）
- Context: Delivery計画が契約固定前に進むと、A2/A3で再凍結が発生して手戻りが増える。
- Decision: RS-02はA1承認を先行ゲートとし、A2/A3は「準備は可、Openは承認後のみ」に固定する。
- Consequences: 承認待ち期間はA2/A3をDraft/Open(hold)に据え置き、実行開始しない。

### Phase 3) Plan（A1先行・A2/A3開放条件）
- 開放判定（提案）:
  - `OpenA2A3 = (a1Status=="Done" && approvalStatus=="approved" && pendingDecisionQueueCount==0)`
- A2/A3の開放条件は上式のみを採用し、派生条件のローカル追加を禁止。

### Phase 4) Execute（契約固定）
- 固定参照:
  - `HIL-RS-02-A1-CONTRACT-FREEZE-v1`
  - `A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|A1-ERROR-IF`
- 禁止:
  - `Pending` の暗黙解決
  - `approvalStatus!="approved"` での次Phase進行

### Phase 5) Verify（条件一致監査）
- 監査観点:
  1. Gate式が4ファイル間で一致
  2. Freeze keys が一致
  3. 安全境界後退要求が0件
- 監査失敗時は3回上限で自己修復、超過時停止。

### Phase 6) Proceed（Open化条件の提案）
- Open提案:
  - `Proceed = (OpenA2A3==true && schemaVersion=="1.0.0" && overridePolicy=="human_dual_control_only" && contractLinkLocked==true && sharedResourceFreeze==true)`
- `Proceed==false` の場合はDecision Queueへ返却し、承認待ちを継続する。

## Stream D Delivery Plan Synchronization Record (2026-04-18)

### Phase 1 Read
- 対象4ファイルを再読し、Unlock式と禁止遷移を照合。
- 固定式: `a1Status=="Done" && pendingDecisionQueueCount==0`。

### Phase 2 ADR CDC
- Context: Delivery計画はA1契約の運用同期であり、ゲート式の派生追加を許容しない。
- Decision: A2/A3 Openは `a1Status=="Done" && pendingDecisionQueueCount==0` 成立時のみ。
- Consequences: A1完了前はA2/A3をOpenしない。未承認確定化は禁止。
- Decision Status: Pending Approval（追加文言は承認待ち）。

### Phase 3 Plan
- AC/DoD補完:
  - A1完了前Open禁止を固定規約として明文化。
  - 強制サイクル `Plan -> Execute -> Verify -> Proceed` を継続。

### Phase 4 Execute
- 状態遷移契約同期:
  - 許可: `Pending -> Approved | Rejected`
  - 禁止: `Pending bypass` / `a1Status!="Done"` での `A2/A3 Draft -> Open`
  - 停止: 式不一致 / 未承認確定化 / 修復3回超過

### Phase 5 Verify
- 式一致確認: `a1Status=="Done" && pendingDecisionQueueCount==0`。
- docs-checkを必須化。

### Phase 6 Proceed
- 条件一致時のみProceed。
- 不一致時は即停止し、A1契約へ差戻し。

## Stream A Execution Record (2026-04-18, dedicated lane)

### Phase 1 Read（4ファイル差分一覧）
- Status差分: 全件 `Open`（差分なし）。
- Dependencies差分: 本Issueは `freezeContractId` 明示依存を持つ delivery計画。
- Gate式差分: 全件 `a1Status=="Done" && pendingDecisionQueueCount==0` 一致（差分なし）。

### Phase 2 ADR CDC
- Context: delivery計画は契約運用の同期レイヤであり、契約再定義レイヤではない。
- Decision: 方針変更不要。CDCは同期記録として明文化。
- Consequences: A2/A3でのローカル契約変更は禁止し、差分要求はA1へ差戻し。
- Approval: `agreementStatus=agreed`（同期合意）。

### Phase 3 Plan（Checklist宣言）
- `Plan -> Execute -> Verify -> Proceed` を固定チェックリスト化。
- AC/DoD不足なし。Proceed条件に `agreementStatus=agreed` を保持。

### Phase 4 Execute
- issue本文の契約語彙・禁止遷移・差戻し条件をA1正本へ同期。
- 明示禁止: A2/A3での固定契約値再定義。

### Phase 5 Verify
- docs-check相当（validator + rg）を実施。
- self-correction 3回まで、4回目相当は停止。

### Phase 6 Proceed
- Gate成立項目のみ進行し、未確定項目は Decision Queue に戻す。

## Stream B HIL-RS Execution Planning Update (2026-04-18)

### Phase 1) Read（最新メタ再読）
- 再読対象を `issue-HIL-RS-02-next-phase-delivery-plan.md` と `issue-HIL-RS-01-next-phase-human-loop-reversible-synthesis.md` の2件へ固定。
- `ADR-0026/0027/0028` と本Issueの依存・停止条件の整合を再確認し、上位改定不要（既存CDC継続）を確認。

### Phase 2) Plan設計（AC / DoD / 検証計画）
- AC:
  1. Open/Proceed判定は `a1Status=="Done" && pendingDecisionQueueCount==0` の単一式を維持。
  2. 固定識別子（`freezeContractId`, `contractIds`, `schemaVersion=1.0.0`, `overridePolicy=human_dual_control_only`, `contractLinkLocked=true`, `sharedResourceFreeze=true`）一致を必須化。
  3. 禁止遷移（Pending bypass / A1未完了でのA2/A3 Open / 未承認確定化）を0件維持。
- DoD:
  - `Plan -> Execute -> Verify -> Proceed` の記録を本Issueへ残し、未確定は必ず Decision Queue へ戻す。
- 検証計画:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
  - `rg` で Gate式・固定識別子・禁止遷移・Fail-safe 文言の存在確認。

### Phase 3) モック前提化（I/F依存の切断）
- A2/A3着手判定は Mock Snapshot + Freeze Pack を参照する read-only 仕様とし、下流Issueで契約値を変更しない。
- I/F差分や未定義競合は `issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md` へ差し戻す。

### Phase 4) Verify（依存 / 優先度 / 責務境界の整合）
- 依存整合: `A1 -> A2 -> A3` を維持し、`A1!=Done` または `pendingDecisionQueueCount>0` なら `NoGo`。
- 優先度整合: 安全境界後退要求（SafeMode/share-export/`human_dual_control_only`）を即停止トリガーとして維持。
- 責務境界整合: Stream B は planning memo の更新のみ実施し、code / architecture / shared files は非対象を維持。

### Phase 5) Proceed（次の1手固定）
- 次の1手（固定）:
  1. validator実行で整合を確認。
  2. 整合不一致は Decision Queue へ返却し、承認待ちで停止。
  3. 整合一致時は read-only handoff pack をA2/A3側へ連携（契約値の編集権限なし）。
- フェイルセーフ:
  - Self-correction 上限は3回。超過時は停止し指示待ち。

## Stream B HIL Umbrella Planning Update (2026-04-18, A1 gate-only alignment)

### Phase 1: Read（対象2ファイル再Read）
- 再Read対象を次の2ファイルに固定して再確認した。
  1. `issue-HIL-RS-01-next-phase-human-loop-reversible-synthesis.md`
  2. `issue-HIL-RS-02-next-phase-delivery-plan.md`
- 整合確認対象は **A1ゲート式のみ** とし、`a1Status=="Done" && pendingDecisionQueueCount==0` の一致を確認。

### Phase 2: ADR CDC（変更要否判定）
- Context: Stream B は umbrella planning 担当であり、planning issue 以外は編集しない。
- Decision: 仕様変更不要（既存CDCでゲート式整合を満たす）。
- Consequences: 仕様変更が必要になった場合のみ CDC追記 + `approvalStatus="pending"` で停止する。

### Phase 3: Plan（AC/DoDドラフト明確化）
- AC/DoDドラフト（合意済み運用）:
  1. `A1完了前Open化禁止` を明示維持。
  2. `pendingDecisionQueueCount==0` 充足前は Proceed 不可。
  3. A1ゲート式の語彙差分を発生させない。

### Phase 4: Execute（状態遷移契約として記述）
- 依存契約:
  - `Go = (a1Status=="Done" && pendingDecisionQueueCount==0)`
  - `NoGo = (a1Status!="Done" || pendingDecisionQueueCount>0)`
- 実装待ちは着手条件にしない（契約参照のみ）。

### Phase 5: Verify（validator + rg）
- 検証コマンド:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
  - `rg -n 'a1Status=="Done" && pendingDecisionQueueCount==0|A1完了前Open化禁止|Pending bypass|NoGo' 01_Plans/issues/issue-HIL-RS-01-next-phase-human-loop-reversible-synthesis.md 01_Plans/issues/issue-HIL-RS-02-next-phase-delivery-plan.md`
- Self-Correctionは最大3回。4回目相当は停止して指示待ち。

### Phase 6: Proceed（Go条件のみ進行）
- Go条件成立時のみ進行。
- 条件未達は Decision Queue へ返却する。

### Fail-safe（本ストリーム）
- 未承認決定の確定化、固定ID不一致、自己修復3回超過は停止して指示待ち。

## Stream A Critical Path Execution (2026-04-19)

### Phase 1 Read
- Status=`Open`, Priority=`P1`, DecisionStatus=`Fixed` を再確認。
- ContractID=`HIL-RS-02-A1-CONTRACT-FREEZE-v1` と A1 contract IDs を参照固定。
- GoNoGoGate=`a1Status=="Done" && pendingDecisionQueueCount==0` を維持。

### Phase 2 ADR CDC
- Context/Decision/Consequences の上位差分は検出なし。
- 承認待ちCDCの新規作成は不要（既存固定方針を継続）。

### Phase 3 Plan
- AC/DoD不足なし。`agreementStatus=agreed` を維持し Execute へ進行。

### Phase 4 Execute（A1契約固定証跡）
- `contractLinkLocked=true` / `sharedResourceFreeze=true` の固定証跡を維持。
- A2/A3はread-only handoffでのみ契約値を利用（再定義禁止）。

### Phase 5 Verify
- docs-check / 依存リンク整合 / ContractID collision=0 を確認（Self-Correction 0/3）。

### Phase 6 Proceed（固定I/F + 非目標）
- 固定I/F: `HIL-RS-02-A1-CONTRACT-FREEZE-v1`, `A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|A1-ERROR-IF`, `schemaVersion=1.0.0`, `overridePolicy=human_dual_control_only`, `contractLinkLocked=true`, `sharedResourceFreeze=true`。
- 非目標: Pending bypass、A2/A3での契約変更、安全境界の緩和。
