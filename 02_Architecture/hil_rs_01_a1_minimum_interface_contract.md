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
- `targetRef`: `card:` / `island:` / `cluster:` / `edge:` / `proposal:` で始まる不透明参照。現行UIの島は `island:` を正とし、既存文書互換の `cluster:` を残す。
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
- `before` / `after`: どちらもキーは必須。追加/削除など片側が存在しない操作では片側 `null` を許可する。ただし両方 `null` は非可逆として禁止する。
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
- `reviewedAt`: `human_reviewed` では ISO 8601。`unreviewed` では `null`。
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

## 7) Stream A contract freeze declaration（2026-05-09）

### Phase 1 Read（I/F unresolved inventory）
- Unresolved（Decision Queue）:
  1. `Approval Record=Pending`
  2. `HIL-RS-02-GOV-EXCEPTION-01=held`
- Confirmed frozen:
  - `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
  - `schemaVersion=1.0.0`
  - `overridePolicy=human_dual_control_only`
  - `safeModeDefault=ON`
  - `safeModeBoundary=SAFE_MODE_STRICT_ON`

### Phase 2 ADR（Context / Decision / Consequences）
- Context: A1契約はA2/A3の単一参照境界であり、未承認項目を確定化すると統治契約が破綻する。
- Decision:
  - A1最小I/Fの型・署名・判定条件・schemaVersionを凍結（read-only handoff）。
  - 未承認2件は確定扱いにせず、`Pending/held` のまま管理。
- Consequences:
  - `pendingDecisionQueueCount>0` の間、A2/A3 `Draft -> Open` は不許可。
  - 変更要求はA1 CDCへ戻す（下流で契約更新しない）。

### Phase 3 Freeze scope（A2/A3参照専用）
- Fixed Interfaces:
  - `A1-CRITIQUE-IF` / `A1-REDIFF-IF` / `A1-ATTR-IF` / `A1-ERROR-IF`
- Fixed Signatures:
  - `CritiqueV1(input)->CritiqueV1Result`
  - `ReDiffV1(input)->ReDiffV1Result`
  - `AttributionV1(input)->AttributionV1Result`
  - `A1ErrorV1(input)->A1ErrorV1Result`
- Fixed gate:
  - `A2A3_OPEN_ALLOWED = (a1Status=="Done" && pendingDecisionQueueCount==0 && freezeContractId=="HIL-RS-02-A1-CONTRACT-FREEZE-v1" && schemaVersion=="1.0.0" && overridePolicy=="human_dual_control_only" && contractLinkLocked==true && sharedResourceFreeze==true && safeModeDefault=="ON" && safeModeBoundary=="SAFE_MODE_STRICT_ON")`

### Phase 4 Handoff summary（read-only）
- Contract summary for downstream:
  - `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
  - `schemaVersion=1.0.0`
  - `overridePolicy=human_dual_control_only`
  - `safeModeDefault=ON`
  - `safeModeBoundary=SAFE_MODE_STRICT_ON`
  - `decisionQueueTransition=Pending -> Approved | Pending -> Rejected`
- Current decision: `Hold/Needs-decision`（承認待ち未解消）。
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
2. `01_Plans/issues/done/issue-HIL-RS-02-A1-governance-contract-hardening.md`（統治ゲート）
3. `01_Plans/issues/done/issue-HIL-RS-02-A2-frontend-reversible-synthesis-application.md`（A2参照先）
4. `01_Plans/issues/done/issue-HIL-RS-02-A3-operations-documentation-sync.md`（A3参照先）
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

## 9) Stream A A1 Contract Freeze Declaration（2026-05-03）

### Phase 1 Read Gate（未確定項目一覧）
- APIシグネチャ: `CritiqueV1 / ReDiffV1 / AttributionV1 / A1ErrorV1` を固定し、追加・改名・削除を禁止。
- 型: `schemaVersion="1.0.0"`、`overridePolicy="human_dual_control_only"`、`decisionQueueTransition="Pending -> Approved | Pending -> Rejected"` を固定。
- 判定条件: `A2A3_OPEN_ALLOWED`（本書 4章）以外の派生式を禁止。
- `contractLinkLocked=true` / `sharedResourceFreeze=true` / `safeModeDefault=ON` / `safeModeBoundary=SAFE_MODE_STRICT_ON` を固定。

