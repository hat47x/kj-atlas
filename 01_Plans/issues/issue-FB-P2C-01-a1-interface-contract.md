# Issue Draft: FB-P2C-01 A1 interface contract freeze（Stream B critical path）

- Type: Feature request
- Status: Open（A1 contract freeze active）
- Priority: P0
- Owner: Stream H（FB Open/P0 planning convergence）
- Scope: A1最小I/F契約の固定（Contract ID / Signature / Deterministic Rule）
- Dependencies: `A1 -> A2 -> A3`, A2/A3はA1 read-only参照
- Related ADR: `ADR-0001`, `ADR-0026`, `ADR-0027`, `ADR-0028`
- Verification level: `docs-check`
- Non-target file policy: allowlist 2ファイル以外は不干渉

- Contract snapshot date: `2026-04-27`（固定入力）
- Execution order (Stream H fixed serial): 2/2 FB-P2C A1契約凍結

---

## Phase 1: Read（再読・差分確認）
- 差分検知時は停止候補として `held` に記録し、Executeへ進まない。
- Phase開始直前に対象2ファイル（本ファイル / `issue-FB-P0-2A2B2C-stream-c-planning-baseline.md`）を再読し、語彙・判定式・held条件の差分有無を確認する。
### Extracted
- Status: `Open`
- Priority: `P0`
- Scope: A1契約固定のみ
- Dependencies: 下流A2/A3はA1契約の参照専用
- Related ADR: `ADR-0001/0026/0027/0028`

### Delta log
- 現値（critical-path freeze）
  - `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
  - `contractIds=A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|A1-ERROR-IF`
  - `safeModeDefault=ON`
  - `sharedResourceFreeze=true`
- 事前想定との差分
  - `CTR-FB-P2C-01-A1-TIEBREAK-V1` は legacy候補として凍結し、判定ゲートから除外済み（read-only参照のみ）。
- 判定: A1 SSOTとの差分なし（Proceed可）。
- 固定キー検証（`freezeContractId`, `contractIds`, `schemaVersion`, `overridePolicy`, `contractLinkLocked`, `sharedResourceFreeze`, `safeModeDefault`, `unlockRule`, `decisionQueueTransition`）: 差分 `0`。ドリフト検知時は即停止し `held` に記録する。
- Phase gate checklist: `Status / Scope / Dependencies / 固定キー` を各Phase開始時に再確認し、差分が1つでもあれば `held` に記録して停止。
- Stream B hard-stop: allowlist外編集要求 / 未定義競合 / self-correction 4回目相当は即時停止。

### held record
- `HIL-RS-02-GOV-EXCEPTION-01`: 未承認事項として `held` 維持（確定扱い禁止）

## Phase 2: ADR/CDC Consensus
### Context
- A1は全下流判定ゲートであり、Contract IDを単一SSOTへ収束させる必要がある。

### Decision
- 固定（採用）
  - `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
  - `contractIds=A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|A1-ERROR-IF`
  - `schemaVersion=1.0.0`
  - `overridePolicy=human_dual_control_only`
  - `contractLinkLocked=true`
  - `decisionQueueTransition=Pending -> Approved | Pending -> Rejected`
  - `safeModeDefault=ON`
  - `sharedResourceFreeze=true`
  - `unlockRule=a2a3Unlock = (a1Status=="Done" && pendingDecisionQueueCount==0)`
  - `NoGo return path = issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`
- 保留
  - `HIL-RS-02-GOV-EXCEPTION-01`: `held` 維持（未承認事項）。
  - `CTR-FB-P2C-01-A1-TIEBREAK-V1`: legacy参照のみ（判定ゲート非採用、確定扱いしない）。

### Approval Gate（Execute進行条件）
- ADR/CDC（Context / Decision / Consequences）の承認完了までは Phase 4 Execute へ進まない。
- 未承認事項は `pending/held` のまま保持し、確定扱いしない。
- Phase開始直前に対象2ファイルを再読し、C/D/C + 承認状態に差分があれば停止する。

### Consequences
- A2/A3はA1 freeze contract参照のみ（再定義禁止）。
- 未承認アルゴリズム詳細は開始条件に使わない。

## Phase 3: Plan
- 宣言: `Plan -> Execute -> Verify -> Proceed`（直列運用・逆走禁止）。
- 差分意図: A1契約を「唯一ゲート」に戻す。
- 非対象不干渉: allowlist 2ファイル外は編集しない。
- Phase開始直前に対象2ファイルを再読し、AC/DoD不足があれば AIドラフト提案として追記してから Execute へ進む。

### AC / DoD
- AC
  1. A1 SSOTキーが他Issueと一致。
  2. `held` 論点を確定扱いしない。
  3. A2/A3 read-only参照を明記。
  4. `A2A3_OPEN_ALLOWED` をA1/A2/A3共通判定式として固定。
