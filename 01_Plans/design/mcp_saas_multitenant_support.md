# MCP saas-multitenant 対応 設計案

- Status: Proposed
- Date: 2026-08-09
- Related: ADR-0059, ADR-0054, `03_Implement/mcp/`, THREAT_MODEL §6-1

## 現状

MCP (Model Context Protocol) サーバは TypeScript 実装（`03_Implement/mcp/src/http_server.ts`）で、
OAuth 2.1 Resource Server として Bearer token 検証を行う。しかし `saas-multitenant` プロファイルでは
起動時に `resolve_tenant_session_bootstrap_mode` が `tenant-session-required` を返すと起動拒否される。

現在の MCP は single-tenant 想定で：
- `KJ_ATLAS_MCP_TRUSTED_ISSUER`（単一 issuer）
- `KJ_ATLAS_MCP_JWKS_URI`（単一 JWKS エンドポイント）
- `KJ_ATLAS_MCP_RESOURCE_URL`（保護リソース URL）

テナント識別や `tenantSessionVersion` precondition は実装されていない。

## 提案

### 選択肢 A: MCP に `tenantSessionVersion` precondition を追加（推奨）

```
Client → MCP Server
  Header: Authorization: Bearer <JWT>
  Header: Kj-Atlas-Tenant-Session-Version: <version>

MCP Server:
  1. JWT 検証（既存の OAuth 2.1 RS ロジック）
  2. tenant_ref claim 抽出
  3. tenantSessionVersion 検証（Backend API を呼び出し）
  4. テナントスコープでリソースアクセス
```

- Backend の `resolve_trusted_saas_request_session` を MCP から呼び出す
- または MCP が直接 `identity_providers` / `tenant_identity_providers` を参照
- 実装コスト: 中（MCP の TypeScript 実装修正 + Backend API 追加）

### 選択肢 B: MCP を single-tenant 専用のまま維持

- `saas-multitenant` では MCP を無効化
- SaaS デプロイメントでは MCP の代わりに別の API を提供
- 実装コスト: 低（現状維持）
- 機能制限: MCP クライアントが SaaS で使えない

### 選択肢 C: MCP のテナント分離を Backend プロキシで実現

```
Client → Backend (/mcp/* proxy) → MCP Server (localhost only)
```

- Backend がテナント検証を行い、検証済みリクエストだけを MCP に転送
- MCP 自体は single-tenant のまま
- 実装コスト: 中（Backend にプロキシエンドポイント追加）

## 推奨

選択肢 C（Backend プロキシ）。MCP サーバ自体の変更を最小限に抑えつつ、
既存の Backend テナント検証インフラを再利用できる。

## 必要な作業（選択肢 C）

1. Backend に `/mcp/{path}` プロキシエンドポイント追加
2. `require_tenant_scoped_api_precondition` を適用
3. 検証済みテナントコンテキストを MCP リクエストヘッダーに注入
4. MCP サーバを localhost のみで listen するよう変更
5. テスト: tenant A/B プロキシ分離

## 判断ポイント

- MCP は SaaS で必須か？それとも single-tenant 専用でよいか？
- プロキシアプローチのレイテンシ・複雑性は許容範囲か？
- MCP の OAuth 2.1 RS 実装と Backend の JWT 検証の二重実装を統合すべきか？
