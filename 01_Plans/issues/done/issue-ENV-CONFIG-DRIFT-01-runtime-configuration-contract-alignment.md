# Issue Draft: ENV-CONFIG-DRIFT-01 Runtime configuration contract alignment

- Type: Bug
- Status: Done
- Source Issue: N/A
- Priority: P2
- Owner: Codex (runtime-configuration steward; accountable runtime owner remains Platform Operator)
- Scope: `02_Architecture/`, `03_Implement/backend/`, `03_Implement/frontend/`, `03_Implement/deploy/`, `04_Documentation/`
- Related Backlog: `ENV-ARCH-01`
- Related ADR/Spec: `01_Plans/adr/ADR-0021-env-var-global-prefix-migration.md`, `01_Plans/adr/ADR-0029-third-party-runtime-env-boundary.md`, `02_Architecture/runtime_parameter_registry.md`, `03_Implement/frontend/src/api/client.ts`, `03_Implement/frontend/Dockerfile`, `03_Implement/deploy/docker-compose.yml`, `03_Implement/backend/src/kj_atlas_api/settings.py`, `03_Implement/backend/src/kj_atlas_api/access_control.py`
- Dependencies: N/A
- Expected verification level: `integration`

## Requirement meta I/F（共通キー）

- RequirementID: ENV-CONFIG-DRIFT-01
- RequirementStatement: public runtime configuration keys are exhaustively documented and every public environment variable starts with `KJ_ATLAS_`.
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=ADR-0021 and runtime registry are accepted; 操作=Compose build, backend settings load, frontend build, and docs-check are executed; 期待結果=only `KJ_ATLAS_*` keys are exposed to users and all accepted keys are documented; 除外=changing SafeMode/share/export policy.
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: public-exposure

## 1) 課題 / Problem statement

- The project policy now requires all public environment variables to use `KJ_ATLAS_` without exception.
- User-facing docs must list every public environment variable, not only the major settings.
- Frontend build configuration previously exposed Vite-style keys to users, and Compose previously exposed non-prefixed port/database keys.
- Backend settings and the runtime registry previously diverged on `KJ_ATLAS_CE4_STUB_UNRESOLVED_CONTRACTS`.
- Access control behavior still has a policy decision point: `external_http` without endpoint currently falls back to `noop`. Changing that to fail-fast may require ADR because it changes the accepted availability/security trade-off.
- Compose still has to pass values into a third-party PostgreSQL container using that image's required internal names. `ADR-0029` defines the accepted adapter boundary. If the project interprets "no exceptions" as applying to every process environment inside third-party containers, the deployment design needs a replacement implementation.

## 2) 背景 / Context

- ADR-0021 fixes the global prefix policy and rejects legacy unprefixed backend keys.
- The latest documentation work aligns the public docs, frontend build, Compose input keys, and backend settings with the `KJ_ATLAS_*` contract.
- `runtime_parameter_registry.md` is the source of truth. `04_Documentation/configuration.md` must mirror the full public key set.

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: configuration drift makes self-hosted evaluation harder and raises setup risk.
- 安全（THREAT_MODEL / SafeMode）: implicit compatibility keys can hide unintended external routing or access-control weakening.
- 企業・行政要件（enterprise_architecture）: strict deployments need auditable, explicit configuration contracts.
- 後方互換（schemas）: removing public compatibility keys is acceptable here because the requirement says there are no prefix exceptions.

## 4) 提案する解決策 / Proposed solution

- Treat `KJ_ATLAS_*` as the only public environment-variable namespace.
- Keep third-party or build-tool-specific names as internal implementation details only, never as user-facing settings.
- Ensure `runtime_parameter_registry.md` and `04_Documentation/configuration.md` list the same public key set.
- Keep backend `Settings` validation aligned with the registry, including `KJ_ATLAS_CE4_STUB_UNRESOLVED_CONTRACTS`.
- Validate access-control adapter and fail-safe enum values in settings.
- Keep `ADR-0029` as the accepted decision record for the third-party container environment boundary.
- Create another ADR only if the team decides to change accepted runtime behavior, especially `external_http` missing-endpoint fallback or a stricter no-vendor-env deployment model.

Non-goals:

- Do not change SafeMode defaults.
- Do not redesign RBAC/ABAC semantics.
- Do not expose non-`KJ_ATLAS_*` compatibility keys in public docs.

## 5) 受入条件 / Acceptance criteria

- [x] `runtime_parameter_registry.md` lists every public environment variable.
- [x] `04_Documentation/configuration.md` lists every public environment variable.
- [x] Public docs and run guides do not instruct users to set non-`KJ_ATLAS_*` environment variables.
- [x] Frontend build can be configured with `KJ_ATLAS_FRONTEND_API_BASE`.
- [x] Docker Compose public inputs use `KJ_ATLAS_WEB_PORT`, `KJ_ATLAS_POSTGRES_DB`, `KJ_ATLAS_POSTGRES_USER`, `KJ_ATLAS_POSTGRES_PASSWORD`, and `KJ_ATLAS_FRONTEND_API_BASE`.
- [x] Third-party container environment boundaries are resolved through `ADR-0029`; replacing the PostgreSQL deployment path is only required if the team later adopts a stricter no-vendor-env policy.
- [x] Backend settings and `runtime_parameter_registry.md` agree on all `KJ_ATLAS_CE4_*` keys, including legacy-key rejection behavior.
- [x] Invalid access-control adapter and fail-safe values fail validation or are explicitly justified by ADR.
- [x] `external_http` without endpoint is either fail-fast or explicitly retained by ADR with user-facing warning text.
- [x] Integration-level verification covers Compose build args, backend settings load, frontend build, and relevant docs-checks (Docker execution is recorded as environment-limited when unavailable).

## 6) 実装タスク分解 / Task breakdown

- [x] T1: Reconcile frontend API base across Dockerfile, Compose, Vite config, `client.ts`, and docs.
- [x] T2: Reconcile Compose public input keys with the `KJ_ATLAS_*` contract.
- [x] T3: Reconcile CE4 runtime keys across registry, settings, legacy-key rejection, and tests.
- [x] T4: Add settings validation for access-control adapter and fail-safe mode.
- [x] T5: Resolve the third-party container boundary through `ADR-0029`; replacement of the PostgreSQL deployment path is only required if stricter no-vendor-env policy is later adopted.
- [x] T6: Update 02/03/04 docs after implementation alignment.
- [x] T7: Add or update tests for the agreed runtime contract.

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `python 01_Plans/issues/validate_active_issue_memos.py`
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `pytest 03_Implement/backend/tests/test_settings_env_prefix_migration.py`
  - `cd 03_Implement/frontend && npm run typecheck && npm run test`
  - `cd 03_Implement/deploy && docker compose config`
  - `rg -n -P "<non-prefixed-public-env-key-pattern>" 02_Architecture 03_Implement 04_Documentation`
