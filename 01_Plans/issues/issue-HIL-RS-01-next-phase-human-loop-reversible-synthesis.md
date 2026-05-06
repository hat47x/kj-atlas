# Issue Plan: HIL-RS-01 次フェーズ実行計画（Human-in-the-loop / Reversible Synthesis, Stream D）

- Type: Process
- Status: In Progress
- Priority: P1
- Owner: Stream A（contract freeze and minimum interface agreement）
- Scope: 本ファイルのみ（docs-only）
- Dependencies:
  - `issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`
  - `issue-HIL-RS-02-A1-governance-contract-hardening.md`

## Serial Phases（固定）
1. Phase 1 Read
2. Phase 2 ADR（Context / Decision / Consequences）
3. Phase 3 Plan（AC / DoD）
4. Phase 4 Execute
5. Phase 5 Verify
6. Phase 6 Proceed

## Constraints（固定）
- `freezeContractId` / `schemaVersion` / `overridePolicy` / `safeModeBoundary` は固定参照のみ。
- `Pending` bypass禁止。
- mock契約参照で独立遂行（外部レーン完了待ち前提を置かない）。

## Phase 1 Read
- 親計画はA1契約（最小I/F + hardening）の参照ノードであり、再定義ノードではない。

## Phase 2 ADR（C/D/C）
### Context
- 親計画で契約値を再定義すると下流レーンの整合が崩れる。

