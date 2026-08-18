# Issue Draft: FB-P0 baseline / Stream B critical-path planning baseline（legacy filename: stream-c）

- Type: Process
- Status: Done
- Priority: P0
- Owner: Stream H（FB Open/P0 planning convergence）
- Scope: allowlist 2ファイル（本ファイル / `issue-FB-P2C-01-a1-interface-contract.md`）の計画・契約整合のみ

## Done 2026-06-20
A2A3_OPEN_ALLOWED satisfied: HIL-RS-01-A1 Done + HIL-RS-02-A1 Done + pendingDecisionQueueCount=0 (ADR-0039).
FB-P2C-01-a1 Done. All freeze key conditions verified. P0 planning baseline converged.
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

## Stream C standalone planning baseline（2026-05-07）

### Phase 1: Read同期
- 対象は allowlist 2ファイル（本ファイル / `issue-FB-P2C-01-a1-interface-contract.md`）のみ。
- 再読確認項目（差分が1つでもあれば停止して `held` 記録）:
  1. `Status=Open`, `Priority=P0`, `Scope=allowlist 2ファイル限定`
  2. 依存表記 `A1 -> A2 -> A3`（A2/A3はmock-first準備のみ）
  3. 固定キー `freezeContractId`, `contractIds`, `schemaVersion`, `overridePolicy`, `contractLinkLocked`, `sharedResourceFreeze`, `safeModeDefault`, `safeModeBoundary`, `decisionQueueTransition`

### Phase 2: P0基準線（Context / Decision / Consequences）
#### Context
- FB-P0基準線の目的は、A1契約凍結を唯一SSOTとしてA2/A3の誤開放を防止し、安全境界（`safeModeDefault=ON`, `SAFE_MODE_STRICT_ON`）を後退させないこと。

#### Decision
- 固定値（freeze）:
  - `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
  - `contractIds=A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|A1-ERROR-IF`
  - `schemaVersion=1.0.0`
  - `overridePolicy=human_dual_control_only`
  - `contractLinkLocked=true`
  - `sharedResourceFreeze=true`
  - `safeModeDefault=ON`
  - `safeModeBoundary=SAFE_MODE_STRICT_ON`
  - `decisionQueueTransition=Pending -> Approved | Pending -> Rejected`
- 判定式（唯一SSOT）:
  - `A2A3_OPEN_ALLOWED = (a1Status=="Done" && pendingDecisionQueueCount==0 && freezeContractId=="HIL-RS-02-A1-CONTRACT-FREEZE-v1" && schemaVersion=="1.0.0" && overridePolicy=="human_dual_control_only" && contractLinkLocked==true && sharedResourceFreeze==true && safeModeDefault=="ON" && safeModeBoundary=="SAFE_MODE_STRICT_ON")`
- 保留事項:
  - `Approval Record=Pending` は `held` 維持
  - `HIL-RS-02-GOV-EXCEPTION-01` は `held` 維持

#### Consequences
- `A2A3_OPEN_ALLOWED=false` の間はA2/A3を確定扱いしない。
- 未承認事項は `held` のまま保持し、承認証跡（`approved_by`, `approved_at`, `evidence`）が揃うまでGo判定しない。
- `safeModeDefault=ON` / `SAFE_MODE_STRICT_ON` を変更する要求は `No-Go` として即停止。

### Phase 3: 非依存完結の計画粒度へ再編
- 本Issue単体で完結する作業単位（他ストリームの進捗を前提にしない）:
  1. **Contract sync**: allowlist 2ファイル間で固定キーと判定式の文字列一致を維持。
  2. **Gate sync**: `ProceedGate / Conditional / NoGo / Needs-decision` の語彙と条件を一致。
  3. **Safety lock**: safeMode固定値とNo-Go条件（未承認確定化、allowlist外編集要求、未定義競合）を明示。
  4. **Evidence pending管理**: `Approval Record=Pending` と `held` を確定化せず維持。
- 非依存化ルール:
  - 他ストリームの実装完了を待たず、本Issueは「契約文面の整合性検証」で完了判定可能。
  - allowlist外のファイル更新・追加依頼は即 `No-Go` 停止。

### Phase 4: Verify（最大3回）
- Verifyは以下を順に実施し、失敗時はSelf-Correctionを最大3回まで許可。
  1. `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
  2. `python3 -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  3. `git diff --check`
- Self-Correction count が `4回目相当` に到達した時点でフェイルセーフ停止。

## Stream D 実行計画ベースライン（FB-P0-2A2B2C Planning Baseline / 2026-05-09）

### Phase 1: Read
- 各Phase開始時に allowlist 2ファイル（本ファイル / `issue-FB-P2C-01-a1-interface-contract.md`）を再読する。
- 差分確認の必須観点:
  1. `A1 -> A2 -> A3` の依存順が維持されていること
  2. Ready/Blocked 判定語彙が両ファイルで一致していること
  3. `safeModeDefault=ON` / `safeModeBoundary=SAFE_MODE_STRICT_ON` が維持されていること
- 差分発見時は `held` 記録のみ許可し、以降のPhaseへ進行しない。

### Phase 2: ADR（Context / Decision / Consequences）
#### Context
- A1契約凍結を唯一SSOTとして、A2/A3は誤って確定しないように統治する必要がある。
- 依存関係を **実装依存** と **I/F依存** に分離し、並列化可能区間を明示する必要がある。

#### Decision
- 依存関係の分離定義（固定）:
  - 実装依存: `A1 implementation -> A2 implementation -> A3 implementation`（直列）
  - I/F依存: `A1 interface-contract -> A2 mock-validation`, `A1 interface-contract -> A3 mock-validation`（mock-firstで並列準備可）
- Ready/Blocked 判定:
  - `Ready(A2/A3) = (A1 interface-contract Approved) && (pendingDecisionQueueCount==0)`
  - `Blocked(A2/A3) = !Ready(A2/A3) || undefinedConflictDetected`
- mock活用条件（I/F依存のみで許可）:
  1. upstreamが契約（I/F）未実装でも、契約ID・schemaVersionが一致していること
  2. mock artifactに `A1-CONTRACT-MOCK-v1` を使用すること
  3. mock結果は `implementation done` と同義扱いしないこと

#### Consequences
- I/F依存箇所は mock-first で並列準備可能、実装依存箇所は A1→A2→A3 の直列を維持する。
- 依存自己矛盾（例: A2をReadyとしつつA1未承認）は `No-Go` として停止する。

### Phase 3: Plan（AC/DoD）
- AC
  1. 依存関係が「実装依存 / I/F依存」に分離記述されている。
  2. I/F依存の全箇所に mock-first 条件が付記されている。
  3. Ready/Blocked 判定がA1→A2→A3依存順と矛盾しない。
  4. allowlist外ファイル差分が0である。
- DoD
  1. docs-checkで依存順・優先度・競合回避の整合が確認できる。
  2. diff健全性（`git diff --check`）がpassする。
  3. self-correctionは最大3回以内で収束する。

### Phase 4: Execute
- 本ファイル内でのみ、依存関係・判定式・mock条件の記述を統一する。
- 実装仕様の確定、他issueの改変、allowlist外編集を実施しない。
- AC/DoD不足を検知した場合はドラフト提案として追記し、合意前は確定扱いしない。

### Phase 5: Verify
- 最低実施:
  1. docs-check（依存順、優先度、競合回避の整合）
  2. diff健全性（`git diff --check`）
  3. self-correction 最大3回
- 実行コマンド:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
  - `python3 -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `git diff --check`

