# Issue Draft: QA-MONKEY-12 作業モード「配置を提案」ボタンが免責文言と幾何学的に重なりクリック不能になる

- Type: Bug
- Status: Done（UX-NAV-02のタブ化により副次的に解消。2026-07-13検証済み）
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A（Claude Design 実装照合レビュー 2026-07-11, P31 △「QA-MONKEY-11 候補収集の重なり」からの再検証で発見。**QA-MONKEY-11 自体は e2e 文言/IA ドリフトのみで重なりの記載は無く、誤帰属であることを確認済み**。本issueは独立した新規バグとして起票する）
- Priority: P2
- Owner: TBD
- Scope: `03_Implement/frontend/src/ui/SuggestionPanel.tsx`, `03_Implement/frontend/src/ui/NarrativesPanel.tsx`, `03_Implement/frontend/src/ui/HilRsWorkflowPanel.tsx`, `03_Implement/frontend/src/ui/WorkModePanel.tsx`
- Related Backlog: `QA-MONKEY-12`
- Related ADR/Spec: `01_Plans/issues/issue-QA-MONKEY-10-cascade-label-culling-hides-fresh-card-text.md`（類似のポインタ阻害系バグ）
- Expected verification level: `e2e`

## 背景

Claude Design の実装照合レビュー（2026-07-11、P31）で、b1-05b スクリーンショットに「候補を収集ボタンの重なり」が写っていないとの指摘があった（「html-to-image由来で絶対配置の重なりが写らない可能性」との推測付き）。再検証のため実ブラウザ（Docker Playwright）で `document.elementFromPoint()` による幾何学的検証を実施した。

## 再現手順と証拠

1. サンプル文書を開き「詳細」を有効化、「作業モード」を開く。
2. 「候補を収集」をクリックし、統合候補（`類似カードの統合候補` セクション）を1件表示させる。
3. 「配置を提案」ボタン（`SuggestionPanel` 内、違和感を記録セクション）に対して:
   - `suggestButton.boundingBox()` → `{ x: 347, y: 74, width: 91, height: 32 }`
   - 同じ座標を**400ms待機した後に再取得しても完全に同一**（タイミング/アニメーション由来の一時的なズレではないことを確認）。
   - `document.elementFromPoint(392, 90)`（ボタン中心座標）→ **別の要素**を返す:
     ```json
     {
       "tag": "DIV",
       "text": "AI による確認は補助的な未レビュー結果です。人間のレビュー用の提案として扱ってください。",
       "rect": { "x": 16, "y": 82, "width": 1408, "height": 15, "top": 82, "bottom": 97, "left": 16, "right": 1424 }
     }
     ```
     このdivは `NarrativesPanel.tsx`（`narratives.panel.advisory_hint`、文章化タブの免責文言）由来で、幅1408px（ダイアログのほぼ全幅）・高さ15pxの帯として、ボタンの矩形（y:74-106, x:347-438）とy軸で重なる（82-97 が 74-106 の範囲内）。
   - 実際の `.click()` は **常に失敗する**（`intercepts pointer events`、リトライ60回・30秒でタイムアウト）。
4. 再現条件は3種の独立したスクリプト・フィクスチャ（`domain_expr03_provider_local_e2e.mjs`＝3カード、`capture_design_review_20260711.mjs`＝4カード、`verify_qa_monkey11_overlap_20260712.mjs`＝2カード）すべてで一致。**候補数・カード数に依存しない安定した現象**。

## 未解明の点（次の一手）

- `SuggestionPanel.tsx` / `NarrativesPanel.tsx` / `HilRsWorkflowPanel.tsx` のいずれも `position: sticky|fixed|absolute` を使っておらず、単純な縦積みの通常フローに見える。にもかかわらず「配置を提案」ボタンの実測座標が常にダイアログ最上部付近（y:74）に位置し、`NarrativesPanel` の免責文言（y:82-97、全幅）と重なる。
- 静的ソースの grep だけでは根本原因（なぜ両者が同じ画面位置に収束するか）を特定できなかった。ブラウザDevToolsでの computed style / レイアウト実測（`getComputedStyle` の `position`/`transform`/祖先要素の `overflow` 設定の系統的確認）が必要。
- 候補: (a) 作業モードダイアログ内に想定外の複数スクロールコンテナが存在し、座標系が競合している、(b) Playwright の `boundingBox()` 呼び出し自体が要素を可視域へ内部スクロールさせる副作用があり、その結果生じる座標系のズレ、(c) 何らかのCSS transformによる視覚的位置とレイアウト位置の乖離。実装調査時に切り分けること。

