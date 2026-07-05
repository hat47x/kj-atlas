# Issue Draft: UX-EMPTY-01 空キャンバスの中核ループ誘導（操作で消えるオンボーディング）

- Type: Feature request
- Status: Done
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P1
- Owner: Codex
- Scope: `03_Implement/frontend/src/App.tsx`, `03_Implement/frontend/src/canvas/`, `03_Implement/frontend/src/i18n/locales/`, `03_Implement/frontend/e2e/`
- Related Backlog: `UX-EMPTY-01`
- Related ADR/Spec: `01_Plans/adr/ADR-0048-visual-language-command-reach-and-kj-vocabulary.md`（D3 憲章）, `01_Plans/adr/ADR-0043-complexity-budget-for-cognitive-load.md`（CB-1 空状態）, `01_Plans/issues/issue-PRODUCT-UX-01-first-run-document-entry.md`（Done・入口のみ）, `01_Plans/issues/issue-PRODUCT-VALUE-01-first-meaningful-map-activation.md`（In Progress・連携）
- Expected verification level: `e2e`

## Requirement meta I/F（共通キー）

- RequirementID: UX-EMPTY-01
- RequirementStatement: 文書を開いた/作成した後のカード0枚キャンバスで、最初の一手と中核ループ（書く→並べる→束ねる→つなぐ→保留する）を、常設せず操作で消える誘導として提示する。「保留は健全」という核思想を初回体験で伝える。
- PriorityClass（Must / Should / Could）: Should
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=新規文書を作成し provider=none・詳細OFF / 操作=空キャンバスを表示→最初のカードを作成 / 期待結果=空状態ヒント（最初の一手＋「決めないのは健全」）が表示され、カード作成と同時に消える。各ループ段階の示唆はその操作を一度行うと再表示されない / 除外=StartPanel（入口）の再設計、常設チュートリアル、AI 依存の誘導。
- GoNoGoGate（Required / Optional / N/A）: Optional
- SecurityGateImpact: N/A
- VerificationLevel: e2e
- DecisionStatus（Fixed / Pending）: Fixed（ADR-0048 D3 憲章＋壁打ち観点1）
- DecisionQueueRef: `ADR-0048`

## 1) 課題 / Problem statement

- PRODUCT-UX-01（Done）は開始パネル（入口）のみを対象とし、**文書を開いた後の空キャンバス**は明示的にスコープ外（同 memo L69/L146）。現状はただの白紙で、最初の一手も中核ループも「保留の健全さ」も伝わらない。
- 常設チュートリアルは CB-1（既定の静けさ）に反するため、「操作で前進し消える」誘導が必要。

## 2) 背景 / Context

- 壁打ち成果（拡張提案 観点1・図C）が空状態ヒント＋5ステップの消える示唆を設計済み。プロトタイプに実装例あり。
- PRODUCT-VALUE-01（In Progress）が初回価値到達（3枚・1まとまり・保存/共有前確認）の KPI とヒントを所有。本Issueは**表示面（空状態とループ示唆）**を担当し、KPI・進捗判定は PRODUCT-VALUE-01 に委ねる（重複禁止）。

## 3) 判断基準による優先度評価

- 価値: 初回体験で「曖昧さの保持は健全」を伝えることはコア価値の伝達そのもの。低コスト・高効果（壁打ち段階1）。
- 安全: 表示のみ。provider=none で完結。
- 規模拡大: 誘導は消えるため恒常負荷ゼロ。
- 後方互換: スキーマ変更なし（既習得フラグはローカル保存）。

## 3.2 非目標 / Non-goals

- StartPanel の再設計（PRODUCT-UX-01 Done の再決定禁止）。常設チュートリアル・ツアーの自動起動。KPI 計測（PRODUCT-VALUE-01 の領分）。AI による誘導。

## 4) 提案する解決策 / Proposed solution

- 空キャンバス（cards=0）に1枚のヒント: 「まず、思いついたことを1枚書く」＋核思想の一文（「正しさはあとで。曖昧なまま置いていい」）＋『＋新規カード』『サンプルを開く』への導線。**最初のカード作成で消える**。
- 中核ループの示唆（2枚目→ドラッグ、2枚選択→島を作成、右クリック→関係線、迷ったら→保留）は各操作を一度行うと二度と出ない。既習得状態はローカルに保持し、設定から再表示可能。
- フォーカスを奪わない（aria-live=polite）。キーボードのみでも前進可能。

## 5) 受け入れ条件 / Acceptance criteria

- [x] AC-1: 新規文書の空キャンバスでヒントが表示され、カード1枚作成で消えることが e2e で固定される。
- [x] AC-2: 各ループ示唆が該当操作の初回実行後に再表示されないこと、および設定からの再表示が可能なことを確認。
- [x] AC-3: 誘導がフォーカスを奪わず、Tab 順・既存キーボード契約（UX-OPERABILITY-01/02）が非回帰。
- [x] AC-4: provider=none・詳細OFF の既定構成のみで完結（AI 参照なし）。
- [x] AC-5: `ux_operability_regression.test.ts` の初期表示アンカー非回帰。

## 6) 実装タスク分解 / Task breakdown

- [x] T1 空状態ヒントコンポーネント（cards=0 判定・消失遷移）。
- [x] T2 ループ示唆の既習得管理（localStorage）＋設定からの再表示。
- [x] T3 i18n（ja/en）追加。
- [x] T4 e2e（表示→消失、示唆の一回性、フォーカス非奪取）。

## 7) 検証計画 / Validation plan

- `cd 03_Implement/frontend && npm run typecheck && npm test && npx playwright test`
- PRODUCT-VALUE-01 のヒント（DomainStateSummary）と表示が競合しないことを目視＋e2e で確認。

## 複雑性予算（ADR-0043 自己申告）

複雑性予算: 初期表示への純増=なし（空状態と未習得時のみ表示し、中身が出たら消える） / 保留操作の距離=改善（「迷ったら保留」をループの正規ステップとして提示） / 取り消し導線=あり（誘導は再表示可能・すべての一手は元に戻せる）

## Traceability

- Related: `01_Plans/adr/ADR-0048-visual-language-command-reach-and-kj-vocabulary.md`
- Related: `01_Plans/issues/issue-PRODUCT-UX-01-first-run-document-entry.md`（スコープ境界）, `issue-PRODUCT-VALUE-01-first-meaningful-map-activation.md`（連携先）
- Related: `02_Architecture/design/kj-atlas 拡張提案.dc.html`（観点1・図C）
- Derived-from: `01_Plans/adr/ADR-0048-visual-language-command-reach-and-kj-vocabulary.md`

## 実装設計の到着（2026-07-04）

- Claude Design Round 4 成果（同上 §段階1レッドライン）に空状態ヒントの出現・消滅条件（カード0枚時のみ・最初のカード作成で消滅・コーチマークは一度実行で再表示なし=localStorage）の仕様が確定。プロトタイプが参照実装。
- 2026-07-04 Codex: `EmptyCanvasHint` を追加し、新規文書を `cards: []` から開始するように変更。StartPanelを閉じた後の空キャンバスでだけ初回ヒントを表示し、`Write first card` / `最初のカードを書く` 操作でカード作成と同時に消えることを `empty_canvas_onboarding.spec.ts` で確認する方針にした。再表示抑制・リセット導線（AC-2）は別スライスで継続。
- 2026-07-04 Codex: 初回カード作成時に空キャンバスヒントの完了状態を localStorage に保存し、以後の空キャンバスでは再表示しないようにした。表示パネルから「空キャンバスのヒントを再表示」できるリセット導線を追加し、同一E2Eで再表示まで確認する方針に更新。
