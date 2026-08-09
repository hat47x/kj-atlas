# Issue: SAAS-TENANT-FK-03 レガシーID紐付け照会がexternal_uidの大文字小文字非依存indexを使えていない

- Type: Bug
- Status: Done
- Resolution: 2026-08-09 — `identity_binding.py:132` の `external_uid` 比較に `func.lower()` を適用。`uq_user_identities_provider_lower_external_uid` インデックスが完全利用可能になった
- Source Issue: N/A
- Priority: P2
- Owner: Maintainer
- Scope: `03_Implement/backend/src/kj_atlas_api/identity_binding.py`
- Related ADR/Spec: `issue-SAAS-TENANT-FK-02-identity-model-missing-case-insensitive-index.md`, `03_Implement/backend/alembic/versions/20260314_0005_enforce_identity_lookup_uniqueness.py`
- Expected verification level: `unit`

## 課題

- 現在の問題:
  - `identity_binding.py:128-136` の `resolve_user_identity()` のレガシーフォールバック照会は次のとおり:
    ```python
    legacy_matches = (
        db.query(UserIdentityRow)
        .filter(
            func.lower(UserIdentityRow.provider) == normalize_provider(provider),
            UserIdentityRow.external_uid == subject,
        )
        .limit(2)
        .all()
    )
    ```
  - `user_identities` テーブルの唯一の大文字小文字非依存indexは `uq_user_identities_provider_lower_external_uid`（`models.py:195-199`、migration `20260314_0005` で導入）であり、`lower(provider)` と **`lower(external_uid)`** の組み合わせに対して定義されている。
  - しかしこの照会は `external_uid` を`lower()`でラップせずに比較している。そのため、当該indexの先頭列（`lower(provider)`）までは絞り込めても、`external_uid` 側の条件はindex式と一致せずindexシークできず、該当providerの行を1件ずつフィルタする必要がある。
  - `resolve_user_identity()` は `resolve_identity_context → _resolve_identity_row` 経由で認証済みリクエストのたびに呼ばれ、`routes/admin.py::provision_user` からも呼ばれる、実質的にすべてのリクエストが通るホットパス。
- 利用者または開発への影響:
  - 単一の主要SSOプロバイダを持つデプロイでは、そのプロバイダの `user_identities` 行数が大きくなるほど、認証済みリクエストごとにこの照会のコストが線形に増加する。

## 対応方針

- 実施すること（人間の設計判断が必要。次のいずれかを選ぶ）:
  - (a) `external_uid` の比較も `func.lower(UserIdentityRow.external_uid) == normalize_provider_agnostic_value(subject)` のように大文字小文字非依存にし、既存indexをそのまま使えるようにする。ただしこれは「レガシーフォールバックの照合は大文字小文字を区別すべきか」という意味論上の判断を伴う（DBの一意性制約自体は既に大文字小文字非依存なので、揃えるのが自然だが、`subject` の由来次第では意図的に区別したい場合もありうる）。
  - (b) 大文字小文字を区別する現状の意味論を維持する場合は、`(provider, external_uid)` の生値に対する index（`uq_user_identities_provider_external_uid` は既に存在するが、`func.lower(provider)` 比較と組み合わせているため、この一意制約だけでは救えない）を見直すか、専用のクエリ経路に分ける。
- 実施しないこと:
  - `user_identities` テーブル・migrationの再設計（本issueは既存indexとクエリ述語の不一致という一点に閉じる）。

## 受入条件

- [ ] `resolve_user_identity()` のレガシーフォールバック照会が、既存の `uq_user_identities_provider_lower_external_uid` indexを実際に利用できる形になる（またはそれに相当する適切なindexが追加される）。
- [ ] 大文字小文字の区別に関する意味論の変更がある場合、既存の認証テスト（`test_auth_context_resolution.py` 等）で明示的に検証される。
- [ ] 関連する安全・互換性を損なわない。
- [ ] 宣言した検証を実行するか、未実施理由を記録する。

## 検証計画

- 実行する確認:
  - `python -m pytest tests/test_auth_context_resolution.py tests/test_auth_jit_provisioning.py tests/test_identity_lookup_uniqueness_migration.py -q`
  - 採用した方針に応じたクエリプラン確認（`EXPLAIN`）または新規テストの追加。
- 期待結果:
  - 既存テストが継続して通過し、レガシー照会がindexを利用できることを確認する。

## 補足

- 依存・リスク・ロールバックがある場合だけ記載する。
  - `SAAS-TENANT-FK-02` はORMモデルとDB migrationのindex宣言の不一致を修正済みだが、本issueはその修正後もなお残る「クエリ述語とindex式の不一致」という別の問題である。

---
