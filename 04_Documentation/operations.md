# Operations

対象読者: kj-atlas の日常運用、検証環境管理、リリース後確認を担当する人。

目的: 起動、停止、状態確認、更新、バックアップ、障害時の初動を再現できる手順としてまとめます。

範囲外: 組織固有の承認フロー、秘密情報管理、インフラ監視基盤の構築。

公開区分: 運用者向け公開候補。起動、停止、確認、バックアップ、共有前確認の運用境界を扱い、組織固有の承認履歴や内部計画は含めません。

## 標準構成

Docker Compose の標準構成は次の3サービスです。

| サービス | 役割 |
| --- | --- |
| `web` | React frontend と nginx proxy |
| `api` | FastAPI backend |
| `db` | PostgreSQL |

標準 URL は `http://localhost:8080` です。nginx は `/api/` を backend に転送します。`web` は loopback（`127.0.0.1`）へ bind されるため、この URL は起動したホスト自身からだけ開けます。別端末や LAN からの利用が必要な場合は、認証 proxy・TLS を伴う別構成が必要です。

## 運用で見るもの

kj-atlas の運用確認は、次の順で見ると切り分けやすくなります。

1. 画面が開くか。
2. API が `/api/healthz` に応答するか。
3. DB が healthy か。
4. 保存と再読み込みができるか。
5. LLM や audit など、外部接続を有効にした部分だけ追加で確認する。

最初からすべてのログを読む必要はありません。利用者影響のある入口から順に確認します。

画面側の入口は次の状態を目安にします。起動直後に「作業を開始」パネルが表示され、新しい文書、サンプル、`document.json`、レビューパックの入口と SafeMode の状態を確認できれば、利用者は次の操作を選べます。

![運用確認で見る作業開始パネル](assets/screenshots/start-document-entry.png)

開始パネルを閉じるか入口を選ぶと、ヘッダーに SafeMode、表示モード、共有と再現、保存などの主要操作があり、キャンバスと右側パネルが表示されます。この状態まで進めば、次に API と保存の確認へ進めます。

![運用確認で見る標準画面](assets/screenshots/app-canvas-overview.png)


## Runtime profile の選択

