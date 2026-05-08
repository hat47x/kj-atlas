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


## Stream A parent-plan gate sync（2026-05-06）

### A1→A2/A3解放条件（親計画参照専用）
- 親計画は以下を再定義せず参照する。
  - `a1Status=="Done"`
  - `pendingDecisionQueueCount==0`
  - `Approval Record=Approved`
  - `HIL-RS-02-GOV-EXCEPTION-01` が終端状態（Approved/Rejected）

### Proceed policy
- `pendingDecisionQueue` 未解消または未承認論点残存時は `Hold/Needs-decision` 固定。
- Stopper検知（allowlist外要求/未定義競合/自己修復上限超過）時はNoGo停止して再開条件を明示する。

## Stream A authoritative alignment update（2026-05-06 / A1 contract alignment）

### Phase 1: Read同期
- A1契約Issueと本親計画、ADR-0026参照を再読し、固定値ドリフト `0` を確認。
- Status/Priority: `In Progress` / `P1`。
- AC/DoD差分: 重大差分なし。未承認項目は継続（`Approval Record=Pending`）。

### Phase 2: ADR（Context / Decision / Consequences）
#### Context
親計画は A1契約の参照ノードであり、契約再定義は下流整合を破壊する。

#### Decision
- 親計画は A1 契約I/Fを参照専用で固定する。
  - 判定I/F: `evaluateA1Gate(input: A1GateInput): A1GateOutput`
  - mock I/F: `mockEvaluateA1Gate(input: A1GateInput): A1GateOutput`
