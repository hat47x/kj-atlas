# Issue Draft: HIL-RS-01 A1 Architecture 最小I/F契約固定（Stream D）

- Type: Process
- Status: In Progress
- Lifecycle: Draft -> Open -> In Progress -> Done
- Priority: P1
- Owner: Stream A（contract freeze and minimum interface agreement）
- Scope: 本ファイルのみ（docs-only）
- Dependencies: なし（A1最小I/Fの先行固定）
- Related ADR/Spec: `ADR-0026`, `ADR-0027`, `ADR-0028`

## Serial Phases（固定）
1. Phase 1 Read
2. Phase 2 ADR（Context / Decision / Consequences）
3. Phase 3 Plan（AC / DoD）
4. Phase 4 Execute
5. Phase 5 Verify
6. Phase 6 Proceed

## Constraints（固定参照）
- `freezeContractId` / `schemaVersion` / `overridePolicy` / `safeModeBoundary` は**固定参照のみ**（再定義禁止）。
- `Pending` 項目の bypass は禁止。
- mock契約参照で独立遂行し、外部レーン完了待ちを前提化しない。

## Phase 1 Read
### Context
- A1はHIL-RS-01/02の統治契約SSOT。
- A1未固定のまま後続へ進むと、承認遷移と責務境界が分岐する。

## Phase 2 ADR（C/D/C）
### Context
- 失敗モードは `Pending bypass` と `AI承認代行`。

### Decision
- 固定語彙（再定義禁止）:
  - `freezeContractId`, `contractIds`, `schemaVersion`, `overridePolicy`, `contractLinkLocked`, `sharedResourceFreeze`, `safeModeDefault`, `safeModeBoundary`, `unlockRule`, `decisionQueueTransition`, `NoGo return path`
- 固定値（凍結）:
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
  - `NoGo return path=issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`
- 境界固定:
  - AIは `proposal-only`。
  - 承認遷移確定（`Pending -> Approved/Rejected`）は人間のみ。

### Consequences
- A2/A3は凍結値をread-only参照。
- 未承認時は `decision=Hold` / `executeAllowed=false`。

## Phase 3 Plan（AC / DoD）
### Acceptance Criteria
- AC-1: 固定語彙/固定値ドリフト0。
- AC-2: `Pending` bypass禁止が明示されている。
- AC-3: `NoGo return path` が一意固定。
- AC-4: 外部レーン完了待ちを前提化しない mock契約参照が明示。

### Definition of Done
- DoD-1: `safeModeDefault=ON` / `safeModeBoundary=SAFE_MODE_STRICT_ON` 後退なし。
- DoD-2: `overridePolicy=human_dual_control_only` 後退なし。
- DoD-3: AI責務と人間承認責務の分離が明示。
- DoD-4: `Pending` が1件でもあれば Execute不許可。

## Phase 4 Execute
- Inputs: `freezeContractId`, `contractIds`, `schemaVersion`, `safeModeDefault`, `safeModeBoundary`, `pendingDecisionQueueCount`, `a1Status`
- Outputs: `executeAllowed`, `decision(Go|NoGo|Hold)`, `reasonCodes`, `requiredHumanActions`, `noGoReturnPath`
- Gate: `Pending -> Approved | Pending -> Rejected` 以外禁止。

### Responsibility Boundary（契約責務境界）
- Human Approver（2者承認）:
  - `decisionQueueTransition` の最終確定のみ実施可能。
  - `Approved/Rejected` の根拠と `requiredHumanActions` を監査可能な形で記録する。
- AI / Automation:
  - `executeAllowed` / `decision` / `reasonCodes` の算出提案のみ可能（proposal-only）。
  - `Pending` を終端状態へ遷移させる操作は禁止。
- Parent Plan / Downstream（A2/A3）:
  - A1固定値を read-only 参照する。
  - `freezeContractId` / `schemaVersion` / `safeModeBoundary` の再定義は禁止。

### Hold / NoGo Reason Codes（固定）
- `HOLD_PENDING_QUEUE`: `pendingDecisionQueueCount > 0`
- `NOGO_SAFE_MODE_REGRESSION`: `safeModeDefault!=ON` または `safeModeBoundary!=SAFE_MODE_STRICT_ON`
- `NOGO_OVERRIDE_POLICY_REGRESSION`: `overridePolicy!=human_dual_control_only`
- `NOGO_CONTRACT_DRIFT`: `freezeContractId` / `contractIds` / `schemaVersion` の不一致
- `NOGO_SHARED_RESOURCE_CONFLICT`: `sharedResourceFreeze` 違反または競合検知

## Phase 5 Verify
- 固定値整合: pass
- 境界分離: pass
- bypass禁止: pass

### Verify Procedure（自己修復上限=3）
1. Contract Snapshot照合（固定語彙/固定値/NoGo return path）。
2. 責務境界照合（AI proposal-only / Human final approval）。
3. `Pending` 残存チェック（1件でも `executeAllowed=false`）。
4. 不一致があれば修正し再検証（最大3回）。
5. 3回で解消不能なら **致命エラーとして停止**（Phase 6 Proceedへ進まない）。

## Phase 6 Proceed
- Go: A1最小I/F契約の凍結完了。
- Hold/NoGo: 承認不足・前提崩れ・競合・修復上限超過時。

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
