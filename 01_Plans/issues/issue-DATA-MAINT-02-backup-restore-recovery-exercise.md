# Issue Draft: DATA-MAINT-02 バックアップ/復旧演習の標準検証

- Type: Process
- Status: Done
- Source Issue: N/A
- Priority: P1
- Owner: Codex
- Scope: `01_Plans/issues/issue-DATA-MAINT-02-backup-restore-recovery-exercise.md`, `03_Implement/backend/`, `04_Documentation/operations.md`, `04_Documentation/data_handling.md`
- Related Backlog: `DATA-MAINT-02`
- Related ADR/Spec: `01_Plans/issues/issue-DATA-MAINT-01-admin-maintenance-and-recovery-operations.md`, `01_Plans/adr/ADR-0033-mvp-data-support-and-maintenance-boundary.md`, `01_Plans/adr/ADR-0019-e2e-verification-policy-and-compose-runbook.md`, `02_Architecture/data_model_operations_overview.md`, `04_Documentation/operations.md`
- Expected verification level: `integration`

## Requirement meta I/F（共通キー）

- RequirementID: DATA-MAINT-02
- RequirementStatement: MVPのDocument保存と判断ログについて、隔離環境でバックアップ、復元、整合確認を行う代表演習を定義し、製品化判断に使える証跡として残せるようにする。
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=Platform operatorが検証環境でkj-atlasの永続DBを扱う / 操作=代表Documentと`merge_decision_logs`を作成し、バックアップ、復元、整合確認を行う / 期待結果=復元後のDocument、判断ログ、共有前安全確認が破綻していないことを説明できる / 除外=本番DBへの破壊的restore、法域別保持期限の自動判定、削除/所有者移管の製品実装。
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: SafeMode / share-export / public-exposure

## Dependency graph（DATA-MAINT）

- Upstream（先行固定）: `DATA-MAINT-01`（管理・復旧・棚卸し境界）, `ADR-0033`（MVPデータサポート境界）
- Parallel（並行整備）: `PRODUCT-QA-01`（製品化品質ゲート）, `PROJECT-BASELINE-01`（最新main健康状態ベースライン）
- Downstream（後続依存）: `PRODUCT-OPS-01`（サポート/診断導線）, 必要に応じた復旧runbook実装issue
- Blocker条件: バックアップ/復旧が本番データを対象にしそうな場合、または本文閲覧、削除、所有者移管、保持期限を演習内で方針固定しようとした場合は停止し、ADRまたは別issueへ分離する。

## 1) 課題 / Problem statement

- `DATA-MAINT-01` は管理・復旧・棚卸しの境界を整理したが、代表的な復旧演習そのものは未完了である。
- MVPは全データ構造を完全にメンテナンスする段階ではないため、復旧演習では「何を復元できたら十分か」と「何を復元保証と誤解してはいけないか」を分ける必要がある。
- 公開向け文書では、各組織が決めるべき保持期間、暗号化、保管先、承認手順を過度に規定せず、判断を支援する情報として提示する必要がある。

## 2) 背景 / Context

- `documents` はDocument全体を保存するMVP正本であり、`merge_decision_logs` は判断ログとしてDocumentに従属する。
- 復旧時には `Document.version`、schema version gate、判断ログの時系列、SafeMode/共有前確認の安全境界を同時に確認する必要がある。
- SQLiteとPostgreSQLは利用環境が異なるため、演習はDB種別ごとの差を記録しつつ、組織固有のバックアップポリシーを製品標準として押し付けない。

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: 利用者が思考の途中状態を安心して保存するには、運用者が復旧可能性を説明できる必要がある。
- 安全（THREAT_MODEL / SafeMode）: バックアップや支援情報の共有で、未レビュー本文や個人情報を不要に広げない確認が必要である。
- 企業・行政要件（enterprise_architecture）: 導入前の検収では、復旧演習の証跡、失敗時のエスカレーション、責任分担が求められる。
- 後方互換（schemas）: 復元後のDocumentがversion gateとsupport level境界を満たすかを確認する必要がある。

## 4) 提案する解決策 / Proposed solution

- 変更対象:
  - 代表Documentと判断ログを用いたバックアップ/復旧演習。
  - SQLite/PostgreSQL別の実行可否、コマンド、代替検証、再開条件の記録。
  - 公開向け運用文書には、判断支援に必要な最小説明のみを反映する。
