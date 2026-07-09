# Issue Draft: PERF-BUDGET-01 代表規模の応答性E2E

- Type: Quality / E2E
- Status: Done
- Completion: 2026-07-10; `responsiveness_performance_budget.spec.ts` passed in 10.8s with backend-backed initial document loading.
- Evidence: document replacement, search/filter, card selection, View panel opening, Share panel opening, and long-task budget all remain within the representative thresholds.
- Note: the related four-spec regression run initially reached 10/11 because of an independent stale `Critique:` assertion; the test drift is tracked in `01_Plans/issues/issue-DX-E2E-04-critique-label-assertion-drift.md` and is not a performance failure.
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P1
- Owner: Codex
- Scope: `03_Implement/frontend/e2e/responsiveness_performance_budget.spec.ts`, `01_Plans/adr/ADR-0046-responsiveness-performance-budget.md`, `02_Architecture/value_traceability.md`
- Related Backlog: `PERF-BUDGET-01`
- Related ADR/Spec: `01_Plans/adr/ADR-0046-responsiveness-performance-budget.md`, `01_Plans/adr/ADR-0043-complexity-budget-for-cognitive-load.md`, `01_Plans/issues/issue-PRODUCT-UX-04-responsive-large-document-operability.md`
- Expected verification level: `e2e`

## 1) 課題 / Problem statement

`ADR-0046` は、思考を中断させないための応答性予算として PB-1〜PB-5 を固定している。一方、代表規模（カード約300・島約30）で、主要操作の劣化を検知する最小E2Eが未整備だった。

このままでは、機能追加に伴う検索、選択、パネル表示、共有前確認の静かな遅延を、リリース前に検知しにくい。

## 2) 背景 / Context

- `ADR-0046` は `PERF-BUDGET-01` を性能アサーション追加issue候補として明記している。
- `large_document_operability.spec.ts` は大規模文書の見切れやexport可否を確認するが、代表規模の操作時間アサーションは持たない。
- 個人OSS段階では厳密なSLAではなく、劣化検知用の余裕ある閾値を置く。

## 3) 受入条件 / Acceptance criteria

- [x] カード約300・島約30の代表fixtureでPlaywright E2Eを実行できる。
- [x] 文書読み込み、検索/絞り込み、カード選択、表示パネル、共有前確認の主要操作に上限時間を置く。
- [x] 長時間のメインスレッド停止が発生した場合に検知できる補助観測を置く。
- [x] 性能予算は厳密SLAではなく、劣化検知のための目安であることを明記する。

## 4) 検証計画 / Validation plan

- `cd 03_Implement/frontend && node .\node_modules\@playwright\test\cli.js test e2e/responsiveness_performance_budget.spec.ts --reporter=line`
- `cd 03_Implement/frontend && node .\node_modules\@playwright\test\cli.js test e2e/complexity_budget_foregrounding.spec.ts e2e/domain_expression_keyboard_access.spec.ts e2e/review_pack_trace_export.spec.ts e2e/responsiveness_performance_budget.spec.ts --reporter=line`
- `cd 03_Implement/frontend && node .\node_modules\typescript\bin\tsc --noEmit`

## 5) リスクとロールバック / Risks & rollback

- 失敗モード: CI環境差で時間アサーションが揺れる。
- 緩和: 閾値は厳しすぎない値にし、失敗時は具体操作ラベルを見て再測定する。
- ロールバック: E2Eを一時的に `PRODUCT-QA-01` の手動性能観点へ戻し、閾値またはfixtureを再調整する。

## 実装記録 2026-06-29

- `responsiveness_performance_budget.spec.ts` を追加し、代表規模fixture（300 cards / 30 islands / 299 edges）で次を検証する。
  - document replace
  - search + hide non-matches
  - selected-card context rendering
  - View panel opening
  - Share & Reproduce panel opening
- `PerformanceObserver` の `longtask` を補助観測し、ブラウザが対応する場合は極端な停止を検出する。
- 性能予算: 代表規模での主要操作=劣化検知E2Eを追加 / メインスレッド100ms超の同期処理=新規追加なし（E2Eは利用者操作の観測のみ）

## E2E実行記録 2026-06-29

- 委任元: 利用者指示「Playwright E2E 実行（PERF-BUDGET-01, DOMAIN-EXPR-03/04）」。
- 実行環境: Codex Windows host、Viteを bundled Node.js で `http://127.0.0.1:4173` に起動。
- 実行コマンド:
  - `node .\node_modules\@playwright\test\cli.js test e2e/first_meaningful_map_mouse_flow.spec.ts e2e/first_value_share_preflight.spec.ts e2e/domain_expression_keyboard_access.spec.ts e2e/review_pack_trace_export.spec.ts e2e/complexity_budget_foregrounding.spec.ts e2e/responsiveness_performance_budget.spec.ts --reporter=line`
- 結果: **10 passed**。
- PERF-BUDGET-01対象: `responsiveness_performance_budget.spec.ts` が代表規模fixtureで replace / search-filter / card-selection / View panel / Share panel の上限時間を満たした。
- 判定: **Go for lightweight regression budget**。これは厳密SLAではなく、`ADR-0046` の劣化検知予算として扱う。

## Authoring Checklist（人間/生成AI 共通）

- [x] `Source Issue` が運用状態と整合している。
- [x] `Related ADR/Spec` が最低1件ある。
- [x] 受入条件に「安全」「互換」「検証」が含まれる。
- [x] `Validation plan` に具体コマンドがある。
- [x] 非目標が明記されスコープ逸脱を防いでいる。
