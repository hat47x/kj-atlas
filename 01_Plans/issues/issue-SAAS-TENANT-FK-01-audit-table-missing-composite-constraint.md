# Issue: SAAS-TENANT-FK-01 監査テーブルにtenant複合外部キー制約がない

> 個人OSS・プレリリース段階では `ADR-0039` を適用し、実行に必要な情報だけを記載する。

- Type: Bug
- Status: Draft
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P2
- Owner: Maintainer
- Scope: `03_Implement/backend/src/kj_atlas_api/models.py`, `03_Implement/backend/alembic/versions/20260717_0011_add_document_access_admin_audit.py`
- Related ADR/Spec: `01_Plans/adr/ADR-0059-saas-tenant-authorization-boundary.md`, `01_Plans/issues/issue-SAAS-TENANT-01-tenant-context-and-storage-foundation.md`
- Expected verification level: `integration`

## 課題

- 現在の問題: `ADR-0059`のD7は「Document従属表はtenantIdを重複保持し、`(tenantId, docId)`の複合外部キーで親へ接続する。docIdだけのjoin、更新、削除をrepository APIで提供しない」と定める。`issue-SAAS-TENANT-01`のAC-3（`[x]`済み）はこれに対応して「`documents`と全Document従属表がtenant複合制約を持ち」と記載している。しかし実装を確認すると、`DocumentAccessMetadataRow`（`models.py`）は`ForeignKeyConstraint(["tenant_id", "doc_id"], ["documents.tenant_id", "documents.id"])`を持つ一方、同じくDocument従属表である`DocumentAccessAdminAuditEventRow`は`tenant_id`に対する単純な`ForeignKey("tenants.id")`のみを持ち、`doc_id`列（`Text`型）には外部キー制約が一切ない。対応するmigration（`20260717_0011_add_document_access_admin_audit.py`）でも同様に`tenant_id`単体の制約しか定義されていない。
- 利用者または開発への影響: 現時点で`DocumentAccessAdminAuditEventRow`への挿入箇所は`routes/document_access_admin.py`の1箇所のみで、`tenant_id`と`doc_id`を常に同じtenant-scopedな値の組で渡しており、実際に他tenantの`doc_id`が混入する経路は確認されなかった。ただし、DB自体はこの制約を持たないため、AC-3が主張する「複合制約を持つ」という保証はこのテーブルには存在しない。将来のコード変更がこの前提を壊しても、DBレベルでは検出されない。

## 対応方針

- 実施すること: `DocumentAccessAdminAuditEventRow`に`(tenant_id, doc_id) -> (documents.tenant_id, documents.id)`の複合外部キー制約を追加するかどうかをMaintainerが判断する。
- 実施しないこと: 制約の追加そのもの。追加する場合の`ondelete`挙動（監査証跡が文書削除後も残るべきか、他の2表と同じ`CASCADE`に揃えるべきか）はコンプライアンス上の判断を伴い、コーディングエージェントが独断で選ぶべきではない。また、`issue-SAAS-TENANT-01`のAC-3チェック状態自体の修正も、当該issueが他セッションにより活発に編集中のため本issueでは行わない。

## 受入条件

- [ ] `DocumentAccessAdminAuditEventRow`のtenant/doc複合制約について、追加する/しないの方針が決定される。
- [ ] 追加する場合、既存の監査挿入経路（`routes/document_access_admin.py`）を壊さずmigrationが追加され、テストがgreenであることを確認する。

## 検証計画

- 実行する確認: 方針決定・実装後、`python3 -m pytest tests/test_document_access_admin_audit_migration.py`等の関連テスト。
- 期待結果: 複合制約追加後も既存の監査記録フローが正常に動作する。

## 補足

- 発見経緯: SaaSテナント対応マージ後の広範な棚卸し（第3ラウンド）で、ADR-0059の各ゲート条件と実装の突き合わせにより発見。他の複数のゲート条件（`saas-multitenant`のfail-fast、`GET /session/context`等のroute契約、Postgres RLSテストの権限要件）は突き合わせの結果、乖離なしと確認済み。
