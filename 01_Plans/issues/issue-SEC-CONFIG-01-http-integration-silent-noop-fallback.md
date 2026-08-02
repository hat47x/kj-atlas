# Issue: SEC-CONFIG-01 external_http連携がエンドポイント未設定時に無警告でnoopへ縮退する（access_control/audit共通）

> 個人OSS・プレリリース段階では `ADR-0039` を適用し、実行に必要な情報だけを記載する。

- Type: Security
- Status: Done
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P0
- Owner: Maintainer
- Scope: `01_Plans/adr/ADR-0062-explicit-http-integration-fail-fast.md`, `02_Architecture/api.md`, `02_Architecture/enterprise_architecture.md`, `02_Architecture/runtime_parameter_registry.md`, `03_Implement/backend/src/kj_atlas_api/settings.py`, `03_Implement/backend/src/kj_atlas_api/access_control.py`, `03_Implement/backend/src/kj_atlas_api/audit.py`, `03_Implement/backend/tests/test_trusted_http_settings.py`, `03_Implement/backend/tests/test_access_control_external_http_adapter.py`, `03_Implement/backend/tests/test_audit.py`, `04_Documentation/configuration.md`, `04_Documentation/security.md`, `THREAT_MODEL.md`
- Related ADR/Spec: `01_Plans/adr/ADR-0062-explicit-http-integration-fail-fast.md`, `02_Architecture/runtime_parameter_registry.md`, `02_Architecture/api.md`, `THREAT_MODEL.md`
- Expected verification level: `unit`

## 課題

- 現在の問題:
  - `settings.py:85-102` の `_validate_optional_http_integration()` は、`enabled=True` かつ `endpoint=None` の場合でも例外を送出せず、`Settings()` の構築が成功してしまう。
  - この関数は `KJ_ATLAS_ACCESS_CONTROL_ADAPTER=external_http`（`settings.py:521-527`）と `KJ_ATLAS_AUDIT_TRANSPORT=http`（`settings.py:514-520`）の両方の検証に使われている。
  - 実行時、`access_control.py:build_access_control_adapter()`（554-579行、特に568-579行）は、`adapter_name="external_http"` でもエンドポイントが解決できなければ **無警告で** `NoopAccessControlAdapter` を返し、その `authorize()`（116-120行）は常に `AccessDecision(allow=True)` を返す。つまり運用者が「外部PDPで認可を強制している」つもりでも、実際には**すべてのリクエストが無条件許可**される。
  - `audit.py:build_audit_dispatcher()`（364-390行）も同様に `NoopAuditTransport` へ縮退するが、こちらは `logger.warning(...)` を出すため、access_control側よりは検知可能性が高い。
  - 同じファイル内の兄弟実装 `document_policy_binding_resolver`/`tenant_capability_resolver` は `_validate_trusted_http_resolver()`（19-40行）で検証されており、`enabled` 時にエンドポイントが無ければ `Settings()` 構築の時点で明示的に `ValueError` を送出し、実行時ビルダーも fail-closed な `Unavailable*Resolver`（利用時に例外）を返す。`access_control`/`audit` の2箇所だけがこのパターンから外れ、fail-open になっている。
  - **重要**: 単純に `_validate_optional_http_integration()` を厳格化するだけでは済まない。`test_access_control_external_http_adapter.py:381-388`（`test_build_access_control_adapter_external_http_fallbacks_to_noop_when_endpoint_missing`）は、この「エンドポイント欠落時にnoopへ縮退する」挙動を**意図した仕様として明示的に固定するテスト**として既に存在する。また `test_trusted_http_settings.py:139-142`（`test_http_integration_normalizes_transport_and_rejects_unknown_value`）も、`KJ_ATLAS_AUDIT_TRANSPORT="http"` をエンドポイント未設定のまま構築できることに暗黙に依存している。このため、これが「見過ごされたバグ」なのか「意図されたグレースフルデグレード」なのかは人間の判断が必要であり、機械的に直すことはできない。
