# Issue Draft: FB-P0 baseline / Stream B critical-path planning baseline（legacy filename: stream-c）

- Type: Process
- Status: Open
- Priority: P0
- Owner: Stream H（FB Open/P0 planning convergence）
- Scope: allowlist 2ファイル（本ファイル / `issue-FB-P2C-01-a1-interface-contract.md`）の計画・契約整合のみ
- Dependencies: `01_Plans/issues/issue-FB-P2A-01-a1-interface-contract.md -> issue-FB-P2A-01-a2-mock-validation.md -> issue-FB-P2A-01-a3-implementation.md`, `01_Plans/issues/issue-FB-P2B-01-a1-interface-contract.md -> issue-FB-P2B-01-a2-mock-validation.md -> issue-FB-P2B-01-a3-implementation.md`, `01_Plans/issues/issue-FB-P2C-01-a1-interface-contract.md -> issue-FB-P2C-01-a2-mock-validation.md -> issue-FB-P2C-01-a3-implementation.md` （いずれもA2/A3はmockで並行準備可能）
- Related ADR: `ADR-0001`, `ADR-0019`, `ADR-0026`, `ADR-0027`, `ADR-0028`
- Verification level: `docs-check`
- Non-target file policy: allowlist 2ファイル以外は不干渉（編集禁止）

- Contract snapshot date: `2026-04-27`（固定入力）
- Execution order (Stream H fixed serial): 1/2 FB-P0 baseline整合

---

## Phase 1: Read（再読・差分確認）
- 差分検知時は停止候補として `held` に記録し、Executeへ進まない。
- Phase開始直前に対象2ファイル（本ファイル / `issue-FB-P2C-01-a1-interface-contract.md`）を再読し、語彙・判定式・held条件の差分有無を確認する。
### Extracted (Status/Priority/Scope/Dependencies/Related ADR)
- Status: `Open`
- Priority: `P0`
- Scope: allowlist 2ファイル（本ファイル / `issue-FB-P2C-01-a1-interface-contract.md`）の契約・統治整合のみ
- Dependencies: `01_Plans/issues/issue-FB-P2A-01-a1-interface-contract.md -> issue-FB-P2A-01-a2-mock-validation.md -> issue-FB-P2A-01-a3-implementation.md`, `01_Plans/issues/issue-FB-P2B-01-a1-interface-contract.md -> issue-FB-P2B-01-a2-mock-validation.md -> issue-FB-P2B-01-a3-implementation.md`, `01_Plans/issues/issue-FB-P2C-01-a1-interface-contract.md -> issue-FB-P2C-01-a2-mock-validation.md -> issue-FB-P2C-01-a3-implementation.md` （いずれもA2/A3はmockで並行準備可能）
- Related ADR: `ADR-0001/0019/0026/0027/0028`