- DoD
  1. Go/NoGo判定でA1 freeze値のみ参照（`schemaVersion/overridePolicy/contractLinkLocked/sharedResourceFreeze` を含む）。
  2. 指定外ファイル差分0。

## Phase 4: Execute
- Phase開始直前に対象2ファイルを再読し、Phase 2承認済みDecisionとの差分があれば `held` を更新して停止する。
- `A2A3_OPEN_ALLOWED = (a1Status=="Done" && pendingDecisionQueueCount==0 && freezeContractId=="HIL-RS-02-A1-CONTRACT-FREEZE-v1" && schemaVersion=="1.0.0" && overridePolicy=="human_dual_control_only" && contractLinkLocked==true && sharedResourceFreeze==true && safeModeDefault=="ON" && safeModeBoundary=="SAFE_MODE_STRICT_ON")`
- `NoGo判定 = (!A2A3_OPEN_ALLOWED) || pendingBypassDetected || undefinedConflictDetected`
- `ProceedGate = (A2A3_OPEN_ALLOWED && validatorPass==true)`
- `Go = ProceedGate`
- `Conditional = (!ProceedGate && heldCount>0 && unresolvedApprovalsAreHeldOnly)`
- `NoGo = (!ProceedGate && !Conditional)`
- `NoGo return path = issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`
- Handoff snapshot（read-only）
  - `SnapshotID=SNAP-HIL-RS-02-A1-CONTRACT-FREEZE-v1`
  - `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
  - `contractIds=A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|A1-ERROR-IF`
  - `safeModeDefault=ON`
  - `sharedResourceFreeze=true`
  - `MutationPolicy=read-only`

## Phase 5: Verify
- Phase開始直前に対象2ファイルを再読し、検証対象と判定式の一致を確認する。
- AC/DoD自己検証を先に実施し、その後 docs-check（validator / unittest / diff check）を順に実行する。
- 失敗時は Self-Correction を最大3回まで実施し、4回目相当はフェイルセーフ停止する。
- `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- `python3 -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
- `git diff --check`

## Phase 6: Proceed（Go / Conditional / No-Go）
- Phase開始直前に対象2ファイルを再読し、Proceed判定式の差分がないことを確認する。
- Go: `ProceedGate=true` かつ AC/DoD全充足、`held` 以外の未承認事項なし。
- Conditional: `ProceedGate=false` だが未承認事項が `held` のみに限定される場合。
- No-Go: SSOT競合、未承認確定、Self-Correction 3回超過、指定外差分。
- No-Go時出力: 原因・影響・再開条件を明文化する。


## 変更凍結セクション（Contract Freeze / Stream B）
- Freeze name: `A1 Interface Contract Freeze v1`
- Immutable IDs:
  - `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
  - `SnapshotID=SNAP-HIL-RS-02-A1-CONTRACT-FREEZE-v1`
- Immutable schema/signature:
  - `schemaVersion=1.0.0`
  - `contractIds=A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|A1-ERROR-IF`
  - `decisionQueueTransition=Pending -> Approved | Pending -> Rejected`
- Start condition（A2/A3 open gate）:
  - `A2A3_OPEN_ALLOWED=true` かつ `Approval Record=Approved`
- Prohibited changes（凍結中禁止）:
  1. Immutable IDs/schemas/signature の変更
  2. `safeModeDefault=ON` / `safeModeBoundary=SAFE_MODE_STRICT_ON` の後退
  3. `overridePolicy=human_dual_control_only` の緩和
  4. `pending` を経由しない確定（bypass）

## Handover Artifact（下流向け固定契約一覧）
- 不変ID: `HIL-RS-02-A1-CONTRACT-FREEZE-v1`, `SNAP-HIL-RS-02-A1-CONTRACT-FREEZE-v1`
- 禁止変更点: Contract ID再定義、schemaVersion改版、safeMode境界緩和、Pending bypass
- モック仕様（推測補完禁止）:
```yaml
mock_contract_v1:
  freeze_contract_id: "HIL-RS-02-A1-CONTRACT-FREEZE-v1"
  schema_version: "1.0.0"
  contract_ids:
    - "A1-CRITIQUE-IF"
    - "A1-REDIFF-IF"
    - "A1-ATTR-IF"
    - "A1-ERROR-IF"
  open_gate:
    a1_status: "Done"
    pending_decision_queue_count: 0
```


## Stream B handover checkpoint（2026-04-27）

### Phase 6 Proceed判定（今回）
- 判定: **Needs-decision**（`Approval Record: Pending` と `held` 論点が残存）。
- Go/No-Go条件: 既存の `ProceedGate` / `NoGo` 判定式を継続適用（再定義しない）。