- 変更の最小単位:
  - まずSQLiteの隔離環境で、Document作成、判断ログ追記、DB退避、復元、整合確認を1本の再現可能な手順にする。
  - PostgreSQLはcompose環境で実行できる場合に演習し、実行できない場合は未実施理由と再開条件を残す。
- 非目標:
  - 本番DBへ直接restoreすること。
  - 削除、アーカイブ、所有者移管、保持期限を本Issueで仕様確定すること。
  - サポート担当が利用者本文を横断閲覧できる管理機能を作ること。

## 5) 受入条件 / Acceptance criteria

- [x] 代表Documentと`merge_decision_logs`を持つ検証データを隔離環境で作成できる。
- [x] SQLiteのバックアップ/復元演習が、コマンド、入力、期待結果、失敗時の中断条件つきで記録されている。
- [x] PostgreSQLのバックアップ/復元演習が実行されるか、未実施理由と再開条件が明記されている。
- [x] 復元後に `Document.version`、schema version gate、`merge_decision_logs.doc_id`、判断ログ順序、L1/L1.5優先復旧を確認できる。
- [x] 復旧後の共有前確認で、SafeMode既定ON、PII抑制、未レビュー本文の扱いが破綻していないことを確認できる。
- [x] 一般公開向け文書では、保持期間、暗号化、外部保管、承認手順を各組織の判断事項として扱い、必要以上に細かい規定にしない。
- [x] 演習中に削除、所有者移管、管理者本文閲覧、法域別保持期限の方針固定が必要になった場合は、ADRまたは別issueへ分離されている。

## 6) 実装タスク分解 / Task breakdown

- [x] T1 backendのDocument保存、判断ログ、SQLite/PostgreSQL設定、テストfixtureを確認する。
- [x] T2 SQLite隔離環境で、Document作成からbackup/restore/整合確認までの代表演習を実行または自動化する。
- [x] T3 PostgreSQL compose環境で同等演習を実行し、難しい場合は阻害要因と再開条件を記録する。
- [x] T4 `04_Documentation/operations.md` と `04_Documentation/data_handling.md` に、一般向けに必要な最小限の判断支援情報を反映する。
- [x] T5 `DATA-MAINT-01`、`PRODUCT-QA-01`、必要なADR/issueへ結果を戻す。

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `git diff --check -- 01_Plans/issues 04_Documentation 03_Implement/backend`
  - `python 01_Plans/issues/validate_active_issue_memos.py`
  - `python -m unittest 01_Plans/issues/tests/test_validate_active_issue_memos.py`
  - `python 01_Plans/triage_actionable_plans.py`
  - `cd 03_Implement/backend && .\\.venv\\Scripts\\python.exe -m pytest <復旧演習対象テスト> -q --basetemp .pytest_tmp_data_maint_02 -p no:cacheprovider`
- 期待結果:
  - 復旧演習の成否、未実施理由、再開条件が、製品化判断に使える粒度で残る。
  - 公開向け文書が、組織ごとの運用判断を支援しつつ、過度に細かい規定へ踏み込まない。
- 未実施時の理由・代替検証:
  - PostgreSQLやcomposeが利用できない場合は、SQLite演習、既存API結合テスト、コマンド案レビューを代替証跡とし、PostgreSQL演習の再開条件を記録する。

## 8) 代替案 / Alternatives considered

- 代替案A: 公開文書にDBコマンドだけを詳しく書く。却下理由: 組織ごとのバックアップ方針や権限設計を飛び越え、誤操作を誘発する。
- 代替案B: CIの単体テストだけで復旧可能とみなす。却下理由: 実際のDB退避/復元、判断ログ整合、SafeMode共有前確認の横断証跡が残らない。
- 代替案C: 管理UI実装を先に行う。却下理由: 認可、監査、削除/所有者移管の判断が未確定のまま管理導線が先行する。

## 9) リスクとロールバック / Risks & rollback

- 失敗モード: 復旧演習が本番restore手順と誤読される。
- 影響範囲: backendテスト、DB設定、運用文書、公開文書、製品化品質ゲート。
- ロールバック手順: 演習手順を隔離環境限定に戻し、公開文書から実行コマンドの断定表現を削除する。実装差分がある場合は、復旧演習テストと文書更新を別コミットへ分離して戻す。

## 10) Additional context

- ADR化が必要になる条件: 削除、アーカイブ、所有者移管、管理者本文閲覧、保持期限、外部保管、暗号化方式を製品標準として固定する場合。
- 本Issueは、`DATA-MAINT-01` のT5「代表的な復旧演習」を実行可能な単位に分解するための後続issueである。

