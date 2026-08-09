# Issue: DB-PORTABILITY-01 DB能力レジストリと段階的な多DB対応

- Type: Architecture / Feature
- Status: In Progress
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: User request 2026-08-09
- Priority: P2
- Scope: `03_Implement/backend/`, Alembic migration, database CI, configuration documentation
- Related ADR/Spec: `ADR-0066`, `ADR-0059`, `02_Architecture/database_portability.md`, `02_Architecture/runtime_parameter_registry.md`
- Expected verification level: integration / real database

## 課題

- SQLAlchemyが認識するdialectを、そのままkj-atlasの正式対応DBとは扱えない。
- 現行の無制限`TEXT`主キー・索引とSQLite/PostgreSQL専用migrationは、MySQL/MariaDB等で成立しない。
- DB追加ごとにruntime・migration・CIへ個別条件を散らすと、将来候補が増えるほど保守不能になる。

## 対応方針

- DB backendの対応状態、family、migration strategy、共有SaaS可否を単一レジストリへ集約する。
- 未検証candidateは資格情報を反射せず、engine生成・migration開始前に拒否する。
- 次段階でidentifierとcontentの型を分離し、MySQL/MariaDB familyのmigrationと実DBmatrixを追加する。
- SQL Server、Oracle、CockroachDBは同じ昇格手順を再利用し、需要に応じて順序を変更できるようにする。

## 受入条件

- [x] AC-1: SQLite/PostgreSQLのverified状態とmigration strategyが一か所で定義される。
- [x] AC-2: MySQL/MariaDB、SQL Server、Oracle、CockroachDBがcandidateとして分類され、runtimeではfail-fastになる。
- [x] AC-3: DB URLエラーがcredentialやURL全体を反射しない。
- [ ] AC-4: identifier/index文字列がbounded portable型へ移行され、SQLite/PostgreSQL回帰が通る。
- [ ] AC-5: MySQL/MariaDBでfresh migration、roundtrip、複合制約、upgrade/downgradeが実DBで通る。
- [ ] AC-6: 公開文書でMySQL/MariaDBをverifiedへ昇格し、driver optional dependencyとCIを追加する。
- [ ] AC-7: 将来candidateの追加が既存repository/APIへDB固有分岐を増やさず、同じ検証契約を再利用できる。
- [x] AC-8: shared-schema SaaSはPostgreSQL限定を維持し、candidate追加で安全条件を緩和しない。

## 検証計画

- capability registryとURL validationのunit test。
- SQLite/PostgreSQLの既存migration・roundtrip回帰。
- candidate昇格時は一時的な実DB containerでfresh/upgrade/downgrade/constraint/CRUDを検証する。
- SafeMode、proposal-only、share/export/importには変更を加えない。

## Phase 1 checkpoint 2026-08-09

- `database_support.py`へverified/candidate、DB family、migration strategy、shared-schema SaaS可否を集約した。
- Settings、engine生成、Alembicが利用するURL正規化を同じverified判定へ接続した。未知DBとcandidateはdriver接続前に停止し、エラーへ接続URL・user・passwordを含めない。
- MySQL/MariaDBを同一familyとして登録し、SQL Server、Oracle、CockroachDBも将来候補として同じ昇格手順へ載せた。現行TEXT主キー・索引がMySQL系で成立しないため、未検証のまま接続だけ許可する対応は行っていない。
- SQLite/PostgreSQLだけを正式対応、共有schema SaaSはPostgreSQLだけとする既存境界を維持した。AC-4〜7は後続段階として残す。
- 検証はdatabase registry／Settings／trusted SaaS runtime近接72件、SQLite tenant-key migration 2件、変更対象Ruff、Active issue validator 60件を通過した。backend全体は791件pass・25件skip・10件deselectで、今回と無関係な既存`ProposalDecisionAuditResponse` field不整合1件だけが単独再実行でもfailした。docs-checkも既存`KJ_ATLAS_LLM_TASK_MODEL_MAP`のruntime registry未登録1件でfailしており、本issueでは別領域の修正を混在させない。