- 期待結果:
  - active issue metadata validates or only known unrelated drift remains.
  - settings tests cover canonical and legacy key behavior.
  - frontend build reads `KJ_ATLAS_FRONTEND_API_BASE`.
  - public docs and registry no longer expose non-`KJ_ATLAS_*` settings.
- 未実施時の理由・代替検証:
  - Docker unavailable environments may substitute `docker compose config` plus Dockerfile diff review, but final Done requires a real build.

## 8) 代替案 / Alternatives considered

- Keep Vite-style or Compose-specific public keys:
  - Rejected because the accepted requirement says there are no prefix exceptions.
- Document only major variables:
  - Rejected because operators need the full supported configuration surface.

## 9) リスクとロールバック / Risks & rollback

- 失敗モード: existing local users who set old public keys need to rename them.
- 影響範囲: Docker Compose startup, frontend API routing, backend settings validation, enterprise access-control deployments.
- ロールバック手順: restore previous key mapping only with an explicit ADR or migration decision; do not silently reintroduce public non-`KJ_ATLAS_*` keys.

## 10) Additional context

- Related issue: `01_Plans/issues/issue-ENV-ARCH-01-global-env-prefix-migration.md`
- ADR化が必要になる条件:
  - changing the accepted `ADR-0029` adapter boundary into a stricter no-vendor-env deployment redesign.
  - changing `external_http` missing-endpoint behavior from current `noop` fallback to fail-fast.



### Stream B contract split (2026-05-18)

- Public contract keys are frozen to the SSOT set in `02_Architecture/runtime_parameter_registry.md` (`KJ_ATLAS_*` only).
- Vendor names are allowed only as private adapter names at implementation boundaries (Compose third-party service internals).
- "Strict interpretation" (ban non-`KJ_ATLAS_*` in every process env) is tracked as a separate architecture change, not as a drift-fix interpretation of this issue.

## 11) Stream C execution snapshot (2026-05-17)

### Public key extraction result

- `02_Architecture/runtime_parameter_registry.md` and `04_Documentation/configuration.md` expose the same 42 public keys (`KJ_ATLAS_*` only).
- Compose/public runtime inputs are constrained to `KJ_ATLAS_WEB_PORT`, `KJ_ATLAS_POSTGRES_DB`, `KJ_ATLAS_POSTGRES_USER`, `KJ_ATLAS_POSTGRES_PASSWORD`, `KJ_ATLAS_FRONTEND_API_BASE`, and backend runtime keys remain `KJ_ATLAS_*`.

### Contract boundary result

- Third-party env names are limited to private adapter use inside the PostgreSQL service boundary and are not part of the public contract.
- ADR-0029 now records C/D/C (Confirmed / Decided / Clarified pending) for this boundary.

### Pending queue (non-blocking for this stream)

1. Governance decision: whether to require zero non-`KJ_ATLAS_*` names in every process environment, including third-party containers.
2. Governance decision: whether `external_http` without endpoint should remain fallback/noop or become fail-fast by default.

### Stream C stop check (Fail-safe)

- No conflict detected between public contract and internal adapter boundary under current ADR-0029 interpretation.
- No SafeMode/share/export policy change in this stream.
- Self-correction threshold not exceeded.

## 15) Stream F execution snapshot (2026-05-20)

### Scope lock

- Stream F は `runtime_parameter_registry.md` と関連運用文書（configuration / security operational guidelines）のみを対象にし、実装コード・deploy定義は変更しない。

### Execute result（naming / defaults / compatibility）

- Naming: 公開キーは引き続き `KJ_ATLAS_*` のみを許容し、追加の互換キー導入は行わない。
- Defaults: `KJ_ATLAS_ALLOW_JIT_PROVISIONING`（実装既定 `true`）と enterprise 推奨値（`false`）の差を registry と運用文書で明示した。
- Compatibility: `KJ_ATLAS_ACCESS_CONTROL_FAIL_SAFE_MODE` の既定値と enterprise 運用時の選択肢（`read_only`/`deny`）を文書間で同期した。

### Verify summary

- `runtime_parameter_registry.md` / `configuration.md` / `security_operational_guidelines.md` の profile 記述に矛盾がないことを差分確認で検証。
- SafeMode/share/export の既定ポリシー変更はなし。


## 12) Stream D execution snapshot (2026-05-17)

### Runtime parameter contract alignment result

- `KJ_ATLAS_FRONTEND_API_BASE` の公開契約を「path（`/` 始まり）」へ明文化し、`runtime_parameter_registry.md` と `deployment.md` の記述を一致させた。
- frontend env 読み取り層（`src/api/client.ts`）で不正値（空文字、`/` 非始まり）を `/api` へ正規化し、実行時契約ドリフトを封じた。

### Verification summary

- Frontend typecheck/test により API client の変更が既存型・振る舞いと整合することを確認。
- backend/compose の公開キー面には追加ドリフトを検出しなかった（`KJ_ATLAS_*` 契約維持）。

## 13) Stream E execution snapshot (2026-05-17)

### Phase progression record

- Phase 1 Read: `AGENTS.md` Read Order と対象契約（`runtime_parameter_registry.md`）を再確認し、Stream E の編集許可スコープを固定。
- Phase 2 ADR: `ADR-0021`（global prefix policy）と `ADR-0029`（third-party runtime env boundary）を前提契約として採用し、新規ADR追加は不要と判断。
- Phase 3 Plan: 本 issue を単一正本として、命名・既定値・境界の整合状態を「公開契約面」と「内部 adapter 面」に分けて検証する方針を確定。
- Phase 4 Execute: issue 本文へ Stream E の独立検証結果を追記し、他ストリーム依存を増やさない形で整理。
- Phase 5 Verify: 公開キー契約（`KJ_ATLAS_*` のみ）と `KJ_ATLAS_FRONTEND_API_BASE` の path 契約が維持されることを文書整合で確認。
- Phase 6 Proceed/Stop: Stream E のミッション範囲では追加実装なしで Stop。残論点は governance queue に留め、設計変更は起票条件を満たした場合のみ進行。

### Alignment result (naming / defaults / boundaries)

- Naming: 公開環境変数の命名は `KJ_ATLAS_*` に統一され、例外は third-party container 内部名に限定される（公開契約外）。
- Defaults: `runtime_parameter_registry.md` の既定値記述と issue 側の受入意図に矛盾なし（特に `KJ_ATLAS_FRONTEND_API_BASE=/api` と CE4/ACl 系の安全側既定）。
- Boundaries: 利用者向け契約（公開キー）と内部実装変換（vendor/env adapter）の境界が `ADR-0029` 前提で一貫。

### Stream E pending queue (governance-only)

1. third-party container の内部環境名を将来的に完全排除するか（公開契約外で許容継続か）を governance で最終決定する。
2. `external_http` endpoint 未設定時の `noop` fallback を fail-fast へ変更するかを ADR レベルで最終決定する。


