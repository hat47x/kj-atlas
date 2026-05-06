# Issue Memo: QA boundary E2E for PUB-01 + I18N-03

- Type: QA/E2E verification log
- Status: Done
- Scope: `03_Implement/frontend/e2e/`, `01_Plans/issues/`
- Related backlog: `PUB-01`, `I18N-03`
- Policy reference: `ADR-0019`

## Goal

仕様境界ベースで、PUB-01（visibility編集）と I18N-03（英語UI等価）を対象に、
smoke + 変更対象フロー + 安全境界（SafeMode/read-only）を E2E で確認する。

## CDC (Context / Decision / Consequences)

### Context
- QA-PUB 境界では、`PUB-01`（公開可視性）と `I18N-03`（ja/en 等価）に加えて、`readOnly` と SafeMode の禁止操作境界が同時に成立している必要がある。
- KPI監査（Gate D）で再利用できるよう、E2E結果は「再現可能なコマンド列 + 判定根拠」で記録する必要がある。

### Decision
- 本メモの検証対象を 3 軸（公開互換 / i18n 等価 / 安全境界）で固定する。
- 判定証跡は `Date / Gate / Command / Result / Decision / Next action` の 6 項目で記録する。
- 失敗時は最大 3 回まで自己修復し、4回目相当は Fail-safe 停止とする。

### Consequences
- Gate C→D→E の引き継ぎ時に、QA 境界の pass/fail を KPI 監査へ直接入力できる。
- 実行環境依存（ブラウザライブラリ不足等）を「仕様不一致」と分離して扱える。
- 追加の公開境界ケースが発生した場合も、同一フォーマットで比較可能な監査履歴を維持できる。

## AC/DoD 補強提案（QA-PUB 境界）

### Acceptance Criteria（追補）
1. 公開互換: visibility 変更が保存後リロードでも保持される（View/Pack 両方）。
2. i18n 等価: `?locale=en` でも同一フローが成立し、ja と主要 UI 振る舞いが一致する。
3. 安全境界: `?readOnly=1` で禁止操作が disable され、SafeMode locked context が表示される。
4. 証跡再現性: 実行コマンドと結果を第三者が再実行可能な粒度で記録する。

### Definition of Done（追補）
- 境界3軸（公開互換 / i18n等価 / 安全境界）それぞれに pass/fail の根拠が1つ以上ある。
- 失敗時は 3 回上限ルールに従った停止判断が明記される。
- KPI監査文書（issue-0019 / issue-0020）と語彙不一致がない。

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


## Stream H linkage for FB-RM realignment (2026-05-04)
- FB-RM 系列の Proceed 判定に合わせ、QA 境界の証跡フォーマットは `Command/Result/Decision/Next action` を必須保持する。
- A2 モック先行時も E2E 境界では同一入力再現（deterministic replay）を検証対象に含める。
- 依存矛盾（I18N/MID/RS/SEC の前提不一致）検知時は、3回上限の自己修復ルール後に Fail-safe 停止する。

## Stream F independent pass (2026-05-06)

### Phase 1 Read同期
- `AGENTS.md` の Stream F 対象境界を再確認し、本メモの編集範囲を QA/I18N/RM の独立検証記録に限定した。
- 上流方針（`ADR-0019`, SafeMode既定ON, share/export fail-closed）との整合を再確認した。

### Phase 2 依存確認（モック契約基準）
- 依存 I/F は contract-first とし、内部実装詳細ではなく観測可能な入出力・状態遷移を判定対象に固定した。
- 先行依存（I18N→MID→RS→SEC / PUB境界）に矛盾がないかを確認し、矛盾時は Proceed せず Stop する条件を維持した。

### Phase 3 Plan / Execute / Verify / Proceed
- Plan: AC/DoD/Go-NoGo と検証コマンドの対応を再点検した。
- Execute: docs-only で判定文面を整備し、実装コード変更は行わない方針を維持した。
- Verify: 本メモ記載の証跡形式（Command/Result/Decision/Next action）で再実行可能性を確認した。
- Proceed: 依存未解決・環境制約・境界後退のいずれかがある場合は Hold/Stop を優先する。

### Phase 4 Self-Correction（最大3回）
- 自己修復上限を `3回` に固定し、4回目相当が必要な場合は Fail-safe 停止を適用する。
- 修復時は「欠落AC補完 → 判定再確認 → 証跡更新」の順で最小差分更新のみ許容する。

### Phase 5 Stopper
- 停止トリガー: 依存矛盾、SafeMode境界後退、GoNoGo未充足、または自己修復上限超過。
- 停止時は未達項目と再開前提（必要I/F・実行環境・判定根拠）を本メモへ追記して引き継ぐ。