### Phase 6: Proceed or Stop
- Proceed条件:
  - AC/DoD充足
  - 未承認事項が `held` として明示維持され、確定扱いされていない
  - 依存関係の自己矛盾がない
- Stop条件（ストッパー）:
  1. 未定義競合
  2. 依存関係の自己矛盾
  3. scope逸脱（allowlist外編集要求/実施）
  4. self-correction 3回超過の修復失敗

### Phase 5: 停止条件（即停止・報告）
- 即停止トリガー:
  1. allowlist外編集要求
  2. 未定義競合（`undefinedConflictDetected=true`）
  3. 未承認事項の確定化要求（`Approval Record=Pending` / `held` をDone扱い）
  4. self-correction 4回目相当
  5. safeMode後退要求（`ON -> OFF` または `SAFE_MODE_STRICT_ON -> relaxed`）
- 停止時の報告フォーマット（固定）:
  - `原因` / `影響I/F` / `要判断点` / `再開条件`


### Phase 6: Proceed（終了判定）
- 判定は `Proceed / Hold / Stop` の3値で明記し、推測確定を禁止する。
- `Proceed`: `A2A3_OPEN_ALLOWED=true` かつ `validatorPass=true` かつ `Approval Record=Approved`。
- `Hold`: 未承認事項が `held` のみに限定され、固定キー差分が `0` の場合。
- `Stop`: フェイルセーフ条件（allowlist外編集要求 / 前提崩壊 / self-correction 4回目相当 / 未定義競合）を満たした場合。
- 次アクションは本Issue内で完結する内容（文面同期・held更新・判定式照合）に限定する。

### Delta log分類ルール（Phase 1運用固定）
- `語彙差分`: Go/No-Go/Conditional/Needs-decision など判定語彙の不一致。
- `依存差分`: `A1 -> A2 -> A3` の順序・依存記法の不一致。
- `契約キー差分`: `freezeContractId` / `contractIds` / `schemaVersion` / `safeModeDefault` など固定キーの不一致。
- 差分を検知した場合は `held` に分類ラベル付きで記録し、Phase 2以降へ進行しない。

## Stream A alignment run（2026-05-08 / baseline sync for A1 freeze）

### Phase 1: Read同期
- allowlist 2ファイル（本ファイル / `issue-FB-P2C-01-a1-interface-contract.md`）を再読。
- 固定キー（`freezeContractId`, `contractIds`, `schemaVersion`, `overridePolicy`, `contractLinkLocked`, `sharedResourceFreeze`, `safeModeDefault`, `safeModeBoundary`, `decisionQueueTransition`）の一致を確認。
- 判定: 差分 `0`、未定義競合なし。

