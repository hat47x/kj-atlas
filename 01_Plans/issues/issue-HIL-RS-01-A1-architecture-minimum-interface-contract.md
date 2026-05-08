# Issue Draft: HIL-RS-01 A1 Architecture 最小I/F契約固定（Stream F）

- Type: Process
- Status: In Progress
- Lifecycle: Draft -> Open -> In Progress -> Done
- Priority: P1
- Owner: Stream F（A1 minimum interface contract freeze）
- Scope: 本ファイルのみ（docs-only）
- Dependencies: なし（A1最小I/Fの先行固定）
- Related ADR/Spec: `ADR-0026`, `ADR-0027`, `ADR-0028`

## Mission
A1最小I/F契約（Critique / ReDiff / Attribution / Error）を、責務境界と停止条件込みで再読可能に固定する。

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
- A1未承認事項は「未承認のまま」扱い、確定化しない。

## Phase 1 Read
### Re-read checkpoints
- Constraints の固定語彙・固定値・再定義禁止境界を再読する。
- Serial Phases の順序逸脱がないことを再読する。
- Hold/NoGo reason code と Stop条件の適用ルールを再読する。

### Context
- A1はHIL-RS-01/02の統治契約SSOT。
- A1未固定のまま後続へ進むと、承認遷移と責務境界が分岐する。
- A1が曖昧だとA2/A3で契約再定義が発生する。

## Phase 2 ADR（C/D/C）
### Context
- 失敗モードは `Pending bypass` と `AI承認代行`。
- 契約曖昧性はA2/A3の差分解釈を誘発し、監査不可能性を増幅する。

### Decision
- 最小I/F・責務分界・承認ゲートを固定する。
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
- A2/A3は契約再定義なしで進行可能（read-only前提）。

## Phase 3 Plan（AC / DoD）
### Acceptance Criteria
- AC-1: 固定語彙/固定値ドリフト0。
- AC-2: `Pending` bypass禁止が明示されている。
- AC-3: `NoGo return path` が一意固定。
- AC-4: 外部レーン完了待ちを前提化しない mock契約参照が明示。
- AC-5: 判定式（`a2a3Unlock`）と停止時条件が明示されている。
- AC-6: Critique/ReDiff/Attribution/Error の4契約IDが最小I/F集合として明示されている。

### Definition of Done
- DoD-1: `safeModeDefault=ON` / `safeModeBoundary=SAFE_MODE_STRICT_ON` 後退なし。
- DoD-2: `overridePolicy=human_dual_control_only` 後退なし。
- DoD-3: AI責務と人間承認責務の分離が明示。
- DoD-4: `Pending` が1件でもあれば Execute不許可。
- DoD-5: Hold/NoGo理由コードとStop条件が同一契約内で再読可能。

## Phase 4 Execute（文面整備のみ）
- 実施原則: **契約優先**。実装詳細は追加しない。
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
- `NOGO_UNAPPROVED_A1_ASSERTION`: A1未承認事項の確定化要求を検知

### Stop Conditions（強制停止）
以下のいずれかを検知した時点で `decision=Stop` とし、以降フェーズを進めない。
1. A1未承認事項の確定化要求
2. safeMode後退前提
3. 指定外編集（本ファイル以外の変更）

## Phase 5 Verify
### Verify Procedure（自己修復上限=3）
1. Contract Snapshot照合（固定語彙/固定値/NoGo return path）。
2. 責務境界照合（AI proposal-only / Human final approval）。
3. `Pending` 残存チェック（1件でも `executeAllowed=false`）。
4. AC/DoD照合（判定式・停止条件・4契約ID集合の明示を含む）。
5. 不一致があれば修正し再検証（最大3回）。
6. 3回で解消不能なら **致命エラーとして停止**（Phase 6 Proceedへ進まない）。

### Verification Result Template
- self-check #1: Contract drift
- self-check #2: Responsibility boundary
- self-check #3: Pending/Stop condition
- self-correction count: `x/3`

## Phase 6 Proceed
- Proceed=Go 条件:
  - `a1Status=="Done" && pendingDecisionQueueCount==0`
  - Stop条件未検知
  - AC/DoD全件pass
- Hold 条件:
  - 承認不足、`Pending`残存、監査証跡不足
- Stop 条件:
  - 「Stop Conditions（強制停止）」に合致

### Current Record（this edit）
- decision: `Hold`
- executeAllowed: `false`
- reasonCodes:
  - `HOLD_PENDING_QUEUE`（承認待ちを想定）
- noGoReturnPath:
  - `issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`
- note:
  - 本更新は契約文面整備のみ。実装詳細の追加なし。
