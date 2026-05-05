# Issue Draft: HIL-RS-01 A1 Architecture 最小I/F契約固定

- Type: Process
- Status: Open
- Lifecycle: Draft -> Open -> In Progress -> Done
- Priority: P1
- Source Issue: N/A
- Related ADR/Spec: `ADR-0026`, `ADR-0027`, `ADR-0028`, `02_Architecture/hil_rs_01_a1_minimum_interface_contract.md`
- Owner: Stream E (Architecture Minimum I/F Contract)
- Dependencies: `01_Plans/issues/issue-HIL-RS-01-next-phase-human-loop-reversible-synthesis.md`（計画親）, `01_Plans/issues/issue-HIL-RS-02-A1-governance-contract-hardening.md`（後続が参照）
- Scope: `01_Plans/issues/issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md` のみ
- Expected verification level: `docs-check`
- Contract snapshot date: `2026-04-27`（固定入力）

## Stream E Serial Contract-Sync Protocol（2026-05-04）
- Fixed serial order: Phase 1（A1最小I/F再確認）→ Phase 2（RS-01計画整合）→ Phase 3（RS-02 A1 governance hardening）→ Phase 4（RS-02 delivery plan同期）→ Phase 5（RS-02 A3 mock準備）→ Phase 6（Verify総合判定）。
- Mandatory per-phase discipline: **対象ファイル再読 → Plan → Execute → Verify → Proceed**。
- Mandatory per-phase memo: 各Phaseで `Context / Decision / Consequences (C/D/Csq)` を必ず残す。
- Self-correction limit: `<=3`（4回目相当は即停止）。
- Hard stop conditions: `safeMode` 後退要求、契約ID再定義要求、pending bypass を検知した時点で即停止し、`NoGo return path` へ差戻す。

## Stream E Execution Ledger（2026-05-04）
- Phase 1 Read: 完了（Status / Scope / 固定キー / Execute禁止条件を再確認）
- Phase 2 ADR明文化: 完了（Context / Decision / Consequences を実装非依存で固定）
- Phase 3 Plan（AC/DoD提案と合意）: 完了（本Issue内のAC/DoDをStream E提案版として凍結）
- Phase 4 Execute（minimum I/F定義具体化）: 完了（v1.0.0の入力・出力・遷移・非機能・禁止事項を固定）
- Phase 5 Verify: 完了（不一致修復 0/3、ドリフト 0）
- Stop条件判定: 未該当（3回超過なし、前提崩壊なし）


## Upstream Alignment Guard（ADR整合ガード）

- 本Issueは **contract-only** であり、実装記述（画面/コード/DB/運用手順の確定）は対象外。
- 上流整合の正本は `ADR-0026`（契約先行・HIL境界）、`ADR-0027`（凍結値・Go/NoGo統治）、`ADR-0028`（CE-0非後退契約）とする。
- 本Issueで定義する最小I/Fは次の不変条件を満たすこと。
  - AIは `proposal-only`（承認・昇格・本番適用を行わない）
  - 人間のみが `Pending -> Approved/Rejected` を確定できる
  - `safeModeDefault=ON` と `safeModeBoundary=SAFE_MODE_STRICT_ON` を後退させない
  - `NoGo return path` と `freezeContractId` を再定義しない

## Stream E Mission
HIL-RS-01 A1 の最小I/F契約を固定し、後続ストリーム（A2/A3）が **安全に並行実装** できる起点を提供する。

## Fixed Constraints（厳守）
- `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`（再定義禁止）
- `safeModeDefault=ON` / `safeModeBoundary=SAFE_MODE_STRICT_ON`（緩和禁止）
- `NoGo return path=issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`（変更禁止）
- `Approval Record: Pending` が1件でも残る場合、`Execute=Forbidden`（Plan/Verifyのみ許可）
- Self-Correction は最大3回。4回目相当または未定義競合を検出した時点で停止し、
  `原因 / 影響I/F / 人間判断論点` を記録する。