### Phase 3 契約固定（A2/A3向け凍結対象）
- 変更凍結対象:
  1. `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
  2. `contractIds=A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|A1-ERROR-IF`
  3. `schemaVersion=1.0.0`
  4. `overridePolicy=human_dual_control_only`
  5. `NoGo return path=issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`
- deterministic inputs:
  - `pendingDecisionQueueCount`（整数）
  - `hasUndefinedContractChangeRequest`（boolean）
  - `hasSafeModeRegressionRequest`（boolean）
  - `hasShareExportLeakageRelaxationRequest`（boolean）
- acceptance checkpoints:
  - C1: freeze keys 差分0
  - C2: pending bypass 0件
  - C3: A1完了前の A2/A3 `Draft -> Open` 0件

### Phase 4 受け渡し（Lane B/C handoff）
- fixed interface list: `A1-CRITIQUE-IF`, `A1-REDIFF-IF`, `A1-ATTR-IF`, `A1-ERROR-IF`
- prohibited changes list:
  - Contract ID再定義
  - `schemaVersion`更新
  - `overridePolicy`緩和
  - SafeMode境界後退
  - `Pending` bypass
- mock assumptions list:
  - A2/A3 は mock-first で本契約を read-only 参照する。
  - 実装有無に関わらず Gate 判定は本書の式を唯一参照する。

### Phase 5 Verify & Publish（A1 DoD）
- 差分説明可能性: freeze keys / gate式 / NoGo return path の変更有無を必ず記録。
- 依存リンク: `ADR-0026` / `ADR-0027` / `ADR-0028` / `issue-HIL-RS-02-A1-governance-contract-hardening.md`。
- 停止条件: self-correction 3回超過、未承認確定化、未定義競合、allowlist外編集要求。

## 10) Stream A Contract Snapshot (read-only handoff, 2026-05-04)

### A1 freeze declaration（Contract Freeze）
- `freezeContractId="HIL-RS-02-A1-CONTRACT-FREEZE-v1"`
- `snapshotId="SNAP-HIL-RS-02-A1-CONTRACT-FREEZE-v1"`
- `schemaVersion="1.0.0"`
- `safeModeDefault="ON"`
- `safeModeBoundary="SAFE_MODE_STRICT_ON"`
- `overridePolicy="human_dual_control_only"`
- `contractLinkLocked=true`
- `sharedResourceFreeze=true`

### API signature freeze（変更禁止）
- `CritiqueV1(critiqueId, targetRef, critiqueType, createdAt, iteration, comment?, constraintHints?)`
- `ReDiffV1(proposalId, basedOnIteration, diffOps[], traceKey, rationale?)`
- `AttributionV1(reviewState, reviewedAt, reviewerRef, auditRecordedAt, reviewContext?, ownerRef?)`
- `A1ErrorV1(errorCode, message, contractId, retryable, occurredAt)`

### Gate freeze（A2/A3 unlock）
- `A2A3_OPEN_ALLOWED` は本書4章の固定式を唯一参照する。
- DecisionQueue 遷移は `Pending -> Approved | Pending -> Rejected` のみ許可。
- `NoGo return path="issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md"` を固定する。

### Verification log（A1 scope）
- Phase 1(Read): 未確定項目は `Approval Record` 未入力と `held` 1件のみ。
- Phase 2(ADR): 追加ADR不要（既存 ADR-0026/0027/0028 で十分）。
- Phase 3(Freeze): 固定キー差分 `0`。
- Phase 4(Handoff): read-only snapshot 発行済み。
- Phase 5(Verify): self-correction `0/3`、未承認が残るため Proceed は `Conditional`。


## 9) Stream A Verify Gate Snapshot（2026-05-06）

### Context
- 本スナップショットは A2/A3 開始前の最終ゲート確認を目的とする（contract freeze の再定義禁止）。

### Decision
- 以下を凍結参照として維持する。
  - `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
  - `schemaVersion=1.0.0`
  - `overridePolicy=human_dual_control_only`
  - `contractLinkLocked=true`
  - `sharedResourceFreeze=true`
  - `safeModeDefault=ON`
  - `safeModeBoundary=SAFE_MODE_STRICT_ON`

