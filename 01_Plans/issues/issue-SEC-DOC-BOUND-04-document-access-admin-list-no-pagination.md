# Issue: SEC-DOC-BOUND-04 GET /tenant-admin/document-access がpagination無しでテナント全ドキュメントを返す

> 個人OSS・プレリリース段階では `ADR-0039` を適用し、実行に必要な情報だけを記載する。

- Type: Security
- Status: Draft
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P2
- Owner: Maintainer
- Scope: `03_Implement/backend/src/kj_atlas_api/routes/document_access_admin.py`, `03_Implement/backend/src/kj_atlas_api/document_access_metadata_repository.py`
- Related ADR/Spec: `issue-SEC-DOC-BOUND-01-unbounded-document-and-identity-fields.md`, `issue-SEC-DOC-BOUND-02-unbounded-list-fields-in-llm-prompts.md`
- Expected verification level: `integration`

## 課題

- 現在の問題:
  - `list_document_access_settings`（`routes/document_access_admin.py:236-250`、`GET /tenant-admin/document-access`）は`request`と`db`以外のクエリパラメータを一切受け取らない。
  - 呼び出し先の`list_document_access_metadata_entries`（`document_access_metadata_repository.py:52-73`）は次のクエリを`.limit(...)`無しで実行する:
    ```python
    rows = db.execute(
        select(DocumentRow.id, DocumentAccessMetadataRow)
        .outerjoin(DocumentAccessMetadataRow, and_(...))
        .where(DocumentRow.tenant_id == tenant.tenant_id)
        .order_by(DocumentRow.id.asc())
    ).all()
    ```
  - `DocumentRow`はテナントが持つドキュメント本体のテーブルであり、件数の自然な上限が無い。テナントのドキュメント数が増えるほど、このエンドポイントは1回のレスポンスで全件（joinしたaccess-metadata含む）を返し続ける。
  - `03_Implement/backend/src/kj_atlas_api`全体を`.limit(`でgrepしても既存のpagination規約が0件で、模倣できる「境界のある兄弟パターン」が存在しない。
- 利用者または開発への影響: テナントのドキュメント数が増加するにつれ、このエンドポイントへの毎回の呼び出しでDB負荷とレスポンスペイロードサイズが無制限に増加する。クライアント側が部分取得する手段も無い。

## 対応方針

- 実施すること: pagination方式（offset/limit方式か、`DocumentRow.id`をcursorにしたcursor方式か）と、デフォルト/最大ページサイズをMaintainerが決定する。既存の`GET /docs`一覧系エンドポイント（もしpagination規約があれば）との整合も確認する。
- 実施しないこと: pagination方式選定なしに特定のデフォルト値だけを機械的に追加すること（模倣できる既存規約が無いため）。

## 受入条件

- [ ] pagination方式（offset/limitまたはcursor）とデフォルト/最大ページサイズが決定される。
- [ ] 実装後、大量ドキュメントを持つテナントでもレスポンスサイズが上限内に収まることを確認する。
- [ ] 宣言した検証を実行するか、未実施理由を記録する。

## 検証計画

- 実行する確認: 実装後、多数のドキュメントを持つテナントに対する統合テストで、レスポンス件数が指定した上限を超えないこと、および次ページ取得手段が機能することを確認する。
- 期待結果: レスポンスサイズが常に上限内に収まり、テナントのドキュメント数増加に対してO(1)に近い応答時間・ペイロードサイズを維持する。

## 補足

- 発見経緯: 第31ラウンドの「backend unbounded-query/resource-exhaustion」観点監査で発見。独立検証者が`document_access_metadata_repository.py`のクエリと`tenant_db_guard.apply_database_tenant_context`（tenant絞り込みのみでrow capは無い）を直接確認し、`01_Plans/issues/`内に同一ギャップを扱う既存issueが無いことを確認済み。関連する`SEC-DOC-BOUND-01/02/03`はいずれも書き込み経路（リクエスト側フィールド長・件数上限）を扱っており、本issueが指す読み取り経路（レスポンス側pagination欠如）とは別種の問題。
