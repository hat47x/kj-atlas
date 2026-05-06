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


## Stream A Critical Path Update（2026-05-06 / Phase 1-5）

### Plan
- Scope: `issue-HIL-RS-01*` と `*interface*` 契約文書の再読と凍結条件の再検証（docs-only）。
- Non-Goals: 実装コード変更、A2/A3側契約の再定義、未承認事項の確定化。
- AC:
  - [ ] 契約未確定項目を一覧化する。
  - [ ] CDC（Context / Decision / Consequences）を「承認待ち」状態で明文化する。
  - [ ] `contractLinkLocked/sharedResourceFreeze` を固定参照として再確認する。
  - [ ] A2/A3向け固定I/F配布情報を明記する。
  - [ ] Verify GateでA2開始可否を判定する。

### Execute
#### Phase 1 Read（契約未確定項目）
- `Approval Record`: Pending（最終 human dual approval 未完了）。
- `HIL-RS-02-GOV-EXCEPTION-01`: held（例外可否の人間判断待ち）。
- `pendingDecisionQueueCount`: 0確証の運用証跡が未添付（ゲート判定に必要）。

#### Phase 2 ADR-CDC（承認待ち）
- Context: A1凍結値はA2/A3の唯一参照境界であり、未承認事項を確定扱いすると契約ドリフトが発生する。
- Decision: `freezeContractId/schemaVersion/overridePolicy/safeModeBoundary` は凍結候補として維持し、未承認項目は `Pending` を継続する。
- Consequences: A2/A3は read-only handoff のみ許可、実行判定は `Hold` 維持。

#### Phase 3 Freeze（固定条件）
- `contractLinkLocked=true`（固定）
- `sharedResourceFreeze=true`（固定）
- `safeModeDefault=ON` / `safeModeBoundary=SAFE_MODE_STRICT_ON`（固定）
- `decisionQueueTransition=Pending -> Approved | Pending -> Rejected`（固定）

#### Phase 4 Handoff（A2/A3配布）
- Fixed I/F: `A1-CRITIQUE-IF | A1-REDIFF-IF | A1-ATTR-IF | A1-ERROR-IF`
- Fixed `schemaVersion=1.0.0`
- Prohibited changes:
  1. 契約ID・必須キー・`schemaVersion` の再定義
  2. `Pending` bypass
  3. SafeMode/share-export 境界後退

### Verify（Phase 5 Gate）
- Gate check:
  - `a1Status=="Done"`: pass
  - `contractLinkLocked==true && sharedResourceFreeze==true`: pass
  - `pendingDecisionQueueCount==0` の監査証跡: **not satisfied**（証跡不足）
  - 未承認項目0件: **not satisfied**
- Decision: **Block 維持（A2開始不可）**。
- Self-Correction count: `1/3`（文書内整合の再照合を1回実施、未解消論点は人間承認待ちのため停止継続）。

### Proceed
- 現状態は `Hold/Block`。
- 解除に必要な人間判断:
  1. `Approval Record` の最終承認（2者承認）
  2. `HIL-RS-02-GOV-EXCEPTION-01` の Approved/Rejected 確定
  3. `pendingDecisionQueueCount==0` を示す監査証跡の添付

## Stream A contract freeze sync（2026-05-06 / A1 minimum interface）

### Phase 1: Read
- 固定語彙・固定値・責務境界（AI proposal-only / Human final approval）を再読し、差分 `0` を確認。

### Phase 2: ADR（Context / Decision / Consequences）
- Context: A1最小I/Fは下流全体の契約SSOTであり、再定義を許すと統治が破綻する。
- Decision: 固定語彙と固定値（`freezeContractId`, `contractIds`, `schemaVersion`, `overridePolicy`, `contractLinkLocked`, `sharedResourceFreeze`, `safeModeDefault`, `safeModeBoundary`, `unlockRule`, `decisionQueueTransition`）を維持。
- Consequences: `Pending` が残る限り `executeAllowed=false` を継続し、Proceedを `Hold/Needs-decision` に固定する。

### Phase 3-6: Freeze / Verify / Proceed
- Freeze: `NoGo return path` は本Issueに固定。
- Verify: `Pending bypass` なし、SafeMode後退なしを再確認。
- Proceed: 人間承認待ちで `Hold`。

- Verify:
  - self-check 2/3: pass（固定語彙・固定値・責務境界に差分なし）
  - self-check 3/3: pass（Pending項目を確定化していない）
- Proceed Gate:
  - 判定: **Hold**
  - 根拠: `Approval Record=Pending` および `HIL-RS-02-GOV-EXCEPTION-01=held` のため、`a1Status=="Done" && pendingDecisionQueueCount==0` を未充足。
  - 停止条件評価: 前提崩れ/未定義競合/承認未記録は未解消であり、推測確定は行わない。

#### Phase 4 Verify（AC/DoD照合・依存解放条件）
- AC照合:
  - AC-1（固定契約ドリフト0）: pass
  - AC-2（Pending bypass禁止）: pass
  - AC-3（NoGo return path固定）: pass
  - AC-4（A2/A3非干渉）: pass
- DoD照合:
  - DoD-1 SafeMode後退なし: pass
  - DoD-2 overridePolicy後退なし: pass
  - DoD-3 人間承認責務分離: pass
  - DoD-4 Pending残存時のExecute不許可: pass
- 依存解放条件:
  - 未解放（`pendingDecisionQueueCount==0` を満たさない）
- 競合リスク（他stream編集候補）と禁止境界:
  1. `freezeContractId` / `schemaVersion` の改変競合（禁止）
  2. `decisionQueueTransition` の拡張（禁止）
  3. SafeMode境界緩和（禁止）
  4. A2/A3側での再定義（禁止）

#### Phase 5 Proceed（Yes/Hold/Stop）
- **Proceed=Hold**
- 理由:
  - 契約は frozen-candidate として凍結済みだが、人間最終承認ログが未完了。
  - クリティカルパス要件に従い、未承認項目の推測確定は禁止。
- 下流向け凍結契約サマリ（read-only）:
  - `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
  - `contractIds=A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|A1-ERROR-IF`
  - `schemaVersion=1.0.0`
  - `overridePolicy=human_dual_control_only`
  - `safeModeDefault=ON`
  - `safeModeBoundary=SAFE_MODE_STRICT_ON`
  - `decisionQueueTransition=Pending -> Approved | Pending -> Rejected`
  - `unlock precondition=a1Status=="Done" && pendingDecisionQueueCount==0`