## 14) Stream J execution snapshot (2026-05-18)

### Plan → Execute → Verify → Proceed

#### Phase 1: Read同期（棚卸し）

- 対象SSOT（`runtime_parameter_registry.md`）と deploy 定義（`deployment.md` / `docker-compose.yml` / `nginx.conf`）を再読し、公開キー・既定値・適用範囲を棚卸しした。
- 公開契約キーは `KJ_ATLAS_*` のみで一致していることを確認した。
- `docker-compose.yml` の `POSTGRES_*` は third-party container 内部 adapter 名であり、公開契約外であることを再確認した（`ADR-0029` 前提）。

#### Phase 2: ADR要素明文化（Context / Decision / Consequences）

- Context: ENV prefix migration は backend で互換なし一括移行済み、deploy 層は公開キー `KJ_ATLAS_*` と内部 adapter 名（PostgreSQL）を分離して運用している。
- Decision: 現時点では runtime/deploy の実装変更は不要とし、契約ドリフト防止の運用手順（切替条件・監視・ロールバック）を issue/architecture に固定する。
- Consequences: 破壊的変更（例: `external_http` fail-fast 既定化、vendor env 完全排除）は本 issue では実施せず、ADR 起票条件を満たした場合のみ進行する。

#### Phase 3: 契約固定（SSOT基準化 + 整合マトリクス）

整合マトリクス（2026-05-18時点）:

| Public key | Registry | Deployment policy | Compose | Status |
| --- | --- | --- | --- | --- |
| `KJ_ATLAS_WEB_PORT` | Defined (`8080`) | Defined | Used in `web.ports` | Aligned |
| `KJ_ATLAS_POSTGRES_DB` | Defined (`kj_atlas`) | Defined | Mapped to `db.POSTGRES_DB` | Aligned |
| `KJ_ATLAS_POSTGRES_USER` | Defined (`kj_atlas`) | Defined | Mapped to `db.POSTGRES_USER` | Aligned |
| `KJ_ATLAS_POSTGRES_PASSWORD` | Defined (`kj_atlas`) | Defined | Mapped to `db.POSTGRES_PASSWORD` | Aligned |
| `KJ_ATLAS_FRONTEND_API_BASE` | Defined (`/api`) | Defined | Used in `web.build.args` | Aligned |
| `KJ_ATLAS_DATABASE_URL` | Defined | Defined | Used in `api.environment` | Aligned |
| `KJ_ATLAS_LLM_PROVIDER` | Defined (`none`) | Defined | Used in `api.environment` | Aligned |

## 15) Stream E execution snapshot (2026-05-20)

### Plan → Execute → Verify → Proceed（Phase gate record）

#### Phase 1 Read（再読・抽出）

- SSOT と ADR を再読し、公開契約キー・既定値・適用境界の抽出対象を固定した。対象: `runtime_parameter_registry.md`, `ADR-0021`, `ADR-0029`。
- 実装参照先（read-only）として `settings.py` / `docker-compose.yml` / frontend `Dockerfile` / `client.ts` / `access_control.py` を比較対象に設定した。

#### Phase 2 Plan（AC/DoD 整理）

- 優先順位を以下に固定:
  1. **セキュリティ影響キー**: `KJ_ATLAS_ACCESS_CONTROL_*`, `KJ_ATLAS_AUDIT_*`, `KJ_ATLAS_API_KEY`
  2. **起動不能リスクキー**: `KJ_ATLAS_DATABASE_URL`, `KJ_ATLAS_LLM_PROVIDER`, `KJ_ATLAS_POSTGRES_*`
  3. **運用観測系キー**: profile 推奨値・adapter boundary の運用ルール
- 本 issue の DoD を「公開契約（命名/既定値/境界）が文書正本で一意に読めること」に限定し、実装変更は非目標として維持した。

#### Phase 3 ADR 明文化（追加 ADR 要否判定）

- 追加 ADR は **不要** と判断。
- 理由: 命名規約は `ADR-0021` で Accepted、third-party 境界は `ADR-0029` で Accepted。今回の残作業は「差分可視化と契約固定」であり、意思決定自体は既存 ADR で充足するため。

#### Phase 4 Execute（差分可視化と契約固定）

実装参照（read-only）とのドリフト確認表（2026-05-20時点）:

| Contract topic | SSOT / ADR expectation | Implementation reference (read-only) | Drift |
| --- | --- | --- | --- |
| Public naming | Public key は `KJ_ATLAS_*` のみ | backend settings aliases は `KJ_ATLAS_*` のみ、legacy key は reject | None |
| Legacy compatibility | 旧キー互換なし（fail-safe） | `LEGACY_ENV_KEYS` 検知時に `ValueError` | None |
| Frontend API base key | `KJ_ATLAS_FRONTEND_API_BASE`（default `/api`、path契約） | Dockerfile ARG/ENV と `client.ts` の `/api` fallback 正規化 | None |
| Compose public inputs | 利用者入力は `KJ_ATLAS_*` | `web/api/db` の公開入力は `KJ_ATLAS_*` | None |
| Vendor adapter boundary | `POSTGRES_*` は private adapter（公開契約外） | `db.environment` 内のみ `POSTGRES_*` に写像 | None |
| Access-control enum boundary | adapter=`noop/mock/external_http`, fail-safe=`read_only/deny` | settings validator で列挙値を fail-fast 検証 | None |
| `external_http` endpoint absence | governance pending（現挙動を ADR で明示継続） | `external_http` 未設定時 fail-fast 既定化は未導入 | **Pending by design** |

#### Phase 5 Verify（AC/DoD 照合）

- Naming（`KJ_ATLAS_*` only）: **Pass**
- Defaults（registry と実装既定値整合）: **Pass**
- Boundary（public vs private adapter 分離）: **Pass**
- Governance pending の切り分け: **Pass**（`external_http` endpoint 未設定時の fail-fast 化は別決定として維持）
- 自己修復回数: 0/3（停止条件未到達）

#### Phase 6 Proceed（完了/未完了/保留）

**完了**
- ENV-CONFIG-DRIFT-01 の計画・仕様レベルで、命名/既定値/適用境界を単一契約として再固定。
- 実装参照との差分を可視化し、現時点ドリフトが「なし（または意図的保留）」であることを記録。

**未完了（この stream では非実施）**
- 実装コード変更（非目標のため未実施）。

**保留（governance-only）**
1. `external_http` endpoint 未設定時に `noop` fallback を廃止し fail-fast を既定化するか。
2. third-party container 内部を含む「全 process env で非 `KJ_ATLAS_*` 禁止」を採用するか（採用時は deployment 再設計が前提）。

### Stream E fail-safe stop check