### Phase 2: ADR明文化（Context / Decision / Consequences）
- Context: A1契約凍結を唯一ゲートとして `A1 -> A2 -> A3` 順序を維持する。
- Decision:
  - `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
  - `schemaVersion=1.0.0`
  - `safeModeDefault=ON`
  - `safeModeBoundary=SAFE_MODE_STRICT_ON`
  - `contractLinkLocked=true`
  - `sharedResourceFreeze=true`
  - `A2A3_OPEN_ALLOWED` を唯一判定式として維持
- Consequences:
  - A2/A3 は read-only / mock-first 参照のみ。
  - A2/A3で契約再定義は禁止。
  - 未承認項目は `held` 維持で確定化しない。
- Approval state: `approved-for-freeze-candidate`（docs scope）

### Phase 3: Plan
- 変更対象: baseline/A1 issue の契約固定・停止条件同期セクション。
- 非対象: allowlist外ファイル、実装詳細、他ストリーム実作業。
- 停止条件: 固定キー不一致 / 未定義競合 / allowlist外編集要求 / self-correction 4回目相当。

### Phase 4: Execute
- 契約固定値は変更せず、同期文面のみ更新。
- 安全境界（`safeModeDefault=ON`, `SAFE_MODE_STRICT_ON`）後退なし。

### Phase 5: Verify
- Plan適合: 適合。
- allowlist逸脱: なし。
- 契約固定値整合: A1 issue と一致。
- Self-Correction count: `0/3`。

### Phase 6: Proceed/Stop
- Decision state: `Hold (Needs-decision)`。
- 根拠: `Approval Record=Pending` と `HIL-RS-02-GOV-EXCEPTION-01=held` が未解消。
- 必要承認項目: `approved_by`, `approved_at`, `evidence`, `HIL-RS-02-GOV-EXCEPTION-01 final decision`。


## Stream A A1 contract-only sync run（2026-05-09）

### Phase 1 Read
- allowlist 2ファイルを再読し、`A2A3_OPEN_ALLOWED` と固定キー群（`freezeContractId`, `schemaVersion`, `safeModeDefault`, `safeModeBoundary`, `decisionQueueTransition`）の差分を確認。
- 結果: 差分 `0`。

### Phase 2 ADR/CDC
- Context: baselineはA1凍結契約の運用基準線であり、判定式ドリフトを許容しない。
- Decision: 既存の固定値・判定式・No-Go条件を据え置く（再定義しない）。
- Consequences: 未承認事項は `held` 維持、A2/A3の確定化は禁止。
- Approval log: `stream-a-baseline-consensus-2026-05-09=approved`（docs scope）。

### Phase 3 Plan / Phase 4 Execute
- Plan: 本ファイルへ同期監査記録を追記し、A1契約Issueと整合を固定。
- Execute: allowlist内のみ更新。契約ID・SafeMode境界・遷移式の値変更は未実施。

### Phase 5 Verify / Phase 6 Proceed
- Verify: AC/DoD自己照合 + docs-check前提を満たすことを確認。
- Proceed: `Conditional (Needs-decision)` 維持（`Approval Record=Pending`, `HIL-RS-02-GOV-EXCEPTION-01=held`）。

## Stream E planning-baseline convergence（2026-05-09）

### Phase 1: 現状Read & ギャップ抽出
- 対象: allowlist 2ファイル（本ファイル / `issue-FB-P2C-01-a1-interface-contract.md`）のみ。
- Read結果（固定値の再確認）:
  - `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
  - `schemaVersion=1.0.0`
  - `overridePolicy=human_dual_control_only`
  - `safeModeDefault=ON`
  - `safeModeBoundary=SAFE_MODE_STRICT_ON`
  - `A2A3_OPEN_ALLOWED` は A1完了 + pendingDecisionQueue=0 + 固定キー一致を必須。
- ギャップ（収束阻害要因）:
  1. `Approval Record=Pending` が継続し、Go判定に必要な承認証跡（`approved_by/approved_at/evidence`）が欠落。
  2. `HIL-RS-02-GOV-EXCEPTION-01` が `held` のまま未解消。
  3. Stream表記（B/C/F/H）が混在しており、実行主体の識別ノイズが残る。

### Phase 2: 優先順位・依存・モック可否
- 優先順位（P0固定）:
  1. **Safety/Contract lock維持**: safeMode固定値とA2/A3誤開放防止を最優先。
  2. **Approval evidence整備**: Go判定に必要な承認証跡の充足。
  3. **表記正規化**: stream混在表記の整理（意味を変えず語彙を揃える）。
- 依存関係（固定）:
  - `A1 -> A2 -> A3`（A2/A3は `A2A3_OPEN_ALLOWED=true` になるまで確定禁止）。
  - NoGo return path は `issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md` 固定。
- モック可否:
  - **可**: 契約整合検証（固定キー一致/判定式文字列一致/No-Go条件存在確認）は mock-first で実施可。
  - **不可**: `Approval Record` の最終承認（人間承認）と `held` 解消判断はモック代替不可。

### Phase 3: 実行可能タスク列（直列）
1. **Plan**: allowlist 2ファイルを再読し、固定キーと判定式の差分有無をチェック（差分ありは即 `held`）。
2. **Execute-1**: 本Issue内の運用表記を Stream E 観点で補足し、既存判定式・固定値は不変で維持。
3. **Execute-2**: `Approval Record=Pending` / `held` 継続時の扱い（Go不可・Conditional/Needs-decision維持）を明文化。
4. **Verify**: `validate_active_issue_memos.py` → `unittest` → `git diff --check` を順に実行。
5. **Proceed判定**:
   - Go: `A2A3_OPEN_ALLOWED=true` かつ `Approval Record=Approved` かつ `validatorPass=true`
   - Conditional/Needs-decision: `held` のみ未承認が残る場合
   - No-Go: 未定義競合 / allowlist外編集要求 / self-correction 3回超過