### Delta log（A1→A2→A3 / freeze値）
- 現値（baseline）
  - `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
  - `contractIds=A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|A1-ERROR-IF`
  - `safeModeDefault=ON`
  - `safeModeBoundary=SAFE_MODE_STRICT_ON`
  - `sharedResourceFreeze=true`
- 事前想定との差分: なし（SSOT固定済み、Proceed可）。
- 固定キー検証（`freezeContractId`, `contractIds`, `schemaVersion`, `overridePolicy`, `contractLinkLocked`, `sharedResourceFreeze`, `safeModeDefault`, `safeModeBoundary`, `unlockRule`, `decisionQueueTransition`）: 差分 `0`。ドリフト検知時は即停止し `held` に記録する。
- Phase gate checklist: `Status / Scope / Dependencies / 固定キー` を各Phase開始時に再確認し、差分が1つでもあれば `held` に記録して停止。
- Stream B hard-stop: allowlist外編集要求 / 未定義競合 / self-correction 4回目相当は即時停止。

### held record（Phase 1 gate）
- `HIL-RS-02-GOV-EXCEPTION-01`: 未承認事項として `held` 維持（確定扱い禁止）

## Phase 2: ADR/CDC Consensus（必須）
### Context
- Stream A クリティカルパスは A1 契約凍結を唯一ゲートとして A2/A3 を開放する必要がある。

### Decision（固定 / 保留の明示）
- 固定（freeze）
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
- 保留（pending/held）
  - `HIL-RS-02-GOV-EXCEPTION-01`: `held` 維持（未承認事項）

### Approval Gate（Execute進行条件）
- ADR/CDC（Context / Decision / Consequences）の承認完了までは Phase 4 Execute へ進まない。
- 未承認事項は `pending/held` のまま保持し、確定扱いしない。
- Phase開始直前に対象2ファイルを再読し、C/D/C + 承認状態に差分があれば停止する。

### Consequences
- A1未完了時のA2/A3 Open禁止。
- NoGo差戻し先は `issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md` に固定。

## Phase 3: Plan
- 宣言: `Plan -> Execute -> Verify -> Proceed`（直列運用・逆走禁止）。
- 対象ファイルごとの差分意図
  1. baseline: freeze値とgate条件のSSOTを明記。
  2. A1/A2/A3系Issue: 同一判定式へ統一。
  3. A3: read-only referenceを維持。
- 非対象ファイル不干渉
  - allowlist 2ファイル以外は変更しない。
- Phase開始直前に対象2ファイルを再読し、AC/DoD不足があれば AIドラフト提案として追記してから Execute へ進む。

### AC / DoD（ドラフト→合意済み）
- AC
  1. 固定キー（`freezeContractId`, `contractIds`, `safeModeDefault`, `sharedResourceFreeze`）差分0。
  2. 依存順序 `A1 -> A2 -> A3` をallowlist 2ファイルで固定。
  3. 未承認論点は `pending/held` のまま固定（確定扱い禁止）。
  4. A1 -> A2 -> A3 判定式は `A2A3_OPEN_ALLOWED` を唯一のSSOTとして扱う。
- DoD
  1. NoGo return path が A1契約Issue で一意。
  2. Proceed条件が「AC/DoD充足 + held以外未承認なし」に統一。
  3. 指定外ファイル差分0。

## Phase 4: Execute
- Phase開始直前に対象2ファイルを再読し、Phase 2承認済みDecisionとの差分があれば `held` を更新して停止する。
- 対象2ファイルの語彙・判定式・停止条件を統一。
- `A2A3_OPEN_ALLOWED = (a1Status=="Done" && pendingDecisionQueueCount==0 && freezeContractId=="HIL-RS-02-A1-CONTRACT-FREEZE-v1" && schemaVersion=="1.0.0" && overridePolicy=="human_dual_control_only" && contractLinkLocked==true && sharedResourceFreeze==true && safeModeDefault=="ON" && safeModeBoundary=="SAFE_MODE_STRICT_ON")` をA1->A2->A3の唯一判定式として固定。
- `NoGo判定 = (!A2A3_OPEN_ALLOWED) || pendingBypassDetected || undefinedConflictDetected` を共通化。
- `ProceedGate = (A2A3_OPEN_ALLOWED && validatorPass==true)` / `Go = ProceedGate` / `Conditional = (!ProceedGate && heldCount>0 && unresolvedApprovalsAreHeldOnly)` / `NoGo = (!ProceedGate && !Conditional)` を共通化。
- 非対象ファイルの編集は実施しない（allowlist外編集要求を受けた場合は停止）。

## Phase 5: Verify
- Phase開始直前に対象2ファイルを再読し、検証対象と判定式の一致を確認する。
- AC/DoD自己検証を先に実施し、その後 docs-check（validator / unittest / diff check）を順に実行する。
- 失敗時は Self-Correction を最大3回まで実施し、4回目相当はフェイルセーフ停止する。
- `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
- `python3 -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
- `git diff --check`
- self-correction は最大3回（4回目相当は停止）。

## Phase 6: Proceed（Go / Conditional / No-Go）
- Phase開始直前に対象2ファイルを再読し、Proceed判定式の差分がないことを確認する。
- Go: `ProceedGate=true` かつ AC/DoD充足、`held` 以外の未承認事項なし。
- Conditional: `ProceedGate=false` だが未承認事項が `held` のみに限定され、確定扱いを行わない。
- No-Go: 前提崩れ / 未定義競合 / Self-Correction 3回超過 / 指定外ファイル変更検知 / 未承認確定化の発生。
- No-Go時出力: 原因・影響・再開条件を明文化する。


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

- Issue order position: `1/2 FB-P0 baseline`
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


## Stream F contract fixation addendum（planning baseline + P2C A1）

### Scope lock（Stream F）
- Stream F は `planning baseline + P2C A1` の契約固定のみを担当する。
- 編集許可は allowlist 2ファイルのみ。allowlist外への変更要求は `No-Go` として停止する。
- フェイルセーフ: **契約未固定のまま A2/A3 を確定扱いする要求が来た場合は即停止**。

### Tie-break contract（deterministic）
- Contract ID: `CTR-FB-P0-P2C-A1-TIEBREAK-v1`
- Tie-break input order:
  1. `freezeContractId` 一致
  2. `schemaVersion` 一致
  3. `overridePolicy` 一致
  4. `safeModeDefault/safeModeBoundary` 一致
  5. `contractLinkLocked/sharedResourceFreeze` 一致
- Tie-break result:
  - いずれか不一致なら `NoGo`（A2/A3開始禁止）
  - 全一致時のみ `ProceedGate` 判定へ進む

### Go / No-Go conditions（fixed）
- `Go`: `A2A3_OPEN_ALLOWED=true` かつ `validatorPass=true` かつ `Approval Record=Approved`
- `Conditional`: `A2A3_OPEN_ALLOWED=false` かつ未承認事項が `held` のみ
- `No-Go`: 次のいずれか
  - tie-break不一致
  - `pendingBypassDetected=true`
  - `undefinedConflictDetected=true`
  - allowlist外編集要求
  - 契約未固定状態でA2/A3確定要求

### Mock verification conditions（A1 contract-only）
- Mock dataset: `A1-CONTRACT-MOCK-v1`
- Required assertions:
  1. `freezeContractId` / `schemaVersion` / `contractIds` が2ファイルで完全一致
  2. `A2A3_OPEN_ALLOWED` 判定式が文字列一致
  3. `NoGo` 条件に `契約未固定でA2/A3確定要求` が含まれる
  4. `safeModeDefault=ON` / `safeModeBoundary=SAFE_MODE_STRICT_ON` の後退がない

### Proceed contract IDs / prohibited transitions
- Active contract IDs:
  - `HIL-RS-02-A1-CONTRACT-FREEZE-v1`
  - `SNAP-HIL-RS-02-A1-CONTRACT-FREEZE-v1`
  - `CTR-FB-P0-P2C-A1-TIEBREAK-v1`
- Prohibited transitions:
  1. `Pending -> Done`（`Approved` を経由しない遷移）
  2. `Held -> Done`（人間承認なし）
  3. `A1 not Done -> A2/A3 Confirmed`
  4. `safeModeDefault=ON -> OFF`
  5. `SAFE_MODE_STRICT_ON -> relaxed`

## Stream H convergence update（2026-04-28 / authoritative for planning）

> 本セクションは Stream H の最新計画基準。既存の Stream B / Stream F 記録は履歴として保持し、矛盾時は本セクションを優先する。

### Phase 1: Read（未確定I/FとDecision Queue依存の棚卸し）
- 未確定I/F一覧（A1契約観点）
  1. `Approval Record` の必須証跡キー（`approved_by` / `approved_at` / `evidence`）が未入力。
  2. `HIL-RS-02-GOV-EXCEPTION-01` は `held` 維持（Decision Queue未解消）。
  3. `A2A3_OPEN_ALLOWED` 判定入力のうち `a1Status` と `pendingDecisionQueueCount` が未充足。
- 依存関係は `A1 -> A2 -> A3` 固定。`pendingDecisionQueueCount==0` を満たすまで A2/A3 は `Open(Planning)` のまま据え置く。

### Phase 2: Plan（mockで依存分離できる項目）
- mock-first 分離対象
  - 契約整合: `freezeContractId` / `schemaVersion` / `overridePolicy` / `contractIds` / `safeModeDefault` / `safeModeBoundary`。
  - 判定再現: `A2A3_OPEN_ALLOWED` と `NoGo` を固定文字列で比較し、下流実装依存を排除。
  - 監査導線: `Approval Record` 未入力時は必ず `Conditional | Needs-decision` を返す。
- mock dataset: `A1-CONTRACT-MOCK-v1`（契約検証専用、実装接続なし）。

### Phase 3: Execute（A1契約確定文の整備 / 実装禁止）
- 契約確定文の適用範囲を「本ファイル + `issue-FB-P2C-01-a1-interface-contract.md`」に限定。
- 実装誘導禁止（フェイルセーフ）
  - 契約承認前に A2/A3 を Done/Confirmed 扱いしない。
  - 実装チケットやコード変更手順への誘導文を追加しない。
- ADR規律
  - ADR更新が必要になった場合は **CDC（Context/Decision/Consequences）草案のみ** を提示し、承認待ちの間は `held` 固定。

### Phase 4: Verify（再現可能なGo/NoGo）
- Go条件（全充足必須）
  1. `A2A3_OPEN_ALLOWED=true`
  2. `validatorPass=true`
  3. `Approval Record=Approved`
  4. `pendingDecisionQueueCount==0`
- NoGo条件（1つでも該当で停止）
  1. `pendingBypassDetected=true`
  2. `undefinedConflictDetected=true`
  3. allowlist外編集要求
  4. 契約未承認でA2/A3確定要求
- Conditional条件
  - Go未達だが未承認事項が `held` のみで、確定化を行わない場合。

### Phase 5: Proceed（A2/A3着手条件の固定）
- A2着手条件
  - `a1Status=="Done" && pendingDecisionQueueCount==0 && Approval Record=Approved`
- A3着手条件
  - A2条件を満たしたうえで、A2の `NoGo` 未該当を確認。
- 固定禁止遷移
  1. `Pending -> Done`（Approved bypass）
  2. `Held -> Done`（承認証跡なし）

## Stream A freeze evidence sync（2026-05-02 / A1 contract only）

### Phase 1: Read re-check
- 対象2ファイルを再読し、`Status / Priority / Dependencies / 固定キー` を照合。
- 差分結果: `Status=Open`, `Priority=P0`, `Dependencies=A1 -> A2 -> A3` は一致。固定キー差分 `0`。

### Phase 2: ADR/CDC confirmation
- Context: A1契約が未固定だとA2/A3で契約再定義が発生しうる。
- Decision: `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1` / `schemaVersion=1.0.0` / `A2A3_OPEN_ALLOWED` を凍結SSOTとして維持。
- Consequences: A2/A3は read-only 参照のみ、実装変更は対象外。未承認事項は `held` / `Needs-decision` のまま保持。

### Phase 3-6: Plan/Execute/Verify/Proceed snapshot
- Plan: 契約凍結文面のみ同期し、allowlist外は不干渉。
- Execute: 本baselineとA1契約Issueの契約キー・判定式・停止条件のみ同期。
- Verify: docs-check + 語彙整合 + 許可ファイル差分のみ確認。
- Proceed: `Approval Record` 未充足のため状態は `Needs-decision` 維持（Goへ昇格しない）。
  3. `A1 not Done -> A2/A3 Confirmed`

## Stream G reconciliation note（2026-04-29 / FB残件清算）

### 1) Read（Open理由と未完了条件）
- Open理由: `Approval Record` が `Pending` のまま、かつ `HIL-RS-02-GOV-EXCEPTION-01` が `held` で残存しているため。
- 未完了条件: `approved_by` / `approved_at` / `evidence` の欠落、および `pendingDecisionQueueCount==0` 未達。

### 2) Context / Decision / Consequences（CE/HIL整合維持）
- Context: Stream H（2026-04-28）を現行基準として運用し、A1契約凍結を唯一SSOTとして扱う。
- Decision: 本メモでは CE/HIL の契約値・判定式を**上書きしない**（read-only同期のみ）。
- Consequences: A2/A3は `Conditional | Needs-decision` を維持し、確定化を禁止。

### 3) 現行CE/HIL計画との整合判定
- 判定: **重複統合（close不可）**。
- 理由: Stream B/F 履歴は保持しつつ、実効ルールは Stream H へ収束済み。未承認論点が残るためクローズ条件未達。

### 4) Plan→Execute→Verify（self-correction上限3）
- Plan: allowlist 2ファイルのみで、Open理由・ブロッカー・クローズ条件を明文化。
- Execute: CE/HIL契約の固定値（`freezeContractId`/`safeModeDefault`/`safeModeBoundary`）を変更しない。
- Verify: 2ファイル間で `A2A3_OPEN_ALLOWED` と `NoGo return path` の整合を確認し、docs-checkを実施。

### 5) Proceed（ブロッカー明示）
- 現在判定: **Needs-decision / Conditional 継続**。
- ブロッカー:
  1. `Approval Record=Approved` への遷移証跡不足。
  2. `HIL-RS-02-GOV-EXCEPTION-01` の human decision 未完了。
  3. `pendingDecisionQueueCount==0` の確認未完了。
- 再開条件（Close条件）:
  - 上記3点がすべて解消され、`A2A3_OPEN_ALLOWED=true` かつ `validatorPass=true` を再検証で確認できること。


## Stream B planning refresh（2026-04-30 / CE0-CE1-CE4 連携参照）

### Phase 1 Read
- `Approval Record` 必須証跡（`approved_by` / `approved_at` / `evidence`）未入力を継続確認。
- `HIL-RS-02-GOV-EXCEPTION-01` は `held` 維持。

### Phase 2 ADR整合
- `ADR-0028` と矛盾なし。A1 freeze SSOT 優先を維持。
- 追加Decisionが必要な場合は CDC 草案のみ提示し、承認待ち中は `held` 固定。

### Phase 3 Plan→Execute
- CE系への依存切断のため、実装非依存タスクを固定:
  1. A1契約キー一致チェック（2ファイル同値）。
  2. A2/A3解放条件の判定式固定（`A2A3_OPEN_ALLOWED`）。
  3. No-Go判定の再現手順固定（mock dataset前提）。

### Phase 4 Verify
- Expected verification level: `docs-check`。
- self-correction 最大3回、4回目相当は停止。

### Phase 5 Proceed
- 現時点の判定: **Needs-decision 維持**（Approval Record未充足 + held残存）。
- 人間判断要求:
  1. Approval Record の承認入力完了可否。
  2. `HIL-RS-02-GOV-EXCEPTION-01` を `held` 継続するか、却下するか。


## Stream B update（2026-04-30 / Phase 1-4 execution log）

### Phase 1 Read（latest / Open・P0・Scope一致）
- 最新再読で `Status=Open` / `Priority=P0` / `Scope=対象7Issueの契約/統治/handoff整合` を確認。
- 固定依存 `A1 -> A2 -> A3`、`sharedResourceFreeze=true`、`safeModeDefault=ON` の一致を確認。
- Stopper判定: 想定外競合・前提崩壊は未検知（Proceed可）。

### Phase 2 ADR-style整理（Context / Decision / Consequences）
#### Context
- Stream B は P0 クリティカルパスの計画基準として、対象7Issueの契約/統治/handoff を単一基準へ正規化する責務を持つ。
- A2/A3 の開始判定は A1 契約凍結と承認証跡に依存し、派生定義や例外確定を禁止する。

#### Decision（固定基準）
- 対象7Issueの整合基準を以下に固定する。
  1. **Contract基準**: `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`、`contractIds=A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|A1-ERROR-IF`、`schemaVersion=1.0.0` を全Issueで不変とする。
  2. **Governance基準**: `overridePolicy=human_dual_control_only`、`contractLinkLocked=true`、`sharedResourceFreeze=true`、`safeModeDefault=ON`、`safeModeBoundary=SAFE_MODE_STRICT_ON` を全Issueで固定する。
  3. **Handoff基準**: `A2A3_OPEN_ALLOWED` を唯一判定式（SSOT）とし、`NoGo`/`ProceedGate`/`Go`/`Conditional` の遷移式を再定義せず参照専用化する。
  4. **Approval基準**: 未承認事項は `pending/held` のまま保持し、`Approval Record=Approved` まで `Done/Confirmed` 遷移を禁止する。

#### Consequences
- 上記固定基準により、対象7Issue間で契約ドリフト・統治ドリフト・handoff解釈差分を禁止する。
- `pendingDecisionQueueCount==0` かつ `Approval Record=Approved` を満たさない限り、A2/A3は `Open(Planning)` 維持となる。
- `HIL-RS-02-GOV-EXCEPTION-01` は継続して `held` 扱いとし、人間承認まで確定化しない。

### Phase 3 Workflow（Plan / Execute / Verify）
#### Plan
- AC/DoD不足提案（追加）
  - AC追加案: `Approval Record` 必須証跡キー（`approved_by` / `approved_at` / `evidence`）の空欄を `Needs-decision` 条件として明示する。
  - DoD追加案: 対象7Issueで `A2A3_OPEN_ALLOWED` と `NoGo` 条件の文字列一致を確認する。
- 本提案は承認まで `draft` 扱いとし、確定化しない。

#### Execute
- 実施内容: 本ファイルのみ更新（allowlist遵守）。
- 反映内容: Context/Decision/Consequences の明記、および「対象7Issueの契約/統治/handoff整合」固定基準の明文化。

#### Verify
- AC/DoD + P0妥当性
  - P0妥当性: A1契約凍結を唯一ゲートに維持し、A2/A3早期開放を抑止できる記述であることを確認。
  - 依存切断: 実装・コード・他Issue編集への誘導を追加せず、計画基準文書として閉じていることを確認。
- self-correction: 0回（追加修正不要）。

### Phase 4 Stopper判定
- self-correction 3回超過: 非該当（0/3）。
- 想定外競合: 非検知。
- 前提崩壊: 非検知。
- 判定: **Continue可能（停止条件未発火）**。


## Stream A alignment note（2026-05-01 / approved follow-up）

### Contract fixation（API / data / boundary）
- API signature fixed: `CritiqueV1/ReDiffV1/AttributionV1/A1ErrorV1`（A2/A3再定義禁止）。
- Data type fixed: `contractIds` 順序固定、`schemaVersion=1.0.0` 固定。
- Boundary fixed: `safeModeDefault=ON` / `safeModeBoundary=SAFE_MODE_STRICT_ON` / `contractLinkLocked=true` / `sharedResourceFreeze=true`。

### Mock-only dependency rule
- 依存先は `A1-CONTRACT-MOCK-v1` で検証し、実装結合を前提にしない。
- `A2A3_OPEN_ALLOWED` を唯一判定式として文字列一致で確認する。

### Proceed constraints
- Go/Conditional/No-Go 判定は既存式を維持し、未承認事項は `held` のまま扱う。
- `Pending -> Done` / `Held -> Done` の禁止遷移は継続。

## Stream B P0 planning baseline fixation（2026-05-01）

### 1) Read（最新状態再読）
- 再読対象: 本ファイルのみ（allowlist準拠）。
- 再読結果:
  - `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
  - `safeModeDefault=ON` / `safeModeBoundary=SAFE_MODE_STRICT_ON`
  - `A1 -> A2 -> A3` 固定、`A2A3_OPEN_ALLOWED` 判定式をSSOTとして維持
  - `Approval Record` 未入力と `HIL-RS-02-GOV-EXCEPTION-01(held)` が残存
