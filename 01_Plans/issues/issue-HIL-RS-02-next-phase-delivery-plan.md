# Issue Draft: HIL-RS-02 次フェーズ実行計画（Stream I 再設計版）

- Type: Process
- Status: Open
- Source Issue: N/A
- Lifecycle: Draft -> Open -> In Progress -> Done
- Priority: P1
- Owner: Stream I Agent（Delivery Plan Orchestrator）
- Scope: `01_Plans/issues/issue-HIL-RS-02-next-phase-delivery-plan.md` のみ
- Dependencies (minimal): `HIL-RS-02-A1-CONTRACT-FREEZE-v1`（参照固定）, `02_Architecture/hil_rs_01_a1_minimum_interface_contract.md`（SSOT参照）
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

## 1. 実行規律（全Phase共通）
1. 各Phaseで **Read同期** を先に実施する。
2. 各Phaseは必ず **Plan -> Execute -> Verify -> Proceed** の順序で進める。
3. AC/DoD不足を検知した場合は **Draft提案を提示し、合意までExecuteを制限** する。
4. Self-Correctionは最大3回（`0/3` 開始、再試行ごとに `+1`）。
5. 次の重大不整合は即停止し、`原因 / 影響I/F / 人間判断論点` を記録する。
   - `self_correction_attempt >= 4`
   - pending bypass（未承認事項の確定化）
   - 固定ガードレールの後退要求
   - allowlist外編集要求

---

## Phase 1: 依存マップ作成（Dependency Isolation）

### Plan
- 現行計画の依存を `論理依存` と `リソース依存` に分解し、切断可能性を判定する。

### Execute
#### 1) 論理依存（Logical）
- L1: `A1契約凍結`（固定キー一致）
- L2: `Approval Record`（二者承認）
- L3: `A2A3_OPEN_ALLOWED` 判定

#### 2) リソース依存（Resource）
- R1: 承認者（Architecture Owner / Governance reviewer）
- R2: docs-check実行者
- R3: A2/A3担当ストリームの着手タイミング

#### 3) 切断候補（他ストリーム依存最小化）
- C1: `A2/A3実装進行` を切断し、Stream Iは **Gate定義と判定ログ** のみ管理。
- C2: 承認未完了時は `Conditional` 固定として前進可能範囲を `Plan/Verify` に限定。
- C3: I/F定義を mock-first で先行確定し、実装進捗待ち依存を分離。

### Verify
- 依存が `L1-L3 / R1-R3` に分類され、切断候補 `C1-C3` が明示されていること。

### Proceed
- 依存分類と切断候補が欠落なく記述されていればPhase 2へ進行。

---

## Phase 2: ADR-style 明文化（Context / Decision / Consequences）

### Plan
- Stream I単独で運用可能な決定事項をADR形式で固定する。

### Execute
### Context
- 既存計画はA2/A3の進捗に引きずられやすく、Stream I単独での完遂条件が曖昧。

### Decision
- D1: Stream Iの責務を `Gate仕様固定・判定・証跡維持` に限定する。
- D2: `A2/A3実装可否` は **判定出力のみ** 提供し、実装進捗管理は他ストリーム責務と分離。
- D3: `Approval Record: Pending` が1件でもある場合、`Execute=Forbidden`（Plan/Verifyのみ許可）を維持する。

### Consequences
- 実装待ちでもStream Iは `判定・記録・エスカレーション` を独立継続できる。
- A2/A3は `判定インターフェース` を入力としてのみ参照し、契約値再定義を禁止する。

### クリティカルパス
1. 固定キー整合確認
2. Approval Record整合確認
3. Gate判定出力
4. Verify（docs-check）

### 並列可能領域
- P1: A2 mock実装準備（I/F参照のみ）
- P2: A3ドキュメント同期準備（判定結果待ち）
- P3: 承認証跡収集

### Verify
- Context / Decision / Consequences の3要素と、クリティカルパス・並列領域が明示されていること。

