# Issue Draft: UX-OPERABILITY-01 マウス・キーボード操作を含むUI/UX動線レビュー

- Type: Bug
- Status: Draft
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P1
- Owner: Codex
- Scope: `03_Implement/frontend/src/`, `04_Documentation/acceptance_check.md`
- Related Backlog: `UX-OPERABILITY-01`
- Related ADR/Spec: `01_Plans/adr/ADR-0001-value-to-requirements.md`, `01_Plans/adr/ADR-0030-ui-operability-progressive-disclosure-and-keyboard-scope.md`, `02_Architecture/architecture.md`, `04_Documentation/acceptance_check.md`
- Expected verification level: `e2e`

## Requirement meta I/F（共通キー）

- RequirementID: UX-OPERABILITY-01
- RequirementStatement: 一般利用者がマウスまたはキーボードで、主要操作へ自然に到達し、結果を理解し、戻れる状態にする。
- PriorityClass（Must / Should / Could）: Must
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=標準サンプルドキュメントをChromeで開く / 操作=新規作成、カード選択、島作成、表示切替、共有前確認、保存をマウスとキーボードで行う / 期待結果=フォーカス順序、ボタン名、パネル配置、戻り導線が自然で、見切れや重なりがない / 除外=全面的な情報設計リニューアル。
- GoNoGoGate（Required / Optional / N/A）: Required
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: SafeMode / share-export
- VerificationLevel（docs-check / unit / integration / e2e）: e2e
- DecisionStatus（Fixed / Pending）: Pending
- DecisionQueueRef（未確定時の参照先）: N/A

## 1) 課題 / Problem statement

- 右側パネルの一部で横幅が不足し、ボタンや入力欄が見切れる状態が確認された。
- UI上に英語ラベルが残っており、日本語利用者にとって操作の意味が直感的でない箇所がある。
- 一般利用者向け文書では、マウス操作だけでなくキーボード操作、フォーカス順序、戻り方、操作結果の分かりやすさまで扱う必要がある。
- 2026-05-14 の代表操作検証で、カードがキーボード選択できない、カード選択後に関連詳細が現在表示範囲へ出ない、表示/共有パネルが `Escape` で閉じない、主要ツールバーにlegacy操作が目立つ、という具体課題を確認した。

## 2) 背景 / Context

- `04_Documentation/acceptance_check.md` に、マウスとキーボードで確認する観点を追加した。
- 既存の `QA-MONKEY-05` と `QA-MONKEY-06` は、島操作のアクセシビリティとヘッダーのレスポンシブ崩れを修正済み。
- ただし、画面全体の自然な操作動線を製品品質として固定するには、個別修正を横断的に検証する必要がある。

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: 思考の整理に集中するには、操作が予測可能である必要がある。
- 安全（THREAT_MODEL / SafeMode）: SafeMode、共有、export の操作名や状態が見えないと、誤共有につながる。
- 企業・行政要件（enterprise_architecture）: キーボード操作とアクセシビリティは組織導入の前提になりやすい。
- 後方互換（schemas）: UI動線改善であり、データ契約は維持する。

## 4) 提案する解決策 / Proposed solution

- 変更対象:
  - ヘッダー、表示パネル、共有と再現パネル、右側パネル、CE3パッチワークスペース、ナラティブ、関係要約
- 変更の最小単位:
  - 主要ユーザージャーニーをPlaywrightで記録し、見切れ、未翻訳、フォーカス迷子、戻れない操作を個別修正する。
  - 個別修正が大きいものは `UX-OPERABILITY-02` 以降へ分離し、操作モデルの判断は `ADR-0030` で管理する。
- 非目標:
  - 画面構成やナビゲーション全体を一度に作り替えること。

## 5) 受入条件 / Acceptance criteria

- [ ] 主要操作のボタン名、入力欄、状態表示が日本語UIで理解できる。
- [ ] マウス操作で、操作後の結果と次にできることが分かる。
- [ ] キーボード操作で、主要パネルを開き、操作し、閉じるまたは次の操作へ移れる。
- [ ] 右側パネルと共有パネルのボタン、入力欄、長いラベルが見切れない。
- [ ] SafeMode、共有、export に関わる操作は、見た目上もキーボード上も到達可能である。
- [ ] ADR化が必要な情報設計変更は、本Issueで確定せずADR候補として分離される。

