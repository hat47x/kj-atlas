# Issue Draft: UX-SCALE-01 スケール操作の拡充（ミニマップ・一括操作・島の直交描線・関係線エスカレーション）

- Type: Feature request
- Status: Done
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P3
- Owner: Claude Code
- Scope: `03_Implement/frontend/src/canvas/`, `03_Implement/frontend/src/domain/`, `03_Implement/frontend/e2e/`
- Related Backlog: `UX-SCALE-01`
- Related ADR/Spec: `01_Plans/adr/ADR-0048-visual-language-command-reach-and-kj-vocabulary.md`（D1/D3）, `01_Plans/adr/ADR-0046-responsiveness-performance-budget.md`（PB-1..5）, `01_Plans/issues/issue-PERF-BUDGET-01-large-document-performance-assertions.md`（In Progress・性能検証の正本）
- Expected verification level: `e2e`

## Requirement meta I/F（共通キー）

- RequirementID: UX-SCALE-01
- RequirementStatement: 大規模文書（PB-1: 約300カード/30島）での見通しと操作を、(a) ミニマップ、(b) 複数選択の一括操作バー、(c) 島の直交描線（矩形/L字/コの字）＋複雑さ表示＋可逆な「整える」、(d) ズーム連動の関係線エスカレーション、で拡充する。いずれも既存 LOD・構造レベル・読み順可視化（実装済み）を再決定せず拡張する。
- PriorityClass（Must / Should / Could）: Could
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=300カード/30島規模のフィクスチャ / 操作=縮小して俯瞰→ミニマップでビュー移動→複数選択して一括保留→島の「整える」→ズームアウト / 期待結果=現在ビューがミニマップに表示され移動できる。一括操作が1回の取り消しで戻る。島は凸空白を含まない直交描線になり複雑さが表札に出る。省略カードの関係線は同島内=内部化・異島間=表札へ昇格 / 除外=WebGL 化・仮想化等のレンダリング刷新（ADR-0046 非目標）、LOD 閾値の再設計。
- GoNoGoGate（Required / Optional / N/A）: Optional
- SecurityGateImpact: N/A
- VerificationLevel: e2e
- DecisionStatus（Fixed / Pending）: Fixed（ADR-0048。ただし着手は段階1/2 issue 完了後）
- DecisionQueueRef: `ADR-0048`

## 1) 課題 / Problem statement

- LOD・構造レベル・読み順は実装済みだが、規模拡大時の (a) 全体ナビ手段が無い、(b) 多数選択後の操作が個別で重い、(c) 島の外接矩形が空白の角を含み面積過大＝散らかりの原因が見えない、(d) 縮小時にカードが省略されると関係線の扱いが未定義、という残課題がある。
- 配置の散らかりを「点数」でなく**描線複雑さ（凹み角数）のサイン**として可視化し、可逆な「整える」候補で応える設計（反スコアリング整合）が壁打ちで確立した。

## 2) 背景 / Context

- 壁打ち成果（拡張提案 観点2・図R/S/T・複雑さメトリクス・エスカレーション規則）がプロトタイプ検証済み: 直交単純多角形の複雑さ=(頂点数−4)/2、JOIN/LEAVE 二重閾値、同島内関係の内部化・異島間の表札昇格。
- 性能の正本は ADR-0046（PB-4 対話操作の即時感）と PERF-BUDGET-01（In Progress）。本Issueは性能検証を重複させず、PB 準拠を宣言して同フィクスチャに乗る。

## 3) 判断基準による優先度評価

- 価値（ADR-0001 P-06）: 俯瞰↔詳細の視点制御の完成形。俯瞰でも保留・違和感・規模（N枚）を落とさない（全体性の保持）。
- 安全: N/A（表示・整列のみ。整列は自動実行せず人間起動・可逆）。
- 規模拡大: 本Issueがスケール UX の中核。ただし基盤（視覚言語・入力体系）完了後の段階3。
- 後方互換: スキーマ変更なし（描線・ナビ・一括操作は表示/操作層）。

## 3.2 非目標 / Non-goals

- レンダリング刷新（仮想化・WebGL）。LOD 閾値・構造レベルの再設計。自動整列の既定化（提案・人間起動・可逆に限る）。関係記号の種別追加（DOMAIN-KJ-01 の領分）。

## 4) 提案する解決策 / Proposed solution

