# Issue Draft: HIL-RS-02 次フェーズ実行計画（Stream G 自己完結版）

- Type: Process
- Status: Open
- Source Issue: N/A
- Lifecycle: Draft -> Open -> In Progress -> Done
- Priority: P1
- Owner: Stream G Agent（HIL-RS-02 delivery plan self-contained）
- Scope: `01_Plans/issues/issue-HIL-RS-02-next-phase-delivery-plan.md` のみ
- Dependencies (minimal): `01_Plans/issues/issue-HIL-RS-02-A1-governance-contract-hardening.md`（contract freeze参照）, `issue-HIL-RS-02-A2-frontend-reversible-synthesis-application.md` / `issue-HIL-RS-02-A3-operations-documentation-sync.md`（mock契約で並行可能）
- Related ADR/Spec: `ADR-0026`, `ADR-0027`, `ADR-0028`
- Expected verification level: `docs-check`

## Stream E Serial Contract-Sync Protocol（2026-05-04）
- Fixed serial order: Phase 1（A1最小I/F再確認）→ Phase 2（RS-01計画整合）→ Phase 3（RS-02 A1 governance hardening）→ Phase 4（RS-02 delivery plan同期）→ Phase 5（RS-02 A3 mock準備）→ Phase 6（Verify総合判定）。
- Mandatory per-phase discipline: **対象ファイル再読 → Plan → Execute → Verify → Proceed**。
- Mandatory per-phase memo: 各Phaseで `Context / Decision / Consequences (C/D/Csq)` を必ず残す。
- Self-correction limit: `<=3`（4回目相当は即停止）。
- Hard stop conditions: `safeMode` 後退要求、契約ID再定義要求、pending bypass を検知した時点で即停止し、`NoGo return path` へ差戻す。

## 0. Fixed Guardrails（変更禁止）
- `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
- `schemaVersion=1.0.0`
- `overridePolicy=human_dual_control_only`
- `contractLinkLocked=true`
- `sharedResourceFreeze=true`
- `safeModeDefault=ON`
- `safeModeBoundary=SAFE_MODE_STRICT_ON`
- `decisionQueueTransition=Pending -> Approved | Pending -> Rejected`
- `NoGo return path = issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`

## 1. 独立実行ルール（Stream G 固定）
- 他レーン進捗は参照しない（状態収集・進捗推定・完了見込み推測を禁止）。
- 参照可能な外部入力は mock契約ID のみ（値の再定義は禁止）。
- allowlist外編集は禁止（本ファイル以外の編集要求は即停止対象）。
- Self-Correction は最大3回（`0/3` 開始、再試行ごとに `+1`、`>=4` で即停止報告）。

---

## Phase 1. Read

### Plan
- 固定ガードレールと独立実行ルールを再確認し、開始時点の逸脱有無を記録する。

### Execute
- Guardrail snapshot を本文 `0. Fixed Guardrails` と照合。
- 独立実行ルール（他レーン非参照 / mock契約ID限定 / allowlist外編集禁止）を再宣言。
- Self-Correction counter を `0/3` に初期化。

### Verify
- ガードレール項目の欠落・改変がない。
- 逸脱検知時の即停止条件が明記されている。

---

## Phase 2. ADR明文化（Context / Decision / Consequences）

### Context
- Delivery Plan が外部進捗参照を前提にすると、実行可能範囲と停止条件が曖昧化する。
- 本タスクは単一ファイル編集・mock契約参照のみで自己完結する必要がある。

### Decision
- D1: Stream G の責務を `Gate判定ログ整備 / AC-DoD照合 / 停止条件固定` に限定する。
- D2: 他レーン状態は入力として扱わず、参照は mock契約ID の存在確認に限定する。
- D3: `Approval Record: Pending` が残る間は `Conditional` を維持し、確定Goを宣言しない。

### Consequences
- 外部進捗に依存せず、文書単体で再開可能な運用ログを維持できる。
- 依存未解決時も推測実装を避け、停止判断を即時に実行できる。

### Verify
- Context / Decision / Consequences がすべて存在し、相互矛盾がない。

---

## Phase 3. Plan（AC/DoD補完・非目標固定）

### AC（Acceptance Criteria）
- AC-1: 6フェーズ（Read / ADR明文化 / Plan / Execute / Verify / Stop）が順序通り定義されている。
- AC-2: 依存分解（Logical/Resource）と切断案（C1-C3）が明示されている。
- AC-3: Gate判定ログが `Conditional / Ready-By-Contract` で明示されている。
- AC-4: Self-Correction 上限（最大3回）と停止条件（S1-S4）が固定されている。

### DoD（Definition of Done）
- DoD-1: 本ファイルのみ更新（allowlist遵守）。
- DoD-2: 固定ガードレールの後退なし。
- DoD-3: 他レーン進捗の参照記述なし。
- DoD-4: mock契約ID参照境界が維持されている。
- DoD-5: 再開条件と停止報告条件が本文で追跡可能。

### 非目標（Out of Scope）
- N1: A1/A2/A3 の実装進捗管理・完了見込みの推定。
- N2: 共有リソース（dashboard/README/他issue）の編集。
- N3: mock契約ID以外の新規入力値定義。

### 依存分解
#### 論理依存（Logical）
- L1: `freezeContractId` 一致確認
- L2: `Approval Record` 状態確認（Pending/Approved/Rejected）
- L3: `A2A3_OPEN_ALLOWED` 判定可能性（入力整合のみ確認）

#### 資源依存（Resource）
- R1: 承認証跡入力（`approved_by / approved_at / evidence`）
- R2: docs-check 実行環境
- R3: mock契約ID定義の可読性

#### 切断案（Stream G 自己完結）
- C1: 他レーン進捗説明を排除し、契約ID参照のみ保持する。
- C2: 実装進捗管理を責務外とし、Gate判定ログ管理に限定する。
- C3: 未承認時は `Conditional` 固定で Plan/Verify のみ継続可能とする。

---

## Phase 4. Execute（self-contained計画更新）

### Gate判定ログ（本Issue管理対象）
- GATE-01 `A1-GOV-GATE-V1`: **Conditional**（Approval Record 入力待ち）
- GATE-02 `A2-PROPOSAL-ENVELOPE-V1`: **Ready-By-Contract**（契約ID参照のみ完了）
- GATE-03 `A3-DOC-SYNC-CHECK-V1`: **Ready-By-Contract**（同期I/F参照のみ完了）

### 停止条件（Stop）
- S1: `self_correction_attempt >= 4`
- S2: pending bypass 検知
- S3: 固定ガードレール改変要求
- S4: allowlist外編集要求

### エスカレーション条件
- E1: `Approval Record` の責務分離違反
- E2: `A2A3_OPEN_ALLOWED` 判定不能（入力欠落/矛盾）
- E3: `NoGo return path` 変更要求
- E4: mock契約にない入力値の参照要求

---

## Phase 5. Verify（3回修復まで）

### Execute
- Self-Correction counter: `0/3`（今回更新時点）
- docs-check コマンド（固定）:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
  - `python3 -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `git diff --check`

