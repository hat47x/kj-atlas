# HIL-RS-01-A1: Architecture最小I/F契約（Critique / ReDiff / Attribution / Error）

- Contract ID: `HIL-RS-01-A1`
- Status: Fixed (a1Status=="Done")
- Owner: Architecture Owner
- Scope: `02_Architecture/`
- Upstream: `ADR-0026`, `ADR-0027`, `ADR-0001`, `00_Prompt/domain.md`

## 0) Governance Context / Decision / Consequences（A1 Hardening）

### Context
- HIL-RS-02 では A1契約を先行固定し、A2/A3の再定義・誤Open・Pending bypass を防止する必要がある。

### Decision
- 固定契約ID: `HIL-RS-02-A1-CONTRACT-FREEZE-v1`
- 固定統治値: `schemaVersion=1.0.0`, `overridePolicy=human_dual_control_only`, `contractLinkLocked=true`, `sharedResourceFreeze=true`
- Decision Queue 遷移: `Pending -> Approved | Pending -> Rejected` のみ
- A2/A3 Open化判定は本書で定義する **Gate条件の参照のみ** とし、A1ストリームでは実行しない

### Consequences
- A1契約に関する変更要求はA1 CDCへ集約され、下流での局所補完を禁止する。
- `human_dual_control_only` と safeMode境界の後退要求は NoGo（即停止）になる。

## 1) SSOT and Freeze

- Single Source of Truth:
  - `02_Architecture/hil_rs_01_a1_minimum_interface_contract.md`
- Freeze Pack ID:
  - `HIL-RS-02-A1-CONTRACT-FREEZE-v1`
- Freeze keys（must hold）:
  - `contractIds=A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|A1-ERROR-IF`
  - `schemaVersion=1.0.0`
  - `overridePolicy=human_dual_control_only`
  - `contractLinkLocked=true`
  - `sharedResourceFreeze=true`

## 2) Contract Matrix

### 2.1 `A1-CRITIQUE-IF`
- `schemaVersion`: `1.0.0`
- required: `critiqueId`, `targetRef`, `critiqueType`, `createdAt`, `iteration`
- optional: `comment`, `constraintHints`
- prohibits:
  - critique入力のみで自動確定
  - review自動昇格
  - 生ID（email/external_uid/provider user id）の保存

### 2.2 `A1-REDIFF-IF`
- `schemaVersion`: `1.0.0`
- required: `proposalId`, `basedOnIteration`, `diffOps[]`, `traceKey`
- `diffOps[].required`: `opId`, `opType`, `targetRef`, `before`, `after`
- `opType`: `add | remove | move | regroup | relabel`
- optional: `rationale`
- prohibits:
  - 非可逆差分
  - `traceKey` 欠落
  - SafeMode禁止操作の暗黙実行

### 2.3 `A1-ATTR-IF`
- `schemaVersion`: `1.0.0`
- required: `reviewState`, `reviewedAt`, `reviewerRef`, `auditRecordedAt`
- optional: `reviewContext`, `ownerRef`
- `reviewState`: `unreviewed | human_reviewed`
- `overridePolicy`:
  - allowed: `human_dual_control_only`
  - prohibited: `ai_only_override`, `safemode_relaxation`, `share_export_leakage_relaxation`
- prohibits:
  - AIのみで `human_reviewed` へ昇格
  - 生ID保存

### 2.4 `A1-ERROR-IF`
- `schemaVersion`: `1.0.0`
- required: `errorCode`, `message`, `contractId`, `retryable`, `occurredAt`
- fixed `contractId`: `A1-CRITIQUE-IF | A1-REDIFF-IF | A1-ATTR-IF`
- fixed `errorCode` enum:
  - `A1_SCHEMA_VERSION_MISMATCH`
  - `A1_REQUIRED_FIELD_MISSING`
  - `A1_TRACE_KEY_MISSING`
  - `A1_OVERRIDE_POLICY_VIOLATION`
  - `A1_PII_POLICY_VIOLATION`
- prohibits:
  - A1改訂なしでのerrorCode追加
  - `message` へのPII埋め込み

## 3) Deterministic Tie-break（A1-ATTR-IF）

- `schemaVersion=1.0.0`
- fixed order:
  1. `padding_compliance`
  2. `self_intersection_avoidance`
  3. `minimum_area_delta`
  4. `minimum_vertex_count`

## 4) Governance Gate（A2/A3 unlock rule）

