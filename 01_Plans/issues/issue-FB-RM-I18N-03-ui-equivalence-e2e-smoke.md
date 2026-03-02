# Issue Memo: FB-RM-I18N-03 UI equivalence E2E smoke gate

- Type: QA/E2E
- Status: Done (Local)
- Scope: `03_Implement/frontend/e2e/`, `01_Plans/issues/`
- Related Backlog: `FB-RM-I18N-03` (`01_Plans/adr/ADR-0007-future-backlog.md`)
- Expected verification level: `e2e`

## Goal

直近の i18n 等価化変更に対して、価値境界ベースの最小有効E2E（smoke + 変更フロー）を追加し、
Compose不可環境でも SQLite 代替経路で品質ゲートを継続できる状態を作る。

## Added scenario

- `e2e/i18n_locale_query_equivalence.spec.ts`
  - smoke: `?locale=en` で主要シェル導線（Share / View）が英語表示になる
  - flow: `?locale=en` で Share Panel の `Load document.json -> Replace current document` が成功し、カード表示まで到達

## Validation log (2026-03-02)

- Compose優先経路:
  - `docker compose version` -> 未実施（環境に docker コマンドが存在しない）
- SQLite代替経路:
  - backend: `uvicorn kj_atlas_api.main:app --host 127.0.0.1 --port 8000`
  - frontend: `npm run dev -- --host 127.0.0.1 --port 4173`
  - health:
    - `curl -fsS http://127.0.0.1:8000/healthz` -> pass
    - `curl -fsS http://127.0.0.1:4173/api/healthz` -> pass
  - docs roundtrip:
    - `PUT /docs/e2e-qa-roundtrip` -> pass
    - `GET /docs/e2e-qa-roundtrip` -> pass
  - Playwright:
    - `npm run e2e -- e2e/i18n_locale_query_equivalence.spec.ts` -> pass
    - 再実行（flake check）`npm run e2e -- e2e/i18n_locale_query_equivalence.spec.ts` -> pass
