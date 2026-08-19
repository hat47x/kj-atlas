# Issue: SEC-DOC-BOUND-06 `GET /docs` 一覧と archive/unarchive が visibility・capability を経ない

- Type: Security / Bug
- Status: Done
- Source Issue: N/A
- Priority: P1
- Owner: Maintainer
- Scope: `03_Implement/backend/src/kj_atlas_api/routes/docs.py`, `03_Implement/backend/src/kj_atlas_api/access_control.py`, `02_Architecture/api.md`, `02_Architecture/schemas.md`
- Related ADR/Spec: `01_Plans/adr/ADR-0073-document-ownership-and-lifecycle-model.md`, `01_Plans/adr/ADR-0059-saas-tenant-authorization-boundary.md`, `02_Architecture/post-mvp-business-scope-design-program.html` §8.2/§9
- Norms: `DOM-AI-06`（本issueはAI経路ではなく人間の通常操作の欠落だが、同じ「承認なしに適用される」構造を持つ）
- Expected verification level: `integration`

## 三要素整合（ADR-0067）

- **業務設計（Business）**: テナント内の一利用者が、自分に read 権限の無い `Restricted` 文書の存在・タイトル・作成者を一覧で知り、その文書を archive/unarchive できてよいかは、業務として決めた記憶が無い。`ADR-0073` D1=C は「管理権は capability」と定めたが、archive/unarchive という具体操作にその capability チェックが反映されていない。
- **データ設計（Data）**: `document_access_metadata.visibility`（Public/Unlisted/Org/Restricted）は単一文書の読み取りをゲートする設計で作られ、一覧という集合演算を想定していない。
- **機能設計（Function）**: 単一文書の `GET`/`PUT /docs/{doc_id}` は `_authorize_request()` を経由し PDP（`access_control_adapter`）へ照会するが、`GET /docs`（一覧）と `POST /docs/{doc_id}/archive`・`/unarchive` は `_resolve_request_tenant()` のみを呼び、tenant一致だけを確認する。

## 課題

- 現在の問題: `03_Implement/backend/src/kj_atlas_api/routes/docs.py` の `list_documents()` と `_transition_lifecycle()`（`archive_document`/`unarchive_document` が呼ぶ）は、いずれも `_resolve_request_tenant()` のみでテナントを解決し、`get_document`/`put_document` が呼ぶ `_authorize_request()`（`document_access_resource_resolver` → `access_control_adapter` PDP照会）を経由しない。

  結果として、同一テナント内であれば：
  1. 自分に read 権限の無い `Restricted`/`Org` 文書の `id`・`title`・`created_by`・`lifecycle_state` を一覧経由で知ることができる（本文カードは含まれないため被害は限定的だが、存在の秘匿としては破れている）。
  2. 自分に write 権限の無い文書を archive/unarchive できる（`archived` になった文書は `put_document` の 423 チェックにより読み書き不能になるため、閲覧権限を持つ他者への実質的なDoSになり得る）。

  `02_Architecture/api.md` §2.2 はこれを「認可：tenant-scoped」と正直に記載しているが、同ファイル §2.4（実装前に書かれた `DATA-MODEL-OPS-02` 契約、本issue対応後に削除予定）は同じ `GET /docs` に対して「対象集合：現認可主体がread可能な文書のみ」という逆の契約を記載していた。実装時にこの契約差分が見落とされたと考えられる。

- 利用者または開発への影響: `visibility=Restricted` を選んだ利用者の期待（「この文書はこの人たちにしか見えない」）が、一覧経由で部分的に破られる。archive/unarchive については、閲覧権限のある他利用者の作業を無権限の第三者が妨害できる。

## 対応方針

- 実施すること:
  - `list_documents()` に visibility フィルタを追加する。単一文書向けの `_authorize_request()` は `doc_id` 1件を前提とするため、そのまま流用できない。**集合に対する認可**という新しい形が要る（例: PDPに「このtenant・このprincipalが read 可能な doc_id 集合」を問い合わせるバルクAPI、または `document_access_metadata` を直接JOINして `Public`/`Unlisted`/自分が member の `Org`/自分が対象の `Restricted` のみを返すクエリ）。
  - `_transition_lifecycle()`（archive/unarchive）に write capability 相当の確認を追加する。最小対応として `_authorize_request(action="write", ...)` を通す。
  - 上記適用後、`02_Architecture/api.md` §2.2 の「認可：tenant-scoped」の記述を実際の挙動に更新する。
  - 対応完了後、`02_Architecture/api.md` §2.4 と `02_Architecture/schemas.md` §3.4.1（廃止済みマーカーを付けた旧契約）を削除する。

- 実施しないこと:
  - 一覧のページネーション（`SEC-DOC-BOUND-05`）の変更。本issueは認可の欠落のみを扱う。
  - 新しい capability 種別・PDP契約全体の再設計。既存の `AccessControlAdapter`/`resolve_access_decision` の拡張で収める（`access_control.py` の `AccessAction` に `"list"` 相当を追加するか、既存 `"read"`/`"write"` を集合向けに再利用するかは実装時に判断する）。

## 受入条件

