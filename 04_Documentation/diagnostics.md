# Diagnostics

対象読者: 画面表示、保存、AI 提案、worker 処理の問題を調査する開発者、QA、運用担当者。

目的: 障害時に最初に見る場所、切り分け順、記録すべき情報をまとめます。

範囲外: 非公開の監視基盤、個別インシデントの詳細ログ、秘密情報を含む調査記録。

## 最初に確認すること

1. どの URL で発生したか。
2. どの操作で発生したか。
3. 直前に保存、import、export、AI 提案、レビュー操作を行ったか。
4. API は応答しているか。
5. ブラウザ console と network にエラーがあるか。

## ヘルスチェック

Docker Compose:

```bash
curl -fsS http://localhost:8080/api/healthz
docker compose ps
docker compose logs api --tail=200
```

直接起動:

```bash
curl -fsS http://127.0.0.1:8000/healthz
```

## ブラウザで見る場所

- Console: JavaScript error、worker error、failed fetch。
- Network: `/api/docs/<doc_id>`、`/api/ai/*`、status code。
- Application/Storage: local storage や cache が古い状態を保持していないか。

## よくある切り分け

| 症状 | 主な確認 |
| --- | --- |
| 画面が真っ白 | frontend build、console error、nginx logs |
| 保存に失敗 | API status、`X-API-Key`、backend logs、DB 接続 |
| AI 提案が出ない | `KJ_ATLAS_LLM_PROVIDER`、provider endpoint、SafeMode |
| export が失敗 | 対象ドキュメントの schema、ブラウザ console |
| worker が落ちる | 入力データ、worker console、該当 worker の単体テスト |

## worker 関連の確認

frontend の worker 実装は `03_Implement/frontend/src/worker/` にあります。worker 由来の問題は、まず入力データの大きさ、schema、review 状態を確認します。

```bash
cd 03_Implement/frontend
npm run test
npm run typecheck
```

特定の worker test がある場合は、そのファイルだけを指定して実行します。

```bash
npm run test -- src/worker/<test-file>.test.ts
```

## 記録する情報

- 発生日時
- commit
- URL
- ブラウザと viewport
- 操作手順
- 期待結果
- 実際の結果
- API status code
- console error
- 再現率

秘密情報、API key、token、生の顧客データは記録しません。

## 復旧の基本

1. 変更直後なら、直前の設定差分を確認します。
2. DB 接続や migration エラーなら backend logs を確認します。
3. frontend の表示だけ壊れている場合は cache を無効化して再読み込みします。
4. LLM や audit の外部送信が関係する場合は、一度 `KJ_ATLAS_LLM_PROVIDER=none`、`KJ_ATLAS_AUDIT_EXPORT_ENABLED=false` に戻して再確認します。

## 関連文書

- [operations.md](operations.md)
- [configuration.md](configuration.md)
- [e2e_testing.md](e2e_testing.md)
- [security.md](security.md)
