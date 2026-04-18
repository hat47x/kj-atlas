# Issue Draft: HIL-RS-01 次フェーズ計画（Human-in-the-loop可逆統合）

- Type: Process
- Status: Open
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P1
- Owner: Plan Owner (Stream B)
- Scope: `01_Plans/issues/`（planning only）
- Dependencies: `ADR-0026`, `ADR-0027`, `ADR-0028`, `state-transition gate (a1Status=="Done" && pendingDecisionQueueCount==0)`
- Related ADR/Spec: `ADR-0026`, `ADR-0027`, `ADR-0001`, `00_Prompt/domain.md`
- Expected verification level: `docs-check`

## 1) Goal

HIL-RS-01 を **Plan契約の単一正本（issue群）** として再整理し、A1/A2/A3 依存を「実装待ち」ではなく **状態遷移契約** で管理する。

## 2) Mock Contract Snapshot（Interface固定識別子のみ参照）

- Snapshot ID: `MOCK-CONTRACT-SNAPSHOT-HIL-RS-v1`
- Freeze Pack ID: `HIL-RS-02-A1-CONTRACT-FREEZE-v1`
- Fixed Contract IDs:
  - `A1-CRITIQUE-IF`
  - `A1-REDIFF-IF`
  - `A1-ATTR-IF`
  - `A1-ERROR-IF`
- Fixed values:
  - `schemaVersion=1.0.0`
  - `overridePolicy=human_dual_control_only`
  - `contractLinkLocked=true`
  - `sharedResourceFreeze=true`

## 3) ADR CDC（Phase 2）

- Context:
  - 本issueは `ADR-0026/0027/0028` の下位計画であり、Stream B は architecture/documentation 実体編集を行わない。
- Decision:
  - A1/A2/A3 の依存は `state-transition contract` として固定し、実装完了待ちを着手条件にしない。
- Consequences:
  - 不一致はA1へ差し戻す。A2/A3は契約再定義を行わない。

## 4) State Transition Contract（依存切断）

- Allowed:
  - `A1: Draft -> Open -> In Progress -> Done`
  - `A2/A3: Draft -> Open` は `A1==Done && pendingDecisionQueueCount==0` のときのみ
  - `DecisionQueue: Pending -> Approved | Rejected`
- Forbidden:
  - Pending bypass
  - `A1!=Done` での `A2/A3 Draft -> Open`
  - A2/A3 側での契約ID再定義

## 5) Acceptance Criteria / DoD

- [x] CDC（Context/Decision/Consequences）が明文化されている。
- [x] 依存が状態遷移契約で記述されている。
- [x] Mock Contract Snapshot の固定識別子のみを参照している。
- [x] SafeMode既定ON / share-export漏えい防止 / `human_dual_control_only` 後退禁止が明示されている。
- [x] Proceed条件（Open化条件と停止条件）が明文化されている。

## 6) Serial Phases（Plan -> Execute -> Verify -> Proceed）

### Phase 1 Read
- 対象5 issueを再Readし、Status/Scope/Dependencies/Contract IDs を再確認する。

### Phase 2 ADR CDC
- CDCを再確認し、上位ADR改定が必要なら停止（承認待ち）する。

### Phase 3 Plan
- AC/DoDと状態遷移契約の不足を補完する。

### Phase 4 Execute
- issue本文のみ同期し、依存契約・禁止遷移・差し戻し先を更新する。

### Phase 5 Verify
- `validate_active_issue_memos.py` + `rg` で整合確認。失敗時は自己修復最大3回。

### Phase 6 Proceed
- Open化条件を満たすものだけを次アクションへ進め、未確定はDecision Queueへ戻す。

## 7) Open化条件（Proceed Gate）

1. `A1==Done`
2. `pendingDecisionQueueCount==0`
3. 固定識別子（Freeze Pack/Contract IDs/schemaVersion/overridePolicy）が一致
4. 安全境界後退要求が存在しない

## 8) Fail-safe

- 停止条件:
  1. Verify失敗が3回超過
  2. 未承認決定の確定化
  3. 固定識別子の不一致
- 停止時記録:
  - 失敗条件 / 対象issue / 必要承認者 / Yes-No確認事項

## 9) Stream F update (2026-04-12, planning memo only)