## 6) 実装タスク分解 / Task breakdown

- [x] T1 Chromeで標準サンプルを開き、マウス操作の主要経路を記録する。
- [x] T2 `Tab` / `Enter` / `Space` / テキスト入力で同じ経路を確認する。
- [x] T3 不自然な操作名、重なり、見切れ、フォーカス順序を分類する。
- [ ] T4 小さく直せるUIラベル・レイアウトは修正する。
- [x] T5 情報設計やナビゲーションの変更が必要なものはADR候補として分離する。

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `npm run typecheck`
  - `npm run test:i18n`
  - `npx playwright test e2e/header_toolbar_layout.spec.ts --reporter=line`
  - Chromeで 1280px / 960px / 390px の手動確認
- 期待結果:
  - 操作名が読み取れ、見切れがなく、キーボードで主要操作に到達できる。

## 8) 代替案 / Alternatives considered

- 代替案A: 未翻訳ラベルだけ直す。操作導線の不自然さが残るため不十分。
- 代替案B: 大規模なナビゲーション再設計を先行する。ADRが必要な判断を含むため、本Issueでは検出と小修正を先に行う。

## 9) リスクとロールバック / Risks & rollback

- 失敗モード: 小さなラベル修正が既存テストや利用者の慣れた操作を壊す。
- 影響範囲: frontend UI、i18n、E2E、公開文書。
- ロールバック手順: UI修正をコンポーネント単位で戻し、文書更新は `acceptance_check.md` の観点追加だけに残す。

## 10) Additional context

- ADR化が必要になる条件: ヘッダー/サイドパネル/共有と再現の情報設計、ショートカット体系、キーボード操作モデルを再定義する場合。
- 2026-05-14 実施ログ:
  - 実行環境: Edge Chromium（Chrome代替。ローカルChrome実体は未検出） / `http://127.0.0.1:5173/?locale=ja` / backend `127.0.0.1:8000` 起動済み。
  - viewport: `1440x900`, `960x720`, `390x844`。
  - 起動確認: `/api/docs/doc_phase1_canvas` は frontend proxy 経由で 200。`Internal Server Error` は画面本文に出ない。
  - 検証済みの良好点: 検索欄に `観察` を入力すると `1/1` になり、検索状態は理解できる。共有パネルの右端見切れは `390px` / `960px` / `1440px` で再発なし。SafeMode と共有範囲ラベルは日本語表示。
  - 課題1: `Tab` 70回の巡回にキャンバスカード本文が含まれず、`CardView.tsx` も `div` + pointer handler のみでキーボード選択の意味付けがない。起票: `issue-UX-OPERABILITY-02-keyboard-card-selection.md`。
  - 課題2: マウスで `ユーザー課題を集める` を選択しても、`カードの確認` は `y=3956`、`1 card selected` は `y=3987` で現在viewport外。起票: `issue-UX-OPERABILITY-03-contextual-selection-panel.md`。
  - 課題3: `表示` / `共有と再現` を開いた後、`Escape` で閉じられない。起票: `issue-UX-OPERABILITY-04-panel-dismissal-focus-scope.md`。
  - 課題4: 起動直後の主要ツールバーに `JSON取り込み` / `JSON書き出し` が目立ち、画面上ではlegacy導線として案内される。起票: `issue-UX-OPERABILITY-05-primary-toolbar-task-prioritization.md`。
  - ADR: 右側パネルの段階的開示、選択文脈優先、パネルの閉じ方、キーボードスコープを `ADR-0030-ui-operability-progressive-disclosure-and-keyboard-scope.md` として提案。

---

## Authoring Checklist（人間/生成AI 共通）

- [x] `Source Issue` が運用状態と整合している。
- [x] `Related ADR/Spec` が最低1件ある。
- [x] 受入条件に「安全」「互換」「検証」が含まれる。
- [x] `Validation plan` に具体コマンドがある。
- [x] 非目標が明記されスコープ逸脱を防いでいる。
