# Issue Draft: HIL-RS-01 A1 Architecture 最小I/F契約固定（Stream D）

- Type: Process
- Status: Open
- Lifecycle: Draft -> Open -> In Progress -> Done
- Priority: P1
- Source Issue: N/A
- Owner: Stream D（HIL A1 governance/interface contract）
- Scope: 本ファイルのみ（docs-only）
- Dependencies: なし（A1最小I/Fの先行固定）
- Expected verification level: docs-check
- Related ADR/Spec: `ADR-0026`, `ADR-0027`, `ADR-0028`

## Serial Phases（固定）
1. Phase 1 Read
2. Phase 2 ADR/CDC（Context / Decision / Consequences）
3. Phase 3 Plan
4. Phase 4 Execute
5. Phase 5 Verify
6. Phase 6 Proceed

## Fail-safe（即停止条件）
- 承認不足
- 前提崩れ
- 競合発生
- 3回超修復（self-correction >= 4 相当）

---

## Phase 1 Read（実施記録）
### Context
- A1は HIL-RS-01/02 の後続計画に先行する契約SSOT。
- A1未固定で hardening/親計画へ進むと、判定式と責務境界が分岐する。

### Decision
- A1最小I/Fを **contract-only** で凍結し、実装記述は含めない。
- `safeModeDefault=ON` / `safeModeBoundary=SAFE_MODE_STRICT_ON` を後退禁止。

### Consequences
- A1完了まで、後続は read-only参照のみ。
- 競合時は NoGo とし、本Issueに差し戻す。

---

## Phase 2 ADR/CDC（先行明文化）
### Context
- 承認境界とAI責務境界の曖昧さは、Pending bypass と監査不能を誘発する。

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
- AI責務境界:
  - AIは `proposal-only`。
  - AIは承認状態変更・本番適用を行わない。
- 人間承認境界:
  - `Pending -> Approved/Rejected` の確定は人間のみ。

### Consequences
- A2/A3は凍結値を read-only 参照。
- 承認不足時は Execute 禁止（Plan/Verifyのみ許可）。

---

## Phase 3 Plan（A1最小I/F）
- 入力・出力・遷移・禁止事項を最小構成で固定。
- Non-goal: 実装手順、runtime詳細、別レーン（A2/A3/Delivery）への介入。

## Phase 4 Execute（contract definition）
### Inputs
- `freezeContractId`, `contractIds`, `schemaVersion`, `safeModeDefault`, `safeModeBoundary`, `pendingDecisionQueueCount`, `a1Status`

### Outputs
- `executeAllowed`, `decision(Go|NoGo|Hold)`, `reasonCodes`, `requiredHumanActions`, `noGoReturnPath`

### State/Gate
- 許可遷移: `Pending -> Approved | Pending -> Rejected`
- `Approval Record: Pending` が1件でもあれば `executeAllowed=false` かつ `decision=Hold`

### Prohibitions
- safeMode既定の緩和
- AIによる承認自動昇格
- `freezeContractId` 再定義
- `NoGo return path` 変更

## Phase 5 Verify
- 固定語彙/固定値のドリフト: 0
- 境界分離（AI責務 / 人間承認）: 明示済み
- fail-safe条件: 明示済み

## Phase 6 Proceed
- Go: A1最小I/F契約の凍結完了（本書）
- Hold/NoGo: 承認不足・前提崩れ・競合・修復上限超過時

## Stream A contract freeze run（2026-05-05）

### Phase 1: Plan → Execute → Verify → Proceed（Read sync）
- Read対象を再同期し、契約キーを抽出。
- state keys: `a1Status`, `decision`, `executeAllowed`。
- gate keys: `pendingDecisionQueueCount`, `unlockRule`, `decisionQueueTransition`。
- approval keys: `approved_by`, `approved_at`, `evidence`。
- 判定: drift `0`（固定語彙/固定値の差分なし）。

### Phase 2: ADR明文化（Context / Decision / Consequences）
- Context: A1契約を先に固定しない場合、A2/A3で承認境界と遷移条件の再解釈が発生する。
- Decision: 本Issueの契約値を `contract-only` で凍結し、未合意事項は `未確定` として保持する。
- Consequences: 合意入力がない限り `decision=Hold` を維持し、確定扱いに進めない。
- 未確定: `Approver-A/B` の実名マッピング、証跡保管先URI。

### Phase 3: 契約凍結案確定（implementation-decoupled）
- I/F signature frozen:
  - Inputs: `freezeContractId`, `contractIds`, `schemaVersion`, `safeModeDefault`, `safeModeBoundary`, `pendingDecisionQueueCount`, `a1Status`。
  - Outputs: `executeAllowed`, `decision`, `reasonCodes`, `requiredHumanActions`, `noGoReturnPath`。
- state transition frozen:
  - `Pending -> Approved | Pending -> Rejected` のみ許可。
- approval evidence frozen:
  - `approved_by`, `approved_at`, `evidence`（全必須）。

### Phase 4: モック仕様公開（他ストリーム独立進行可）
- 下流向け mock contract（JSON例）:
```json
{
  "contractId": "HIL-RS-02-A1-CONTRACT-FREEZE-v1",
  "schemaVersion": "1.0.0",
  "input": {
    "a1Status": "Done",
    "pendingDecisionQueueCount": 0,
    "approvalRecord": {
      "approved_by": "Architecture Owner",
      "approved_at": "2026-05-05T00:00:00Z",
      "evidence": "decision-log://a1/2026-05-05"
    }
  },
  "output": {
    "executeAllowed": true,
    "decision": "Go",
    "reasonCodes": [],
    "requiredHumanActions": [],
    "noGoReturnPath": "issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md"
  }
}
```
- 型定義（契約専用）:
```ts
export type A1GovernanceGateV1 = {
  contractId: "HIL-RS-02-A1-CONTRACT-FREEZE-v1";
  schemaVersion: "1.0.0";
  a1Status: "Draft" | "Open" | "In Progress" | "Done";
  pendingDecisionQueueCount: number;
  approvalRecord: {
    approved_by?: string;
    approved_at?: string;
    evidence?: string;
  };
  executeAllowed: boolean;
  decision: "Go" | "NoGo" | "Hold";
};
```
- fixture雛形:
  - `fixtureId: A1-contract-freeze-minimal-v1`
  - `expectedDecisionWhenPending>0: Hold`
  - `expectedDecisionWhenPending=0+approvalComplete: Go`
- 明示: この契約に一致すれば実装は独立進行可（contract-only、挙動実装は別Issue）。

### Phase 5: Verify & Handoff
- AC/DoD照合: pass（契約ID・schemaVersion・禁止事項を固定）。
- handoff最小セット:
  - contractId: `HIL-RS-02-A1-CONTRACT-FREEZE-v1`
  - schemaVersion: `1.0.0`
  - prohibitions:
    1. safeMode既定緩和
    2. AIによる承認自動昇格
    3. `Pending` bypass
    4. `freezeContractId` 再定義