## Contract Vocabulary（固定語彙）
- `freezeContractId`
- `contractIds`
- `schemaVersion`
- `overridePolicy`
- `contractLinkLocked`
- `sharedResourceFreeze`
- `safeModeDefault`
- `safeModeBoundary`
- `unlockRule`
- `decisionQueueTransition`
- `NoGo return path`

## Contract Values（固定値）
- `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
- `contractIds=A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|A1-ERROR-IF`
- `schemaVersion=1.0.0`
- `overridePolicy=human_dual_control_only`
- `contractLinkLocked=true`
- `sharedResourceFreeze=true`
- `safeModeDefault=ON`
- `safeModeBoundary=SAFE_MODE_STRICT_ON`
- `unlockRule=a2a3Unlock = (a1Status=="Done" && pendingDecisionQueueCount==0)`
- `decisionQueueTransition=Pending -> Approved | Pending -> Rejected`

---

## Phase 1: 現況と不足抽出（Plan -> Execute -> Verify -> Proceed）

### Read同期（Phase開始時必須）
- 本Issueを再読し、`Status / Scope / 固定キー / Execute禁止条件` を再確認する。

### Plan
- 最小I/F定義で不足しやすい観点を先に固定する。
  1. **型**（入力/出力/エラー/識別子）
  2. **責務**（AIがやること・人間が承認すること）
  3. **禁止事項**（auto-apply、review自動昇格、safeMode緩和）

### Execute（docs-only）
- 不足抽出結果を下記に記録する。

### Verify
- 欠落が「型・責務・禁止事項」の3分類に収まっていることを確認。
- 未定義語の持ち込みがないことを確認。

### Proceed判定（Phase 2進行条件）
- 欠落項目がすべて列挙済みであること。

### Phase 1 Findings（最小I/F欠落の確定）
- 型: `request/response/error/audit` の最小項目が未固定だとストリーム間実装差分が発生する。
- 責務: `AI提案境界` と `人間承認境界` が曖昧だと `Pending bypass` が起きる。
- 禁止事項: `safeMode既定緩和` / `AI review auto promotion` / `consensus direct write` の禁止表現が不足すると監査不能になる。

---

## Phase 2: ADR-style 明文化（Plan -> Execute -> Verify -> Proceed）

### Read同期（Phase開始時必須）
- 固定語彙と固定値にドリフトがないことを再確認。

### Plan
- ADR形式（Context / Decision / Consequences）で、A1契約を **実装非依存** に固定する。

### Execute（contract-only）
### Context
- HIL-RS-01 A1は、A2/A3の並行実装時に参照される契約ゲートである。
- 契約が曖昧なまま進行すると、ストリーム間で判定式と責務境界が分岐し、後段で非可逆な統合作業が発生する。

### Decision
- A1は **contract freeze only** とし、実装最適化を含めない。
- 人間承認境界:
  - `Pending -> Approved/Rejected` の遷移確定は人間のみ。
  - `overridePolicy=human_dual_control_only` を必須化。
- AI責務境界:
  - AIは `proposal-only`。
  - AIは承認状態変更・レビュー昇格・本番適用を実行しない。

### Consequences
- A2/A3は同一契約IDをread-only参照し、独自派生定義を持てない。
- A1未完了またはPending残存時は、A2/A3 Executeは開始不可。
- 監査ログ不備時は fail-closed とし、Go判定しない。

### Verify
- Context/Decision/Consequences がすべて記載されていること。
- 人間承認境界とAI責務境界が分離されていること。

### Proceed判定（Phase 3進行条件）
- ADR-style 3要素に未記入項目がないこと。

---

## Phase 3: 契約固定（Plan -> Execute -> Verify -> Proceed）

### Read同期（Phase開始時必須）
- `freezeContractId` / `contractIds` / `unlockRule` の一致を再確認。

### Plan
- 入出力、状態遷移、非機能（監査/再現性）を最小I/Fとして固定する。

### Execute（contract-only）
### A1 Minimum Interface Contract（v1.0.0）

#### 1) Inputs
- `contractRequest`
  - `freezeContractId: string`（固定値一致必須）
  - `contractIds: string`（固定4 IDの連結表現）
  - `schemaVersion: "1.0.0"`
  - `safeModeDefault: "ON"`
  - `safeModeBoundary: "SAFE_MODE_STRICT_ON"`
  - `pendingDecisionQueueCount: number (>=0)`
  - `a1Status: "Open" | "In Progress" | "Done"`

#### 2) Outputs
- `contractDecision`
  - `executeAllowed: boolean`
  - `decision: "Go" | "NoGo" | "Hold"`
  - `reasonCodes: string[]`
  - `requiredHumanActions: string[]`
  - `noGoReturnPath: "issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md"`

#### 3) State Transition
- `Pending -> Approved | Pending -> Rejected` 以外の遷移は禁止。
- `a2a3Unlock = (a1Status=="Done" && pendingDecisionQueueCount==0)` のみ許可。
- `Approval Record: Pending` が1件でもある場合、`decision=Hold` かつ `executeAllowed=false`。

#### 4) Non-Functional Contract
- 監査:
  - すべての判定で `reasonCodes` を必須出力。
  - 判定時刻と判定主体（human/ai role）を追跡可能にする（記録先は実装側に委譲）。
- 再現性:
  - 同一入力に対して同一判定を返す（決定論）。
  - 固定値キー不一致時は fail-closed（`NoGo`）を返す。

#### 5) Prohibitions（禁止事項）
- `safeModeDefault` の既定緩和
- AIによる `Approved` への自動昇格
- `NoGo return path` の変更
- `freezeContractId` の再定義

### Verify
- I/Fが `入力 / 出力 / 状態遷移 / 非機能` の4区分で定義済み。
- 禁止事項が安全境界と整合。

### Proceed判定（Phase 4進行条件）
- 契約固定テキストが単独で読め、A2/A3が参照可能であること。

---

## Phase 4: mock検証計画（Plan -> Execute -> Verify -> Proceed）

### Read同期（Phase開始時必須）
- Execute禁止条件（Pending残存時禁止）を再確認。

### Plan
- 実装前に成立する契約準拠チェック（mock-first）を設計する。

### Execute
### Contract Compliance Check Plan（実装前検証）
1. **Fixed Key Check**
   - 入力に固定キー10項目が存在し、値が固定値と一致すること。
2. **Pending Gate Check**
   - `pendingDecisionQueueCount>0` のmock入力で `executeAllowed=false` / `decision=Hold` を確認。
3. **Unlock Rule Check**
   - `a1Status="Done" && pendingDecisionQueueCount==0` のみ `Go` 判定可能であること。
4. **NoGo Path Check**
   - NoGo時の戻り先が固定パスで変化しないこと。
5. **Safety Prohibition Check**
   - `safeModeDefault!=ON` または `safeModeBoundary!=SAFE_MODE_STRICT_ON` を与えた場合、必ず `NoGo`。
6. **Determinism Check**
   - 同一mock入力3回で判定が一致すること。

### Verify
- 各チェックが「実装不要・契約文のみで判定可能」な設計になっていること。
- Execute禁止条件と矛盾しないこと。

### Proceed判定（Phase 5進行条件）
- mock検証項目に抜けがなく、失敗時の停止条件が明示されていること。

---

## Phase 5: Verify（AC/DoD監査・停止レポート）

### Read同期（Phase開始時必須）
- AC/DoD と停止条件を再読する。

### Acceptance Criteria（AC）
- [x] 最小I/Fの `型・責務・禁止事項` が明文化されている。
- [x] ADR-style `Context/Decision/Consequences` が記載されている。
- [x] 人間承認境界とAI責務境界が分離されている。
- [x] 入出力/状態遷移/非機能（監査・再現性）が固定されている。
- [x] mock検証計画が実装前チェックとして成立している。
- [x] 上流ADR（0026/0027/0028）と矛盾する新規契約語彙・遷移が追加されていない。

### Definition of Done（DoD）
- [x] 固定キー差分 0（driftなし）。
- [x] `NoGo return path` が一意固定。
- [x] `safeModeDefault=ON` を維持。
- [x] `Self-Correction <= 3` を満たす（実績: 0/3）。
- [x] 未確定論点は確定化せず `stopped/held` へ記録する。

### stopped/held（未確定論点の停止レポート）
- `Approval Record: Pending` の承認主体・時刻・証跡は未記入（人間入力待ち）。
- 未承認が残る限り、A2/A3 Execute開始は不可。
- 競合（固定語彙再定義要求、safeMode緩和要求、NoGo path変更要求）発生時は即停止し人間判断へエスカレーションする。


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


## Stream A Phase Ledger (2026-05-05 / HIL-RS-02-A1 contract-governance hardening)

### Phase 1: Read
- Read同期対象: `Status / Scope / Dependencies / fixed keys / NoGo return path`.
- Extracted Context: 契約固定値は `HIL-RS-02-A1-CONTRACT-FREEZE-v1` + `schemaVersion=1.0.0` + `overridePolicy=human_dual_control_only` を核に、`safeModeDefault=ON` と `safeModeBoundary=SAFE_MODE_STRICT_ON` を後退不可境界として扱う。
- Extracted Decision: `Pending -> Approved | Pending -> Rejected` 以外の遷移は禁止、A2/A3解放は `a1Status=="Done" && pendingDecisionQueueCount==0` 前提。
- Extracted Consequences: Pending残存時は Execute禁止、NoGo時は `issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md` へ固定差戻し。

### Phase 2: Plan
- 宣言: **Plan -> Execute -> Verify -> Proceed**（逆走禁止）。
- AC/DoD不足補完（Draft提案）:
  1. A1完了条件を `fixed keys diff=0` + `pendingDecisionQueueCount==0` + `Approval Record必須3項目充足` に固定。
  2. NoGo条件を `未承認確定化 / 未定義競合 / allowlist外差分 / pending bypass` に固定。
  3. 停止条件を `self-correction>=4相当` で即停止し、`原因・不足情報・再開条件` を出力に固定。
- 合意ログ: 本Draftは `Approval Record: Pending` とし、承認完了まで Execute拡張を禁止。

### Phase 3: ADR明文化と合意
- Context: Stream AはA1契約・統治固定のみを担当し、実装確定を含めない。
- Decision: fixed vocabulary/value を再定義せず参照のみで運用し、`Approval Record` がPendingの間は Phase 4 Execute を禁止。
- Consequences: A2/A3は mock準備のみ許可、Open化判定はA1完了後の別責務に留める。
- 合意状態: `Pending`（未承認のため確定扱い禁止）。

### Phase 4: Execute
- 編集範囲: Stream A allowlist内ファイルのみ。
- 契約保護: `freezeContractId/schemaVersion/overridePolicy/contractLinkLocked/sharedResourceFreeze/safeModeDefault/safeModeBoundary` の固定値を変更しない。

### Phase 5: Verify
- 自己検証:
  - A1完了条件: 明文化済み（未充足時はGo不可）。
  - NoGo条件: 明文化済み（固定差戻し先あり）。
  - 停止条件: 明文化済み（self-correction上限あり）。
- Self-Correction counter: `0/3`（本更新時点）。

### Phase 6: Proceed / Stop
- Go条件: `AC/DoD充足` かつ `契約矛盾なし`。
- No-Go条件: `未承認確定化` / `未定義競合` / `指定外差分` / `self-correction上限超過`。
- 再開条件: `Approval Record` の `approved_by / approved_at / evidence` 充足 + Pending queue解消。