- `03_Implement/**` は未編集（禁止事項遵守）。
- ENV 以外 issue は未編集（禁止事項遵守）。
- 他ストリーム依存が必須化する変更は未着手。

補足:
- `nginx.conf` は固定ルーティング (`/api` → `api:8000`) のみを担い、公開 env key を増やしていない。
- Compose 内 `POSTGRES_*` は内部変換先であり、利用者入力は `KJ_ATLAS_POSTGRES_*` だけを維持する。

#### Phase 4: Execute（Issue AC/DoD更新）

- 本 issue に Stream J の同期結果と運用手順を追記し、環境依存の破壊的変更を避けた。
- 実装ファイル変更は不要（既存契約が一致）と判断した。

#### Phase 5: Verify（契約一致 / 後方互換 / 自己修復）

- Registry ↔ Deployment ↔ Compose の key/default/purpose が一致していることを文書ベースで確認した。
- 後方互換は「backend 互換なし」「frontend key は `KJ_ATLAS_FRONTEND_API_BASE` 正規」を前提に逸脱なし。
- Self-heal policy（max 3）: 今回は不一致検知 0 件のため修復ループ未使用。

#### Phase 6: Proceed（切替 / ロールバック / 監視）

- 切替手順:
  1. 運用者が設定する env を `KJ_ATLAS_*` のみに限定する。
  2. Compose 起動前に `KJ_ATLAS_POSTGRES_*` と `KJ_ATLAS_DATABASE_URL` の整合を確認する。
  3. frontend build では `KJ_ATLAS_FRONTEND_API_BASE` を `/` 始まり path のみで設定する。
- ロールバック手順:
  1. 新規設定投入後に起動不全が発生した場合、直前の `KJ_ATLAS_*` 設定セットへ復元する。
  2. 旧キー復活は行わず、registry の契約値へ修正して再展開する。
- 監視ポイント:
  - Compose config 生成時に `KJ_ATLAS_*` 以外の公開キーが runbook/ops に混入していないこと。
  - `KJ_ATLAS_FRONTEND_API_BASE` が不正値（空や `/` 非始まり）で運用されていないこと。
  - third-party adapter 境界（`POSTGRES_*`）が公開契約へ漏れていないこと。

### Stream J stop check (Fail-safe)

- 3回超過修復: 未該当。
- 既存運用停止リスク: 重大な新規リスク追加なし（変更は契約同期のみ）。
- 不明な環境依存: 新規導入なし。
- 判定: **Proceed（本 stream scope で完了）**。

## 15) Stream E re-validation snapshot (2026-05-18)

### Phase 1 Read（再読）

- `AGENTS.md` の Read Order と Stream E の編集境界を再確認した。
- SSOT として `02_Architecture/runtime_parameter_registry.md`、公開運用文書として `04_Documentation/configuration.md` を再読した。

### Phase 2 ADR（Context / Decision / Consequences）

- Context: 公開キー契約は `KJ_ATLAS_*` 固定、内部 adapter 境界は `ADR-0029` で管理される。
- Decision: Stream E では契約ドリフト検証に限定し、仕様変更や新規 ADR 起票は行わない。
- Consequences: 既定値不一致・prefix 競合・registry/doc 不整合があれば Stop する前提を維持する。

### Phase 3 Plan（AC / DoD）

- AC-1: 命名が `KJ_ATLAS_*` 公開契約に一致すること。
- AC-2: 既定値が registry と configuration で一致すること。
- AC-3: 公開契約と内部 adapter 境界が混線していないこと。
- DoD: ドリフト 0 件、または governance 論点として隔離済みであること。

### Phase 4 Execute（命名・既定値・prefix整合）

- 命名整合を確認: 公開キーは `KJ_ATLAS_*` のみ。
- 既定値整合を確認: `KJ_ATLAS_FRONTEND_API_BASE=/api`、`KJ_ATLAS_WEB_PORT=8080`、`KJ_ATLAS_LLM_PROVIDER=none` 等が一致。
- 境界整合を確認: `POSTGRES_*` は third-party container 内部名としてのみ扱い、公開契約外で維持。

### Phase 5 Verify（lint/整合チェック・自己修復3回）

- 文書差分と整合チェックで、prefix 競合・既定値不一致・registry/doc 不整合の新規発生なし。
- 自己修復ループ（最大3回）は未使用（不一致検知 0 件）。

### Phase 6 Proceed/Stop

- 判定: **Proceed（Stream E scope で完了）**。
- Stop 条件評価: 解消不能な不一致は未検出。
- 残課題: `external_http` endpoint 未設定時の fail-fast 化可否、および third-party 内部名完全排除可否は governance/ADR 論点として継続。

## 16) Stream E completion snapshot (2026-05-19)

### Phase-based execution (Read → Plan → Execute → Verify → Proceed)

- Read: AC/Validation と SSOT（`02_Architecture/runtime_parameter_registry.md`）を再確認し、編集対象を runtime registry と issue メモに限定。
- Plan: DoD を「命名統一」「drift差分解消」「profile 運用判断基準の明文化」に固定。
- Execute: runtime registry に Profile selection criteria と Drift check gates を追加し、命名・既定値・境界の判定軸を明示。
- Verify: 公開契約キーが `KJ_ATLAS_*` のみであること、profile 表と新設判断基準が矛盾しないことを文書差分で確認。
- Proceed: 実装コードや認証契約には波及させず、governance-only pending（strict interpretation / external_http fail-fast）は未確定キューのまま維持。

### Stream E deliverables

1. Runtime profiles の選択条件を文書化（`local-dev` / `evaluation` / `enterprise-production`）。
2. Drift check gates（命名・既定値・境界・プロファイル更新同時性）を SSOT 側へ追加。
3. 変更は docs 範囲に限定し、SafeMode/share/export の既定や運用境界は不変更。

## 16) Stream E update (2026-05-19): Env gate hardening

### Phase 1: Read
- `runtime_parameter_registry.md` / `configuration.md` / compose 契約境界の既存定義を再確認し、公開契約と内部adapterを分離して評価した。

### Phase 2: ゲート定義（E1-E3）
- **E1 Public key contract**: 公開文書・runbookに非 `KJ_ATLAS_*` を公開設定として記載しない。
- **E2 Runtime validation**: backend settings が無効値（adapter/fail-safe/endpoint）を検出し、許容時は ADR 根拠を要求。
- **E3 Compose consistency**: `KJ_ATLAS_*` 入力と compose 展開結果が一致し、vendor env 名は private boundary に閉じる。

### Phase 3: 検証設計
- 必須テストセット:
  - issue validator
  - backend settings env tests
  - frontend typecheck/tests
  - `docker compose config`
  - docs key-drift search
- 失敗時判断:
  - Blocker: 公開契約キー逸脱、設定値検証欠落、compose 展開破綻。
  - Major: 文書整合欠落（ただし即時修正可能）。
  - Minor: 注釈不足・説明順序。

