# 受け入れ確認

対象読者: kj-atlas を起動したあと、画面から主要操作を確認したい利用者、運用担当者、評価担当者。

目的: マウスとキーボードで基本操作が自然に行えるか、保存や共有前確認ができるかを、短い手順で確認します。

範囲外: Playwright などの開発者向け自動テスト、CI 設定、組織固有の検証管理。

## 確認前の準備

標準構成で起動します。

```bash
cd 03_Implement/deploy
docker compose up --build -d
curl -fsS http://localhost:8080/api/healthz
curl -fsS http://localhost:8080/api/docs/doc_phase1_canvas
```

ブラウザで `http://localhost:8080` を開きます。Docker を使わない起動方法は [導入手順](installation.md) を参照してください。

標準サンプルの確認で `Internal Server Error` が表示される場合は、まず backend が起動しているかを確認します。Docker を使わない場合は、frontend だけでなく backend も別端末で起動してから、`http://127.0.0.1:<frontend-port>/api/docs/doc_phase1_canvas` が成功することを確認してください。

## 画面全体を見る

起動後は、ヘッダー、キャンバス、右側パネルが見えることを確認します。ヘッダーには SafeMode、表示、検索、共有と再現、保存などの主要操作があります。

![起動後の標準画面](assets/screenshots/app-canvas-overview.png)

## マウスで確認すること

1. 新規ドキュメントを作成する。
2. カードを選択し、キャンバス上で移動する。
3. 必要に応じて島を作成し、右側パネルの情報が更新されることを確認する。
4. `表示` を開き、表示モードや SafeMode の状態を確認する。
5. `共有と再現` を開き、共有や export の前に出力範囲と SafeMode を確認する。
6. 保存し、ページを再読み込みして変更が残っていることを確認する。

操作中に、ボタンやパネルが見切れる、隣の操作を覆う、押した後の結果が分からない、という状態があれば記録してください。

## キーボードで確認すること

1. `Tab` でヘッダー、キャンバス操作、右側パネルへ移動できることを確認する。
2. フォーカス中のボタンを `Enter` または `Space` で実行できることを確認する。
3. `表示` や `共有と再現` のパネルを開いたあと、次に操作すべき項目へ自然に移動できることを確認する。
4. 文字入力欄では、入力、削除、保存または反映の流れが分かることを確認する。
5. 操作をやめたいときに、キャンセル、閉じる、または別の場所への移動で自然に戻れることを確認する。

キーボードだけで主要操作に届かない場合や、同じ名前の操作が複数出て迷う場合は、UI/UX の課題として記録してください。

## 表示幅を変えて確認する

画面崩れを確認するときは、少なくとも次の幅を見ます。

| 幅 | 目的 |
| --- | --- |
| 1280px | 標準的な desktop |
| 960px | 狭めの desktop / tablet |
| 390px | mobile 相当 |

すべての細部を見る必要はありません。主要操作が見えるか、テキストが重ならないか、保存できるかを優先します。

390px では、ヘッダーが複数行に折り返され、検索、表示、共有と再現、保存などの主要操作が画面外へ消えないことを確認します。

![390px viewport のヘッダー確認](assets/screenshots/mobile-toolbar-smoke-390.png)

## 共有や export の前に確認すること

share/export を使う場合は、[データ取り扱い](data_handling.md) のチェックリストに沿って、出力に秘密情報や内部メモが混ざっていないことを確認します。

![共有と再現パネルの export/share 前チェック](assets/screenshots/share-export-safe-mode.png)

## 問題を記録するとき

次の情報があると、再現と修正がしやすくなります。

- 対象 URL
- ブラウザ名
- 画面幅
- 操作手順
- 期待した結果
- 実際の結果
- 可能ならスクリーンショット

ログやスクリーンショットを共有するときは、API key、token、password、未加工の顧客情報を含めません。どこまで残すか迷う場合は [データ取り扱い](data_handling.md) を確認してください。

## 開発者向け自動テスト

Playwright E2E や PR 前の自動確認は、公開利用者向けの本文ではなく、GitHub 上の [開発者向け E2E Testing](https://github.com/hat47x/kj-atlas/blob/main/03_Implement/frontend/docs/e2e_testing.md) を正本として管理します。


## Product QA Gate（P0）に沿った記録

受け入れ確認を実施したら、次の4点を最低限記録します。

- Candidate（対象PR/コミット）
- Gate結果（Go / Conditional Go / No-Go）
- 証跡（実行コマンド、画面幅、スクリーンショット、失敗時メモ）
- No-Go/Conditional Go時の戻し先 issue と再判定日

この記録は `issue-PRODUCT-QA-01-release-readiness-quality-gates.md` の Gate Record と同じ項目で管理します。

## 関連文書

- [導入手順](installation.md)
- [運用手順](operations.md)
- [診断と障害調査](diagnostics.md)
- [データ取り扱い](data_handling.md)
- [セキュリティ](security.md)


## UI Operability ADR-0030 に基づく実装前確認（計画）

本節は **実装前の仕様確認計画** です。コード変更手順ではありません。

- 開始→選択→表示→閉じる→復帰 の5段階で確認観点を記録する。
- `Escape` での閉じると、起点フォーカス復帰を観測可能な受入条件として扱う。
- キーボード到達性（カード/島/主要操作）と段階的開示（文脈優先）を同時に確認する。
- 詳細要件は `ADR-0030` と `issue-UX-OPERABILITY-01`〜`04` を正本として参照する。


## QA/Release Gate 実行順（PRODUCT-QA-01 / MVP-EXIT-01）

1. 手動smoke（主要操作 + SafeMode + 共有前確認）
2. 回帰（typecheck / unit / regression guard）
3. E2E（compose優先、不可時mock）
4. 公開文書・運用文書整合確認
5. Gate Record記入と Exit 判定（Pass/Conditional/Fail）

失敗時は次工程へ進まず、Blocker一覧に「再現手順・影響範囲・再開条件」を記録します。
