# Issue: DX-DOC-05 3件のbackend endpointがapi.md/schemas.mdに未記載

> 個人OSS・プレリリース段階では `ADR-0039` を適用し、実行に必要な情報だけを記載する。

- Type: Documentation
- Status: Draft
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P3
- Owner: Maintainer
- Scope: `02_Architecture/api.md`, `02_Architecture/schemas.md`
- Related ADR/Spec: `03_Implement/backend/src/kj_atlas_api/routes/admin.py`, `03_Implement/backend/src/kj_atlas_api/routes/docs.py`, `03_Implement/backend/src/kj_atlas_api/routes/ai.py`
- Expected verification level: `docs-check`

## 課題

- 現在の問題: 次の3つのbackend endpointは実装済み・`response_model`宣言済みだが、`api.md`と`schemas.md`のいずれにも一切記載がない（該当route/model名でgrepして0件）。
  1. `POST /admin/hil-rs/a2a3-gate:validate`（`admin.py:224`、`response_model=A2A3GateValidationResponse`：`go`/`schemaVersion`/`freezeContractId`）。関連する`hil_rs_01_a1_minimum_interface_contract.md`は判定ロジック（`A2A3_OPEN_ALLOWED`）のみ記載し、実際のresponse形状やroute自体には触れていない。
  2. `GET /docs/{doc_id}/similar-candidate-groups`（`docs.py:769`、`response_model=CandidateListViewModel`：`generatedAt`/`groups`/`totalGroupCount`、`SimilarCandidateGroup`の各field）。`data_model_operations_overview.md`の概要表に1行あるのみでfield詳細はない。
  3. `GET /ai/provider-status`（`ai.py:491`、`response_model=ProviderStatusResponse`：`providerKind`）。`llm_provider_spec.md`を含む関連文書のいずれにも記載がない。
- 利用者または開発への影響: これら3 endpointの契約を確認するには実装コードを直接読む必要があり、api.md/schemas.mdを正本として参照する開発フローと整合しない。実害はない（実装自体は正常に動作している）。

## 対応方針

- 実施すること: 3 endpointそれぞれについて、api.md/schemas.mdへ記載するかどうか、記載する場合のタイミング（特に`A2A3GateValidationResponse`はHIL-RS-02関連の実装がまだ進行中の可能性があり、記載後すぐに陳腐化するリスクがある）をMaintainerが判断する。
- 実施しないこと: 3 endpointの文書追記そのもの。特にHIL-RS-02関連endpointについては、実装の安定度を確認せずに文書化すると却って陳腐化リスクを生む。

## 受入条件

- [ ] 3 endpointそれぞれについて、文書化する/しないの方針が決定される。
- [ ] 文書化する場合、`api.md`/`schemas.md`の既存フォーマットに合わせてfield一覧を記載する。

## 検証計画

- 実行する確認: 文書化後、`python3 01_Plans/docs_check.py`。
- 期待結果: 既存の文書契約チェックが通過する。

## 補足

- 発見経緯: SaaSテナント対応マージ後の広範な棚卸し（第7ラウンド）で発見。対照として`PolygonHandoffContractVerificationResponse`・`ProvisionUserResponse`はapi.md/schemas.mdと完全に一致していることを確認済みで、この3件は本当に記載漏れであり、field名の不一致ではない。