### Verify
- AC-1〜AC-4 を満たす。
- DoD-1〜DoD-5 を満たす。
- 3回修復上限（`<=3`）を超える場合は Phase 6 へ強制遷移する。
- 判定: **Conditional**（承認証跡入力待ちのため）。

---

## Phase 6. Stop（致命条件で停止）

### 致命停止条件
1. `self_correction_attempt >= 4`
2. pending bypass を検知
3. 固定ガードレール改変要求を受領
4. allowlist外編集要求を受領

### 停止時報告テンプレ
- `stop_reason`: `S1|S2|S3|S4`
- `last_safe_phase`: `Read|ADR|Plan|Execute|Verify`
- `guardrail_diff`: `none|detected`
- `next_action`: `NoGo return pathへ差戻し`

### 次回再開チェックリスト（停止しなかった場合のみ）
1. `freezeContractId` と Guardrail差分の再照合
2. `Approval Record` 入力有無の確認
3. `self_correction_attempt` の継続値確認（`<=3` 必須）
4. allowlist外編集要求の有無確認

### 未解決論点（保持）
- O1: `approved_by / approved_at / evidence` の入力待ち
- O2: `A2A3_OPEN_ALLOWED` の最終Go判定は A1入力確定後に再評価


## Stream B Sync Snapshot（2026-05-04 / Read&Gap→ADR→Dependency-cut→Verify）

### 1) Dependency / Ready / Blocker 再検証
- dependency_state: `contract-first` を維持（実装完了待ちを Ready 条件に含めない）。
- ready_contract: `freezeContractId/schemaVersion/overridePolicy/safeModeDefault` 一致。
- ready_execution: `approved_by/approved_at/evidence` 充足かつ `Decision Queue Pending=0`。
- blockers_normalized:
  - `approval_pending`
  - `decision_queue_pending`
  - `contract_mismatch`
  - `out_of_scope_request`

