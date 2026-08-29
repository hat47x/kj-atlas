# Issue: UX-PERF-01 初期JavaScript chunkが大きく低速環境の操作開始を遅らせる余地がある

- Type: Performance / UX / Architecture
- Status: Done
- Source Issue: N/A（2026-08-16のUX継続検証におけるproduction build警告）
- Priority: P2
- Owner: Maintainer
- Scope: `03_Implement/frontend/src/App.tsx`, `03_Implement/frontend/src/ui/`, `03_Implement/frontend/vite.config.ts`, frontend performance E2E
- Related ADR/Spec: `01_Plans/adr/ADR-0046-responsiveness-performance-budget.md`, `01_Plans/adr/ADR-0043-complexity-budget-for-cognitive-load.md`
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

- [x] 現行main chunkの上位moduleと操作可能化時間を基準値として記録する。
- [x] 採用する分割境界が初期主要操作を含まず、失敗時に再試行可能である。
- [x] 代表条件で操作可能化時間または初期転送・parse量が改善する。
- [x] keyboard focus、SafeMode、未保存Document、AI proposal-onlyが回帰しない。
- [x] production build、frontend E2E、低速条件の性能probeが成功する。

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

## 対応記録（2026-08-25・AC-2〜3の分割実装、AC-4の回帰検証）

2026-08-21記録の観察（`SharePanel`・`PatchWorkspacePanel`・`InquiryJourneyPrototypePanel`・
`RepresentativeVisualCuePrototypePanel`・`AgentResponseImportPanel`・`DiagnosticsBundlePanel`の6件が
分割候補）を実装した。対応方針3・4を実施し、AC-2・AC-3・AC-4を満たす（詳細は各ACの節を参照）。
AC-1（実端末・低速条件でのTime-to-Interactive計測）とAC-5の「低速条件の性能probe」は依然未着手
のため、両ACともチェックしない。

### 実装

- `App.tsx`の6箇所の静的import（`import { X } from "./ui/X"`）を`React.lazy(() => import("./ui/X").then(m => ({ default: m.X })))`へ変更。コンポーネント本体のみを遅延化し、随伴するtype/value export
  （`DomainExpressionShareSummary`、`ImportedProposalReview`、`boundResolvedAgentImportedProposalReviews`）
  は静的importのまま維持した。
- 新規`03_Implement/frontend/src/ui/LazyPanelBoundary.tsx`: 6箇所で共有する`<Suspense>`+
  再試行付きErrorBoundaryのラッパー。`aria-busy="true"`のloading表示（`LazyPanelFallback`）と、
  chunk読込失敗時に再試行を提示する`LazyPanelErrorBoundary`を持つ。汎用抽象化はせず、この6箇所専用。
- `AgentResponseImportPanel`・`DiagnosticsBundlePanel`（`isOpen`を自身の内部で判定して`null`を返す
  常時マウント型のオーバーレイ）は、`useMountOnceOpened(isOpen)`フックで初回オープンまで
  `LazyPanelBoundary`自体のマウントを遅らせている。理由: このフックなしでは、閉じている間も
  Suspenseの読込フォールバックが初期表示時に一瞬（低速環境では長く）表面化し、かつ
  chunk取得が「開いた時」ではなく「初期表示時」に発生してしまい、対応方針の意図（初期操作に
  不要な機能は明示操作時にのみ読込む）に反する。初回オープン後は従来通りマウントされ続けるため、
  `DiagnosticsBundlePanel`の分類コード・HTTPステータス入力など内部状態のクローズ後保持は変更していない。
  `PatchWorkspacePanel`・`InquiryJourneyPrototypePanel`・`RepresentativeVisualCuePrototypePanel`は
  `WorkModePanel`自身が`isOpen`でchildrenの描画自体を止めているため、追加のガードは不要だった。