### Phase 4: 監査テンプレ
- Env判定ログ必須項目:
  - Checked keys set hash（キー集合の比較結果）
  - Validation failure sample
  - ADR reference（例外時のみ）
  - Escalation issue + owner + due date

### Phase 5: 反映
- 本Issueを env drift の戻し先として維持。
- 破壊的判断（vendor env 完全排除 / external_http fail-fast 既定化）は本Issueで確定せず、ADR起票条件を維持。

### Fail-safe
- 判定に必要な契約正本が不整合のときは進行停止し、先に SSOT 修復を要求する。

## 17) Stream E execution snapshot (2026-05-19)

### Phase 1) Read

- `runtime_parameter_registry.md` を再読し、命名/prefix/profile と公開契約境界（public vs private adapter）を再確認した。
- `issue-ENV-ARCH-01` の「互換期間なし一括移行」と `issue-ENV-PROFILE-01` の profile guidance 前提を再確認した。

### Phase 2) Plan

- 互換維持方針:
  - backend 公開キーは `KJ_ATLAS_*` 単独契約を維持する。
  - vendor 内部 env 名は private adapter としてのみ許容し、公開契約へ昇格しない。
- 移行ステップ提案:
  1. SSOT（runtime registry）更新
  2. issue 側の execution snapshot 追記
  3. drift prevention checklist の更新
  4. 非互換が必要なら Stopper 発動（ADR/承認待ち）

### Phase 3) Execute

- `runtime_parameter_registry.md` に drift recurrence prevention checklist を追記した。
- 本 issue に Stream E（2026-05-19）の実行ログを追記し、ENV-CONFIG/ENV-ARCH/ENV-PROFILE の整合状態を明文化した。

### Phase 4) Verify

- drift 再発防止の確認観点を registry 側チェックリストへ固定した（Naming / Defaults / Boundary / Profiles / Cross-doc / Compatibility gate）。
- 既存 pending queue（governance-only）を変更せず、設計変更が必要な論点は ADR 起票条件に留めた。

### Phase 5) Stopper

- 判定: **Stopper未発動**。
- 理由: 今回は契約明文化のみであり、非互換を新規導入していない。非互換変更が必要になった場合は checklist の Compatibility gate に従って停止・承認待ちへ移行する。


## 15) Stream B execution snapshot (2026-05-19)

### Phase 1 Read同期

- `ADR-0029` / `runtime_parameter_registry.md` / `docker-compose.yml` / `configuration.md` を再読し、公開契約面と内部adapter境界面を分離して確認。
- 公開設定は `KJ_ATLAS_*` のみ、vendor 名は private adapter boundary のみという解釈で一致。

### Phase 2 ADR確定

- `ADR-0029` の Status を `Accepted` に更新。
- Context / Decision / Consequences の適用境界を補強するため、boundary contract matrix を追加。

### Phase 3 Contract反映

- `runtime_parameter_registry.md` に private adapter boundary 表を追加。
- `configuration.md` に公開設定と内部adapter境界の分離表を追加。
- `docker-compose.yml` コメントを「private adapter boundary only」として明示。

### Phase 4 Verify

- 公開キー集合は `KJ_ATLAS_*` のみを維持（registry / configuration / compose inputs）。
- 利用者向け文書で vendor 名を公開設定として要求しないことを確認。
- Self-heal loop: 不一致 0 件のため未使用（上限3回以内）。

## 16) Stream E execution snapshot (2026-05-20)

### Plan → Execute → Verify → Proceed

#### Phase 1: Read & Baseline固定
- Allowlist 対象（registry/deployment/enterprise/configuration/operations/security guidelines/issue群/ADR-0021）を再読し、公開キーが `KJ_ATLAS_*` に統一されていることを再確認。
- ギャップ抽出結果: 命名・既定値・公開/内部境界は 02 層で整合済み。04層に profile 運用判断の導線を追加する余地を確認。

#### Phase 2: 契約統一方針の再確認
- 旧名→新名方針は `ADR-0021` の「互換なし一括移行」を再採用（追加ADR不要）。
- 後方互換方針: backend runtime は互換層なし、third-party adapter 内部名のみ private boundary として許容。
- プロファイル安全既定値: `enterprise-production` では `KJ_ATLAS_ALLOW_JIT_PROVISIONING=false` と fail-safe (`read_only`/`deny`) を運用上の必須確認項目として維持。

#### Phase 3: ドキュメント同期
- `04_Documentation/configuration.md` に Runtime profiles セクションを追加し、実装既定値と本番推奨値の違い（JIT provisioning）を明示。
- `04_Documentation/operations.md` に profile 選択セクションを追加し、運用開始前の profile 固定と enterprise 追加チェックを明示。
- `04_Documentation/security_operational_guidelines.md` に profile 前提の変更抑止（未確定時は変更しない）を追加。

#### Phase 4: 実装追随判定
- ENV 読取実装への致命的不一致は検出せず、コード変更は不要と判断。

#### Phase 5: Verify & Proceed
- 文書差分を確認し、公開キー命名・既定値・境界に新たなドリフトがないことを確認。
- Proceed 判定: Stream E scope で完了。残る論点は governance queue（strict no-vendor-env 解釈、`external_http` fail-fast 方針）のみ。


## Stream D update (2026-05-20)

### Phase 1) Read同期

- `runtime_parameter_registry.md` をSSOTとして再読し、公開キー集合・既定値・profile差分を固定した。
- 関連issue（ENV-ARCH-01 / ENV-CONFIG-DRIFT-01 / ENV-PROFILE-01）の `Status / Priority / Dependencies / Related ADR` を同一セッションで再確認した。

### Phase 2) Context / Decision / Consequences

- Context: backendは `KJ_ATLAS_*` 単独契約で移行完了。deploy/frontendは公開契約と内部adapter境界の明文化が主課題。
- Decision: 公開契約は `KJ_ATLAS_*` のみを維持し、互換は private layer（third-party env / frontend shim）に閉じ込める。
- Consequences: 旧キー再導入や prefix例外は本streamで実施しない。必要時は新規ADRでGo/No-Goを先行確定する。

### Phase 3) グローバルprefix移行と互換レイヤ設計

- Public layer: 利用者入力は `KJ_ATLAS_*` のみ受理。
- Private layer: `POSTGRES_*` は third-party container内部名、`VITE_API_BASE` は非公開互換shimとして限定運用。
- Exit条件: 命名/既定値/境界/profile の4観点が同時に満たされること。

### Phase 4) Plan → Execute → Verify → Proceed

- Plan: 4観点ゲートを固定。
- Execute: 契約文書（02）→ issue運用（01）の順で同期。
- Verify: docs-check中心で差分検証し、実装契約との不整合がないことを確認。
- Proceed: 不整合なしのため継続可能。追加の実装変更は不要。

### Phase 5) 3回失敗で停止

