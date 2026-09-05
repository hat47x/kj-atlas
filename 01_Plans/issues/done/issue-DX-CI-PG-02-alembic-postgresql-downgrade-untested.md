# Issue: DX-CI-PG-02 alembic downgrade()のPostgreSQL経路がCIで一切実行されない

- Type: Bug
- Status: Done
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

- [x] PostgreSQL経路のdowngrade検証方針（既存6テストのパラメータ化 or 往復テスト追加）が決定される。
- [x] 決定に応じてCIまたはテストが更新され、`20260717_0007`〜`20260717_0012`のPostgreSQL専用downgrade分岐が実際に一度は実行されることが確認できる。

## 検証計画

- 実行する確認: 実装する場合、`cd 03_Implement/backend && python -m pytest -m postgres -q`（PostgreSQLサービス起動時）。
- 期待結果: PostgreSQL経路でのdowngrade実行が失敗なく完了し、既存のSQLite向けdowngradeテストと同等の表明（drop検証等）が通過する。

## 対応記録（2026-08-21）

第三の方針（c）を採った: 既存6テストのパラメータ化（a）でも、`downgrade base`往復テストの新規追加（b）でもなく、
**既存の`test_oracle_portability.py`/`test_mysql_family_portability.py`/`test_mssql_portability.py`/
`test_cockroachdb_portability.py`と同じ「DB engine別の専用portabilityテストファイル」という確立済みの
規約に倣い、`test_postgres_migration_downgrade_matrix.py`を新規追加した**。理由:

- 4つの他DB engineはいずれもこの規約で0007の downgrade（1ホップ）を検証しているが、**flagshipであり
  既にCI serviceが起動しているPostgreSQLだけがこの規約から漏れていた**——(a)/(b)より、既存規約への
  整合を優先した。
- `alembic downgrade`は指定先まで**間に挟まる全migrationのdowngrade()を順に実行する**ため、
  `head`から`20260716_0006`への**1ホップ**で0012→0011→0010→0009→0008→0007の6件すべての
  postgres専用分岐を実行できる。6テストへの個別パラメータ化（a）は不要だった。
- `.github/workflows/ci.yml`は変更不要——postgres serviceと`pytest -m postgres`ステップは既に存在し、
  新規テストは既存の`KJ_ATLAS_RUN_PG_TESTS`/`KJ_ATLAS_DATABASE_URL`/`KJ_ATLAS_TEST_POSTGRES_CONTAINER`
  契約にそのまま乗る。CI実行時間への追加影響は新規テスト1件の実行時間（ローカル実測 約75秒）のみ。
- 共有`kj_atlas` DB（同一CI jobの他のpostgres-markedテストが前提とするスキーマ）を乱さないため、
  `test_postgres_backup_restore.py`と同じ「`postgres`メンテナンスDBへの管理接続からisolatedな
  databaseを作成・破棄する」パターンを踏襲した。

**ローカルのDocker PostgreSQL 16-alpineコンテナ（CI設定と同一）で実機検証した**:

- 初回実行: 1 passed（約77秒）。
- **変異検査**: (1) 0009 downgradeの`documents`側`DISABLE ROW LEVEL SECURITY`行を削除 → 対応する
  assertionが正確にその行で失敗することを確認。(2) 0007 downgradeの`subject`列drop呼び出しを
  無効化 → 対応するassertionが正確にその行で失敗することを確認。両方とも復元後に元migrationファイルが
  `git status`でクリーンであることを確認した。
- **クリーンアップの信頼性を実機で発見・修正**: 変異検査による失敗実行のうち約半数で、isolated
  databaseが削除されずに残留することを発見した（`DROP DATABASE`が`pg_terminate_backend`の直後でも
  Postgres側のbackendプロセス終了と競合し得るため）。5回・短いbackoff付きのretryを追加し、
  同じ失敗シナリオを再現して残留ゼロを確認した。
- 既存のSQLite向け関連テスト13件（`test_identity_provider_binding_migration.py`等5ファイル＋
  `test_alembic_lineage.py`）に回帰がないことを確認した。
- `ruff check`: All checks passed。

**Scope欄の補足**: `.github/workflows/ci.yml`と既存6テストファイルは実際には変更していない
（新規ファイル1件の追加のみ）。上記のとおり既存CI契約へそのまま乗るため。

## 補足

- 発見経緯: 第19ラウンドの「alembic migration downgrade()正しさ」観点監査で発見。全13migrationファイルのdowngrade()自体は2名の独立検証者によりコード面で正しいことが確認済み（機械的に直すべきバグは0件）。本issueは実装の誤りではなく、テスト・CIカバレッジの欠落を対象とする。
- 別件（既存・未解決）: `20260716_0006_add_tenant_foundation.py`のdowngrade()がデータ件数を確認せず無条件にtenant関連4テーブルをdropする点は、既存の`issue-SAAS-TENANT-MIGRATION-01-downgrade-lacks-data-safety-guard.md`（Status: Draft）で既に追跡済みであり、本issueでは重複して扱わない。
- 軽微な附随所見（未issue化、低優先度）: `20260717_0008_use_tenant_document_keys.py`の`_postgres_downgrade()`が再作成する`documents`のPK/`merge_decision_logs`のFKに、元のmigration（0001/0003）が付与しなかった明示的な名前（`pk_documents_id`/`fk_merge_decision_logs_doc_id`）を新たに与えている。2回目以降のround-tripでは安定するため機能的な問題はなく、カタログのメタデータ表記が変わるだけの美観上の差異。


## 配置の整理（2026-09-05）

- 本Issueは、PostgreSQL固有downgrade経路またはWSL/Node runtime差によって本来の検証が抜ける・起動不能になる問題を、既存CI／E2E契約に沿う検証基盤として解消し、実環境差を含む確認まで終えて `Done` となっていた。一方、R18時点のlegacy集合に含まれたため、完了済みのまま作業中Issueと同じルートへ残っていた。
- 既存のライフサイクル契約に従い、本変更ではverification infrastructure境界の完了済みIssue 2件を `01_Plans/issues/done/` へ移し、`LEGACY_DONE_AT_ROOT_BASELINE` を41から39へ縮小した。
- R18時点のidentity manifestは、新しいDone-at-rootの混入を防ぐ歴史境界なので変更しない。
- 旧rootパスを引用していた箇所は、現在の `done/` パスへ同時に更新した。
