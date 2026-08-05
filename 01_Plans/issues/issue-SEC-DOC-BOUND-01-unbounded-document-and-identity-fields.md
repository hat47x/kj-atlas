# Issue: SEC-DOC-BOUND-01 ドキュメント/ユーザー関連フィールドの上限未設定

- Type: Security
- Status: Draft
- Source Issue: N/A
- Priority: P3
- Owner: Maintainer
- Scope: `03_Implement/backend/src/kj_atlas_api/models.py`, `03_Implement/backend/src/kj_atlas_api/models_ai.py`, `03_Implement/backend/src/kj_atlas_api/routes/admin.py`
- Related ADR/Spec: `issue-SEC-INQUIRY-01-inquiry-file-size-limit.md`, `issue-SEC-RATE-LIMIT-01-backend-api-has-no-rate-limiting.md`
- Expected verification level: `unit`

## 課題

- 現在の問題: 次のフィールドは長さ/件数の上限が無く、DB保存またはLLMプロンプトへの埋め込みに使われている。
  1. `DocumentV1.cards`/`.edges`/`.islands`（`models.py:815-817`）: 件数上限が無い。`PUT /docs/{doc_id}`（`routes/docs.py`）でそのまま`payload_json`へ永続化され、`routes/ai.py`の`_build_prompt`/`_build_merge_prompt`/`_build_narrative_check_prompt`/`_build_generate_narrative_prompt`がこれらを反復してLLMプロンプト文字列へ結合する。
  2. `CardBase.text`（`models.py:257`）、`MergeDecisionRecord.note`/`.decidedBy`（`models.py:542-543`）: 文字数上限が無い。同モデルの`mergedTextDraft`/`editedText`（L530-531）も同様に無制限で、模倣できる「境界のある兄弟フィールド」が存在しない。
  3. `CheckNarrativeRequest.narrativeText`（`models_ai.py:42`）: `min_length=1`のみで`max_length`が無く、そのままLLMプロンプトに埋め込まれる。
  4. `ProvisionUserRequest`の`displayName`/`email`/`provider`/`externalUid`（`routes/admin.py:34-40`）: 上限が無いままDBの`UserRow`/`UserIdentityRow`に保存される。
  5. `ActiveTenantRequestV1.tenantId`（`routes/session.py:64`）: 上限が無い。同ファイルの他の識別子フィールド（`id`/`principalId`）は`MAX_SESSION_IDENTIFIER_LENGTH`を使っており一見「同じ定数を適用するだけ」の機械的修正に見えたが、実際に`Field(min_length=1, max_length=MAX_SESSION_IDENTIFIER_LENGTH)`を適用したところ、`test_session_context_routes.py::test_active_tenant_change_rejects_free_or_noncanonical_tenant_ids`が失敗した。このテストは257文字の`tenantId`を送った場合に404（テナント未検出として fail-closed）を期待しているが、Pydanticの`max_length`検証がその前段で422を返してしまう。つまり「不正な形式のtenantIdは404で拒否する」という既存の契約と、「上限を超える長さは422で拒否する」という新しい制約が衝突しており、上限値をどう設定するか（またはテストの期待値をどう変更するか）はMaintainerの判断が必要。
  - いずれも`02_Architecture/schemas.md`/`api.md`に上限の記載が無い（ドリフトではなく、そもそも未規定というギャップ）。
- 利用者または開発への影響: 巨大なドキュメント（カード/島の件数が非常に多い、またはテキストが極端に長い）を送信することで、DB行サイズの肥大化や、LLM呼び出しのコスト・レイテンシの増大（場合によっては呼び出し失敗）を引き起こせる可能性がある。

## 対応方針

- 実施すること: 各フィールドについて妥当な上限値をMaintainerが決定する（ドキュメントあたりの最大カード/エッジ/島数、カード本文の最大文字数、LLMプロンプトに渡すテキストの最大長、表示名/メールアドレスの最大長など）。
- 実施しないこと: 上限値の設定そのもの。模倣できる既存の境界パターンが無い、またはビジネス上の妥当な値を判断する必要があるため、機械的には対応しない。

## 受入条件

- [ ] 各フィールドについて上限値が決定される。
- [ ] 実装後、既存の巨大ドキュメントを扱うテスト（もしあれば）が新しい上限と整合することを確認する。

## 検証計画

- 実行する確認: 上限追加後、`python3 -m pytest`（backend、該当モデルのバリデーションテスト）。
- 期待結果: 上限を超える入力が明示的に拒否されることを確認する。

## 補足

- 発見経緯: 第9ラウンドの棚卸し（入力バリデーション境界観点）で発見。`tenantId`への上限追加は当初「機械的に対応可能」と判断したが、実装して既存テストを実行したところ既存の契約（不正形式は404）と衝突することが判明したため、直接の修正を取り消して本issueに含めた。
