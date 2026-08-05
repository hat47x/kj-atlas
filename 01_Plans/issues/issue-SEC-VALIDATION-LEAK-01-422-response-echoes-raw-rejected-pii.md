# Issue: SEC-VALIDATION-LEAK-01 グローバルなRequestValidationErrorハンドラが拒否された生PII値を422レスポンスへそのまま返す

- Type: Security
- Status: Draft
- Source Issue: N/A
- Priority: P2
- Owner: Maintainer
- Scope: `03_Implement/backend/src/kj_atlas_api/main.py`, `03_Implement/backend/src/kj_atlas_api/routes/ai.py`, `03_Implement/backend/src/kj_atlas_api/routes/ai_relations.py`, `03_Implement/backend/src/kj_atlas_api/routes/context.py`
- Related ADR/Spec: `issue-SEC-DOC-BOUND-03-context-query-constraints-unbounded-recursive-shape.md`, `issue-SEC-AUDIT-LOG-01-proposal-decision-reason-unmasked-in-server-log.md`
- Expected verification level: `integration`

## 課題

- 現在の問題:
  - `main.py:120-122`の唯一の`RequestValidationError`ハンドラは次の通り:
    ```python
    @app.exception_handler(RequestValidationError)
    def handle_validation_error(_, exc: RequestValidationError) -> JSONResponse:
        return JSONResponse(status_code=422, content={"detail": exc.errors()})
    ```
    `exc.errors()`はpydantic v2の既定挙動として、各エラー辞書に検証に失敗した生の値を`input`キーで含む。`include_input=False`等のフィルタリングは行われていない。
  - `models.py:644-671`の`ReviewAttribution.reviewerRef`/`ownerRef`は、まさにメールアドレスや`sso:`/`oidc:`/`saml:`/`provider:`接頭辞付きの生の外部IDを「opaqueでない」として拒否するバリデータであるが、`DocumentV1.reviewAttribution`（`models.py:842`）を含む`doc: DocumentV1`を直接受け取る`/ai/*`系エンドポイント（`CheckNarrativeRequest`/`GenerateNarrativeRequest`/`SuggestIslandSummaryRequest`/`SummarizeIslandRelationRequest`（`models_ai.py`）、`SuggestLayoutRequest`/`SuggestMergesRequest`（`models.py`）、それぞれ`routes/ai.py`・`routes/ai_relations.py`の該当handlerに直結）は、FastAPI自身のリクエストボディ自動検証を経由するため、バリデータが拒否した直後にこのグローバルハンドラが422レスポンスへ生の値をそのまま含めてしまう。つまり「opaqueでなければならない」と拒否した値そのものをレスポンスボディで露出する。
  - 対照的に`PUT /docs/{doc_id}`（`routes/docs.py:96-113`の`_validate_document_payload_with_a1_contract`）は手動でpydanticの`ValidationError`を捕捉し、`errors[0].get("msg")`のみを使う独自の`A1ErrorResponse`を構築しており、`input`キーを含めない。この安全性は`tests/test_docs_a1_error_contract.py::test_put_document_returns_a1_error_contract_for_pii_violation`で確認されている。`/ai/*`系にはこの保護が無い。
  - `routes/context.py:36`の`_validate_payload`も同一の`raise HTTPException(status_code=400, detail=exc.errors())`パターンを持つが、対象モデル（`ContextQuery`等）には現状reviewerRef相当のPIIフィールドが見当たらないため、同種のアンチパターンとして参考記載するに留める。
- 利用者または開発への影響: `/ai/check-narrative`・`/ai/generate-narrative`・`/ai/suggest-layout`・`/ai/suggest-merges`・`/ai/suggest-island-summary`・`/ai/relations/summarize-island-relation`のいずれかに、`reviewAttribution.reviewerRef`/`ownerRef`がメールアドレスやプロバイダ接頭辞付きの値であるドキュメントを送信すると、拒否はされるが、その拒否された生の値がHTTPレスポンスボディにそのまま含まれる。クライアント側やAPIゲートウェイのアクセスログにレスポンスボディを記録する構成があれば、そこにも残る。

## 対応方針

- 実施すること: 修正方針をMaintainerが決定する。候補:
  - (a) `handle_validation_error`で`exc.errors()`の各要素から`input`キーを一律削除する（デバッグ性は全エンドポイントで低下するが、実装は最小）。
  - (b) `routes/docs.py`の`A1ErrorResponse`のような、フィールド単位で安全な独自エラーレスポンスを`/ai/*`系にも構築する（既存の安全パターンの流用だが、対象フィールドの選定という判断を伴う）。
  - (c) `input`を含めたまま返してよいフィールドとそうでないフィールド（`reviewerRef`/`ownerRef`等）を判別するallowlist/denylistを設ける。
  - いずれを採るか、また`routes/context.py`の同種パターンも同時に対応するかはMaintainerの判断。
- 実施しないこと: 修正方針の選定なしに`input`キーを機械的に削除すること。全エンドポイントのデバッグ性への影響を考慮せずに一律適用すべきではない。

## 受入条件

- [ ] 修正方針が決定される。
- [ ] `/ai/*`系エンドポイントに対して、`reviewerRef`/`ownerRef`にメールアドレス等の生PIIを含むドキュメントを送信しても、422レスポンスに当該値が含まれないことを確認する。
- [ ] `tests/test_docs_a1_error_contract.py::test_put_document_returns_a1_error_contract_for_pii_violation`と同種の統合テストを対象エンドポイントに追加する。
- [ ] 宣言した検証を実行するか、未実施理由を記録する。

## 検証計画

- 実行する確認: 実装後、`reviewerRef`にメールアドレスを設定したドキュメントを対象の各`/ai/*`エンドポイントへ送信し、レスポンスボディに当該メールアドレス文字列が含まれないことを確認する統合テスト。
- 期待結果: 拒否は従来通り発生するが、拒否された生の値はレスポンスに含まれない。

## 補足

- 発見経緯: 第32ラウンドの「backend sensitive-data-logging」観点監査で発見。独立検証者が`main.py`のハンドラ実装、`models.py`のバリデータ、6つの`/ai/*`エンドポイントの型付きリクエストモデル定義、および`routes/docs.py`の安全な対照パターンを直接確認し、`01_Plans/issues/`内に本ギャップ（422レスポンスの`input`キー経由のPII露出）を扱う既存issueが無いことを確認済み。`issue-SEC-DOC-BOUND-03`は同じハンドラに言及するが「uncaught 500へのcatch-allが無い」点のみを扱っており本issueとは別観点。`issue-SEC-AUDIT-LOG-01`はサーバーログ内の別フィールド（`reason`）の露出であり、本issueが指すHTTPレスポンスボディ経由の露出とは経路が異なる。
