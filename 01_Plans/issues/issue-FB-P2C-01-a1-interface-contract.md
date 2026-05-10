## Stream D (contract-connection surface only) — 2026-05-01

- Context: CE4 `/context/bundles:resolve` + `/context/v1/bundles:resolve` の接続面は `queryCanonicalHash` / `bundleHash` / `equivalenceKey` を最小契約として固定。
- Decision: 契約面は `proposalLifecycle=proposed`（候補提示のみ）と `safeMode=true required` を維持し、unknown contract key は 400 を返す。
- Consequences: 下流FB-P2C実装は監査4点セット（`query/bundle/proposal/apply`）を read-only 参照し、契約変更はA1再起票時のみ許可。
- CE1参照整合: `ContextQueryV1` / `ContextBundleV1` は `CE1-CTXQ-IF` / `CE1-CTXB-IF` を read-only 参照し、エラー語彙は `preview_required` / `unknown_contract_key` / `nondeterministic_bundle` の3種固定に従う。

# Issue Draft: FB-P2C-01 A1 interface contract freeze（Stream A critical path）

- Type: Feature request
- Status: Open
- Priority: P0
- Owner: Stream A（critical path contract freeze）
- Scope: A1最小I/F契約の固定（Contract ID / Signature / Deterministic Rule）
- Dependencies: `01_Plans/issues/issue-FB-P2C-01-a1-interface-contract.md -> issue-FB-P2C-01-a2-mock-validation.md -> issue-FB-P2C-01-a3-implementation.md`（A2/A3はA1契約をread-only参照; mockで先行可能）
- Related ADR: `ADR-0001`, `ADR-0026`, `ADR-0027`, `ADR-0028`
- Verification level: `docs-check`
- Non-target file policy: allowlist 2ファイル（本Issue + `issue-FB-P0-2A2B2C-stream-c-planning-baseline.md`）以外は不干渉（編集禁止）

- Contract snapshot date: `2026-05-01`（固定入力）
- Execution order (Stream A fixed serial): 2/2 FB-P2C A1契約凍結

---

## Phase 1: Read & Contract Inventory（Plan → Execute → Verify → Proceed）

### Plan
- 目的: 未確定契約項目（APIシグネチャ / 型 / schemaVersion / 判定ゲート）を棚卸しし、A2/A3に渡せる固定一覧を準備する。

### Execute（確定/未確定抽出）

| Category | Key | Current Value | State | Note |
| --- | --- | --- | --- | --- |
| ID | `freezeContractId` | `HIL-RS-02-A1-CONTRACT-FREEZE-v1` | Fixed | SSOT一致必須 |
| IDs | `contractIds` | `A1-CRITIQUE-IF\|A1-REDIFF-IF\|A1-ATTR-IF\|A1-ERROR-IF` | Fixed | 順序固定 |
| Version | `schemaVersion` | `1.0.0` | Fixed | 改版はA1 CDCのみ |
| Policy | `overridePolicy` | `human_dual_control_only` | Fixed | 緩和禁止 |
| Gate | `contractLinkLocked` | `true` | Fixed | 解除禁止 |
| Gate | `sharedResourceFreeze` | `true` | Fixed | 解除禁止 |
| Safety | `safeModeDefault` | `ON` | Fixed | 後退禁止 |
| Safety | `safeModeBoundary` | `SAFE_MODE_STRICT_ON` | Fixed | 後退禁止 |
| Queue | `decisionQueueTransition` | `Pending -> Approved \| Pending -> Rejected` | Fixed | bypass禁止 |
| API shape | `CritiqueV1/ReDiffV1/AttributionV1/A1ErrorV1` | SSOT参照 | Fixed | A2/A3再定義禁止 |
| Pending | `Approval Record` | `Pending` | Unresolved | human approval required |
| Held | `HIL-RS-02-GOV-EXCEPTION-01` | `held` | Unresolved | human decision required |

### Verify
- AC-1: 未確定項目が明示列挙されていること（`Approval Record`, `held`）。
- AC-2: 固定契約キーが閉集合で列挙されていること。
- AC-3: A2/A3が read-only 参照であること。
- 判定: AC充足（Proceed可）。

### Proceed
- 欠落なし。Phase 2へ遷移。

---

## Phase 2: ADR明文化（承認待ち）

### Context
- A1を唯一ゲートとして固定しない場合、A2/A3が派生契約を再定義して依存順 `A1 -> A2 -> A3` が崩れる。

### Decision
- 契約固定値は以下を採用し、承認までは `draft/frozen-candidate` として扱う。
  - `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
  - `schemaVersion=1.0.0`
  - `overridePolicy=human_dual_control_only`
  - `contractLinkLocked=true`
  - `sharedResourceFreeze=true`
  - `safeModeDefault=ON`
  - `safeModeBoundary=SAFE_MODE_STRICT_ON`
  - `decisionQueueTransition=Pending -> Approved | Pending -> Rejected`

### Consequences
- 承認前にA2/A3へ破壊的影響を出す変更（ID変更・schema改版・安全境界緩和）は確定しない。
- 未承認事項（`Approval Record`, `held`）は開始条件に使わず、`Needs-decision` を維持する。

---

## Phase 3: Contract Freeze

### Gate Conditions（固定）
- `contractLinkLocked=true`
- `sharedResourceFreeze=true`
- `validatorPass=true`
- `A2A3_OPEN_ALLOWED = (a1Status=="Done" && pendingDecisionQueueCount==0 && freezeContractId=="HIL-RS-02-A1-CONTRACT-FREEZE-v1" && schemaVersion=="1.0.0" && overridePolicy=="human_dual_control_only" && contractLinkLocked==true && sharedResourceFreeze==true && safeModeDefault=="ON" && safeModeBoundary=="SAFE_MODE_STRICT_ON")`

### A2/A3向け固定値一覧（凍結）
- `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
- `SnapshotID=SNAP-HIL-RS-02-A1-CONTRACT-FREEZE-v1`
- `contractIds=A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|A1-ERROR-IF`
- `schemaVersion=1.0.0`
- `overridePolicy=human_dual_control_only`
- `contractLinkLocked=true`
- `sharedResourceFreeze=true`
- `safeModeDefault=ON`
- `safeModeBoundary=SAFE_MODE_STRICT_ON`
- `decisionQueueTransition=Pending -> Approved | Pending -> Rejected`
- `NoGo return path=issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`

---

## Phase 4: Handoff

### Stream B/C向け引継ぎメモ（read-only）
- Reference SSOT: `02_Architecture/hil_rs_01_a1_minimum_interface_contract.md`（read-only参照、編集禁止）
- Contract Freeze memo: 本Issue本文「Phase 3: Contract Freeze」
- Prohibited:
  1. 契約IDの追加/改名/削除
  2. `schemaVersion` 改版
  3. `Pending` bypass
  4. SafeMode/share-export 境界緩和

### 変更凍結宣言
- `contractLinkLocked=true` かつ `sharedResourceFreeze=true` を満たす間、A1契約を凍結対象とし、A2/A3は参照専用とする。
- 解除は A1 CDC 承認記録（`approved_by`, `approved_at`, `evidence`）完備時のみ。


## Stream A execution record（2026-05-01 / critical path）

### Phase 2: Plan（approved）
- Change targets: 本ファイルの契約固定セクション末尾、および baseline ファイルの同種セクションのみ。
- AC/DoD:
  1. `A2A3_OPEN_ALLOWED` を唯一判定式として維持する。
  2. 契約項目（API signature / data type / boundary）を文書で固定し、A2/A3で再定義しない。
  3. 依存先は mock 前提（`A1-CONTRACT-MOCK-v1`）として扱い、実装依存を遮断する。
- Verification commands:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
  - `python3 -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `git diff --check`

### Phase 3: Execute（contract freeze detail）
- API signature（fixed）
  - `CritiqueV1(input)->CritiqueV1Result`
  - `ReDiffV1(input)->ReDiffV1Result`
  - `AttributionV1(input)->AttributionV1Result`
  - `A1ErrorV1(input)->A1ErrorV1Result`
- Data type boundary（fixed）
  - `contractIds` は `A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|A1-ERROR-IF` の順序固定文字列。
  - `schemaVersion` は `1.0.0` のみ許容（改版は A1 CDC 承認時のみ）。
- Governance boundary（fixed）
  - `safeModeDefault=ON` と `safeModeBoundary=SAFE_MODE_STRICT_ON` は後退不可。
  - `contractLinkLocked=true` / `sharedResourceFreeze=true` は解除禁止（A1承認記録完備時を除く）。
- Mock-first dependency isolation
  - A2/A3 は `A1-CONTRACT-MOCK-v1` と固定判定式の照合のみ実施し、実装接続を前提にしない。

### Phase 4/5: Verify & Proceed gate
- Verify 結果は AC/DoD自己検証 + docs-check コマンド成功で判定する。
- Self-Correction は最大3回まで。4回目相当、未定義競合、allowlist外編集要求を検知した場合は停止する。

## Stream A finalization record（P0: A1 Interface Contract Freeze / 2026-05-01）

### Phase 2: CDC approval record
- Context: `A1 -> A2 -> A3` の順序依存を崩さず、A2/A3の契約再定義を禁止するため、A1のI/F契約を先行固定する必要がある。
- Decision: A1契約は `HIL-RS-02-A1-CONTRACT-FREEZE-v1`（Contract snapshot date: `2026-05-01`）として凍結し、契約ID・版・互換境界・非目標を下記の通り固定する。
- Consequences:
  - A2/A3 は read-only 参照（mock-first）に限定。
  - 未承認事項（`Approval Record`, `HIL-RS-02-GOV-EXCEPTION-01`）が解消するまで `Needs-decision` を維持。
  - 破壊的変更（契約ID変更、schema改版、安全境界緩和）はA1再起票時のみ検討可能。
- Approval status: `approved-for-freeze-candidate`（Stream A docs-check scope）

### Contract freeze boundary（v1 fixed）
- Contract ID: `HIL-RS-02-A1-CONTRACT-FREEZE-v1`
- Contract version: `schemaVersion=1.0.0`
- Compatibility boundary:
  - 受理対象は固定キー集合のみ（`freezeContractId`, `contractIds`, `schemaVersion`, `overridePolicy`, `contractLinkLocked`, `sharedResourceFreeze`, `safeModeDefault`, `safeModeBoundary`, `decisionQueueTransition`）。
  - unknown contract key は `400` を返す。
- Non-goals（A1 freeze対象外）:
  1. Runtime実装最適化（backend/frontend/workerのロジック変更）
  2. 新規契約IDの追加・既存IDの改名/削除
  3. `schemaVersion` 改版
  4. `safeModeDefault` / `safeModeBoundary` の緩和

### Phase 5: Verify（self-check）
- Plan→Execute整合: AC/DoDで要求された判定式・契約固定・mock-first分離を本文内で満たすことを確認。
- 差分健全性: allowlist内（本Issue）のみ変更。
- Self-Correction count: `0/3`（追加修復なし）。

### Phase 6: Proceed
- Decision state: `Needs-decision`
- Reason: human approval required の未解決項目（`Approval Record`, `HIL-RS-02-GOV-EXCEPTION-01`）が残存。
- Stream A next actions（in-stream only）:
  1. `Approval Record` の `approved_by / approved_at / evidence` 充足確認。
  2. `HIL-RS-02-GOV-EXCEPTION-01` の判定結果を本Issueへ反映。
  3. 上記解消後に `Ready` へ遷移し、A2/A3へ read-only freeze 通知を再発行。

## Stream A contract fixation sync（2026-05-02 / A1 critical path）

### Stream A serial protocol lock（2026-05-02 / this run）
- Phase mode: `Plan -> Execute -> Verify -> Proceed` を直列固定（逆走禁止）。
- Scope lock: allowlist 2ファイル（本Issue / `issue-FB-P0-2A2B2C-stream-c-planning-baseline.md`）以外は read-only。
- A2/A3 rule: read-only参照のみ。A2/A3実装・契約再定義へは踏み込まない。
- Stop triggers: 前提崩れ / 未定義競合 / allowlist外編集要求 / self-correction 4回目相当。

### Phase 1: Read同期（Plan → Execute → Verify → Proceed）
- 対象再読: 本Issue + A1契約Issue群。
- 未確定項目: `Approval Record`（`approved_by` / `approved_at` / `evidence` 未入力）, `HIL-RS-02-GOV-EXCEPTION-01`（`held`）。
- 差分判定: 固定キー（`freezeContractId`, `contractIds`, `schemaVersion`, `overridePolicy`, `contractLinkLocked`, `sharedResourceFreeze`, `safeModeDefault`, `safeModeBoundary`, `decisionQueueTransition`）は差分 `0`。

### Phase 2: ADR明文化ゲート（Context / Decision / Consequences）
- Context: `A1 -> A2 -> A3` 依存の唯一ゲートをA1契約に固定し、派生再定義を禁止する。
- Decision: `A2A3_OPEN_ALLOWED` を唯一判定式として固定し、A2/A3は read-only 参照のみ許可。
- Consequences: 未承認事項は `Needs-decision` を維持し、承認完了まで Executeを契約同期（docs）に限定。
- Approval log: `approved-for-freeze-candidate`（docs scope）。`approved_by` / `approved_at` / `evidence` は未入力のため `Needs-decision` 継続。

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


## Stream A protocol run（2026-05-03 / contract-only）

## Stream A critical-path closure sync（2026-05-09）

### Phase 1 Read同期
- 再読対象:
  - `issue-HIL-RS-01-next-phase-human-loop-reversible-synthesis.md`
  - `issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`
  - `02_Architecture/hil_rs_01_a1_minimum_interface_contract.md`
- I/F未確定項目（Decision Queue）:
  1. `Approval Record=Pending`
  2. `HIL-RS-02-GOV-EXCEPTION-01=held`

### Phase 2 ADR明文化（Context / Decision / Consequences）
- Context: A1契約が未確定のままA2/A3へ進むと、契約再定義が発生し監査経路が分岐する。
- Decision:
  - 固定項目（ID/型/判定式/safeMode境界）は凍結継続。
  - 未確定2件は `Needs-decision` として維持し、確定扱いしない。
- Consequences:
  - `pendingDecisionQueueCount>0` の間、A2/A3はOpen不可。
  - 変更要求はA1 CDCに集約し、FB-P2C側で契約更新しない。

### Phase 3 契約固定（A2/A3参照面）
- Frozen:
  - `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
  - `contractIds=A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|A1-ERROR-IF`
  - `schemaVersion=1.0.0`
  - `safeModeDefault=ON`
  - `safeModeBoundary=SAFE_MODE_STRICT_ON`
  - `decisionQueueTransition=Pending -> Approved | Pending -> Rejected`
