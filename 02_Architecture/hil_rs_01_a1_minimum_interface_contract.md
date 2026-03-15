# HIL-RS-01-A1: Architecture最小I/F契約（Critique / 再提案差分 / レビュー帰属）

- Contract ID: `HIL-RS-01-A1`
- Status: Fixed
- Owner: Architecture Owner
- Scope: `02_Architecture/`
- Upstream: `01_Plans/adr/ADR-0026-next-phase-human-in-the-loop-reversible-synthesis.md`, `01_Plans/adr/ADR-0001-value-to-requirements.md`, `00_Prompt/domain.md`
- Related: `02_Architecture/review_attribution.md`, `02_Architecture/schemas_review_attribution.md`

## 0. Purpose

`ADR-0026` D2（契約先行）の下位具体化として、A2/A3が参照専用で利用する最小I/F契約を固定する。

## 1. Single reference / fixed IDs

- Single Reference / Single Source of Truth（SSOT）: `02_Architecture/hil_rs_01_a1_minimum_interface_contract.md`
- Contract IDs（固定）:
  - `A1-CRITIQUE-IF`
  - `A1-REDIFF-IF`
  - `A1-ATTR-IF`
  - `A1-ERROR-IF`

## 2. Contract matrix（必須 / 任意 / 禁止）

### 2.0 `A1-ERROR-IF`（共通エラー契約）

- `schemaVersion`: `1.0.0`（固定）
- `errorEnvelope` 必須:
  - `errorCode`（string, 固定列挙）
  - `message`（string, 人間可読・PII禁止）
  - `contractId`（`A1-CRITIQUE-IF | A1-REDIFF-IF | A1-ATTR-IF`）
  - `retryable`（boolean）
  - `occurredAt`（ISO-8601）
- `errorCode` 固定列挙:
  - `A1_SCHEMA_VERSION_MISMATCH`
  - `A1_REQUIRED_FIELD_MISSING`
  - `A1_TRACE_KEY_MISSING`
  - `A1_OVERRIDE_POLICY_VIOLATION`
  - `A1_PII_POLICY_VIOLATION`
- 禁止:
  - A1改訂なしでのエラーコード追加
  - `message` への email / external_uid / provider user id 埋め込み
  - `contractId` 欠落状態でのエラー返却

### 2.1 `A1-CRITIQUE-IF`

- `schemaVersion`: `1.0.0`（固定）
- 必須:
  - `critiqueId`
  - `targetRef`
  - `critiqueType` (`too_close | too_far | not_the_same | feels_off | no_articulable_reason`)
  - `createdAt` (ISO-8601)
  - `iteration` (integer >= 1)
- 任意:
  - `comment`
  - `constraintHints`
- 禁止:
  - critique入力のみで自動確定へ遷移
  - `reviewed` の自動更新
  - 実名 / email / external_uid / provider など生ID保存

### 2.2 `A1-REDIFF-IF`

- `schemaVersion`: `1.0.0`（固定）
- 構造固定（A2/A3で型追加・必須緩和を行わない）
- 必須:
  - `proposalId`
  - `basedOnIteration`
  - `diffOps[]`
  - `traceKey`（`critiqueId` と連結可能）
- `diffOps`最小単位:
  - `opId`
  - `opType` (`add | remove | move | regroup | relabel`)
  - `targetRef`
  - `before`
  - `after`
- 任意:
  - `rationale`
- 禁止:
  - 逆操作不能な片方向差分
  - `traceKey` なしの差分
  - SafeMode禁止操作（share/export）を暗黙実行

### 2.3 `A1-ATTR-IF`

- `schemaVersion`: `1.0.0`（固定）
- 必須:
  - `reviewState` (`unreviewed | human_reviewed`)
  - `reviewedAt`
  - `reviewerRef`（opaque string）
  - `auditRecordedAt`
- 任意:
  - `reviewContext`
  - `ownerRef`
- `overridePolicy`（固定）:
  - allowed: `human_dual_control_only`
  - prohibited: `ai_only_override`, `safemode_relaxation`, `share_export_leakage_relaxation`
  - requiredApproval: `SecurityOfficer+SystemOwner`
