# E2E Testing

対象読者: kj-atlas の実装変更に対して Playwright E2E、回帰テスト、PR 前確認を行う開発者、QA、メンテナ。

目的: Docker Compose またはローカル起動環境で、開発者向け E2E を再現できるようにします。一般利用者向けの画面確認は [受け入れ確認](../../../04_Documentation/acceptance_check.md) を参照してください。

範囲外: 組織固有のテスト管理、非公開データを使った検証、CI 基盤の詳細設定、一般利用者向けの導入説明。

## 事前準備

標準構成を起動します。

```bash
cd 03_Implement/deploy
docker compose up --build -d
curl -fsS http://localhost:8080/api/healthz
curl -fsS http://localhost:8080/api/docs/doc_phase1_canvas
```

ローカル開発サーバーで確認する場合は [導入手順](../../../04_Documentation/installation.md) の「Docker を使わない最小起動」を使います。Vite の `/api` proxy は backend が起動していないと 500 を返すため、E2E 前に次の両方を確認します。frontend の port を変更した場合は `4173` を実際の port に置き換えてください。

```bash
curl -fsS http://127.0.0.1:8000/healthz
curl -fsS http://127.0.0.1:8000/docs/doc_phase1_canvas
curl -fsS http://127.0.0.1:4173/api/docs/doc_phase1_canvas
```

## 手動確認と自動テストの違い

| 種類 | 目的 | 使う場面 |
| --- | --- | --- |
| 手動 smoke test | 利用者の主要操作が実際にできるかを見る | 初回起動、画面変更、障害調査 |
| Playwright E2E | ブラウザ操作を自動で再現する | PR、リリース前、回帰確認 |
| unit/regression test | 小さなロジックやデータ変換を速く確認する | 実装変更後、原因切り分け |

一般利用者の確認では、まず [受け入れ確認](../../../04_Documentation/acceptance_check.md) の手動 smoke test だけで十分です。開発変更を含む場合は自動テストも実行します。

## 手動 smoke test

1. `http://localhost:8080` を開く。
2. 新規ドキュメントを作成する。
3. カードを追加する。
4. カードを移動する。
5. 島またはレビュー関連の表示が崩れていないことを確認する。
6. 保存し、ページを再読み込みする。
7. 変更が残っていることを確認する。
8. share/export を使う場合、[データ取り扱い](../../../04_Documentation/data_handling.md) のチェックリストに沿って、出力に秘密情報や内部メモが混ざっていないことを確認する。

表示設定や SafeMode の確認を含める場合は、`View` パネルを開きます。手動 smoke test では、視点プリセット、深さ、SafeMode、export legacy 導線が表示され、キャンバスが操作不能になっていないことを確認します。

![View パネルを開いた手動確認画面](../../../04_Documentation/assets/screenshots/view-controls-safe-mode.png)

## Playwright を実行する

frontend の依存関係を入れます。

```bash
cd 03_Implement/frontend
npm ci
```

`npm ci` は `package-lock.json` に固定された依存関係を入れるため、E2E の再現性を保ちやすい手順です。

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
| 標準サンプル | `doc_phase1_canvas` が backend 直アクセスと frontend proxy の両方で成功する |
| 保存 | 作成・編集した内容が再読み込み後も残る |
| SafeMode | 未レビュー情報を AI が自動確定しない |
| LLM disabled | `KJ_ATLAS_LLM_PROVIDER=none` では AI 機能が disabled として扱われる |
| export | 秘密情報や共有不要な調査メモが混ざらない |
| 画面 | ヘッダー、ツールバー、主要ボタンが狭い幅でも重ならない |

## viewport の目安

画面崩れを確認するときは、少なくとも次の幅を見ます。

| 幅 | 目的 |
| --- | --- |
| 1280px | 標準的な desktop |
| 960px | 狭めの desktop / tablet |
| 390px | mobile 相当 |

すべての細部を確認する必要はありません。主要操作が見えるか、テキストが重ならないか、保存操作ができるかを優先します。

390px では、ヘッダーが複数行に折り返され、検索、表示モード、共有と再現、保存などの主要操作が画面外へ消えないことを確認します。

![390px viewport のヘッダー確認](../../../04_Documentation/assets/screenshots/mobile-toolbar-smoke-390.png)

## 失敗時に残す情報

- 実行したコマンド
- 対象 URL
- ブラウザと viewport
- 失敗した操作
- API status code
- `docker compose logs api --tail=200`
- 可能ならスクリーンショット

ログやスクリーンショットを共有するときは、API key、token、password、未加工の顧客情報を含めません。どこまで残すか迷う場合は [データ取り扱い](../../../04_Documentation/data_handling.md) を参照してください。

## E2E 記録

検証結果を残すときは内部の検証記録テンプレートを使います。個人情報、秘密情報、内部承認履歴は記録しません。

## 関連文書

- [導入手順](../../../04_Documentation/installation.md)
- [受け入れ確認](../../../04_Documentation/acceptance_check.md)
- [運用手順](../../../04_Documentation/operations.md)
- [診断と障害調査](../../../04_Documentation/diagnostics.md)
- [データ取り扱い](../../../04_Documentation/data_handling.md)
- [セキュリティ](../../../04_Documentation/security.md)