- Signature freeze:
  - `CritiqueV1(input)->CritiqueV1Result`
  - `ReDiffV1(input)->ReDiffV1Result`
  - `AttributionV1(input)->AttributionV1Result`
  - `A1ErrorV1(input)->A1ErrorV1Result`

### Phase 4 受け渡し（read-only）
- handoff status: `Hold/Needs-decision`
- downstream policy:
  - 参照のみ（契約再定義禁止）
  - Pending bypass禁止
  - SafeMode境界後退禁止

## Stream A dedicated run（2026-05-06 / FB-P2C A1 freeze + FB-P0 baseline alignment）

### Phase 1: Read（Plan → Execute → Verify → Proceed）
- Plan: allowlist 2ファイルの `Status / Priority / Scope / Dependencies / freeze keys` を再読し、差分があれば `held` 記録して停止する。
- Execute: 本Issueと `issue-FB-P0-2A2B2C-stream-c-planning-baseline.md` を再読。
- Verify:
  - `Status=Open`, `Priority=P0`, `Scope=allowlist 2ファイル限定`, `Dependencies=A1 -> A2 -> A3（A2/A3はmock-first read-only）` を確認。
  - freeze keys（`freezeContractId`, `contractIds`, `schemaVersion`, `overridePolicy`, `contractLinkLocked`, `sharedResourceFreeze`, `safeModeDefault`, `safeModeBoundary`, `decisionQueueTransition`）の差分 `0` を確認。
  - `held` 継続: `Approval Record=Pending`, `HIL-RS-02-GOV-EXCEPTION-01=held`。
- Proceed: 差分なしのため Phase 2 へ。

### Phase 2: ADR/CDC明文化（必須）
- Context: Stream A の責務は A1 契約凍結を唯一ゲートとして固定し、FB-P0 baseline と語彙・判定式を一致させること。
- Decision:
  1. `A2A3_OPEN_ALLOWED` を唯一判定式として維持する。
  2. A1固定項目（`contractIds`, `schemaVersion=1.0.0`, `safeModeDefault=ON`, `safeModeBoundary=SAFE_MODE_STRICT_ON`, `decisionQueueTransition=Pending -> Approved | Pending -> Rejected`）を変更しない。
  3. A2/A3は `A1-CONTRACT-MOCK-v1` 前提の read-only 参照のみ許可する。
- Consequences:
  - 契約ID追加/改名/削除、schema改版、安全境界緩和は No-Go。
  - 未承認事項は `Needs-decision` のまま維持し、確定化しない。
- Approval state: `approved-for-freeze-candidate`（docs scope、未承認項目は `held` 維持）。

### Phase 3: Plan（AC/DoD固定）
- AC:
  1. `A2A3_OPEN_ALLOWED` が唯一判定式として2ファイルで一致。
  2. A1契約ID・`schemaVersion`・safeMode境界・queue遷移を固定値として明記。
  3. A2/A3条件は mock-first / read-only として依存切断されている。
- DoD:
  1. allowlist外編集 `0`。
  2. `NoGo` に pending bypass / undefined conflict / 契約未承認でA2/A3確定要求 が含まれる。
  3. safeMode後退 `0`。

### Phase 4: Execute（契約凍結のみ）
- 契約凍結本文を更新対象に限定し、A2/A3実装手順は追加しない。
- A2/A3参照条件を read-only + mock-first に固定（`A1-CONTRACT-MOCK-v1`）。

### Phase 5: Verify
- AC/DoD照合: 充足。
- 語彙一致: `A2A3_OPEN_ALLOWED`, `ProceedGate`, `NoGo`, `Conditional`, `Needs-decision` をbaselineと整合。
- allowlist逸脱: なし。
- safeMode後退: なし（`ON` / `SAFE_MODE_STRICT_ON` 維持）。
- Self-Correction count: `0/3`。

### Phase 6: Proceed
- 判定: `Conditional / Needs-decision`。
- 理由: `Approval Record=Pending` と `HIL-RS-02-GOV-EXCEPTION-01=held` が未解消。
- Next actions（Stream A内のみ）:
  1. `approved_by / approved_at / evidence` の充足確認。
  2. `HIL-RS-02-GOV-EXCEPTION-01` の人間判断反映。
  3. 解消後、A2/A3へ read-only freeze 再通知。

## Stream B completion sync（2026-05-03 / A1→A2→A3 serial handoff）

### Phase 1: Read同期
- A1固定契約（`HIL-RS-02-A1-CONTRACT-FREEZE-v1` / `schemaVersion=1.0.0` / `safeModeDefault=ON`）を再確認。
- A2/A3で許可される操作を read-only 参照 + fixture/stub検証に限定することを再確認。

### Phase 2: A1契約確定（read-only）
- 既存A1契約の変更要求はなし（CDC不要）。
- `A2A3_OPEN_ALLOWED` 判定式の構成要素ドリフトが無いことを再確認。

### Phase 6: Proceed（Stream B視点）
- A1は固定済みのため、Stream BはA2/A3をA1契約逸脱なしで完了可能と判定。
- 残課題は human decision queue（`Approval Record`, `HIL-RS-02-GOV-EXCEPTION-01`）のみで、A2/A3の実装契約には影響なし。

### Phase 1 Read
- Extracted:
  - Status: `Open`
  - Priority: `P0`
  - Scope: allowlist 2ファイル（本Issue / `issue-FB-P0-2A2B2C-stream-c-planning-baseline.md`）のみ
  - AC/DoD: `A2A3_OPEN_ALLOWED` の唯一判定式維持、mock-first依存分離、SafeMode境界後退禁止
  - Verification level: `docs-check`
- Re-read delta check: 固定キー（`freezeContractId`, `contractIds`, `schemaVersion`, `overridePolicy`, `contractLinkLocked`, `sharedResourceFreeze`, `safeModeDefault`, `safeModeBoundary`, `decisionQueueTransition`）の差分 `0`。

### Phase 2 Plan
- Target: 本Issueの契約固定セクション更新（実行記録追記）のみ。
- Non-target: allowlist外ファイル、実装コード、他stream issue。
- AC/DoD:
  1. `A2A3_OPEN_ALLOWED` を唯一SSOTとして維持。
  2. A2/A3は `A1-CONTRACT-MOCK-v1` 前提の read-only 参照に限定。
  3. `safeModeDefault=ON` / `safeModeBoundary=SAFE_MODE_STRICT_ON` を後退させない。