- (a) **ミニマップ**: 隅に小型・控えめ表示（既定表示は要 CB-1 宣言。折りたたみ可）。現在ビュー枠のドラッグで移動。
- (b) **一括操作バー**: 複数選択時のみ出現（島に束ねる・一括保留/違和感・一括型変更・削除）。1操作=履歴1ステップで取消可能。保持系を左端（最上位）に配置。
- (c) **島の直交描線**: メンバー矩形のグリッド占有から縦横線のみのポリゴンを生成（≤2枚は丸角矩形）。複雑さ（凹み角数）を表札に小さく表示し、「整える」（右クリック/⌘K から人間起動・⌘Z で一括取消）で密なグリッドへ再配置。点数化しない（見直しのサインに留める）。
- (d) **関係線エスカレーション**: 鳥瞰でカードが表札チップに省略された際、同一島内に両端が集約された関係=非表示（内部化）、異なる島/残存カードへの関係=表札へ昇格して描画（昇格線はラベルで区別）。ズーム復帰で可逆。
- すべて PB-4（対話操作の即時感）を満たすこと。劣化時は PB-5 の可視化に従う。

## 5) 受け入れ条件 / Acceptance criteria

- [x] AC-1: ミニマップで現在ビューの把握と移動ができ、折りたたみ状態が保持される（`e2e/minimap.spec.ts`）。
- [x] AC-2: 一括操作（束ねる・保留・型変更）が複数選択時のみ出現し、1回の取り消しで全体が戻る（`e2e/bulk_operations_bar.spec.ts`）。
- [x] AC-3: 島の描線が空白の角を含まない直交ポリゴンで描かれ、複雑さ表示→「整える」→複雑さ低減が e2e で固定される（自動実行しない、`e2e/island_tidy.spec.ts`）。
- [x] AC-4: 鳥瞰時の関係線が内部化/昇格規則どおりに増減し、ズーム復帰で元に戻る（`e2e/edge_escalation.spec.ts`）。
- [x] AC-5: PERF-BUDGET-01 のフィクスチャ上で PB-4 相当の対話性が維持される（同Issueの既存計測ハーネス`e2e/responsiveness_performance_budget.spec.ts`を再利用・重複計測なし。下記完了記録参照）。

## 6) 実装タスク分解 / Task breakdown

- [x] T1 ミニマップ（ビュー枠・折りたたみ・CB-1 宣言）。
- [x] T2 一括操作バー（選択数連動・履歴1ステップ）。
- [x] T3 直交描線ジェネレータ＋複雑さ算出＋「整える」。
- [x] T4 エスカレーション規則（内部化/昇格/ラベル）。
- [x] T5 e2e＋PB 準拠確認。

## 7) 検証計画 / Validation plan

- `cd 03_Implement/frontend && npm run typecheck && npm test && npx playwright test`
- PERF-BUDGET-01 の大規模フィクスチャでの操作スモーク（同Issueのハーネスを利用）。

## 複雑性予算（ADR-0043 自己申告）

複雑性予算: 初期表示への純増=+1（ミニマップ。ただし小型・隅・折りたたみ可。理由=俯瞰ナビは規模拡大時の中核導線） / 保留操作の距離=改善（一括操作バーで複数カードの保留が1操作） / 取り消し導線=あり（一括操作・整えるは1ステップで可逆、エスカレーションはズームで可逆）

## Traceability

- Related: `01_Plans/adr/ADR-0048-visual-language-command-reach-and-kj-vocabulary.md`
- Related: `01_Plans/adr/ADR-0046-responsiveness-performance-budget.md`, `01_Plans/issues/issue-PERF-BUDGET-01-large-document-performance-assertions.md`
- Related: `02_Architecture/design/kj-atlas 拡張提案.dc.html`（観点2・図R/S/T）
- Derived-from: `01_Plans/adr/ADR-0048-visual-language-command-reach-and-kj-vocabulary.md`

## 実装設計の到着（2026-07-04 Round 5）

- レッドライン確定（同 §段階3）: ミニマップ=右下 約160×110 角丸8 半透明・カード4px点（型色）・現ビュー枠青2px・ドラッグ/クリック移動・狭幅自動折畳。一括操作バー=選択時に下中央出現・保持系左端・「n件選択」aria-live（評価語なし）・0件で消滅。エスカレーション昇格ラベル=淡紫で「集約された関係」区別・縮退時は種類を出さず汎用表示。島直交描線・エスカレーションはプロトタイプ実装済み。