A2/A3 の `Draft -> Open` は次の全条件を満たす場合のみ許可。

- `freezeContractId == "HIL-RS-02-A1-CONTRACT-FREEZE-v1"`
- `schemaVersion == "1.0.0"`
- `overridePolicy == "human_dual_control_only"`
- `contractLinkLocked == true`
- `sharedResourceFreeze == true`
- `a1Status == "Done"`
- `pendingDecisionQueueCount == 0`
- `hasUndefinedContractChangeRequest == false`
- `hasSafeModeRegressionRequest == false`
- `hasShareExportLeakageRelaxationRequest == false`
- Go/No-Go判定式（固定）:
  - `Go = (freezeContractId=="HIL-RS-02-A1-CONTRACT-FREEZE-v1" && schemaVersion=="1.0.0" && overridePolicy=="human_dual_control_only" && contractLinkLocked==true && sharedResourceFreeze==true && a1Status=="Done" && pendingDecisionQueueCount==0 && hasUndefinedContractChangeRequest==false && hasSafeModeRegressionRequest==false && hasShareExportLeakageRelaxationRequest==false)`
  - `NoGo = !Go`

Decision Queue permitted transitions:
- `Pending -> Approved`
- `Pending -> Rejected`

Any other transition is Block.

## 4.2) Unresolved Execution Tasks Start Conditions（A1 Freeze準拠）

A1凍結I/Fを維持したまま、未解決タスク（A2/A3）へ着手するための前提を次で固定する。

### A2（Frontend reversible synthesis application）着手条件

- 必須（全件一致）:
  - `freezeContractId=="HIL-RS-02-A1-CONTRACT-FREEZE-v1"`
  - `schemaVersion=="1.0.0"`
  - `overridePolicy=="human_dual_control_only"`
  - `contractLinkLocked==true`
  - `sharedResourceFreeze==true`
  - `a1Status=="Done"`
  - `pendingDecisionQueueCount==0`
  - `hasUndefinedContractChangeRequest==false`
  - `hasSafeModeRegressionRequest==false`
  - `hasShareExportLeakageRelaxationRequest==false`
  - `agreementStatus=="agreed"`（Phase PlanでAC/DoD不足が解消済み）
- 追加証跡（A2特有）:
  - Read-only artifact参照宣言（`mutationAllowed=false`）をA2メモに記載済み。
  - `A1-CRITIQUE-IF` / `A1-REDIFF-IF` / `A1-ATTR-IF` / `A1-ERROR-IF` の再定義差分 0 件。

### A3（Operations / documentation sync）着手条件

- 必須（全件一致）:
  - A2着手条件の全項目を満たすこと。
  - 運用文書同期は read-only handoff 値のみ使用し、契約値の局所補完をしないこと。
- 追加証跡（A3特有）:
  - Stop template（失敗条件 / 影響I/F / 必要な人間判断）がA3メモに存在すること。
  - `Pending -> Approved|Rejected` 以外の遷移を許容する記述が 0 件であること。

### NoGo / Stop（A2/A3共通）

- 次のいずれかで NoGo:
  - 固定値不一致（`schemaVersion` / `overridePolicy` / freeze flags）。
  - 未定義契約変更要求あり（`hasUndefinedContractChangeRequest==true`）。
  - 安全境界後退要求あり（SafeMode または share/export）。
  - Decision Queue に `Pending` が残存（`pendingDecisionQueueCount>0`）。
- Self-Correction は最大3回。4回目相当は停止し、A1 CDCへ差戻す。

## 4.1) Read-only Contract Snapshot Artifact（Phase 4 発行物）

A1契約の mock用I/F は以下の read-only artifact として固定し、A2/A3 での再定義を禁止する。

| Artifact Key | Signature / Type | Prohibited Changes |
| --- | --- | --- |
| `A1-CRITIQUE-IF` | `CritiqueV1(critiqueId, targetRef, critiqueType, createdAt, iteration, comment?, constraintHints?)` | 必須キー削除 / review自動昇格 / 生ID保存 |
| `A1-REDIFF-IF` | `ReDiffV1(proposalId, basedOnIteration, diffOps[], traceKey, rationale?)` | `traceKey`欠落 / 非可逆差分 / SafeMode禁止操作の暗黙実行 |
| `A1-ATTR-IF` | `AttributionV1(reviewState, reviewedAt, reviewerRef, auditRecordedAt, reviewContext?, ownerRef?)` | `overridePolicy`緩和 / AIのみで`human_reviewed`昇格 |
| `A1-ERROR-IF` | `A1ErrorV1(errorCode, message, contractId, retryable, occurredAt)` | 未承認`errorCode`追加 / PII埋め込み |