### 未確定論点一覧（次回引き継ぎ）
1. `Approval Record` の承認主体・時刻・証跡（`approved_by` / `approved_at` / `evidence`）が未入力。
2. `HIL-RS-02-GOV-EXCEPTION-01` は `held` 維持中で、人間判断待ち。
3. A2/A3公開判定は `A1 Done && pendingDecisionQueueCount==0` 未充足のため据え置き。

### No-Go条件の再確認
- self-correction 4回目相当、未承認確定化、未定義競合、allowlist外編集要求を検知した場合は即停止して人間へエスカレーションする。

## Stream B fixed-serial protocol replay（2026-04-27 / Plan→Execute→Verify→Proceed）

- Issue order position: `2/2 FB-P2C-01 A1`
- Protocol lock: 各Phaseで `Plan -> Execute -> Verify -> Proceed` を維持（逆走・省略禁止）。
- Contract lock: `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1` / `safeModeDefault=ON` / `safeModeBoundary=SAFE_MODE_STRICT_ON` / `NoGo return path=issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md` を固定。

### Phase 1: Read
- 対象2ファイルを再読し、`Status / Scope / Dependencies / 固定キー` の差分を確認。
- 差分検知時は `held` 記録のみ許可し、Executeへ進まない。

### Phase 2: ADR/CDC
- Context: A1契約凍結を唯一SSOTとし、A2/A3への派生定義を禁止。
- Decision: 固定キーと `A2A3_OPEN_ALLOWED` 判定式を再定義せず参照専用化。
- Consequences: 未承認事項は `pending/held` 維持（確定扱い禁止）。

### Phase 3: Plan
- AC/DoD不足はDraft提案として追記し、`Approval Record` 合意前は確定化しない。
- 非干渉ルールを再確認し、allowlist外編集を実施しない。

### Phase 4: Execute
- 契約固定の文言同期のみ更新対象とし、実装・派生契約追加は実施しない。
- `safeModeDefault=ON` / `SAFE_MODE_STRICT_ON` / NoGo return path 固定を後退させない。

### Phase 5: Verify
- AC/DoD自己検証後に docs-check（validator / unittest / diff check）を実施。
- self-correctionは `0〜3` 回まで、`4回目相当` は即停止して人間判断へエスカレーション。

### Phase 6: Proceed
- Go/Conditional/No-Go を既存判定式で評価。
- `Approval Record: Pending` または `held` 残存時は `Conditional` または `Needs-decision` を維持。
- フェイルセーフ発火時の報告形式を固定: `原因 / 影響I/F / 要判断点`。


## Stream F execution contract（A1 machine-verifiable freeze）

### Phase 2 Plan補強（tie-break / gate / mock）
- Tie-break Contract ID: `CTR-FB-P0-P2C-A1-TIEBREAK-v1`
- Tie-break policy（機械判定順）:
  1. `freezeContractId`
  2. `schemaVersion`
  3. `overridePolicy`
  4. `contractIds`
  5. `safeModeDefault` + `safeModeBoundary`
  6. `contractLinkLocked` + `sharedResourceFreeze`
- 判定結果:
  - mismatch ≥1: `No-Go`（契約再固定まで停止）
  - mismatch =0: `Execute/Verify` 継続可

### Phase 3 Execute固定（A1契約を機械検証可能粒度へ）
- Canonical predicate（single line / SSOT）:
  - `A2A3_OPEN_ALLOWED = (a1Status=="Done" && pendingDecisionQueueCount==0 && freezeContractId=="HIL-RS-02-A1-CONTRACT-FREEZE-v1" && schemaVersion=="1.0.0" && overridePolicy=="human_dual_control_only" && contractLinkLocked==true && sharedResourceFreeze==true && safeModeDefault=="ON" && safeModeBoundary=="SAFE_MODE_STRICT_ON")`
- Deterministic key set（closed-world）:
  - `freezeContractId,schemaVersion,overridePolicy,contractIds,contractLinkLocked,sharedResourceFreeze,safeModeDefault,safeModeBoundary,pendingDecisionQueueCount,a1Status`
- Unknown key policy:
  - 未定義キー検知は `undefinedConflictDetected=true` として `No-Go`

### Phase 4 Verify補強（mock-first）
- Mock verification must pass before any A2/A3 claim:
  1. `mock_contract_v1` を用いて `A2A3_OPEN_ALLOWED` を3回再評価し、結果一致（3/3）
  2. `contractIds` 順序と要素が固定文字列一致
  3. `NoGo return path` が `issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md` に固定
  4. `Approval Record=Pending` の場合、出力は必ず `Conditional` か `Needs-decision`
- Fail-safe:
  - **契約未固定のままA2/A3確定扱い要求を受けた場合は即停止（No-Go）**

