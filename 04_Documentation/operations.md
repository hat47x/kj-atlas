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

PostgreSQL volume を使っている場合、更新や検証前に dump を取得します。

```bash
cd 03_Implement/deploy
docker compose exec db pg_dump -U kj_atlas kj_atlas > kj_atlas_backup.sql
```

復元は既存データを上書きする可能性があります。対象環境を確認してから実行してください。

```bash
cat kj_atlas_backup.sql | docker compose exec -T db psql -U kj_atlas kj_atlas
```

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

## 運用手順（DOC-OPS-05）
1. 対象読者（Audience）と目的（Goal）を先に確認する。
2. 公開境界（Public boundary）を確認し、内部手順は公開文書へ直接書かない。
3. 実行後は関連文書の導線（Related links）と矛盾がないか確認する。

## 判断基準（DOC-OPS-05 品質ゲート）
- 可読性: 用語が定義済み語彙と一致し、読者の次アクションが明確であること。
- 検証可能性: 手順・確認コマンド・期待結果が対応していること。
- 保守性: 上流（00〜02）と矛盾せず、関連文書へ責務を分離していること。

## 失敗時対応
- 参照不整合、用語不一致、公開境界の曖昧化を検出した場合は更新を停止する。
- 自己修復は最大3回までとし、4回目相当は Hold として論点化する。
- Architecture/ADR 本体の変更が必要な場合は、この文書では確定せず提案に留める。


## AUTH契約硬化ランブック（Stream E）

AUTH系（schema/api/ops/e2e）の契約更新を行うときは、次の固定手順で実施します。

1. `02_Architecture/strict_mode_exception_approval_flow.md` と `02_Architecture/enterprise_architecture.md` の契約差分を確定する。
2. 本書と `04_Documentation/security.md` に同日反映する。
3. `01_Plans/issues/issue-AUTH-*` の進捗・停止条件・検証ログを更新する。

### 実行前チェック（Fail Fast）

- D1〜D4 と役割語彙（Security Officer / System Owner / Platform Operator）が一致している。
- `StoppedForClarification` 条件が解除される根拠が3層で一致している。
- 例外運用の有効化条件（2者承認 + TTL + rollbackBy）が欠損していない。

### 実行後チェック（Verify）

- `KJ_ATLAS_ALLOW_JIT_PROVISIONING` の現在値・変更理由・復旧期限が監査ログに記録されている。
- strict復帰（`false`）の手順と証跡（実行時刻、実行者、判定根拠）が残っている。
- E2E回帰（Level 1 常時、Level 2 条件付き）の実施計画が issue 側に反映されている。