### Phase 1) Read同期
- Re-read fixed scope memos: `issue-HIL-RS-01-next-phase-human-loop-reversible-synthesis.md`, `issue-HIL-RS-02-next-phase-delivery-plan.md`, `issue-HIL-RS-02-A1-governance-contract-hardening.md`, `issue-HIL-RS-02-A2-frontend-reversible-synthesis-application.md`, `issue-HIL-RS-02-A3-operations-documentation-sync.md`.
- Verified lock values remain unchanged: `schemaVersion=1.0.0`, `overridePolicy=human_dual_control_only`, `contractLinkLocked=true`, `sharedResourceFreeze=true`.

### Phase 2) A1/A2/A3依存 + Decision Queue更新
| QueueID | Topic | Status | Gate | Owner |
| --- | --- | --- | --- | --- |
| `DQ-HIL-RS-01-001` | A1 freeze pack consistency (`HIL-RS-02-A1-CONTRACT-FREEZE-v1`) | Closed | `A1==Done` | Stream F |
| `DQ-HIL-RS-01-002` | A2/A3 open precondition (`pendingDecisionQueueCount==0`) | Closed | `Pending -> Approved/Rejected` only | Stream F |
| `DQ-HIL-RS-01-003` | Safety boundary downgrade request handling | Closed | downgrade request = `Rejected` | Stream F |

### Phase 3) AC/DoD不足補完
- Added explicit NoGo condition: if `A1!=Done` **or** unresolved queue exists, A2/A3 must remain `Draft` or `Open (hold)` and cannot move to active execution.
- Added explicit rollback target: any contract drift must be routed back to A1 memo, not patched in A2/A3.
- Reconfirmed unique unlock invariant: `unlockAllowed := (A1==Done && pendingDecisionQueueCount==0)`.
- Reconfirmed forbidden path: no transition may treat `Pending` as implicitly resolved.

### Phase 4) docs-check
- Validation command is fixed to: `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`.
- If validation fails, self-correction loop max is 3; after that, stop and escalate with queue status snapshot.

### Phase 5) 次レーンhandoff
- Next lane package must include: `Snapshot ID`, `Freeze Pack ID`, queue table, and explicit Go/NoGo result.
- Handoff rule: A2/A3 lanes receive reference-only contract payload; contract value edits are prohibited.

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
- Stream C は **HIL-RS計画系issueの整流化のみ** を担当し、実装完了待ちでA1をブロックしない。
- 本ストリームで行うのは次の2点のみ。
  1. ゲート条件明文化（`a1Status=="Done" && pendingDecisionQueueCount==0`）
  2. 差戻し導線固定（契約差分は常にA1へ戻す）
- A1を「外部完了待ち」状態へ遷移させる記述は禁止。

### Phase Execution Record（1〜6）
1. **Phase 1 Read**: 対象3ファイルを再読し、固定識別子・依存・禁止遷移を再確認。
2. **Phase 2 ADR明文化（CDC）**: 既存CDCを再確認し、上位ADR改定不要を確認（issue内CDCを継続採用）。
3. **Phase 3 Plan**: AC/DoD不足として「A1外部待ち禁止」「差戻し先A1固定」を追記。
4. **Phase 4 Execute**: 状態遷移契約を `a1Status=="Done" && pendingDecisionQueueCount==0` に一本化。
5. **Phase 5 Verify**: docs-check + 差分検証を実施。失敗時は自己修復最大3回、4回目相当で停止。
6. **Phase 6 Proceed**: Go/NoGoを上記ゲート式で判定し、曖昧点は質問化して停止。

### State Transition Clarification（契約明確化）
- **Go**: `a1Status=="Done" && pendingDecisionQueueCount==0`
- **NoGo**: `A1!=Done` または `pendingDecisionQueueCount>0`
- **Rollback route**: 契約不一致・語彙ドリフト・安全境界後退の要求は **A1 issueへ差戻し**。

### Failure-stop Rule（3回超停止）
- Verify失敗の自己修復は最大3回。
- 3回超過時は作業停止し、未確定点を Yes/No 質問に分解して記録する。

## Stream B HIL Planning Update (2026-04-13)

### Phase 1) Read（対象2ファイル再読）
- Re-read対象を本メモと `issue-HIL-RS-02-next-phase-delivery-plan.md` の2件に限定し、Scope/Dependencies/Gate式/固定識別子を再確認。
- 参照値は `MOCK-CONTRACT-SNAPSHOT-HIL-RS-v1` と `HIL-RS-02-A1-CONTRACT-FREEZE-v1` のみを採用。

