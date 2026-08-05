# Issue Draft: UX-VISUAL-02 少数意見の可視化（一匹狼・小さな島の保護強調）

- Type: Feature request
- Status: Done
- Source Issue: N/A
- Priority: P3
- Owner: Claude Code
- Scope: `03_Implement/frontend/src/canvas/`, `03_Implement/frontend/src/ui/`, `03_Implement/frontend/src/i18n/locales/`, `03_Implement/frontend/e2e/`
- Related Backlog: `UX-VISUAL-02`
- Related ADR/Spec: `01_Plans/adr/ADR-0048-visual-language-command-reach-and-kj-vocabulary.md`（D3 改訂 2026-07-03・D1 4チャネル規則）, `01_Plans/adr/ADR-0043-complexity-budget-for-cognitive-load.md`, `01_Plans/issues/issue-UX-VISUAL-01-card-meta-row-and-canvas-legend.md`（凡例への追記先）
- Expected verification level: `e2e`

## Requirement meta I/F（共通キー）

- RequirementID: UX-VISUAL-02
- RequirementStatement: 一匹狼（どの島にも属さないカード）・小さな島・単独の違和感を「弱い/劣る」でなく保護対象として淡く強調し、多数派への収束圧力に抗する表示を提供する。点数・順位・比率は提示しない（反スコアリング）。
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=島に属するカード群と、属さないカード1枚を含む文書を開く / 操作=キャンバスを俯瞰・凡例を開く / 期待結果=一匹狼カードに控えめな「少数」マークが付き、凡例に意味（保護対象であり劣後ではない）が記載される。件数・比率・順位は表示されない / 除外=少数意見の自動抽出/AI 判定、強調の常時大型表示、スコア化。
- SecurityGateImpact: N/A（表示のみ）

## 1) 課題 / Problem statement

- KJ法の「一匹狼を許す」（無理に分類しない）は憲章として採択済みだが、表示上は無所属カード・小さな島が視覚的に「取り残し」に見え、束ねて解消したくなる収束圧力が働く。
- 少数・単独であることを健全な状態として肯定的に見せる手段が無い。

## 2) 背景 / Context

- ADR-0048 D3 改訂で条件付き採択: 保護対象としての淡い強調・表示のみ・反スコアリング・既定は控えめ（CB-1）。プロトタイプでカード面の「少数」バッジを検証済み。
- 判定は決定論（島メンバーシップ・違和感の単独性）で行い、AI を使わない。

## 3) 判断基準による優先度評価

- 価値（ADR-0001 P-01/P-02）: 一匹狼の保護は「早すぎる収束を防ぐ」核価値の表示面。単一正解への誘導をしない設計と一体。
- 安全: N/A。
- 規模拡大: 大規模文書ほど少数の埋没が起きやすく、俯瞰時の発見性に寄与（LOD 遠景での扱いは UX-VISUAL-01 の点規則に従属）。
- 後方互換: スキーマ変更なし（表示導出のみ）。

## 3.2 非目標 / Non-goals

- 少数意見の内容的な自動判定（意味解析）。件数・比率・順位・「少数派スコア」の表示。強調の常時大型化。束ね推奨の自動提示。

## 4) 提案する解決策 / Proposed solution

- 判定（決定論）: どの島にも属さないカード＝一匹狼。メンバー数が閾値以下（例: ≤2）の島＝小さな島。単独の違和感タグ＝単独 critique。いずれも導出値でスキーマに保存しない。
- 表示: メタ行に淡い「少数」ピル（amber 系ではなく中立色。保持系と混同しないチャネル選択は ADR-0048 D1 に従う）。島は表札の淡いマーク。ホバー/選択時に「保護対象（無理に分類しない）」の一文。
- 凡例（UX-VISUAL-01）に1行追加: 少数=保護対象。
- 表示トグル: View パネルに ON/OFF（既定は控えめ表示 ON か OFF かを実装時に CB-1 自己申告で決定し記録）。

## 5) 受け入れ条件 / Acceptance criteria

- [x] AC-1: 一匹狼カード・小さな島に決定論でマークが付くことが e2e で固定される（`e2e/canvas_protection.spec.ts`・`CardView.protection.render.test.ts`）。「単独違和感」は一匹狼カードが critique を併せ持つケースとして自然に表現され、別チャネルを増やさない（下記完了記録）。
- [x] AC-2: 件数・比率・順位・スコアがどこにも表示されない（render/e2e で非スコアを固定）。
- [x] AC-3: 凡例に意味（保護対象・優劣ではない）が記載され、i18n（ja/en）が同期する（`legend.group.protection`/`legend.item.protected`）。
- [x] AC-4: マークの追加で本文可読性（UX-VISUAL-01 のメタ行規則）が非回帰（isProtected はメタ行の表示条件に**加える**だけ・vitest 全件通過）。
- [x] AC-5: 初期表示アンカー非回帰（トグルは View パネル内・core-action×7 不変）＋CB-1 自己申告（完了記録に記載）。