- `AgentResponseImportPanel`のみ、追加のリファクタが必要だった:
  `boundResolvedAgentImportedProposalReviews`・`ImportedProposalReview`・`ImportedProposalStatus`を
  `ui/AgentResponseImportPanel.tsx`から`import/agent_response_import.ts`へ移動した。理由:
  `App.tsx`が同一ファイルから値（`boundResolvedAgentImportedProposalReviews`）を静的importし続けると、
  Rollupは「静的importが1本でも到達しているモジュールは、別の場所での動的importと無関係に
  同じchunkへ統合する」ため、`React.lazy()`化してもmain chunkから分離されない
  （`npm run build`自身がこの警告を出した: "AgentResponseImportPanel.tsx is dynamically imported ...
  but also statically imported ... dynamic import will not move module into another chunk"）。
  分離後は独立chunk（5.78KB / gzip 2.00KB）になった。

### AC-2（採用する分割境界が初期主要操作を含まず、失敗時に再試行可能である）— チェック

- 分割境界: 6件はいずれも「カード作成・編集」という初期主要操作の経路上にない
  （`SharePanel`はexport/share、他5件はWork ModeまたはAdvanced UI配下の高度機能）。
  実ブラウザでの新規文書作成・カード追加は本変更と無関係に即時動作することを確認した
  （後述の検証を参照）。
- 失敗時の再試行: 実装当初は「ErrorBoundaryの状態をリセットしてSuspenseに同じ
  `import()`を再試行させる」だけの単純な1段retryだったが、Playwright（実Chromium、
  `vite dev`・productionの`vite preview`両方）でネットワーク層のリクエストを検証した結果、
  **ブラウザのモジュールレジストリは同一URLへの失敗した動的importを永続的にキャッシュし、
  同じ`import()`を再度呼んでもネットワークへの新規リクエストは一切発生しない**ことを実測で確認した
  （`page.route()`でchunkのfetchを1回だけabortし、後で許可に切り替えてから「再試行」を押しても
  リクエスト数が増えないことをrequestイベントで直接カウントして確認）。これはこのissueが名指しする
  「低速回線でのchunk取得失敗」シナリオそのものであり、単純な状態リセットのretryは実質機能しない
  ことが分かったため、2段retryへ変更した:
  1段目（初回失敗時）は状態リセットのみ（モジュールが既に読み込み済みで、失敗原因が
     import()自体ではない一時的なrender例外だった場合はこれで復旧する）。
  2段目（1段目のretryが再び同じ場所で失敗した場合）は`window.confirm()`で確認の上、
     `window.location.reload()`によるページ全体の再読込に切り替える（新しいモジュール
     レジストリで初めて実際に新規fetchが発生する）。confirmを挟むのは、この再読込が
     当該パネルだけでなく文書全体の未保存変更にも影響するため。
  この2段retryを、production build（`vite preview`）に対しPlaywrightで実際に
  「1回目失敗→retryでも同URLは失敗のまま→2段目のconfirm→accept→reload→
  ネットワーク復旧後に実際にパネルが正常表示される」まで一巡させて確認した。

### AC-3（代表条件で操作可能化時間または初期転送・parse量が改善する）— チェック（転送量側のみ）

`npm run build`（`vite v5.4.21`、WSL `~/kjnative-fe`、Node 20、2026-08-21と同条件）:

| ファイル | 変更前（2026-08-21記録） | 変更後 |
|---|---|---|
| main chunk (`dist/assets/index-*.js`) | 1,377.88 KB / gzip 378.13 KB | 1,271.65 KB / gzip 355.68 KB |

差分: raw -106.23KB（-7.7%）、gzip -22.45KB（-5.9%）。分離された6chunk:

| chunk | raw | gzip |
|---|---|---|
| `SharePanel` | 36.57 KB | 7.57 KB |
| `InquiryJourneyPrototypePanel` | 41.66 KB | 10.52 KB |
| `PatchWorkspacePanel` | 13.14 KB | 3.90 KB |
| `RepresentativeVisualCuePrototypePanel` | 8.30 KB | 3.56 KB |
| `DiagnosticsBundlePanel` | 6.87 KB | 2.68 KB |
| `AgentResponseImportPanel` | 5.78 KB | 2.00 KB |

実端末・低速条件での操作可能化時間（AC-1が求めるTime-to-Interactive計測）は今回も未計測のまま
（AC-1は引き続き未チェック）。AC-3は「操作可能化時間または初期転送・parse量」のうち後者のみを、
production build出力の実測比較で満たす。

### AC-4（keyboard focus、SafeMode、未保存Document、AI proposal-onlyが回帰しない）— チェック

