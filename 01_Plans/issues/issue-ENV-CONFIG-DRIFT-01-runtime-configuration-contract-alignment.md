# Issue Draft: ENV-CONFIG-DRIFT-01 Runtime configuration contract alignment

- Type: Bug
- Status: Open
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
- DecisionStatus（Fixed / Pending）: Pending
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