- 本更新では Verify失敗 0回。
- 以後、同一論点で Verify が3回連続失敗した場合は Stop し、再開条件と要判断事項をissueに追記する。

## 18) Productization readiness boundary check (2026-06-02)

### Read

- `ADR-0029` の Status が `Accepted` であることを再確認した。
- `runtime_parameter_registry.md` の公開キー表、private adapter boundary、drift recurrence checklist を再確認した。
- 本 issue 冒頭に残っていた `ADR-0029` を proposed とする古い記述を、accepted decision として更新した。

### Decision boundary

| 論点 | 判定 | 理由 |
| --- | --- | --- |
| 公開環境変数の命名 | Pass | 利用者・運用者が設定する公開キーは `KJ_ATLAS_*` のみ。 |
| 第三者コンテナ内部名 | Pass under ADR-0029 | `POSTGRES_*` は private adapter boundary であり、公開設定ではない。 |
| issue owner | Clarified | `Owner: TBD` を解消し、runtime-configuration steward と accountable runtime owner を分離した。 |
| 全 process env からの非 `KJ_ATLAS_*` 排除 | Pending by design | 採用する場合は deployment 再設計を伴う別ADRが必要。 |
| `external_http` endpoint 未設定時の fail-fast 既定化 | Pending by design | 可用性/安全性トレードオフを変更するため、この issue だけでは決めない。 |

### Done readiness

- This issue is close to Done for the public runtime contract, because the registry, public documentation, Compose inputs, and backend settings contract now point to the same `KJ_ATLAS_*` namespace.
- Do not mark the issue Done until final verification records the concrete command results for settings validation, frontend build-key behavior, docs key-drift search, and Compose config.
- No new ADR is required for this update. A new ADR is required only if the team chooses either a stricter no-vendor-env deployment model or a fail-fast default for missing `external_http` endpoints.

### Next verification commands

