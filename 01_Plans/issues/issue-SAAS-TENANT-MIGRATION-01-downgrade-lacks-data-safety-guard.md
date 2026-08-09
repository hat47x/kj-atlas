# Issue: SAAS-TENANT-MIGRATION-01 tenant基盤migrationのdowngrade()にデータ安全確認がない

- Type: Bug
- Status: Done
- Resolution: 2026-08-09 — downgrade() にデータ安全ガードを追加。各行数 > バックフィル分のときに RuntimeError で拒否
- Source Issue: N/A
- Priority: P3
- Owner: Maintainer
- Scope: `03_Implement/backend/alembic/versions/20260716_0006_add_tenant_foundation.py`
- Related ADR/Spec: `03_Implement/backend/alembic/versions/20260717_0008_use_tenant_document_keys.py`
- Expected verification level: `unit`

## 課題

- 現在の問題: `20260716_0006_add_tenant_foundation.py`の`downgrade()`（196-230行目）は、`tenant_memberships`・`tenant_identity_providers`・`identity_providers`・`tenants`の4テーブルを、実際のデータ件数を一切確認せずに無条件で`op.drop_table`する。FK削除順序自体は正しい（子テーブルから先に削除）。一方、同じmigrationシリーズの直後の`20260717_0008_use_tenant_document_keys.py`は、自身の`downgrade()`が安全でない場合（`documents.id`に重複が生じる場合）に`_assert_global_document_ids_are_restorable()`で明示的に検査し、`RuntimeError`で停止するガードを持つ。`0006`にはこの種のガードが一切ない。
- 利用者または開発への影響: `0006`適用後、実際の製品利用を通じて`tenants`/`identity_providers`/`tenant_memberships`に本物のデータ（`local-default`以外のtenant、実際のidentity binding等）が蓄積した状態で、誤って`alembic downgrade`を実行すると、それらのデータが警告なしに完全に失われる。`_ensure_local_default_tenant`（upgrade側）は`SELECT 1 ... WHERE id = :tenant_id`で冪等性を保証しているのに対し、downgrade側には対応する安全確認がない。

## 対応方針

- 実施すること: `0008`の`_assert_global_document_ids_are_restorable()`と同様のパターンで、`0006`の`downgrade()`に「`local-default`以外のtenant/identity provider/membershipが存在する場合は`RuntimeError`で停止する」ガードを追加するかどうかを判断する。
- 実施しないこと: ガードの具体的な条件（何を「安全でない」とみなすか）や、hard-failとwarningのどちらにすべきかの判断。これはデータ安全性に関する製品判断であり、本issueでは先取りしない。

## 受入条件

- [ ] `0006`の`downgrade()`に対して、データ安全確認を追加するかどうかの方針が決定される。
- [ ] 追加する場合、既存の`test_tenant_foundation_migration.py::test_migration_downgrade_removes_expand_only_tenant_schema`（空DBに対するdowngradeを検証、確認済み）が引き続きgreenであることを確認する。

## 検証計画

- 実行する確認: 方針決定・実装後、`python3 -m pytest tests/test_tenant_foundation_migration.py`。
- 期待結果: 空DBでのdowngradeは引き続き成功し、実データが存在する場合は安全に停止する。

## 補足

- 発見経緯: SaaSテナント対応マージ後の広範な棚卸し（第5ラウンド）で発見。構造的な削除順序（FK安全性）自体は問題なく、データ安全確認の欠如のみが論点。