- 固定参照値:
  - `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
  - `schemaVersion=1.0.0`
  - `overridePolicy=human_dual_control_only`
  - `safeModeDefault=ON`
  - `safeModeBoundary=SAFE_MODE_STRICT_ON`
  - `decisionQueueTransition=Pending -> Approved | Pending -> Rejected`
- 互換方針:
  - 破壊的変更は human dual approval 完了まで禁止。

#### Consequences
- 親計画での派生判定式追加を禁止。
- `pendingDecisionQueueCount>0` は `Hold` 固定。

### Phase 3: Plan
- 変更対象行: 本Issue末尾の親計画整合ブロックのみ。
- 変更意図: A1契約のAPIシグネチャ/型/互換方針/mock I/F を親計画に明示参照。
- 非変更範囲: A1正本値、他Issue、ADR本文、実装コード。

### Phase 4: Execute
- 親計画に A1契約参照（I/F + 互換 + mock）を追記。
- A2/A3 は read-only handoff を前提に継続可能（実装完了待ちを前提化しない）。

### Phase 5: Verify
- AC-1 fixed keys drift=0: pass
- AC-2 hardening参照整合: pass
- AC-3 NoGo return path固定: pass
- AC-4 A2/A3非干渉: pass
- self-correction: `0/3`

### Phase 6: Proceed判定
- 判定: `Hold/Needs-decision`
- 理由: 人間最終承認未完了。
- 状態明記: **contract-frozen（read-only / pending human final approval）**。

## Stream D alignment run（2026-05-07 / Parent-plan lock）

### Phase 1 Read同期（最新再確認）
- 再読対象:
  1. `issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`
  2. `issue-HIL-RS-01-next-phase-human-loop-reversible-synthesis.md`（本書）
- 同期結果:
  - 親計画は参照ノード、A1は正本ノードという責務分離を再確認。
  - 固定参照値と解放ゲート（`a1Status=="Done" && pendingDecisionQueueCount==0`）の表記は一致。

### Phase 2 ADR（Context / Decision / Consequences）
- Context:
  - 次フェーズ計画が契約値を再定義すると、A2/A3の判定系が二重化して統治不整合を生む。
- Decision:
  - 親計画は `evaluateA1Gate` 系I/Fを含めて**参照専用**を維持し、契約値の再記述を増やさない。
  - `Hold` と `NoGo` の境界は A1 reason codes に従属させ、親計画独自の終端遷移は追加しない。
- Consequences:
  - 実行順序（A1固定 → hardening固定 → 親計画整合）は維持。
  - 人間最終承認未完了の間は `Proceed=Hold` を継続。

### Phase 3 Plan（AC/DoD不足提案→合意）
- AC補強提案:
  - AC-5: 親計画内の `Go/Hold/NoGo` 条件がA1契約の reason code 方針と矛盾しないこと。
- DoD補強提案:
  - DoD-5: `Approval Record=Pending` 時の状態名を `Hold/Needs-decision` に固定すること。
- 合意結果:
  - 本更新では文書整合チェックとして採用し、契約の新規導出は行わない。

### Phase 4 Execute（docs-only）
- 実施内容:
  - 親計画の責務を「参照整合判定」に限定する方針を再固定。
  - A2/A3への非干渉（編集/判定代行なし）を維持。

### Phase 5 Verify（自己修復上限=3）
- verify 1/3:
  - A1固定値との drift=0: pass
  - hardening参照（SoD/承認遷移）整合: pass
- verify 2/3:
  - `NoGo return path` 一意固定: pass
  - `Pending bypass` 禁止: pass
- verify 3/3:
  - A2/A3非干渉: pass
  - self-correction count: `0/3`

### Phase 6 Proceed/Stop
- 判定: **Proceed=Hold**
- 理由:
  - `Approval Record=Pending` と `HIL-RS-02-GOV-EXCEPTION-01=held` が未解決。
  - 親計画は推測確定を禁止し、再開条件（終端承認 + queue解消）充足まで停止継続。


## Stream A serial run（2026-05-07 / parent plan contract lock）

### Phase 1: Read & Plan
- Status: `In Progress`
- Priority: `P1`
- Dependencies: `issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`（read-only参照）。
- Scope: 親計画として参照整合のみ実施（契約再定義禁止）。
- AC/DoD補完（合意記録）:
  1. AC: A1固定参照値とのドリフト0。
  2. AC: A2/A3非干渉（編集・判定代行なし）。
  3. DoD: `pendingDecisionQueueCount>0` なら `Hold/NoGo` 固定。

### Phase 2: ADR明文化（Approval gate）
- Context: 親計画側の再定義は契約ドリフトを誘発する。
- Decision: 親計画は `freezeContractId/schemaVersion/overridePolicy/safeModeBoundary/decisionQueueTransition` を参照専用で固定。
- Consequences: 未承認状態では Proceedせず `Needs-decision` 継続。
- Approval: `approved-for-freeze-candidate`（docs scope）を維持。

### Phase 3: Execute（契約凍結）
- Fixed gate（参照専用）:
  - `a1Status=="Done" && pendingDecisionQueueCount==0`
- Mock-first note:
  - A2/A3は `A1-CONTRACT-MOCK-v1` で先行検証可能、実装接続待ちを前提化しない。

### Phase 4: Verify（self-check）
- AC/DoD検証: pass（参照整合・非干渉・Hold条件維持）。
- Self-Correction count: `0/3`。

### Phase 5: Proceed / Stop
- 判定: `Hold`。
- 理由: human final approval未完了のため、推測でGoへ遷移しない。


## Stream A parent reflection update（2026-05-07 / Phase 1-5）

### Phase 1: ADR整合確認（再Read実施）
- 再読対象: 親Issue / A1 Issue / ADR-0026。
- Context: 親Issueは契約参照ノードであり再定義ノードではない。
- Decision: A1固定契約を read-only 参照し、判定式は `a1Status=="Done" && pendingDecisionQueueCount==0` を維持。
- Consequences: 未承認論点は親Issueで確定せず `Hold list` に隔離。

### Phase 2: A1最小契約の反映
- 親Issueへ反映する対象を限定:
  - fixed reference keys/values
  - Go/Hold/NoGo gate
  - 非干渉ポリシー（A2/A3編集・判定代行禁止）
- 下流依存は mock前提で切断し、外部レーン完了待ちを開始条件にしない。

### Phase 3: Hold list（未承認論点の隔離）
- `Approval Record` final approval: Pending
- `HIL-RS-02-GOV-EXCEPTION-01`: held
- `pendingDecisionQueueCount==0` の監査証跡: insufficient evidence

### Phase 4: 検証
- AC/DoD照合: pass。
- リンク整合: pass（NoGo return path はA1 Issueへ一意固定）。
- 状態遷移妥当性: pass（`Pending -> Approved | Rejected` 以外禁止）。
- Self-Correction: `0/3`。

### Phase 5: 完了報告
- 変更要約: A1固定契約の親Issue反映を参照専用で正規化。
- 残リスク: 未承認論点があるため `Proceed=Hold` 継続。
- 他ストリームへ渡す契約固定点: `freezeContractId`, `contractIds`, `schemaVersion`, `overridePolicy`, `safeModeDefault`, `safeModeBoundary`, `decisionQueueTransition`, `unlock precondition` は不変。
