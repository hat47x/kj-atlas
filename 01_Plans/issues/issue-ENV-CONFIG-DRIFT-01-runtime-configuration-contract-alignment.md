# Issue Draft: ENV-CONFIG-DRIFT-01 Runtime configuration contract alignment

- Type: Bug
- Status: Open
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P2
- Owner: TBD
- Scope: `02_Architecture/`, `03_Implement/backend/`, `03_Implement/frontend/`, `03_Implement/deploy/`, `04_Documentation/`
- Related Backlog: `ENV-ARCH-01`
- Related ADR/Spec: `01_Plans/adr/ADR-0021-env-var-global-prefix-migration.md`, `02_Architecture/runtime_parameter_registry.md`, `03_Implement/frontend/src/api/client.ts`, `03_Implement/frontend/Dockerfile`, `03_Implement/deploy/docker-compose.yml`, `03_Implement/backend/src/kj_atlas_api/settings.py`, `03_Implement/backend/src/kj_atlas_api/access_control.py`
- Dependencies: N/A
- Expected verification level: `integration`

## Requirement meta I/F（共通キー）

- RequirementID: ENV-CONFIG-DRIFT-01
- RequirementStatement: runtime parameter registry, deploy wiring, backend settings validation, and user-facing configuration docs remain mutually consistent.
- PriorityClass（Must / Should / Could）: Should
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=ADR-0021 and runtime registry are accepted; 操作=Compose build, backend settings load, and docs-check are executed; 期待結果=canonical keys and compatibility shims behave exactly as documented; 除外=changing SafeMode/share/export policy.
- GoNoGoGate（Required / Optional / N/A）: Required
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: public-exposure
- VerificationLevel（docs-check / unit / integration / e2e）: integration
- DecisionStatus（Fixed / Pending）: Pending
- DecisionQueueRef（未確定時の参照先）: N/A

## 1) 課題 / Problem statement

- `runtime_parameter_registry.md` defines `VITE_KJ_ATLAS_API_BASE` as the frontend canonical API base key, but the current Docker Compose / Dockerfile build path only passes `VITE_API_BASE`.
- `runtime_parameter_registry.md` lists `KJ_ATLAS_CE4_STUB_UNRESOLVED_CONTRACTS`, but `settings.py` does not expose the prefixed key and does not reject the unprefixed legacy variant.
- Access control configuration is partly permissive at runtime: unknown adapter names and `external_http` without endpoint fall back to `noop`; `KJ_ATLAS_ACCESS_CONTROL_FAIL_SAFE_MODE` is consumed as `read_only|deny` by type contract but is not validated in settings.
- Some `02_Architecture` documents still contain unprefixed examples such as `DATABASE_URL`, `LLM_PROVIDER`, `ACCESS_CONTROL_*`, and `ALLOW_JIT_PROVISIONING` even though ADR-0021 and the registry define `KJ_ATLAS_*` as the accepted backend contract.
- User-facing docs can describe current behavior, but the implementation/configuration contract should be aligned so operators do not mistake a compatibility path or fallback for the canonical secure path.

## 2) 背景 / Context

- ADR-0021 fixes the global prefix policy and delegates execution tracking to ENV-ARCH-01.
- ENV-ARCH-01 is Done, but later implementation added a frontend compatibility shim and CE4/runtime settings continued to evolve.
- `04_Documentation/configuration.md` and `04_Documentation/security.md` were updated to state the current behavior, including the Compose `VITE_API_BASE` path and access control fallback.

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: configuration drift makes self-hosted evaluation harder and weakens privacy-default expectations.
- 安全（THREAT_MODEL / SafeMode）: access control fallback can become public exposure if operators believe external PDP enforcement is active.
- 企業・行政要件（enterprise_architecture）: strict access-control deployments need fail-fast configuration and auditable PDP wiring.
- 後方互換（schemas）: frontend `VITE_API_BASE` compatibility should remain until a migration/removal decision is explicit.

## 4) 提案する解決策 / Proposed solution