## 6) 実装タスク分解 / Task breakdown

- [x] T1 決定論判定（島メンバーシップ・閾値）の導出ロジック。
- [x] T2 メタ行/表札マーク＋ホバー文言＋i18n。
- [x] T3 凡例追記＋View トグル。
- [x] T4 e2e（判定・非スコア・非回帰）。

## 7) 検証計画 / Validation plan

- `cd 03_Implement/frontend && npm run typecheck && npm test && npx playwright test`

## 複雑性予算（ADR-0043 自己申告）

複雑性予算: 初期表示への純増=マークのみ（小・淡色。凡例1行追加。トグルは View パネル内） / 保留操作の距離=不変（少数マークは保持系の位置規則を侵さない） / 取り消し導線=あり（View トグルで非表示化可能）

## Traceability

- Related: `01_Plans/adr/ADR-0048-visual-language-command-reach-and-kj-vocabulary.md`（D3 改訂・D1）
- Related: `01_Plans/issues/issue-UX-VISUAL-01-card-meta-row-and-canvas-legend.md`
- Related: `02_Architecture/design/kj-atlas 拡張提案.dc.html`（仕様精査 B）, `02_Architecture/design/kj-atlas プロトタイプ.dc.html`
- Derived-from: `01_Plans/adr/ADR-0048-visual-language-command-reach-and-kj-vocabulary.md`

## 実装設計の到着（2026-07-04）

- Claude Design Round 4 でマークのラベルが「少数」から**「保護」**（保護対象・無理に分類しない）へ改訂された。実装時は「保護」系ラベルを採用し、本文の「少数」表記は読み替える（意味・条件は不変: 淡い強調・非スコア・CB-1）。

## 完了記録 2026-07-06（Claude Code）

- 判定（決定論・AI不使用）: `CanvasShell` の `protectedCardIdSet` = 一匹狼（どの島にも属さないカード）を **islands.length > 0 のときのみ**（＝クラスタリングが始まって初めて「孤立」が意味を持つ。新規文書で全カードが一匹狼になる誤検出を回避）。小さな島 = `island.cardIds.length <= 2`（App の islandViews で判定し IslandView へ）。
- 表示: `CardView` メタ行に中立スレートの「保護」ピル（bg `#f8fafc`・border `#cbd5e1`・fg `#475569`＋小さな角丸ドット。**amber も型色も使わない**＝ADR-0048 D1 の1チャネル1意味を堅持）。`IslandView` は表札の件数バッジの隣に中立「保護」マーク。ホバー/aria に「保護対象（無理に分類しない・優劣ではない）」。
- 凡例（UX-VISUAL-01 の `CanvasLegend`）に「保護」群を1行追加 → UX-VISUAL-01 側の残タスク（凡例1行追加）も本PRで解消。
- トグル: View パネルに「保護マークを表示/隠す」（`showProtectionMarks`・aria-pressed）。**既定ON**。
- **CB-1 自己申告**: 既定ON は本機能の価値（収束圧力に抗して少数を今この場で可視化する）に不可欠で、ADR-0048 D3 の「淡く強調」に一致。マークは小・淡色・データ駆動（コントロールではない）で初期表示コントロールアンカー（core-action×7）に不変。一匹狼は islands 存在時のみ・島は≤2 に限定し純増を有意な少数へ限定。OFF トグルで可逆。→ CB-1 遵守。
- 検証: typecheck 0 / vitest **871 passed**（179 files。protection render 3・回帰アンカー1追加含む）/ e2e `canvas_protection` 1 passed（既定表示→島メンバーは非表示→凡例説明→OFFで消滅→ONで復帰）+ `canvas_legend`・`card_meta_row` 非回帰 / 実機スクショで設計照合（大島=無印・小島=保護・一匹狼=仮説＋保護、中立色・非スコア）。

## 追加検証記録 2026-07-08（Codex）

- Codex 環境では `npm` が PATH に無い場合があるため、Playwright の webServer 起動を `node node_modules/vite/bin/vite.js --host 127.0.0.1 --port 4173` に変更した。
- `@playwright/test` 1.61.1 と一致する Chromium v1228 をローカルに導入し、`node node_modules\@playwright\test\cli.js test e2e/protected_voice_markers.spec.ts --reporter=list` が実ブラウザで通過した。
- Vite の backend proxy はバックエンド未起動時に `/docs/doc_phase1_canvas` で警告を出すが、このE2Eは route fulfill で対象文書を固定しており、検証対象の保護マーカー挙動は成功している。
