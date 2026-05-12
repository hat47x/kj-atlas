# Diagnostics

対象読者: 画面表示、保存、AI 提案、worker 処理の問題を調査する開発者、QA、運用担当者。

目的: 障害時に最初に見る場所、切り分け順、記録すべき情報をまとめます。

範囲外: 非公開の監視基盤、個別インシデントの詳細ログ、秘密情報を含む調査記録。

読後にできること: 画面、API、DB、外部接続のどこで問題が起きているかを切り分け、共有に必要な情報を安全に記録できます。

## 最初に確認すること

1. どの URL で発生したか。
2. どの操作で発生したか。
3. 直前に保存、import、export、AI 提案、レビュー操作を行ったか。
4. API は応答しているか。
5. ブラウザ console と network にエラーがあるか。

## 調査の考え方

障害調査では、まず「画面だけの問題か」「API も失敗しているか」「DB まで影響しているか」を分けます。原因を一度に決めつけず、利用者に見えている症状から奥へ進みます。

最初の5分では、原因の断定よりも再現条件の確認を優先してください。発生 URL、操作手順、API status、console error がそろうだけで、後続の調査がかなり楽になります。

| 層 | 見るもの |
| --- | --- |
| 画面 | ブラウザ console、表示崩れ、操作不能 |
| API | HTTP status、`/healthz`、backend logs |
| DB | `db` health、migration、保存結果 |
| 外部接続 | LLM provider、audit endpoint、access control endpoint |

## 前提知識

この文書の調査では、次の3つを区別できれば十分です。

| 用語 | 意味 |
| --- | --- |
| frontend | ブラウザで動く画面側です。 |
| backend/API | 保存、AI 提案、認証などを処理するサーバー側です。 |
| DB | ドキュメントや操作結果を保存するデータベースです。 |

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

秘密情報、API key、token、生の顧客データは記録しません。どの情報を残せるか迷う場合は [data_handling.md](data_handling.md) を確認してください。

## 共有用テンプレート

```text
発生日時:
環境:
URL:
ブラウザ:
操作手順:
期待した結果:
実際の結果:
API status:
再現率:
添付できるログ:
秘密情報の除去確認: 済 / 未
```

## 復旧の基本

1. 変更直後なら、直前の設定差分を確認します。
2. DB 接続や migration エラーなら backend logs を確認します。
3. frontend の表示だけ壊れている場合は cache を無効化して再読み込みします。
4. LLM や audit の外部送信が関係する場合は、一度 `KJ_ATLAS_LLM_PROVIDER=none`、`KJ_ATLAS_AUDIT_EXPORT_ENABLED=false` に戻して再確認します。

復旧を急ぐ場合でも、秘密情報を含むログをそのまま共有しないでください。共有前に API key、token、個人情報、生の顧客データを除去します。

## 関連文書

- [operations.md](operations.md)
- [configuration.md](configuration.md)
- [e2e_testing.md](e2e_testing.md)
- [data_handling.md](data_handling.md)
- [security.md](security.md)