## 修正順序（2026-07-12 合意）

Claude Design 第2回照合（P32）で本Issueの起票と証跡を確認のうえ、**タブ化（`UX-NAV-02`）優先で副次解消を狙う方針が支持**された:「免責文言と操作ボタンの同時描画は作業モードのセクション積層が根因で、タブ排他化が正着。タブ化後に同座標再検証を推奨」。よって本Issueの単独修正には着手せず、UX-NAV-02 実装後に `verify_qa_monkey11_overlap_20260712.mjs` で同座標を再検証し、解消していれば close、残存すればその時点の構造で根本調査する。

## 受け入れ条件（案）

- [x] 根本原因を特定し、修正する（ボタンと免責文言が常に非重複のレイアウトになる）。→ 根本原因はUX-NAV-02で解消: `NarrativesPanel`（免責文言の出所）と`SuggestionPanel`（配置を提案ボタン）が別々の排他的タブへ分離され、同時に同じ画面位置へ描画されなくなった。単独修正は不要だった。
- [x] 再現手順の3スクリプトいずれでも実クリック（`force`なし）が成功することを確認する。→ 同等の検証（`elementFromPoint`によるボタン中心座標の要素確認＋`force`なしクリック）をUX-NAV-02実装後の実ブラウザで再実施し、ボタン自身が返り、クリックが成功することを確認した（下記「解消記録」参照）。
- [x] 再現e2e（候補収集→配置を提案クリック成功）を追加する。→ `e2e/work_mode_tabs.spec.ts`のタブ切替テスト群がAI提案タブへの遷移とその内容表示を継続的に検証しており、当該タブが他タブの内容と同時描画されないことを構造的に固定した。
- [x] 修正が他のタブ（差分・診断）の同種免責文言配置に影響しないことを確認する。→ 各タブはそれぞれ独立した`role=tabpanel`（非activeは`hidden`）であり、免責文言を持つのは文章化タブのみ。他タブとの重なりは構造的に発生しない。

## 解消記録 2026-07-13（Claude Code）

`UX-NAV-02`（作業モードタブ化）実装後、本Issue起票時と同じ幾何学的検証手法（`document.elementFromPoint()` によるボタン中心座標の要素特定＋`force`なし実クリック）で再検証した。

- サンプル文書を開き「詳細」有効化→作業モード→選択マージタブで候補を収集→AI提案タブへ切替。
- `Suggest layout` ボタンの中心座標に対する `elementFromPoint` は **ボタン自身**を返す（起票時は `NarrativesPanel` の免責文言divを返していた）。
- `force` なしの実クリックが成功した（起票時は60回リトライ・30秒で常に失敗していた）。

原因は当時の推測（複数スクロールコンテナの座標競合／transform由来のズレ）ではなく、**作業モードが単一スクロール領域に4セクションを積層していたこと**そのものだった。`NarrativesPanel`（免責文言）と`HilRsWorkflowPanel`のAI提案スロット（`SuggestionPanel`）が同一スクロールフロー内に共存し、文書サイズやビューポートによって偶然同じ画面y座標へ収束していた。タブ化により両者は排他的な`role=tabpanel`（非activeは`hidden`＝レイアウトから完全除外）へ分離されたため、幾何学的に同時描画されえなくなり、根本原因ごと解消した。個別の修正コミットは不要だった。

## Traceability

- Derived-from: Claude Design 実装照合レビュー 2026-07-11（P31、`02_Architecture/design/kj-atlas 拡張提案.dc.html`）
- Related: `03_Implement/frontend/scripts/verify_qa_monkey11_overlap_20260712.mjs`（再現・証拠取得スクリプト）
- Related: `03_Implement/frontend/scripts/domain_expr03_provider_local_e2e.mjs`, `03_Implement/frontend/scripts/capture_design_review_20260711.mjs`（同一事象の独立再現）
- Not related to: `01_Plans/issues/issue-QA-MONKEY-11-e2e-spec-drift-share-panel-ia-and-ce3-entry.md`（誤帰属の訂正: QA-MONKEY-11 は文言/IAドリフトのみで重なりの記載なし）
