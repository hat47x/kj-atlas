# E2E Testing

対象読者: 変更後に kj-atlas の主要操作を確認する開発者、QA、運用担当者。

目的: Docker Compose またはローカル起動環境で、ブラウザを使った受け入れ確認と Playwright E2E を再現できるようにします。

範囲外: 組織固有のテスト管理、非公開データを使った検証、CI 基盤の詳細設定。

## 事前準備

標準構成を起動します。

```bash
cd 03_Implement/deploy
docker compose up --build -d
curl -fsS http://localhost:8080/api/healthz
```

ローカル開発サーバーで確認する場合は [installation.md](installation.md) の「Docker を使わない最小起動」を使います。

## 手動 smoke test

1. `http://localhost:8080` を開く。
2. 新規ドキュメントを作成する。
3. カードを追加する。
4. カードを移動する。
5. 島またはレビュー関連の表示が崩れていないことを確認する。
6. 保存し、ページを再読み込みする。
7. 変更が残っていることを確認する。
8. share/export を使う場合、出力に秘密情報や内部メモが混ざっていないことを確認する。

## Playwright を実行する

frontend の依存関係を入れます。

```bash
cd 03_Implement/frontend
npm install
```

E2E を実行します。

```bash
npm run e2e
```

画面を見ながら確認する場合:

```bash
npm run e2e:headed
```

特定の mock E2E だけ実行する場合:

```bash
npm run e2e:mock
```

## 単体・回帰テスト

E2E の前に軽量な回帰確認を行う場合:

```bash
cd 03_Implement/frontend
npm run typecheck
npm run test
npm run test:regression-guards
```

backend:

```bash
cd 03_Implement/backend
python -m pytest
```

## 確認観点

| 観点 | 期待 |
| --- | --- |
| 起動 | `/api/healthz` が成功する |
| 保存 | 作成・編集した内容が再読み込み後も残る |
| SafeMode | 未レビュー情報を AI が自動確定しない |
| LLM disabled | `KJ_ATLAS_LLM_PROVIDER=none` では AI 機能が disabled として扱われる |
| export | 秘密情報や内部作業ログが混ざらない |
| 画面 | ヘッダー、ツールバー、主要ボタンが狭い幅でも重ならない |

## 失敗時に残す情報

- 実行したコマンド
- 対象 URL
- ブラウザと viewport
- 失敗した操作
- API status code
- `docker compose logs api --tail=200`
- 可能ならスクリーンショット

## E2E 記録

検証結果を残すときは [e2e_verification_log_2026-03-03.md](e2e_verification_log_2026-03-03.md) のテンプレートを使います。個人情報、秘密情報、内部承認履歴は記録しません。

## 関連文書

- [installation.md](installation.md)
- [operations.md](operations.md)
- [diagnostics.md](diagnostics.md)
- [security.md](security.md)
