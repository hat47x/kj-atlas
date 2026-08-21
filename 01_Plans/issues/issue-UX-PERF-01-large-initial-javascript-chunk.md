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

## 対応記録（2026-08-21・AC-1の一部: bundle内訳の基準値）

AC-1は「上位moduleと操作可能化時間」を1項目として要求しているが、**bundle内訳（上位module）のみ**を
本記録で満たす。**操作可能化時間（実端末・低速条件でのnavigationから主要操作可能までの計測）は
未実施のまま残す**——既存のE2Eには対応するTime-to-Interactive計測spec（`inquiry_bundle_capacity_budget.spec.ts`
はimport/serialize/parseの処理時間を計測するが、ページ読込自体の計測ではない）が無く、新規に
ネットワークthrottling・複数試行・中央値比較を備えたE2E specを書く必要があるため、本記録の範囲外とする。
AC-1のチェックは付けない（半分のみ達成のため）。

**計測条件**: `npm run build`（`vite v5.4.21`、native WSL環境、`.nvmrc`のNode 20）。
`npx vite-bundle-visualizer`（ad-hoc実行・`package.json`へ追加せず一時利用のみ）でmodule単位の
render前サイズを取得。

**production build出力（変更なし・現状確認）**:

| ファイル | サイズ | gzip |
|---|---|---|
| `dist/assets/index-*.js`（main chunk） | 1,377.88 KB | 378.13 KB |
| `dist/assets/bundle_zip.worker-*.js` | 98.20 KB | — |
| `dist/assets/inquiry_bundle.worker-*.js` | 55.81 KB | — |
| `dist/assets/diagnostics.worker-*.js` | 30.04 KB | — |
| `dist/assets/trace.worker-*.js` | 7.37 KB | — |
| `dist/assets/diff.worker-*.js` | 2.96 KB | — |

500KB警告は継続（issue記載の約1,366KBから約1,378KBへ、issue起票後の開発により微増）。

**main chunk内のmodule別サイズ上位（bundle-visualizer render前サイズ・gzip概算付き、上位20）**:

| render前バイト | gzip概算 | module |
|---|---|---|
| 428,659 | 71,304 | `/src/App.tsx` |
| 228,541 | 27,236 | `/src/ui/SidePanel.tsx` |
| 154,727 | 36,595 | `/src/i18n/locales/ja.json` |
| 133,960 | 31,608 | `/src/i18n/locales/en.json` |
| 133,297 | 42,391 | `react-dom`（vendor） |
| 97,688 | 28,491 | `jszip`（vendor。**`bundle_zip.worker`にも別途同梱されており重複**） |
| 74,934 | 9,384 | `/src/ui/SharePanel.tsx` |
| 44,938 | 6,624 | `/src/domain/validate_doc.ts` |
| 44,571 | 7,101 | `/src/ui/InquiryJourneyPrototypePanel.tsx` |
| 43,599 | 8,668 | `/src/canvas/CanvasShell.tsx` |
| 37,766 | 4,567 | `/src/ui/ViewControlsPanel.tsx` |
| 29,501 | 5,633 | `/src/domain/validate.ts` |
| 24,727 | 4,111 | `/src/api/client.ts` |
| 24,356 | 4,305 | `/src/canvas/IslandView.tsx` |
| 23,069 | 4,010 | `/src/ui/NarrativesPanel.tsx` |
| 21,003 | 3,329 | `/src/export/view_metadata.ts` |
| 20,545 | 4,775 | `/src/domain/representative_visual_cue_assets.ts` |
| 18,446 | 3,865 | `/src/domain/inquiry_bundle_safe_mode.ts` |
| 18,232 | 4,514 | `/src/canvas/CardView.tsx` |
| 17,804 | 3,687 | `/src/ui/workspace/PatchWorkspacePanel.tsx` |

**カテゴリ別集計**（render前バイト、全261 module合計2,425,119バイトに対する内訳）:
- `node_modules`（vendor）: 245,108バイト（10.1%）
- `src/`（自社コード）: 2,178,145バイト（89.8%） — **主要因は vendor ではなく自社コード**
- `i18n/locales/*.json`（両ロケール分を常に同梱）: 288,687バイト（11.9%）

**観察（判断は行わない・以降の方針決定はMaintainer）**:
- 上位2件（`App.tsx`・`SidePanel.tsx`）は初期主要操作（カード作成・編集）に直結する可能性が高く、
  対応方針3が言う「初期操作に不要な高度機能」の分割候補としては**適さない可能性がある**——実際に
  どのuseState/handlerが初期表示に必須かは、この measurement だけでは判別できない。
- `SharePanel.tsx`・`InquiryJourneyPrototypePanel.tsx`・`PatchWorkspacePanel.tsx`は、issueが対応方針3で
  例示する「export/import、agent、作業モード等」の高度機能に名称が一致し、分割候補として測定上も上位に
  来ている。同様に上位20には`RepresentativeVisualCuePrototypePanel`・`DiagnosticsBundlePanel`・
  `AgentResponseImportPanel`（20位以下）も含まれる。
- `jszip`が主chunkと`bundle_zip.worker`の両方に同梱され重複している可能性がある（メインスレッド側の
  `jszip`利用箇所を特定すればworkerへ一本化できる余地）。
- 両ロケールのJSON（計288KB、gzip概算68KB）が常に同梱される。動的import化すれば、利用中でない
  ロケール分（片方）は初期転送から除外できる可能性がある。

**次のステップ（未着手）**: 実端末・低速条件でのTime-to-Interactive基準値計測（AC-1残り）、および
上記観察を踏まえた分割境界の評価と決定（対応方針3・4、AC-2〜5）。いずれもMaintainerの方針判断を要する。
