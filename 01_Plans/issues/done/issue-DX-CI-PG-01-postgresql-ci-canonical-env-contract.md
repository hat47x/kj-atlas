# Issue: DX-CI-PG-01 PostgreSQL CI canonical env contract

- Type: Bug
- Status: Done
- Source Issue: N/A
- Priority: P1
- Owner: Codex
- Scope: `.github/workflows/ci.yml`, `03_Implement/backend/tests/test_settings_env_prefix_migration.py`
- Related Backlog: `ENV-CONFIG-DRIFT-01`
- Related ADR/Spec: `ADR-0021`, `02_Architecture/runtime_parameter_registry.md`
- Expected verification level: `unit`

## 課題

CI が旧 `DATABASE_URL` / `RUN_PG_TESTS` を設定する一方、backend は正規の
`KJ_ATLAS_DATABASE_URL` / `KJ_ATLAS_RUN_PG_TESTS` だけを読む。修正前のCI相当実行は
PostgreSQL 18件をすべて skip して成功し、migration も既定SQLiteへ流れる偽陽性だった。

## 受入条件

- [x] SQLite、Auth Level1/2、PostgreSQL migration/test のCI入力が `KJ_ATLAS_*` のみである。
- [x] PostgreSQL test step が `KJ_ATLAS_RUN_PG_TESTS=1` とPostgreSQL URLを同時に渡す。
- [x] 旧キー再導入を focused regression test で拒否する。
- [x] SafeMode、LLM、share/export の挙動は変更しない。

## 実施内容

- `.github/workflows/ci.yml` のbackend job 6箇所を正規キーへ移行した。
- `test_backend_ci_uses_canonical_database_test_keys` を追加し、旧キー0件と正規キー件数を固定した。

## 検証・証跡

- 修正前再現: `RUN_PG_TESTS=1 DATABASE_URL=postgresql+psycopg://... pytest -m postgres -rs -q`
  -> `18 skipped, 293 deselected`。
- 修正後: `pytest -q tests/test_settings_env_prefix_migration.py::test_backend_ci_uses_canonical_database_test_keys`
  -> pass。
- 回帰束: `pytest -q tests/test_auth_federation_level2.py tests/test_settings_env_prefix_migration.py`
  -> `19 passed`。
- backend全体: `pytest -q` -> `289 passed, 24 skipped`。
- `ruff check src tests` -> pass。

## 非目標

- PostgreSQL schema、Compose、製品runtimeの既定値は変更しない。
- 新規ADRは起票しない。既存 `ADR-0021` の実装ドリフト是正に限定する。