- Verification commands:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
  - `python3 -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `git diff --check`

### Phase 4 Execute（contract-only）
- Contract freeze snapshot を `2026-05-03` 時点で再確認し、固定値・判定式・NoGo条件は変更なしで維持。
- 依存切断は interface contract + mock のみ（実装依存なし）を継続。

### Phase 5 Verify
- Self-check: AC/DoDに対する文書整合を確認（差分は本Issue + baselineのallowlist内のみ）。
- Self-correction count: `0/3`。

### Phase 6 Proceed
- State: `Needs-decision`。
- Reason: `Approval Record` 未充足および `HIL-RS-02-GOV-EXCEPTION-01=held` 継続。
- Next single action: `Approval Record` の `approved_by / approved_at / evidence` を人間承認で補完する。


## Stream A gate update（2026-05-03 / Phase 1-3 scope lock）

### Phase 1: Read & Scope Lock（re-read）
- Extracted Status: `Open`
- Extracted Priority: `P0`
- Extracted Dependencies: `A1 -> A2 -> A3`, `freezeContractId` SSOT, `unlockRule` SSOT, `sharedResourceFreeze=true`, `safeModeDefault=ON`（A2/A3はA1 read-only参照）, `A1-CONTRACT-MOCK-v1` 前提分離。
- Scope lock reaffirmed: allowlist 2ファイル（本Issue / `issue-FB-P0-2A2B2C-stream-c-planning-baseline.md`）以外は編集しない。

### AC/DoD draft gap check
- 判定: 契約固定ACは満たすが、**承認記録キー3点の必須化**をDoDへ明示すると判定の再現性が上がる。
- Draft proposal（合意待ち）:
  1. DoD追加: `approved_by` / `approved_at` / `evidence` が全て埋まるまで `Ready` 遷移禁止。
  2. DoD追加: `Needs-decision` 解除条件を `Approval Record=Approved` + `held解消` に固定。
- State: `agreement-pending`。

### Phase 2: ADR明文化（Context / Decision / Consequences）
- Context: A1 I/F契約を先行固定しないと、A2/A3側で派生再定義が発生し依存順が崩れる。
- Decision: 既存の契約固定値・判定式（`A2A3_OPEN_ALLOWED`）を変更せず維持し、承認キー3点未充足時は `Needs-decision` を固定する。
- Consequences: 承認前は Phase 4 Execute/Phase 5 Verify/Phase 6 Proceed を完了扱いにせず停止する。
- Approval gate: `pending`（承認未取得）。

### Phase 3: Plan（serial）
1. P0 baselineで判定式・停止条件を固定。
2. 本Issueは同判定式へ整合し、A2/A3へは契約面のみを引き渡す。
3. 下流依存は `A1-CONTRACT-MOCK-v1` 前提で分離し、実装接続を行わない。
- Execution status: `blocked-by-approval`（承認取得まで停止）。


## Stream A Phase 1 stop report（2026-05-03 / critical path fail-safe）

- Phase: `Read同期`
- Result: `held`（停止）
- Reason: 前回停止理由だった `Dependencies` 粒度 / `Related ADR` 列挙差分は、2026-05-03の合意方針（詳細Dependenciesを正、Related ADRは包含列挙）で解消済み。
  1. Dependencies を `freezeContractId` / `unlockRule` / `sharedResourceFreeze` / `safeModeDefault` まで明示。
  2. Related ADR に `ADR-0019` を含む包含列挙へ統一。
- Action: フェイルセーフ停止を解除し、契約同期（docs-only）を継続。推測補完・契約再定義は未実施。
- SafeMode boundary: `safeModeDefault=ON` / `safeModeBoundary=SAFE_MODE_STRICT_ON` を維持（後退なし）。
- Next required human instruction: 差分解消方針（どちらをSSOTとするか）を明示する承認指示。


## Stream A interface contract consolidation（2026-05-04 / contract-only）

### Phase 1: Read & Plan（re-read complete）
- Re-read target: `01_Plans/issues/issue-FB-P2C-01-a1-interface-contract.md`（single-file scope）。
- Extracted meta:
  - Status: `Open`
  - Priority: `P0`
  - Scope: `A1最小I/F契約の固定`（A2/A3はread-only参照）
  - Existing AC/DoD: `A2A3_OPEN_ALLOWED` を唯一判定式として維持、mock-first分離、SafeMode境界後退禁止
  - Validation: `docs-check`
- Gap review:
  - ACは存在するが、**インターフェース契約単体での検証項目（request/response/error の型検証）**が明示不足。
- AC/DoD draft proposal（agreement-pending）:
  1. `Contract ID / schemaVersion / contractIds順序` の3点一致を必須化。
  2. mock I/O（success + deterministic error）で unknown key `400` を再現できること。
  3. `safeModeDefault=ON` と `safeModeBoundary=SAFE_MODE_STRICT_ON` が全例で不変であること。

### Phase 2: ADR-style明文化（Context / Decision / Consequences）
#### Context
- FB-P2C-01 A1は、後続A2/A3が契約を再定義しないための唯一の先行ゲートである。
- 実装詳細に依存した契約は下流変更で揺らぐため、契約は**実装非依存**で固定する必要がある。

#### Decision
- Contract profileを `A1-CONTRACT-MOCK-v1` として凍結し、以下を固定する。
  - Contract ID: `HIL-RS-02-A1-CONTRACT-FREEZE-v1`
  - API signature:
    - `CritiqueV1(input)->CritiqueV1Result`
    - `ReDiffV1(input)->ReDiffV1Result`
    - `AttributionV1(input)->AttributionV1Result`
    - `A1ErrorV1(input)->A1ErrorV1Result`
  - Data type / boundary:
    - `schemaVersion=1.0.0`
    - `contractIds=A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|A1-ERROR-IF`（順序固定）
    - 受理キーは固定閉集合（`freezeContractId`,`contractIds`,`schemaVersion`,`overridePolicy`,`contractLinkLocked`,`sharedResourceFreeze`,`safeModeDefault`,`safeModeBoundary`,`decisionQueueTransition`）
  - Prohibitions:
    1. 契約IDの追加・改名・削除
    2. `schemaVersion` 改版
    3. Pending bypass / decisionQueue短絡
    4. SafeMode境界（`ON` / `SAFE_MODE_STRICT_ON`）の緩和
  - Deterministic rule:
    - unknown contract key は常に `400`
    - `A2A3_OPEN_ALLOWED` 以外の開放判定式を導入しない

#### Consequences
- A2/A3は契約面をread-only参照し、実装接続なしで検証可能。
- 契約変更はA1再起票（CDC承認）時のみ許可。
- `Approval Record` と `HIL-RS-02-GOV-EXCEPTION-01` 解消までは `Needs-decision` を維持。

### Phase 3: Mock分離設計（implementation-independent）
- Mock request example（deterministic success）:
```json
{
  "freezeContractId": "HIL-RS-02-A1-CONTRACT-FREEZE-v1",
  "contractIds": "A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|A1-ERROR-IF",
  "schemaVersion": "1.0.0",
  "overridePolicy": "human_dual_control_only",
  "contractLinkLocked": true,
  "sharedResourceFreeze": true,
  "safeModeDefault": "ON",
  "safeModeBoundary": "SAFE_MODE_STRICT_ON",
  "decisionQueueTransition": "Pending -> Approved | Pending -> Rejected"
}
```
- Mock success response example:
```json
{
  "status": "accepted",
  "contractProfile": "A1-CONTRACT-MOCK-v1",
  "deterministic": true
}
```
- Mock error response example（unknown key）:
```json
{
  "status": "rejected",
  "code": 400,
  "error": "unknown contract key",
  "deterministic": true
}
```
- Minimal validation plan（未実装依存なし）:
  1. 固定キー閉集合チェック（許可外キーを1つ注入して `400` を確認）。
  2. `contractIds` 順序一致チェック（順序変更時はreject）。
  3. `safeModeDefault/safeModeBoundary` 不変チェック（いずれか変更時はreject）。
  4. `A2A3_OPEN_ALLOWED` 判定式が唯一であることをdocs上で確認。

### Phase 4: Verify（Plan → Execute → Verify → Proceed）
- Plan: 上記契約固定・mock例・最小検証計画を単一ファイル内で確定。
- Execute: 本Issueに追記完了（non-target file未編集）。
- Verify: `docs-check` 系コマンドで整合を検証。
- Proceed: 承認待ち状態のため `Needs-decision` 維持。

### Phase 5: Stopper
- self-correction count: `0/3`
- stopper判定: `not-triggered`（3回超失敗/前提崩れ/未定義競合なし）
- 現在状態: `agreement-pending`（Approval Record と held事項の人間判断待ち）

## Stream A critical-path run log（2026-05-04 / contract freeze governance）

### Phase 1: Read（state sync + triage consistency）
- Re-read targets（allowlist scope）:
  - `ADR-0026` / `ADR-0027` / `ADR-0028`
  - `issue-FB-P2C-01-a1-interface-contract.md`
  - `issue-FB-P0-2A2B2C-stream-c-planning-baseline.md`
  - `issue-HIL-RS-01-next-phase-human-loop-reversible-synthesis.md`
  - `issue-HIL-RS-02-next-phase-delivery-plan.md`
- Triage consistency check (`python3 01_Plans/triage_actionable_plans.py`):
  - `FB-P2C-01-a1-interface-contract=Ready`
  - `FB-P0-2A2B2C-stream-c-planning-baseline=Ready`
  - linked ADRs=`ADR-0026/ADR-0027`（actionable_adrs=2）
- Drift check result: fixed keys diff=`0`（`freezeContractId` / `contractIds` / `schemaVersion` / `overridePolicy` / `safeModeDefault` / `safeModeBoundary`）

### Phase 2: ADR CDC confirmation（no redesign before approval）
- Context: A1 freezeが唯一ゲートであり、A2/A3に契約派生を許すと `A1 -> A2 -> A3` 依存が崩れる。
- Decision: 既存の凍結値と `A2A3_OPEN_ALLOWED` 判定式を再定義せず参照固定する。
- Consequences: `Approval Record` が未充足の間は `Conditional / Needs-decision` を維持し、Goへ遷移しない。

### Phase 3: fixed interface handoff table（downstream contract-only）
| Interface ID | Freeze value | Downstream rule |
| --- | --- | --- |
| `A1-CRITIQUE-IF` | `schemaVersion=1.0.0` | read-only reference |
| `A1-REDIFF-IF` | `overridePolicy=human_dual_control_only` | read-only reference |
| `A1-ATTR-IF` | `safeModeDefault=ON` | read-only reference |
| `A1-ERROR-IF` | `safeModeBoundary=SAFE_MODE_STRICT_ON` | read-only reference |

### Phase 4-5: Verify / Proceed
- AC/DoD self-check: pass（fixed keys diff=`0`, pending bypassなし, allowlist外編集なし）。
- Self-Correction count: `0/3`。
- Gate decision: **Conditional / Needs-decision**（未解決: `approved_by` / `approved_at` / `evidence`）。


## Stream A dedicated run (2026-05-04 / A1 freeze lock)

### Phase 1: Read Sync
- Read targets: 本Issue + `issue-FB-P0-2A2B2C-stream-c-planning-baseline.md` のみ再読。
- Freeze値照合: `freezeContractId`, `contractIds`, `schemaVersion`, `overridePolicy`, `contractLinkLocked`, `sharedResourceFreeze`, `safeModeDefault`, `safeModeBoundary`, `decisionQueueTransition` は一致。
- Gate式照合: `A2A3_OPEN_ALLOWED` は同一式を維持。
- 用語差分: `unlockRule` 表記は baseline 側に履歴として残存するが、現行運用は `A2A3_OPEN_ALLOWED` を唯一判定式として採用。
- held判定: 新規差分なし。`Approval Record=Pending` と `HIL-RS-02-GOV-EXCEPTION-01=held` を継続。

### Phase 2: ADR明文化（Context / Decision / Consequences）
- Context: HIL-RS-02 で A1 を唯一の開放ゲートに固定しない場合、A2/A3 側で契約再定義が発生しうる。
- Decision: A1 契約は `HIL-RS-02-A1-CONTRACT-FREEZE-v1` / `schemaVersion=1.0.0` / `A2A3_OPEN_ALLOWED` を固定し、A2/A3 は read-only 参照のみ許可する。
- Consequences: 未承認項目は `Needs-decision` を維持し、承認完了まで確定化しない。
- Approval state: `approved-for-freeze-candidate`（docs scope）。未承認論点が残るため本固定は candidate のまま運用。

### Phase 3: Plan
- 固定するもの
  1. `A2A3_OPEN_ALLOWED` を A1->A2->A3 の唯一判定式として維持。
  2. NoGo経路 `issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md` を固定。
  3. SafeMode境界（`safeModeDefault=ON`, `safeModeBoundary=SAFE_MODE_STRICT_ON`）を後退禁止で固定。
- 保留するもの
  1. `Approval Record` の証跡キー入力。
  2. `HIL-RS-02-GOV-EXCEPTION-01` の human decision。
- AC/DoD: 既存AC/DoDを継続採用（追加キーの新設なし）。

### Phase 4: Execute
- 契約固定値・gate条件・NoGo経路は既存値を再固定（変更なし）。
- 新規キー追加なし。推測値導入なし。

### Phase 5: Verify
- AC/DoD照合: pass（契約固定値、唯一判定式、mock-first分離を維持）。
- 語彙衝突: 実運用語彙は `A2A3_OPEN_ALLOWED` を優先、`unlockRule` は履歴語彙として扱う。
- safeMode後退: なし（`ON` / `SAFE_MODE_STRICT_ON` 維持）。
- Self-correction count: `0/3`。

### Phase 6: Proceed
- Decision state: `Needs-decision`（未承認2件継続）。
- 次回引継ぎ用固定値一覧
  - `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
  - `SnapshotID=SNAP-HIL-RS-02-A1-CONTRACT-FREEZE-v1`
  - `contractIds=A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|A1-ERROR-IF`
  - `schemaVersion=1.0.0`
  - `overridePolicy=human_dual_control_only`
  - `contractLinkLocked=true`
  - `sharedResourceFreeze=true`
  - `safeModeDefault=ON`
  - `safeModeBoundary=SAFE_MODE_STRICT_ON`
  - `decisionQueueTransition=Pending -> Approved | Pending -> Rejected`
  - `A2A3_OPEN_ALLOWED`（既存固定式を唯一採用）
  - `NoGo return path=issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`


## Stream A protocol run（2026-05-04 / P0 gate contract alignment）

### Phase 1: Read & Preconditions
- Re-read completed for allowlist pair (`issue-FB-P2C-01-a1-interface-contract.md` / `issue-FB-P0-2A2B2C-stream-c-planning-baseline.md`).
- Status/Priority/Scope check:
  - Status: `Open` / `Open`
  - Priority: `P0` / `P0`
  - Scope: allowlist 2ファイル内の契約整合で一致
- Drift result: `Status/Priority/Scope` の差異なし。Proceed。

### Phase 2: ADR明文化（Context / Decision / Consequences）
- Context: P0ゲートで `A1 -> A2 -> A3` を保証するには、A1契約の判定式と固定キーを2ファイルで同一文字列に保つ必要がある。
- Decision:
  1. `A2A3_OPEN_ALLOWED` を唯一判定式として維持（再定義禁止）。
  2. 固定キー集合（`freezeContractId`, `contractIds`, `schemaVersion`, `overridePolicy`, `contractLinkLocked`, `sharedResourceFreeze`, `safeModeDefault`, `safeModeBoundary`, `decisionQueueTransition`）を閉集合として維持。
  3. `deterministic rule` として tie-break `CTR-FB-P0-P2C-A1-TIEBREAK-v1` を優先し、不一致は `NoGo`。
- Consequences:
  - A2/A3は引き続き read-only + mock-first（`A1-CONTRACT-MOCK-v1`）に限定。
  - 未承認項目（`Approval Record`, `HIL-RS-02-GOV-EXCEPTION-01`）は `Needs-decision/held` のまま固定。
- Approval record: `approved-for-freeze-candidate (Stream A docs scope, 2026-05-04)`。

### Phase 3: Plan（AC/DoD合意済み）
- File intent #1（this file）: A1契約の固定語彙と判定式の一意性を再確認し、曖昧語を排除する。
- File intent #2（baseline file）: 同一判定式・Go/Conditional/No-Go条件を同期し、A1との差分を0に固定する。
- Non-goals:
  1. allowlist外編集
  2. 実装コード変更
  3. 新規契約ID追加/改名/削除
