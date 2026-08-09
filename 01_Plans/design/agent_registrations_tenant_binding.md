# agent_registrations テナントバインディング設計案

- Status: Proposed
- Date: 2026-08-09
- Related: ADR-0059 D10, `api.md` §9.5, SAAS-TENANT-01 AC-7

## 現状

`agent_registrations` テーブルは `docId` のみでテナントバインディングを持たず、
ADR-0059 D10 で「将来対応」とされている。現在は API contract のみ定義され、
実テーブル・エンドポイントは存在しない。

## 提案

### 選択肢 A: `agent_registrations` に `tenant_id` 列を追加（推奨）

```sql
ALTER TABLE agent_registrations ADD COLUMN tenant_id TEXT NOT NULL
  REFERENCES tenants(id) ON DELETE CASCADE;
ALTER TABLE agent_registrations ADD PRIMARY KEY (tenant_id, agent_id);
```

- 全テナントスコープ API と同じ複合キーパターン
- `tenantSessionVersion` precondition が自然に適用される
- 実装コスト: 低（既存パターンの踏襲）

### 選択肢 B: agent をテナント非依存のまま維持

- agent はドキュメント単位で動作するためテナント分離は不要という立場
- テナント越境リスク: 同一 docId が別テナントに存在する場合の誤動作
- 実装コスト: 低（現状維持）だがセキュリティリスクが残る

### 選択肢 C: agent をテナントスコープ + ドキュメントスコープの二重バインディング

- `(tenant_id, doc_id, agent_id)` の 3 要素複合キー
- 最も厳格だが過剰設計の可能性

## 推奨

選択肢 A。ADR-0059 D5/D8 の「すべてのテナント依存データは複合キー」原則に従う。

## 必要な作業

1. migration: `agent_registrations` に `tenant_id` 列追加 + 複合 PK
2. `agent_registrations` テーブルの CRUD repository
3. `POST /agents/register` / `POST /agents/revoke` エンドポイント
4. `require_tenant_session_request_precondition` を agent エンドポイントに適用
5. テスト: tenant A/B agent 分離の unit + E2E

## 判断ポイント

- agent は「テナントに属する」か「ドキュメントに属する」か？
- agent のライフサイクルは誰が管理するか（Platform Admin / Tenant Admin / Document Owner）？