## 11) 起票ログ（2026-05-24）

### Context

- `DATA-MAINT-01` の境界整理により、読み取り中心の棚卸しとバックアップ/復旧演習は必要だが、書き込み系管理操作はADR前に実装しない方針が確認された。
- 代表的な復旧演習は `docs-check` では不足し、backendの永続化と運用文書を横断する `integration` レベルの証跡が必要である。

### Decision

- `DATA-MAINT-02` をOpen issueとして起票し、SQLite/PostgreSQL別の演習、Document/判断ログ整合、SafeMode共有前確認、公開文書の書きぶりを追跡する。
- 保持期間、暗号化、外部保管、承認手順は、各組織が検討する判断事項として扱い、製品標準として固定しない。

### Consequences

- `DATA-MAINT-01` のT5は、本Issueの実行結果を受けて完了判定する。
- PostgreSQL演習やcomposeが実行できない場合でも、未実施理由と再開条件を残すことで、製品化ゲートの未達項目として扱える。

## 12) 復旧演習レコード（2026-05-25）

### Candidate

- 対象: SQLite隔離DBでの Document + `merge_decision_logs` 復旧演習。
- 追加証跡: `03_Implement/backend/tests/test_data_maintenance_recovery_exercise.py`
- 公開文書反映: `04_Documentation/operations.md`, `04_Documentation/data_handling.md`
- Executor: Codex
- Environment: Windows / PowerShell / backend `.venv`

### 実行内容

| Area | Command / Evidence | Result | Gate mapping |
| --- | --- | --- | --- |
| Backend integration | `cd 03_Implement/backend && .\.venv\Scripts\python.exe -m pytest tests\test_data_maintenance_recovery_exercise.py -q --basetemp .pytest_tmp_data_maint_02 -p no:cacheprovider` | Pass: 1 test | DATA-MAINT-02 / G6 / G7 |
| Backend regression | `cd 03_Implement/backend && $env:Path="$PWD\.venv\Scripts;$env:Path"; .\.venv\Scripts\python.exe -m pytest --basetemp .pytest_tmp_data_maint_02_full -p no:cacheprovider` | Pass: 257 passed / 19 skipped | G7 |
| SQLite backup/restore | test内で source SQLite DB に代表Documentと判断ログを作成し、`sqlite3.Connection.backup()` で退避後、別DBとして復元 | Pass: 復元先でDocumentと判断ログをAPI経由で確認 | L1 / L1.5 |
| Document consistency | 復元後 `GET /docs/{doc_id}` | Pass: `version=2`, `id`, card review flags, embedded merge suggestion decisionを確認 | schema version gate / L1 |
| Decision log consistency | 復元後 `GET /docs/{doc_id}/merge-decision-logs/by-group/{group_id}` と `/restore/{snapshot_version}` | Pass: `decision-1`, `decision-2` と `accept`, `partial` の順序を確認 | L1.5 |
| Safe sharing gate | 復元後 `POST /docs/{doc_id}/export-audit` with `safeMode=true` | Pass: `403 Access denied: safe_mode` | SafeMode / share-export |
| PostgreSQL toolchain | WSL2 `docker --version`; `docker compose version` | Pass: Docker 28.3.3 / Compose v2.39.1 | PostgreSQL実行条件 |
| PostgreSQL schema | temporary PostgreSQL 16.14 container + `alembic upgrade head` | Pass: migrations `20260211_0001` through `20260314_0005` applied | L1 / L1.5 |
| PostgreSQL app rehearsal | `python tests/scripts/data_maintenance_pg_rehearsal.py` against temporary PostgreSQL DB | Pass: `version=2`, card review flags `[true, false]`, decision logs `decision-pg-1`, `decision-pg-2`, SafeMode `403 Access denied: safe_mode` | DATA-MAINT-02 / G6 / G7 |
| PostgreSQL dump/restore | `pg_dump -Fc -U kj_atlas kj_atlas`; `pg_restore -U kj_atlas -d kj_atlas_restore --clean --if-exists` | Pass: restored DB contains the rehearsal Document and `merge_decision_logs` in expected order | PostgreSQL代表演習 |

### PostgreSQL実施内容と残る前提

