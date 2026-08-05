# Issue: SEC-RATE-LIMIT-01 backend APIにrate limitが一切ない（MCP transportとの非対称）

- Type: Security
- Status: Draft
- Source Issue: N/A
- Priority: P2
- Owner: Maintainer
- Scope: `03_Implement/backend/src/kj_atlas_api/main.py`
- Related ADR/Spec: `03_Implement/mcp/src/http_server.ts`, `THREAT_MODEL.md`
- Expected verification level: `integration`

## 課題

- 現在の問題: `03_Implement/mcp/src/http_server.ts`はTHREAT_MODEL.mdの記述通り（「全route（metadata含む）に60 req/min/IPのrate limitを適用」）、`express-rate-limit`を使い実際に60 req/min/IPのrate limitを実装している。一方、backend API（`03_Implement/backend/src/kj_atlas_api`）にはrate limit相当の仕組みが一切存在しない（`rate.?limit|slowapi|throttl|Retry-After|429`でrepository全体をgrepしても`pyproject.toml`含め0件）。`main.py`の唯一のmiddlewareは`require_api_key`（静的な共有シークレットheader確認）で、`settings.api_key`が未設定の場合は素通りする。
- 利用者または開発への影響: 特に`POST /admin/provision/users`（`Depends(get_db)`のみで認証依存なし）と、`auth_context.py`内のJIT provisioning（`settings.allow_jit_provisioning`の既定値`True`時、未知のprovider/external_uidヘッダーから新規`UserRow`/`UserIdentityRow`を作成）は、事前認証なしに到達可能かつ状態変更を伴う。`settings.api_key`の既定値は`None`（未設定）であるため、既定構成ではこれらのエンドポイントへのrequest数に上限が一切ない。`POST /session/active-tenant`も同様に未制限。

## 対応方針

- 実施すること: backend APIへrate limitを導入するかどうか、導入する場合どの方式（プロセス内limiter、共有store（Redis等）を用いた分散limiter等）を採るかをMaintainerが判断する。FastAPI/uvicornの実際のデプロイ形態（単一worker/複数worker）によって、プロセス内limiterでは不十分な場合があるため、アーキテクチャ判断を要する。
- 実施しないこと: rate limit実装そのもの。方式選定なしに特定のlibraryを追加することは行わない。

## 受入条件

- [ ] backend APIのrate limit方針（採用する場合の方式、対象エンドポイント）が決定される。
- [ ] 導入する場合、少なくとも`/admin/provision/users`とJIT provisioning経路が対象に含まれる。

## 検証計画

- 実行する確認: 方針決定・実装後、対象エンドポイントへの過剰requestが期待通り制限されることを統合テストで確認する。
- 期待結果: 制限超過時に一貫した応答（例: 429）を返す。

## 補足

- 発見経緯: SaaSテナント対応マージ後の広範な棚卸し（第6ラウンド）で発見。`01_Plans`内の既存rate-limit言及は、ADR-0059や関連research文書内の「将来rate limitを実装する場合はtenantIdをkeyに含める」という前向きな設計メモのみで、「backendにrate limitがない」という現状のギャップ自体はどこにも記録されていなかった。