### Phase 2) ADR CDC
- Context: Stream B は planning-only であり、A1契約値を変更しない。
- Decision: `Go = (a1Status=="Done" && pendingDecisionQueueCount==0 && schemaVersion==1.0.0 && overridePolicy==human_dual_control_only && contractLinkLocked==true && sharedResourceFreeze==true)` を唯一のProceed判定式として固定。
- Consequences: 契約値ドリフト/未定義競合は推測修正せず A1 へ差し戻し、Decision Queueへ戻す。

### Phase 3) Plan（AC/DoD不足提案）
- AC補強: `Gate式一致`, `固定識別子一致`, `Pending bypass=0`, `安全境界後退要求=0` を同時成立条件として運用。
- DoD補強: `Plan -> Execute -> Verify -> Proceed` の順序証跡をissue本文へ残す。

### Phase 4) Execute（状態遷移契約同期）
- `Open/Proceed Allowed := (a1Status=="Done" && pendingDecisionQueueCount==0)` を維持し、NoGo を `A1!=Done || pendingDecisionQueueCount>0` に固定。
- A2/A3 の契約再定義禁止、差分要求の差戻し先A1固定を再確認。

### Phase 5) Verify（ゲート式・固定識別子参照整合）
- Gate式/固定識別子/禁止遷移を `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` と `rg` で照合。
- 自己修復ループ上限は3回。4回目相当は停止。

### Phase 6) Proceed（未確定はDecision Queueへ戻す）
- Proceed許可は `a1Status=="Done" && pendingDecisionQueueCount==0` 充足時のみ。
- 未確定・前提崩れ・未定義競合はDecision Queueへ返却し、Yes/No質問化して停止。

### Fail-safe Contract
- 停止条件: 自己修復3回超過 / 固定識別子不一致 / 未承認確定化 / 前提崩れ。
- 禁止: 推測での契約補完、A2/A3側での契約値変更、Pendingの暗黙解決。


## Stream A Critical Path Update (2026-04-13, contract freeze)

### Phase 1: Read Sync
- A1ゲート式・固定値・Decision Queue状態を再読し、差分なしを確認。
- 固定ゲート式を `Go = (a1Status=="Done" && pendingDecisionQueueCount==0 && schemaVersion==1.0.0 && overridePolicy==human_dual_control_only && contractLinkLocked==true && sharedResourceFreeze==true)` に統一。

### Phase 2: ADR CDC（承認待ち化ポリシー）
- Context: HIL-RS-01 は A2/A3 参照契約の上流であり、下流での契約補完は禁止。
- Decision: 変更提案は CDC 形式（Context/Decision/Consequences）で先に起票し、承認前は `Draft/Open(hold)` を維持。
- Consequences: 未承認の契約変更は Proceed 不可。差分要求は A1 へ差戻し。

### Phase 3: Plan（A2/A3参照契約の明文化）
- A2/A3 参照契約ID: `HIL-RS-02-A1-CONTRACT-FREEZE-v1`, `A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|A1-ERROR-IF`, `CE0-CTX-IF`, `CE0-SAFEMODE-IF`, `CE0-REVIEW-IF`, `CG-01..05`。
- 禁止事項: Pending bypass / A2-A3側契約値再定義 / SafeMode後退 / review自動昇格 / direct write / auto-apply。
- Proceed条件: `a1Status=="Done" && pendingDecisionQueueCount==0` かつ固定値一致。

### Phase 4: Execute（planning文書固定）
- 本issueを契約正本として、判定式・契約ID・停止条件を固定。
- 実装/統合ファイル編集は行わない。