- Artifact policy: `readOnly=true`, `mutationAllowed=false`, `changeRequestRoute=A1-CDC-only`。
- Snapshot validity: `schemaVersion=="1.0.0"` かつ `freezeContractId=="HIL-RS-02-A1-CONTRACT-FREEZE-v1"`。

### A2/A3 Fixed Reference Table（2026-04-30 / immutable handoff）

| Key | Fixed Value | Change Policy |
| --- | --- | --- |
| `freezeContractId` | `HIL-RS-02-A1-CONTRACT-FREEZE-v1` | immutable |
| `SnapshotID` | `SNAP-HIL-RS-02-A1-CONTRACT-FREEZE-v1` | immutable |
| `schemaVersion` | `1.0.0` | immutable |
| `overridePolicy` | `human_dual_control_only` | immutable |
| `contractLinkLocked` | `true` | immutable |
| `sharedResourceFreeze` | `true` | immutable |
| `safeModeDefault` | `ON` | immutable |
| `safeModeBoundary` | `SAFE_MODE_STRICT_ON` | immutable |
| `decisionQueueTransition` | `Pending -> Approved \| Pending -> Rejected` | immutable |
| `NoGo return path` | `issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md` | immutable |

Prohibited for A2/A3:
1. 追加ID・改名・派生判定式の導入。
2. `Pending` bypass。
3. 安全境界（safeMode/share-export）後退。

## 5) CDC（ADR要否）

- Context:
  - 本契約は `ADR-0026` / `ADR-0027` の下位実装契約。
- Decision:
  - 上位ADR改定が必要な要求は承認完了まで停止。
- Consequences:
  - A2/A3で契約再定義をしない。変更要求はA1へ差し戻し。


## 6.1) Stop Conditions（Contract Freeze）

次のいずれかを検知した場合は即停止し、推測で継続しない。

- `schemaVersion` 不一致（`1.0.0` 以外）
- `overridePolicy` 不一致（`human_dual_control_only` 以外）
- freeze flags 不一致（`contractLinkLocked/sharedResourceFreeze`）
- 未定義遷移（`Pending -> Approved|Rejected` 以外）
- Self-Correction 3回超過

停止報告テンプレ:
1. 失敗条件
2. 影響契約ID（`A1-CRITIQUE-IF` / `A1-REDIFF-IF` / `A1-ATTR-IF` / `A1-ERROR-IF`）
3. 必要な人間判断

## 6) Fail-safe

即停止条件:
- 修復3回超過
- 未承認決定の確定化
- 未定義競合検出

停止時報告:
1. 失敗条件
2. 競合ファイル
3. 必要承認者
4. Yes/No質問


## 7) Stream A Contract Freeze Pack v1.1（2026-04-16）

### Phase 1: Read Sync（Plan → Execute → Verify → Proceed）
- Plan: Freeze Pack要素（Contract IDs / `schemaVersion` / `overridePolicy` / SSOT）を抽出し、A1を唯一正本として照合する。
- Execute: `A1-CRITIQUE-IF | A1-REDIFF-IF | A1-ATTR-IF | A1-ERROR-IF` と固定値を再確認。

## 8) Frozen Contract Snapshot v1.2（2026-04-30 / Stream A Audit）

### Snapshot Declaration（参照固定）
- declaration: `THIS_VERSION_IS_FROZEN_FOR_ALL_DOWNSTREAM_LANES`
- snapshotId: `SNAP-HIL-RS-02-A1-CONTRACT-FREEZE-v1`
- referenceContractId: `HIL-RS-02-A1-CONTRACT-FREEZE-v1`
- schemaVersion: `1.0.0`
- apiSignatureSet:
  - `CritiqueV1(critiqueId, targetRef, critiqueType, createdAt, iteration, comment?, constraintHints?)`
  - `ReDiffV1(proposalId, basedOnIteration, diffOps[], traceKey, rationale?)`
  - `AttributionV1(reviewState, reviewedAt, reviewerRef, auditRecordedAt, reviewContext?, ownerRef?)`
  - `A1ErrorV1(errorCode, message, contractId, retryable, occurredAt)`