- 禁止:
  - AIのみで `human_reviewed` へ遷移
  - 生ID保存
  - `reviewEvents` 欠如を理由に閲覧不可化

### 2.4 `A1-ATTR-IF` tie-break policy

- `schemaVersion`: `1.0.0`（固定）
- 順序（固定・入替禁止）:
  1. `padding_compliance`
  2. `self_intersection_avoidance`
  3. `minimum_area_delta`
  4. `minimum_vertex_count`

## 3. Cross-cutting constraints

- SafeMode既定ONを後退させない。
- share/export漏えい防止を弱めない。
- 監査情報は最小化し、PII保存を既定禁止とする。
- A2は `03_Implement/**` のみ、A3は `04_Documentation/**` のみ編集する。
- `01_Plans/issues/README.md` と `01_Plans/project-progress-dashboard.md` は統合フェーズまで編集しない。

## 4. ADR要否判定（Context / Decision / Consequences）

### Context

A1は `ADR-0026` D2の下位具体化であり、価値軸・安全制約・停止条件の上位方針変更を伴わない。

### Decision

ADR追加・更新は不要。上位方針変更を要する契約変更要求が出た場合のみ、承認完了まで停止する。

### Consequences

A2/A3は契約待ちなしで着手可能。契約変更要求はA1へ差し戻し、人間承認なしの改訂を禁止する。

## 5. Contract freeze evidence

- `contractLinkLocked=true`
- `sharedResourceFreeze=true`
- 固定値は本書を唯一参照先とし、複線化を禁止する。

## 6. Handoff packet（A2 / A3）

- 固定値一覧:
  - `A1-CRITIQUE-IF`
  - `A1-REDIFF-IF`
  - `A1-ATTR-IF`
  - `CritiqueInputContract.schemaVersion=1.0.0`
  - `ReviewAttributionContract.schemaVersion=1.0.0`
  - `ReviewAttributionContract.overridePolicy=human_dual_control_only`
  - `DeterministicTieBreakContract.schemaVersion=1.0.0`
  - `DeterministicTieBreakContract.order=padding_compliance>self_intersection_avoidance>minimum_area_delta>minimum_vertex_count`
  - `ErrorContract.schemaVersion=1.0.0`
  - `ErrorContract.codes=A1_SCHEMA_VERSION_MISMATCH|A1_REQUIRED_FIELD_MISSING|A1_TRACE_KEY_MISSING|A1_OVERRIDE_POLICY_VIOLATION|A1_PII_POLICY_VIOLATION`
  - `contractLinkLocked=true`
  - `sharedResourceFreeze=true`
- 明示禁止:
  - 契約本文を参照せず独自I/Fを追加すること
  - 契約変更をA2/A3で実施すること
  - SafeMode / share-exportの安全制約を後退させること
- エスカレーション規定:
  - 契約変更要求は必ずA1へ差し戻し。A2/A3で改訂しない。


## 7. Contract change request routing（固定）

- 差し戻し先（唯一）:
  - `01_Plans/issues/issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`
- 受付対象:
  - 契約ID / schemaVersion / requiredFields / overridePolicy / tie-break順序の変更要求
- A2/A3での禁止:
  - 本契約書の直接改訂
  - 単一参照先（SSOT）の複線化


## 8. Phase 5 Gate判定（A2開始条件）

- チェックリスト（全項目必須）:
  - [x] Single Reference / Single Source of Truth（SSOT）が本書のみである。
  - [x] `contractLinkLocked=true` / `sharedResourceFreeze=true` が維持されている。
  - [x] `schemaVersion=1.0.0`（Critique / ReDiff / Attribution tie-break policy）が維持されている。
  - [x] 共通エラー契約（`A1-ERROR-IF`, `ErrorContract.schemaVersion=1.0.0`）が維持されている。
  - [x] 禁止事項（SafeMode後退禁止、share/export漏えい防止後退禁止、PII生値保存禁止）が維持されている。
  - [x] A2/A3文書に「契約本文を変更しない」ルールが明記されている。
- Gate判定:
  - Ready: 全項目達成かつ未定義契約変更要求0件。
  - Block: 1項目でも未達、または未定義契約変更要求/共有リソース更新要求/SafeMode後退前提が発生。

