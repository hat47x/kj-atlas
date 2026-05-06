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
