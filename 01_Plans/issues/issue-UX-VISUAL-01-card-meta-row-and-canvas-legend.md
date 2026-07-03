# Issue Draft: UX-VISUAL-01 カードのメタ行分離とキャンバス内凡例

- Type: Feature request
- Status: Draft
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P1
- Owner: TBD
- Scope: `03_Implement/frontend/src/canvas/CardView.tsx`, `03_Implement/frontend/src/canvas/`, `03_Implement/frontend/src/i18n/locales/`, `03_Implement/frontend/src/ui/ux_operability_regression.test.ts`
- Related Backlog: `UX-VISUAL-01`
- Related ADR/Spec: `01_Plans/adr/ADR-0048-visual-language-command-reach-and-kj-vocabulary.md`（D1）, `01_Plans/adr/ADR-0043-complexity-budget-for-cognitive-load.md`, `01_Plans/issues/issue-DOMAIN-EXPR-01-readonly-state-surfacing.md`（Done・バッジ過多リスクの引き継ぎ）
- Expected verification level: `e2e`

## Requirement meta I/F（共通キー）

- RequirementID: UX-VISUAL-01
- RequirementStatement: カードの状態表示（claimType・保留系・未レビュー・違和感・矛盾）を ADR-0048 D1 の4チャネル規則（色/形/位置/密度）に従いメタ行へ再配置し、本文の文頭が常に読める状態にする。あわせて既定OFFの開閉式凡例をキャンバス内に提供する。
- PriorityClass（Must / Should / Could）: Should
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=claimType・holdState・critique・未レビューが同時に付いたカードを含む文書を開く / 操作=カードを目視・凡例を開閉 / 期待結果=バッジが本文1行目に重ならず、状態はメタ行・左エッジ・右上・行末に分散し、凡例で全チャネルの意味を参照できる / 除外=状態の追加・スキーマ変更・LOD 閾値の変更。
- GoNoGoGate（Required / Optional / N/A）: Optional
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: N/A（表示のみ）
- VerificationLevel（docs-check / unit / integration / e2e）: e2e
- DecisionStatus（Fixed / Pending）: Fixed（ADR-0048 D1）
- DecisionQueueRef: `ADR-0048`

## 1) 課題 / Problem statement

- DOMAIN-EXPR-01/02（Done）が導入したバッジ群は、カード本文1行目に重なり文頭が読めない（`ui-card-domain-badges.png` で観測、壁打ち課題5）。一級データであるはずの状態表示が本文と可読性を取り合っている。
- 状態の意味を画面内で参照する手段が無い（View パネル内の LOD 説明のみ）。状態が増えるたびに暗黙知が増える。

## 2) 背景 / Context

- ADR-0048 D1 が4チャネル規則と「凡例は既定OFF」を確定済み。本Issueはその最小実装（壁打ち成果の段階1）。
- DOMAIN-EXPR-01 の Risks 節は「バッジ過多」を自らの失敗モードとして予見しており、本Issueはその是正を引き継ぐ（再決定ではない）。

## 3) 判断基準による優先度評価

- 価値（ADR-0001 P-01/P-03）: 保留・違和感・未レビューの可読性はコア価値の表示面。本文が読めない状態は思考を雑にする。
- 安全: 表示のみ。share/export 境界に影響なし。
- 規模拡大: 4チャネル規則は状態追加に対する恒久的な受け皿。
- 後方互換: スキーマ変更なし。表示の再配置のみ。

## 3.2 非目標 / Non-goals

- 新しい状態・スキーマの追加。LOD 閾値・構造レベルの変更。色トークンの変更（既存トークンの意味固定は ADR-0048 で決定済み）。

## 4) 提案する解決策 / Proposed solution

- CardView に**メタ行**を導入: 本文の上に claimType 型バッジ＋保持系 amber ピル＋（末尾）矛盾件数。未レビューは右上の点、違和感は左エッジ tick＋件数に再配置。文頭は常に可読。
- **凡例**: 既定OFFの開閉（ショートカットは UX-SHORTCUT-01 に委譲、まずはボタン起動）。型（色）/ 保持系（位置）/ 確認（形）/ 根拠・矛盾（色＋形）の4群を1画面で提示。
- 遠景 LOD でも未レビュー・違和感の点は残す（ADR-0048 D1、既存 LOD 実装への追記）。
- 英語/和訳の混在（Fact/事実）を和訳へ統一し、i18n カタログを同期。

## 5) 受け入れ条件 / Acceptance criteria

- [ ] AC-1: 全状態（claimType＋保留＋未レビュー＋違和感＋矛盾）を同時に付けたカードで、本文1行目が隠れないことが e2e で固定される。
- [ ] AC-2: 凡例が既定で非表示、明示操作で開閉し、Escape で閉じてトリガへフォーカス復帰する（ADR-0030 契約）。
- [ ] AC-3: 遠景 LOD で未レビュー・違和感の点が残ることが e2e で確認される。
- [ ] AC-4: `ux_operability_regression.test.ts` の初期表示アンカーが非回帰（UX-COMPLEXITY-01 AC-3 の上限内）。
- [ ] AC-5: i18n（ja/en）のキー整合テストが通る。

## 6) 実装タスク分解 / Task breakdown

- [ ] T1 CardView のメタ行レイアウト＋バッジ再配置。
- [ ] T2 凡例コンポーネント（既定OFF・開閉・フォーカス契約）。
- [ ] T3 LOD 遠景での点保持。
- [ ] T4 i18n 和訳統一＋カタログ同期。
- [ ] T5 e2e（メタ行可読性・凡例開閉・LOD 点）＋回帰アンカー確認。

## 7) 検証計画 / Validation plan

- `cd 03_Implement/frontend && npm run typecheck && npm test`
- `npx playwright test`（メタ行・凡例・LOD の新規 spec を含む）
- `rg -n "data-ui-region|advanced" src/ui/ux_operability_regression.test.ts`（アンカー非回帰）

## 複雑性予算（ADR-0043 自己申告）

複雑性予算: 初期表示への純増=なし（バッジ再配置は置換。凡例は既定OFFで呼び出し時のみ） / 保留操作の距離=改善（保持系がメタ行先頭＝確定情報より手前に固定） / 取り消し導線=あり（凡例は Escape/再操作で閉じる）

## Traceability

- Related: `01_Plans/adr/ADR-0048-visual-language-command-reach-and-kj-vocabulary.md`
- Related: `01_Plans/issues/issue-DOMAIN-EXPR-01-readonly-state-surfacing.md`, `issue-DOMAIN-EXPR-02-hold-and-pending-shelf.md`
- Related: `04_Documentation/ui_catalog.md`（§4 現行バッジ）, `02_Architecture/design/kj-atlas 拡張提案.dc.html`（観点3・図B）
- Derived-from: `01_Plans/adr/ADR-0048-visual-language-command-reach-and-kj-vocabulary.md`

## 実装設計の到着（2026-07-04）

- Claude Design Round 4 成果（`02_Architecture/design/kj-atlas 拡張提案.dc.html` §段階1レッドライン・図BB）に本Issueの実装仕様（タイポ 本文13/メタ12/補助11/凡例10・左帯3px・メタ行 padding 7/11・バッジ角丸4・未レビュー点7px・凡例右下オーバーレイ ⌘/ 開閉）が確定。実装時はこれを参照実装（プロトタイプ同梱）とする。