### Phase 5: Verify
- docs-check: `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- 依存式一致検査: `rg -n "a1Status=="Done" && pendingDecisionQueueCount==0|HIL-RS-02-A1-CONTRACT-FREEZE-v1|schemaVersion=1.0.0|overridePolicy=human_dual_control_only|contractLinkLocked=true|sharedResourceFreeze=true|Pending bypass|direct write|auto-apply|review自動昇格|SafeMode後退" 01_Plans/issues/issue-HIL-RS-01-next-phase-human-loop-reversible-synthesis.md 01_Plans/issues/issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md 01_Plans/issues/issue-HIL-RS-02-next-phase-delivery-plan.md 01_Plans/issues/issue-HIL-RS-02-A1-governance-contract-hardening.md 01_Plans/issues/issue-HIL-RS-02-A3-operations-documentation-sync.md`
- 失敗時Self-Correction上限: 3回。

### Phase 6: Proceed（read-only contract pack）
- 引継ぎ形式を read-only contract pack に固定。
- Pack内容: 契約ID一覧・判定式・禁止事項・停止条件・差戻し先A1。

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
- 再Read対象を次の3ファイルに固定。
  1. `issue-HIL-RS-01-next-phase-human-loop-reversible-synthesis.md`
  2. `issue-HIL-RS-02-next-phase-delivery-plan.md`
  3. `issue-HIL-RS-02-A3-operations-documentation-sync.md`
- Gate式・固定識別子・Fail-safeが3ファイルで同値であることを確認。

### Phase 2 ADR CDC（先行明文化）
- Context: Stream BはHIL umbrella planning専用であり、実装・architecture・operations本文の編集を行わない。
- Decision: `Go = (a1Status=="Done" && pendingDecisionQueueCount==0 && schemaVersion==1.0.0 && overridePolicy==human_dual_control_only && contractLinkLocked==true && sharedResourceFreeze==true)` を親issueの唯一Proceed条件として維持。
- Consequences: 不一致・未承認・競合は推測で補完せずDecision Queueへ返却し、A1契約正本へ差し戻す。

### Phase 3 Plan
- AC/DoD不足がある場合はドラフト提案を先行し、`agreementStatus=agreed` を確認するまで Execute に進まない。
- 追加AC: `3-file reread evidence`, `CDC先行`, `Plan->Execute->Verify->Proceed証跡`, `Self-repair<=3`。

### Phase 4 Execute
- 本issueは planning SSOT として、3ファイル横断で使う Gate式・禁止遷移・差し戻し先を文言同期。
- A2/A3での契約値再定義禁止と Pending bypass 禁止を維持。

### Phase 5 Verify
- `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- `rg -n "Stream B HIL Umbrella Planning Update \(2026-04-16\)|a1Status==\"Done\" && pendingDecisionQueueCount==0|schemaVersion=1.0.0|overridePolicy=human_dual_control_only|contractLinkLocked=true|sharedResourceFreeze=true|Self-repair<=3|Decision Queue" 01_Plans/issues/issue-HIL-RS-01-next-phase-human-loop-reversible-synthesis.md 01_Plans/issues/issue-HIL-RS-02-next-phase-delivery-plan.md 01_Plans/issues/issue-HIL-RS-02-A3-operations-documentation-sync.md`
- Verify失敗時の自己修復は最大3回。4回目相当は停止。

### Phase 6 Proceed
- Proceed条件: Go式一致 + Pending bypass 0 + 安全境界後退要求 0 + Verify pass。
- 未確定項目はYes/No質問へ分解してDecision Queueへ戻し、推測確定しない。


## Stream A Contract Freeze Output v1.1（2026-04-16）

### Phase 1 Read Sync
- Plan: HIL-RS-01/02およびA1契約正本を再読して Freeze Pack 整合を確認。
- Execute: Contract IDs / `schemaVersion` / `overridePolicy` / SSOT の一致を照合。
- Verify: 想定差分なし（不一致 0件）。
- Proceed: 契約を参照専用で公開継続。

### Phase 2 Plan（AC/DoD不足の補完方針）
- `agreementStatus=agreed` を満たすまで Execute へ進めない。
- 未確定論点は「決定に必要な証跡」を明記し、`Pending` のまま保持する。

### Phase 3 ADR/Decision（Context / Decision / Consequences）
- Context: 下流レーンの前提を都度成果物ではなく固定仕様参照に変換する必要がある。
- Decision: A1 Freeze Pack v1.1 を唯一参照とし、未承認項目は確定扱いしない。
- Consequences: A2/A3 は契約再定義禁止。変更要求は A1 へ差戻し。

### Phase 4 固定I/Fパック（版番号付き）
- Reference Pack: `HIL-RS-02-A1-CONTRACT-FREEZE-v1.1`
- 変更禁止項目:
  - `freezeContractId`
  - `contractIds`
  - `schemaVersion=1.0.0`
  - `overridePolicy=human_dual_control_only`
  - `contractLinkLocked=true`
  - `sharedResourceFreeze=true`