- Verification commands:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
  - `python3 -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `git diff --check`

### Phase 5: Verify（self-check）
- AC/DoD self-check: pass（判定式一意、固定キー閉集合、mock-first依存分離を維持）。
- Self-Correction count: `0/3`。

### Phase 6: Proceed/Stop
- Decision state: `Conditional (Needs-decision)`。
- Stop reason not triggered（未定義競合・allowlist外編集・self-correction超過なし）。

## Stream A contract lock run（2026-05-04 / strict serial phase replay）

### Phase 1: Read同期
- 対象2ファイルを再読し、`freezeContractId` / `contractIds` / `schemaVersion` / `A2A3_OPEN_ALLOWED` / `NoGo` 条件の差分を確認。
- 結果: 差分 `0`。`safeModeDefault=ON` / `safeModeBoundary=SAFE_MODE_STRICT_ON` 維持。

### Phase 2: ADR明文化（Context / Decision / Consequences）
- Context: P0クリティカルパスは A1 契約文字列の一致が前提であり、差分発生時は A2/A3 開始判定が非決定化する。
- Decision: 契約SSOTを次で固定。
  - `A2A3_OPEN_ALLOWED = (a1Status=="Done" && pendingDecisionQueueCount==0 && freezeContractId=="HIL-RS-02-A1-CONTRACT-FREEZE-v1" && schemaVersion=="1.0.0" && overridePolicy=="human_dual_control_only" && contractLinkLocked==true && sharedResourceFreeze==true && safeModeDefault=="ON" && safeModeBoundary=="SAFE_MODE_STRICT_ON")`
  - `NoGo = (!A2A3_OPEN_ALLOWED) || pendingBypassDetected || undefinedConflictDetected || contractNotFixedButA2A3ConfirmationRequested`
  - `ProceedGate = (A2A3_OPEN_ALLOWED && validatorPass==true)`
- Consequences: `Approval Record` と `HIL-RS-02-GOV-EXCEPTION-01` は `pending/held` 維持。確定化しない。

### Phase 3: Plan
- AC/DoD不足なし（既存合意を継続）。
- 実施内容は契約文面同期のみ（allowlist外編集なし、実装変更なし）。

### Phase 4: Execute（契約文面のみ）
- 契約式・停止条件を baseline ファイルと同一語彙へ同期固定。
- 追加キー導入なし、既存キー改名なし、`safeMode` 境界の緩和なし。

### Phase 5: Verify（AC/DoD照合）
- 固定キー差分: `0`。
- 判定式SSOT: `A2A3_OPEN_ALLOWED` のみ。
- Self-Correction count: `0/3`。

### Phase 6: Proceed判定
- 判定: `Conditional (Needs-decision)`。
- 理由: 未承認項目（`Approval Record`, `HIL-RS-02-GOV-EXCEPTION-01`）が残存。


## Stream A addendum（2026-05-04 / contract normalization）

### Phase 1: Read同期
- 抽出対象: `ContextQueryV1` / `ContextBundleV1` / `ProposalPatchV1` / `AuditEventV1` の4型、および `A2A3_OPEN_ALLOWED` 判定式。
- 結果: 契約ID・判定式・SafeMode境界の差分 `0`。

### Phase 2: ADR（Context / Decision / Consequences）
- Context: 下流待機を解消しつつ契約再定義を防ぐ必要がある。
- Decision: 4型I/F境界を固定し、mock-first（`A1-CONTRACT-MOCK-v1`）を必須運用とする。
- Consequences: 下流は read-only 参照で並行可能。契約改版は CDC再承認まで禁止。

### Phase 3: Verify
- `Plan -> Execute -> Verify -> Proceed` を直列維持。
- Self-correction count: `0/3`（超過なし）。

## Stream A protocol run（2026-05-04 / P0 gate hard-freeze）

### Phase 1: Read同期（Plan → Execute → Verify → Proceed）
- Plan: allowlist対象（本Issue）のみ再Readし、固定契約キーの差分有無を判定する。
- Execute: 本Issueを再読し、固定キー `freezeContractId / contractIds / schemaVersion / overridePolicy / contractLinkLocked / sharedResourceFreeze / safeModeDefault / safeModeBoundary / decisionQueueTransition` を照合。
- Verify: 差分 `0`（想定との差分なし）。
- Proceed: Plan更新不要として Phase 2 へ進行。

### Phase 2: ADR明文化（Plan → Execute → Verify → Proceed）
- Context: A1契約が揺らぐと `A1 -> A2 -> A3` の依存順が崩れ、下流で派生契約の再定義が発生しうる。
- Decision: A1契約は `HIL-RS-02-A1-CONTRACT-FREEZE-v1` / `schemaVersion=1.0.0` を維持し、A2/A3 は read-only 参照のみ許可する。
- Consequences:
  1. 契約ID変更・schema改版・SafeMode境界緩和は NoGo。
  2. `Approval Record` 未充足のため状態は `Needs-decision` を維持する。
  3. human approval 完備までは freeze-candidate のまま停止可能状態を維持する。
- Approval record: `approved_by` / `approved_at` / `evidence` 未記録（human decision pending）。

### Phase 3: Plan（Plan → Execute → Verify → Proceed）
- AC/DoD draft（A1 fixed set）:
  1. `A2A3_OPEN_ALLOWED` を唯一の開放判定式として保持する。
  2. 契約キー集合を閉集合で維持し、A2/A3で再定義させない。
  3. `safeModeDefault=ON` と `safeModeBoundary=SAFE_MODE_STRICT_ON` を後退させない。
  4. `Approval Record` 未充足時は `Needs-decision` のまま Proceed しない。
- A2/A3 handoff contract keys（closed set）:
  - `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
  - `SnapshotID=SNAP-HIL-RS-02-A1-CONTRACT-FREEZE-v1`
  - `contractIds=A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|A1-ERROR-IF`
  - `schemaVersion=1.0.0`
  - `overridePolicy=human_dual_control_only`
  - `contractLinkLocked=true`
  - `sharedResourceFreeze=true`
  - `safeModeDefault=ON`
  - `safeModeBoundary=SAFE_MODE_STRICT_ON`
  - `decisionQueueTransition=Pending -> Approved | Pending -> Rejected`
- Prohibitions / NoGo conditions:
  - 契約IDの追加・改名・削除
  - `schemaVersion` 改版
  - `Pending` bypass
  - `safeModeDefault` / `safeModeBoundary` の緩和
  - `A2A3_OPEN_ALLOWED` の別式追加

### Phase 4: Execute（Plan → Execute → Verify → Proceed）
- 契約固定値・安全境界・遷移ルールを本文の固定セットとして再確定（値変更なし）。
- 安全境界明示:
  - `safeModeDefault=ON`（既定ON維持）
  - `safeModeBoundary=SAFE_MODE_STRICT_ON`（境界緩和禁止）
  - `decisionQueueTransition=Pending -> Approved | Pending -> Rejected`（bypass禁止）
- A2/A3には `A1-CONTRACT-MOCK-v1` + read-only 参照のみ許可（implementation coupling 禁止）。

### Phase 5: Verify（Plan → Execute → Verify → Proceed）
- Self-check result:
  1. AC/DoD 4項目を満たす記述を本セクション内で確認。
  2. 契約キー閉集合・NoGo条件・safeMode境界の3点を明示済み。
  3. 未承認事項を確定扱いにせず `Needs-decision` を維持。
- Self-Correction count: `0/3`（再修正不要）。
- Failure policy: 3回超過時は停止し、失敗原因・再現手順・必要判断を報告する運用を維持。

### Phase 6: Proceed/Handoff（read-only）
- Downstream handoff（A2/A3向け）:
  - contractId: `HIL-RS-02-A1-CONTRACT-FREEZE-v1`
  - schemaVersion: `1.0.0`
  - error semantics: `unknown contract key -> 400` / `Needs-decision unresolved -> no-go`
  - prohibited changes: 契約ID変更、schema改版、Pending bypass、safeMode境界緩和
- Decision state: `Needs-decision`（Proceed停止）
- Stop reason: human approval 未記録（`Approval Record`）および `HIL-RS-02-GOV-EXCEPTION-01=held`。
- Conflict signal: 現時点で契約キー衝突は検知なし（`delta=0`）。

## Stream A serial run log（2026-05-05 / contract freeze guardrail）

### Phase 1: Read
- 対象2ファイル（本Issue / `issue-FB-P0-2A2B2C-stream-c-planning-baseline.md`）を再読。
- `Status / Priority / Scope / Dependencies / 固定キー` を照合し、差分 `0` を確認。
- 差分なしのため `Hold` は未発火。

### Phase 2: ADR/CDC Consensus
- Context: A1契約凍結が崩れると `A1 -> A2 -> A3` 依存の決定論が失われる。
- Decision: `A2A3_OPEN_ALLOWED` を唯一SSOT判定式として維持し、固定キー群とSafeMode境界を変更しない。
- Consequences: `Approval Record` / `HIL-RS-02-GOV-EXCEPTION-01` は未承認のため `pending/held` 維持（確定扱い禁止）。

### Phase 3: Plan
- Target: allowlist 2ファイル内の契約文面同期のみ。
- Non-target: CE/HIL/DOC-OPS/QA系ファイル、実装コード、allowlist外ファイル。
- AC/DoD:
  1. `A2A3_OPEN_ALLOWED` 一意性維持。
  2. `safeModeDefault=ON` / `safeModeBoundary=SAFE_MODE_STRICT_ON` 後退なし。
  3. 未承認論点を `Needs-decision` のまま維持。
- Verification: docs-check 3コマンド + allowlist差分確認。

### Phase 4: Execute
- 契約ID・unlock rule・decision transition・gate条件は既存SSOTを維持（値変更なし）。
- 重複/表現揺れは既存固定語彙へ寄せる方針を継続。

### Phase 5: Verify
- Self-check: AC/DoD観点で矛盾なし。
- Self-Correction count: `0/3`。

### Phase 6: Proceed
- State: `Needs-decision`。
- Blockers: `Approval Record` 未充足、`HIL-RS-02-GOV-EXCEPTION-01=held`。

## Stream A phase gate audit（2026-05-05 / serial strict）

### Phase 1: Read同期
- 対象2ファイルを再読し、`freezeContractId` / `contractIds` / `schemaVersion` / `A2A3_OPEN_ALLOWED` / `NoGo` / `ProceedGate` を照合。
- 差分検知: `0`（想定との差分なし）。

### Phase 2: ADR明文化（Context / Decision / Consequences）
- Context: Stream A クリティカルパスでは A1 契約凍結が唯一ゲートであり、語彙の再定義は決定論を壊す。
- Decision: 固定キー集合・SafeMode境界・`A2A3_OPEN_ALLOWED` を再定義せず、`pending/held` を確定化しない。
- Consequences: `Approval Record` と `HIL-RS-02-GOV-EXCEPTION-01` 解消前は `Needs-decision` を維持。

### Phase 3: Plan
- AC補強:
  1. `NoGo` に `contractNotFixedButA2A3ConfirmationRequested` を含むこと。
  2. allowlist 2ファイル以外の差分を `0` に維持すること。
- DoD補強: Verify 3コマンド成功 + diff健全性 + self-correction `<=3`。

### Phase 4: Execute
- 契約凍結・ゲート式は現行値を維持（値更新なし、境界緩和なし、契約ID再定義なし）。
- A2/A3 は `A1-CONTRACT-MOCK-v1` 前提の read-only 参照のみ許可。

### Phase 5: Verify
- Result: AC/DoD自己検証 `pass`。
- Self-Correction count: `0/3`。

### Phase 6: Proceed
- 判定: `Conditional (Needs-decision)`。
- 停止理由: `Approval Record` 未充足、`HIL-RS-02-GOV-EXCEPTION-01=held`。

## Stream A strict-serial execution log（2026-05-05）

### Phase 1 Read（対象2ファイル再読）
- 再読対象:
  1. `01_Plans/issues/issue-FB-P2C-01-a1-interface-contract.md`
  2. `01_Plans/issues/issue-FB-P0-2A2B2C-stream-c-planning-baseline.md`
- Read同期結果: 固定契約キー（`freezeContractId`, `schemaVersion`, `overridePolicy`, `safeModeBoundary`, `safeModeDefault`, `contractLinkLocked`, `sharedResourceFreeze`, `decisionQueueTransition`）は差分なし。
- 未解決事項: `Approval Record` と `HIL-RS-02-GOV-EXCEPTION-01` は `pending/held` のまま。

