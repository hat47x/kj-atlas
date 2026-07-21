# Issue: DX-CI-PG-02 alembic downgrade()のPostgreSQL経路がCIで一切実行されない

> 個人OSS・プレリリース段階では `ADR-0039` を適用し、実行に必要な情報だけを記載する。

- Type: Bug
- Status: Draft
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P3
- Owner: Maintainer
- Scope: `.github/workflows/ci.yml`, `03_Implement/backend/tests/test_tenant_foundation_migration.py`, `test_identity_provider_binding_migration.py`, `test_document_tenant_key_migration.py`, `test_document_access_metadata_migration.py`, `test_document_access_admin_audit_migration.py`, `test_identity_lookup_uniqueness_migration.py`
- Related ADR/Spec: N/A
- Expected verification level: `integration`

## 課題

- 現在の問題: `03_Implement/backend/alembic/versions/`配下の13件のmigrationのうち、`20260717_0007`〜`20260717_0012`の6件（tenant identity provider binding・tenant document key repointing・document access metadata・document access admin audit・RLS enablement群）は、`downgrade()`内にSQLite/PostgreSQLで分岐する専用コード（FK削除順序・`DROP POLICY`/`NO FORCE`/`DISABLE ROW LEVEL SECURITY`等）を持つ。これらを実際に検証する`downgrade`実行テストは6ファイル存在するが、いずれも`_run_alembic`ヘルパー内で`env["KJ_ATLAS_DATABASE_URL"]`を`sqlite:///...`へ無条件に上書きしており、**PostgreSQL側のdowngrade分岐は一度も実行されたことがない**。`.github/workflows/ci.yml`のPostgreSQLジョブ相当ステップは`alembic upgrade head`を実PostgreSQLサービスに対して実行するが、`downgrade`という文字列は`ci.yml`・`release.yml`のどちらにも一度も現れない。
- 利用者または開発への影響: 手動で読んだ限り現在のdowngradeコードは正しいが、将来の変更でPostgreSQL専用分岐（ポリシー名・制約名等）にtypoが入っても、CIは一切検知できない。「めったに実行されないdowngrade経路が静かに劣化する」典型的なリスク。
- 判断が必要な理由: 対応方法が複数あり（(a) 既存6テストの`_run_alembic`ヘルパーをパラメータ化し、CIで既に起動済みのPostgreSQLサービスに対しても実行する、(b) 別途「`alembic downgrade base && alembic upgrade head`」という往復テストをPostgreSQL CIステップへ追加する）、CI実行時間への影響とテスト設計をどちらの方針にするかはMaintainerの判断が必要。

## 対応方針

- 実施すること: 上記(a)/(b)のいずれの方針を採るかをMaintainerが決定する。
- 実施しないこと: 方針が決まる前に、テストヘルパーを機械的に変更すること（CI実行時間・並列実行時のDB分離等、決定前に考慮すべき点があるため）。

## 受入条件

- [ ] PostgreSQL経路のdowngrade検証方針（既存6テストのパラメータ化 or 往復テスト追加）が決定される。
- [ ] 決定に応じてCIまたはテストが更新され、`20260717_0007`〜`20260717_0012`のPostgreSQL専用downgrade分岐が実際に一度は実行されることが確認できる。

## 検証計画

- 実行する確認: 実装する場合、`cd 03_Implement/backend && python -m pytest -m postgres -q`（PostgreSQLサービス起動時）。
- 期待結果: PostgreSQL経路でのdowngrade実行が失敗なく完了し、既存のSQLite向けdowngradeテストと同等の表明（drop検証等）が通過する。

## 補足

- 発見経緯: 第19ラウンドの「alembic migration downgrade()正しさ」観点監査で発見。全13migrationファイルのdowngrade()自体は2名の独立検証者によりコード面で正しいことが確認済み（機械的に直すべきバグは0件）。本issueは実装の誤りではなく、テスト・CIカバレッジの欠落を対象とする。
- 別件（既存・未解決）: `20260716_0006_add_tenant_foundation.py`のdowngrade()がデータ件数を確認せず無条件にtenant関連4テーブルをdropする点は、既存の`issue-SAAS-TENANT-MIGRATION-01-downgrade-lacks-data-safety-guard.md`（Status: Draft）で既に追跡済みであり、本issueでは重複して扱わない。
- 軽微な附随所見（未issue化、低優先度）: `20260717_0008_use_tenant_document_keys.py`の`_postgres_downgrade()`が再作成する`documents`のPK/`merge_decision_logs`のFKに、元のmigration（0001/0003）が付与しなかった明示的な名前（`pk_documents_id`/`fk_merge_decision_logs_doc_id`）を新たに与えている。2回目以降のround-tripでは安定するため機能的な問題はなく、カタログのメタデータ表記が変わるだけの美観上の差異。