### Phase 5 Verify & Proceed
- Proceed条件: `a1Status=="Done" && pendingDecisionQueueCount==0` かつ固定値一致。
- 失敗時はSelf-Correction最大3回、超過時は停止してDecision Queueへ返却。
- 公開状態: `reference-only`（下流は参照のみ）。


## Stream B Serial Contract Alignment (2026-04-17)

### Phase 1 Read（Dependencies / State Transition / Fail-safe 再読）
- 再読対象を本メモと `issue-HIL-RS-02-next-phase-delivery-plan.md` の2件に固定し、`Dependencies` / `State Transition Contract` / `Fail-safe` の3要素だけを点検。
- 確認結果: 依存記述は「実装完了待ち」ではなく、`a1Status=="Done" && pendingDecisionQueueCount==0` の状態遷移契約へ統一可能。

### Phase 2 ADR CDC（変更明文化・承認待ち）
- Context: Stream B は planning-only であり、A1契約値は read-only 参照に限定する。
- Decision: 依存の正規表現を `state-transition gate` に統一し、着手可否をゲート式でのみ判定する。
- Consequences: 既存ファイル依存を「参照導線」と「状態遷移契約」に分離し、契約不一致はA1へ差し戻す。
- Decision Status: `Pending Approval`（CDC承認待ちのため確定扱いしない）。

### Phase 3 Plan（AC/DoD不足提案）
- AC提案: `dependencyExpressionDrift=0`, `gateExpressionDrift=0`, `failSafeDrift=0`, `pendingBypass=0`。
- DoD提案: `Read -> CDC -> Plan -> Execute -> Verify -> Proceed` の各フェーズ証跡を本メモに残す。
- 合意状態: `agreementStatus=pending_approval`（承認前は `Draft/Open(hold)` を維持）。

### Phase 4 Execute（依存記述の契約統一）
- 本メモの `Dependencies` は `state-transition gate` を明示する記述へ統一。
- `Go/NoGo` 判定・禁止遷移・差戻し先A1は既存契約を維持し、再定義しない。

### Phase 5 Verify（docs-check + diff整合）
- 検証コマンド正本: `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`。
- 差分整合: `rg` で `state-transition gate`, `a1Status=="Done" && pendingDecisionQueueCount==0`, `Fail-safe` を照合。
- 自己修復上限: 3回（4回目相当は停止）。

### Phase 6 Proceed（未解決の返却）
- 未承認CDC・未定義競合・前提崩れは Decision Queue へ返却し、推測で確定しない。
- Proceed条件は既存どおり `a1Status=="Done" && pendingDecisionQueueCount==0`。


## Stream A Serial Governance Record (2026-04-17)

### Phase 1 Read
- 本メモと Stream A 編集許可4ファイルを再読し、固定値・契約ID・Proceedゲートに想定差分ゼロを確認。
- 差分ゼロ確認項目: `schemaVersion=1.0.0` / `overridePolicy=human_dual_control_only` / `contractLinkLocked=true` / `sharedResourceFreeze=true` / `a1Status=="Done" && pendingDecisionQueueCount==0`。

### Phase 2 ADR CDC
- Context: 本Issueは HIL-RS umbrella の統治計画正本であり、A1契約値の再定義を禁止する必要がある。
- Decision: CDCの追加起票は不要（既存CDCで足りる）。契約差分要求はA1へ差戻し固定。
- Consequences: A2/A3の開始判定は read-only 参照のみで運用し、Pending の暗黙解決を禁止する。

### Phase 3 Plan
- AC/DoD不足なしを再確認（不足発生時のみCDCドラフト起票）。
- 合意済みProceed条件を維持: `Proceed = (a1Status=="Done" && pendingDecisionQueueCount==0)`。

### Phase 4 Execute
- 契約境界を再固定:
  - Go/NoGo: `Go = (a1Status=="Done" && pendingDecisionQueueCount==0)`, `NoGo = !Go`
  - 停止条件: 固定識別子不一致 / 未承認確定化 / SafeMode後退要求 / Self-Correction 3回超過

### Phase 5 Verify / Proceed
- docs-check 実行: `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`（Pass）。
- Proceed判定: `a1Status=="Done" && pendingDecisionQueueCount==0` 未達時は NoGo とし、A1差戻しを継続。

## Stream E Contract Advancement Update (2026-04-17)