- keyboard focus: `SharePanel`（`isOpen`のトグルで自身がopen/close focusを管理）と
  `DiagnosticsBundlePanel`（`useMountOnceOpened`でガードされる側）それぞれについて、
  ad-hoc Playwright specで「openで所定要素にfocus」「closeでtriggerへfocus復帰」を実際の
  ブラウザで確認した（非committed、検証後削除）。既存committed specでも
  `diagnostics_bundle.spec.ts`「Escape closes the panel, returns focus to the trigger」、
  `pre_share_summary_gate.spec.ts`「Back/Escape ... returns focus to the export button」、
  `work_mode_tabs.spec.ts`のstaged Escape focusテストが変更後も成功した。
  **注記**: 手動検証で使ったブラウザツール（Claude Browser pane）は`document.visibilityState`が
  `"hidden"`のままで`requestAnimationFrame`が発火しない環境だったため、rAFに依存する
  focus移動をそのツールだけでは確認できなかった（`SharePanel`・`DiagnosticsBundlePanel`の
  open/close focusはいずれも内部で`requestAnimationFrame`を使う）。これは当該ツールの
  制約であり本変更のバグではないと判断した根拠は、同一シナリオをPlaywright（実Chromium、
  visible pageとして動作）で実行すると期待通りfocusが移動したことで確認した。
- SafeMode: 新規文書作成後、ヘッダーに「セーフモード: ON」、選択パネルに
  「SafeMode ON: 1件の未レビュー項目は共有時に非表示になります」が表示されることを確認した
  （デフォルトON、本変更はSafeModeのロジックに触れていない）。
- 未保存Document: 新規文書作成→カード追加が本変更と無関係に即時動作することを確認した。
  `DiagnosticsBundlePanel`の内部状態（HTTPステータス入力値）がclose→reopenで保持されることを
  ad-hoc Playwright specで確認し、`useMountOnceOpened`導入前の「常時マウント」動作と同等であることを
  検証した。
- AI proposal-only: 本変更はいずれのパネルの内部ロジックも変更していない（読込方式のみ変更）。
  既存の`agent_response_import.spec.ts`のうちバックエンド非依存の1件
  （re-pasting the same response does not create duplicate proposals）は成功した。
  バックエンド依存の2件（audit registration等がバックエンドを要する）は今回の検証環境
  （バックエンド未起動）では変更前・変更後の両方で同一に失敗することを、変更前コードへ
  一時的に戻して同条件で再実行し確認した（本変更による回帰ではない）。

### 検証内容

- WSL `~/kjnative-fe`へ`03_Implement/frontend/src`を同期し、`npm run typecheck`
  （エラー0件）、`npm run test`（vitest全件: 1547 passed / 1 failed / 2 test files failed
  ── 失敗2件は`04_Documentation`・`02_Architecture`をリポジトリルート相対で参照するテストが
  frontendサブツリーのみをコピーした検証環境に存在しないディレクトリを探す既知の環境起因で、
  本変更と無関係。新規追加は`LazyPanelBoundary.test.ts`11件）を実行した。
- `npm run build`成功（上記の表のとおりmain chunk縮小・6chunk分離を確認）。
- Playwright E2E: `work_mode_tabs.spec.ts`・`ce3_patch_workspace.spec.ts`・
  `agent_response_import.spec.ts`・`diagnostics_bundle.spec.ts`・
  `representative_visual_cue_prototype.spec.ts`・`pre_share_summary_gate.spec.ts`・
  `first_value_share_preflight.spec.ts`・`tenant_session_multitab.spec.ts`・
  `inquiry_end_confirmation.spec.ts`ほかを実行。バックエンド未起動環境由来と判断した3件の失敗
  （`agent_response_import.spec.ts`×2、`ce3_patch_workspace.spec.ts`×1）は、変更前コードで同条件
  再実行し同一に失敗することを確認済み。他は全件成功。
- ad-hoc（非committed、検証後削除）Playwright specで、production build（`vite preview`）に対し
  SharePanelのfocus管理、DiagnosticsBundlePanelの状態保持とfocus管理、および2段retryの
  end-to-endフロー（chunk fetch失敗→retry→reload確認→復旧後の正常表示）を確認した。

### 残課題（未着手）