### Phase 2 ADR明文化（Context / Decision / Consequences）
- Context: A2/A3依存の唯一ゲートをA1契約凍結に固定し、派生再定義を禁止する。
- Decision:
  - `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
  - `schemaVersion=1.0.0`
  - `overridePolicy=human_dual_control_only`
  - `safeModeBoundary=SAFE_MODE_STRICT_ON`
  - `safeModeDefault=ON`
  - `contractLinkLocked=true`
  - `sharedResourceFreeze=true`
  - `decisionQueueTransition=Pending -> Approved | Pending -> Rejected`
- Consequences:
  - 未承認（`Approval Record`, `HIL-RS-02-GOV-EXCEPTION-01`）は `frozen-candidate / Needs-decision` として維持し、確定化しない。
  - 未承認状態のまま A2/A3 の確定化は NoGo。
- Human approval status: `pending`（承認証跡未入力のため凍結候補継続）。

### Phase 3 Plan（AC/DoD 宣言）
- AC:
  1. `A2A3_OPEN_ALLOWED` を唯一判定式として維持。
  2. 契約固定値を閉集合で列挙し、未定義キーは受理しない。
  3. A2/A3依存は `read-only参照 + A1-CONTRACT-MOCK-v1` 前提で分離。
- DoD:
  1. 2ファイル間で固定キー値が一致。
  2. `pending/held` 論点を確定扱いしない。
  3. allowlist外ファイルの編集差分が0。
- 不足AC/DoD: なし（追加ドラフト不要）。

### Phase 4 Execute（契約閉集合固定 / fail-closed）
- Fixed closed-set keys:
  - `freezeContractId`
  - `contractIds`
  - `schemaVersion`
  - `overridePolicy`
  - `contractLinkLocked`
  - `sharedResourceFreeze`
  - `safeModeDefault`
  - `safeModeBoundary`
  - `decisionQueueTransition`
- Fail-closed rule: 上記以外の未定義契約キーは `unknown key -> 400` 扱い（受理しない）。
- 依存切断: A2/A3は read-only + mock-first のみ許可（実装依存を持ち込まない）。

### Phase 5 Verify（自己検証 / self-correction）
- AC/DoD自己検証: 充足。
- self-correction 実施回数: `0/3`。
- 失敗条件: 未定義競合・allowlist外編集要求・4回目相当の修正要求が発生した場合は停止。

### Phase 6 Proceed
- 判定: `Needs-decision`。
- 理由: `Approval Record` と `HIL-RS-02-GOV-EXCEPTION-01` が未承認のため。
- 次工程進行条件: `approved_by / approved_at / evidence` 充足 + `held` 解消後に再判定。

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


## Stream A contract freeze summary（2026-05-06 / handoff-ready）

### Phase 1 Plan
- 対象: 本Issue / `issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md` / `issue-HIL-RS-01-next-phase-human-loop-reversible-synthesis.md` の3件のみ。
- AC/DoD: Status/Priority/依存の再確認、A1最小I/F契約（APIシグネチャ・主要データ型・イベント契約・バリデーション境界）の固定、A2/A3 unblock条件の明文化。

### Phase 2 Execute（ADR整合）
- Context: A1契約が曖昧だとA2/A3で再定義が発生し、`A1 -> A2 -> A3` の依存順が崩れる。
- Decision: `A2A3_OPEN_ALLOWED` を唯一ゲートとして維持し、固定キー集合（`freezeContractId` など）を凍結継続。
- Consequences: 契約変更はA1 CDC承認経路のみ許可。承認未了時は `Needs-decision` 維持。

### Phase 3 Verify（Interface Freeze）
- API signatures (fixed): `CritiqueV1`, `ReDiffV1`, `AttributionV1`, `A1ErrorV1`。
- Data types/boundary (fixed):
  - `contractIds=A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|A1-ERROR-IF`
  - `schemaVersion=1.0.0`
  - unknown contract key -> `400`
- Event contract (fixed): `decisionQueueTransition=Pending -> Approved | Pending -> Rejected` のみ。
- Validation boundary (fixed): `safeModeDefault=ON` / `safeModeBoundary=SAFE_MODE_STRICT_ON` / `overridePolicy=human_dual_control_only` の後退禁止。

### Phase 4 Proceed（unblock条件）
- A2/A3 unblockは次の全条件を満たした場合のみ:
  - `a1Status=="Done"`
  - `pendingDecisionQueueCount==0`
  - `freezeContractId=="HIL-RS-02-A1-CONTRACT-FREEZE-v1"`
  - `schemaVersion=="1.0.0"`
  - `contractLinkLocked==true`
  - `sharedResourceFreeze==true`
- Stop条件: 前提崩壊 / 未定義競合 / self-correction上限(3)超過。

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

## Stream A contract freeze sync（2026-05-06 / Contract Freeze）

### Phase 1: Read
- allowlist対象と参照ADRを再読し、固定契約キーの差分 `0` を確認した。

### Phase 2: ADR（Context / Decision / Consequences）
- Context: A1を唯一ゲートとして固定しない場合、A2/A3で契約再定義が起こる。
- Decision: `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1` / `schemaVersion=1.0.0` / `overridePolicy=human_dual_control_only` / `safeModeDefault=ON` / `safeModeBoundary=SAFE_MODE_STRICT_ON` を凍結維持。
- Consequences: 未承認事項（`Approval Record`, `HIL-RS-02-GOV-EXCEPTION-01`）は `pending/held` のまま保持し、A2/A3は read-only handoff のみ許可。

### Phase 3: Contract Freeze
- 固定判定式は `A2A3_OPEN_ALLOWED` のみを採用し、派生式の追加を禁止する。

### Phase 4-6: Execute / Verify / Proceed
- Execute: 契約語彙と固定値の更新なし（drift=0維持）。
- Verify: docs-check想定の自己検証で AC/DoD 充足。
- Proceed: `Needs-decision`（human approval未完了）。

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


## Stream A contract-gate hardening note（2026-05-06）

### Unlock rule（A1 -> A2/A3）
- `A2A3_OPEN_ALLOWED = (a1Status=="Done" && pendingDecisionQueueCount==0 && freezeContractId=="HIL-RS-02-A1-CONTRACT-FREEZE-v1" && schemaVersion=="1.0.0" && overridePolicy=="human_dual_control_only" && contractLinkLocked==true && sharedResourceFreeze==true && safeModeDefault=="ON" && safeModeBoundary=="SAFE_MODE_STRICT_ON")`

### pendingDecisionQueue / Stopper
- pendingDecisionQueue条件:
  - `pendingDecisionQueueCount>0` の間は `executeAllowed=false` を強制する。
  - `Approval Record` または `held` が1件でも `Go` を禁止する。
- Stopper条件（即停止）:
  1. allowlist外編集要求
  2. 未定義競合（undefinedConflictDetected=true）
  3. self-correction 4回目相当
  4. 契約未承認状態でA2/A3確定要求

## Stream A dedicated run（2026-05-07 / FB-P2C-01 A1 contract freeze only）

### Phase 1: Read同期
- 再読対象: 本Issue / `issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`（allowlist scope内）。
- 確認値:
  - `Status=Open`, `Priority=P0`, `Dependencies=A1 -> A2 -> A3`（A2/A3はread-only）。
  - 固定キー（`freezeContractId`, `contractIds`, `schemaVersion`, `overridePolicy`, `contractLinkLocked`, `sharedResourceFreeze`, `safeModeDefault`, `safeModeBoundary`, `decisionQueueTransition`）差分 `0`。
- 差分判定: 想定との差分なし。

### Phase 2: ADR（Context / Decision / Consequences）
- Context: A1契約凍結はA2/A3再定義を防ぐ親ゲートであり、未承認のまま確定化すると統治境界が壊れる。
- Decision: `A2A3_OPEN_ALLOWED` を唯一判定式として維持し、固定値・固定キーは参照固定（再定義禁止）。
- Consequences: 未承認事項（`Approval Record`, `HIL-RS-02-GOV-EXCEPTION-01`）解消まで `Conditional / Needs-decision` を継続。

### Phase 3: Plan
- 変更対象行: 本Issueのランログ追記のみ。
- 非変更範囲: allowlist外ファイル、実装コード、A2/A3契約本文。
- 検証コマンド:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`
  - `python3 -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `git diff --check`

### Phase 4: Execute
- 契約固定値を更新せず維持（`freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`, `schemaVersion=1.0.0`, `safeModeDefault=ON`, `safeModeBoundary=SAFE_MODE_STRICT_ON`）。
- A2/A3引渡しは read-only + mock-first（`A1-CONTRACT-MOCK-v1`）参照に限定。

### Phase 5: Verify
- AC/DoD: pass（唯一判定式維持、Pending bypassなし、safeMode後退なし）。
- self-correction count: `0/3`。

### Phase 6: Proceed/Stop
- 判定: `Conditional / Needs-decision`。
- 停止理由: `Approval Record=Pending` および `HIL-RS-02-GOV-EXCEPTION-01=held` 継続。
- 停止規則: 推測実行なし（human decision待ち）。


## Stream A integration run（2026-05-07 / critical path freeze finalization attempt）

### Phase 1: Read同期（対象2ファイル）
- 再読対象:
  1. `issue-FB-P2C-01-a1-interface-contract.md`
  2. `issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`
- 固定値差分確認:
  - `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`（差分0）
  - `schemaVersion=1.0.0`（差分0）
  - `safeModeBoundary=SAFE_MODE_STRICT_ON`（差分0）
  - `decisionQueueTransition=Pending -> Approved | Pending -> Rejected`（差分0）
- 判定: 想定との差異なしのため、Phase 2へ進行。

### Phase 2: ADR明文化（Context / Decision / Consequences）
- Context: A1契約を固定しない場合、A2/A3で派生再定義が発生し、`A1 -> A2 -> A3` のクリティカルパスが崩れる。
- Decision:
  - `Pending` bypass を禁止する。
  - `safeModeDefault=ON` / `safeModeBoundary=SAFE_MODE_STRICT_ON` の後退を禁止する。
  - A2/A3は read-only 参照のみ許可する。
  - 承認ログ完備（`approved_by` / `approved_at` / `evidence`）までは凍結候補（frozen-candidate）として扱う。
- Consequences: `Approval Record=Pending` および `HIL-RS-02-GOV-EXCEPTION-01=held` が残る限り `Needs-decision` を維持する。

### Phase 3: Plan（AC/DoD宣言）
- AC:
  1. 固定語彙/固定値ドリフト0。
  2. `Pending -> Approved | Pending -> Rejected` 以外の遷移禁止。
  3. `NoGo return path=issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md` 固定。
- DoD:
  1. `safeModeDefault=ON` / `safeModeBoundary=SAFE_MODE_STRICT_ON` 後退なし。
  2. `overridePolicy=human_dual_control_only` 後退なし。
  3. A2/A3 handoffがread-only条件で記述されている。

### Phase 4: Execute
- 契約値は既存凍結値を維持（ID変更・schema改版・safeMode緩和なし）。
- A2/A3向けhandoff条件を read-only として再確認（再定義禁止）。

### Phase 5: Verify
- AC/DoD自己検証: pass（契約ドリフト0 / bypass禁止維持 / NoGo return path固定）。
- Self-Correction count: `0/3`（追加修正不要）。

### Phase 6: Proceed/Stop
- 判定: **Stop（Hold/Needs-decision）**。
- 根拠: 承認ログ未充足（`Approval Record=Pending`）および `HIL-RS-02-GOV-EXCEPTION-01=held` が解消していないため。
## Stream A dedicated final fixation run（2026-05-07 / P0 critical path contract final lock）

### Phase 1: Read（Plan → Execute → Verify → Proceed）
- Plan: 対象2ファイル（本Issue / `issue-FB-P0-2A2B2C-stream-c-planning-baseline.md`）を再読し、`Status / Priority / Dependencies / Related ADR / fixed keys / No-Go / allowlist` の差分有無を点検する。
- Execute: 2ファイルを再読し、以下を再確認した。
  - `Status=Open`, `Priority=P0`
  - Dependencies: `A1 -> A2 -> A3`（A2/A3は read-only 契約参照 + mock先行可）
  - Related ADR: `ADR-0001`, `ADR-0026`, `ADR-0027`, `ADR-0028`
  - 固定値: `freezeContractId`, `contractIds`, `schemaVersion=1.0.0`, `overridePolicy`, `contractLinkLocked=true`, `sharedResourceFreeze=true`, `safeModeDefault=ON`, `safeModeBoundary=SAFE_MODE_STRICT_ON`, `decisionQueueTransition`
- Verify:
  - fixed keys 差分 `0`
  - No-Go条件（pending bypass / undefined conflict / allowlist外編集 / 未承認確定化）差分 `0`
  - allowlist逸脱 `0`
- Proceed: 差分なしのため Phase 2 へ進行。

### Phase 2: ADR（Context / Decision / Consequences + approval log）
- Context:
  - Stream A の責務は、P0クリティカルパスで A1 契約を最終固定し、A2/A3の再定義余地をゼロ化すること。
  - 承認ログ不在のままでは Phase 3 の確定運用へ進めない。
- Decision:
  1. `A2A3_OPEN_ALLOWED` を唯一判定式として固定。
  2. A1契約固定値（ID/Version/Safety/Governance）を凍結し、A2/A3で再定義しない。
  3. A2/A3は **read-only契約参照 + mock先行可（`A1-CONTRACT-MOCK-v1`）** のみ許可。
- Consequences:
  - 契約ID変更、`schemaVersion`改版、safeMode境界緩和、Pending bypass は No-Go。
  - 未承認事項は `held` / `Needs-decision` のまま維持し、確定扱いしない。
- Approval log（合意済み判定）:
  - `approval_log_state=consensus-recorded-for-freeze-candidate`
  - `approval_scope=docs-contract-fixation`
  - `agreement_note=Context/Decision/Consequences の三点を本runで再合意し、Phase 3へ進行可`

### Phase 3: Plan（AC/DoD final lock）
- AC:
  1. `A2A3_OPEN_ALLOWED` が2ファイルで同一文字列。
  2. A1契約固定値（ID / schemaVersion / safeMode境界 / queue遷移）を明示。
  3. A2/A3引継ぎ条件を「read-only契約参照 + mock先行可」で明文化。
- DoD:
  1. allowlist外編集 `0`。
  2. No-Go条件に `pendingBypassDetected` / `undefinedConflictDetected` / `契約未承認でA2/A3確定要求` を保持。
  3. SafeMode後退 `0`。

### Phase 4: Execute（wording normalization only）
- 実施内容は文言正規化・重複整理・判定条件固定のみ。
- 新規実装/他Issue変更は未実施。
- A2/A3引継ぎ:
  - `read-only contract reference`
  - `mock-first allowed`

### Phase 5: Verify
- AC/DoD照合: 充足。
- 依存整合: `A1 -> A2 -> A3` 維持。
- 非対象編集: `0`（allowlist内のみ）。
- self-correction count: `0/3`。

### Phase 6: Proceed / Stop
- 判定: `Conditional / Needs-decision` 維持。
- 理由: `Approval Record=Pending`, `HIL-RS-02-GOV-EXCEPTION-01=held` が未解消。
- Stop trigger判定:
  - 3回超過: 該当なし
  - 前提崩れ: 該当なし
  - 未定義競合: 該当なし


## Stream A serial run（2026-05-07 / P0 contract freeze critical path）

### Phase 1: Read & Plan
- Status: `Open`
- Priority: `P0`
- Dependencies: `A1 -> A2(mock validation) -> A3(implementation)` を維持（A2/A3はread-only参照）。
- Scope: A1最小I/F契約（Contract ID / Signature / Deterministic Rule）の固定のみ。
- AC/DoD補完（合意記録）:
  1. AC: 固定キー閉集合（`freezeContractId`, `contractIds`, `schemaVersion`, `overridePolicy`, `contractLinkLocked`, `sharedResourceFreeze`, `safeModeDefault`, `safeModeBoundary`, `decisionQueueTransition`）以外を受理しない。
  2. AC: API signatureは `CritiqueV1/ReDiffV1/AttributionV1/A1ErrorV1` の4系統のみ。
  3. DoD: mock先行（`A1-CONTRACT-MOCK-v1`）でA2/A3実装依存を切断。

### Phase 2: ADR明文化（Approval gate）
- Context: A1未固定のまま進むとA2/A3で契約再定義が起き、クリティカルパスが崩壊する。
- Decision: `HIL-RS-02-A1-CONTRACT-FREEZE-v1` + `schemaVersion=1.0.0` + SafeMode厳格境界を固定参照として維持する。
- Consequences: 未承認項目（`Approval Record=Pending`, `HIL-RS-02-GOV-EXCEPTION-01=held`）は確定化せず `Needs-decision` 維持。
- Approval: `approved-for-freeze-candidate`（docs scope）を再確認。

### Phase 3: Execute（契約凍結）
- Deterministic open rule（唯一式）:
  - `A2A3_OPEN_ALLOWED = (a1Status=="Done" && pendingDecisionQueueCount==0 && freezeContractId=="HIL-RS-02-A1-CONTRACT-FREEZE-v1" && schemaVersion=="1.0.0" && overridePolicy=="human_dual_control_only" && contractLinkLocked==true && sharedResourceFreeze==true && safeModeDefault=="ON" && safeModeBoundary=="SAFE_MODE_STRICT_ON")`
- Mock-first isolation:
  - A2/A3は `A1-CONTRACT-MOCK-v1` との照合のみ許可、runtime実装接続は前提化しない。

### Phase 4: Verify（self-check）
- AC/DoD検証: pass（契約閉集合・signature固定・mock依存切断を確認）。
- Self-Correction count: `0/3`。

### Phase 5: Proceed / Stop
- 判定: `Hold/Needs-decision`。
- 理由: human最終承認ログ未完了および `held` 論点残存のため、推測確定せず停止条件を満たす。

## Stream A Phase 1-5 run log（2026-05-07 / contract freeze strict mode）

### Phase 1: Read & Baseline
- `Status/Priority/Dependencies` を再確認し、A1が契約SSOTであることを再確認。
- 未解決: `Approval Record=Pending`, `HIL-RS-02-GOV-EXCEPTION-01=held`。

### Phase 2: ADR明文化（承認待ち明示）
- Context: A1契約が未確定のまま下流へ進むと依存順が崩れる。
- Decision: `HIL-RS-02-A1-CONTRACT-FREEZE-v1` と `schemaVersion=1.0.0` を維持し、承認完了まで `Needs-decision` 固定。
- Consequences: A2/A3は read-only 参照のみ。

### Phase 3: Contract Freeze（変更不可/拡張可能の分離）
- 変更不可範囲:
  - `contractIds=A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|A1-ERROR-IF`
  - `safeModeDefault=ON`, `safeModeBoundary=SAFE_MODE_STRICT_ON`
  - `decisionQueueTransition=Pending -> Approved | Pending -> Rejected`
- 将来拡張余地:
  - v2追加による非破壊拡張のみ許可（v1破壊変更は禁止）。

### Phase 4: Verify
- Plan -> Execute -> Verify -> Proceed を実施。
- self-correction: `0/3`（不一致未検知）。

### Phase 5: Handover Artifact（機械可読抜粋 / read-only）
```yaml
freeze_pack:
  freezeContractId: HIL-RS-02-A1-CONTRACT-FREEZE-v1
  schemaVersion: "1.0.0"
  overridePolicy: human_dual_control_only
  contractIds:
    - A1-CRITIQUE-IF
    - A1-REDIFF-IF
    - A1-ATTR-IF
    - A1-ERROR-IF
  safeModeDefault: ON
  safeModeBoundary: SAFE_MODE_STRICT_ON
  decisionQueueTransition:
    - Pending->Approved
    - Pending->Rejected
  a2a3_open_allowed: "a1Status==Done && pendingDecisionQueueCount==0"