### Phase 1) Read同期（4ファイル固定）
- Read対象を以下4ファイルに固定し、他ストリーム成果へ依存しないことを確認。
  1. `issue-HIL-RS-01-next-phase-human-loop-reversible-synthesis.md`
  2. `issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`
  3. `issue-HIL-RS-02-next-phase-delivery-plan.md`
  4. `issue-HIL-RS-02-A1-governance-contract-hardening.md`
- 再確認項目: `a1Status=="Done" && pendingDecisionQueueCount==0`、`schemaVersion=1.0.0`、`overridePolicy=human_dual_control_only`、`contractLinkLocked=true`、`sharedResourceFreeze=true`。

### Phase 2) CDC起票/更新（ADR要件）
- Context: HIL-RS契約の進行判定が複数記述に分散すると、A2/A3の誤Open化が発生しうる。
- Decision: Stream E は4ファイル内でのみ契約判定を固定し、A1先行（A1完了前はA2/A3開放禁止）を維持する。
- Consequences: 契約差分要求はA1に集約し、承認済みになるまで `Open(hold)` を維持する。

### Phase 3) Plan（A1先行・A2/A3開放条件）
- A1先行条件（固定）:
  - `A1 Gate = (a1Status=="Done")`
- A2/A3開放条件（固定）:
  - `OpenAllowed = (a1Status=="Done" && pendingDecisionQueueCount==0 && schemaVersion=="1.0.0" && overridePolicy=="human_dual_control_only" && contractLinkLocked==true && sharedResourceFreeze==true)`
- Phase進行条件（承認ゲート）:
  - `phaseApprovalRequired=true`
  - `approvalStatus!="approved"` の間は次Phaseへ進まない。

### Phase 4) Execute（契約固定）
- 契約固定対象:
  - Freeze Pack: `HIL-RS-02-A1-CONTRACT-FREEZE-v1`
  - Contract IDs: `A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|A1-ERROR-IF`
- 禁止事項（再確認）:
  - `Pending` bypass
  - A1未完了でのA2/A3 `Draft -> Open`
  - SafeMode既定ON / share-export漏えい防止 / `human_dual_control_only` の後退

### Phase 5) Verify（条件一致監査）
- 実行コマンド（4ファイル閉域）:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
  - `rg -n 'a1Status=="Done" && pendingDecisionQueueCount==0|schemaVersion=1.0.0|overridePolicy=human_dual_control_only|contractLinkLocked=true|sharedResourceFreeze=true|HIL-RS-02-A1-CONTRACT-FREEZE-v1|A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|A1-ERROR-IF|phaseApprovalRequired=true|approvalStatus!="approved"' 01_Plans/issues/issue-HIL-RS-01-next-phase-human-loop-reversible-synthesis.md 01_Plans/issues/issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md 01_Plans/issues/issue-HIL-RS-02-next-phase-delivery-plan.md 01_Plans/issues/issue-HIL-RS-02-A1-governance-contract-hardening.md`
- Self-Correction上限: 3回。

### Phase 6) Proceed（Open化条件の提案）
- 提案Open化条件:
  1. `approvalStatus=="approved"`
  2. `OpenAllowed==true`
  3. `Pending` 件数0
- 1つでも未充足なら `Proceed=NoGo` とし、Decision Queueへ戻す。

## Stream D Plan Synchronization Record (2026-04-18)

### Phase 1 Read
- 対象4ファイルを再読し、Unlock式の一致を確認。
- 一致式（固定）: `a1Status=="Done" && pendingDecisionQueueCount==0`。

### Phase 2 ADR CDC
- Context: Umbrella計画でUnlock式が複数化するとA2/A3のOpen判定が分岐する。
- Decision: A1ゲートは単一式に固定し、A1完了前はA2/A3をOpenしない。
- Consequences: 未承認の確定化は禁止。未解決項目はDecision Queueへ保持。
- Decision Status: Pending Approval（追加確定は承認待ち）。

### Phase 3 Plan
- AC/DoD補完:
  - `A1完了前にA2/A3をOpenしない` 規約を固定。
  - `Plan -> Execute -> Verify -> Proceed` を必須サイクル化。

### Phase 4 Execute
- 状態遷移契約を同期:
  - 許可: `DecisionQueue: Pending -> Approved | Rejected`
  - 禁止: `Pending bypass` / `a1Status!="Done"` での `A2/A3 Draft -> Open`
  - 停止: 式不一致、未承認確定化、修復3回超過