### Consequences
- ゲート判定は `Hold/Block` を維持。
- 理由:
  1. `Approval Record` が Pending（2者承認未完了）。
  2. `HIL-RS-02-GOV-EXCEPTION-01` が held。
  3. `pendingDecisionQueueCount==0` の監査証跡が未添付。
- A2/A3は本書の固定I/Fを read-only 参照し、変更要求は A1 CDC に差し戻す。

## 9) Stream A (Critical Path) Contract Freeze Pack v20260507

### Phase 1: Read（Plan → Execute → Verify → Proceed）
- Plan:
  - 対象: 本書（A1 SSOT）と `01_Plans/issues/done/issue-HIL-RS-02-A1-governance-contract-hardening.md` の契約値を比較。
  - AC（Read）:
    1. 固定キー（`freezeContractId` / `schemaVersion` / `overridePolicy` / `safeModeBoundary`）を抽出できる。
    2. Decision Queue遷移制約の差分有無を判定できる。
- Execute:
  - 差分抽出結果: 既存契約との差分は0件（未確定事項のみ管理対象）。
- Verify:
  - `Pending -> Execute` 禁止が両文書で維持されていることを確認。
- Proceed:
  - Read Gate通過。

### Phase 2: ADR/Decision明文化（Plan → Execute → Verify → Proceed）
- Plan:
  - 未確定点を確定値へ昇格せず、承認待ちIDを発行する。
- Execute:
  - Pending Decision IDs:
    - `PD-20260507-A1-001`: Approval Recordの証跡URL形式を `path-or-url` のみで固定するか。
    - `PD-20260507-A1-002`: `reviewerRef` の匿名化要件を正規表現で固定するか。
  - Context:
    - A2/A3で局所補完が起きるとI/Fドリフトが発生する。
  - Decision:
    - 未承認IDは `contract_snapshot_v20260507` に「pending」として記録し、確定扱いしない。
  - Consequences:
    - Pending ID解消までは既存固定I/F以外を追加禁止。
- Verify:
  - 承認待ちIDが「未確定」状態で記録されていることを確認。
- Proceed:
  - ADR Gate通過。

### Phase 3: 契約スナップショット固定（Plan → Execute → Verify → Proceed）
- Plan:
  - A2/A3参照用 read-only snapshot を作成する。
- Execute:
  - `contract_snapshot_v20260507` を発行（readOnly=true / mutationAllowed=false）。
  - 固定セット:
    - `freezeContractId=HIL-RS-02-A1-CONTRACT-FREEZE-v1`
    - `schemaVersion=1.0.0`
    - `overridePolicy=human_dual_control_only`
    - `safeModeBoundary=SAFE_MODE_STRICT_ON`
    - `decisionQueueTransition=Pending -> Approved | Pending -> Rejected`
    - `apiSignatureSet` は v1.2 と同一。
  - 禁止事項固定:
    1. `Pending` bypass
    2. `errorCode` の未承認追加
    3. safeMode/share-export 後退
- Verify:
  - snapshot値が本書の固定値と一致。
- Proceed:
  - Snapshot Gate通過。

### Phase 4: 受け渡し（Plan → Execute → Verify → Proceed）
- Plan:
  - 実装レーン向け凍結通知を明文化する。
- Execute:
  - 変更不可I/F:
    - `A1-CRITIQUE-IF` / `A1-REDIFF-IF` / `A1-ATTR-IF` / `A1-ERROR-IF`
  - 許容拡張:
    - `PD-20260507-A1-001/002` が Approved になった場合のみ A1 CDC経由で拡張審査。
  - エスカレーション条件:
    1. 固定キー不一致
    2. 未定義遷移検出
    3. Self-Correction 3回超過
  - 凍結宣言:
    - `freezeDeclaration=ACTIVE (2026-05-07 UTC)`
- Verify:
  - 実装レーンが参照すべき固定値・禁止事項・エスカレーション条件が明示されていることを確認。
- Proceed:
  - Stream A handoff 完了。


## 7) Stream A handoff manifest（2026-05-07 / contract-I/F freeze）

