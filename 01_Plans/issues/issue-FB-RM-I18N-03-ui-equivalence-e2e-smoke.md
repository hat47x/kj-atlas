# Issue Memo: FB-RM-I18N-03 UI equivalence E2E smoke gate

- Type: QA/E2E
- Status: Done
- Source Issue: N/A (GitHub Issues are not used in current operations)
- Priority: P1
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

## Task contract freeze (2026-03-03)

### Scope
- Frontend i18n functional-equivalence verification for ja/en in unit + E2E.
- Observation points are fixed as: **操作可否 / 表示文言 / 副作用（永続状態） / export結果**.
- SafeMode + readOnly behavior parity verification in ja/en.

### Non-Goals
- 新規ロケール追加（fr等）は対象外。
- 文言改善・翻訳品質改善（意訳調整）は対象外。
- API/Backend のlocale-aware behavior追加は対象外。

### Acceptance Criteria (AC)
- [x] AC1: ja/en切替で主要UI操作（Share導線・document置換）が同一に成立する（E2E）。
- [x] AC2: ja/enでSafeMode + readOnlyの禁止操作・固定マスク挙動が同値（E2E）。
- [x] AC3: ja/enで辞書キー等価 + fallback契約（requested -> ja -> key）を維持（unit）。
- [x] AC4: export結果はlocaleに依存せず決定論が維持される（unit）。
- [x] AC5: VerifyでAC/DoD照合結果を記録し、未達なら原因/次手を明記。

### Checks
- [x] unit: i18n translate / i18n UI equivalence / bundle export locale-independence
- [x] e2e: locale=en smoke + replace flow, visibility persistence, safeMode/readOnly parity (ja/en)
- [x] contract: fallback order and dictionary key-equivalence remain green

## Verify (AC / DoD cross-check)

| ID | 判定 | 根拠 |
|---|---|---|
| AC1 | ✅ 達成 | `i18n_locale_query_equivalence.spec.ts` と `pub_visibility_i18n_readonly_flow.spec.ts` の locale=en flow が pass。 |
| AC2 | ✅ 達成 | `i18n_locale_functional_equivalence.spec.ts` で ja/en それぞれ readOnly + SafeMode locked context を確認。 |
| AC3 | ✅ 達成 | `src/i18n/translate.test.ts` で fallback順序・辞書キー等価テストが pass。 |
| AC4 | ✅ 達成 | `src/export/bundle_export.test.ts` の locale差分非依存ハッシュ検証が pass。 |
| AC5 | ✅ 達成 | 本セクションでAC/DoD全照合を明文化。 |

### 未達
- なし。

### 備考
- E2E実行時に dev server から `/docs/*` proxy の `ECONNREFUSED` 警告は出るが、今回のフローは UI-only でテストはすべて pass。

## Stream I Done/Completed Audit (2026-04-23)
- 判定: 再オープン不要（Done/Completed/Closedの完了根拠と整合）。
- Related ADR/Spec: 参照先リンク切れなし（存在確認済み）。
- Dependencies: `FB-RM-I18N-03` (`01_Plans/adr/ADR-0007-future-backlog.md`)
- 重複Backlog: 該当なし。