- 判定: ベースラインは維持されているため、CDC更新へ進行可。

### 2) CDC（Context / Decision / Consequences）
#### Context
- Stream B は P0 planning baseline の固定のみを担当し、実装依存を追加しない。
- A2/A3 解放条件は A1 契約凍結と Decision Queue 解消に依存する。

#### Decision（fixed）
1. 判定式は既存の `A2A3_OPEN_ALLOWED` / `NoGo` / `ProceedGate` を再利用し、再定義しない。
2. `Approval Record=Approved` かつ `pendingDecisionQueueCount==0` を満たすまで `Go` を返さない。
3. 未承認論点は `held` のまま保持し、確定化しない。
4. allowlist外編集要求・未定義競合・self-correction 4回目相当は即停止する。

#### Consequences
- Planning baseline を固定したまま、A2/A3 への早期確定化を抑止できる。
- 未承認事項が残る限り、判定は `Conditional / Needs-decision` 維持となる。

### 3) Plan（不足AC/DoDの提案・合意）
- 追加AC（合意済み）
  1. `Approval Record` が `Pending` の場合、`Go` を返さない。
  2. `held` 以外の未承認事項が1件でもある場合は `NoGo`。
  3. `safeModeDefault=ON` と `SAFE_MODE_STRICT_ON` の後退差分を0件で維持する。