- AC-1: 実端末・低速条件でのTime-to-Interactive基準値計測（引き続き未着手）。
- AC-5の低速条件性能probe: 上記と同様、専用のネットワークthrottling E2E計測機構が未構築。
- `jszip`の主chunk・`bundle_zip.worker`重複、両ロケールJSON常時同梱は2026-08-21記録のまま未着手
  （本対応のscope外）。

## 対応記録（2026-08-26・AC-1のTime-to-Interactive計測とAC-5の低速条件性能probe）

Maintainerの方針判断（2026-08-26）: 測定に使う低速条件は独自プロファイルを作らず、Chrome
DevTools/Lighthouse系ツールが慣用的に使う「slow representative」条件（Fast 3G相当のネットワーク
+ 4倍CPU slowdown）を、既存の名前付き規約から正確な数値を引いて採用する。本記録はこの方針に基づき、
2026-08-21のbundle内訳・2026-08-25の分割実装に続く、AC-1の残り半分（操作可能化時間）とAC-5
（低速条件の性能probe）を満たす。

### 操作可能化（操作可能化時間の定義）

「操作可能化」＝ start panel（`data-panel="start-document-entry"`）の「新規文書を作成」ボタン
（`start_panel.action.new`）が有効化された瞬間、と定義した。`DOMContentLoaded`/`load`ではなくこれを
採るのは以下の理由による。

- `App.tsx`は初回paintから`isStartPanelVisible`を`useState(true)`で無条件に表示するため、
  start panelの存在自体は「hydration完了」を何も意味しない。
- `StartPanel.tsx`は`canCreateNew = !isBusy && !isReadOnly`（`isBusy`は`App.tsx`のmount時
  document読込を追跡する既存の`isLoading`state）が偽の間、当該ボタンを`disabled`にする。つまり
  「ボタンが有効化される」は、本probe用に考案したheuristicではなく、production code自身が既に
  「アプリが起動を終え利用者が作業を開始できる」と定義している既存の状態遷移である。
- 「新規文書を作成」→「最初のカードを書く」の遷移（`handleStartCreateNewDocument` →
  `handleNewDocument`）はネットワークを伴わないローカル状態遷移であり、
  `empty_canvas_onboarding.spec.ts`が既に固定している導線と同じである。新規spec自身も、計測対象
  の5試行に加えて非計測の1回、実際にこの導線を最後までクリックしてカード作成に到達することを
  確認し、「ボタンが有効」が見た目のattributeだけでなく実際の操作可能性と一致することを検証する。

### 低速条件プロファイル（引用元付き）

Chrome DevTools frontendの"Fast 3G"プリセット（`ChromeDevTools/devtools-frontend`、
`front_end/core/sdk/NetworkManager.ts`、内部識別子は`Slow4GConditions`だが`i18nTitleKey`は
`UIStrings.fastG`——DevTools Network conditionsパネルの表示名は"Fast 3G"）と、Lighthouseの既定
mobile throttling定数（`GoogleChrome/lighthouse`、`lighthouse-core/config/constants.js`の
`throttling.mobile3G`、`DEVTOOLS_RTT_ADJUSTMENT_FACTOR=3.75`・`DEVTOOLS_THROUGHPUT_ADJUSTMENT_FACTOR=0.9`）
は同一の数値規約であり、CPU throttling倍率（`cpuSlowdownMultiplier: 4`）もLighthouse側で定義される。
両ソースをGitHub上のファイルから直接確認し、次の値をCDP経由で適用した（
`03_Implement/frontend/e2e/ux_perf_01_time_to_interactive.spec.ts`のファイル冒頭コメントに同じ引用を記載）。

| パラメータ | 値 | 由来 |
|---|---|---|
| `Network.emulateNetworkConditions` latency | 562.5ms | `150ms RTT * 3.75`（DEVTOOLS_RTT_ADJUSTMENT_FACTOR） |
| downloadThroughput | 180,000 B/s（≈1.44Mbps） | `1.6Mbps * 0.9`（DEVTOOLS_THROUGHPUT_ADJUSTMENT_FACTOR） |
| uploadThroughput | 84,375 B/s（≈0.675Mbps） | `750Kbps * 0.9` |
| `Emulation.setCPUThrottlingRate` rate | 4 | Lighthouse `cpuSlowdownMultiplier` |

