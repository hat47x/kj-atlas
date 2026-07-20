# Issue: SEC-DOC-BOUND-02 追加のリストフィールドがLLMプロンプトへ無制限に埋め込まれる

> 個人OSS・プレリリース段階では `ADR-0039` を適用し、実行に必要な情報だけを記載する。

- Type: Security
- Status: Draft
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P3
- Owner: Maintainer
- Scope: `03_Implement/backend/src/kj_atlas_api/models_ai.py`, `03_Implement/backend/src/kj_atlas_api/models.py`, `03_Implement/backend/src/kj_atlas_api/routes/ai.py`, `03_Implement/backend/src/kj_atlas_api/routes/ai_relations.py`
- Related ADR/Spec: `issue-SEC-DOC-BOUND-01-unbounded-document-and-identity-fields.md`
- Expected verification level: `unit`

## 課題

- 現在の問題: `issue-SEC-DOC-BOUND-01`（前ラウンドで起票済み、`DocumentV1.cards/edges/islands`等が対象）に含まれない、次のリストフィールドが上限無しでLLMプロンプトへ1件ずつ埋め込まれている。
  1. `CheckNarrativeRequest.basedOnReadingOrder`（`models_ai.py:43`、`list[str] | None`）: `routes/ai.py`の`_build_narrative_check_prompt`で1件ごとにプロンプト行を生成し、未一致のidもそのまま埋め込む。
  2. `DocumentV1.readingOrder`（`models.py:833`、`list[str] | None`）: `_build_narrative_check_prompt`と`_build_generate_narrative_prompt`の両方で使用され、`PUT /docs/{doc_id}`で`payload_json`にそのまま永続化もされる。
  3. `SummarizeIslandRelationRequest.cardTexts`/`.edgeTexts`/`.groundingCardIds`/`.groundingEdgeIds`（`models_ai.py:106-109`）: `routes/ai_relations.py`の`_build_relation_summary_prompt`で全件がプロンプトに展開される。このrouteは`db`依存を持たないため永続化はされないが、クライアントが文書実サイズと無関係に任意の件数を送信できる。
- 判断が必要な理由: リポジトリ全体で「リストの件数」に対する`Field(max_length=...)`の先例は、`routes/session.py`の`availableTenants`/`effectiveCapabilities`（いずれもサーバー側で内部的に確定する集合のサイズを守るためのもの）のみで、クライアントが自由に送信するリクエストフィールドに対する件数上限の先例は無い。妥当な上限値（読み順の最大件数、根拠カード/エッジの最大件数、文字列1件あたりの最大長を含む）はプロダクトのキャパシティ判断が必要。
- 利用者または開発への影響: 巨大なリストを送信することで、LLM呼び出しのコスト・レイテンシ増大や失敗を引き起こせる可能性がある。

## 対応方針

- 実施すること: 各フィールドの妥当な上限値をMaintainerが決定する。
- 実施しないこと: 上限値の設定そのもの。模倣できる同種の先例（クライアント自由送信リストの件数上限）が無いため、機械的には対応しない。

## 受入条件

- [ ] 各フィールドについて上限値が決定される。

## 検証計画

- 実行する確認: 対応後、`python3 -m pytest`（backend、該当route）。
- 期待結果: 上限を超える入力が明示的に拒否される。

## 補足

- 発見経緯: 第15ラウンドの棚卸し（`issue-SEC-DOC-BOUND-01`に含まれない未発見のリクエストボディサイズ上限観点）で発見。同じ観点で確認した「Pydanticの自動サイズ制限付きJSONパースを迂回する生のリクエストボディ読み取り」は該当箇所無し（クリーン）。