### 7.1 Machine-readable freeze manifest
```json
{
  "manifestVersion": "a1-freeze-manifest-2026-05-07",
  "freezeContractId": "HIL-RS-02-A1-CONTRACT-FREEZE-v1",
  "snapshotId": "SNAP-HIL-RS-02-A1-CONTRACT-FREEZE-v1",
  "schemaVersion": "1.0.0",
  "contractIds": ["A1-CRITIQUE-IF", "A1-REDIFF-IF", "A1-ATTR-IF", "A1-ERROR-IF"],
  "overridePolicy": "human_dual_control_only",
  "contractLinkLocked": true,
  "sharedResourceFreeze": true,
  "safeModeDefault": "ON",
  "safeModeBoundary": "SAFE_MODE_STRICT_ON",
  "decisionQueueTransition": ["Pending->Approved", "Pending->Rejected"],
  "a2a3ReferenceMode": "read_only",
  "destructiveChange": "forbidden"
}
```

### 7.2 B/C handoff constraints
- B/C（A2/A3）は本manifestを read-only 参照し、派生契約を再定義しない。
- 変更要求は `A1-CDC-only` ルートに差し戻す。
- 未解決項目（`Approval Record=Pending`, `HIL-RS-02-GOV-EXCEPTION-01=held`）が残る間は `NoGo/Hold` を維持する。


## 8) Stream A Freeze Pack（2026-05-17 / HIL-RS-CE0 contract freeze handoff）

### Phase 1 Read & Baseline
- Re-read completed: `issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md`, `issue-HIL-RS-01-next-phase-human-loop-reversible-synthesis.md`, `issue-HIL-RS-02-A1-governance-contract-hardening.md`, `issue-CE0-contract-freeze.md`, `ADR-0027`.
- Baseline delta: no fixed-key drift detected for `freezeContractId`, `contractIds`, `schemaVersion`, `overridePolicy`, `safeModeDefault`, `safeModeBoundary`.
- AC/DoD gap decision: no new gaps; unresolved items remain approval-related only.

### Phase 2 ADR freeze（Context / Decision / Consequences）
- Context: downstream redefinition risk remains non-zero until A1 gate is the single source of truth.
- Decision:
  - Keep A1 fixed values immutable.
  - Keep Decision Queue transitions fixed to `Pending -> Approved | Pending -> Rejected`.
  - Keep `A2A3_UNLOCK` as the sole open predicate.
- Consequences:
  - A2/A3 cannot transition `Draft -> Open` while queue pending exists.
  - Any contract redefinition request must return to A1 CDC/issue.

### Phase 3 Execute（contract lock only / no implementation）
- Contract lock scope is limited to interface/governance/stop-condition definition.
- Non-goal (explicit): frontend/backend/schema implementation start, dashboard edit, and non-allowlist document edits.

### Phase 4 Verify（self-check）
- Dependency transition rule check: `A1 before A2/A3 Open` enforced.
- Destructive diff check: no destructive mutation to frozen interface IDs/keys.
- Self-correction count: `0/3`.

### Phase 5 Proceed（Freeze Pack for downstream）

| Item | Frozen value | Change policy |
| --- | --- | --- |
| Freeze Pack ID | `HIL-RS-CE0-FREEZE-PACK-2026-05-17` | immutable |
| `freezeContractId` | `HIL-RS-02-A1-CONTRACT-FREEZE-v1` | immutable |
| `contractIds` | `A1-CRITIQUE-IF|A1-REDIFF-IF|A1-ATTR-IF|A1-ERROR-IF` | immutable |
| `schemaVersion` | `1.0.0` | immutable |
| `overridePolicy` | `human_dual_control_only` | immutable |
| `safeModeDefault` | `ON` | immutable |
| `safeModeBoundary` | `SAFE_MODE_STRICT_ON` | immutable |
| Decision Queue transition | `Pending -> Approved | Pending -> Rejected` | immutable |
| Unlock rule | `A2A3_UNLOCK = (a1Status=="Done" && pendingDecisionQueueCount==0)` | immutable |
| NoGo return path | `issue-HIL-RS-01-A1-architecture-minimum-interface-contract.md` | immutable |

#### Downstream contract I/F table（input / output / failure / audit event）