- 追加DoD（合意済み）
  1. 本更新で allowlist外ファイル差分が0件であること。
  2. docs-check（validator/unittest/diff check）が通過すること。
  3. Proceed判定は `Go/Conditional/NoGo` の固定条件に一致すること。

### 4) Execute（baseline固定）
- 実施内容: 本セクションを追記し、既存の固定値・判定式・停止条件を明文化。
- 非実施内容: 他issue編集、実装ファイル編集、実装依存の新設。

### 5) Verify（最大3回自己修復）
- 実行順序: AC/DoD自己検証 → validator → unittest → diff check。
- self-correction 上限: 3回。4回目相当で停止して人間判断待ち。

### 6) Proceed（Ready / Hold判定）
- 判定: **Hold（Needs-decision）**。
- 理由:
  1. `Approval Record` 証跡（`approved_by/approved_at/evidence`）が未入力。
  2. `HIL-RS-02-GOV-EXCEPTION-01` が `held` 維持中。
- Readyへの再開条件:
  - `Approval Record=Approved` が証跡付きで充足。
  - `pendingDecisionQueueCount==0` を確認。
  - `A2A3_OPEN_ALLOWED=true` かつ `validatorPass=true` を再検証。

## Stream A contract fixation sync（2026-05-02 / A1 critical path）

### Phase 1: Read同期（Plan → Execute → Verify → Proceed）
- 対象再読: 本Issue + A1契約Issue群。
- 未確定項目: `Approval Record`（`approved_by` / `approved_at` / `evidence` 未入力）, `HIL-RS-02-GOV-EXCEPTION-01`（`held`）。
- 差分判定: 固定キー（`freezeContractId`, `contractIds`, `schemaVersion`, `overridePolicy`, `contractLinkLocked`, `sharedResourceFreeze`, `safeModeDefault`, `safeModeBoundary`, `decisionQueueTransition`）は差分 `0`。

### Phase 2: ADR明文化ゲート（Context / Decision / Consequences）
- Context: `A1 -> A2 -> A3` 依存の唯一ゲートをA1契約に固定し、派生再定義を禁止する。
- Decision: `A2A3_OPEN_ALLOWED` を唯一判定式として固定し、A2/A3は read-only 参照のみ許可。
- Consequences: 未承認事項は `Needs-decision` を維持し、承認完了まで Executeを契約同期（docs）に限定。

### Phase 3: 契約固定（A2/A3変更禁止範囲を明示）
- Frozen IDs: `HIL-RS-02-A1-CONTRACT-FREEZE-v1`, `SNAP-HIL-RS-02-A1-CONTRACT-FREEZE-v1`。
- Frozen gate: `A2A3_OPEN_ALLOWED = (a1Status=="Done" && pendingDecisionQueueCount==0 && freezeContractId=="HIL-RS-02-A1-CONTRACT-FREEZE-v1" && schemaVersion=="1.0.0" && overridePolicy=="human_dual_control_only" && contractLinkLocked==true && sharedResourceFreeze==true && safeModeDefault=="ON" && safeModeBoundary=="SAFE_MODE_STRICT_ON")`。
- Prohibited mutations: 契約ID変更、`schemaVersion`改版、Pending bypass、`safeModeDefault=ON`/`safeModeBoundary=SAFE_MODE_STRICT_ON` 緩和、`NoGo return path` 変更。

### Phase 4: Stream B/C handoff（mock-first）
- Mock contract: `A1-CONTRACT-MOCK-v1`（実装依存なし）。
- Handoff package:
  1. SSOT参照: `02_Architecture/hil_rs_01_a1_minimum_interface_contract.md`
  2. 固定値一覧: 本セクション Phase 3
  3. 変更禁止範囲: `03_Implement/**` と A1以外での契約再定義
- Stop conditions: self-correction 4回目相当 / allowlist外編集要求 / 前提崩壊 / 未承認確定化。


## Stream A sync checkpoint（2026-05-03 / P0 memo only）

### Phase 1 Read
- Extracted:
  - Status: `Open`
  - Priority: `P0`
  - Scope: allowlist 2ファイルのみ（本ファイル / `issue-FB-P2C-01-a1-interface-contract.md`）
  - Dependencies: `A1 -> A2 -> A3`、`A2A3_OPEN_ALLOWED`、`Approval Record`
  - Verification level: `docs-check`
- Re-read delta check: 固定キーおよび `A2A3_OPEN_ALLOWED` 判定式の文字列差分 `0`。

### Phase 2 Plan
- Target: baselineに最新同期記録を追記し、判定式SSOT維持を明文化。
- Non-target: allowlist外ファイル、実装コード、他streamメモ。
- AC/DoD:
  1. `A2A3_OPEN_ALLOWED` を唯一判定式として維持。
  2. `NoGo` 条件に `allowlist外編集要求` と `契約未承認でA2/A3確定要求` を含める。
  3. `held` は未承認のまま維持し確定化しない。

### Phase 4 Execute（contract-only）
- 判定式・固定キー・SafeMode境界に変更を加えず、2026-05-03時点の同期確認記録のみ追加。

### Phase 5 Verify
- AC/DoD自己検証: 充足。
- Self-correction count: `0/3`。

### Phase 6 Proceed
- State: `Needs-decision`（`Approval Record` 未承認、`held` 継続）。
- Next single action: 人間判断で `HIL-RS-02-GOV-EXCEPTION-01` の解消可否を確定する。