## 完了記録（1/4）2026-07-07（Claude Code）— ミニマップ（AC-1・T1）

### 事前調査で判明した既存基盤

実装着手前に `src/domain/geometry/` 以下（凸包・多角形パディング・自己交差検査・頂点編集等）と `src/canvas/` の関連実装を精査した。判明事項:
- 島の境界には**既に**汎用の任意多角形システム（`Island.shape`/`geometry`、`PolygonEditLayer.tsx` によるドラッグ編集、`handleGenerateIslandPolygon` による凸包ベースの自動フィット）が存在するが、**直交（軸並行）ではなく凸多角形**であり、AC-3 の「直交描線」とは別物。複雑さメトリクスは未実装。
- 島↔島の関係線集約（`island_edge_aggregate.ts`）が**既に**同一島内の内部化（黙示的）と異島間の集約・破線表示・ズームでの可逆化を実装済み。AC-4 の残作業は「孤立カード（島に属さないカード）への昇格」のみ。
- ミニマップ・一括操作バーは実装ゼロ（デザイン文書のレッドラインのみ）。
- 詳細は各サブ機能着手時にコードコメントで参照する。

### 実装（ミニマップのみ）

- `src/ui/Minimap.tsx`（新規）: 右下・160×110・角丸8・半透明。カードは型色ドット（`CardView.tsx` の `CLAIM_TYPE_STYLE.fg` と同じ固定色を複製、ADR-0048 D1 準拠で新色は追加せず）。島は淡いアウトライン矩形。現在ビュー枠は青2px、ドラッグで実際のカメラをパン（既存の `requestCameraTransform` に委譲、新規パン/ズームロジックは追加なし）。640px 未満で自動折畳（手動設定より優先）。折畳状態は `src/storage/minimap_collapsed.ts` で永続化。
- App.tsx: `minimapCards`/`minimapIslands`（`getVisibleBoundsExportArea` と同一の可視性フィルタを再利用）と `handleMinimapPan` を追加し、`CanvasLegend` と並置してレンダリング。

### スコープ判断

- **キーボード操作は範囲外**（ポインタ専用）。ミニマップは補助的なナビゲーション導線であり、パン・フィット等の主要操作は既存の他経路（既存のキーボード到達可能な操作群）で引き続き到達可能なため、ADR-0030 D1（主要操作のキーボード到達性）の対象には当たらないと判断。

### 検証

- typecheck 0 / vitest **900 passed**（183 files。UX-SCALE-01 (a) 回帰アンカー1件・ストレージ永続化テスト2件を追加）
- e2e 新規3件 passed: `minimap.spec.ts`（ドラッグでカメラがパンされる／折畳と再展開・リロード後の永続化／640px未満での自動折畳が手動設定より優先）
- 既存の広範な e2e で非回帰確認（`header_toolbar_layout`・`canvas_legend`・`canvas_protection`・`complexity_budget_foregrounding`）

## 完了記録（2/4）2026-07-07（Claude Code）— 関係線エスカレーション完成（AC-4・T4）

### 実装

- `src/domain/island_edge_aggregate.ts`: `getDerivedIslandEdges` を拡張し、既存の島↔島昇格（同一島内=内部化・異島間=集約昇格）に加え、**片方だけが島に属する場合（残存する孤立カードへの関係）を島↔カードとして昇格**するロジックを追加。`DerivedIslandEdge.toKind` を `"island" | "card"` に拡張。ダングリング参照（実在しないカードID）は昇格せず従来どおり無視するガードを追加。
- `src/canvas/CanvasShell.tsx`・`src/domain/geometry/bounds.ts`・`src/export/canvas_svg.ts`: 派生エッジの可視性フィルタが `toId` を常に島IDとして扱っていたバグを修正（`toKind` に応じてカード可視集合も参照するよう分岐）。`src/export/abstract_map_export.ts`（テキスト版アウトライン書き出し）は行フォーマットが島ペア専用のため、カード昇格エッジは明示的にスコープ外として除外。
- **副次的に発見・修正した既存バグ**: `EdgeLayer.tsx` へ渡す `cards` プロパティが `visibleCards`（LOD で圧縮され個別カードが除外された集合）に限定されていたため、多角形未生成の島の中心点フォールバック計算（メンバーカード位置が必要）が鳥瞰時に失敗し、**新規の昇格エッジだけでなく既存実装済みの島↔島エスカレーション自体も鳥瞰時に描画されない状態だった**（デバッグ属性を一時追加し `derived-count: 2` かつ `visible-edges-count: 2` は正しいのに実際のレンダリングが0件になることを直接確認して特定）。修正: `EdgeLayer` へは `document.cards`（全カード）を渡し、実際の表示可否は既存の `hiddenCardIds` フィルタに委譲（多角形を持つ島は元々影響を受けない）。

