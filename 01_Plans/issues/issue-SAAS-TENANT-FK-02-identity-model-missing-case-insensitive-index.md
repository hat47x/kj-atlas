# Issue: SAAS-TENANT-FK-02 UserIdentityRowモデルに大文字小文字非依存の一意インデックスが宣言されていない

> 個人OSS・プレリリース段階では `ADR-0039` を適用し、実行に必要な情報だけを記載する。

- Type: Bug
- Status: Done
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P3
- Owner: Maintainer
- Scope: `03_Implement/backend/src/kj_atlas_api/models.py`, `03_Implement/backend/tests/test_auth_context_resolution.py`, `03_Implement/backend/tests/test_auth_jit_provisioning.py`, `03_Implement/backend/tests/test_identity_lookup_uniqueness_migration.py`
- Related ADR/Spec: `03_Implement/backend/alembic/versions/20260314_0005_enforce_identity_lookup_uniqueness.py`
- Expected verification level: `unit`

## 課題

- migration `20260314_0005_enforce_identity_lookup_uniqueness.py` は `user_identities` に `(lower(provider), lower(external_uid))` の一意functional indexを作成するが、`UserIdentityRow.__table_args__` に同じindexがなく、ORMモデルと実DBスキーマが一致していなかった。
- 一方、3件の認証テストは移行前・破損データに対するアプリケーション層の曖昧マッピング検知を確認するため、意図的に大文字小文字違いの重複を作成していた。ORMへindexを追加するだけではfixture構築時にDB制約で停止し、多層防御の検証へ到達できない。

## 対応

- `UserIdentityRow` にmigrationと同名・同式の一意index `uq_user_identities_provider_lower_external_uid` を宣言し、`Base.metadata.create_all()` で構築するDBも実スキーマと同じ制約を持つようにした。
- 曖昧マッピング検知の3テストに限り、専用fixture引数 `allow_legacy_ambiguous_identities=True` を明示して当該indexだけを削除し、移行前・破損データを再現するようにした。通常のfixtureは制約を保持する。
- ORM宣言のindex名、一意性、2つの `lower(...)` 式を確認する近接テストを追加した。DB側の導入・重複拒否・downgradeは既存migrationテストで引き続き確認する。
- 既に適用済みのmigrationが同じDB制約を持つため、新しいmigrationは追加しない。

## 受入条件

- [x] ORMモデルが実DBの大文字小文字非依存一意indexを宣言する。
- [x] 通常の新規テストDBにも同indexが作成される。
- [x] 移行前・破損データに対するアプリケーション層の競合検知を、明示的な専用fixtureで継続検証する。
- [x] 認証とidentity lookup migrationの近接テストがgreenである。

## Validation

- `python -m pytest tests/test_auth_context_resolution.py tests/test_auth_jit_provisioning.py tests/test_identity_lookup_uniqueness_migration.py -q`: 25 passed。
- `ruff check src/kj_atlas_api/models.py tests/test_auth_context_resolution.py tests/test_auth_jit_provisioning.py tests/test_identity_lookup_uniqueness_migration.py`: passed。
- `python 01_Plans/docs_check.py --root .`: passed。
- `python 01_Plans/issues/validate_active_issue_memos.py --root .`: passed。