| Interface | Input | Output | Failure | Audit event |
| --- | --- | --- | --- | --- |
| `A1-CRITIQUE-IF` | `critiqueId,targetRef,critiqueType,createdAt,iteration` | critique proposal record | `A1_REQUIRED_FIELD_MISSING` / `A1_PII_POLICY_VIOLATION` | `query`,`proposal` |
| `A1-REDIFF-IF` | `proposalId,basedOnIteration,diffOps[],traceKey` | reversible diff proposal | `A1_TRACE_KEY_MISSING` / non-reversible diff reject | `bundle`,`proposal` |
| `A1-ATTR-IF` | `reviewState,reviewedAt,reviewerRef,auditRecordedAt` | attribution state update proposal | `A1_OVERRIDE_POLICY_VIOLATION` | `proposal`,`apply` |
| `A1-ERROR-IF` | `errorCode,message,contractId,retryable,occurredAt` | structured contract error | invalid enum / PII in message | `query`,`bundle`,`proposal`,`apply` |

#### Re-open conditions
1. Human dual-approval evidence completed (`approved_by`, `approved_at`, `evidence`).
2. `pendingDecisionQueueCount==0` confirmed.
3. No fixed-key drift and no safeMode regression requests.

## 9) Stream A Contract Pack v3（2026-05-20 / critical-path refresh）

### Phase 1: Read（再読差分確認）
- Re-read targets: `ADR-0026`, `ADR-0027`, `02_Architecture/hil_rs_01_a1_minimum_interface_contract.md`.
- Delta check result: fixed keys and transition constraints remain unchanged (`diff=0`)。
- Remaining unresolved approvals are kept as pending; no implicit confirmation performed.

### Phase 2: ADR確定（Context / Decision / Consequences）
#### Context
- Downstream streams require a stable and singular contract reference to prevent contract drift and unauthorized unlock.

#### Decision
- Freeze the contract pack as read-only reference with the following immutable set:
  - API signatures: `A1-CRITIQUE-IF`, `A1-REDIFF-IF`, `A1-ATTR-IF`, `A1-ERROR-IF`
  - Data type baseline: `CritiqueV1`, `ReDiffV1`, `AttributionV1`, `A1ErrorV1`
  - `schemaVersion=1.0.0`
  - `overridePolicy=human_dual_control_only`
  - Feature-flag equivalent governance keys: `contractLinkLocked=true`, `sharedResourceFreeze=true`, `safeModeDefault=ON`, `safeModeBoundary=SAFE_MODE_STRICT_ON`

#### Consequences
- Pending items (`Approval Record`, governance exception holds) remain explicit blockers; downstream cannot treat them as approved.
- Any mutation request must be routed to A1 CDC and must not be implemented in downstream streams.

### Phase 3: Contract Pack 発行（参照専用）
```text
Contract Pack v3
- Pack ID: HIL-RS-CE0-CONTRACT-PACK-v3
- SSOT: 02_Architecture/hil_rs_01_a1_minimum_interface_contract.md
- API signatures frozen: A1-CRITIQUE-IF | A1-REDIFF-IF | A1-ATTR-IF | A1-ERROR-IF
- Data types frozen: CritiqueV1 | ReDiffV1 | AttributionV1 | A1ErrorV1
- schemaVersion: 1.0.0
- Feature flags / governance keys frozen:
  - contractLinkLocked=true
  - sharedResourceFreeze=true
  - safeModeDefault=ON
  - safeModeBoundary=SAFE_MODE_STRICT_ON
  - overridePolicy=human_dual_control_only
- Transition rule frozen:
  - DecisionQueue: Pending -> Approved | Pending -> Rejected
  - Unlock: A2A3 only when (a1Status==Done && pendingDecisionQueueCount==0)
```

### Phase 4: Verify（AC/DoD自己検証）
- AC-1: Context / Decision / Consequences explicitly documented. ✅
- AC-2: API signature / data type / schemaVersion / feature-flag equivalents frozen. ✅
- AC-3: Unapproved items are explicitly isolated as pending. ✅
- AC-4: No implementation scope changes performed. ✅
- Self-correction count: `0/3`.

### Phase 5: Proceed/Stop
- Gate result: **STOP (Conditional / approval pending)**。
- Reason: unresolved approval artifacts remain (`approved_by`, `approved_at`, `evidence` not complete).
- Policy: no speculative implementation or downstream unlock.
