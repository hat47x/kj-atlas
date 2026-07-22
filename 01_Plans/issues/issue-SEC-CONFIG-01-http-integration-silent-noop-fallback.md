# Issue: SEC-CONFIG-01 external_http連携がエンドポイント未設定時に無警告でnoopへ縮退する（access_control/audit共通）

> 個人OSS・プレリリース段階では `ADR-0039` を適用し、実行に必要な情報だけを記載する。

- Type: Security
- Status: Draft
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P0
- Owner: Maintainer
- Scope: `03_Implement/backend/src/kj_atlas_api/settings.py`, `03_Implement/backend/src/kj_atlas_api/access_control.py`, `03_Implement/backend/src/kj_atlas_api/audit.py`, `03_Implement/backend/tests/test_trusted_http_settings.py`, `03_Implement/backend/tests/test_access_control_external_http_adapter.py`
- Related ADR/Spec: `THREAT_MODEL.md`, `AGENTS.md`（SafeMode/アクセス制御はfail-closedが最優先の安全境界）
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

- 実施すること（人間の設計判断が必要）:
  - (a) `test_build_access_control_adapter_external_http_fallbacks_to_noop_when_endpoint_missing` が固定している現在の挙動を「意図しない抜け穴」と判断するなら、`_validate_trusted_http_resolver()` と同様に `Settings()` 構築時点でfail-closed（`ValueError`）にする。この場合、当該テストと `test_http_integration_normalizes_transport_and_rejects_unknown_value` の両方を、新しい契約に合わせて更新する必要がある。
  - (b) 逆に現在の「設定不備時はnoopへ縮退する」を意図した設計として維持するなら、少なくとも `access_control.py` 側にも `audit.py` と同様の `logger.warning(...)` を追加し、運用者が気づけるようにする（audit側と同水準の検知可能性を確保する）。
  - どちらを採るかは、この経路が「意図的なグレースフルデグレード」なのか「見落とし」なのかという製品/運用ポリシー判断そのものであり、当issueの対応方針としてはこの判断を待つ。
- 実施しないこと:
  - `document_policy_binding_resolver`/`tenant_capability_resolver` 側（既にfail-closed）の変更。

## 受入条件

- [ ] 上記(a)または(b)のいずれかの方針が採用され、`KJ_ATLAS_ACCESS_CONTROL_ADAPTER=external_http` かつエンドポイント未設定の状態が、少なくとも運用者に検知可能な形になる。
- [ ] 既存のテスト（`test_build_access_control_adapter_external_http_fallbacks_to_noop_when_endpoint_missing` 等）が、採用した方針を正しく反映する形に更新される。
- [ ] 関連する安全・互換性を損なわない。
- [ ] 宣言した検証を実行するか、未実施理由を記録する。

## 検証計画

- 実行する確認:
  - `python -m pytest tests/test_trusted_http_settings.py tests/test_access_control_external_http_adapter.py tests/test_access_control_adapter_contract.py tests/test_access_control_adapter_contracts.py -q`
- 期待結果:
  - 採用した方針に沿ってテストが更新され、全て green。

## 補足

- 依存・リスク・ロールバックがある場合だけ記載する。
  - この所見は round 26 の「backend config validation」調査から得られたが、機械的な修正を試みる前に既存テスト（fallback-to-noopを意図として固定するテスト）を発見したため、修正を保留してissue化した。
  - ADR化が必要になる条件: (a)を採用しfail-closedにする場合、既存デプロイでこの設定漏れに依存している環境があれば起動不能になるため、影響範囲次第では新規ADRでトレードオフを固定する。

---

## Authoring Checklist（人間/生成AI 共通）

- [x] `Source Issue` が運用状態と整合している。
- [x] `Related ADR/Spec` が最低1件ある。
- [x] 受入条件に「安全」「互換」「検証」が含まれる。
- [x] `Validation plan` に具体コマンドがある。
- [x] 非目標が明記されスコープ逸脱を防いでいる。