- 利用者または開発への影響:
  - `KJ_ATLAS_ACCESS_CONTROL_EXTERNAL_HTTP_ENDPOINT` の設定漏れやtypoだけで、外部PDPによる認可制御が完全に無効化され、しかもそれに気づく手段が現状ない（ログもエラーもない）。

## 対応方針

- (a) のfail-fastを採用した。外部HTTP連携の選択とendpointを不可分の設定とし、警告後のnoop縮退では認可の全許可を防げないためである。
- `KJ_ATLAS_ACCESS_CONTROL_ADAPTER=external_http` または `KJ_ATLAS_AUDIT_TRANSPORT=http` を明示した場合、対応endpointがなければ `Settings()` 構築時に `ValueError` で停止する。
- runtime builderにも防御層を置き、設定差し替えや直接呼び出しでもendpoint欠落時に例外を送出し、noopへ縮退させない。
- 既定値と明示的な `noop` は維持する。完全設定後のaccess-control実行時障害は既存の `read_only|deny`、audit送信障害は既存のfail-openを維持し、起動時の到達性probeは行わない。
- 全runtime profileへ同じ規則を適用する。個人OSS・プレリリースで既存利用者向け移行契約がないため、互換flagは追加しない。
- `document_policy_binding_resolver`/`tenant_capability_resolver` 側は変更しない。

## 実施結果

- `ADR-0062` に判断、代替案、互換影響、安全境界を固定した。
- Settings検証とaccess-control/auditの両builderから暗黙のnoop fallbackを除去した。
- 欠落拒否、秘密値非反射、既定noop、完全設定時のHTTP transport選択、既存の実行時障害方針をテストで確認した。
- runtime registry、API、enterprise architecture、公開設定・安全ガイド、脅威モデルを同じ契約へ同期した。

## 受入条件

- [x] (a)を採用し、access-controlとauditの明示的HTTP選択でendpointが未設定なら起動時および直接builder呼び出し時に検知・拒否される。
- [x] 既存のfallbackテストとaudit transport正規化テストを新契約へ更新し、欠落拒否と完全設定の正常系を追加した。
- [x] 既定/明示noop、access-control実行時fail-safe、audit送信時fail-open、秘密値非反射を維持した。
- [x] 宣言した検証を実行し、結果と対象外の既存失敗を記録した。

## 検証

- `python -m pytest tests/test_trusted_http_settings.py tests/test_access_control_external_http_adapter.py tests/test_access_control_adapter_contract.py tests/test_access_control_adapter_contracts.py tests/test_audit.py -q`
  - `67 passed`
- `python -m ruff check .`
  - passed
- `python 01_Plans/docs_check.py`
  - passed
- `git diff --check`
  - passed
- backend全体回帰（補助コマンドの検索パスを補正し、既存の別OS向け `.venv/lib64` を走査する1件を除外）
  - `636 passed, 25 skipped, 1 deselected`
- 除外した `test_project_env_access_points_use_kj_atlas_prefix` は別OS環境で単独実行し、既存のmonkey test scriptsにある非 `KJ_ATLAS_*` 環境変数5件を検出した。当issueの変更ファイル外にある既存失敗のため修正しない。

## 補足

- 依存・リスク・ロールバックがある場合だけ記載する。
  - この所見は round 26 の「backend config validation」調査から得られたが、機械的な修正を試みる前に既存テスト（fallback-to-noopを意図として固定するテスト）を発見したため、修正を保留してissue化した。
  - (a)の採用と互換影響は `ADR-0062` に固定した。明示的HTTP連携を選びながらendpointを欠く既存構成は起動しなくなるため、正しいendpointを設定するか、連携を使わない意図を明示して `noop` に戻す。

---

## Authoring Checklist（人間/生成AI 共通）

- [x] `Source Issue` が運用状態と整合している。
- [x] `Related ADR/Spec` が最低1件ある。
- [x] 受入条件に「安全」「互換」「検証」が含まれる。
- [x] `Validation plan` に具体コマンドがある。
- [x] 非目標が明記されスコープ逸脱を防いでいる。