### Proceed
- ADR-style要素の欠落がなければPhase 3へ進行。

---

## Phase 3: mock-first導入（I/F先行分離）

### Plan
- I/F先行で進める工程と実装待ち工程を分離し、受入条件をPhase単位で定義する。

### Execute
### I/F先行工程（Stream Iで進行可）
- M1: `HIL_RS_DECISION_GATE_V1` を判定I/Fとして固定。
- M2: `A2-PROPOSAL-ENVELOPE-V1` を入力制約のみ固定。
- M3: `A3-DOC-SYNC-CHECK-V1` を同期結果I/Fとして固定。

### 実装待ち工程（他ストリーム依存）
- W1: A2本実装への組込み
- W2: A3本同期ジョブへの接続
- W3: 承認者による本番承認入力

### フェーズ受入条件（AC）
- AC-3.1: I/F名・入出力・監査フィールドが明示されている。
- AC-3.2: 実装待ち工程 `W1-W3` がI/F先行工程 `M1-M3` と混在していない。
- AC-3.3: `Approval Record: Pending` 時の実行制限が保持されている。

### DoD
- DoD-3.1: mock-first分離表が更新済み。
- DoD-3.2: 固定ガードレールの再定義がない。
- DoD-3.3: self-correction回数が記録されている。

### Verify
- AC-3.1〜3.3 / DoD-3.1〜3.3 の自己点検を記録。

### Proceed
- AC/DoD充足でPhase 4へ進行。不足時はDraft提案へ戻す。

---

## Phase 4: 実行計画確定（番号・DoD・停止/エスカレーション固定）

### Plan
- 直列フェーズ計画を運用定義として確定する。

### Execute
### 実行フェーズ定義（固定）
1. Phase 1: 依存マップ作成
2. Phase 2: ADR-style明文化
3. Phase 3: mock-first導入
4. Phase 4: 実行計画確定
5. Phase 5: Verify

### 全体DoD
- DoD-G1: 各Phaseに `Plan -> Execute -> Verify -> Proceed` が定義済み。
- DoD-G2: 依存切断候補が3件以上明示済み。
- DoD-G3: クリティカルパスと並列可能領域が明記済み。
- DoD-G4: mock-first分離とフェーズACが定義済み。
- DoD-G5: 停止条件・エスカレーション条件が固定済み。

### 停止条件（Stop）
- S1: `self_correction_attempt >= 4`
- S2: pending bypass検知
- S3: 固定ガードレール改変要求
- S4: allowlist外編集要求

### エスカレーション条件
- E1: `Approval Record` の責務分離違反
- E2: `A2A3_OPEN_ALLOWED` 判定不能（入力欠落/矛盾）
- E3: `NoGo return path` 変更要求

### Verify
- DoD-G1〜G5、Stop条件S1〜S4、Escalation条件E1〜E3 の明示を確認。

### Proceed
- 固定項目に欠落がなければPhase 5へ進行。

---

## Phase 5: Verify（AC/DoD準拠確認 + 残課題一覧）

### Plan
- 全フェーズのAC/DoD適合性を検証し、未解決課題を一覧化する。

### Execute
- Self-Correction counter: `0/3`（開始時）
- docs-checkコマンド（固定）:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
  - `python3 -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `git diff --check`

### Verify
#### AC/DoD準拠結果
- AC: Phase 1〜4で定義したAC項目が本文上で追跡可能。
- DoD: Global DoD（G1〜G5）を満たす構造に更新済み。

#### 残課題（Open）
1. `Approval Record` の `approved_by / approved_at / evidence` 入力待ち。
2. `HIL-RS-02-GOV-EXCEPTION-01` の人間判断待ち（held継続）。
3. `A2A3_OPEN_ALLOWED` の最終Go判定はA1完了入力待ち。

### Proceed
- 判定: **Conditional**（未承認・held論点が残るため）。
- 再開条件:
  1. 二者承認の証跡入力完了
  2. pendingDecisionQueueCount=0
  3. 固定ガードレール差分=0