- Update Dockerfile/Compose wiring so `VITE_KJ_ATLAS_API_BASE` is accepted as the canonical build arg while preserving `VITE_API_BASE` as a documented compatibility shim.
- Add `KJ_ATLAS_CE4_STUB_UNRESOLVED_CONTRACTS` to backend settings or remove it from the registry after confirming the CE4 contract. Reject the unprefixed legacy variant if the setting remains.
- Validate `KJ_ATLAS_ACCESS_CONTROL_ADAPTER` and `KJ_ATLAS_ACCESS_CONTROL_FAIL_SAFE_MODE` in settings. If changing `external_http` missing-endpoint fallback from `noop` to fail-fast would alter the accepted availability/security decision, open a small ADR before implementation.
- Sync `02_Architecture` examples to the ADR-0021/registry naming contract, or explicitly mark legacy mentions as rejected historical context.
- Keep 04 docs focused on current behavior and update them after implementation alignment lands.

Non-goals:

- Do not change SafeMode defaults.
- Do not remove frontend `VITE_API_BASE` compatibility without a migration decision.
- Do not redesign RBAC/ABAC policy semantics.

## 5) 受入条件 / Acceptance criteria

- [ ] Compose builds can be configured with `VITE_KJ_ATLAS_API_BASE` and still support `VITE_API_BASE` as a compatibility path.
- [ ] Backend settings and `runtime_parameter_registry.md` agree on all `KJ_ATLAS_CE4_*` keys, including legacy-key rejection behavior.
- [ ] Invalid access control adapter and fail-safe values fail validation or are explicitly justified by ADR.
- [ ] `external_http` without endpoint is either fail-fast or explicitly retained by ADR with user-facing warning text.
- [ ] `02_Architecture` no longer presents unprefixed backend environment keys as current configuration.
- [ ] `03_Implement/README.md` and `04_Documentation/configuration.md` do not instruct users to rely on unimplemented configuration keys.
- [ ] Integration-level verification covers Compose build args, backend settings load, and relevant docs-checks.

## 6) 実装タスク分解 / Task breakdown

- [ ] T1: Reconcile frontend API base build args across Dockerfile, Compose, `client.ts`, and docs.
- [ ] T2: Reconcile CE4 runtime keys across registry, settings, legacy-key rejection, and tests.
- [ ] T3: Add settings validation for access control adapter and fail-safe mode, or document the ADR-backed reason for retaining permissive fallback.
- [ ] T4: Update 02/03/04 docs after implementation alignment.
- [ ] T5: Add or update tests for the agreed runtime contract.

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `python 01_Plans/issues/validate_active_issue_memos.py`
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `pytest 03_Implement/backend/tests/test_settings_env_prefix_migration.py`
  - `cd 03_Implement/deploy && docker compose build web`
  - `rg -n "VITE_KJ_ATLAS_API_BASE|VITE_API_BASE|KJ_ATLAS_CE4_STUB_UNRESOLVED_CONTRACTS|KJ_ATLAS_ACCESS_CONTROL" 02_Architecture 03_Implement 04_Documentation`
- 期待結果:
  - active issue metadata validates.
  - settings tests cover canonical and legacy key behavior.
  - Compose web build receives the documented API base value.
  - docs and registry no longer contradict implementation behavior.
- 未実施時の理由・代替検証:
  - Docker unavailable environments may substitute `docker compose config` plus Dockerfile diff review, but final Done requires a real build.

## 8) 代替案 / Alternatives considered

- Leave current compatibility behavior documented only:
  - Rejected as the sole fix because registry/implementation drift would remain and operators could rely on a non-canonical path indefinitely.
- Remove `VITE_API_BASE` immediately:
  - Rejected for now because frontend compatibility removal needs migration timing and release-note handling.

## 9) リスクとロールバック / Risks & rollback

- 失敗モード: existing Compose users with only `VITE_API_BASE` break if compatibility is removed too early.
- 影響範囲: Docker Compose builds, frontend API routing, backend settings validation, enterprise access-control deployments.
- ロールバック手順: restore compatibility shim and revert stricter validation only if it blocks documented safe configurations; do not relax SafeMode/share/export policy.

## 10) Additional context

- Related issue: `01_Plans/issues/issue-ENV-ARCH-01-global-env-prefix-migration.md`
- ADR化が必要になる条件: changing the accepted access-control availability/security trade-off, especially replacing `external_http` missing-endpoint `noop` fallback with fail-fast behavior.