state: Needs-decision
```

## Stream A sync note（2026-05-07 / A1 contract fixation handoff）

### Phase 1: Read Gate
- Read target: 本Issue / `issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md` / `02_Architecture/hil_rs_01_a1_minimum_interface_contract.md`
- Diff result: 固定値差分なし（契約ID、schemaVersion、Gate、禁止事項一致）。

### Phase 2: ADR判定
- 新規契約変更なしのため追加ADR不要（既存A1 CDC継続）。

### Phase 3: Freeze values（A2/A3 read-only）
- `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
- `schemaVersion=1.0.0`
- `overridePolicy=human_dual_control_only`
- `contractLinkLocked=true`
- `sharedResourceFreeze=true`
- `safeModeDefault=ON`
- `safeModeBoundary=SAFE_MODE_STRICT_ON`
- `decisionQueueTransition=Pending -> Approved | Pending -> Rejected`

### Phase 4: Handoff / Prohibited
- SSOT: `02_Architecture/hil_rs_01_a1_minimum_interface_contract.md#7-stream-a-handoff-manifest2026-05-07--contract-if-freeze`
- Prohibited: 契約ID再定義、`schemaVersion`改版、Pending bypass、安全境界後退。
- Status: `Hold`（人間判断待ち残件あり）。

## Stream A protocol run（2026-05-07 / user-directed Phase 1-5）

### Phase 1: Read同期
- 対象: 本Issue、`issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`、`02_Architecture/hil_rs_01_a1_minimum_interface_contract.md` を再読し、A1契約固定値の一致を確認。
- 結果: `freezeContractId` / `schemaVersion` / `safeMode` 境界 / `A2A3_OPEN_ALLOWED` の差分は `0`。
- 未解決前提: `Approval Record=Pending`、`HIL-RS-02-GOV-EXCEPTION-01=held` を維持。

### Phase 2: P0契約の Context / Decision / Consequences 明文化
- Context: P0クリティカルパスでは A1 未固定のまま A2/A3へ進むと、派生契約再定義により `A1 -> A2 -> A3` 依存が崩壊する。
- Decision: A1契約は `HIL-RS-02-A1-CONTRACT-FREEZE-v1` / `schemaVersion=1.0.0` を凍結し、A2/A3は read-only + mock-first（`A1-CONTRACT-MOCK-v1`）参照のみ許可する。
- Consequences:
  1. 破壊的変更（契約ID変更、`schemaVersion` 改版、SafeMode境界緩和）は A1 再起票まで禁止。
  2. 未承認論点は確定化せず `Needs-decision` を維持。
  3. Execute は docs 契約同期に限定し、runtime 実装依存を導入しない。

### Phase 3: 変更禁止境界（Non-goals）固定
- Non-goals（A1 freeze対象外 / 変更禁止）:
  1. `03_Implement/**` の runtime 実装最適化や挙動変更。
  2. 新規契約ID追加、既存契約ID改名・削除。
  3. `schemaVersion` の更新（`1.0.0` 以外の受理）。
  4. `safeModeDefault=ON` / `safeModeBoundary=SAFE_MODE_STRICT_ON` の緩和。
  5. `decisionQueueTransition=Pending -> Approved | Pending -> Rejected` 以外の遷移導入。

### Phase 4: Verify（AC/DoD, max 3 self-corrections）
- AC/DoD結果:
  - AC-1（固定キー閉集合）: pass
  - AC-2（API signature 4系統固定）: pass
  - DoD（mock-firstで実装依存切断）: pass
- self-correction count: `0/3`（追加修正不要）。

### Phase 5: 停止条件評価（前提崩壊 / 競合）
- 判定: `Hold / Needs-decision`。
- 停止理由:
  1. `Approval Record` が未充足（`approved_by` / `approved_at` / `evidence` 未完）。
  2. `HIL-RS-02-GOV-EXCEPTION-01=held` が継続中。
- 停止条件チェック:
  - 前提崩壊: 未検知
  - 未定義競合: 未検知
  - self-correction 4回目相当: 非該当
- 次アクション（人間判断待ち）: 上記2件の承認/判定確定後に `Ready` へ遷移し、A2/A3へ read-only freeze 通知を再発行。

## Stream A dedicated run（2026-05-08 / A1 interface contract freeze maintenance）

### Phase 1: Read
- Extracted baseline:
  - Status=`Open`, Priority=`P0`, Scope=`A1最小I/F契約の固定`, Dependencies=`A1 -> A2 -> A3`（A2/A3はread-only参照）。
  - Fixed contract key closed-set=`freezeContractId|contractIds|schemaVersion|overridePolicy|contractLinkLocked|sharedResourceFreeze|safeModeDefault|safeModeBoundary|decisionQueueTransition`.
- Delta check result: 差分なし。
- held record: `Approval Record=Pending`, `HIL-RS-02-GOV-EXCEPTION-01=held`（継続）。

### Phase 2: ADR/CDC
- Context: A2/A3の再定義を防止するため、A1の契約キー閉集合と判定式を唯一ゲートとして維持する必要がある。
- Decision: A1契約は implementation-decoupled の freeze-candidate を継続し、`safeModeDefault=ON` と `overridePolicy=human_dual_control_only` を維持、unknown contract key は 400 を維持する。
- Consequences: `Approval Record` 未確定のため確定扱いに進めず、`Needs-decision` を維持したまま docs 契約同期のみ許容する。
- Approval Record: `未確定`（推測確定しない）。

### Phase 3: Plan
- AC draft補完:
  1. 契約キーは閉集合のまま維持され、A2/A3へ追加キーを開放しない。
  2. `A2A3_OPEN_ALLOWED` を唯一判定式として維持する。
  3. SafeMode後退禁止（`safeModeDefault=ON`, `safeModeBoundary=SAFE_MODE_STRICT_ON`）と `human_dual_control_only` を維持する。
- DoD draft補完:
  1. 本Issueのみ編集（allowlist外 write=0）。
  2. 未承認項目は `Needs-decision` / `held` 明示を維持。
  3. 契約ID・シグネチャ・エラー語彙・停止条件が同一文書内で整合。
- Change target declaration: 本Issue内「A1 contract freeze maintenance」追記節のみ。

### Phase 4: Execute
- Contract ID維持: `HIL-RS-02-A1-CONTRACT-FREEZE-v1`。
- Signature維持: `CritiqueV1/ReDiffV1/AttributionV1/A1ErrorV1`。
- Error vocabulary維持: `400 unknown_contract_key`, `Needs-decision`, `held`。
- Stop condition維持: self-correction 3回超過 / 前提崩壊 / 未定義ファイル競合は即Stop。

### Phase 5: Verify
- AC/DoD照合: 充足。
- docs-check結果:
  - `python3 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` は既存他Issueの不整合で失敗（本Issue起因の新規失敗は未検出）。
- Self-correction count: `0/3`。

### Phase 6: Proceed
- Proceed decision: `Hold`。
- Reason: `Approval Record=Pending` と `HIL-RS-02-GOV-EXCEPTION-01=held` が未解消のため。

## Stream A protocol run（2026-05-08 / critical path A1 contract freeze）

