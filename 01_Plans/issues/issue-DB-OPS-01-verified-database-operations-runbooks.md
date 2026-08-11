# Issue: DB-OPS-01 Verified DBの運用runbookと復旧証跡を公開対応範囲へ揃える

- Type: Documentation
- Status: Draft
- Source Issue: DB-PORTABILITY-01
- Priority: P1
- Owner: Maintainer
- Scope: `03_Implement/backend/README.md`, `04_Documentation/installation.md`, `04_Documentation/operations.md`, `04_Documentation/diagnostics.md`, `03_Implement/backend/tests/test_*_portability.py`
- Related ADR/Spec: `01_Plans/adr/ADR-0066-database-portability-capability-registry.md`, `02_Architecture/database_portability.md`, `01_Plans/issues/issue-DATA-MAINT-02-backup-restore-recovery-exercise.md`
- Expected verification level: `integration`

## 課題

- 現在の問題: runtimeと実DBmatrixではSQLite、PostgreSQL、MySQL 8.4、MariaDB 11.4、SQL Server 2022、CockroachDB 26.2、Oracle AI Database 26aiがVerifiedだが、公開運用runbookのバックアップ／復旧手順はSQLiteとPostgreSQLだけを対象としている。残る5製品はpromotion test内にnative backup／restore証跡を持つ一方、導入者が使える最小runbook、必要権限、中断条件、復元後確認へ還元されていない。
- 利用者または開発への影響: 「アプリが接続・migration・CRUDできる」と「運用者が安全に退避・復元できる」の対応範囲が異なる。Verifiedを本番運用保証と誤読する可能性があり、障害時にテストコードから製品固有コマンドを逆算させる状態になっている。

## 対応方針

- 実施すること: DB共通の復旧前提、隔離復元、中断条件、整合確認を一つの共通手順にし、製品固有部分だけをprovider別付録へ分離する。既存promotion testで実行済みのnative tool、権限、container image/versionを証拠として使い、SQLite/PostgreSQLを含む全Verified DBの「検証済み範囲」と「利用者環境で別途決める範囲」を明記する。
- 実施すること: support matrixまたは公開runbookから、各DBの最新復旧演習証跡へ辿れるようにする。新DB昇格時は実DBtestだけでなく公開runbookのprovider節も宣言契約testで必須化する。
- 実施しないこと: 本番環境への自動restore、cloud provider固有のmanaged backup設定、保持期間・暗号鍵・承認者を製品既定として固定すること、アプリからDB管理者権限を行使すること。

## 受入条件

- [ ] 全Verified DBについて、固定検証version、backup方式、隔離restore方式、最小権限または管理権限が必要な箇所、復元後の整合確認が公開runbookから確認できる。
- [ ] 共通手順は本番DBを直接上書きせず、復元先取り違え、schema version不一致、Document／判断ログ欠落、秘密情報を含むログ共有を中断条件に含む。
- [ ] provider固有コマンドは既存の実DBpromotion testまたは再実行した同等環境と一致し、少なくとも一度は隔離restoreまで成功している。
- [ ] `database_portability.md`のVerified backend追加時に、対応するprovider別運用節または明示的な非対応注記が欠ければ通常テストで検出される。
- [ ] SQLite/PostgreSQLの既存手順とSafeMode共有前確認を後退させない。

## 検証計画

- 実行する確認: provider別portability testのbackup／restore部分を固定versionの実DBで再実行し、公開runbookのコマンド・前提・結果と照合する。通常テストでは能力レジストリとprovider別運用節の静的契約を実行する。
- 期待結果: runtime Verified、実DB復旧証跡、公開運用範囲がDBごとに追跡可能になり、未検証の本番保証を表明しない。

## 補足

- DB固有手順をREADME、installation、operationsへ重複記載せず、`operations.md`を公開運用手順の正本として他文書から参照する。
- `DATA-MAINT-02`は当時の正式範囲だったSQLite/PostgreSQLの代表演習としてDoneを維持する。本Issueは後からVerifiedへ昇格したDBの運用文書追随を扱い、過去Issueの完了証跡を書き換えない。
