# Issue: DX-DOC-05 実装済みresponse modelをAPI正本へ記載する

- Type: Documentation
- Status: Done
- Source Issue: N/A
- Priority: P3
- Owner: Maintainer
- Scope: `02_Architecture/api.md`, `02_Architecture/schemas.md`, `01_Plans/docs_contract_checks.py`
- Related ADR/Spec: `03_Implement/backend/src/kj_atlas_api/routes/admin.py`, `03_Implement/backend/src/kj_atlas_api/routes/docs.py`, `03_Implement/backend/src/kj_atlas_api/routes/ai.py`
- Expected verification level: `docs-check` and adjacent backend route tests

## 課題

実装済みかつ `response_model` 指定済みの次の3 APIについて、`api.md` と `schemas.md` にresponse contractのまとまった記載がなかった。

1. `POST /admin/provision/hil-rs/a2a3-gate:validate` — `A2A3GateValidationResponse`
2. `GET /docs/{doc_id}/similar-candidate-groups` — `CandidateListViewModel`
3. `GET /ai/provider-status` — `ProviderStatusResponse`

発見時メモでは1件目を `/admin/hil-rs/...` としていたが、router prefixとOpenAPI snapshotを照合し、公開パスは `/admin/provision/hil-rs/...` が正しいと確定した。

## 対応

- `api.md` §2.11に、3 APIの公開パス、response model、主要field、現行のerror・安全境界を記載した。
- `schemas.md` §13に、response view modelの型と不変条件を記載した。
- `DC-API-001` を追加し、APIパス、model名、主要fieldが両正本から脱落した場合にdocs-checkを失敗させるようにした。
- 実装API、Document永続schema、SafeMode、proposal-only境界は変更していない。

## Acceptance

- [x] 3 APIすべてについて文書化方針を確定した。
- [x] `api.md` / `schemas.md` の既存形式に沿ってresponse fieldを記載した。
- [x] 文書契約の再脱落を検出する自動テストを追加した。

## Validation

- `python -m pytest -q 01_Plans/tests/test_docs_contract_checks.py 01_Plans/tests/test_docs_check.py`: 57 passed
- `python 01_Plans/docs_check.py --root .`: passed
- `python -m pytest -q 03_Implement/backend/tests/test_a2_a3_gate_validation.py 03_Implement/backend/tests/test_ai_provider_status_route.py 03_Implement/backend/tests/test_docs_roundtrip.py`: 37 passed, 21 skipped
- `python -m ruff check 01_Plans/docs_check.py 01_Plans/docs_contract_checks.py 01_Plans/tests/test_docs_check.py 01_Plans/tests/test_docs_contract_checks.py`: passed
- `python 01_Plans/issues/validate_active_issue_memos.py --root 01_Plans/issues`: passed（36 active memos）