- 実施環境: WSL2 / Docker 28.3.3 / PostgreSQL 16.14 / temporary Docker network `kj-atlas-rehearsal-20260525` / temporary DB `kj_atlas_restore`。
- Compose build contextの検証で、backend配下の生成物 `.pytest_cache` がWSL/Dockerのxattr読み取りで失敗したため、`.dockerignore` を追加した。これはCompose運用上の不要ファイル混入を避ける修正であり、アプリの実行時契約は変更しない。
- 代表データ:
  - Document: `doc-data-maint-pg-recovery-20260525`
  - `cards[0].textReviewed=true`, `cards[1].textReviewed=false`
  - embedded merge suggestion group: `group-recovery-pg`
  - `merge_decision_logs`: `decision-pg-1` / `accept`, `decision-pg-2` / `partial`
  - SafeMode export gate: `POST /docs/{doc_id}/export-audit` with `safeMode=true` returned `403 Access denied: safe_mode`
- 復元先確認:
  - `documents`: `doc-data-maint-pg-recovery-20260525|2|true|false|group-recovery-pg`
  - `merge_decision_logs`: `decision-pg-1|group-recovery-pg|snapshot-recovery-pg-1|accept`, `decision-pg-2|group-recovery-pg|snapshot-recovery-pg-1|partial`
- 残る前提: 今回の確認は一時PostgreSQL DBでの製品代表演習であり、各組織の本番運用に必要な保持期間、暗号化、保管先、職務分掌、承認手順、復旧目標時間は固定しない。

### Decision

- SQLite代表演習: **Go**。
- PostgreSQL代表演習: **Go for temporary operational rehearsal**。一時PostgreSQL DBで `pg_dump` / `pg_restore` と復元先確認まで完了。ただし本番組織のバックアップ運用ポリシーは別issue/ADRなしに固定しない。
- ADR要否: **不要**。今回の差分は演習証跡と公開文書の判断支援であり、保持期間、暗号化、外部保管、承認手順、削除、所有者移管、管理者本文閲覧の方針を固定していない。
- 戻し先:
  - `DATA-MAINT-01`: T5代表復旧演習の実行証跡として参照可能。
  - `PRODUCT-QA-01`: G6（診断とサポート）/ G7（回帰）の条件付き証跡として参照可能。
  - `MVP-EXIT-01`: 製品化判定では、PostgreSQL本番相当演習が残るため Conditional のまま扱う。

## 13) Closeout（2026-05-31）

### Context

- 最新mainには、SQLite隔離DBと一時PostgreSQL DBでの代表復旧演習、`merge_decision_logs` 整合確認、SafeMode export gate確認の証跡が反映されている。
- 受入条件とT1-T5はすべて完了しており、演習結果は `DATA-MAINT-01`、`PRODUCT-QA-01`、`MVP-EXIT-01` の判断材料として戻し済みである。
- 本Issueの目的は「製品代表演習の証跡を残すこと」であり、各組織の本番バックアップ保持期間、暗号化方式、保管先、職務分掌、承認手順を製品標準として固定することではない。

### Decision

- `DATA-MAINT-02` は **Done** とする。
- 追加ADRは起票しない。今回の証跡はバックアップ/復旧演習であり、削除、アーカイブ、所有者移管、管理者本文閲覧、保持期限管理の製品方針を固定していない。
- 高権限データライフサイクル操作は、`DATA-MAINT-01` のStop条件、および後続の `DATA-MAINT-03` / future ADRで扱う。

### Consequences

- `DATA-MAINT-02` はReady issueから外し、復旧演習の追加検証が必要になった場合は新しいIssueまたは `PRODUCT-QA-01` のリリース候補ゲートで扱う。
- `MVP-EXIT-01` の全体出荷判定は、本Issue単独ではGoにしない。代表復旧演習はGoだが、製品価値、UX、release-candidate E2E、組織ごとの本番運用条件は別ゲートの判断対象である。

### Verify

- `03_Implement/backend/.venv/Scripts/python.exe -m pytest tests/test_data_maintenance_recovery_exercise.py -q --basetemp .pytest_tmp_data_maint_02_closeout -p no:cacheprovider`
- `03_Implement/backend/.venv/Scripts/python.exe 01_Plans/issues/validate_active_issue_memos.py`
- `03_Implement/backend/.venv/Scripts/python.exe 01_Plans/triage_actionable_plans.py`
- `git diff --check -- 01_Plans/issues/issue-DATA-MAINT-02-backup-restore-recovery-exercise.md`
