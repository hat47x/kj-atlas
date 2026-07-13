# Issue: DX-AUTH-L2-01 Level2 marker and diagnostics contract

- Type: Bug
- Status: Done
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P2
- Owner: Codex
- Scope: `02_Architecture/runtime_parameter_registry.md`, `03_Implement/backend/`
- Related Backlog: `AUTH-E2E-01`
- Related ADR/Spec: `ADR-0020`, `ADR-0021`, `02_Architecture/runtime_parameter_registry.md`
- Expected verification level: `integration`

## 課題

legacy federation test は未登録 `level2` markerを使い、通常pytestでも追跡対象の
`.tmp/level2-diagnostics` へ書き込んでいた。2つのLevel2 entrypointは別モジュールを実行し、
mock SP health path も `/health` と `/healthz` でずれていたため、統合ハーネスの3件がskipされていた。

## 受入条件

- [x] 両Level2モジュールが登録済み `auth_level2` markerへ統一される。
- [x] pytest は `--strict-markers` で未知markerを拒否する。
- [x] 通常pytestは診断を書かず、`KJ_ATLAS_LEVEL2_DIAG_DIR` 明示時だけJSONを出力する。
- [x] 両Level2 scripts は `.artifacts/auth-level2/legacy-federation` を既定の診断先として設定する。
- [x] 統合ハーネスが両モジュールを実行し、skipなしで完走する。

## 実施内容

- verification harness key をruntime registryへ先行追加した。
- legacy testを `auth_level2` へ統一し、診断出力をopt-in化する回帰テストを追加した。
- root entrypointを統合ハーネスへ委譲し、統合側で両Level2モジュールを実行するようにした。
- mock SPの確認先を実装済み `/healthz` へ統一した。

## 検証・証跡

- `bash -n scripts/run_auth_level2.sh tests/scripts/run_auth_level2.sh` -> pass。
- `./scripts/run_auth_level2.sh` -> `7 passed`、skip 0。
- `pytest -q tests/test_auth_federation_level2.py tests/test_settings_env_prefix_migration.py`
  -> `19 passed`。
- backend全体: `pytest -q` -> `289 passed, 24 skipped`。未知marker警告なし。
- `ruff check src tests` -> pass。

## 非目標

- IdP/SP契約、認証ヘッダー意味、SafeMode、外部接続方式は変更しない。
- ADR-0054および外部接続レイヤーは対象外とする。
