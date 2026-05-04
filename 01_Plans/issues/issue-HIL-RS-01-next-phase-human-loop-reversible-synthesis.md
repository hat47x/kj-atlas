# Issue Plan: HIL-RS-01 次フェーズ実行計画（Human-in-the-loop / Reversible Synthesis）

- Type: Process
- Status: Open
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P1
- Owner: Architecture Owner (Stream A contracts)
- Dependencies: `01_Plans/issues/issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`（A1契約）, `01_Plans/issues/issue-HIL-RS-02-next-phase-delivery-plan.md`（実行接続）
- Scope: `01_Plans/issues/`（planning only / docs only）
- Editable policy: 本Issueのみ編集可（本ストリーム制約）
- Expected verification level: `docs-check`
- Contract baseline date: `2026-04-27`
- Related ADR/Spec:
  - `ADR-0026`（Context）
  - `ADR-0027`（Decision）
  - `ADR-0028`（Consequences）
  - `02_Architecture/hil_rs_01_a1_minimum_interface_contract.md`（SSOT）

## Stream E Serial Contract-Sync Protocol（2026-05-04）
- Fixed serial order: Phase 1（A1最小I/F再確認）→ Phase 2（RS-01計画整合）→ Phase 3（RS-02 A1 governance hardening）→ Phase 4（RS-02 delivery plan同期）→ Phase 5（RS-02 A3 mock準備）→ Phase 6（Verify総合判定）。
- Mandatory per-phase discipline: **対象ファイル再読 → Plan → Execute → Verify → Proceed**。
- Mandatory per-phase memo: 各Phaseで `Context / Decision / Consequences (C/D/Csq)` を必ず残す。
- Self-correction limit: `<=3`（4回目相当は即停止）。
- Hard stop conditions: `safeMode` 後退要求、契約ID再定義要求、pending bypass を検知した時点で即停止し、`NoGo return path` へ差戻す。

## 0. Fixed Governance Envelope（固定境界）

- `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`（再定義禁止）
- `schemaVersion=1.0.0`
- `overridePolicy=human_dual_control_only`
- `contractLinkLocked=true`
- `sharedResourceFreeze=true`
- `safeModeDefault=ON`（緩和禁止）
- `safeModeBoundary=SAFE_MODE_STRICT_ON`（緩和禁止）
- `decisionQueueTransition=Pending -> Approved | Pending -> Rejected`
- `NoGo return path=issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`（固定）

## 1. Global Execution Discipline（全Phase共通）

1. 各Phase開始時に **Read同期** を必須実施する。
   - 同期対象: `Status / Scope / Dependencies / fixed keys / NoGo return path`
2. 各Phaseは必ず **Plan → Execute → Verify → Proceed** の順で実行する。
3. AC/DoD不足を検知した場合、AIは `Draft` を提示し、`Approval Record` 合意まで Executeを拡張しない。
4. Self-Correctionは最大3回（`0/3`開始）。4回目相当は即停止。
5. 前提崩れ・未定義競合・allowlist外編集要求は即停止。

---

## 2. Phase 1: 計画分解（Plan decomposition）

### Plan
- 現行計画を以下の作業単位へ分解する。
  - W1: 契約固定値の検証単位
  - W2: 人間承認ループ（Approval Record）の検証単位
  - W3: 可逆性（NoGo差戻し）検証単位
  - W4: 安全境界（safeMode/override/freeze）検証単位
  - W5: A2/A3解放ゲート検証単位

### Execute
- 曖昧性を明示する。
  - A-1: 承認主体/時刻/証跡の入力責任が未確定
  - A-2: `held` に残す論点の完了定義が曖昧
  - A-3: Conditional継続とNo-Go移行の閾値説明が不足

### Verify
- 依存記述が `contract reference only` であることを確認。
- 実装依存（コード改修）記述が混入していないことを確認。

### Proceed
- Proceed条件: 曖昧性A-1〜A-3が「承認待ち論点」として明示済み。
- 停止条件: 固定キー差分を1件でも検出。

---

## 3. Phase 2: ADR-style 明文化（Context / Decision / Consequences）

### Context
- HIL-RS-01はHIL-RS-02へ接続する前段であり、契約値ドリフトを許容しない。
- 人間承認が未完了の状態での確定化はガバナンス違反となる。