### Decision
- 親計画側は以下を参照のみ:
  - `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
  - `schemaVersion=1.0.0`
  - `overridePolicy=human_dual_control_only`
  - `safeModeDefault=ON`
  - `safeModeBoundary=SAFE_MODE_STRICT_ON`
  - `decisionQueueTransition=Pending -> Approved | Pending -> Rejected`
  - `NoGo return path=issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`
- 解放ゲート参照:
  - `a1Status=="Done" && pendingDecisionQueueCount==0`

### Consequences
- 親計画は gate条件を再定義しない。
- 矛盾時は Proceedせず Hold/NoGo。

## Phase 3 Plan（AC / DoD）
### Acceptance Criteria
- AC-1: A1最小I/F固定値とのドリフト0。
- AC-2: hardening（SoD/承認遷移固定）の参照整合。
- AC-3: `NoGo return path` 一意固定。
- AC-4: A2/A3非干渉（編集・判定代行なし）。

### Definition of Done
- DoD-1: `safeModeDefault=ON` / `safeModeBoundary=SAFE_MODE_STRICT_ON` 後退なし。
- DoD-2: `overridePolicy` 後退なし。
- DoD-3: `Pending` 残存時は `Hold/NoGo` のみ。
- DoD-4: 外部レーン完了待ちを前提にしない独立遂行条件を維持。

## Phase 4 Execute
- A1先行固定 → hardening固定 → 親計画整合反映の順序だけを実施。

### Responsibility Boundary（親計画の責務）
- Parent Plan（本issue）:
  - 契約再定義は行わず、A1/hardening契約の参照整合のみ判定する。
  - `Go/Hold/NoGo` 判定結果と `reasonCodes` を記録する。
- A1 Contract Owner:
  - `freezeContractId` / `schemaVersion` / `overridePolicy` / `safeModeBoundary` の正本管理。
- Human Approver:
  - `Pending -> Approved | Rejected` の遷移確定責務を持つ。
- AI / Automation:
  - 判定補助（差分検知・整合チェック）まで。承認遷移確定は禁止。

### Execute Gate（判定式固定）
- `Go` の必要十分条件:
  - `a1Status=="Done"`
  - `pendingDecisionQueueCount==0`
  - 固定参照値にドリフトなし
- `Hold` 条件:
  - `pendingDecisionQueueCount>0`
- `NoGo` 条件:
  - SafeMode境界後退 / overridePolicy後退 / fixed key drift / 競合検知

## Phase 5 Verify
- 固定値整合: pass
- hardening整合: pass
- bypass禁止: pass

### Verify Procedure（自己修復上限=3）
1. A1固定参照値との一致確認（drift=0）。
2. hardening参照（SoD/承認遷移固定）の一致確認。
3. 非干渉確認（A2/A3への編集・判定代行なし）。
4. 不一致は最小修正して再検証（最大3回）。
5. 3回で解消不能なら **致命エラーとして停止**（Proceed禁止）。

## Phase 6 Proceed
- Proceed: 上記順序・固定参照・非干渉が維持された場合のみ。

### Stream A protocol run（2026-05-06 / A1契約凍結クリティカルパス）

#### Phase 1 Read（対象3ファイル再読）
- 対象:
  1. `issue-FB-P2C-01-a1-interface-contract.md`
  2. `issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`
  3. `issue-HIL-RS-01-next-phase-human-loop-reversible-synthesis.md`
- 差分確認結果（固定値）:
  - `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`（一致）
  - `schemaVersion=1.0.0`（一致）
  - `safeModeDefault=ON` / `safeModeBoundary=SAFE_MODE_STRICT_ON`（一致）
  - `decisionQueueTransition=Pending -> Approved | Pending -> Rejected`（一致）
  - gate参照は `A2A3_OPEN_ALLOWED` または同値条件（`a1Status=="Done" && pendingDecisionQueueCount==0`）で整合。
- 未承認項目:
  - `Approval Record` = Pending
  - `HIL-RS-02-GOV-EXCEPTION-01` = held
- 判定: 想定との差分なし（Phase継続可）。

#### Phase 2 ADR明文化（C/D/C）
- Context:
  - A1凍結契約はA2/A3の唯一参照境界であり、親計画側での再定義は契約ドリフトを生む。
- Decision:
  - A1契約は frozen-candidate として既存固定値を維持し、未承認項目を確定扱いしない。
  - `safeModeDefault=ON` / `safeModeBoundary=SAFE_MODE_STRICT_ON` の後退を禁止する。
- Consequences:
  - 承認ログ（`approved_by`, `approved_at`, `evidence`）未充足のため状態は `Needs-decision` を維持。
  - A2/A3への受け渡しは read-only 契約セットに限定。
- Approval log status:
  - `approved-for-freeze-candidate`（docs scope）
  - Human final approval: 未完了

#### Phase 3 Plan → Execute → Verify → Proceed
- Plan（AC/DoD）:
  - AC-1: 固定ID・schemaVersion・SafeMode境界・queue遷移にドリフト0。
  - AC-2: 未承認項目を確定化しない。
  - DoD-1: `A2A3_OPEN_ALLOWED` の前提式を後退させない。
- Execute:
  - 契約固定値の記述を更新せず維持（drift=0）。
  - queue遷移は `Pending -> Approved | Pending -> Rejected` のみ許容を再確認。
- Verify:
  - self-check 1/3: pass（ドリフトなし・未承認明示あり）
  - self-correction count: `0/3`
- Proceed:
  - `pendingDecisionQueueCount` 相当の未解決項目があるため `Hold/Needs-decision` 維持。

#### Phase 4 Handoff（read-only）
- Downstream handoff package（read-only）:
  - `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
  - `schemaVersion=1.0.0`
  - `safeModeDefault=ON`
  - `safeModeBoundary=SAFE_MODE_STRICT_ON`
  - `decisionQueueTransition=Pending -> Approved | Pending -> Rejected`
- 禁止事項再確認:
  1. SafeMode既定ONの解除
  2. 安全境界後退
  3. A2/A3での契約再定義

## Stream A contract freeze sync（2026-05-06 / parent plan alignment）

### Phase 1: Read
- A1契約Issue / P0 baseline / ADR-0026 / ADR-0028 を再読し、親計画は参照ノードであることを再確認。

### Phase 2: ADR（Context / Decision / Consequences）
- Context: 親計画で契約値を再定義すると下流整合が崩れる。
- Decision: `freezeContractId` / `schemaVersion` / `safeModeDefault` / `safeModeBoundary` / `decisionQueueTransition` は参照専用を継続。
- Consequences: `Pending` 残存時は `Hold/Needs-decision` 以外へ遷移しない。

### Phase 3-6: Plan / Execute / Verify / Proceed
- Plan: A2/A3非干渉を維持。
- Execute: 文書整合のみ（実装依存を追加しない）。
- Verify: fixed key drift=0、SafeMode後退なし。
- Proceed: human approval待ちのため `Hold` 維持。