DevToolsの標準的な運用（throttling＋cache無効化を対にする）に合わせ、各試行は`Network.setCacheDisabled`
で新規contextを都度生成し、初回アクセス相当（cold visit）を再現した。

### 計測結果（production build、`vite build` → `vite preview`、N=5試行の中央値）

`03_Implement/frontend/e2e/ux_perf_01_time_to_interactive.spec.ts`を新規に追加し、
`npm run e2e:prod-tti`（`vite build && playwright test --config=playwright.prod-tti.config.ts`）
で計測した。WSL native環境（`~/kjnative-fe-uxperf01`、Node 20、`vite v5.4.21`）、開発機1台での実行。

| 実行 | 通常条件（中央値、5試行） | 低速条件（中央値、5試行） | 低速/通常 比率 |
|---|---|---|---|
| 1回目 | 763.3ms（範囲746.1–1107.9） | 6566.7ms（範囲6216.2–6991.3） | 約8.6倍 |
| 2回目 | 872.7ms（範囲714.9–1009.2） | 6646.9ms（範囲6217.0–6773.1） | 約7.6倍 |
| 3回目（`npm run e2e:prod-tti`本番導線） | 831.3ms（範囲679.7–992.2） | 7035.0ms（範囲6587.1–7155.0） | 約8.5倍 |

3回の独立実行を通じて、通常条件は概ね700–1100ms、低速条件は概ね6200–7200msに収まり、試行間で
桁が変わるような不安定さは見られなかった（安定した再現性ありと判断）。この数値はこの計測を行った
開発機のハードウェア・負荷状況に依存する相対値であり、絶対値そのものを他機種の基準にはできない
——bundle内訳（2026-08-21記録）や分割前後の転送量比較（2026-08-25記録）と同様、この記録もAC-1の
「基準値」であって性能目標値ではない。

### AC-1（現行main chunkの上位moduleと操作可能化時間を基準値として記録する）— チェック

上位moduleは2026-08-21記録で既に確定済み。操作可能化時間は本記録の上表で確定した。両者が揃ったため
AC-1のチェックを付ける。

### AC-5（production build、frontend E2E、低速条件の性能probeが成功する）— チェック（regression probeの設計に限界あり、詳細は次項）

- production build: `npm run build`成功（main chunk 1,271.65KB / gzip 355.68KB、2026-08-25記録と同値、
  本対応でproduction codeは変更していないため変化なし）。
- frontend E2E: 既定並列度で全224件実行し、198 passed / 11 skipped / 15 failed。失敗15件のうち13件は
  既知（`agent_response_import.spec.ts`×2・`agent_task_export.spec.ts`×1・`ce3_patch_workspace.spec.ts`×1・
  `diagnostics_structural_metrics.spec.ts`×1・`first_meaningful_map_mouse_flow.spec.ts`×2・
  `large_document_operability.spec.ts`×1・`public_pack_visibility_compat.spec.ts`×2・
  `representative_visual_cue_capacity_budget.spec.ts`×1・`document-title-editor.spec.ts`×2、いずれも
  `agent_failure_log.md`および関連done issueに記録済み）。残り2件（`a11y_axe_smoke.spec.ts`・
  `inquiry_bundle_capacity_budget.spec.ts`）は本対応で新たに観測したが、`--workers=1`での単独再実行で
  11件全件成功したことから並列CPU競合による単発flakeと判断した（詳細は`agent_failure_log.md`
  2026-08-26記録）。本対応のdiffはe2e spec 1本の追加とconfig 2件への`testMatch`/`testIgnore`追加のみ
  （production codeへの変更なし）であり、これら15件のいずれとも無関係。
- 低速条件の性能probe: `ux_perf_01_time_to_interactive.spec.ts`自体がこの低速条件probeであり、
  3回の独立実行すべてで成功（1 passed）した。

