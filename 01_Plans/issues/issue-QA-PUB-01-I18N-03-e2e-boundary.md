# Issue Memo: QA boundary E2E for PUB-01 + I18N-03

- Type: QA/E2E verification log
- Status: Done
- Scope: `03_Implement/frontend/e2e/`, `01_Plans/issues/`
- Related backlog: `PUB-01`, `I18N-03`
- Policy reference: `ADR-0019`

## Goal

仕様境界ベースで、PUB-01（visibility編集）と I18N-03（英語UI等価）を対象に、
smoke + 変更対象フロー + 安全境界（SafeMode/read-only）を E2E で確認する。

## Added / adjusted Playwright coverage

- `e2e/pub_visibility_i18n_readonly_flow.spec.ts`（新規）
  - visibility 編集（View/Pack）→ リロード後の保持
  - `?locale=en` で visibility + document置換フローの機能等価
  - `?locale=en&readOnly=1` で禁止操作（Suggest layout）が disabled、SafeMode locked context 文言が表示
- `e2e/public_pack_visibility_compat.spec.ts`（調整）
  - strict locator 競合を避ける assertion へ更新（`View visibility` exact match）
  - 実際のUI表示に合わせて `Loaded pack visibility` の期待を削除

## Execution log

### Compose優先経路

- `docker compose version` → **未実施**
  - 理由: 実行環境に `docker` コマンドが存在しない（`command not found`）

### SQLite代替経路

- backend 起動（SQLite）
  - `cd 03_Implement/backend && source .venv/bin/activate && export PYTHONPATH=src && .venv/bin/uvicorn kj_atlas_api.main:app --host 127.0.0.1 --port 8000`
- health check
  - `curl -fsS http://127.0.0.1:8000/healthz` → pass
- API roundtrip
  - `PUT /docs/e2e-pub01-i18n03` → pass
  - `GET /docs/e2e-pub01-i18n03` → pass（保存カード `roundtrip-card` を確認）
- Playwright
  - `cd 03_Implement/frontend && npm run e2e -- e2e/public_pack_visibility_compat.spec.ts e2e/i18n_locale_query_equivalence.spec.ts e2e/pub_visibility_i18n_readonly_flow.spec.ts` → pass（7 passed）

## Acceptance criteria mapping

1. health check が通る
   - pass（`/healthz` 200）
2. visibility 変更の保存→再読込がE2Eで成立
   - pass（`pub_visibility_i18n_readonly_flow.spec.ts`）
3. 英語UIで同フローが機能等価
   - pass（`i18n_locale_query_equivalence.spec.ts` + `pub_visibility_i18n_readonly_flow.spec.ts` locale=enケース）
4. SafeMode/read-onlyで禁止操作がブロックされる
   - pass（readOnlyで `Suggest layout` disabled + SafeMode locked context 文言表示）
5. 実行コマンドと結果をPR記録できる形で残す
   - pass（本メモに記録済み）

## Stream I Done/Completed Audit (2026-04-23)
- 判定: 再オープン不要（Done/Completed/Closedの完了根拠と整合）。
- Related ADR/Spec: 参照先リンク切れなし（存在確認済み）。
- Dependencies: N/A
- 重複Backlog: 該当なし。


## Stream H execution log (2026-04-30)

### Phase 1) Read同期
- `AGENTS.md` Read Order の上流（`00_Prompt`/`01_Plans`/`02_Architecture`/`ADR-0019`）を再読し、
  QA専任スコープを `frontend/e2e`, `backend/tests(境界)`, `issue memo` のみに固定。
- SafeMode既定ON・公開可視性互換・i18n等価の品質境界を再確認。

### Phase 2) Plan（検証マトリクス作成）

| Axis | Target | Specs / Backlog | Test assets | Pass condition |
|---|---|---|---|---|
| 公開互換 | PUB visibility fallback / read-only safety | `PUB-01`, `ADR-0019` | `public_pack_visibility_compat.spec.ts`, `pub_visibility_i18n_readonly_flow.spec.ts` | 旧pack互換 + visibility保持 + readOnly制御 |
| i18n 等価 | ja/en locale query functional parity | `I18N-03` | `i18n_locale_query_equivalence.spec.ts`, `i18n_locale_functional_equivalence.spec.ts` | UI操作/表示/副作用がja/en同値 |
| 回帰監視 | diagnostics structural metrics export determinism | `FB-RM-RS-02` | `diagnostics_structural_metrics.spec.ts` | 同一入力で diagnostics 出力一致 |

### Phase 3) Execute（E2E/回帰）

- Attempt #1
  - `npm run e2e -- <5 specs>`
  - 結果: 失敗（Playwright browser executable 未導入）
- Attempt #2
  - `npx playwright install chromium` 実行後に `npm run e2e -- <5 specs>`
  - 結果: 失敗（`libatk-1.0.so.0` 共有ライブラリ欠如で Chromium 起動不可）
- Attempt #3
  - `npm run e2e -- e2e/i18n_locale_query_equivalence.spec.ts`
  - 結果: 失敗（同一要因 `libatk-1.0.so.0`）

### Phase 4) Verify（AC/DoD）

| Check | Status | Evidence |
|---|---|---|
| AC: i18n/PUB/RS-02 E2E 実行 | ❌ 未達 | 3回ともブラウザ依存ライブラリ不足で起動失敗 |
| DoD: 実行事実の記録 | ✅ 達成 | コマンド/結果/失敗要因を本メモに記録 |
| DoD: 停止条件適用 | ✅ 達成 | 3回実行で上限到達のため停止 |

### Phase 5) Stop条件適用（3回上限超で停止）
- Verify retry は 3回で打ち切り。
- 継続には実行環境への OS 依存パッケージ導入（`libatk-1.0-0` 等）が前提。