- [x] `visibility=Restricted` で自分が対象外の文書が、`GET /docs` の一覧に現れない
- [x] `visibility=Restricted` で write capability の無い利用者が、`POST /docs/{doc_id}/archive` で 403（または同等の拒否）を受け取る
- [x] 既存の `Public`/`Unlisted`/対象内の `Org`・`Restricted` 文書は一覧・archive/unarchive とも従来通り動作する（回帰なし）
- [x] `api.md` §2.2 の認可記述が実装と一致する
- [x] `api.md` §2.4・`schemas.md` §3.4.1（廃止マーカー付き旧契約）を削除する
- [x] 検出力の確認: 一覧のvisibilityフィルタ・archive/unarchiveの認可チェックを一時的に無効化した状態でテストが失敗することを確認する

## 対応記録（2026-08-18・archive/unarchive）

- `_transition_lifecycle()`（`archive_document`/`unarchive_document` が呼ぶ）を、`_resolve_request_tenant()` のみから
  `_authorize_request(action="write", ...)` へ切り替えた。`put_document` と同じ認可経路を通るようになった。
- この変更は `PUT`/`GET` が既に確立している認可契約（`_authorize_request`）を**そのまま再利用**するだけであり、
  新しい設計判断を要しない。したがって第3反復を待たずに対応した。
- 一方、`list_documents()` の visibility フィルタは当時対応していなかった。理由: 単一文書向けの
  `_authorize_request`（1リクエスト・1 doc_id・外部PDPへの1回のHTTP照会）を一覧（最大500件）にそのまま
  適用すると、1リクエストあたり最大500回の外部PDP呼び出しが発生し、レイテンシとPDP負荷の観点で許容できない。
  正しい解決には「集合に対する認可」という新しい照会形が要り、これは個別の場当たり対応ではなく
  第3反復（協働）の設計として最初から扱うべきと判断した。
- 検証: `test_docs_access_control_integration.py` に `test_archive_denied_by_adapter`・
  `test_unarchive_denied_by_adapter` を追加。修正前のコードに対して一時的に適用し、
  403 を期待する箇所が実際に 204（無認可で成功）を返すことを確認したうえで、修正を戻して緑化した。
  既存56件（一覧・archive関連含む）・access-control-integration19件は回帰なし。

## 対応記録（2026-08-19・一覧のvisibilityフィルタ、完了）

第3反復（協働、`post-mvp-business-scope-design-program.html` §11.2）で設計した方式を実装した。
`Public`/`Unlisted`/`Org` は無条件表示、`Restricted`（メタデータ行が存在しない場合も含む）は作成者本人にのみ表示する。
外部PDPの契約変更・追加照会は不要——`document_access_metadata.visibility` という既存のローカル列だけで判定する。

- **既定のnoopアダプタとの整合を確認・修正した。** `access_control_adapter` の既定値は `None` ではなく
  `NoopAccessControlAdapter`（常に許可）であり、この既定構成では単一文書の `GET`/`PUT /docs/{doc_id}` も
  `apply_tenant_boundary_guard` のみを経由し、visibility を一切参照しない。したがって「アダプタが設定されているか」
  だけでフィルタの有効・無効を判定すると、既定構成（本番の大半）で一覧だけが単一文書より厳しくなり、
  ユーザから見えるはずの文書が一覧に出ないという回帰を生む。実際に最初の実装で `test_docs_list_filters_by_creator`
  等4件が回帰し、この問題を検出した。判定を「アダプタが設定され、かつ `name != "noop"`」に修正して解消した。
- `list_documents()`（route）は `_resolve_request_identity_and_tenant()`（新設。呼び手のuser_idも返す）を呼び、
  `DatabaseDocumentContentStore.list_documents()` に `requesting_user_id`・`apply_visibility_filter` を渡す。
  後者はSQL側で `document_access_metadata` を `outerjoin` し、`visibility IN (Public,Unlisted,Org) OR created_by = :requesting_user_id`
  で絞り込む。ページネーション（`SEC-DOC-BOUND-05`）はこのWHERE句の上に乗るため、`has_more`/カーソルの正しさは保たれる。
- `_resolve_request_tenant()` は既存の呼び出し元（テスト含む）と互換性を保つため、新設関数への薄いラッパーとして残した。
  `test_tenant_session_precondition.py` のAST静的検査（各ルートがテナント境界チェックを呼んでいることを検証する）が
  ルート本体の直接呼び出ししか見ないため、新設関数を検査対象のフローセットへ追加した。
- 検証: `test_docs_access_control_integration.py` に4件追加
  （作成者本人には表示・他者には非表示、metadataなしの文書もRestricted扱い、Public/Orgは全員表示、
  noopアダプタ時はフィルタが効かないことの回帰ガード）。フィルタを一時的に無効化して2件が実際に失敗することを確認し、
  修正を戻して緑化した。バックエンド全体1173件 pass（回帰なし）。ruff clean。
- `api.md` §2.2 の認可記述・§2.4（廃止マーカー付き旧契約）・`schemas.md` §3.4.1/§3.4.2 を実装済み状態に更新・整理した。