- `python 01_Plans/issues/validate_active_issue_memos.py`
- `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
- `pytest 03_Implement/backend/tests/test_settings_env_prefix_migration.py`
- `cd 03_Implement/deploy && docker compose config`
- `rg -n -P "<non-prefixed-public-env-key-pattern>" 02_Architecture 03_Implement 04_Documentation`

### Slice verification (2026-06-02)

- Pass: `03_Implement\backend\.venv\Scripts\python.exe 01_Plans\issues\validate_active_issue_memos.py` -> validated 5 active issue memos.
- Pass: `03_Implement\backend\.venv\Scripts\python.exe -m unittest 01_Plans\issues\tests\test_validate_active_issue_memos.py` -> 10 tests passed.
- Pass: `03_Implement\backend\.venv\Scripts\python.exe 01_Plans\triage_actionable_plans.py` -> stopper none.
- Pass: `03_Implement\backend\.venv\Scripts\python.exe -m unittest 01_Plans\tests\test_triage_actionable_plans.py` -> 1 test passed.
- Pass: `03_Implement\backend\.venv\Scripts\python.exe -m pytest 03_Implement\backend\tests\test_settings_env_prefix_migration.py -q --basetemp 03_Implement\backend\.pytest_tmp_env_config_readiness -p no:cacheprovider` -> 12 tests passed.
- Reviewed: key scan for `VITE_API_BASE`, `POSTGRES_*`, `DATABASE_URL`, `WEB_PORT`, and `FRONTEND_API_BASE` showed public docs/config using `KJ_ATLAS_*`; `POSTGRES_*` appears only in private-boundary documentation or Compose adapter mapping.
- Not run: `docker compose config`; this host does not have the `docker` command. Final Done still requires a real Compose config/build verification on a Docker-capable host.

## 19) Verification harness prefix sync (2026-06-04)

### Scope

- Read: `runtime_parameter_registry.md`, backend test harness scripts, Auth Level2 fixtures, PostgreSQL roundtrip test opt-in, and related internal issue examples.
- Finding: product runtime public keys already used `KJ_ATLAS_*`, but local verification harness keys still had non-prefixed PostgreSQL opt-in, provider profile, and Auth Level2 names.
- Decision: verification harness keys are not public runtime settings and remain out of `04_Documentation/configuration.md`; however, the "no prefix exception" rule still applies to names used by kj-atlas scripts and tests.

### Execute

- Renamed PostgreSQL roundtrip opt-in to `KJ_ATLAS_RUN_PG_TESTS`.
- Renamed Auth Level2 harness inputs and derived URLs to `KJ_ATLAS_AUTH_LEVEL2_*` and `KJ_ATLAS_AUTH_PROVIDER_PROFILE_DIR`.
- Updated backend README and AUTH-E2E internal issue examples so copied commands no longer introduce legacy non-prefixed names.
- Added a non-public "Verification harness keys" table to `runtime_parameter_registry.md`, including Auth Level2, PostgreSQL test, and recovery rehearsal keys.
- Removed uppercase local variable names in `mock_sp.py` that looked like env names during drift scans.
- Added `test_project_env_access_points_use_kj_atlas_prefix` to keep backend/frontend direct env access points from reintroducing non-prefixed project keys.

### Verify

- Pass: legacy-name scan over `01_Plans`, `02_Architecture`, `03_Implement`, and `04_Documentation` -> no matches.
- Pass: direct env-read scan over backend/frontend/deploy found no non-`KJ_ATLAS_*` env reads, excluding `import.meta.env.DEV`.
- Pass: `03_Implement\backend\.venv\Scripts\python.exe -m pytest 03_Implement\backend\tests\test_docs_roundtrip.py::test_docs_put_get_roundtrip_sqlite 03_Implement\backend\tests\test_docs_roundtrip.py::test_docs_put_get_roundtrip_postgres 03_Implement\backend\tests\test_auth_provider_profile_fixture.py::test_provider_profile_fixture_google_oidc_roundtrip -q --basetemp 03_Implement\backend\.pytest_tmp_env_harness_prefix -p no:cacheprovider` -> 2 passed, 1 skipped.
- Pass: `03_Implement\backend\.venv\Scripts\python.exe 01_Plans\issues\validate_active_issue_memos.py` -> validated 5 active issue memos.
- Pass: `03_Implement\backend\.venv\Scripts\python.exe -m unittest 01_Plans\issues\tests\test_validate_active_issue_memos.py` -> 10 tests passed.
- Pass: `03_Implement\backend\.venv\Scripts\python.exe -m pytest 03_Implement\backend\tests\test_settings_env_prefix_migration.py -q --basetemp 03_Implement\backend\.pytest_tmp_env_prefix_migration -p no:cacheprovider` -> 12 tests passed.
- Pass: `03_Implement\backend\.venv\Scripts\python.exe -m pytest 03_Implement\backend\tests\test_settings_env_prefix_migration.py -q --basetemp 03_Implement\backend\.pytest_tmp_env_prefix_scan -p no:cacheprovider` -> 13 tests passed.

### Proceed/Stop

- Proceed: no product runtime behavior change and no new ADR required.
- Remaining Done blocker: Docker-capable host verification for `docker compose config` is still required before this issue can be closed.

## 20) ADR-0021 readability and public-prefix contract sync (2026-06-06)

### Scope

- Read: `ADR-0021`, `runtime_parameter_registry.md`, public configuration docs, backend settings, frontend env prefix, and deploy Compose inputs.
- Finding: the implementation and public documentation keep the public runtime contract on `KJ_ATLAS_*`, but `ADR-0021` had become hard to read and could no longer serve as the decision record for the no-exception prefix policy.
- Finding: older historical ADRs still contain legacy examples such as `LLM_PROVIDER=none` or `LLM_ESCALATION_ENABLED=false`. These are documentation-quality debt, not current runtime behavior. They should be normalized in a separate ADR/readability slice so encoding repair does not get mixed with runtime contract work.

### Execute

- Rewrote `ADR-0021` in readable Japanese while preserving the Accepted decision: public kj-atlas environment variables must start with `KJ_ATLAS_` without exception.
- Clarified that `POSTGRES_*` and build-tool internal names are private adapter boundary names, not user-facing kj-atlas configuration.
- Kept the issue boundary unchanged: no SafeMode, share/export, LLM opt-in, audit, access-control, Compose behavior, backend settings, or frontend runtime behavior change.

### Proceed/Stop

- Proceed: the public-prefix decision record is readable again and matches the current implementation/documentation contract.
- Stop before Done: Docker-capable `docker compose config` verification is still required, and historical ADR readability cleanup should remain a separate documentation-quality slice.

## 21) Historical ADR legacy environment reference sync (2026-06-06)

### Scope

- Read: historical ADRs that still described runtime settings with legacy unprefixed examples.
- Finding: current implementation, registry, and public docs use `KJ_ATLAS_*`, but several older accepted ADRs still referenced `DATABASE_URL`, `LLM_PROVIDER`, `LLM_ESCALATION_ENABLED`, or `LLM_LARGE_SCALE_OPT_IN` as if they were current setting keys.
- Finding: PR #2335 carried this normalization, but the current `origin/main` checkpoint after PR #2336 still contains the legacy examples. This slice reapplies the same documentation-only correction to the current mainline.
- Decision: normalize those references to the accepted `KJ_ATLAS_*` names without changing the historical ADR decisions or product runtime behavior.

### Execute

- Updated `ADR-0001`, `ADR-0003`, `ADR-0007`, `ADR-0009-local-llm-integration`, and `review-ADR-0009-phase-a` to use current `KJ_ATLAS_*` key names.
- Kept the changes limited to environment-variable names. No design conclusion, implementation scope, LLM policy, SafeMode behavior, or public documentation contract was changed.

### Proceed/Stop

- Proceed: historical decision records no longer contradict the accepted no-exception public prefix policy in their current-key examples.
- Stop before Done remains unchanged: Docker-capable `docker compose config` verification is still required before closing this issue.

## 22) Public configuration exact-key guard (2026-06-07)

### Scope

- Read: `02_Architecture/runtime_parameter_registry.md`, `04_Documentation/configuration.md`, `03_Implement/backend/tests/test_settings_env_prefix_migration.py`, and the deploy/runtime references touched by the current public configuration contract.
- Finding: `04_Documentation/configuration.md` already listed the concrete PostgreSQL Compose keys in the full environment-variable table, but the earlier boundary example still used `KJ_ATLAS_POSTGRES_*` as a shorthand.
- Decision: public user-facing configuration examples should not use shorthand wildcard names when the requirement is to list every supported environment variable. The general policy phrase `KJ_ATLAS_*` remains acceptable for describing the namespace rule, but concrete configuration examples must enumerate exact keys.

### Execute

- Replaced the public-boundary example `KJ_ATLAS_POSTGRES_*` with `KJ_ATLAS_POSTGRES_DB`, `KJ_ATLAS_POSTGRES_USER`, and `KJ_ATLAS_POSTGRES_PASSWORD`.
- Added `test_public_configuration_doc_lists_exact_public_runtime_keys` so `04_Documentation/configuration.md` must contain the same public runtime key set as the public section of `runtime_parameter_registry.md`.
- Added a guard that rejects concrete-key wildcard shorthand such as `KJ_ATLAS_POSTGRES_*` in the public configuration document, while still allowing the namespace policy phrase `KJ_ATLAS_*`.

### Verify

- Pass: `.venv\Scripts\python.exe -m pytest tests\test_settings_env_prefix_migration.py --basetemp ..\..\.pytest_tmp_env_config_exact_keys -p no:cacheprovider` from `03_Implement/backend` -> 14 tests passed.

### Proceed/Stop

- Proceed: public configuration docs now enumerate exact public runtime keys and have a regression guard against future wildcard shorthand drift.
- Stop before Done remains unchanged: Docker-capable `docker compose config` verification is still required before closing this issue.


## 23) Stream E runtime configuration re-validation (2026-06-13)

### Phase 1 — Runtime contract read

- Read `ADR-0021`, `runtime_parameter_registry.md`, `deployment.md`, `llm_runtime_constraints.md`, `configuration.md`, backend `settings.py`, frontend `client.ts`, frontend `Dockerfile`, and `docker-compose.yml`.
- Canonical public runtime keys remain `KJ_ATLAS_*` only. Legacy unprefixed keys are rejection targets, not compatibility aliases.
- External LLM escalation remains default-off: `KJ_ATLAS_LLM_PROVIDER=none`, `KJ_ATLAS_LLM_ESCALATION_ENABLED=false`, and `KJ_ATLAS_LLM_LARGE_SCALE_OPT_IN=false`.

### Phase 2 — ENV-CONFIG-DRIFT-01 resolution

Drift list by setting-name group:

| Setting group | Current canonical state | Drift classification | Action |
| --- | --- | --- | --- |
| Backend runtime keys | Registry, configuration doc, and `Settings` aliases use `KJ_ATLAS_*`. | None | Marked AC/T1-T7 complete. |
| Legacy backend keys | `LEGACY_ENV_KEYS` rejects unprefixed historical names. | None | Verified by backend prefix tests. |
| CE4 keys | Registry and settings agree on `KJ_ATLAS_CE4_*`, including `KJ_ATLAS_CE4_STUB_UNRESOLVED_CONTRACTS`. | None | Verified by backend prefix tests. |
| Access-control enum keys | Registry values match settings validation for adapter, fail-safe, auth mode, and reviewer resolver. | None | Verified by backend prefix tests. |
| Frontend API base | `KJ_ATLAS_FRONTEND_API_BASE` is the public build key and invalid values fall back to `/api`. | None | Verified by frontend API client unit test and typecheck. |
| Compose public inputs | Compose public inputs are `KJ_ATLAS_WEB_PORT`, `KJ_ATLAS_POSTGRES_DB`, `KJ_ATLAS_POSTGRES_USER`, `KJ_ATLAS_POSTGRES_PASSWORD`, `KJ_ATLAS_FRONTEND_API_BASE`, `KJ_ATLAS_DATABASE_URL`, and `KJ_ATLAS_LLM_PROVIDER`. | None | Verified by static Compose review; Docker binary unavailable for live config expansion. |
| Private adapter names | `POSTGRES_DB`, `POSTGRES_USER`, and `POSTGRES_PASSWORD` appear only as PostgreSQL container internal names mapped from `KJ_ATLAS_POSTGRES_*`. | Accepted boundary | Keep under ADR-0029; no public alias added. |
| `external_http` endpoint absence | User-facing docs warn that missing endpoint is treated like `noop`; fail-fast is a separate ADR-level decision. | Governance-only hold, not contract drift | No behavior change in this stream. |

Classification: **Done-ready for the runtime configuration contract; environment-limited Hold only for Docker-capable `docker compose config` evidence in this container.**

### Phase 3 — ENV-ARCH-01 prefix migration

- Prefix migration residuals: none in the runtime configuration surface reviewed here.
- No old-key compatibility alias was added.
- Deploy examples and docs continue to show user-set keys with `KJ_ATLAS_` only.

### Phase 4 — ENV-PROFILE-01 runtime profiles

- Profile guidance remains connected through `runtime_parameter_registry.md` and `configuration.md`.
- No new profile was introduced. Existing profile names remain `local-dev`, `evaluation`, and `enterprise-production`.
- Safe defaults are preserved: LLM provider `none`, escalation disabled, audit HTTP disabled, and access-control fail-safe defaults documented separately from enterprise recommendations.

### Phase 5 — Backend config check

- Backend setting aliases, defaults, enum validation, and legacy-key rejection are aligned with the registry.
- No backend implementation change was required.

### Phase 6 — Frontend config check

- Frontend env reading is limited to `KJ_ATLAS_FRONTEND_API_BASE`.
- Invalid, empty, or non-path values continue to normalize to `/api`.
- No UI component or feature behavior was changed.

### Phase 7 — Deploy / docs sync

- Deploy and configuration docs already use the registry key names.
- Compose does not embed secrets; PostgreSQL defaults are demonstrative local/evaluation values and remain configurable through `KJ_ATLAS_POSTGRES_*`.
- No `nginx.conf` setting drift was found; it does not expose public runtime keys.

### Phase 8 — Verification

- Pass: `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues` -> validated 5 active issue memos.
- Pass: `git diff --check` -> no whitespace errors.
- Pass: `cd 03_Implement/backend && python -m pytest tests/test_settings_env_prefix_migration.py -q --basetemp ../../.pytest_tmp_env_prefix -p no:cacheprovider` -> 14 tests passed.
- Pass: `cd 03_Implement/frontend && npm test -- --run src/api/client.test.ts` -> 4 tests passed.
- Pass: `cd 03_Implement/frontend && npm run lint` -> typecheck passed. npm emitted an environment warning for `http-proxy`, but the command exited 0.
- Warning: `cd 03_Implement/deploy && docker compose config` -> Docker is unavailable in this container (`docker: command not found`), so live Compose expansion remains to be rerun on a Docker-capable host.

### Phase 9 — Final report

- Fixed / verified setting names: registry public keys used by backend settings, the frontend build key, and Compose public inputs listed above.
- Registry alignment: public user-facing keys are `KJ_ATLAS_*`; private adapter names remain non-public.
- Residual drift: none found in the reviewed runtime configuration contract.
- Remaining non-drift hold: Docker-capable `docker compose config` evidence.
- Changed file in this stream: this issue memo only; no code, UI, CE contract, data lifecycle, or public-boundary feature changes.

## 24) Docker-capable host handoff refresh (2026-06-13)

### Scope

- Rechecked the current Codex host after the latest `main` sync.
- `docker --version` still fails with `docker: The term 'docker' is not recognized...`.
- `03_Implement/deploy/docker-compose.yml` remains the Compose source for this issue. No root-level `docker-compose.yml` is expected.
- This update does not change Compose, backend settings, frontend env handling, public docs, SafeMode, share/export, or release authority.

### Current classification

- Runtime configuration contract: **Done-ready**.
- Closure state: **Hold** until a Docker-capable host records live `docker compose config` evidence.
- Drift state: none found in the reviewed public key contract. The remaining blocker is evidence availability, not a known configuration mismatch.

### Human-owned verification task

Run the following from a host with Docker Compose available:

```powershell
cd 03_Implement\deploy
docker compose config
```

Expected result:

- Command exits 0.
- User-facing inputs in the rendered config are driven by `KJ_ATLAS_WEB_PORT`, `KJ_ATLAS_POSTGRES_DB`, `KJ_ATLAS_POSTGRES_USER`, `KJ_ATLAS_POSTGRES_PASSWORD`, `KJ_ATLAS_FRONTEND_API_BASE`, `KJ_ATLAS_DATABASE_URL`, and `KJ_ATLAS_LLM_PROVIDER`.
- `POSTGRES_DB`, `POSTGRES_USER`, and `POSTGRES_PASSWORD` appear only under the PostgreSQL third-party container as private adapter names mapped from `KJ_ATLAS_POSTGRES_*`.
- No additional public non-`KJ_ATLAS_*` setting is introduced.

If the command fails because Docker is unavailable, keep this issue `In Progress`. If it fails because the rendered config exposes a new public non-`KJ_ATLAS_*` input or cannot expand the current public keys, treat that as new drift and update this issue before closing it.

## 25) Legacy frontend key documentation guard (2026-06-19)

### Finding

- The frontend implementation already reads only `KJ_ATLAS_FRONTEND_API_BASE` through Vite's `KJ_ATLAS_` prefix.
- The runtime registry still described `VITE_API_BASE` as an internal compatibility shim even though no such shim exists.
- That description contradicted the accepted no-exception prefix policy and could lead maintainers to reintroduce an unsupported legacy key.

### Execute

- Removed the obsolete compatibility-shim statement from `runtime_parameter_registry.md`.
- Clarified that the frontend build reads only `KJ_ATLAS_FRONTEND_API_BASE` and does not provide a legacy frontend-key shim.
- Added a regression test that rejects `VITE_API_BASE` and `FRONTEND_API_BASE` in the runtime registry and public configuration guide.

### Proceed / Stop

- Proceed: the documented contract now matches the frontend implementation and the `KJ_ATLAS_*`-only policy.
- No ADR is needed because this removes inaccurate compatibility documentation and does not change runtime behavior.
- Stop before Done remains unchanged: Docker is still unavailable on this host, so live `docker compose config` evidence remains human/platform-operator work.
