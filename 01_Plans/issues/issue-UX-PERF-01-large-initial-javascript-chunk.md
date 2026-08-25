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
- [x] 採用する分割境界が初期主要操作を含まず、失敗時に再試行可能である。
- [x] 代表条件で操作可能化時間または初期転送・parse量が改善する。
- [x] keyboard focus、SafeMode、未保存Document、AI proposal-onlyが回帰しない。
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