### Decision
- 固定値は「参照のみ」で運用し、再定義しない。
- `Approval Record` が `Pending` を1件でも含む場合、`Phase 4 Execute` は禁止。
- `A2A3_OPEN_ALLOWED` は以下の全条件一致時のみ `true`:
  - `a1Status=="Done"`
  - `pendingDecisionQueueCount==0`
  - 固定境界（freezeContractId/schemaVersion/overridePolicy/contractLinkLocked/sharedResourceFreeze/safeModeDefault/safeModeBoundary）一致

### Consequences
- A1未完了または承認未了時、A2/A3は `Draft/Open` を変更しない。
- NoGo時は固定の差戻し先へ戻す。
- 未承認論点は `held` 維持（確定化しない）。

### Approval Record（必須）
- Status: `Pending`（初期値）
- Required: `approved_by`, `approved_at`, `evidence`

---

## 4. Phase 3: 依存切断（Interface-first / Implementation-separated）

### Plan
- タスクを「I/F先行で完了可能」か「実装依存」かで分離する。

### Execute
- I/F先行で完了可能（このIssueで扱う）:
  1. 契約固定値一覧
  2. 承認ゲート条件
  3. NoGo差戻し導線
  4. Conditional/No-Go判定ロジック
- 実装依存（このIssueでは扱わない）:
  1. 実コード側の状態遷移実装
  2. runtime連携の実装

### Mock適用ポイント
- A2/A3側は `mock I/F preparation only`。
- 利用可能な最小シグネチャ:

```yaml
stream_a_freeze:
  contract_id: HIL-RS-02-A1-CONTRACT-FREEZE-v1
  schema_version: 1.0.0
  override_policy: human_dual_control_only
  contract_link_locked: true
  shared_resource_freeze: true
  safe_mode_default: ON
  safe_mode_boundary: SAFE_MODE_STRICT_ON
gate:
  a2a3_unlock: a1Status == Done && pendingDecisionQueueCount == 0
```

### Verify
- I/F記述に実装確定の語彙（実装手段・詳細順序）が混入していないことを確認。

### Proceed
- Proceed条件: mock適用点と非対象（実装依存）が分離済み。

---

## 5. Phase 4: 実行計画化（Serial execution design）

### Plan
- 直列順序: `P1分解 -> P2明文化 -> P3依存切断 -> P4実行計画 -> P5検証`

### Execute
- 入口条件（Entry）
  - Read同期完了
  - 固定キー差分0
  - `Approval Record` 状態明示
- 出口条件（Exit）
  - AC/DoD判定根拠を明示
  - `Go / Conditional / No-Go` を式で判定
- 停止条件（Stop）
  - `self_correction_attempt >= 4`
  - pending bypass検知
  - 未定義競合検知
  - allowlist外編集要求

### 判定式（固定）
- `ProceedGate = (A2A3_OPEN_ALLOWED && validatorPass==true)`
- `Go = ProceedGate`
- `Conditional = (!ProceedGate && heldCount>0 && unresolvedApprovalsAreHeldOnly)`
- `NoGo = (!ProceedGate && !Conditional)`

### Verify
- 判定式が再定義されず、固定のまま引用されていることを確認。

### Proceed
- NoGo時は `NoGo return path` へ差戻しを明記する。

---

## 6. Phase 5: Verify（AC/DoD・リスク・次アクション）

### AC（Acceptance Criteria）
- AC-1: 固定キー差分 `0`
- AC-2: `decisionQueueTransition` が固定値のまま
- AC-3: `NoGo return path` が一意固定
- AC-4: A2/A3は解放条件成立前に `Draft/Open` 変更なし

### DoD（Definition of Done）
- DoD-1: `safeModeDefault=ON` / `safeModeBoundary=SAFE_MODE_STRICT_ON` 後退なし
- DoD-2: `overridePolicy` 後退なし
- DoD-3: Self-Correction `<=3`
- DoD-4: `Approval Record` 未充足時は `Needs-decision` または `Conditional` 維持

### Risk register（残件）
1. 承認証跡未入力（`approved_by/approved_at/evidence`）
2. `held` 論点の人間判断待ち
3. pending queue未解消時の長期停滞

### Next one action
- 人間承認者が `Approval Record` 必須3項目を入力し、pending queue解消可否を判定する。

---

## 7. Validation Commands（docs-check）

- `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- `python3 -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
- `git diff --check`