### Phase 5 Proceed（契約IDと禁止遷移の明示）
- Effective contract IDs:
  - `HIL-RS-02-A1-CONTRACT-FREEZE-v1`
  - `SNAP-HIL-RS-02-A1-CONTRACT-FREEZE-v1`
  - `CTR-FB-P0-P2C-A1-TIEBREAK-v1`
- Prohibited transitions（hard fail）:
  1. `Pending -> Done`（Approved bypass）
  2. `Held -> Done`（approval evidenceなし）
  3. `A1 != Done` で `A2/A3 Confirmed`
  4. `safeModeDefault ON` の後退
  5. `SAFE_MODE_STRICT_ON` の緩和

## Stream H convergence update（2026-04-28 / authoritative for A1 contract text）

> 本セクションは Stream H の最新契約整備基準。既存の Stream B / Stream F 記録は履歴として保持し、矛盾時は本セクションを優先する。

### Phase 1: Read（未確定I/F + Decision Queue依存の棚卸し）
- 未確定I/F
  1. `Approval Record` 証跡項目（`approved_by` / `approved_at` / `evidence`）未入力。
  2. `HIL-RS-02-GOV-EXCEPTION-01` は `held` 継続。
  3. `pendingDecisionQueueCount` が 0 でない限り、A2/A3 Openゲートは未達。
- 依存固定: `A1 -> A2 -> A3`。A2/A3はA1契約の read-only 参照を維持。

### Phase 2: Plan（mockで依存分離）
- mock-first 検証対象（実装非依存）
  - `A2A3_OPEN_ALLOWED` 文字列一致
  - `NoGo` 条件一致
  - 不変キー一致（`freezeContractId`,`schemaVersion`,`overridePolicy`,`contractIds`,`safeModeDefault`,`safeModeBoundary`,`contractLinkLocked`,`sharedResourceFreeze`）
- mock dataset: `A1-CONTRACT-MOCK-v1`

### Phase 3: Execute（A1契約確定文のみ整備）
- 実施内容は文言整備に限定し、実装・派生契約・下流手順の追加は禁止。
- ADR更新要否が出た場合は CDC草案を提出して承認待ち（承認まで `held` 固定）。

### Phase 4: Verify（Go/NoGo判定の再現性）
- Go
  - `A2A3_OPEN_ALLOWED=true && validatorPass=true && Approval Record=Approved && pendingDecisionQueueCount==0`
- NoGo
  - `(!A2A3_OPEN_ALLOWED) && (pendingBypassDetected || undefinedConflictDetected || allowlist外編集要求 || 契約未承認でA2/A3確定要求)`
- Conditional
  - Go未達かつ未承認事項が `held` のみ。

### Phase 5: Proceed（A2/A3着手条件固定）
- A2着手: `A1 Done` + `pendingDecisionQueueCount==0` + `Approval Record=Approved`。
- A3着手: A2着手条件充足 + A2側 NoGo なし。
- フェイルセーフ: 契約未承認のまま実装誘導しない。逸脱時は停止し `No-Go` を宣言。

## Stream G reconciliation note（2026-04-29 / FB残件清算）

### 1) Read（Open理由と未完了条件）
- Open理由: A1契約は凍結済みだが、`Approval Record` が `Pending` で `held` 論点が残っている。
- 未完了条件: `approved_by` / `approved_at` / `evidence` 未入力、`pendingDecisionQueueCount==0` 未確認。

### 2) Context / Decision / Consequences（CE/HIL整合維持）
- Context: Stream H（2026-04-28）のA1契約整備基準を authoritative として運用する。
- Decision: CE/HIL現行契約（`freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1` ほか）を**変更しない**。
- Consequences: A2/A3に対する確定シグナルは発行せず、`Conditional | Needs-decision` を維持する。

### 3) 現行CE/HIL計画との整合判定
- 判定: **重複統合（close不可）**。
- 理由: 契約本文はStream Hへ収束済みだが、人間承認系ブロッカーが未解消。

### 4) Plan→Execute→Verify（self-correction上限3）
- Plan: allowlist 2ファイルのみで整合差分を整理し、契約凍結文を維持。
- Execute: A1契約の固定キーと `A2A3_OPEN_ALLOWED` を再定義せず参照専用で扱う。
- Verify: docs-checkと2ファイル照合で、凍結ID・判定式・NoGo導線の不一致がないことを確認。

### 5) Proceed（ブロッカー明示）
- 現在判定: **Needs-decision / Conditional 継続**。
- ブロッカー:
  1. `Approval Record=Approved` の証跡不足。
  2. `HIL-RS-02-GOV-EXCEPTION-01` が `held` のまま。
  3. `pendingDecisionQueueCount==0` の監査確認未完了。
- 再開条件（Close条件）:
  - 上記3点解消後に `A2A3_OPEN_ALLOWED=true`・`validatorPass=true`・`Approval Record=Approved` を同時充足。
