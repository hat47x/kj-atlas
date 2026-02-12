# 運用（最小）

## バックアップ / リストア

バックアップとリストアの最小手順は、バックエンド README の次節を参照してください。

- [03_Implement/backend/README.md - Minimal backup / restore](../03_Implement/backend/README.md#minimal-backup--restore)

要点:

- SQLite: DB ファイルを停止中にコピー
- PostgreSQL: `pg_dump` / `pg_restore`

## 更新手順（Docker Compose）

1. 現在コンテナを停止

```bash
cd 03_Implement/deploy
docker compose down
```

2. 最新コードへ更新（運用フローに従って取得）

3. イメージ再ビルドして起動

```bash
docker compose up --build -d
```

4. API ログと稼働状態を確認

```bash
docker compose ps
docker compose logs api --tail=100
```

## 運用時の注意

- 既定の `LLM_PROVIDER=none` では外部送信は行いません。
- ローカル LLM 利用時は、`LOCAL_LLM_BASE_URL` を社内到達可能な URL に設定してください。
- JSON Export / Import を使う場合は、運用上の取扱ルール（保存場所、持ち出し可否）を組織側で定義してください。
