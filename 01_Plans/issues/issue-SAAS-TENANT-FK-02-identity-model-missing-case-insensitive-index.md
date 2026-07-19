# Issue: SAAS-TENANT-FK-02 UserIdentityRowモデルに大文字小文字非依存の一意インデックスが宣言されていない

> 個人OSS・プレリリース段階では `ADR-0039` を適用し、実行に必要な情報だけを記載する。

- Type: Bug
- Status: Draft
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P3
- Owner: Maintainer
- Scope: `03_Implement/backend/src/kj_atlas_api/models.py`, `03_Implement/backend/tests/test_auth_context_resolution.py`, `03_Implement/backend/tests/test_auth_jit_provisioning.py`
- Related ADR/Spec: `03_Implement/backend/alembic/versions/20260314_0005_enforce_identity_lookup_uniqueness.py`
- Expected verification level: `unit`

## 課題

- 現在の問題: migration`20260314_0005_enforce_identity_lookup_uniqueness.py`は、`user_identities`テーブルに`(lower(provider), lower(external_uid))`の大文字小文字非依存な一意functional indexを実際にDBへ作成する。しかし`models.py`の`UserIdentityRow.__table_args__`はこのindexを一切宣言しておらず（大文字小文字を区別する`UniqueConstraint("provider", "external_uid", ...)`のみ）、ORMモデルは実際のDBスキーマを正しく反映していない。
- 利用者または開発への影響: 直接的な実害はない（実DBは既にmigrationによってこの制約を持つ）。ただし、`models.py`を読んでスキーマを理解する開発者はこの制約の存在に気づけない。加えて、`test_auth_context_resolution.py`の`test_resolve_identity_context_raises_conflict_for_duplicate_provider_subject`と`test_auth_jit_provisioning.py`の`test_admin_provision_rejects_ambiguous_identity_mapping`/`test_docs_strict_mode_rejects_ambiguous_identity_mapping`の3テストは、`Base.metadata.create_all()`（実migrationを介さないfixture構築）を使い、意図的に大文字小文字違いの重複識別（例: `provider="oidc"`と`provider="OIDC"`、同じ`external_uid`）をORM経由で挿入して、アプリケーション層の「曖昧な識別マッピング」検出ロジック（レガシーデータ・移行前データを想定した多層防御）を検証している。もし`models.py`にこのindexを追加すると、これら3テストのfixture構築自体がDB制約違反で失敗し、テストが検証しようとしているアプリケーション層の防御ロジックへ到達できなくなることを確認済み。
- 試行錯誤の経緯: 本セッションで実際に`models.py`へ当該indexを追加してみたところ、上記3テストが新たに失敗することを確認し、モデルとテストの整合を取らずに変更を反映することは安全でないと判断して差し戻した。

## 対応方針

- 実施すること: `models.py`にこのindexを追加する場合、上記3テストのfixture構築方法を、実migrationを経由する（例: 既存の`test_identity_lookup_uniqueness_migration.py`のようにalembicを実行する）か、あるいは当該テストのengineでこの特定indexだけを作成しないようにする、いずれかの方法へ更新する必要がある。どちらの方法を採るか、またはアプリケーション層の「曖昧な識別マッピング」防御ロジック自体が、DBが完全にmigrate済みの環境ではもはや到達不能な防御であることを踏まえてテストの前提を見直すべきかは、テスト設計方針の判断を要する。
- 実施しないこと: 本issueではmodels.pyの変更、テストの変更のいずれも行わない。

## 受入条件

- [ ] `models.py`のindex追加とテストのfixture方法変更を同時に行う方針が決定される。
- [ ] 変更後、既存の3テストを含む全テストがgreenであることを確認する。

## 検証計画

- 実行する確認: 方針決定・実装後、`python3 -m pytest tests/test_auth_context_resolution.py tests/test_auth_jit_provisioning.py`。
- 期待結果: モデルが実DBスキーマを正しく反映しつつ、既存の防御ロジックのテストも引き続き意味のある形で検証される。

## 補足

- 発見経緯: SaaSテナント対応マージ後の広範な棚卸し（第4ラウンド）で発見。当初「モデルをDBの実態に合わせるだけの機械的な修正」と見えたが、実際に適用してみたところ既存テストとの整合性問題が判明したため、本issueとして記録した。