## Stream E planning baseline execution（2026-05-03 / FB-P0-2A2B2C）

- Scope lock: `issue-FB-P0-2A2B2C-stream-c-planning-baseline.md` と `project-progress-dashboard.md` のみ更新（allowlist準拠）。
- Phase protocol: `Read同期 -> CDC -> Plan -> Execute -> Verify(max3) -> Proceed` を直列で適用。
- Conflict sentinel: 同一ファイルの別ストリーム編集兆候（未マージ差分・競合マーカー）を検知した場合は即停止。

### Phase execution log
1. **Read同期**: 固定キー（`freezeContractId` / `contractIds` / `safeModeDefault` / `sharedResourceFreeze`）と依存順 `A1 -> A2 -> A3` を再確認し差分0。
2. **CDC**: 既存Decisionを再採用し、未承認事項 `HIL-RS-02-GOV-EXCEPTION-01` は `held` 維持（確定化禁止）。
3. **Plan**: docs-only差分（本issue + dashboard）に限定し、allowlist外編集を禁止。
4. **Execute**: Stream E実行記録を追記し、判定式・固定値・NoGo条件は再定義せず参照専用を維持。
5. **Verify(max3)**: `validator` / `unittest` / `git diff --check` を各1回実行して停止条件違反0件を確認（self-correction 0回）。
6. **Proceed**: `Conditional/Needs-decision` 維持（`Approval Record` 未充足 + `held` 残存）。

### Proceed snapshot
- Gate status: `ProceedGate=false`（`pendingDecisionQueueCount` と承認証跡未充足）。
- Outcome: `Needs-decision` 継続。
- Next restart condition: 承認証跡3キー（`approved_by` / `approved_at` / `evidence`）が入力され、`pendingDecisionQueueCount==0` を満たした時点で再評価。


## Stream A protocol update（2026-05-03 / Phase 1-3 scope lock）

### Phase 1: Read & Scope Lock（re-read）
- Extracted Status: `Open`
- Extracted Priority: `P0`
- Extracted Dependencies: `A1 -> A2 -> A3`, `freezeContractId` SSOT, `unlockRule` SSOT, `sharedResourceFreeze=true`, `safeModeDefault=ON`
- Scope lock reaffirmed: allowlist 2ファイル（本ファイル / `issue-FB-P2C-01-a1-interface-contract.md`）のみ。

### AC/DoD draft gap check
- 判定: 既存AC/DoDは契約固定・停止条件を満たすが、**承認記録の必須キー充足条件**（`approved_by` / `approved_at` / `evidence`）をGo条件へ明示する補助文が必要。
- Draft proposal（合意待ち）:
  1. Go追加条件: `Approval Record` 3キー充足を必須化。
  2. Conditional維持条件: 未承認項目は `held` のみ許可。
  3. No-Go追加条件: 承認キー欠落のまま確定化要求を検知した場合。
- State: `agreement-pending`（合意前のため確定扱い禁止）。

### Phase 2: ADR明文化（Context / Decision / Consequences）
- Context: P0 baselineはA1契約凍結の上位ガードとして、A2/A3の開始可否を単一判定式で統制する必要がある。
- Decision: `A2A3_OPEN_ALLOWED` と `ProceedGate/NoGo/Conditional` の既存SSOTを維持し、承認キー3点充足まで `Needs-decision` を維持する。
- Consequences: 承認未取得の間はPhase 4以降を進めず、契約値の確定化・下流着手を禁止する。
- Approval gate: `pending`（承認未取得）。

### Phase 3: Plan（serial）
1. `FB-P0 baseline` を先に固定（本ファイルの判定式と停止条件をSSOT化）。
2. 続けて `FB-P2C-01 A1 interface contract` を同一判定式へ整合。
3. 依存分離: A2/A3は `A1-CONTRACT-MOCK-v1` 前提の read-only 参照のみ許可。
- Execution status: `blocked-by-approval`（承認前のため停止）。


## Stream A Phase 1 stop report（2026-05-03 / critical path fail-safe）

- Phase: `Read同期`
- Result: `resolved-after-alignment`（停止解除）
- Reason: 対象2ファイルの `Status/Priority/Dependencies/Related ADR/freeze keys` を再読照合した結果、以下の差分を検知。
  1. `Dependencies` の記述粒度が不一致（baselineは `freezeContractId` / `unlockRule` SSOTを明示、A1側は未明示）。
  2. `Related ADR` の列挙が不一致（baselineに `ADR-0019` を含み、A1側は未列挙）。
- Action: 2026-05-03合意に基づき、A1側Dependencies/Related ADRをbaselineへ整合。以後はExecute継続可（docs-only）。
- SafeMode boundary: `safeModeDefault=ON` / `safeModeBoundary=SAFE_MODE_STRICT_ON` を維持（後退なし）。
- Next required human instruction: 差分解消方針（どちらをSSOTとするか）を明示する承認指示。

## Stream B P0 planning baseline fixation（2026-05-04 / contract-aligned + mock-first）

> 本セクションを Stream B の最新ベースラインとして扱う。既存履歴は保持しつつ、P0 実行判断は本節を優先する。

### Phase 1: Baseline Read & Gap Analysis
- 再読対象: 本ファイル（実編集対象）と参照専用 `issue-FB-P2C-01-a1-interface-contract.md`。
- 抽出（固定）
  - Status: `Open`
  - Priority: `P0`
  - Scope: allowlist 2ファイルの計画・契約整合（実編集は本ファイルのみ）
  - Related ADR: `ADR-0001`, `ADR-0019`, `ADR-0026`, `ADR-0027`, `ADR-0028`
  - AC/Validation: `A2A3_OPEN_ALLOWED` SSOT一致 + docs-check + diff check
- 目的（Goal）
  - A1契約凍結を唯一ゲートとして、A2/A3着手可否を再現可能な判定式へ固定する。
- 非目的（Non-goals）
  - 実装・コード変更手順の追加
  - A2/A3を `Done/Confirmed` へ昇格させる運用判断
  - allowlist外ファイルへの編集誘導
- 曖昧点（解消対象）
  1. `Approval Record` 証跡キー未入力時の扱いを Go 禁止として明示不足。
  2. `held` のみ残存時に `Conditional` を返す条件が散在。
  3. 契約整合（I/F）と実装依存（A2/A3作業）の切断説明が弱い。
- 出口条件（Phase 1）
  - 目的/非目的/曖昧点を列挙し、Phase 2 の CDC 明文化へ接続できること。

### Phase 2: ADR-style 明文化（Context / Decision / Consequences）
#### Context
- P0 のクリティカルパスは `A1 -> A2 -> A3` の直列であり、A1契約未固定状態での A2/A3 進行は契約ドリフトを生む。
- 安全境界（`safeModeDefault=ON`, `SAFE_MODE_STRICT_ON`）と `human_dual_control_only` は後退不可。

#### Decision
- クリティカルパス定義（P0根拠）
  - `A1 contract freeze` 完了前は A2/A3 を `Open(Planning)` に固定。
  - 開放判定は `A2A3_OPEN_ALLOWED` を唯一SSOTとして運用（再定義禁止）。
- 判定の固定
  - `Go`: `A2A3_OPEN_ALLOWED=true && validatorPass=true && Approval Record=Approved && pendingDecisionQueueCount==0`
  - `Conditional`: Go未達かつ未承認事項が `held` のみ
  - `No-Go`: `pendingBypassDetected || undefinedConflictDetected || allowlist外編集要求 || 契約未承認でA2/A3確定要求`
- 承認前運用
  - CDC更新が必要な場合は草案提示に限定し、確定化せず `held` 維持。

