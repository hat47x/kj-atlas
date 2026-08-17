# Issue: SEC-MCP-SCOPE-01 HTTP MCPがread scopeを認可に使用しない

- Type: Security
- Status: Done
- Source Issue: 管理API・MCP・認証／tenant横断モンキーテスト（2026-08-16）
- Priority: P1
- Owner: Maintainer
- Scope: `03_Implement/mcp/src/http_server.ts`, OAuth metadata, HTTP E2E, MCP documentation
- Related ADR/Spec: `ADR-0054`, `EXT-CONN-01`, `THREAT_MODEL.md` §6-1
- Expected verification level: `e2e`

## 課題

HTTP MCPはJWTの署名・issuer・audience・expiryを検証し、`scope` claimも`AuthInfo.scopes`へ格納していたが、`requireBearerAuth`へ`requiredScopes`を渡していなかった。そのため、scopeなし、または`profile`等の無関係scopeしか持たない正規tokenでも`get_context_projection`へ到達できた。認証済みであることを文脈読取の認可と誤認した状態である。

## 対応

- HTTP MCPの全`POST/GET/DELETE /mcp`へ`read:context`を必須化。
- scope不足は401ではなく403 `insufficient_scope`とし、challengeへ必要scopeを含める。
- RFC 9728 protected-resource metadataへ`scopes_supported: ["read:context"]`を追加。
- 正常token、scope欠落、無関係scopeの実HTTP統合testとdogfood HTTP clientを更新。
- stdioはローカルprocess credential境界のため本OAuth scope変更の対象外。`saas-multitenant`はtenant-bound credential未実装のため引き続き起動前に拒否する。

## 受入条件

- [x] 正しい署名・issuer・audienceでも`read:context`が無ければ403になる。
- [x] `read:context`を持つtokenだけがinitialize・tools/list・tool callを完走する。
- [x] discovery metadataと`WWW-Authenticate`が必要scopeを案内する。
- [x] 文書存在確認・backend fetchより前にscope不足を拒否する。
