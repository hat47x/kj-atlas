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

- Single Reference（SSOT）: `02_Architecture/hil_rs_01_a1_minimum_interface_contract.md`
- Contract IDs（固定）:
  - `A1-CRITIQUE-IF`
  - `A1-REDIFF-IF`
  - `A1-ATTR-IF`
  - `deterministicTieBreakOrder`

## 2. Contract matrix（必須 / 任意 / 禁止）

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

- 構造固定（schemaVersionの追加定義は行わない）
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

### 2.4 `deterministicTieBreakOrder`

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
  - `contractLinkLocked=true`
  - `sharedResourceFreeze=true`
- 明示禁止:
  - 契約本文を参照せず独自I/Fを追加すること
  - 契約変更をA2/A3で実施すること
  - SafeMode / share-exportの安全制約を後退させること
- エスカレーション規定:
  - 契約変更要求は必ずA1へ差し戻し。A2/A3で改訂しない。
