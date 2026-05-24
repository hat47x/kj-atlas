# Operations

対象読者: kj-atlas の日常運用、検証環境管理、リリース後確認を担当する人。

目的: 起動、停止、状態確認、更新、バックアップ、障害時の初動を再現できる手順としてまとめます。

範囲外: 組織固有の承認フロー、秘密情報管理、インフラ監視基盤の構築。

## 標準構成

Docker Compose の標準構成は次の3サービスです。

| サービス | 役割 |
| --- | --- |
| `web` | React frontend と nginx proxy |
| `api` | FastAPI backend |
| `db` | PostgreSQL |

標準 URL は `http://localhost:8080` です。nginx は `/api/` を backend に転送します。

## 運用で見るもの

kj-atlas の運用確認は、次の順で見ると切り分けやすくなります。

1. 画面が開くか。
2. API が `/api/healthz` に応答するか。
3. DB が healthy か。
4. 保存と再読み込みができるか。
5. LLM や audit など、外部接続を有効にした部分だけ追加で確認する。

最初からすべてのログを読む必要はありません。利用者影響のある入口から順に確認します。

画面側の入口は次の状態を目安にします。ヘッダーに SafeMode、表示モード、共有と再現、保存などの主要操作があり、キャンバスと右側パネルが表示されていれば、次に API と保存の確認へ進めます。

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

## バックアップ

PostgreSQL volume を使っている場合、更新や検証前に dump を取得します。この節は最小限の判断支援です。バックアップの保持期間、暗号化、保管先、承認手順は、各組織の運用方針に合わせて決めてください。

本番環境へ復元する前に、可能な限り検証環境へ復元し、ドキュメントと判断ログを読み直せることを確認します。復元は既存データを上書きする可能性があるため、対象環境、取得日時、アプリの revision、実行者を記録してから進めます。

```bash
cd 03_Implement/deploy
docker compose exec db pg_dump -U kj_atlas kj_atlas > kj_atlas_backup.sql
```

`KJ_ATLAS_POSTGRES_USER` や `KJ_ATLAS_POSTGRES_DB` を既定値から変えている場合は、上の `kj_atlas` を実際の値に置き換えます。

検証環境で復元する最小例です。

```bash
cat kj_atlas_backup.sql | docker compose exec -T db psql -U kj_atlas kj_atlas
```

復元後は、少なくとも次を確認します。

- `/api/healthz` が成功する。
- 代表ドキュメントを開ける。
- 判断ログやレビュー状態が同じ対象を指している。
- 共有前確認で SafeMode が有効であり、未レビュー本文や個人情報を不用意に共有しない。

SQLite を使う小規模検証では、APIを停止してからDBファイルをコピーし、コピー先を別環境で読み直します。運用の正式手順として採用する場合は、保存場所、取得タイミング、復元確認の担当を組織内で決めてください。

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

### 責務分離（役割衝突の停止条件）

| 役割 | 責務 | 実施してはいけないこと |
| --- | --- | --- |
| First Responder（運用一次対応） | 症状分類、一次切り分け、再現手順の記録 | SafeMode 緩和を独断で有効化すること |
| System Owner（運用責任者） | 復旧優先度判断、外部共有可否の承認 | API key/token を含むログ共有を許可すること |
| Platform Operator（実行担当） | 再起動、設定復旧、ロールバック実行 | 承認なしの恒久設定変更 |

次のいずれかに該当した場合は手順を停止し、責務を明示したうえでエスカレーションします。

- 同一人物が「承認」と「実行」を同時に担う必要がある。
- SafeMode 緩和の必要性はあるが、承認者が不在で判断できない。
- 復旧のために secrets を含む生ログ共有が必要と主張される。


### Plan → Execute → Verify（障害復旧ランブック）

復旧作業は必ず次の順で進めます。各ステップで完了条件が不足している場合は、恒久変更を確定せず **暫定対応メモ** として記録します。

1. **Plan（計画）**
   - 失敗分類コード（WEB-ENTRY / API-UNAVAILABLE / SAVE-FAILURE / IMPORT-VALIDATION / SHARE-SAFEMODE）を決定する。
   - 受入条件（AC）を3点で定義する: 「利用者影響の停止」「安全境界の維持」「再現手順の記録」。
   - 承認者（System Owner）と実行者（Platform Operator / First Responder）を分離して記録する。
2. **Execute（実行）**
   - 一次切り分けコマンドを実行し、復旧アクションは最小変更（再起動・再試行・既知のロールバック）に限定する。
   - SafeMode 緩和や外部共有の拡大が必要な場合は、承認が揃うまで停止する。
3. **Verify（検証）**
   - `/api/healthz`、保存、再読み込み、必要に応じて import/share の動作を確認する。
   - マスク境界（API key / token / password / 未マスク本文を共有しない）を再確認する。
   - 再現テンプレートを埋め、未解決項目は「暫定対応メモ」として次アクションを残す。

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