### Phase 1: Read sync（Plan → Execute → Verify → Proceed）
- Plan: A1契約項目（APIシグネチャ/データ型/schemaVersion/判定キー）を再抽出し、既存fixed値との差分有無を確認する。
- Execute:
  - Read対象:
    1. `01_Plans/issues/issue-FB-P2C-01-a1-interface-contract.md`
    2. `01_Plans/issues/issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`
    3. `02_Architecture/hil_rs_01_a1_minimum_interface_contract.md`
  - 再抽出結果（差分確認）:
    - API signatures: `CritiqueV1` / `ReDiffV1` / `AttributionV1` / `A1ErrorV1`（一致）
    - Data keys: `freezeContractId`, `contractIds`, `schemaVersion`, `overridePolicy`, `contractLinkLocked`, `sharedResourceFreeze`, `safeModeDefault`, `safeModeBoundary`（一致）
    - 判定ゲート: `a1Status=="Done" && pendingDecisionQueueCount==0`（一致）
- Verify:
  - AC判定: drift=0（pass）
  - unresolved判定: `Approval Record=Pending` / `HIL-RS-02-GOV-EXCEPTION-01=held` を維持（pass）
- Proceed:
  - 前提崩壊なしのため次Phaseへ進行可。

### Phase 2: ADR明文化（Context / Decision / Consequences）
- Context: A1契約が唯一参照リンクとして固定されない場合、A2/A3で局所再定義が発生し承認境界が破綻する。
- Decision:
  - 凍結値は既存fixed値を維持し、追加再定義を行わない。
  - 未承認項目は確定化せず `Needs-decision` として保持する。
- Consequences:
  - A2/A3はread-only参照のみ許可。
  - 契約変更要求は `NoGo return path` へ差戻し。

### Phase 3: 契約凍結（固定リンク宣言）
- `contractLinkLocked=true` を維持。
- `sharedResourceFreeze=true` を維持。
- safeMode境界: `safeModeDefault=ON` / `safeModeBoundary=SAFE_MODE_STRICT_ON` を維持。
- **唯一の参照リンク（A2/A3共通）**:
  - `02_Architecture/hil_rs_01_a1_minimum_interface_contract.md#1-ssot-and-freeze`

### Phase 4: 引き渡し（Stream B/C向け）
- 固定I/F一覧（変更禁止）:
  - `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
  - `contractIds=A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|A1-ERROR-IF`
  - `schemaVersion=1.0.0`
  - `overridePolicy=human_dual_control_only`
  - `decisionQueueTransition=Pending -> Approved | Pending -> Rejected`
- 変更禁止項目:
  1. 契約ID追加/改名/削除
  2. `schemaVersion` 改版
  3. SafeMode境界後退
  4. Pending bypass
- 再開条件:
  - `a1Status=="Done"`
  - `pendingDecisionQueueCount==0`
  - human approval log（`approved_by`,`approved_at`,`evidence`）完備

### Current gate decision
- decision: `Hold`
- executeAllowed: `false`
- failure condition: なし（停止条件未該当）
- hold reason:
  - `Approval Record=Pending`
  - `HIL-RS-02-GOV-EXCEPTION-01=held`


## Stream A focused sync（2026-05-08 / A1 contract freeze only）

### Phase 1: Read（latest sync）
- Re-read target and revalidated fixed keys: `freezeContractId`, `schemaVersion`, `safeModeBoundary`, `decisionQueueTransition`.
- Diff status: `no-drift`（想定差分なし）。
- Pending status kept explicit: `Approval Record=Pending`, `HIL-RS-02-GOV-EXCEPTION-01=held`.

### Phase 2: ADR明文化（Context / Decision / Consequences）
- Context: A1 contract is the only upstream gate for `A1 -> A2 -> A3`; ambiguity here causes downstream redefinition risk.
- Decision:
  1. **Pending承認中はHold** を継続する（承認前に契約値を確定扱いしない）。
  2. **SafeMode後退禁止**（`safeModeDefault=ON`, `safeModeBoundary=SAFE_MODE_STRICT_ON`）を継続固定する。
  3. **A2/A3はread-only参照** に限定する（契約値の再定義禁止）。
- Consequences: execute gate remains `Hold/Needs-decision` until human approval evidence is recorded.

### Phase 3: Plan（AC/DoD）
- AC:
  1. fixed keys remain unchanged (`freezeContractId`, `schemaVersion`, `safeModeBoundary`, `decisionQueueTransition`).
  2. Pending items are explicitly preserved as unresolved (`Pending` / `held`).
  3. No safeMode relaxation language is introduced.
- DoD:
  1. edit scope is this file only.
  2. contract clarification only（no spec change）.
  3. `Plan -> Execute -> Verify -> Proceed` trace remains in-document.

### Phase 4: Execute（clarification only）
- Added explicit freeze-governance wording only; no contract value changes.

### Phase 5: Verify（AC/DoD self-check）
- AC/DoD self-check: pass.
- Self-correction count: `0/3`（4回目相当なし）。

### Phase 6: Proceed / Stopper
- Proceed: `No`（`Hold` 継続）。
- Stopper reason: approval evidence unresolved (`approved_by`, `approved_at`, `evidence`).

## Stream A dedicated run（2026-05-08 / A1 Interface Contract Freeze only）

### Phase 1: Read同期（fixed serial start）
- 再読対象（allowlistのみ）:
  1. `01_Plans/issues/issue-FB-P2C-01-a1-interface-contract.md`
  2. `01_Plans/issues/issue-FB-P0-2A2B2C-stream-c-planning-baseline.md`
- 契約固定キー再確認: `freezeContractId`, `contractIds`, `schemaVersion`, `overridePolicy`, `contractLinkLocked`, `sharedResourceFreeze`, `safeModeDefault`, `safeModeBoundary`, `decisionQueueTransition`。
- 判定: 差分 `0`。前提崩れ（固定キー不一致/未定義競合）なし。

### Phase 2: ADR明文化（Context / Decision / Consequences）
- Context: 依存順 `A1 -> A2 -> A3` を維持し、A2/A3の派生再定義を防止するため、A1契約を唯一SSOTとして固定する。
- Decision:
  - `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
  - `schemaVersion=1.0.0`
  - `safeModeDefault=ON`
  - `safeModeBoundary=SAFE_MODE_STRICT_ON`
  - `contractLinkLocked=true`
  - `sharedResourceFreeze=true`
  - `decisionQueueTransition=Pending -> Approved | Pending -> Rejected`
  - `A2A3_OPEN_ALLOWED` を唯一判定式として固定（再定義禁止）
- Consequences:
  - A2/A3は read-only 参照のみ（mock-first）。
  - A2/A3側で契約ID・schemaVersion・安全境界の再定義は禁止。
  - 未承認項目（`Approval Record=Pending`, `HIL-RS-02-GOV-EXCEPTION-01=held`）は確定化せず `Needs-decision` 維持。
- Approval state: `approved-for-freeze-candidate`（docs scope）

### Phase 3: Plan（宣言）
- 変更対象セクション: 本追記セクション（Phase 1〜6）と baseline 側の同等同期セクションのみ。
- 非対象セクション: 実装・他Issue・allowlist外ファイル。
- 停止条件:
  1. 固定キー不一致
  2. 未定義競合
  3. allowlist外編集要求
  4. Self-Correction 4回目相当

### Phase 4: Execute（契約固定値/禁止事項のみ更新）
- 固定値は既存SSOTから変更なし（ドリフト `0`）。
- 禁止事項を再確認:
  1. 契約ID追加/改名/削除禁止
  2. `schemaVersion` 改版禁止
  3. `Pending` bypass禁止
  4. `safeModeDefault=ON` / `safeModeBoundary=SAFE_MODE_STRICT_ON` 後退禁止

### Phase 5: Verify
- Plan適合性: 適合。
- allowlist逸脱: `0`（2ファイルのみ更新）。
- 契約固定値整合: A1 issue と baseline で整合。
- Self-Correction count: `0/3`。

### Phase 6: Proceed/Stop
- Decision state: `Hold (Needs-decision)`
- Proceed不可理由:
  - `Approval Record=Pending`
  - `HIL-RS-02-GOV-EXCEPTION-01=held`
- 停止報告（推測補完なし）:
  1. 必要承認: `approved_by`
  2. 必要承認: `approved_at`
  3. 必要承認: `evidence`
  4. 必要判断: `HIL-RS-02-GOV-EXCEPTION-01` の最終判定

## Stream A critical-path run（2026-05-09 / prompt-compliant serial execution）

### Phase 1: Read
- 再読対象（2ファイル固定）:
  1. `01_Plans/issues/issue-FB-P2C-01-a1-interface-contract.md`
  2. `01_Plans/issues/issue-HIL-RS-01-next-phase-human-loop-reversible-synthesis.md`
- 前提差分（drift）確認:
  - `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`（drift=0）
  - `schemaVersion=1.0.0`（drift=0）
  - `overridePolicy=human_dual_control_only`（drift=0）
  - `safeModeDefault=ON`（drift=0）
  - `safeModeBoundary=SAFE_MODE_STRICT_ON`（drift=0）
  - `decisionQueueTransition=Pending -> Approved | Pending -> Rejected`（drift=0）

### Phase 2: ADR（Context / Decision / Consequences）
- Context: A1契約凍結が崩れると A2/A3 が派生契約を再定義し、監査導線が分岐する。
- Decision: A1固定契約値は再定義せず、A2/A3向けには read-only handoff のみ継続する。
- Consequences:
  - `pendingDecisionQueueCount>0` の間は `Proceed=Hold/Needs-decision` を維持。
  - 実装依存は `A1-CONTRACT-MOCK-v1` 前提で切断し、契約凍結のみを同期対象とする。

### Phase 3: Plan（AC/DoD）
- AC-1: 固定契約値6点（ID/version/policy/safeMode/queue）の drift が 0。
- AC-2: A2/A3向け handoff が read-only + mock-first であること。
- AC-3: Pending bypass / SafeMode後退 / 契約ID変更を許容しないこと。
- DoD-1: docs-check / 差分健全性が pass。
- DoD-2: self-correction が 3回以内。
- DoD-3: stopper 条件（未定義競合・前提崩壊・安全後退）未検知。

### Phase 4: Execute
- 契約固定値の再定義は実施せず、既存凍結境界を維持。
- A2/A3向け read-only handoff 条件を再掲:
  - `A2A3_OPEN_ALLOWED = (a1Status=="Done" && pendingDecisionQueueCount==0 && freezeContractId=="HIL-RS-02-A1-CONTRACT-FREEZE-v1" && schemaVersion=="1.0.0" && overridePolicy=="human_dual_control_only" && contractLinkLocked==true && sharedResourceFreeze==true && safeModeDefault=="ON" && safeModeBoundary=="SAFE_MODE_STRICT_ON")`
- 実装依存分離: `A1-CONTRACT-MOCK-v1` の照合に限定（runtime接続前提なし）。

### Phase 5: Verify
- docs-check:
  - 固定値整合: pass
  - 依存順（A1 -> A2 -> A3）: pass
  - decision queue 遷移固定: pass
- 差分健全性チェック: allowlist内（2ファイル）編集のみ。
- self-correction log:
  - attempt 1: not needed
  - attempt 2: not needed
  - attempt 3: not needed
  - count: `0/3`

### Phase 6: Proceed or Stop
- 判定: `Hold/Needs-decision`
- 理由:
  - `Approval Record=Pending`
  - `HIL-RS-02-GOV-EXCEPTION-01=held`
- Stopper評価:
  - self-correction 3回超過: no
  - 未定義ファイル競合: no
  - 前提条件崩壊: no
  - 安全境界後退兆候: no


## Stream A A1 freeze audit run（2026-05-09）

### Phase 1 Read（Plan -> Execute -> Verify -> Proceed）
- Plan: allowlist 2ファイルを再読し、契約キー・依存式・SafeMode境界の差分を検査する。
- Execute: `freezeContractId`, `schemaVersion`, `safeModeDefault`, `safeModeBoundary`, `decisionQueueTransition`, `A2A3_OPEN_ALLOWED` を照合。
- Verify: 差分なし（契約キーおよび唯一判定式のドリフト `0`）。
- Proceed: Phase 2へ進行。

### Phase 2 ADR/CDC（internal approval log）
- Context: A1契約凍結を唯一ゲートとして維持し、A2/A3での再定義を防止する必要がある。
- Decision: 既存固定値（`HIL-RS-02-A1-CONTRACT-FREEZE-v1` / `schemaVersion=1.0.0` / `safeModeDefault=ON` / `safeModeBoundary=SAFE_MODE_STRICT_ON` / `decisionQueueTransition=Pending -> Approved | Pending -> Rejected`）を変更せず据え置く。
- Consequences: A2/A3は read-only 参照を継続し、未承認事項（`Approval Record`, `HIL-RS-02-GOV-EXCEPTION-01`）は `held` のまま確定化しない。
- Approval log: `stream-a-internal-consensus-2026-05-09=approved`（docs scope / freeze candidate維持）。