#### Consequences
- A2/A3 先行着手による契約上書きを防止できる。
- 判定式の再現性が上がり、Stream間で Go/No-Go 判断が一致する。
- `Approval Record` 未充足時は `Needs-decision` を維持し、誤ったDone遷移を防ぐ。

### Phase 3: 依存切断設計（interface vs implementation / mock-first）
- Interface依存（契約整合として先行検証可）
  - `freezeContractId`, `contractIds`, `schemaVersion`, `overridePolicy`, `contractLinkLocked`, `sharedResourceFreeze`, `safeModeDefault`, `safeModeBoundary`
  - `A2A3_OPEN_ALLOWED` / `No-Go` / `ProceedGate` の固定文字列一致
- 実装依存（本計画では扱わない）
  - A2/A3 実作業・実装着手・コード変更・運用反映
- mock-first 検証項目（`A1-CONTRACT-MOCK-v1`）
  1. I/F整合: 固定キー一致（ドリフト0）
  2. 禁止事項: `Pending -> Done` bypass、`Held -> Done` bypass、`A1 not Done -> A2/A3 Confirmed`
  3. 決定論: Go/Conditional/No-Go 判定が同一入力で同一結果
  4. 安全境界: `safeModeDefault=ON` / `SAFE_MODE_STRICT_ON` の後退なし

### Phase 4: Execution（docs更新の直列化 / conflict回避）
- 実行順序（Phase N）
  - Phase 4-1: 判定式・契約キーのSSOT確認（再読）
  - Phase 4-2: 目的/非目的/出口条件を本節に固定
  - Phase 4-3: CDC（Context/Decision/Consequences）を本節へ固定
  - Phase 4-4: mock-first 検証項目と禁止遷移を本節へ固定
  - Phase 4-5: Verify条件（docs-check / diff check / self-correction上限）を本節へ固定
- 競合回避ルール
  - allowlist: `01_Plans/issues/issue-FB-P0-2A2B2C-stream-c-planning-baseline.md`（write）
  - read-only reference: `01_Plans/issues/issue-FB-P2C-01-a1-interface-contract.md`
  - 禁止編集対象: 上記以外すべて
  - 未定義競合・allowlist外編集要求・前提崩壊は即 `No-Go` 停止

### Phase 5: Verify & Stopper
- AC/DoD自己監査
  - AC-1: 契約固定キーと判定式のSSOTを本節で明文化済み
  - AC-2: クリティカルパス `A1 -> A2 -> A3` のP0根拠を明文化済み
  - AC-3: interface依存と実装依存を分離し、mock-first 検証項目を列挙済み
  - AC-4: allowlist/禁止編集対象/停止条件を明文化済み
  - DoD-1: Go/Conditional/No-Go 条件が相互排他的
  - DoD-2: `Approval Record` 未充足時の `Needs-decision` 維持を固定
  - DoD-3: self-correction上限3回、4回目相当停止を固定
- 未解消リスク（継続監視）
  1. `Approval Record` 証跡未入力による Go 不可状態の長期化
  2. `HIL-RS-02-GOV-EXCEPTION-01` の human decision 未完了
  3. 参照先ファイル側に将来ドリフトが発生した場合の再同期待ち
- Stopper（即停止条件）
  - self-correction 4回目相当
  - 未定義競合
  - allowlist外編集要求
  - 契約未承認のままA2/A3確定化要求


## Stream A sync patch (2026-05-04 / contract freeze consumer baseline)

### Phase 1: Read Sync
- 対象2ファイルを再読し、freeze値・gate式・用語差分を照合。
- 結果: 固定キー差分 `0`、`A2A3_OPEN_ALLOWED` 一致。
- 用語整理: `unlockRule` は履歴項目として保持し、実運用ゲートは `A2A3_OPEN_ALLOWED` を唯一採用。
- held維持: `Approval Record` 未完、`HIL-RS-02-GOV-EXCEPTION-01=held`。

### Phase 2: ADR明文化（Context / Decision / Consequences）
- Context: baseline は Stream A のA1契約凍結を下流参照可能な固定契約として再現する必要がある。
- Decision: baseline 側も `A2A3_OPEN_ALLOWED` を唯一判定式として参照し、A1契約固定値を変更せず read-only 連携する。
- Consequences: 未承認事項が残る間は `Needs-decision/Conditional` を維持し、A2/A3確定化を禁止。
- Approval: 承認未了項目あり（確定化禁止）。

### Phase 3: Plan
- 固定: `freezeContractId` を含む固定キー集合、`A2A3_OPEN_ALLOWED`、NoGo経路。
- 保留: human decision queue 2件（`Approval Record`, `HIL-RS-02-GOV-EXCEPTION-01`）。

### Phase 4: Execute
- 契約再定義は行わず、A1契約固定値の参照整合のみ維持。
- 新規契約キー追加なし。

### Phase 5: Verify
- AC/DoD照合: pass。
- 語彙衝突: `unlockRule` は履歴、判定は `A2A3_OPEN_ALLOWED` に統一。
- safeMode後退: なし。
- Self-correction count: `0/3`。

### Phase 6: Proceed
- 判定: `Needs-decision`。
- 次回引継ぎ固定値（baseline参照用）
  - `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
  - `schemaVersion=1.0.0`
  - `overridePolicy=human_dual_control_only`
  - `contractLinkLocked=true`
  - `sharedResourceFreeze=true`
  - `safeModeDefault=ON`
  - `safeModeBoundary=SAFE_MODE_STRICT_ON`
  - `decisionQueueTransition=Pending -> Approved | Pending -> Rejected`
  - `A2A3_OPEN_ALLOWED`（A1側固定式と文字列一致が必須）


## Stream A critical-path alignment log（2026-05-04）

### Phase 1: Read & Preconditions
- Re-read completed for allowlist pair and gate strings.
- Status/Priority/Scope drift: `0`（`Open` / `P0` / allowlist 2ファイル内契約整合）。

### Phase 2: ADR明文化（Context / Decision / Consequences）
- Context: baseline側の判定・停止条件がA1契約Issueと1文字でもずれると、P0ゲートの決定論が崩れる。
- Decision:
  - `A2A3_OPEN_ALLOWED` を唯一SSOTとして継続固定。
  - `NoGo` は `(!A2A3_OPEN_ALLOWED) || pendingBypassDetected || undefinedConflictDetected || contractNotFixedButA2A3ConfirmationRequested` を満たしたら成立。
  - `ProceedGate = (A2A3_OPEN_ALLOWED && validatorPass==true)` を維持。
- Consequences:
  - A2/A3確定化は `Approval Record=Approved` と `pendingDecisionQueueCount==0` 充足まで禁止。
  - `held` 論点は確定化せず `Conditional/Needs-decision` を維持。
- Approval record: `approved-for-freeze-candidate (Stream A docs scope, 2026-05-04)`。

### Phase 3: Plan（変更意図・非目標・検証）
- Change intent（this file）: baseline判定式をA1契約Issueの固定語彙へ同期し、決定論ルールの読替余地を排除。
- Non-goals: 実装誘導、allowlist外差分、承認待ち論点の確定化。
- Verification commands:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
  - `python3 -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `git diff --check`

### Phase 5: Verify
- AC/DoD self-check: pass（固定キー差分0、判定式SSOT維持、NoGo拡張条件明示）。
- Self-Correction count: `0/3`。

### Phase 6: Proceed/Stop
- Current state: `Conditional (Needs-decision)`。
- Blocking items: `Approval Record` 未充足、`HIL-RS-02-GOV-EXCEPTION-01` held。

