## Stream D (contract-connection surface only) — 2026-05-01

- Context: CE4 `/context/bundles:resolve` + `/context/v1/bundles:resolve` の接続面は `queryCanonicalHash` / `bundleHash` / `equivalenceKey` を最小契約として固定。
- Decision: 契約面は `proposalLifecycle=proposed`（候補提示のみ）と `safeMode=true required` を維持し、unknown contract key は 400 を返す。
- Consequences: 下流FB-P2C実装は監査4点セット（`query/bundle/proposal/apply`）を read-only 参照し、契約変更はA1再起票時のみ許可。

# Issue Draft: FB-P2C-01 A1 interface contract freeze（Stream A critical path）

- Type: Feature request
- Status: Open
- Priority: P0
- Owner: Stream A（critical path contract freeze）
- Scope: A1最小I/F契約の固定（Contract ID / Signature / Deterministic Rule）
- Dependencies: `A1 -> A2 -> A3`, A2/A3はA1 read-only参照
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