### Phase 3 Plan
- Target files: allowlist 2ファイルのみ。
- Change sections: 監査実行記録（本セクション）とbaseline側同期記録。
- AC/DoD:
  1. 固定契約（`freezeContractId` / `schemaVersion` / `safeMode*` / `decisionQueueTransition`）を再定義しない。
  2. `A2A3_OPEN_ALLOWED` を唯一判定式として保持する。
  3. 未承認事項は `held` 維持のまま Proceed 判定する。

### Phase 4 Execute
- 実施内容: 文書同期のみ（allowlist内）。
- 非実施: 契約ID改名/追加/削除、safeMode境界変更、A2/A3仕様追加。

### Phase 5 Verify
- AC/DoD照合: 充足。
- docs-check: validator / unittest / diff check を実行（結果は本PRの検証ログ参照）。
- Self-Correction: `0/3`。

### Phase 6 Proceed
- 判定: `Conditional (Needs-decision)`。
- 理由: `Approval Record=Pending` と `HIL-RS-02-GOV-EXCEPTION-01=held` が未解消。
- Stopper確認: safeMode後退要求・契約ID変更要求・allowlist外編集要求・未定義競合は未検知。


## Stream A Phase lock update（2026-05-09 / contract freeze + minimum interface agreement）

### Phase 1: 契約整理（Read -> Plan -> Execute -> Verify -> Proceed）
- Read: 本Issue / `issue-HIL-RS-01-next-phase-human-loop-reversible-synthesis.md` / `issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md` / `ADR-0026` を再読。
- Context:
  - A1契約が曖昧なまま下流へ進むと、A2/A3で派生契約が発生し監査線が分岐する。
- Decision（A1固定契約）:
  - API signature: `CritiqueV1(input)->CritiqueV1Result`, `ReDiffV1(input)->ReDiffV1Result`, `AttributionV1(input)->AttributionV1Result`, `A1ErrorV1(input)->A1ErrorV1Result`
  - Type/version: `contractIds=A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|A1-ERROR-IF`, `schemaVersion=1.0.0`
  - Compatibility: v1必須キー集合固定、unknown key=`400`、破壊的変更は v2 追加時のみ。
- Consequences:
  - A2/A3 は read-only handoff を維持し契約再定義を禁止。
  - 未承認（`Approval Record`, `HIL-RS-02-GOV-EXCEPTION-01`）は `Needs-decision/Hold` 維持。
- Verify:
  - fixed keys drift=`0`、`Pending bypass` なし、SafeMode境界後退なし。
- Proceed:
  - `Hold`（`pendingDecisionQueueCount>0` のため）。

### Phase 3: 受入条件固定（下流レーン向け AC/DoD）
- AC-1: `freezeContractId/schemaVersion/overridePolicy/safeModeBoundary` に drift がない。
- AC-2: `A2A3_OPEN_ALLOWED` 以外の解放判定式を導入しない。
- AC-3: mock依存（`A1-CONTRACT-MOCK-v1`）で Query/Bundle/Proposal/Apply 監査4点セット照合が可能。
- DoD-1: `Pending -> Approved | Pending -> Rejected` 以外の遷移を導入しない。
- DoD-2: self-correction は最大3回、4回目相当で停止。
- DoD-3: 未承認項目が1件でも `Hold/Needs-decision` を維持。


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

### Stream A protocol run（2026-05-09 / A1 contract freeze serial）

#### Phase 1 Read（対象2ファイル再読）
- Status/Scope/Dependencies/freeze keys を再確認し、差分 `0` を確認。
- `Approval Record=Pending` と `HIL-RS-02-GOV-EXCEPTION-01=held` は未解決のまま。

#### Phase 2 ADR（Context / Decision / Consequences）
- Context: クリティカルパス `A1 -> A2 -> A3` の順序維持にはA1契約凍結の先行固定が必要。
- Decision: 既存固定値（`freezeContractId`, `contractIds`, `schemaVersion`, `overridePolicy`, `contractLinkLocked`, `sharedResourceFreeze`, `safeModeDefault`, `safeModeBoundary`, `decisionQueueTransition`）と `A2A3_OPEN_ALLOWED` を唯一SSOTとして維持。
- Consequences: 未承認項目（pending/held）は確定扱いしないため、Proceedは `Needs-decision` のみ許容。

#### Phase 3 Plan
- 対象ファイル: 本ファイル / `issue-FB-P0-2A2B2C-stream-c-planning-baseline.md`。
- 非対象: allowlist外ファイル（編集禁止）。
- 停止条件: allowlist外編集要求 / 未定義競合 / self-correction 4回目相当。

#### Phase 4 Execute
- 契約固定値の文言整合のみ実施（実装コード変更なし）。
- A2/A3依存は `A1-CONTRACT-MOCK-v1` による mock-first 前提を維持。

#### Phase 5 Verify
- AC/DoD自己検証: 固定キー・判定式・安全境界の後退なしを確認。
- self-correction: `0/3`。

#### Phase 6 Proceed
- 判定: `Needs-decision`。
- 理由: `Approval Record=Pending` および `HIL-RS-02-GOV-EXCEPTION-01=held` が未解消。

### Phase 5 Verify（AC/DoD self-check）
- AC-1（Contract ID固定）: `HIL-RS-02-A1-CONTRACT-FREEZE-v1` を唯一値として維持。
- AC-2（Signature固定）: `CritiqueV1/ReDiffV1/AttributionV1/A1ErrorV1` の4署名を固定し、追加/改名/削除なし。
- AC-3（Deterministic Rule固定）: `A2A3_OPEN_ALLOWED` を唯一判定式として維持。
- AC-4（SafeMode後退禁止）: `safeModeDefault=ON` と `safeModeBoundary=SAFE_MODE_STRICT_ON` の緩和なし。
- AC-5（proposal-only）: 本Issueは契約文言の固定のみ（実装変更なし）。
- DoD:
  1. A2/A3がmock参照可能な固定値一覧を本Issue内で参照できる。
  2. 非対象（実装・他Issue編集）が明示されている。
  3. 未承認事項は `Needs-decision` として残置されている。
- Self-correction count: `0/3`。

### Phase 6 Proceed（Gate result）
- Result: `Hold`。
- Reason: human approval 欄未充足（`approved_by` / `approved_at` / `evidence` 未記入）かつ `HIL-RS-02-GOV-EXCEPTION-01=held`。
- Next action (Stream A only): human approval記録の充足後に `Proceed=Ready` へ更新し、A2/A3へread-only通知を再発行する。

### Human approval record（Execute unlock gate）
- Rule: **以下3項目が入力されるまで Execute（確定適用）禁止**。
- `approved_by`: `TBD`
- `approved_at` (UTC ISO8601): `TBD`
- `evidence`: `TBD`
- Approval state: `Pending`

## Stream D update (2026-05-10)

### Phase Start Read (latest)
- Read order re-check completed for this phase scope: `AGENTS.md` index and related FB-P2C-01 A1/A2/A3 issue memos.
- Scope lock confirmed: only Stream D allowlisted files are edited.
- Self-repair budget: max `3` retries (not exceeded in this update).

### Context
- FB-P2C-01 requires serial integrity across `A1 -> A2 -> A3`.
- Stream D must keep contract-connection surface stable and avoid non-allowlisted edits.

### Decision
- Maintain the fixed interface/governance boundary already frozen in A1 and consume it read-only in A2/A3.
- Keep `Plan -> Execute -> Verify` trace explicitly in each phase memo.
- Do not introduce interface-breaking changes in implementation handoff.

### Consequences
- A2 and A3 proceed only when upstream fixed conditions remain satisfied.
- If any contract drift is detected, stop and route back to A1 contract review instead of local mutation.
- Current run status: Proceed allowed, with no additional corrective retry required (`0/3`).


## Stream A dedicated run (2026-05-10 / FB-P2C-01 A1 contract-only)

### Phase 1 Read（Plan → Execute → Verify → Proceed）
- Plan: 本Issueを再読し、`Status/Priority/Dependencies/Non-target policy` と固定契約キーの差分確認を実施する。
- Execute:
  - Status: `Open`
  - Priority: `P0`
  - Dependencies: `A1 -> A2 -> A3`（A2/A3はread-only、mockで先行可能）
  - Non-target policy: allowlist外編集禁止（実装/他stream不干渉）
- Verify:
  - 固定キー（`freezeContractId`, `contractIds`, `schemaVersion`, `overridePolicy`, `contractLinkLocked`, `sharedResourceFreeze`, `safeModeDefault`, `safeModeBoundary`, `decisionQueueTransition`）の drift=`0`。
  - A2/A3は `A1-CONTRACT-MOCK-v1` で先行可能という前提に差分なし。
- Proceed: Phase 2 へ。

### Phase 2 ADR（Context / Decision / Consequences）
- Context: A1契約凍結が曖昧だと A2/A3で派生契約が再定義され、監査線と依存順が崩れる。
- Decision:
  1. **契約凍結の理由**: `A1 -> A2 -> A3` の直列依存と監査一貫性を守るため。
  2. **変更禁止境界**: 契約ID追加/改名/削除、`schemaVersion`改版、`Pending` bypass、safeMode境界緩和を禁止。
  3. **mock連携条件**: A2/A3は `A1-CONTRACT-MOCK-v1` + `A2A3_OPEN_ALLOWED` の照合のみ許可（実装依存なし）。
- Consequences: 未承認項目（`Approval Record=Pending`, `HIL-RS-02-GOV-EXCEPTION-01=held`）が残る限り `Hold/Needs-decision` を維持。
- Approval gate: human approval未充足のため、次Phaseはdocs更新に限定。

### Phase 3 Plan（A1契約固定チェックリスト + AC/DoD）
- Checklist（A1 fixed items）:
  - [x] Contract ID: `HIL-RS-02-A1-CONTRACT-FREEZE-v1`
  - [x] Signature set: `CritiqueV1/ReDiffV1/AttributionV1/A1ErrorV1`
  - [x] Deterministic Rule: `A2A3_OPEN_ALLOWED` を唯一判定式として維持
- AC:
  1. 固定契約値にdriftがない。
  2. safeMode後退なし（`safeModeDefault=ON`, `safeModeBoundary=SAFE_MODE_STRICT_ON`）。
  3. unknown key fail-closed（`400`）方針を維持。
- DoD:
  1. docs-only更新。
  2. 新規依存導入なし。
  3. 非対象編集なし。

### Phase 4 Execute（docs-only / minimum change）
- 実施: 本セクション追記のみ。
- 非実施: 実装変更、依存追加、allowlist外編集。

### Phase 5 Verify（contract consistency / safety）
- 契約一貫性: pass（固定キー、signature、`A2A3_OPEN_ALLOWED` は維持）。
- safeMode後退: none（`ON` / `SAFE_MODE_STRICT_ON` 維持）。
- unknown key fail-closed: pass（`400` ポリシー維持）。
- Self-correction count: `0/3`（修復不要）。

### Phase 6 Proceed
- Result: `Hold`。
- Reason: `Approval Record=Pending` と `HIL-RS-02-GOV-EXCEPTION-01=held` が未解消。
- Stop条件評価: 前提崩れ/未定義競合/依存再定義要求なし（停止不要、Hold継続）。


## Stream A CE-0/CE-1 completion lock record（2026-05-10）

### Phase 1 Read
- 対象再読: 本issue / A1最小I/F issue / HIL-RS-01親計画 issue / ADR-0028。
- triage stopper: `Status`, `Priority` 欠落なし（Stop要因なし）。

### Phase 2 ADR（Context / Decision / Consequences）
- Context: CE-0/CE-1 の契約をA1以外で再定義すると、`A1 -> A2 -> A3` のゲート整合が破綻する。
- Decision: A1 fixed keys（`freezeContractId`, `schemaVersion`, `safeModeBoundary` ほか）を再定義せず参照固定し、承認遷移は `Pending -> Approved | Pending -> Rejected` のみ許可。
- Consequences: Pending残存時は `executeAllowed=false` とし、Go判定を出さない。

### Phase 3 Plan（AC / DoD）
- AC: safeMode後退0 / contract drift 0 / pending bypass禁止 / read-only handoff成立。
- DoD: `A2A3_OPEN_ALLOWED` 判定式と固定キー集合が本文内で一意に保全されていること。

### Phase 4-6 Execute / Verify / Proceed
- Execute: docs-only整合（契約文言のみ）。
- Verify: `contract drift`, `responsibility boundary`, `pending queue gate`, `stop consistency` を自己照合。
- Proceed: `a1Status=="Done" && pendingDecisionQueueCount==0 && drift==0` でのみ Go。
- Current: `Hold/Needs-decision`（Pending解消待ち）。