### 2) AC/DoD 不足補完ドラフト（合意用）
- AC-draft-1: Ready 判定を `contract-ready` と `execution-ready` に二分し、両方の結果を記録する。
- AC-draft-2: Blocker は正規化4分類のみ使用し、自由記述のみで終わらせない。
- DoD-draft-1: `mock parallelizable items` を最低1件以上列挙する。
- DoD-draft-2: verify の自己修復回数を `<=3` で記録し、`>=4` は停止報告とする。

### 3) 依存切断（実装依存→契約依存）
- replace_rule: 実装依存の待ち条件は、同等の契約キー検証へ置換する。
- mock_parallelizable_items:
  1. Contract ID / fixed key 一致検証
  2. Gate 式（Go/Conditional/No-Go）の入力完全性検証
  3. Audit 4点セット（`query/bundle/proposal/apply`）欠損検知

### 4) Verify（triage再実行）
- command: `python 01_Plans/triage_actionable_plans.py`
- note: Ready/Blocked/Unlocks は triage 出力を正本とし、本Issue記録はその解釈補助とする。
- self_correction: `0/3`（本更新時点）
## Stream E Update（2026-05-05 / HIL-RS-02 delivery & operations sync prep）

### Phase 1 Read（対象2ファイル再読・差分確認）
#### Context
- 対象は `issue-HIL-RS-02-next-phase-delivery-plan` と `issue-HIL-RS-02-A3-operations-documentation-sync` の2ファイルのみ。
- A1系は read-only 参照であり、未確定事項の推測確定は禁止。

#### Decision
- 差分確認の観点を `固定キー / Gate式 / Open条件 / Hold条件 / NoGo return path` に固定する。
- A3は `mock I/F preparation only` を維持し、実装変更を伴う要求は受付しない。

#### Consequences
- 依存未充足時でも、準備計画の品質を独立に維持できる。

### Phase 2 ADR/CDC（未確定依存の明示）
#### Context
- A1 `Approval Record` は Pending のままで、`approved_by / approved_at / evidence` が未確定。
- `a1Status==Done` および `pendingDecisionQueueCount==0` の最終確定はA1入力に依存する。

#### Decision
- 未確定事項を以下として固定し、確定表現を禁止する。
  1. A1承認証跡の入力完了時刻
  2. pendingDecisionQueueCount の正本値
  3. A3 Open判定の最終Go可否
- A1未完了を前提に、判定は `Conditional/Hold` のみ許可する。

#### Consequences
- 依存推測による premature Open を防止する。

### Phase 3 Plan（A3 mock I/F preparation only AC/DoD）
#### Decision
- AC-A3-M1: fixed keys diff=0 を維持する。
- AC-A3-M2: role vocabulary drift=0 を維持する。
- AC-A3-M3: ProceedGateは参照のみ（再定義禁止）。
- AC-A3-M4: A1未完時は Draft維持（Open遷移禁止）。
- DoD-A3-M1: docs-check計画（validator/unittest/diff/scope）が明記されている。
- DoD-A3-M2: NoGo return path がA1 issueへ一意に固定されている。
- DoD-A3-M3: self-correction上限 `<=3` が明記されている。

### Phase 4 Execute（運用同期計画整理のみ）
#### Decision
- 実行内容を「運用同期計画の整理（文書更新）」に限定し、コード・実装・README系更新は実施しない。
- 同期導線は `02_Architecture -> 04_Documentation -> 01_Plans -> AGENTS.md` を参照順として保持する。

#### Consequences
- Stream Eの責務を計画同期に限定し、越境変更を回避する。

### Phase 5 Verify（Draft/Open昇格条件と検証レベル整合）
#### Decision
- 検証レベルは `docs-check` を維持する。
- Draft/Open判定を次で固定する。
  - Open可: `ProceedGate=true` かつ AC/DoD充足
  - Draft維持: `PrepGate=true` かつ `a1Status!=Done`
  - Hold/No-Go: pending bypass / fixed key drift / self_correction_attempt>=4
- 修復は最大3回まで。4回目相当は即停止。

#### Consequences
- 検証失敗時の挙動が deterministic になり、再開判断が容易になる。

### Phase 6 Proceed（Proceed条件 / Hold理由）
#### Decision
- 現時点判定: **Hold**。
- Hold理由:
  1. A1 Approval Record が Pending。
  2. `a1Status==Done` 未確定のため ProceedGate未成立。
  3. A3は mock I/F preparation only の範囲を維持中。
- Proceed再開条件:
  - `approved_by / approved_at / evidence` 充足
  - `pendingDecisionQueueCount==0`
  - fixed keys diff=0 維持