### 検証

- typecheck 0 / vitest **902 passed**（183 files。`island_edge_aggregate.test.ts` に昇格ケース・孤立カード同士の非昇格ケースを追加）
- e2e 新規2件 passed: `edge_escalation.spec.ts`（同一島内=内部化・異島間=昇格・孤立カードへの昇格が実際の `<line stroke="#0f766e">` として描画されズーム復帰で消えることをDOM直接検証）
- 既存の広範な e2e で非回帰確認（`canvas_legend`・`canvas_protection`・`card_meta_row`・`domain_expression_keyboard_access`・`keyboard_release_candidate_flow`・`hierarchy_level_persistence` 等）

## 完了記録（3/4）2026-07-07（Claude Code）— 一括操作バー（AC-2・T2）

### 実装

- `src/ui/BulkOperationsBar.tsx`（新規）: 選択カード数2件以上でのみ出現する下中央バー。保持系（保留・違和感）を左端に配置し、区切り線の後に型変更（`<select>`・即時適用）・「島に束ねる」・削除を続ける。`role="status" aria-live="polite"` で「{count} 件のカードを選択中」を通知（既存 `side_panel.selection.card_multiple` を再利用、評価語なし）。
- `src/App.tsx`: `handleBulkToggleHold`・`handleBulkToggleCritique`・`handleBulkClaimTypeChange` を新規追加。いずれも選択カード全体をひとつのドキュメント変換として `applyDocumentChange` を**1回だけ**呼ぶ（カードごとのループでヒストリーをN件作らない）。「束ねる」と「削除」は新規ロジックなしで既存の `handleCreateIsland`／`handleDeleteSelection`（いずれも元から選択全体に対応・1ステップ）へ直接委譲。
- 一括保留トグルの意味論（未確立だったため設計判断）: 「全カードが保留中」なら解除、それ以外（混在または全て非保留）なら全て保留、という「一括チェックボックス」方式を採用（単一カードのHキー＝held⇄activeの二値トグルと矛盾しない拡張）。一括違和感トグルは、U キーと**全く同じ**安全なマーカー方式（空→定型文言・定型文言→空・自著テキストは無変更）をカードごとに適用。

### 検証

- typecheck 0 / vitest **903 passed**（183 files。UX-SCALE-01 (b) 回帰アンカー1件追加）
- e2e 新規4件 passed: `bulk_operations_bar.spec.ts`（2件未満では非表示／一括保留とCtrl+Zでの1ステップ取り消し／一括型変更／一括削除と1ステップ取り消し）
- **既存 e2e の非回帰対応**: 新規バーが既存の常時表示ツールバー（`data-ui-core-action="create-island"`）と同じラベル「Create Island」/「島を作成」を持つボタンを追加したため、複数選択時にラベルが重複しアクセシブルネームが曖昧になる既存テスト2件（`first_meaningful_map_mouse_flow.spec.ts`・`first_value_share_preflight.spec.ts`）を `getByRole("banner").getByRole(...)` でヘッダー領域に限定するよう修正（UX-MENU-01 で確立した「移設/追加によりラベル重複が生じた既存テストをスコープ限定で修正する」パターンを踏襲）。
- 既存の広範な e2e で非回帰確認（`complexity_budget_foregrounding`・`review_pack_trace_export`）

## 完了記録（4/4）2026-07-07（Claude Code）— 直交描線・複雑さ・「整える」（AC-3・AC-5・T3・T5）

### 実装

- `src/domain/geometry/orthogonal_island_outline.ts`（新規・純粋関数のみ）:
  - `traceGridBoundary`: 単位グリッドセル集合の輪郭を「辺の相殺法」で抽出（隣接する2セルが共有する辺は互いに逆向きに1回ずつ寄与し相殺、生き残った辺が輪郭）。複数ループが生じた場合（非連結クラスタ）は面積最大のものを外周として採用し、他は破棄する既知の簡略化とした（"整える"を実行すれば単一の密な塊に統合され解消する）。
  - `generateOrthogonalIslandOutline`: メンバーカードの実座標を（カード自身の位置ジッターを許容する）丸め込みでグリッドセルへ割付け、`traceGridBoundary`＋共線点の簡約で軸並行ポリゴンを生成。複雑さ = (頂点数−4)/2（凹み角数、直交単純多角形の一般恒等式）。
  - `computeTidyIslandLayout`: 現在の行優先順を保ったまま、`ceil(sqrt(N))` 列の密な正方形に近いグリッドへ再配置する目標座標を計算（人間起動、自動実行はしない）。
  - 単体テスト13件（矩形/L字/ジッター耐性/軸並行性の不変条件/整える後の複雑さ低減/冪等性/カードID保存）ですべて検証。