- 実行制約: Plan→Execute→Verify→Proceed を厳守し、Self-Correction は最大3回。4回目相当で停止。


## Stream A dedicated run（2026-05-09 / critical-path contract freeze）

### Phase 1: Read & Baseline Sync（Plan→Execute→Verify→Proceed）
- Read実施: allowlist 2ファイルを再読し、`Status/Priority/Dependencies` と固定契約キーを照合。
- 固定キー一致確認:
  - `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
  - `schemaVersion=1.0.0`
  - `safeModeDefault=ON`
  - `sharedResourceFreeze=true`
- Drift判定: 差分なし（`held`追加なし）。Proceed。

### Phase 2: ADR明文化（Context / Decision / Consequences）
- Context: A1契約未固定のままA2/A3へ進むと再定義リスクが発生する。
- Decision: 凍結候補を以下に固定（承認完了までは read-only）。
  - ID: `HIL-RS-02-A1-CONTRACT-FREEZE-v1`
  - `schemaVersion=1.0.0`
  - `overridePolicy=human_dual_control_only`
  - SafeMode境界: `safeModeDefault=ON`, `safeModeBoundary=SAFE_MODE_STRICT_ON`
  - `sharedResourceFreeze=true`
- Consequences: 承認前は破壊的変更禁止、未承認事項は `Needs-decision/Hold` 維持。
- Approval log: `approved-for-freeze-candidate`（human approval pending）。

### Phase 3: Contract Freeze Definition
- SSOT判定式（唯一）:
  - `A2A3_OPEN_ALLOWED = (a1Status=="Done" && pendingDecisionQueueCount==0 && freezeContractId=="HIL-RS-02-A1-CONTRACT-FREEZE-v1" && schemaVersion=="1.0.0" && overridePolicy=="human_dual_control_only" && contractLinkLocked==true && sharedResourceFreeze==true && safeModeDefault=="ON" && safeModeBoundary=="SAFE_MODE_STRICT_ON")`
- NoGo条件（固定）:
  - `pendingBypassDetected==true`
  - `undefinedConflictDetected==true`
- non-target編集: `0`（allowlist外編集なし）。

### Phase 4: Verify
- docs-check観点: 構文・契約整合・判定式単一性・禁止事項（SafeMode後退/allowlist外編集）を確認。
- Self-Correction count: `0/3`。失敗なし。

### Phase 5: Proceed / Handoff
- 判定: `Hold/Needs-decision`（`Approval Record: Pending`, `HIL-RS-02-GOV-EXCEPTION-01: held`）。
- 次ストリーム向け: read-only参照のみ（契約再定義・確定化禁止）。

## Stream A critical-path alignment checkpoint（2026-05-09）

### Phase 1 Read
- 対象2ファイル（本ファイル / `issue-FB-P2C-01-a1-interface-contract.md`）を再読し、`Status / Scope / Dependencies / freeze keys` 差分 `0` を確認。

### Phase 2 ADR（Context / Decision / Consequences）
- Context: P0基準線はA1契約凍結を唯一ゲートとしてA2/A3誤開放を防止する。
- Decision: 固定値と `A2A3_OPEN_ALLOWED` 判定式を変更せず維持し、pending/held は確定化しない。
- Consequences: 未承認が残る間は `Needs-decision` を維持し、Goに遷移しない。

### Phase 3 Plan
- 対象: allowlist 2ファイルの契約・ゲート文言同期のみ。
- 非対象: allowlist外ファイル、実装コード、派生契約追加。
- 停止条件: allowlist外編集要求 / 未定義競合 / self-correction 4回目相当。

### Phase 4 Execute
- 契約固定値整備のみを実施し、A2/A3は `A1-CONTRACT-MOCK-v1` 前提で依存切断可能であることを維持。

### Phase 5 Verify
- AC/DoD自己検証で固定キー一致、判定式一致、安全境界維持を確認。
- self-correction: `0/3`。

### Phase 6 Proceed
- 判定: `Needs-decision`（`Approval Record=Pending` と `held` 未解消のため）。


## Stream B dedicated baseline alignment update（2026-05-09）

### Mission（FB-P0 baseline契約整合）
- 目的: `A1/A2/A3 freeze値・gate文言・held条件` を allowlist 2ファイル間で統一し、A1契約凍結を唯一SSOTとして維持する。
- 対象: 本ファイルと `issue-FB-P2C-01-a1-interface-contract.md` のみ（指定外ファイル編集は禁止）。

### Phase 1: Read
- `A1/A2/A3` の固定値、`A2A3_OPEN_ALLOWED`、`ProceedGate/Conditional/No-Go/Needs-decision`、`held` 条件を再読比較する。
- 差分または競合兆候（語彙不一致・判定式不一致・未定義条件）を検知した場合は **ProceedせずStop**。

### Phase 2: Baseline freeze
- freeze値は次を固定し再定義しない: `freezeContractId`, `contractIds`, `schemaVersion`, `overridePolicy`, `contractLinkLocked`, `sharedResourceFreeze`, `safeModeDefault`, `safeModeBoundary`。
- gate文言は `A2A3_OPEN_ALLOWED` / `NoGo` / `ProceedGate` の既存SSOTをそのまま適用する。
- `Approval Record=Pending` と `HIL-RS-02-GOV-EXCEPTION-01` は `held` 維持（確定扱い禁止）。

### Phase 3: Dependency handling（read-only）
- A2/A3依存は **mock前提のread-only参照** とし、A2/A3側の状態を本Issueで確定しない。
- 依存関係表記は `A1 -> A2 -> A3` を維持し、A1 Done + pending queue 0 までA2/A3開放しない。

### Phase 4: Execute
- allowlist 2ファイルの契約文言同期のみ実施する。
- allowlist外編集要求を受けた時点で **Stop（No-Go）**。

### Phase 5: Verify
- docs-check（validator / unittest / diff check）を実行し、self-correctionは最大3回。
- 4回目相当、または競合兆候再発時は **Stop（人間判断へエスカレーション）**。

### Phase 6: Proceed rule
- Go: `ProceedGate=true` かつ承認証跡が充足。
- Conditional: `ProceedGate=false` かつ未承認事項が `held` のみ。
- No-Go/Stop: 競合兆候、未承認確定化、allowlist外編集要求、契約未固定でA2/A3確定要求。

## Stream B dedicated contract update（2026-05-10）

### Phase 1 Read（allowlist / dependencies / mocked parallel prerequisites）
- allowlistは本Issueと `issue-FB-P2C-01-a1-interface-contract.md` の2ファイルのみ。
- 依存は `A1 -> A2 -> A3` を固定し、A2/A3は **mock準備のみ並行可**（確定実装は禁止）。
- 前提条件:
  1. `freezeContractId` と `schemaVersion` が2ファイルで一致。
  2. `safeModeDefault=ON` と `safeModeBoundary=SAFE_MODE_STRICT_ON` が維持。
  3. `Approval Record` 未承認項目は `held` のまま保持。

### Phase 2 ADR（Context / Decision / Consequences）
#### Context
- Stream Bの責務は、baseline契約文面の整合を維持し、A1契約凍結を唯一SSOTとしてA2/A3誤開放を防ぐこと。

#### Decision
- 固定値は既存freeze定義（`HIL-RS-02-A1-CONTRACT-FREEZE-v1` / `schemaVersion=1.0.0` / `overridePolicy=human_dual_control_only`）を再利用し、再定義しない。
- 開放判定は `A2A3_OPEN_ALLOWED` を唯一判定式として継続。
- `Approval Record=Pending` と `HIL-RS-02-GOV-EXCEPTION-01` は `held` 維持。

#### Consequences
- A1未完了または承認証跡不足時はA2/A3を確定扱いしない。
- safeMode固定値の後退要求は `No-Go` で即停止。

### Phase 3 Plan（A1->A2->A3 gate contract only）
- Gate定義（実装禁止、契約のみ）:
  1. **Gate A1**: `a1Status=="Done"` かつ `pendingDecisionQueueCount==0`。
  2. **Gate A2**: `A2A3_OPEN_ALLOWED==true` を満たす場合のみ着手可能（mock validation範囲）。
  3. **Gate A3**: A2完了と同一契約ID一致を条件に計画可能（実装確定は禁止）。
- いずれのGateも allowlist外編集要求・未定義競合検知時は `No-Go`。

### Phase 4 Execute（baseline契約文面のみ更新）
- 実施内容は契約文面の同期と整合確認に限定。
- 新規実装・新規依存・allowlist外ファイル編集は行わない。

### Phase 5 Verify（gate矛盾 / 依存循環 / safeMode後退なし）
- 検証観点:
  1. Gate矛盾なし（`A1 -> A2 -> A3` の一方向のみ）。
  2. 依存循環なし（逆参照・自己循環なし）。
  3. `safeModeDefault=ON` / `SAFE_MODE_STRICT_ON` の後退なし。
  4. `held` 未承認事項の確定化なし。

### Phase 6 Proceed（Proceed / Hold / Stop）
- **Proceed**: `A2A3_OPEN_ALLOWED=true` かつ `validatorPass=true` かつ `Approval Record=Approved`。
- **Hold**: 契約矛盾なしだが `Approval Record=Pending` または `held` 残存。
- **Stop**: Gate矛盾、依存循環、safeMode後退、allowlist外編集要求、未承認確定化のいずれかを検知。

## Stream F planning baseline convergence run（2026-05-17）

### Phase 1: Read（allowlist 2ファイル再読）
- 対象は allowlist 2ファイル（本ファイル / `issue-FB-P2C-01-a1-interface-contract.md`）に限定する。
- 再読チェック（差分1件でも `Stop`）:
  1. 固定キー `freezeContractId / contractIds / schemaVersion / overridePolicy / contractLinkLocked / sharedResourceFreeze / safeModeDefault / safeModeBoundary` が一致。
  2. 判定式 `A2A3_OPEN_ALLOWED` が文字列一致。
  3. 未承認事項（`Approval Record=Pending`, `HIL-RS-02-GOV-EXCEPTION-01=held`）が確定化されていない。

### Phase 2: ADR/Decision整理（Ready化条件とDoD固定）
#### Context
- FB-P0-2A2B2C の収束条件は「A1契約凍結を唯一SSOTに保ったまま、A2/A3誤開放を防止すること」。
- 収束遅延の主因は、依存関係（実装依存 / 計画依存 / I/F依存）が混在し、Ready条件が曖昧になる点。

#### Decision
- Ready判定を次で固定する（stream間で再定義しない）:
  - `Ready(A2/A3-planning) = contractFreezeAligned && gateFormulaAligned && approvalState in {Pending, Approved}`
  - `Ready(A2/A3-execution) = A2A3_OPEN_ALLOWED && Approval Record=Approved`
- DoD（planning baseline）の最小集合を固定:
  1. allowlist 2ファイルで固定キー差分 `0`
  2. `A2A3_OPEN_ALLOWED` と `NoGo` 条件が文字列一致
  3. 未承認事項は `held/pending` のまま維持（Done遷移禁止）
  4. allowlist外差分 `0`

#### Consequences
- A2/A3は **planning準備Ready** と **execution Ready** を分離して扱う。
- mock-first は planning準備にのみ適用し、実装完了の代替には使わない。
- `Approval Record=Pending` が残る限り判定は `Conditional/Needs-decision` を維持する。

### Phase 3: Plan（依存分離の明示）
- 依存を3層で分離して記述固定:
  1. **Implementation dependency（直列）**: `A1 impl -> A2 impl -> A3 impl`
  2. **Interface dependency（並列準備可）**: `A1 interface-contract -> A2/A3 mock-validation`
  3. **Planning dependency（本Issue完結）**: baselineとP2C A1の文面同期が完了すればClose候補
- 非目標（明示）:
  - 実装コード変更
  - allowlist外Issue編集
  - 承認状態の擬似確定

### Phase 4: Execute（docs-only統合作業）
- 本Issueでは planning baseline のメタ（Ready化条件 / DoD / 依存分離）整備のみを実施。
- 契約固定値およびSafeMode境界（`safeModeDefault=ON`, `safeModeBoundary=SAFE_MODE_STRICT_ON`）は変更しない。
- `No-Go` 追加固定: 「契約未固定のままA2/A3をDone扱いする要求」を検知した場合は即停止。

### Phase 5: Verify（収束判定）
- 検証順序（固定）:
  1. `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
  2. `python3 -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  3. `git diff --check`
- 判定ルール:
  - Self-Correction は最大3回。
  - 4回目相当 / allowlist外編集要求 / 未定義競合 / safeMode後退要求は `Stop`。

### Phase 6: Proceed/Stop
- `Proceed`: planning DoD 4項目がすべて充足し、未承認事項が `held/pending` として明示維持されている。
- `Conditional (Needs-decision)`: DoDは充足したが `Approval Record=Pending` または `held` 未解消が残る。
- `Stop`: 依存矛盾、allowlist逸脱、未承認確定化、self-correction超過のいずれかを検知。

## Stream H critical-path recomputation note (2026-05-20)

### Reclassification (Priority / Blocker / Dependency stage)
| 項目 | Priority | 区分 | 依存ステージ |
|---|---|---|---|
| A1固定キー整合（2ファイル） | P0 | Gate prerequisite | A1 |
| A2/A3 mock準備 | P1 | Bypass-capable dependency | A2/A3 pre-start |
| Program Gate最終判定証跡 | P0 | True blocker | MVP Exit |
| Decision Queue未解決2件 | P1 | Conditional blocker | Pre-Go |

### Mock bypass vs true blocker
- Mock bypass可能: A2/A3の事前検証（契約固定とsafeMode境界を前提）。
- True blocker: Go/No-Goを確定するための承認記録不足（判定ログ未記録）。

### Next iteration order (proposal)
1. Gate証跡更新（`PRODUCT-QA-01`, `ENV-CONFIG-DRIFT-01`）
2. Decision Queue Open 2件の期限・責任者更新
3. Program Gate再判定（Go/Conditional/No-Go）
4. A2/A3着手順の最終確定


## Stream H integration lock update（2026-05-20）

### 1) Read集約（Ready出口条件の再収集）
- baseline側で扱う出口条件を `A1 contract freeze consistency` のみに限定する。
- A2/A3の状態は参照のみとし、baseline本文では Open化判定を新規定義しない。

### 2) release readiness接続I/F（統合判定フレームへの受け渡し）
- 本Issueから Program Gate へ渡す出力は次の2点のみ。
  - `fixedKeyDrift=0|>0`
  - `pendingBypassDetected=true|false`
- 上記以外（品質値や候補別判定）は `MVP-EXIT-01` 側の責務とする。

## Stream H current-main checkpoint (2026-06-13)

### Input read

- Candidate: `origin/main@06122262dfbee72b300b89d4fa90201726d594ee`.
- Read files:
  - `issue-FB-P0-2A2B2C-stream-c-planning-baseline.md`
  - `issue-FB-P2C-01-a1-interface-contract.md`
  - `issue-FB-P2C-01-a2-mock-validation.md`
  - `issue-FB-P2C-01-a3-implementation.md`
- Scope note: this checkpoint records planning status only. It does not edit `03_Implement/`, shared architecture files, public documentation, SafeMode policy, or downstream P2A/P2B/P2C issue state.

### Current classification

| Item | Current state | Baseline interpretation |
| --- | --- | --- |
| P2C A1 interface contract | `Status=Done`, `DecisionStatus=Fixed`, `ContractID=CTR-FB-P2C-01-V1` | A1 contract is fixed enough for mock-validation planning. |
| P2C A2 mock validation | `Status=Done`, `DecisionStatus=Fixed`, `MV-01..04` defined | A2 mock evidence requirements are fixed; downstream implementation still needs actual evidence attachment in its own lane. |
| P2C A3 implementation plan | `Status=Done`, `DecisionStatus=Fixed`, implementation plan only | A3 planning handoff is fixed, but Stream H still has no permission to edit implementation files. |
| FB-P0 fixed keys | `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`, `schemaVersion=1.0.0`, `overridePolicy=human_dual_control_only`, `safeModeDefault=ON`, `safeModeBoundary=SAFE_MODE_STRICT_ON` | No fixed-key drift found in this checkpoint. |
| Approval / held state | `Approval Record=Pending`, `HIL-RS-02-GOV-EXCEPTION-01=held` | Program remains `Conditional / Needs-decision`, not Go. |

### Decision

- `fixedKeyDrift=0` for the checked FB-P0/P2C planning boundary.
- `pendingBypassDetected=false` for this checkpoint: no request was made to treat A2/A3 as implementation-ready without the required approval/evidence boundary.
- FB-P0 remains **Open / P0**. Do not mark this issue Done while `Approval Record=Pending` and `HIL-RS-02-GOV-EXCEPTION-01=held` remain unresolved.
- A2/A3 implementation work remains downstream-owned. This checkpoint only clarifies that P2C planning records are internally consistent enough to serve as handoff inputs.

### Next action routing

1. Human/project governance: decide `Approval Record` fields (`approved_by`, `approved_at`, `evidence`) and `HIL-RS-02-GOV-EXCEPTION-01`.
2. Downstream implementation stream: attach real A2 mock pass evidence before treating A3 implementation as startable.
3. Program/release lane: keep final shipment No-Go through `MVP-EXIT-01` until product-value, environment, support, accessibility, and high-privilege lifecycle gates are accepted.
4. Stream H/Codex: continue updating this issue only for planning-boundary evidence; stop if asked to edit implementation files or to weaken `safeModeDefault=ON` / `SAFE_MODE_STRICT_ON`.

### 3) Plan→Execute→Verify（非依存）
- Plan: allowlist 2ファイル内の固定キー整合を維持。
- Execute: 判定式の再定義禁止、safeMode固定値の後退禁止。
- Verify: `fixedKeyDrift` と `pendingBypassDetected` を再計算し、差分があれば `No-Go`。

### 4) Stopper（他ストリーム要求時の停止）
- `issue-FB-P2A-*` / `issue-FB-P2B-*` / `issue-FB-P2C-*` への直接編集要求が来た場合は停止。
- 本Issueは統合入力I/Fの固定のみを担い、他ストリームの進行管理は行わない。

---

## Stream H current-main checkpoint (2026-06-14 post-2391)

### Input read

- Candidate: `origin/main@4e269023c7cf87c0e23484513682acb55bcb25ae`.
- Read files:
  - `issue-FB-P0-2A2B2C-stream-c-planning-baseline.md`
  - `issue-FB-P2C-01-a1-interface-contract.md`
  - `issue-FB-P2C-01-a2-mock-validation.md`
  - `issue-FB-P2C-01-a3-implementation.md`
- Scope note: this checkpoint records planning-boundary freshness only. It does not edit `03_Implement/`, architecture files, public documentation, SafeMode policy, runtime behavior, API/UI behavior, or downstream P2C issue state.

### Current classification

| Item | Current state | Baseline interpretation |
| --- | --- | --- |
| P2C A1 interface contract | `Status=Done`, `DecisionStatus=Fixed`, `ContractID=CTR-FB-P2C-01-V1` | A1 contract remains fixed enough for mock-validation planning. |
| P2C A2 mock validation | `Status=Done`, `DecisionStatus=Fixed`, `MV-01..04` defined | A2 mock evidence requirements remain fixed; downstream implementation still needs actual evidence attachment in its own lane. |
| P2C A3 implementation plan | `Status=Done`, `DecisionStatus=Fixed`, implementation plan only | A3 planning handoff remains fixed, but Stream H still has no permission to edit implementation files. |
| FB-P0 fixed keys | `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`, `schemaVersion=1.0.0`, `overridePolicy=human_dual_control_only`, `safeModeDefault=ON`, `safeModeBoundary=SAFE_MODE_STRICT_ON` | No fixed-key drift found in this checkpoint. |
| Approval / held state | `Approval Record=Pending`, `HIL-RS-02-GOV-EXCEPTION-01=held` | Program remains `Conditional / Needs-decision`, not Go. |

### Decision

- `fixedKeyDrift=0` for the checked FB-P0/P2C planning boundary.
- `pendingBypassDetected=false` for this checkpoint: no request was made to treat A2/A3 as implementation-ready without the required approval/evidence boundary.
- FB-P0 remains **Open / P0**. Do not mark this issue Done while `Approval Record=Pending` and `HIL-RS-02-GOV-EXCEPTION-01=held` remain unresolved.
- A2/A3 implementation work remains downstream-owned. This checkpoint only confirms that P2C planning records are still internally consistent as handoff inputs after #2391.

### Next action routing

1. Human/project governance: decide `Approval Record` fields (`approved_by`, `approved_at`, `evidence`) and `HIL-RS-02-GOV-EXCEPTION-01`.
2. Downstream implementation stream: attach real A2 mock pass evidence before treating A3 implementation as startable.
3. Program/release lane: keep final shipment No-Go through `MVP-EXIT-01` until product-value, environment, support, accessibility, high-privilege lifecycle, and FB-P0 approval/held gates are accepted.
4. Stream H/Codex: continue updating this issue only for planning-boundary evidence; stop if asked to edit implementation files or to weaken `safeModeDefault=ON` / `SAFE_MODE_STRICT_ON`.

### Verify

- `03_Implement\backend\.venv\Scripts\python.exe 01_Plans\issues\validate_active_issue_memos.py`
- `03_Implement\backend\.venv\Scripts\python.exe -m unittest 01_Plans\issues\tests\test_validate_active_issue_memos.py`
- `03_Implement\backend\.venv\Scripts\python.exe 01_Plans\triage_actionable_plans.py --root 01_Plans --format text`
- `git diff --check -- 01_Plans\issues\issue-FB-P0-2A2B2C-stream-c-planning-baseline.md`

---

## Stream H current-main checkpoint (2026-06-15 post-2400)

### Input read

- Candidate: `origin/main@7fcb253b57738229123b9c82581528fb4684caa9`.
- Recent merged planning records included in this sync:
  - #2399 `DATA-MAINT-03` governance checkpoint and backend CI recovery.
  - #2400 project baseline / governance checkpoint after #2399.
- Read files:
  - `issue-FB-P0-2A2B2C-stream-c-planning-baseline.md`
  - `issue-HIL-RS-02-A1-governance-contract-hardening.md`
  - `issue-PROJECT-BASELINE-01-latest-mainline-health-baseline.md`
  - `issue-PROJECT-GOV-01-mainline-convergence-and-branch-hygiene.md`
- Scope note: this checkpoint records planning-boundary freshness only. It does not edit `03_Implement/`, architecture files, public documentation, SafeMode policy, runtime behavior, API/UI behavior, ADR status, or downstream P2C issue state.

### Current classification

| Item | Current state | Baseline interpretation |
| --- | --- | --- |
| FB-P0 fixed keys | `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`, `schemaVersion=1.0.0`, `overridePolicy=human_dual_control_only`, `safeModeDefault=ON`, `safeModeBoundary=SAFE_MODE_STRICT_ON` | No fixed-key drift found in this checkpoint. |
| HIL-RS-02 governance gate | `Approval Record=Pending`, `HIL-RS-02-GOV-EXCEPTION-01=held`, `pendingDecisionQueueCount>0` | Program remains `Hold / Needs-decision`, not Go. |
| Project baseline | #2400 records latest-main health at `origin/main@7fcb253b57738229123b9c82581528fb4684caa9` | Baseline freshness improved; release readiness remains No-Go. |
| CI recovery | #2399 final CI run `9563` passed after `fastapi<0.137` cap | CI recovery evidence only; it does not unlock FB-P0 approval/held gates. |

### Decision

- `fixedKeyDrift=0` for the checked FB-P0 / HIL-RS planning boundary.
- `pendingBypassDetected=false` for this checkpoint: no request was made to treat pending/held records as approved.
- FB-P0 remains **Open / P0**. Do not mark this issue Done while `Approval Record=Pending` and `HIL-RS-02-GOV-EXCEPTION-01=held` remain unresolved.
- A2/A3 implementation work remains downstream-owned. This checkpoint only confirms that the planning records remain internally consistent as handoff inputs after #2400.

### Next action routing

1. Human/project governance: decide `Approval Record` fields (`approved_by`, `approved_at`, `evidence`) and `HIL-RS-02-GOV-EXCEPTION-01`.
2. HIL-RS-02 governance lane: keep `executeAllowed=false` and `Hold / Needs-decision` until pending/held records are explicitly resolved.
3. Program/release lane: keep final shipment No-Go through `MVP-EXIT-01` until product-value, environment, support, accessibility, high-privilege lifecycle, and FB-P0 approval/held gates are accepted.
4. Stream H/Codex: continue updating this issue only for planning-boundary evidence; stop if asked to edit implementation files, infer approval, or weaken `safeModeDefault=ON` / `SAFE_MODE_STRICT_ON`.

### Verify

- `03_Implement\backend\.venv\Scripts\python.exe 01_Plans\issues\validate_active_issue_memos.py`
- `03_Implement\backend\.venv\Scripts\python.exe -m unittest 01_Plans\issues\tests\test_validate_active_issue_memos.py`
- `03_Implement\backend\.venv\Scripts\python.exe 01_Plans\triage_actionable_plans.py --root 01_Plans --format text`
- `git diff --check -- 01_Plans\issues\issue-HIL-RS-02-A1-governance-contract-hardening.md 01_Plans\issues\issue-FB-P0-2A2B2C-stream-c-planning-baseline.md`
