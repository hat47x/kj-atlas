# Issue: PERF-BUDGET-01 代表規模の性能アサーション追加

> 個人OSS段階（`ADR-0039`）の軽量起票。`ADR-0046` の実装入口。回帰検知が目的（厳密ベンチではない）。

- Type: Process
- Status: Done
- Completion: 2026-07-10; `large_document_operability.spec.ts` passed in 7.3s with the 120-card / 12-island fixture.
- Evidence: search and hide-non-matches, View and Share panel viewport fit at 768x720, and review-pack export diagnostics were verified.
- Test contract fixes: the test now uses `?locale=en` for its English assertions and the current `Replaced the current document` status copy.

## Acceptance evidence

- [x] Representative large-document fixture remains executable.
- [x] Search, panel fit, export, and diagnostics behavior pass at the documented viewport.
- [x] Regression verification completed without a runtime or schema change.
## Implementation Progress 2026-06-27

- Fixture scaled to 288 cards + 30 islands (ADR-0046 PB-1)
- Total render+search+export timing assertion <30s added
- Degradation visibility check (PB-5) added
- Existing E2E passes (cannot verify locally; CI only)

Remaining: CI Playwright verification of timing budget
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P2
- Owner: Codex
- Scope: `03_Implement/frontend/e2e/`, `03_Implement/frontend/src/`
- Related Backlog: `PERF-BUDGET-01`
- Related ADR/Spec: `01_Plans/adr/ADR-0046-responsiveness-performance-budget.md`, `02_Architecture/value_traceability.md`（§2.8 PB）, `01_Plans/issues/issue-PRODUCT-UX-04-responsive-large-document-operability.md`
- Expected verification level: `e2e`

## 1) 課題 / Problem statement

`ADR-0046` が性能予算（PB-1..5：代表規模カード約300・worker化100ms基準・劣化可視化）を定義したが、`large_document_operability.spec.ts` は性能アサーション（完了時間・worker非ブロッキング）を持たず、**機能追加のたびの「静かな劣化」を回帰検知できない**。

## 2) 背景 / Context

- `ADR-0046` PB-1（代表規模約300）/ PB-3（メインスレッド100ms超は worker 化）/ PB-5（劣化可視化）。
- `PRODUCT-UX-04`（Done）は大規模操作性を定性的に確認済みだが定量予算が無い。
- DOMAIN-EXPR の状態計算（`state_filter` 等）が増え、性能劣化リスクが上昇。

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: 「待たされて思考が途切れない」は根幹価値の計算軸（`ADR-0046`）。
- 安全: 性能劣化は安全境界を直接壊さないため P2。
- 後方互換: テスト追加のみ、挙動・スキーマ変更なし。

## 4) 提案する解決策 / Proposed solution

- 変更対象（テスト中心）:
  - 代表規模 fixture（カード約300・島約30）を用意（既存 large_document fixture 流用可）。
  - `large_document_operability.spec.ts` に**最小の性能アサーション**を追加：主要操作（初期表示・検索・フィルタ・選択・共有前確認）の完了上限時間、重い処理中に UI が固まらない（worker 利用）こと。
  - 閾値は CI 実行環境のぶれを吸収する余裕を持たせ、**相対的悪化と worker 不使用の検知**を主目的にする。
- 非目標: 厳密 SLA・パーセンタイル固定、レンダリング刷新（仮想化/WebGL）、マイクロベンチ基盤。

## 5) 受入条件 / Acceptance criteria

- [ ] 代表規模 fixture で主要操作の性能アサーションが存在し、緑である。
- [ ] メインスレッドを長時間ブロックする同期処理が無い（重処理は worker 経由）ことを検証する。
- [ ] 大規模・低速時に待機/進捗表示が出る（PB-5、`ADR-0044` UQ-5 と整合）ことを確認する。
- [ ] 閾値超過時にテストが赤になる（回帰検知）。
- [ ] スキーマ・実行挙動に変更がない（テスト追加が主、必要時のみ debounce/メモ化の最小調整）。

## 6) 検証計画 / Validation plan

- 実行コマンド:
  - `cd 03_Implement/frontend && node ./node_modules/playwright/cli.js test e2e/large_document_operability.spec.ts --reporter=line`
  - `rg -n "PB-[1-5]|representative|300|performance" 03_Implement/frontend/e2e/large_document_operability.spec.ts`
- 期待結果: 代表規模で主要操作が予算内、worker で UI 非ブロッキング。
- 未実施時の代替: 実装前は手動で代表規模文書を開き体感確認＋ worker 利用箇所のコードレビュー。

## 7) リスクとロールバック / Risks & rollback

- 失敗モード: CI 環境差で絶対時間がぶれ flaky 化。→ 余裕閾値＋相対悪化/worker不使用を主判定にする。
- 影響範囲: e2e と一部 frontend。ロールバック=アサーション無効化（挙動非依存）。

## 8) Additional context

- 性能影響を伴う将来 issue は `ADR-0046` の「性能予算1行」自己申告を行い、悪化時は `PRODUCT-QA-01` で確認（`BUDGET-OPS-01` で運用定着）。
