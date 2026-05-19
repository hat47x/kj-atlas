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
| 外部接続 | LLM provider、監査ログ連携の接続先、access control の接続先（endpoint） |

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

画面内の diagnostics は、右側パネルの layout/outline 周辺から実行できます。実行後は品質レポート、所見件数、メトリクスが表示されるため、障害調査メモにはこの結果と API status を合わせて残します。

![diagnostics 実行後の品質レポート](assets/screenshots/diagnostics-quality-report.png)

## よくある切り分け

| 症状 | 主な確認 |
| --- | --- |
| 画面が真っ白 | frontend build、console error、nginx logs |
| `Internal Server Error` が表示される | backend が起動しているか、`/api/healthz` と `/api/docs/doc_phase1_canvas` が成功するか |
| 保存に失敗 | API status、`X-API-Key`、backend logs、DB 接続 |
| AI 提案が出ない | `KJ_ATLAS_LLM_PROVIDER`、provider endpoint、SafeMode |
| export が失敗 | 対象ドキュメントの schema、ブラウザ console |
| worker が落ちる | 入力データ、worker console、該当 worker の単体テスト |

## worker 関連の確認

worker 由来の問題が疑われる場合は、まず入力データの大きさ、schema、review 状態を確認します。

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


## 障害分類と一次切り分け（PRODUCT-OPS-01）

5分以内の一次切り分けは、次の分類コードで記録します。

| 分類コード | 判断条件 | 最初の確認コマンド/操作 |
| --- | --- | --- |
| WEB-ENTRY | 画面表示異常が主症状 | ブラウザ Console / `docker compose logs web --tail=100` |
| API-UNAVAILABLE | API応答失敗、502/503 | `curl -fsS http://localhost:8080/api/healthz` / `docker compose logs api --tail=200` |
| SAVE-FAILURE | 保存失敗、再読み込み不一致 | Network status、`docker compose logs db --tail=100` |
| IMPORT-VALIDATION | import時のschema/検証失敗 | importエラーダイアログ、schemaVersion、validation内容 |
| SHARE-SAFEMODE | share/export 前警告、マスク警告 | 共有と再現パネルで SafeMode / visibility 確認 |

## 復旧責務の分離

- First Responder: 分類、再現手順、非機微ログの採取までを担当。
- System Owner: 外部共有可否と復旧優先度を承認。
- Platform Operator: 再起動/設定反映/ロールバックの実行を担当。

停止条件（Stopper）:

- 役割衝突（承認者と実行者が同一で分離できない）。
- 承認責務が不明（誰が SafeMode 緩和や外部共有可否を決めるか未定）。
- secrets 除去前の生ログ共有を要求される。

上記が1つでも該当する場合、復旧作業を先に進めず `operations.md` のエスカレーション導線へ切り替えます。

## 手順再現性チェック

調査完了時に次の3点を必ず残します。

1. 同じ症状を再現できる最小手順（3〜7ステップ）。
2. 実行コマンドと結果（成功/失敗）。
3. 再試行時に必要な前提（環境変数、SafeMode状態、対象ドキュメント）。

## 復旧の基本

1. 変更直後なら、直前の設定差分を確認します。
2. DB 接続や migration エラーなら backend logs を確認します。
3. frontend の表示だけ壊れている場合は cache を無効化して再読み込みします。
4. LLM や audit HTTP 連携が関係する場合は、一度 `KJ_ATLAS_LLM_PROVIDER=none`、`KJ_ATLAS_AUDIT_EXPORT_ENABLED=false` に戻して再確認します。

復旧を急ぐ場合でも、秘密情報を含むログをそのまま共有しないでください。共有前に API key、token、個人情報、生の顧客データを除去します。

## 関連文書

- [operations.md](operations.md)
- [configuration.md](configuration.md)
- [acceptance_check.md](acceptance_check.md)
- [data_handling.md](data_handling.md)
- [security.md](security.md)

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
