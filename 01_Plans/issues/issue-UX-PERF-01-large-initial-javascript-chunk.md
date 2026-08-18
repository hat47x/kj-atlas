# Issue: UX-PERF-01 初期JavaScript chunkが大きく低速環境の操作開始を遅らせる余地がある

- Type: Performance / UX / Architecture
- Status: Open
- Source Issue: N/A（2026-08-16のUX継続検証におけるproduction build警告）
- Priority: P2
- Owner: Maintainer
- Scope: `03_Implement/frontend/src/App.tsx`, `03_Implement/frontend/src/ui/`, `03_Implement/frontend/vite.config.ts`, frontend performance E2E
- Related ADR/Spec: `01_Plans/adr/ADR-0046-performance-budget-and-responsive-interaction.md`, `01_Plans/adr/ADR-0043-ui-complexity-budget.md`
- Expected verification level: `e2e`

## 課題

現行production buildはmain JavaScriptを約1,366KB（gzip約377KB）の単一chunkとして生成し、Viteの500KB警告を継続している。機能上の失敗ではないが、低速回線・低性能端末では初期parse/evaluateと操作可能化を遅らせる可能性がある。現時点では実端末の操作可能化時間、chunk内訳、遅延読込可能な機能境界が測定されていないため、警告閾値を上げて隠す判断はできない。

## 対応方針

1. 代表端末条件と低速条件で、navigationから主要操作可能までを計測する。
2. bundle analyzerでmain chunkの上位moduleを特定する。
3. 初期操作に不要な高度機能（export/import、diagnostics、agent、作業モード等）を候補として、dynamic import境界を1つずつ評価する。
4. loading表示、keyboard focus、失敗時retryを含むUXを保った分割だけを採用する。

三要素牽制: 業務上はカード作成・編集・整理を最短で開始できる必要がある。データ上は遅延読込がDocument、SafeMode、未保存状態を変えてはならない。機能上は初期主要操作をmain chunkへ残し、高度機能を明示操作時に読込む。単なる閾値緩和や一括vendor分割は測定なしで実施しない。

## 受入条件

- [ ] 現行main chunkの上位moduleと操作可能化時間を基準値として記録する。
- [ ] 採用する分割境界が初期主要操作を含まず、失敗時に再試行可能である。
- [ ] 代表条件で操作可能化時間または初期転送・parse量が改善する。
- [ ] keyboard focus、SafeMode、未保存Document、AI proposal-onlyが回帰しない。
- [ ] production build、frontend E2E、低速条件の性能probeが成功する。

## 検証計画

- production buildのchunk size比較とbundle内訳を保存する。
- 実Chromiumで通常条件・低速条件を複数回測定し中央値を比較する。
- 初期主要操作と遅延対象機能のkeyboard/失敗時回帰をE2Eで固定する。