運用手順を開始する前に、対象環境の profile を固定します。
profile の詳細は GitHub 上の [runtime_parameter_registry.md](https://github.com/hat47x/kj-atlas/blob/main/02_Architecture/runtime_parameter_registry.md) を参照してください。ここでは運用時の判断だけを示します。

- 開発再現や不具合切り分け: `local-dev`
- Compose での評価・受入確認: `evaluation`
- 企業/行政の本番相当: `enterprise-production`

`enterprise-production` では次を起動前チェックに追加します。

- `KJ_ATLAS_ALLOW_JIT_PROVISIONING=false`
- `KJ_ATLAS_ACCESS_CONTROL_FAIL_SAFE_MODE=read_only` または `deny`
- 外部接続（LLM / audit / external_http）を有効化する場合、接続先・timeout・秘密管理の確認記録

## 起動

```bash
cd 03_Implement/deploy
docker compose up --build -d
```

## 状態確認

```bash
docker compose ps
curl -fsS http://localhost:8080/api/healthz
docker compose logs api --tail=100
```

確認すること:

- `db` が healthy になっている。
- `api` が migration 後に起動している。
- `web` が `KJ_ATLAS_WEB_PORT` のポートで公開されている。
- `/api/healthz` が `{"status":"ok"}` を返す。

`docker compose ps` はサービスの生死を見るコマンドです。`curl` は API の応答を見るコマンドです。どちらか片方だけでは原因を絞り切れないため、両方を確認します。

## 停止

```bash
cd 03_Implement/deploy
docker compose down
```

データも削除する場合だけ `-v` を付けます。

```bash
docker compose down -v
```

## 更新

1. 変更を取得します。

```bash
git pull --ff-only
```

2. 再ビルドして起動します。

```bash
cd 03_Implement/deploy
docker compose up --build -d
```

3. ヘルスチェックと主要操作を確認します。

```bash
curl -fsS http://localhost:8080/api/healthz
docker compose logs api --tail=100
```

## バックアップと隔離復元

取得先、保管期間、暗号化、外部保管の有無は組織ごとに決める運用事項です。kj-atlasでは、バックアップ取得だけを成功条件にせず、本番DBとは異なる名前・path・schemaへの隔離復元と内容確認までを一組の演習として扱います。

実行前にDB製品とversion、アプリrevision、source、復元先、実行者を記録します。アプリruntimeの接続アカウントへDB作成・backup・restore権限を追加せず、運用者が別の管理資格情報で実行してください。以下は固定versionのpromotion matrixで確認した最小パターンであり、managed DBではprovider公式のbackup機能と権限モデルへ読み替えます。

### 共通の復旧確認

復旧演習は、本番DBを直接上書きする手順ではありません。検証環境または一時DBに復元し、次を確認します。

| 確認項目 | 見る内容 |
| --- | --- |
| 対象 | DB製品/version、アプリrevision、バックアップ取得日時、source、復元先 |
| Schema | `alembic_version`が想定revisionで、起動時のschema gateを通過すること |
| Document | `id`、`version`、`updated_at`、画面またはAPIで読み込めること |
| 判断ログ | `merge_decision_logs`が対象Documentに紐づき、group/snapshot単位の順序が崩れていないこと |
| 大容量本文 | 代表canvasの`payload_json`が欠落・切詰めされず、byte数または文字数がsourceと一致すること |
| 共有前確認 | SafeModeが有効で、未レビュー本文や個人情報を含む出力を不用意に共有しないこと |
| 中断条件 | command失敗・警告付き部分成功、version不整合、件数・digest・本文長・判断ログの不一致、復元先取り違え、秘密情報を含むログ共有があれば完了扱いにしない |

<a id="database-sqlite"></a>
### SQLite

APIを停止し、DBファイルを別pathへコピーします。復元演習では元ファイルを上書きせず、コピーしたDBを別の`sqlite:///...` URLで読み込みます。稼働中の単純なファイルコピーは未確定transactionやWALを欠落させ得るため使用しません。

```bash
cp 03_Implement/backend/kj_atlas.db kj_atlas-backup.sqlite3
cp kj_atlas-backup.sqlite3 kj_atlas-restore.sqlite3
```

<a id="database-postgresql"></a>
### PostgreSQL

標準Composeの例です。`createdb`とrestoreはruntime userではなく、検証用databaseを作成できる運用資格情報で実行します。

```bash
cd 03_Implement/deploy
docker compose exec db pg_dump -Fc -U kj_atlas kj_atlas > kj_atlas_backup.dump
```

復元は既存データを上書きする可能性があります。まず本番DBではない検証用DBへ戻してください。

```bash
docker compose exec db createdb -U kj_atlas kj_atlas_restore
cat kj_atlas_backup.dump | docker compose exec -T db pg_restore -U kj_atlas -d kj_atlas_restore --clean --if-exists
```

<a id="database-mysql"></a>
### MySQL 8.4

`MYSQL_PWD`はこのshell processだけへ設定し、履歴や文書へ値を残しません。`CREATE DATABASE`は運用資格情報で行い、dump対象には整合snapshot用の`--single-transaction`を指定します。

```bash
MYSQL_PWD="$DB_ADMIN_PASSWORD" mysqldump --host="$DB_HOST" --user="$DB_ADMIN_USER" \
  --single-transaction --skip-lock-tables kj_atlas > kj_atlas_mysql.sql
MYSQL_PWD="$DB_ADMIN_PASSWORD" mysql --host="$DB_HOST" --user="$DB_ADMIN_USER" \
  -e 'CREATE DATABASE kj_atlas_restore'
MYSQL_PWD="$DB_ADMIN_PASSWORD" mysql --host="$DB_HOST" --user="$DB_ADMIN_USER" \
  kj_atlas_restore < kj_atlas_mysql.sql
```

<a id="database-mariadb"></a>
### MariaDB 11.4

MySQLと同じ分離方針で、MariaDB同梱clientを使用します。

```bash
MYSQL_PWD="$DB_ADMIN_PASSWORD" mariadb-dump --host="$DB_HOST" --user="$DB_ADMIN_USER" \
  --single-transaction --skip-lock-tables kj_atlas > kj_atlas_mariadb.sql
MYSQL_PWD="$DB_ADMIN_PASSWORD" mariadb --host="$DB_HOST" --user="$DB_ADMIN_USER" \
  -e 'CREATE DATABASE kj_atlas_restore'
MYSQL_PWD="$DB_ADMIN_PASSWORD" mariadb --host="$DB_HOST" --user="$DB_ADMIN_USER" \
  kj_atlas_restore < kj_atlas_mariadb.sql
```

<a id="database-mssql"></a>
### SQL Server 2022

database backup権限と、復元先を作成できる管理権限が必要です。backup fileはSQL Server processから見える管理pathへ置きます。復元前に`RESTORE FILELISTONLY`で実際のlogical file名を確認し、`MOVE`の値へ使います。

```sql
BACKUP DATABASE [kj_atlas]
  TO DISK = N'/var/opt/mssql/data/kj_atlas.bak'
  WITH INIT, COPY_ONLY;
RESTORE FILELISTONLY
  FROM DISK = N'/var/opt/mssql/data/kj_atlas.bak';
RESTORE DATABASE [kj_atlas_restore]
  FROM DISK = N'/var/opt/mssql/data/kj_atlas.bak'
  WITH MOVE N'<data-logical-name>' TO N'/var/opt/mssql/data/kj_atlas_restore.mdf',
       MOVE N'<log-logical-name>' TO N'/var/opt/mssql/data/kj_atlas_restore_log.ldf';
```

<a id="database-cockroachdb"></a>
### CockroachDB 26.2.3

`BACKUP`権限と復元先作成権限が必要です。次はsingle-node検証で確認した`nodelocal`例です。multi-nodeやmanaged serviceでは共有object storage URIとKMS／IAMを組織側で定義します。

```sql
BACKUP DATABASE "kj_atlas" INTO 'nodelocal://1/kj_atlas-backup';
RESTORE DATABASE "kj_atlas" FROM LATEST IN 'nodelocal://1/kj_atlas-backup'
  WITH new_db_name = 'kj_atlas_restore';
```

<a id="database-oracle"></a>
### Oracle AI Database Free 23.26.2

Data Pump directoryへのread/write権限、source schemaのexport権限、復元schemaの作成・quota設定が必要です。passwordを引数へ埋め込まず、walletまたは対話入力等の組織標準のsecret受渡しを使用します。復元先schemaを事前作成してから`REMAP_SCHEMA`で隔離します。

```bash
expdp "$DB_ADMIN_USER@$ORACLE_SERVICE" SCHEMAS=KJ_ATLAS DIRECTORY=DATA_PUMP_DIR \
  DUMPFILE=kj_atlas.dmp LOGFILE=kj_atlas_exp.log REUSE_DUMPFILES=YES
impdp "$DB_ADMIN_USER@$ORACLE_SERVICE" DIRECTORY=DATA_PUMP_DIR \
  DUMPFILE=kj_atlas.dmp LOGFILE=kj_atlas_imp.log \
  REMAP_SCHEMA=KJ_ATLAS:RESTORED_SCHEMA
```

復元確認後は検証用database/schemaと一時backupを、組織の保持・監査方針に従って削除します。削除対象をsourceと照合し、名前が曖昧な状態では実行しません。

## ログを見る

```bash
docker compose logs web --tail=100
docker compose logs api --tail=200
docker compose logs db --tail=100
```

障害調査では、最初に発生時刻、操作内容、対象ドキュメント ID、HTTP status、画面上のエラーを控えます。ログやスクリーンショットを共有する前に、秘密情報を除外してください。診断 worker の見方は [diagnostics.md](diagnostics.md)、残してよい情報の判断は [data_handling.md](data_handling.md) を参照してください。

## 障害時の初動

| 症状 | 確認 |
| --- | --- |
| 画面が開かない | `docker compose ps`、`web` の logs、`KJ_ATLAS_WEB_PORT` の競合 |
| API が 502/503 | `api` の logs、migration エラー、DB 接続 |
| API が 401 | `KJ_ATLAS_API_KEY` と `X-API-Key` ヘッダー |
| AI 機能が使えない | `KJ_ATLAS_LLM_PROVIDER`、local/large-scale provider の設定 |
| 保存できない | API logs、DB logs、ブラウザ developer tools の network |

問い合わせや引き継ぎでは、次の形で共有すると調査が速くなります。

```text
発生日時:
URL:
操作:
期待した結果:
実際の結果:
API status:
直近の変更:
確認したログ:
```


## 障害診断と復旧

### 障害分類（一次切り分け）

| 分類 | 代表症状 | 一次切り分け（5分以内） | 初期復旧アクション |
| --- | --- | --- | --- |
| WEB-ENTRY | 画面が開かない、表示崩れ | `web` logs、ポート競合、ブラウザ console | `web` 再起動、ポート競合解消、再読み込み |
| API-UNAVAILABLE | 502/503、`/api/healthz` 失敗 | `api` logs、`db` health、migration 失敗 | `api`/`db` 再起動、migration 復旧 |
| SAVE-FAILURE | 保存失敗、再読み込みで内容不一致 | API status、`db` logs、Network 失敗応答 | 再保存、API復旧後に再試行、バックアップ確認 |
| IMPORT-VALIDATION | 取り込み失敗、schema 不整合 | import エラー内容、schemaVersion、入力サイズ | 別ファイルで再試行、validation 結果を共有 |
| SHARE-SAFEMODE | 共有前警告、export 制約 | SafeMode 状態、マスク警告、visibility 設定 | 共有を一時停止し、マスク対象確認後に再実行 |

### 小規模運用での判断

個人運用では、Maintainerが状況判断と復旧操作を兼ねても構いません。通常の再起動、再試行、既知バージョンへのロールバックに、仮想的な承認者や役職別記録は不要です。

次の場合だけ作業を止めます。

- secretsや未マスク本文を共有しなければ調査できない。
- SafeModeの緩和、外部共有範囲の拡大、不可逆なデータ変更が必要である。
- 変更後に安全な状態へ戻せる確信がない。

組織が職務分離を必要とする場合は、[strict mode例外緩和仕様](../02_Architecture/strict_mode_exception_approval_flow.html)を組織用プロファイルとして適用します。

### 障害復旧の最小手順

1. 症状に最も近い分類コードを選び、一次切り分けを行います。
2. 再起動、再試行、既知のロールバックなど、可逆な最小操作を実施します。
3. `/api/healthz`、保存、再読み込み、必要な利用者操作を確認します。
4. 未解決の場合だけ、症状、実施内容、結果、次に試すことを短く残します。

**暫定対応メモの記録フォーマット**

```text
暫定対応メモID:
不足している確認:
不足により確定できない判断:
暫定運用（いつまで）:
恒久対応が必要な場合の相談先:
```

### 復旧実行の再現テンプレート

```text
分類:
発生日時:
影響範囲:
一次切り分け結果:
実施コマンド:
復旧結果:
承認者:
実行者:
次回予防策:
```

## SafeMode と外部サービスとの共有

既定では `KJ_ATLAS_LLM_PROVIDER=none`、audit HTTP 連携も無効です。外部 LLM や audit HTTP を有効にする場合は、[data_handling.md](data_handling.md)、[security.md](security.md)、[configuration.md](configuration.md) を先に確認してください。

## 運用前チェックリスト

- [ ] `/api/healthz` が成功する。
- [ ] 画面から新規ドキュメントを作成できる。
- [ ] 保存後に再読み込みして内容が残る。
- [ ] LLM provider が意図した値になっている。
- [ ] API key を使う環境では、キーなし API が 401 になる。
- [ ] バックアップまたは復旧方針が確認済み。

## 関連文書

- [installation.md](installation.md)
- [configuration.md](configuration.md)
- [data_handling.md](data_handling.md)
- [security.md](security.md)
- [diagnostics.md](diagnostics.md)
- [release.md](release.md)

## 更新後の確認

更新や復旧のあと、少なくとも次の順で確認します。

1. 画面が開く。
2. `/api/healthz` が成功する。
3. 標準サンプルまたは対象ドキュメントを読み込める。
4. 保存、再読み込み、共有前確認ができる。
5. 外部接続を有効にしている場合、その接続だけを追加で確認する。

どれか1つでも失敗する場合は、次の変更へ進まず、発生日時、操作、期待結果、実際の結果、直近の変更を記録します。
