# 観測ガイド（OPS-OBSERV-01）

バックエンドの構造化ログ・相関ID・準備状態（readiness）の見方。障害報告をサーバ側ログへ突き合わせるための手順です。

## ログの形式

バックエンドのログは **JSON 1行 = 1レコード** で stdout へ出力されます（`docker compose logs api` で閲覧）。

```json
{"ts": "2026-08-14T21:01:09+0900", "level": "WARNING", "logger": "kj_atlas_api.auth_context", "message": "TRUSTED_PROXIES is not configured. ...", "requestId": "716a516b498c4fdba6851a48435f9c53", "tenantId": "tenant-a", "docId": "doc-1", "queueLength": 3}
```

| フィールド | 意味 |
| --- | --- |
| `ts` | 出力時刻（JST。ISO8601） |
| `level` | `CRITICAL` / `ERROR` / `WARNING` / `INFO` / `DEBUG` |
| `logger` | 出力元モジュール |
| `message` | ログ本文 |
| `requestId` | 処理中リクエストの相関ID（レスポンスの `X-Request-Id` と同一） |
| その他 | 呼び出し側が `extra={...}` で付与した構造化情報（`tenantId` / `docId` / `eventType` / `queueLength` / LLM の `provider` / `model_id` / `trace_id` など） |

**レベル設定**: `KJ_ATLAS_LOG_LEVEL`（既定 `INFO`）で変更します。`CRITICAL`/`ERROR`/`WARNING`/`INFO`/`DEBUG`/`NOTSET` を受理し、未知値は `INFO` へフォールバックします。DEBUG にすると LLM 応答の詳細などが増えます。

## 相関ID（requestId / X-Request-Id）

- 全リクエストに `X-Request-Id` レスポンスヘッダが付与されます。
- 受信リクエストの `x-trace-id` ヘッダが安全な形式（`^[A-Za-z0-9._:-]{1,128}$`）ならそれを尊重し、そうでなければサーバが新しい不透明IDを発行します。
- 処理中のログレコードには同じ値が `requestId` として入ります。
- エラーレスポンス（401 / 422 / 409 / 503 / 500）のボディにも `requestId` が含まれます。

**突き合わせ手順**:
1. 利用者から「14:32 に開けなかった」という報告を受ける。
2. ブラウザの developer tools で該当リクエストの `X-Request-Id` を確認する（または画面・エラーボディの `requestId`）。
3. `docker compose logs api | grep <requestId>` でサーバ側の該当ログを引く。

## ヘルスチェックの意味

| エンドポイント | 意味 | 失敗時 |
| --- | --- | --- |
| `GET /healthz` | **liveness**（プロセス生存のみ。DB には触れない） | プロセス停止時のみ 5xx |
| `GET /readyz` | **readiness**（DB 到達 + schema が migration head と一致） | 503。`reason: database_unavailable` または `reason: schema_mismatch`（`applied` / `expected` 付き） |
| `GET /version` | ビルドリビジョン（`KJ_ATLAS_APP_REVISION`） | — |

`/healthz` が `{"status":"ok"}` でも DB を失っていることがあるため、DB 依存の調査には `/readyz` を使います。

## 監査・LLM の構造化フィールド

- 監査ディスパッチャ失敗: `eventType` / `tenantId` / `docId` / `queueLength` / `error` — どのテナントの何が失われたかを特定できます。
- `/ai/*`: `provider` / `provider_kind` / `model_id` / `requested_at` / `transport` / `trace_id` / `fallback_to_none`（`03_Implement/backend/README.md`「LLM provider audit metadata」参照）。

## 関連

- 障害切り分け順: [diagnostics.md](diagnostics.md)
- ログ共有時の秘密情報除外: [data_handling.md](data_handling.md)
- セキュリティ方針: [security.md](security.md)