### Validation Rules（固定）
- `overridePolicy == "human_dual_control_only"`
- `contractLinkLocked == true`
- `sharedResourceFreeze == true`
- `safeModeDefault == "ON"`
- `safeModeBoundary == "SAFE_MODE_STRICT_ON"`
- `decisionQueueTransition == "Pending -> Approved | Pending -> Rejected"`
- `pendingDecisionQueueCount == 0` を満たさない場合は `NoGo`

### Rollback Conditions（停止/差戻し）
- rollback_trigger_1: `schemaVersion != "1.0.0"`
- rollback_trigger_2: `overridePolicy` の緩和要求（`human_dual_control_only` 以外）
- rollback_trigger_3: `Pending` bypass または未定義遷移の要求
- rollback_trigger_4: safeMode/share-export境界の後退要求
- rollback_target: `issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`

### Immutable Reference Links for Next Lanes（read-only）
1. `02_Architecture/hil_rs_01_a1_minimum_interface_contract.md`（本SSOT）
2. `01_Plans/issues/issue-HIL-RS-02-A1-governance-contract-hardening.md`（統治ゲート）
3. `01_Plans/issues/issue-HIL-RS-02-A2-frontend-reversible-synthesis-application.md`（A2参照先）
4. `01_Plans/issues/issue-HIL-RS-02-A3-operations-documentation-sync.md`（A3参照先）
- Verify: 想定差分は 0（契約ID衝突 0 / 語彙衝突 0 / 安全境界後退 0）。
- Proceed: 差分なしのため Freeze継続。

### Phase 2: Plan（Decision Queueの証跡分解）
未確定論点は次の「証跡が揃うまで `Pending` 維持」を固定する。

| Queue Topic | Required evidence to decide | Close condition |
| --- | --- | --- |
| Contract change request | 変更理由、影響契約ID、下流互換評価、A1 CDC記録 | `Approved` または `Rejected` |
| SafeMode regression request | 回帰有無の再現手順、既定ON維持可否、漏えい境界評価 | `Rejected` 以外はProceed不可 |
| Share/Export relaxation request | 漏えいリスク評価、監査ログ要件、代替案比較 | `Rejected` 以外はProceed不可 |

### Phase 3: ADR/Decision明文化（Context / Decision / Consequences）
- Context: A2/A3の前提を成果物依存ではなく固定仕様参照へ統一する必要がある。
- Decision: Freeze Pack v1.1 を参照専用で固定し、未承認項目は `Pending` のまま保持する。
- Consequences: 下流は再定義不可。変更要求は A1 CDC に集約される。

### Phase 4: Contract Freeze出力（read-only）
- Pack Version: `HIL-RS-02-A1-CONTRACT-FREEZE-v1.1`（reference-only）
- Immutable list:
  - `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
  - `contractIds=A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|A1-ERROR-IF`
  - `schemaVersion=1.0.0`
  - `overridePolicy=human_dual_control_only`
  - `contractLinkLocked=true`
  - `sharedResourceFreeze=true`
- Violation stop conditions:
  - immutable値の改変提案
  - `Pending -> Approved/Rejected` 以外の遷移
  - Self-Correction 3回超過

### Phase 5: Verify & Proceed
- Verify gate: `Go = (a1Status=="Done" && pendingDecisionQueueCount==0 && schemaVersion=="1.0.0" && overridePolicy=="human_dual_control_only" && contractLinkLocked==true && sharedResourceFreeze==true)`
- Publish mode: `readOnly=true` / `mutationAllowed=false`。
- 次の判断待ち: Decision Queueに証跡未充足の項目が1件でもあれば `Pending` 維持。

## 9) Stream A change envelope（type-definition only）

### Allowed updates（A1 scope）
- 許可対象は interface/type signature の明文化・不足注記・整合補足のみ。
- 追加可能なのは次の条件を全て満たす注記に限る。
  1. `schemaVersion=="1.0.0"` を維持する。
  2. `overridePolicy=="human_dual_control_only"` を維持する。
  3. 監査イベント最小4点セット（`query|bundle|proposal|apply`）を欠損させない。

### Prohibited updates（out of Stream A）
- 実装ロジック追加・アルゴリズム変更・runtime挙動変更。
- `contractIds` の追加/削除/改名。
- `Pending -> Approved|Rejected` 以外の遷移導入。
- SafeMode / share-export 境界の緩和。

### Verification rule
- docs-check と契約照合で不一致が出た場合は自己修復を最大3回まで許可し、4回目相当は即停止する。
