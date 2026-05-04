# Issue Draft: HIL-RS-02 次フェーズ実行計画（Stream D 自己完結版）

- Type: Process
- Status: Open
- Source Issue: N/A
- Lifecycle: Draft -> Open -> In Progress -> Done
- Priority: P1
- Owner: Stream D Agent（Delivery Plan Self-Contained）
- Scope: `01_Plans/issues/issue-HIL-RS-02-next-phase-delivery-plan.md` のみ
- Dependencies (minimal): `HIL-RS-02-A1-CONTRACT-FREEZE-v1`（参照固定）, `A1-GOV-GATE-V1` / `A2-PROPOSAL-ENVELOPE-V1` / `A3-DOC-SYNC-CHECK-V1`（mock契約ID参照のみ）
- Related ADR/Spec: `ADR-0026`, `ADR-0027`, `ADR-0028`
- Expected verification level: `docs-check`

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

## 1. 独立実行ルール（Stream D 固定）
- 他レーン進捗は参照しない（状態収集・進捗推定・完了見込み推測を禁止）。
- 参照可能な外部入力は mock契約ID のみ（値の再定義は禁止）。
- allowlist外編集は禁止（本ファイル以外の編集要求は即停止対象）。
- Self-Correction は最大3回（`0/3` 開始、再試行ごとに `+1`、`>=4` で即停止報告）。

---

## Phase 1. Read（固定ガードレール再確認）

### Plan
- 固定ガードレールと独立実行ルールを再確認し、開始時点の逸脱有無を記録する。

### Execute
- Guardrail snapshot を本文 `0. Fixed Guardrails` と照合。
- 独立実行ルール（他レーン非参照 / mock契約ID限定 / allowlist外編集禁止）を再宣言。
- Self-Correction counter を `0/3` に初期化。

### Verify
- ガードレール項目の欠落・改変がない。
- 逸脱検知時の即停止条件が明記されている。

### Proceed
- 逸脱ゼロなら Phase 2 へ進行。

---

## Phase 2. ADR（Context / Decision / Consequences）

### Plan
- Stream D 単独で自己完結可能な意思決定を ADR 形式で固定する。

### Execute
#### Context
- Delivery Plan が外部進捗参照を前提にすると、実行可能範囲と停止条件が曖昧化する。
- 本タスクは単一ファイル編集・mock契約参照のみで自己完結する必要がある。

#### Decision
- D1: Stream D の責務を `Gate判定ログ整備 / AC-DoD照合 / 停止条件固定` に限定する。
- D2: 他レーン状態は入力として扱わず、参照は mock契約ID の存在確認に限定する。
- D3: `Approval Record: Pending` が残る間は `Conditional` を維持し、確定Goを宣言しない。

#### Consequences
- 外部進捗に依存せず、文書単体で再開可能な運用ログを維持できる。
- 依存未解決時も推測実装を避け、停止判断を即時に実行できる。

### Verify
- Context / Decision / Consequences がすべて存在し、相互矛盾がない。

### Proceed
- 欠落がなければ Phase 3 へ進行。

---

## Phase 3. Plan（依存分解と切断案定義）

### Plan
- 依存を `論理依存` と `資源依存` に分解し、Stream Dで切断可能な境界を定義する。

### Execute
#### 論理依存（Logical）
- L1: `freezeContractId` 一致確認
- L2: `Approval Record` 状態確認（Pending/Approved/Rejected）
- L3: `A2A3_OPEN_ALLOWED` 判定可能性（入力整合のみ確認）

#### 資源依存（Resource）
- R1: 承認証跡入力（`approved_by / approved_at / evidence`）
- R2: docs-check 実行環境
- R3: mock契約ID定義の可読性

#### 切断案（Stream D 自己完結）
- C1: 他レーン進捗説明を排除し、契約ID参照のみ保持する。
- C2: 実装進捗管理を責務外とし、Gate判定ログ管理に限定する。
- C3: 未承認時は `Conditional` 固定で Plan/Verify のみ継続可能とする。

### Verify
- 依存が `L1-L3 / R1-R3` に分類され、切断案 `C1-C3` が明示されている。

### Proceed
- 充足なら Phase 4 へ進行。

---

## Phase 4. Execute（Gate判定ログ中心更新）

### Plan
- Gate判定ログを中心に、実行状態・停止条件・エスカレーション条件を固定する。

### Execute
#### Gate判定ログ（本Issue管理対象）
- GATE-01 `A1-GOV-GATE-V1`: **Conditional**（Approval Record 入力待ち）
- GATE-02 `A2-PROPOSAL-ENVELOPE-V1`: **Ready-By-Contract**（契約ID参照のみ完了）
- GATE-03 `A3-DOC-SYNC-CHECK-V1`: **Ready-By-Contract**（同期I/F参照のみ完了）

#### 停止条件（Stop）
- S1: `self_correction_attempt >= 4`
- S2: pending bypass 検知
- S3: 固定ガードレール改変要求
- S4: allowlist外編集要求

#### エスカレーション条件
- E1: `Approval Record` の責務分離違反
- E2: `A2A3_OPEN_ALLOWED` 判定不能（入力欠落/矛盾）
- E3: `NoGo return path` 変更要求
- E4: mock契約にない入力値の参照要求

### Verify
- Gate判定ログ、Stop条件 S1-S4、Escalation条件 E1-E4 が明記されている。

### Proceed
- 欠落がなければ Phase 5 へ進行。

---

## Phase 5. Verify（AC/DoD一致と停止条件確認）

### Plan
- 全Phaseの受入条件（AC）と完了定義（DoD）を照合し、停止条件の有効性を確認する。

### Execute
- Self-Correction counter: `0/3`（今回更新時点）
- docs-check コマンド（固定）:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
  - `python3 -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `git diff --check`

### Verify
#### AC
- AC-1: 6フェーズ（Read/ADR/Plan/Execute/Verify/Proceed）が順序通り定義されている。
- AC-2: 依存分解（Logical/Resource）と切断案（C1-C3）が明示されている。
- AC-3: Gate判定ログが `Conditional/Ready-By-Contract` で明示されている。
- AC-4: Self-Correction 上限（最大3回）と停止条件（S1-S4）が固定されている。

#### DoD
- DoD-1: 本ファイルのみ更新（allowlist遵守）。
- DoD-2: 固定ガードレールの後退なし。
- DoD-3: 他レーン進捗の参照記述なし。
- DoD-4: mock契約ID参照境界が維持されている。
- DoD-5: 再開条件と停止報告条件が本文で追跡可能。

### Proceed
- 判定: **Conditional**（承認証跡入力待ちのため）。
- 停止条件確認: S1-S4 のいずれか成立時は即停止報告。

---

## Phase 6. Proceed（次回運用ログ化）

### Plan
- 次回再開に必要な最小運用ログを残し、自己完結ループを維持する。

### Execute
#### 次回再開チェックリスト
1. `freezeContractId` と Guardrail差分の再照合
2. `Approval Record` 入力有無の確認
3. `self_correction_attempt` の継続値確認（`<=3` 必須）
4. allowlist外編集要求の有無確認

#### 未解決論点（保持）
- O1: `approved_by / approved_at / evidence` の入力待ち
- O2: `A2A3_OPEN_ALLOWED` の最終Go判定は A1入力確定後に再評価

### Verify
- 再開手順が4項目で固定され、未解決論点が推測なしで保持されている。

### Proceed
- 次回開始点: **Phase 1 (Read 再確認) から再開**。
