# Observability

対象読者: kj-atlas を運用し、障害の申告を受けて調査する管理者。

目的: 実行時に何が観測できるか、利用者の申告をログ行へ突き合わせる手順、およびまだ観測できないことを示します。

範囲外: 組織固有の監視基盤の構築手順、メトリクス収集の実装（`OPS-OBSERV-01` の論点として未決）。

公開区分: 利用者/運用者向け公開候補。

## 何が観測できるか

| 対象 | 手段 | 認証 |
| --- | --- | --- |
| プロセスが生きているか | `GET /api/healthz` | 不要 |
| 依存が使える状態か | `GET /api/readyz` | 不要 |
| 稼働中のビルド | `GET /api/version` | 不要 |
| リクエスト単位の追跡 | `X-Request-Id` レスポンスヘッダーとログ行の `requestId` | — |
| アプリケーションの出来事 | 構造化ログ（既定でJSON） | — |

**メトリクスは提供していません。** リクエスト数・レイテンシ・エラー率・DBプール状態・LLM呼び出し回数のいずれも観測できません。したがって障害の**検知**経路は現在も利用者からの申告のみです。「影響範囲はどこまでか」「復旧したか」に機械的に答える手段はありません。導入するかどうかは `OPS-OBSERV-01` の未決事項です。

## `/healthz` と `/readyz` の違い

**`/healthz` は liveness だけです。何も検査しません。** プロセスが応答することのみを示します。データベースを失った状態でも `{"status": "ok"}` を返します。コンテナの再起動判定にはこれを使ってください。

**`/readyz` は依存の状態を検査します。**

```bash
curl -s http://localhost:8080/api/readyz
```

```json
{"status": "ready", "checks": {"database": "ok", "schema": "ok"}}
```

- `database: unreachable` — DBへ到達できません。接続先・認証・DBの稼働を確認してください。理由の詳細は接続文字列を含みうるため応答には出しません。ログ側の `readiness check failed` を見てください。
- `schema: mismatch` — DBの `alembic_version` が、このビルドが期待するリビジョンと一致しません。`schemaExpected` と `schemaApplied` に両方のリビジョンIDが出ます。`alembic upgrade head` の実行漏れか、ビルドとDBの世代差です。**この状態でも `/healthz` は 200 を返します。**

`schema` の検査は、起動時検査が届いていなかった範囲を埋めています。起動時の検査はAlembicの**スクリプト側**の分岐だけを見ており、DBに実際に適用済みのリビジョンを読んでいません。したがって古いスキーマのDBに対しても正常起動し、最初のクエリで失敗します。

## 利用者の申告をログへ突き合わせる

全レスポンスに `X-Request-Id` が付きます。エラー応答では本文にも `requestId` が入ります。

```json
{"detail": "Document changed concurrently", "requestId": "9f2c1d..."}
```

手順:

1. 利用者から `requestId` を聞く（エラー画面から控えられます）。控えられていない場合は、発生時刻とURLで絞り込みます。
2. ログを検索する。

```bash
docker compose logs api | grep '"requestId":"9f2c1d'
```

呼び出し側が `x-trace-id` ヘッダーで独自のIDを送っている場合、それが安全な形式（英数・ハイフン・アンダースコアのみ、128文字以下）であれば `requestId` としてそのまま採用します。安全でない値は破棄してサーバ側で発行します（**リクエスト自体は失敗させません**）。

## ログの形式

既定は1行1JSONです（`KJ_ATLAS_LOG_JSON=true`）。

```json
{"timestamp":"2026-08-13T09:12:33+0000","level":"WARNING","logger":"kj_atlas_api.audit","message":"audit event send failed; keep fail-open","requestId":"9f2c1d...","tenantId":"tenant-a","docId":"doc-1","queueLength":3}
```

`tenantId` / `docId` / `queueLength` のようなフィールドは、コード側が `extra={...}` で渡しているものです。**`OPS-OBSERV-01` 以前はログ設定が存在せず、これらは出力されていませんでした** — 監査送信の失敗すら「どのテナントの何が失われたか」が分からない状態でした。

出力レベルは `KJ_ATLAS_LOG_LEVEL` で変更します。`KJ_ATLAS_LOG_JSON=false` にすると人間可読の1行書式になり、`requestId` は角括弧内に出ます。

### ログに出ないもの

`04_Documentation/security.md` の方針どおり、主体識別子（IdP由来の `subject`）・外部テナント参照・資格情報は出力しません。`extra` にこれらの名前のフィールドが渡された場合は `[redacted]` へ置き換えます。これは方針の機械的な裏打ちであり、方針の代替ではありません。

その結果として、**エラーの主体を特定する手段はログにはありません。** 監査イベント側は `actorRefHash`（ハッシュ）を持ちますが、監査の宛先設定と保存については下記の制約があります。

## まだ観測できないこと

運用上重要なので明示します。

- **メトリクスがありません**（前述）。容量計画・スケールアウト判断の入力が存在しません。**2026-08-26決定: 導入しない**（`ADR-0039`の個人OSS運用規模との整合を優先）。したがって規模拡大・複数テナント並行運用でのスケールアウト判断は本プロジェクトの非目標である。障害検知は引き続き利用者からの申告のみに依存する。
- **監査イベントは既定で捨てられます。** `KJ_ATLAS_AUDIT_EXPORT_ENABLED=false` かつ `KJ_ATLAS_AUDIT_TRANSPORT=noop` が既定です。有効化しても、SafeMode中のイベントは `KJ_ATLAS_AUDIT_ALLOW_IN_SAFE_MODE=false`（既定）では送信されません。`view` イベントは SafeMode 前提で発行されるため、**「監査を有効にした」だけでは文書の閲覧記録はほぼ残りません。** 詳細は `security.md` の Audit export 節。
- **監査イベントのローカル保存と照会APIがありません。** 送信先は noop と外部HTTPの2つだけで、DBにもファイルにも残りません。「誰がこの文書を読んだか」に答える手段は現状ありません（`DATA-MAINT-05` / `DATA-MAINT-06` で方針決定待ち）。
- **管理面の操作の監査は実装済みです**（`admin_audit_events` テーブル、`GET /admin/provision/audit`。`issue-SEC-ADMIN-PLANE-03`で完了）。この節はかつて「未着手」と記載していたが、事実に合わせて訂正した（2026-08-26）。
- **ログの保存・ローテーションはDocker既定に委ねています。** 上限がないため、長期稼働ではホスト側で `json-file` のローテーション設定を行ってください。

## 関連文書

- [operations.md](operations.md): 日常運用と障害時の初動。
- [diagnostics.md](diagnostics.md): 症状からの切り分け順序と診断バンドル。
- [security.md](security.md): ログのPII方針、Audit export の境界。