## Stream A contract lock replay（2026-05-04 / P0 critical path fixation）

### Phase 1: Read同期
- 対象2ファイルを再読し、固定キー/判定式/停止条件の差分有無を確認。
- 結果: 差分 `0`（`freezeContractId`, `contractIds`, `schemaVersion`, `A2A3_OPEN_ALLOWED`, `NoGo`, `ProceedGate`）。

### Phase 2: ADR明文化（Context / Decision / Consequences）
- Context: baseline と A1 契約Issueの判定語彙不一致は P0ゲートの決定論を損なう。
- Decision:
  - `A2A3_OPEN_ALLOWED = (a1Status=="Done" && pendingDecisionQueueCount==0 && freezeContractId=="HIL-RS-02-A1-CONTRACT-FREEZE-v1" && schemaVersion=="1.0.0" && overridePolicy=="human_dual_control_only" && contractLinkLocked==true && sharedResourceFreeze==true && safeModeDefault=="ON" && safeModeBoundary=="SAFE_MODE_STRICT_ON")`
  - `NoGo = (!A2A3_OPEN_ALLOWED) || pendingBypassDetected || undefinedConflictDetected || contractNotFixedButA2A3ConfirmationRequested`
  - `ProceedGate = (A2A3_OPEN_ALLOWED && validatorPass==true)`
- Consequences: 未承認項目は `pending/held` のまま保持し、確定扱いを禁止。

### Phase 3: Plan
- AC/DoD不足なし。契約文面同期のみ実施。
- 非目標: allowlist外編集、実装変更、safeMode境界変更。

### Phase 4: Execute（契約文面のみ）
- 判定式/停止条件を A1 契約Issueと文字列一致で固定。
- tie-break `CTR-FB-P0-P2C-A1-TIEBREAK-v1` を決定論ルールとして維持。

### Phase 5: Verify（AC/DoD照合）
- 固定キー一致: pass。
- 判定式一意性: pass（`A2A3_OPEN_ALLOWED` SSOT）。
- Self-Correction count: `0/3`。

### Phase 6: Proceed判定
- 判定: `Conditional (Needs-decision)`。
- 継続保留: `Approval Record` 未充足、`HIL-RS-02-GOV-EXCEPTION-01` held。


## Stream B baseline addendum（2026-05-04 / interface baseline sync）

### Context
- Stream Aで固定した4型I/FをStream B planning baselineでも同一参照し、派生再定義を抑止する。

### Decision
- `ContextQueryV1` / `ContextBundleV1` / `ProposalPatchV1` / `AuditEventV1` を baseline の参照I/Fとして固定。
- mock-first は `A1-CONTRACT-MOCK-v1` を利用し、実装完了待ちを禁止。

### Consequences
- Plan段階で interface境界が確定し、A2/A3は read-only 契約参照で進行可能。
- 仕様変更要求は本baselineでは確定せず、CDC草案→承認待ちに限定。

## Stream A baseline sync run（2026-05-05 / serial protocol）

### Phase 1: Read
- 対象2ファイルを再読し、`Status / Priority / Scope / Dependencies / 固定キー` を比較。
- 差分結果: `0`（Hold条件非該当）。

### Phase 2: ADR/CDC Consensus
- Context: baseline側とA1契約Issue側の語彙差異はP0ゲートの決定論を崩す。
- Decision: `A2A3_OPEN_ALLOWED` / `NoGo` / `ProceedGate` を既存SSOT表現のまま固定する。
- Consequences: 未承認事項（`Approval Record`, `HIL-RS-02-GOV-EXCEPTION-01`）は `pending/held` 維持。

### Phase 3: Plan
- Target: allowlist 2ファイルの契約・ゲート記述整合。
- Non-target: allowlist外編集、実装誘導、safeMode境界変更。
- AC/DoD: 固定キー差分0、判定式一意、未承認確定化なし。

### Phase 4: Execute
- `freezeContractId` / `unlockRule` / `decisionQueueTransition` / gate条件を既存固定値で維持。
- 重複語彙の扱いはA1契約Issueの固定語彙優先を継続。

### Phase 5: Verify
- AC/DoD自己検証: pass。
- Self-Correction count: `0/3`。

### Phase 6: Proceed
- State: `Conditional (Needs-decision)`。
- Blockers: `Approval Record` 未充足、`HIL-RS-02-GOV-EXCEPTION-01=held`。


## Stream H Quick Sync (2026-05-05 / Phase 1-5 compressed)

### Phase 1 Read（issue現況同期）
- Status/Priority/Scope/Dependencies を再確認し、本ファイルの既存定義と矛盾がないことを確認。
- 未確定事項は `held` / `Pending` のまま維持し、確定化しない。

### Phase 2 Plan（優先順位・ブロッカー再定義）
- 優先順位を `contract-first` で固定し、実装進捗ではなく契約整合を先行。
- Blocker を次の正規化キーに限定: `approval_pending`, `decision_queue_pending`, `contract_mismatch`, `out_of_scope_request`。

### Phase 3 Execute（Issue本文の整理、依存明示）
- 依存を `A1 contract freeze -> A2 mock validation -> A3 implementation/sync` の順序で明示し、A2/A3の先行確定を禁止。
- `A2A3_OPEN_ALLOWED` / `ProceedGate` / `NoGo` は参照専用（再定義禁止）として本文整合を維持。

### Phase 4 Verify（ready/blocked判定整合）
- Ready は `contract-ready` と `execution-ready` の2層で評価。
- `approved_by/approved_at/evidence` 未入力、または `pendingDecisionQueueCount>0` の場合は `blocked` 扱い。
- self-correction は `<=3` を上限とし、`>=4` は停止。

### Phase 5 Proceed（次行動を1手に圧縮）
- **Next One Action**: `Approval Record（approved_by / approved_at / evidence）をA1正本へ入力し、pendingDecisionQueueCount を 0 に更新する。`

## Stream A phase gate audit（2026-05-05 / baseline contract sync）

### Phase 1: Read同期
- 対象2ファイルを再読し、`Status/Priority/Scope/Dependencies` と固定キー群を照合。
- 差分検知: `0`（語彙・判定式とも不一致なし）。

### Phase 2: ADR明文化（Context / Decision / Consequences）
- Context: baseline と A1契約Issue の判定語彙が乖離すると P0 契約ゲートが非決定化する。
- Decision: `A2A3_OPEN_ALLOWED` / `NoGo` / `ProceedGate` は SSOT を再利用し、再定義しない。
- Consequences: 未承認事項は `pending/held` で維持し、A2/A3確定化を禁止。

### Phase 3: Plan
- AC補強:
  1. 固定キー差分 `0`。
  2. `safeModeDefault=ON` / `safeModeBoundary=SAFE_MODE_STRICT_ON` 後退なし。
  3. `NoGo` に bypass/undefined conflict/未固定確定要求を維持。
- DoD補強: docs-check 3コマンド成功 + allowlist外差分 `0`。

### Phase 4: Execute
- 契約文面同期のみ実施（実装誘導・allowlist外編集・契約ID変更は不実施）。
- `A1 -> A2 -> A3` の依存順序と `Needs-decision` 運用を維持。

### Phase 5: Verify
- Result: AC/DoD自己検証 `pass`。
- Self-Correction count: `0/3`。

### Phase 6: Proceed
- 判定: `Conditional (Needs-decision)`。
- 停止理由: `Approval Record` 未充足、`HIL-RS-02-GOV-EXCEPTION-01=held`。

## Stream A strict-serial sync addendum（2026-05-05）