## 9. Fail-safe stop report template

- 失敗再現手順
- 競合ファイル
- 必要承認者
- 解決のYes/No質問


## 10. Decision Queue snapshot（A1 fixed）

| QueueID | Topic | Status | Decision |
|---|---|---|---|
| DQ-HIL-RS-01-A1-001 | Contract IDs freeze | Closed | `A1-CRITIQUE-IF` / `A1-REDIFF-IF` / `A1-ATTR-IF` / `A1-ERROR-IF` 固定 |
| DQ-HIL-RS-01-A1-002 | `schemaVersion` freeze | Closed | `1.0.0` 固定（Critique/Attribution/TieBreak） |
| DQ-HIL-RS-01-A1-003 | Deterministic判定順 | Closed | `padding_compliance > self_intersection_avoidance > minimum_area_delta > minimum_vertex_count` |
| DQ-HIL-RS-01-A1-004 | Change request routing | Closed | A1 issue差し戻しのみ許可 |
| DQ-HIL-RS-01-A1-005 | Error contract freeze | Closed | `A1-ERROR-IF` + errorCode 5件固定 |

## 11. Mock handoff interface（implementation-free validation）

- Critique fixture schema (`CritiqueInputFixtureV1`)
  - required: `schemaVersion`, `critiqueId`, `targetRef`, `critiqueType`, `createdAt`, `iteration`
  - optional: `comment`, `constraintHints`
- ReDiff fixture schema (`ReDiffFixtureV1`)
  - required: `proposalId`, `basedOnIteration`, `diffOps[]`, `traceKey`
  - `diffOps[].required`: `opId`, `opType`, `targetRef`, `before`, `after`
- Review attribution fixture schema (`ReviewAttributionFixtureV1`)
  - required: `schemaVersion`, `reviewState`, `reviewedAt`, `reviewerRef`, `auditRecordedAt`
  - optional: `reviewContext`, `ownerRef`
- Error fixture schema (`ErrorEnvelopeFixtureV1`)
  - required: `schemaVersion`, `errorCode`, `message`, `contractId`, `retryable`, `occurredAt`
  - fixed `errorCode`: `A1_SCHEMA_VERSION_MISMATCH | A1_REQUIRED_FIELD_MISSING | A1_TRACE_KEY_MISSING | A1_OVERRIDE_POLICY_VIOLATION | A1_PII_POLICY_VIOLATION`

Validation rules:
1. `schemaVersion` mismatch is Block.
2. Missing required key is Block.
3. `A1-REDIFF-IF` without `traceKey` is Block.
4. Any fixture with raw PII (`email`, `external_uid`, provider user id) is Block.
5. Any error outside fixed `errorCode` enum is Block.

## 12. Proceed verdict for downstream tracks

- A2: **Ready**（contract fixed + mock schema fixed）
- A3: **Ready**（contract fixed + non-goals fixed）
- Residual risk:
  - Fixture file naming drift between tracks (non-contractual).
  - Mitigation: treat naming drift as documentation mapping issue; do not mutate contract IDs or required fields.



## 13. A2/A3 immutability rule（enforced）

- A2/A3は本書を参照専用で利用し、契約本文の改訂を行ってはならない。
- 契約変更要求はA1 issueへ差し戻し、人間承認完了まで実装に反映しない。
- A2/A3で許可される変更は、実装内マッピング・テストfixture適合・文書注記のみ。


## 14. Downstream interface manifest（A2/A3 fixed handoff）

- A2/A3へ引き渡す固定I/F一覧（変更不可）:
  - `submitCritique(input: CritiqueInputFixtureV1): CritiqueAcceptedV1`
  - `proposeReDiff(input: ReDiffFixtureV1): ReDiffAcceptedV1`
  - `recordReviewAttribution(input: ReviewAttributionFixtureV1): AttributionRecordedV1`
  - `toContractError(input: UnknownFailure): ErrorEnvelopeFixtureV1`
- 検証キー（A2/A3共通）:
  - `contractId`
  - `schemaVersion`
  - `traceKey`
  - `snapshotVersion`
- freeze宣言:
  - `contractLinkLocked=true`
  - `sharedResourceFreeze=true`
