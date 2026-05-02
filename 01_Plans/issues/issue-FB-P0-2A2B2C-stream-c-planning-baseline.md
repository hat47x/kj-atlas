# Issue Draft: FB-P0 baseline / Stream B critical-path planning baseline（legacy filename: stream-c）

- Type: Process
- Status: Open
- Priority: P0
- Owner: Stream H（FB Open/P0 planning convergence）
- Scope: allowlist 2ファイル（本ファイル / `issue-FB-P2C-01-a1-interface-contract.md`）の計画・契約整合のみ
- Dependencies: `A1 -> A2 -> A3`, `freezeContractId` SSOT, `unlockRule` SSOT
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
- Dependencies: `A1 -> A2 -> A3`、`sharedResourceFreeze=true`、`safeModeDefault=ON`
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
