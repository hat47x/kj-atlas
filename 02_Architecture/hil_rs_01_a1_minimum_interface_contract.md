# HIL-RS-01-A1: Architecture最小I/F契約（Critique / ReDiff / Attribution / Error）

- Contract ID: `HIL-RS-01-A1`
- Status: Fixed (A1 Done)
- Owner: Architecture Owner
- Scope: `02_Architecture/`
- Upstream: `ADR-0026`, `ADR-0027`, `ADR-0001`, `00_Prompt/domain.md`

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
