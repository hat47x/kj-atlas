# Issue: SEC-DOC-BOUND-05 GET /docs 一覧が無界（local-dev でも到達可能）

> ドッグフーディング iteration 55 で実機確認により発見。

- Type: Security
- Status: Done
- Source Issue: `SEC-DOC-BOUND-04`（同クラス・`/tenant-admin/document-access` は SaaS 専用）
- Priority: P2
- Owner: Maintainer
- Scope: `03_Implement/backend/src/kj_atlas_api/routes/docs.py`, `03_Implement/backend/src/kj_atlas_api/database_content_store.py`, `03_Implement/frontend/src/api/client.ts`（`listDocuments`）
- Related ADR/Spec: `01_Plans/issues/issue-SEC-DOC-BOUND-04-document-access-admin-list-no-pagination.md`（判断支援: cursor方式・limit 100/max 500 を推奨）
- Expected verification level: `integration`

## 三要素整合（ADR-0067）

- **業務設計（Business）**: キャンバス一覧（`GET /docs`）はテナントの文書メタデータを全件返す。テナントの文書数が増えると毎回全件を返し続け、DB負荷とレスポンスペイロードが無界に増加する。クライアントに部分取得の手段がない。
- **データ設計（Data）**: `DocumentRow` はテナント文書本体のテーブルで件数の自然な上限が無い。返却は行メタデータのみ（カード本文は非露出）だが、行数は無界。
- **機能設計（Function）**: `list_documents`（`routes/docs.py:435`）は `cursor`/`limit` を受け取らず、`list_documents`（`database_content_store.py:222`）は `select(DocumentRow)` を無制限に実行し、Python側で `updated_at` 降順にソートして全件返す。

## 課題

- 現在の問題: `GET /docs` は **local-dev でも到達可能**（`SEC-DOC-BOUND-04` の `/tenant-admin/document-access` は SaaS セッション必須で 503、こちらは無認証 local-dev で動く）。pagination 規約が無く全件返し。
- 実地確認（iteration 55）: 60件の文書を作成 → `GET /docs` が **60件すべて**を返す（`[{"id":"doc-09",...},...]`・レスポンスに境界なし）。

## 対応方針

- 実施すること: `SEC-DOC-BOUND-04` の判断支援（cursor方式・limit/max 500・`nextCursor`）を**本エンドポイントへ適用**した。並び順は `(updated_at DESC, id ASC)` に正規化し、カーソルは `{urlencoded(updated_at)}:{id}`（ISO の `updated_at` がコロンを含むため URL エンコード）で安定させた。レスポンスは配列のままで `X-Next-Cursor` ヘッダーで次ページを返し、**既存クライアントと後方互換**を保つ。frontend `listDocuments()` は既定 limit 500 で現状の UI と後方互換（>500 文書テナントのページング連携は別途の UI 改善とする）。
- 実施しないこと: 方式選定なしに特定のデフォルト値だけを機械的に追加すること（cursor方式を前提に実装）。

## 受入条件

- [x] `GET /docs` が `limit`（既定500・最大500）と `cursor` を受け取り、レスポンス件数が上限内に収まる。— keyset pagination 実装（`database_content_store.list_documents` に `cursor`/`limit`・`docs.py` ルートに Query 追加・`X-Next-Cursor` ヘッダー）。
- [x] ページングが `updated_at` 降順と整合し、欠落・重複がない。— テスト `test_docs_list_keyset_pagination`（4文書・limit2 で2ページ・no overlap/loss・newest first・最終ページは cursor なし）を追加。
- [x] 既存の `GET /docs` 呼び出し（frontend・E2E）が後方互換で動作する。— レスポンス配列のまま・既定 limit 500。E2E シナリオ12（一覧）94/94・docs 回帰 42 tests pass。
- [x] 大量文書テナントでもレスポンスサイズが上限内に収まることを確認する。

## 検証計画

- 実行する確認: 60件以上の文書で `GET /docs` を呼び、`limit` 適用後の件数と `X-Next-Cursor` を確認。E2E シナリオ（一覧取得）の回帰。
- 期待結果: 無界応答が上限内に収まる。