**regression probeとしての限界（誠実な明記）**: このspecは測定結果をtestInfo.attach/console.infoで
記録し、`throttledMedianMs < 45,000ms`という破局的regression（アプリがinteractiveに到達せず
hangする等）だけを検知する健全性チェックのみ持つ。**通常条件・低速条件どちらについても、
「この値を超えたら性能regression」という具体的な閾値assertionは持たない。** これは見落としではなく、
意図的な判断である。AC-1の操作可能化時間はこのチェックポイントまで一度も計測されていなかったため、
過去の基準値と比較できる履歴データが存在しない。履歴なしに閾値を決めると、緩すぎて何も検知しない
か、厳しすぎて通常の実行時ばらつきでCIが不安定になるかのいずれかになり、どちらも「数値の体裁をした
当てずっぽう」に過ぎない。2026-08-21記録がAC-1を「半分のみ達成」として誠実にチェックを見送った
方針に合わせ、本probeも「測定はするが、まだ根拠のない具体的regression基準は主張しない」という
判断を明記する。今後、この計測を複数回・複数日にわたって記録し2〜3点の日付付きデータが蓄積された
時点で、人間が実際の基準に基づいた閾値を設定するのが次の適切なステップである。

以上を踏まえ、AC-5自体（「production build、frontend E2E、低速条件の性能probeが成功する」の文字通りの
要求）は3点とも成功しているためチェックを付けるが、regression probeとしての閾値設計には上記の
既知の限界があることをここに明記する。

### 実装

- 新規: `03_Implement/frontend/e2e/ux_perf_01_time_to_interactive.spec.ts`（計測spec本体）。
- 新規: `03_Implement/frontend/playwright.prod-tti.config.ts`（production build = `vite preview`を
  対象とする専用config。baseURL/port 4175、既存の`playwright.config.ts`のdev server用baseURL
  4173・`playwright.saas.config.ts`の4174とは別ポート）。
- 変更: `03_Implement/frontend/package.json`に`e2e:prod-tti`スクリプト
  （`vite build && playwright test --config=playwright.prod-tti.config.ts`）を追加。
- 変更: `03_Implement/frontend/playwright.config.ts`に`testIgnore`で新specを除外
  （このconfigの`vite dev`サーバーは単一chunkにbundleしないため、対象を誤ると無関係な計測に
  なるうえ、既定の`npm run e2e`の実行時間を不必要に伸ばす）。
- production codeへの変更なし（本対応は計測のみで、6分割済みpanelの実装・`LazyPanelBoundary`には
  一切触れていない）。

### 検証内容

- WSL native環境（このissue用に新規作成した`~/kjnative-fe-uxperf01`。並行して別セッションが使用中
  の既存`~/kjnative-fe`とは衝突を避けるため分離した）へ`03_Implement/frontend`を同期し、
  `npm run typecheck`（エラー0件）、`npm run test`（vitest: 1547 passed / 1 failed / 2 test files
  failed——2026-08-25記録と同一の既知環境要因、本対応と無関係）を実行した。
- `npm run build`成功。
- `npm run e2e:prod-tti`を3回独立実行し、全て成功、数値も安定（上表参照）。
- `npx playwright test --list`で、既定`playwright.config.ts`が新specを含まないこと（224件のまま）、
  `playwright.prod-tti.config.ts`が新specのみを対象とすること（1件）を確認した。
- 既定configでのfrontend E2E全件実行（`npx playwright test`）。結果と既知/新規失敗の切り分けは
  上記AC-5節を参照。
- `python 01_Plans/docs_check.py`成功（`docs-check passed: active_memos=48, tracked_markdown=679`）。
  WSL側のgit worktreeポインタ形式の制約（`agent_failure_log.md` 2026-08-22記録）を踏まえ、
  worktree全体を使い捨てのWSL scratchディレクトリへrsyncし、そこで`git init`した独立repoに対して
  実行した（本worktree自身の`.git`には触れていない）。

### 残課題

なし。AC-1〜AC-5のすべてを満たしたため、本issueのStatusを`Done`とする。`jszip`の主chunk・
`bundle_zip.worker`重複、両ロケールJSON常時同梱の2件（2026-08-21記録の観察）は本issueの対応方針が
挙げた分割候補の範囲外の追加最適化であり、着手しない（対応方針3の「初期操作に不要な高度機能」には
該当しない実装都合の重複であり、必要であれば別issueとして起票する）。regression probeの閾値未設定
（上記AC-5節）は、履歴データが蓄積された時点で別途対応する将来課題として記録するに留める。