### Phase 5 Verify
- Verify式: `a1Status=="Done" && pendingDecisionQueueCount==0`。
- docs-check実施を必須化し、失敗時は最大3回修復。

### Phase 6 Proceed
- Proceedは式一致時のみ許可。
- 不一致時は即停止し、Decision Queueへ返却。

## Stream A Execution Record (2026-04-18, dedicated lane)

### Phase 1 Read（4ファイル差分一覧）
- Status差分: 全件 `Open`（差分なし）。
- Dependencies差分: 親計画として `state-transition gate` を依存宣言し、A1系2件を上流参照。
- Gate式差分: 実効式は全件 `a1Status=="Done" && pendingDecisionQueueCount==0` で一致（差分なし）。

### Phase 2 ADR CDC
- Context: 親計画のゲート分岐は下流誤遷移を生むため禁止。
- Decision: 新規方針追加を行わず、既存CDCに従った契約同期のみ実施。
- Consequences: 未承認・未確定は Proceed させず Decision Queue 保持。
- Approval: `agreementStatus=agreed`（同期作業として合意）。

### Phase 3 Plan（Checklist宣言）
- `Plan -> Execute -> Verify -> Proceed` を検証チェックリストとして宣言。
- AC/DoD不足はなし。Proceed前提を `agreementStatus=agreed` に固定。

### Phase 4 Execute
- 契約語彙、禁止遷移、差戻し条件をA1正本に同期。
- 明示禁止: A2/A3側で固定値の再定義・上書き。

### Phase 5 Verify
- docs-check相当（validator + rg）で一致確認。
- self-correction最大3回、4回目相当で停止。

### Phase 6 Proceed
- Gate成立時のみ進行し、未確定論点は Decision Queue に戻す。

## Stream B HIL-RS Execution Planning Update (2026-04-18)

### Phase 1) Read（最新メタ再読）
- 再読対象を本Issueと `issue-HIL-RS-02-next-phase-delivery-plan.md` の2件に限定し、`ADR-0026` / `ADR-0027` / `ADR-0028` の固定契約と整合することを再確認。
- 固定参照値は `MOCK-CONTRACT-SNAPSHOT-HIL-RS-v1` と `HIL-RS-02-A1-CONTRACT-FREEZE-v1` のみを採用し、A2/A3での契約再定義を禁止。

### Phase 2) Plan設計（AC / DoD / 検証計画）
- AC:
  1. `Go/NoGo` が単一式（`a1Status=="Done" && pendingDecisionQueueCount==0`）で機械判定可能。
  2. 固定識別子（`schemaVersion=1.0.0`, `overridePolicy=human_dual_control_only`, `contractLinkLocked=true`, `sharedResourceFreeze=true`）の一致を必須化。
  3. `Pending bypass=0` と安全境界後退要求=0 を同時成立条件とする。
- DoD:
  - `Plan -> Execute -> Verify -> Proceed` の順序証跡を本Issueに記録し、未承認決定を確定扱いしない。
- 検証計画:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
  - `rg` による Gate式・固定識別子・禁止遷移の一致確認。

### Phase 3) モック前提化（I/F依存の切断）
- A2/A3は Freeze Pack の read-only consumer として扱い、I/F依存は `freezeContractId` + `contractIds` 参照に切断。
- 契約差分要求は `issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md` へ差し戻し、下流Issueでの局所補完を禁止。

### Phase 4) Verify（依存 / 優先度 / 責務境界の整合）
- 依存整合: `A1 -> A2 -> A3` を維持し、A1未完了時は A2/A3 を `Draft/Open(hold)` へ固定。
- 優先度整合: 安全境界（SafeMode既定ON / share-export漏えい防止 / `human_dual_control_only`）を最優先条件として評価。
- 責務境界整合: Stream B は planning-only を維持し、architecture / implementation の変更提案を含めない。

### Phase 5) Proceed（次の1手固定）
- 次の1手（固定）:
  1. `validate_active_issue_memos.py` 実行結果を基準に Go/NoGo を更新。
  2. `NoGo` の場合は Decision Queue へ返却し、Yes/No 形式で未確定論点を記録。
  3. `Go` の場合でも A2/A3 へは read-only handoff pack（Gate式・固定識別子・禁止遷移）のみ連携。
- フェイルセーフ:
  - Self-correction は最大3回。4回目相当で停止し、承認待ちへ遷移。