### Phase 1 Read（対象2ファイル再読）
- 再読対象を本ファイルと `issue-FB-P2C-01-a1-interface-contract.md` に固定し、語彙・判定式・held条件を照合。
- 差分結果: `A2A3_OPEN_ALLOWED` 判定式および固定キー群に差分なし。

### Phase 2 ADR明文化（Context / Decision / Consequences）
- Context: Stream A契約凍結を唯一SSOTとし、A2/A3の派生再定義を禁止する。
- Decision: 固定キー（`freezeContractId`, `schemaVersion`, `overridePolicy`, `safeModeBoundary`, `safeModeDefault`, `contractLinkLocked`, `sharedResourceFreeze`, `decisionQueueTransition`）と `A2A3_OPEN_ALLOWED` を据え置く。
- Consequences: `Approval Record` 未承認および `held` 論点が残る限り、状態は `Conditional/Needs-decision` を維持。
- Human approval status: `pending`（未承認事項は凍結候補として扱う）。

### Phase 3 Plan（AC/DoD）
- AC:
  1. 2ファイルで固定キー差分0。
  2. `A1 -> A2 -> A3` 依存順序を維持。
  3. A2/A3依存は read-only参照 + mock-first。
- DoD:
  1. 未承認論点を確定化しない。
  2. 未定義キー fail-closed を維持。
  3. allowlist外編集0。

### Phase 4 Execute（閉集合契約 + fail-closed）
- 閉集合契約キーをA1 issue記載と同一に固定し、それ以外は受理しない。
- `NoGo判定 = (!A2A3_OPEN_ALLOWED) || pendingBypassDetected || undefinedConflictDetected` を維持。

### Phase 5 Verify
- AC/DoD自己検証: 充足。
- self-correction: `0/3`（追加修復なし）。

### Phase 6 Proceed
- 判定: `Needs-decision`。
- 停止条件: 未承認確定化要求 / 未定義競合 / allowlist外編集要求 / self-correction 4回目相当。

## Stream A contract canonicalization update（2026-05-06）

### Phase 1: Read & Drift Check
- 対象再読: 本ファイルと `issue-FB-P0-2A2B2C-stream-c-planning-baseline.md` / `issue-FB-P2C-01-a1-interface-contract.md`。
- Drift check（Status/Priority/Scope/Dependencies/Related ADR）:
  - `Status=Open` / `Priority=P0` を再確認。
  - Scope は allowlist 2ファイル限定（編集境界固定）。
  - Dependencies は `A1 -> A2 -> A3` を維持し、A2/A3は mock-first read-only。
  - Related ADR は `ADR-0001`, `ADR-0019`, `ADR-0026`, `ADR-0027`, `ADR-0028` を正本語彙として採用。
- 判定: 差分は用語揺れ（`Needs-decision` / `Conditional` の併記）に限定。契約値ドリフトなし。

### Phase 2: Plan（AC/DoD）
- AC
  1. `A2A3_OPEN_ALLOWED` を唯一の開放判定式として維持する。
  2. 固定キー集合（`freezeContractId`, `contractIds`, `schemaVersion`, `overridePolicy`, `contractLinkLocked`, `sharedResourceFreeze`, `safeModeDefault`, `safeModeBoundary`, `decisionQueueTransition`）を閉集合で保持する。
  3. 未承認事項は `held` として保持し、確定扱いしない。
- DoD
  1. 2ファイルで Related ADR を同一集合に正規化。
  2. 依存注記を `A1 -> A2 -> A3（A2/A3はread-only mock-first）` に統一。
  3. allowlist外ファイルの差分を発生させない。

### Phase 3: Execute
- 固定語彙を以下に正規化:
  - 判定状態の正本を `Needs-decision`（`Conditional` は Proceed内の中間判定）として扱う。
  - Related ADR は `ADR-0001/0019/0026/0027/0028` の5件固定。
- 依存注記を更新:
  - `A1 -> A2 -> A3` 順序を維持し、A2/A3の契約再定義禁止・mock-first参照限定を明記。

### Phase 4: Verify
- AC/DoD自己検証: 充足。
- Self-Correction count: `0/3`。

### Phase 5: Proceed Gate
- 判定: **次フェーズへ進行可（Conditional / Needs-decision）**。
- 理由: 契約固定値と判定式は整合済み。未承認事項（`Approval Record`, `HIL-RS-02-GOV-EXCEPTION-01`）は `held` のまま維持され、確定化していない。

## Stream A contract freeze sync（2026-05-06 / P0-P1 minimum interface agreement）

### Phase 1: Read同期
- 対象6ファイルを再読し、固定キー（`freezeContractId`, `contractIds`, `schemaVersion`, `overridePolicy`, `contractLinkLocked`, `sharedResourceFreeze`, `safeModeDefault`, `safeModeBoundary`, `decisionQueueTransition`）の差分を確認。
- 差分結果: `0`（不一致なし）。

### Phase 2: ADR明文化（C/D/C）
- Context: A1契約固定が崩れると `A1 -> A2 -> A3` の依存順が崩壊する。
- Decision: 契約は `HIL-RS-02-A1-CONTRACT-FREEZE-v1` / `schemaVersion=1.0.0` を維持し、`A2A3_OPEN_ALLOWED` を唯一判定式として継続。
- Consequences: `Approval Record=Pending` と `HIL-RS-02-GOV-EXCEPTION-01=held` が残る間は `Needs-decision` を維持し、確定扱いを禁止する。

### Phase 3-6: Freeze / Verify / Proceed
- Freeze: A2/A3は read-only 参照のみ。
- Verify: AC/DoD自己検証で fixed keys drift=0、SafeMode後退なしを確認。
- Proceed: `Conditional/Needs-decision`（人間承認待ち）。


## Stream A execution log（2026-05-06 / Critical Path）

### Phase 1: Read Sync
- 対象4ファイルを再読し、`Status/Priority/Dependencies/固定キー` を突合した。
- 矛盾一覧（検知結果）:
  1. `Approval Record` が全ファイルで `Pending`（承認ログ未充足）。
  2. `HIL-RS-02-GOV-EXCEPTION-01` が `held` 維持（未承認）。
  3. `pendingDecisionQueueCount==0` の監査証跡が未添付（解放条件未達）。
- 固定キー（`freezeContractId/schemaVersion/overridePolicy/safeModeDefault/safeModeBoundary/decisionQueueTransition`）は差分0。

### Phase 2: ADR明文化（C/D/C）
- Context: A1契約凍結がP0契約ゲートであり、ここが揺れるとA2/A3 mock参照が停止する。
- Decision: 固定キーを再定義せず参照専用で維持し、未承認論点は `Pending/held` のまま固定する。
- Consequences: `A2A3_OPEN_ALLOWED` の算出は継続可能だが、Proceedは `Hold/Needs-decision` を維持する。

### Phase 3: Plan（AC/DoD固定）
- AC:
  1. `A1->A2/A3` 解放条件を単一式で固定する。
  2. `pendingDecisionQueueCount>0` または未承認が1件でも `Go` を禁止する。
  3. Stopper（allowlist外編集要求/未定義競合/self-correction 4回目相当）を明記する。
- DoD:
  1. 固定語彙ドリフト0。
  2. pendingDecisionQueue条件が全対象文書で同値。
  3. NoGo return pathがA1契約Issueへ一意。

### Phase 4-6: Execute / Verify / Proceed
- Execute: 契約語彙と依存式を維持（再定義なし）。
- Verify: AC/DoD照合、用語ゆらぎ、状態遷移矛盾を確認し、破綻なし。
- Proceed: **Hold**（`Approval Record=Pending` かつ `held` 残存のため）。