#### Consequences
- A1未完了を前提にした強行を回避し、fail-safe制約に整合する。


## Stream G Quick Sync (2026-05-05 / Phase 1-5 compressed)

### Phase 1 Read（issue現況同期）
- Status/Priority/Scope/Dependencies を再確認し、本ファイルの既存定義と矛盾がないことを確認。
- 未確定事項は `held` / `Pending` のまま維持し、確定化しない。

### Phase 2 Plan（優先順位・ブロッカー再定義）
- 優先順位を `contract-first` で固定し、実装進捗ではなく契約整合を先行。
- Blocker を次の正規化キーに限定: `approval_pending`, `decision_queue_pending`, `contract_mismatch`, `out_of_scope_request`。

### Phase 3 Execute（Issue本文の整理、依存明示）
- 依存を `A1 contract freeze -> A2 mock validation -> A3 implementation/sync` の順序で明示し、A2/A3の先行確定を禁止。
- `A2A3_OPEN_ALLOWED` / `ProceedGate` / `NoGo` は参照専用（再定義禁止）として本文整合を維持。

### Phase 4 Verify（ready/blocked判定整合）
- Ready は `contract-ready` と `execution-ready` の2層で評価。
- `approved_by/approved_at/evidence` 未入力、または `pendingDecisionQueueCount>0` の場合は `blocked` 扱い。
- self-correction は `<=3` を上限とし、`>=4` は停止。

### Phase 5 Proceed（次行動を1手に圧縮）
- **Next One Action**: `Approval Record（approved_by / approved_at / evidence）をA1正本へ入力し、pendingDecisionQueueCount を 0 に更新する。`


## Stream F Execution Update（2026-05-05）

### 1. Read同期
- 対象文書内の固定ガードレール・停止条件・Self-Correction上限（<=3）を再確認。
- Scopeを本ファイル限定として再固定（allowlist外編集禁止）。

### 2. Plan（AC/DoD不足補完）
- AC-F1: Phaseを `Read同期 -> Plan -> ADR C/D/C -> Execute -> Verify -> Proceed` の順序で明示。
- AC-F2: Proceed判定を `Ready / Hold / Needs-decision` の三値で固定。
- DoD-F1: A1未確定事項を推測で埋めず、「前提条件・リスク」として明記。
- DoD-F2: 判定に必要な入力不足時は `Hold` または `Needs-decision` を選択し、Go確定を禁止。

### 3. ADR C/D/C（必要時）
#### Context
- A1 `Approval Record`（`approved_by / approved_at / evidence`）は未確定の可能性があり、確定Go判定の前提が欠ける場合がある。

#### Decision
- D-F1: A1未確定時は `Proceed=Hold` を既定とする。
- D-F2: 判定不能な入力欠落・矛盾がある場合は `Proceed=Needs-decision` とする。

#### Consequences
- 推測埋めを回避し、未確定論点を可視化したまま安全に継続/停止判定できる。

### 4. Execute（delivery planの具体化）
- Proceed判定ルールを次で運用する。
  - `Ready`: 契約固定キー整合 + A1承認証跡充足 + pending bypassなし。
  - `Hold`: 前提不足（例: A1承認証跡未充足）で安全側待機が妥当。
  - `Needs-decision`: 入力矛盾・責務境界の衝突・NoGo経路変更要求など、上位判断が必要。
- Self-Correctionカウンタは `0/3` から開始し、`>=4` は即停止（既存S1整合）。

### 5. Verify（最大3回の自己修復）
- 検証観点:
  1. 本ファイルのみ更新（allowlist遵守）
  2. 固定ガードレールの後退なし
  3. A1未確定事項を「前提条件・リスク」として明示
  4. Proceed三値（Ready/Hold/Needs-decision）が定義済み
- 修復回数が3回を超える場合は検証継続せず停止報告へ遷移。

### 6. Proceed（Ready/Hold/Needs-decision）
- 現時点判定: **Hold**。
- 前提条件（A1未確定事項）:
  - `approved_by / approved_at / evidence` の正本入力完了。
  - `pendingDecisionQueueCount` の確定値提示。
- リスク:
  - 前提未充足のままGo判定すると、pending bypassと同義の運用逸脱になる。
- Ready移行条件:
  - 固定ガードレール整合を維持したまま、前提条件がすべて充足すること。
- Needs-decision遷移条件:
  - 前提入力の矛盾、責務分離違反、または NoGo return path の再定義要求が発生した場合。