- `src/App.tsx`: 島の自動生成（`buildIslandPolygonFromCards`、既存の「多角形を再生成」導線から呼ばれる）を凸包ベースから直交生成へ置換（未使用となった `computeConvexHull`/`padPolygonFromCentroid`/`POLYGON_PADDING` の参照を除去）。手動でのドラッグ編集（`PolygonEditLayer`）は非直交な形状も引き続き作成可能で不変。新規 `handleTidyIsland`（カード再配置とポリゴン再生成を1回の `applyDocumentChange` にまとめ、1操作=1取り消しステップ）を右クリックメニュー「配置を整える」とコマンドパレット（島選択時のみ有効）の両方から起動可能に。
- `src/canvas/IslandView.tsx`: 表札に複雑さバッジを追加（複雑さ>0の時のみ表示＝CB-1。ツールチップに「点数ではなく目安」と明記し反スコアリングを堅持）。

### 検証

- typecheck 0 / vitest **917 passed**（184 files。ジェネレータ専用13件＋UX-SCALE-01 (c) 回帰アンカー1件）
- e2e 新規2件 passed: `island_tidy.spec.ts`（L字島の複雑さ表示→整える→複雑さ0→Ctrl+Zで1ステップ復元、コマンドパレットからの起動）
- 既存の広範な e2e で非回帰確認（`command_palette`・`polygon_import_validation`・`first_meaningful_map_mouse_flow`・`first_value_share_preflight`・`canvas_protection`・`canvas_legend`）
- **AC-5（PERF-BUDGET-01 準拠）**: 既存ハーネス `e2e/responsiveness_performance_budget.spec.ts`（300カード/30島フィクスチャ、重複計測はしていない）をそのまま実行。本セッション全体を通じて UX-MENU-01・UX-SCALE-01 (a)〜(d) の各変更後に複数回実行し、タイミング計測に到達する箇所では常に許容範囲内。ただし同フィクスチャの検索フィルタ手順に**既存の**曖昧ロケータ不具合（`getByText` が2要素にマッチ）があり、クリーンな `main` でも同一エラーで再現することを確認済み（本Issueの変更とは無関係）。PERF-BUDGET-01 のIssue自身も「タイミング予算のCI Playwright検証はローカル不可・CIのみ」と明記しており、本Issueもその制約を継承する。

これにより UX-SCALE-01 の AC-1〜5 全て充足。Status: Done。

### 追記 2026-07-09: 実装照合レビュー（design-qa-checklist）で実バグを発見・修正

本機能は design-qa-checklist（実機スクショ照合）の記録が無かったため初適用した。ミニマップ・L字型の島の輪郭・一括操作バーを実機スクショ（Docker Playwright）で確認した結果、**一括操作バーの選択件数表示（「3件のカードを選択中」）が1文字ずつ縦に折り返るバグを発見**。

原因: `BulkOperationsBar.tsx` の `role="status"` div に `whiteSpace: "nowrap"` が設定されておらず、隣接するボタン群（`buttonStyle` に `whiteSpace: "nowrap"` 設定済み）が折り返らないため、バー全体が幅で押された際にこの要素だけが折り返り先になっていた。日本語の件数文言はスペースを含まないため、通常の折返しが文字単位になり縦書き状に見えていた。既存 e2e（`bulk_operations_bar.spec.ts`）は `toContainText`/`toBeVisible` でDOM内容のみを検証するため、この視覚崩れを検出できていなかった。

修正: 当該 div に `whiteSpace: "nowrap"` を追加。回帰アンカーを `ux_operability_regression.test.ts` に追加。typecheck 0 / vitest 963 passed / `bulk_operations_bar.spec.ts` 4/4 passed で再検証済み。ミニマップ・島輪郭は乖離なし。詳細は `design-qa-checklist.md` 第4回記録を参照。
