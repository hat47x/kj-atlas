# Issue Draft: ENV-CONFIG-DRIFT-01 Runtime configuration contract alignment

- Type: Bug
- Status: In Progress
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P2
- Owner: TBD
- Scope: `02_Architecture/`, `03_Implement/backend/`, `03_Implement/frontend/`, `03_Implement/deploy/`, `04_Documentation/`
- Related Backlog: `ENV-ARCH-01`
- Related ADR/Spec: `01_Plans/adr/ADR-0021-env-var-global-prefix-migration.md`, `01_Plans/adr/ADR-0029-third-party-runtime-env-boundary.md`, `02_Architecture/runtime_parameter_registry.md`, `03_Implement/frontend/src/api/client.ts`, `03_Implement/frontend/Dockerfile`, `03_Implement/deploy/docker-compose.yml`, `03_Implement/backend/src/kj_atlas_api/settings.py`, `03_Implement/backend/src/kj_atlas_api/access_control.py`
- Dependencies: N/A
- Expected verification level: `integration`

## Requirement meta I/F（共通キー）

- RequirementID: ENV-CONFIG-DRIFT-01
- RequirementStatement: public runtime configuration keys are exhaustively documented and every public environment variable starts with `KJ_ATLAS_`.
- PriorityClass（Must / Should / Could）: Should
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=ADR-0021 and runtime registry are accepted; 操作=Compose build, backend settings load, frontend build, and docs-check are executed; 期待結果=only `KJ_ATLAS_*` keys are exposed to users and all accepted keys are documented; 除外=changing SafeMode/share/export policy.
- GoNoGoGate（Required / Optional / N/A）: Required
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: public-exposure
- VerificationLevel（docs-check / unit / integration / e2e）: integration
- DecisionStatus（Fixed / Pending）: Fixed (with pending queue for governance-only items)
- DecisionQueueRef（未確定時の参照先）: N/A

## 1) 課題 / Problem statement

- The project policy now requires all public environment variables to use `KJ_ATLAS_` without exception.
- User-facing docs must list every public environment variable, not only the major settings.
- Frontend build configuration previously exposed Vite-style keys to users, and Compose previously exposed non-prefixed port/database keys.
- Backend settings and the runtime registry previously diverged on `KJ_ATLAS_CE4_STUB_UNRESOLVED_CONTRACTS`.
- Access control behavior still has a policy decision point: `external_http` without endpoint currently falls back to `noop`. Changing that to fail-fast may require ADR because it changes the accepted availability/security trade-off.
- Compose still has to pass values into a third-party PostgreSQL container using that image's required internal names. `ADR-0029` proposes the adapter boundary. If the project interprets "no exceptions" as applying to every process environment inside third-party containers, the deployment design needs a replacement implementation.

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
- Keep `ADR-0029` as the proposed decision record for the third-party container environment boundary.
- Create another ADR only if the team decides to change accepted runtime behavior, especially `external_http` missing-endpoint fallback or a stricter no-vendor-env deployment model.

Non-goals:

- Do not change SafeMode defaults.
- Do not redesign RBAC/ABAC semantics.
- Do not expose non-`KJ_ATLAS_*` compatibility keys in public docs.

## 5) 受入条件 / Acceptance criteria

- [ ] `runtime_parameter_registry.md` lists every public environment variable.
- [ ] `04_Documentation/configuration.md` lists every public environment variable.
- [ ] Public docs and run guides do not instruct users to set non-`KJ_ATLAS_*` environment variables.
- [ ] Frontend build can be configured with `KJ_ATLAS_FRONTEND_API_BASE`.
- [ ] Docker Compose public inputs use `KJ_ATLAS_WEB_PORT`, `KJ_ATLAS_POSTGRES_DB`, `KJ_ATLAS_POSTGRES_USER`, `KJ_ATLAS_POSTGRES_PASSWORD`, and `KJ_ATLAS_FRONTEND_API_BASE`.
- [ ] Third-party container environment boundaries are resolved through `ADR-0029` or by replacing the dependency on vendor-defined process environment names.
- [ ] Backend settings and `runtime_parameter_registry.md` agree on all `KJ_ATLAS_CE4_*` keys, including legacy-key rejection behavior.
- [ ] Invalid access-control adapter and fail-safe values fail validation or are explicitly justified by ADR.
- [ ] `external_http` without endpoint is either fail-fast or explicitly retained by ADR with user-facing warning text.
- [ ] Integration-level verification covers Compose build args, backend settings load, frontend build, and relevant docs-checks.

## 6) 実装タスク分解 / Task breakdown

- [ ] T1: Reconcile frontend API base across Dockerfile, Compose, Vite config, `client.ts`, and docs.
- [ ] T2: Reconcile Compose public input keys with the `KJ_ATLAS_*` contract.
- [ ] T3: Reconcile CE4 runtime keys across registry, settings, legacy-key rejection, and tests.
- [ ] T4: Add settings validation for access-control adapter and fail-safe mode.
- [ ] T5: Resolve `ADR-0029` or replace the PostgreSQL deployment path so no vendor-defined process environment names are required.
- [ ] T6: Update 02/03/04 docs after implementation alignment.
- [ ] T7: Add or update tests for the agreed runtime contract.

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
  - changing the proposed `ADR-0029` adapter boundary into a stricter no-vendor-env deployment redesign.
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
