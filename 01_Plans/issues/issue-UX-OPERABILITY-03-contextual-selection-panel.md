# Issue Draft: UX-OPERABILITY-03 選択直後に関連パネルへ自然に到達できない

- Type: Bug
- Status: Draft
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: N/A
- Priority: P1
- Owner: TBD
- Scope: `03_Implement/frontend/src/App.tsx`, `03_Implement/frontend/src/ui/`, `03_Implement/frontend/e2e/`
- Related Backlog: `UX-OPERABILITY-03`
- Related ADR/Spec: `01_Plans/adr/ADR-0001-value-to-requirements.md`, `01_Plans/adr/ADR-0030-ui-operability-progressive-disclosure-and-keyboard-scope.md`, `04_Documentation/acceptance_check.md`
- Expected verification level: `e2e`

## Requirement meta I/F（共通キー）

- RequirementID: UX-OPERABILITY-03
- RequirementStatement: 利用者がカードまたは島を選択した直後に、選択対象の確認・編集・レビューに関わる情報へ迷わず到達できる。
- PriorityClass（Must / Should / Could）: Must
- AcceptanceScenario（前提 / 操作 / 期待結果 / 除外）: 前提=標準サンプル `doc_phase1_canvas` を開く / 操作=カード「ユーザー課題を集める」をマウスで選択する / 期待結果=選択対象の本文、レビュー状態、次にできる操作が右側パネルの現在表示範囲または明示導線で確認できる / 除外=高度レビュー、CE3、診断、文章化の全面再設計。
- GoNoGoGate（Required / Optional / N/A）: Required
- SecurityGateImpact（SafeMode / share-export / import-sanitize / public-exposure）: N/A
- VerificationLevel（docs-check / unit / integration / e2e）: e2e
- DecisionStatus（Fixed / Pending）: Pending
- DecisionQueueRef（未確定時の参照先）: `ADR-0030`

## 1) 課題 / Problem statement

- マウスでカードを選択しても、直後に右側パネル上部へ表示されるのはレビュー差分、文章化、候補比較、CE3、批評入力などであり、選択カードの確認領域は下部に埋もれている。
- 2026-05-14 の検証では、カード選択後の「カードの確認」は `y=3956`、`1 card selected` は `y=3987` にあり、viewport `900px` の現在表示範囲外だった。
- 操作の結果がすぐ見えないため、利用者は「カードを選べたのか」「次に何をするのか」を判断しにくい。

## 2) 背景 / Context

- `04_Documentation/acceptance_check.md` はマウスとキーボードで基本操作が自然に行えることを確認対象としている。
- 現在の右側パネルは多機能で、初期表示にレビュー差分、文章化、統合候補、パッチワークスペース、批評、差分確認、ガイド付きフロー、診断などが連続している。
- 選択対象の詳細は存在するが、初回利用者が見つけやすい位置にない。

## 3) 判断基準による優先度評価

- 価値・判断軸（ADR-0001）: `UX-06` の俯瞰と詳細の往復は、選択後に詳細が即座に見えることで成立する。
- 安全（THREAT_MODEL / SafeMode）: 直接の安全境界ではないが、レビュー状態の見落としは誤判断につながる。
- 企業・行政要件（enterprise_architecture）: レビュー状態や根拠確認にすぐ到達できることは組織利用で重要。
- 後方互換（schemas）: 表示順序と導線の改善であり、データ互換は維持する。

## 4) 提案する解決策 / Proposed solution

- 変更対象:
  - 右側パネルの表示順序、折りたたみ、タブ、または選択後の自動スクロール。
  - 選択対象の概要、本文、レビュー状態、主要操作を最上位に置く。
  - 高度機能はタスク別に畳むか、明示的なモード切替へ移す。
- 変更の最小単位:
  - カード選択時に「カードの確認」領域が現在表示範囲へ来ることを先に固定する。
  - 島選択時も同様のパターンへ拡張する。
- 非目標:
  - すべての右側パネル機能を削除すること。
  - CE3や文章化の機能仕様をこのIssueで変更すること。

## 5) 受入条件 / Acceptance criteria

- [ ] カードをマウス選択した直後、選択カードの本文または選択状態が現在表示範囲内で確認できる。
- [ ] キーボード選択後も同じ確認領域へ到達できる。
- [ ] 選択カードのレビュー状態、主張タイプ、根拠リンクなどの主要操作が高度ツールより前に提示される。
- [ ] 右側パネル内の高度機能は、選択確認を妨げない位置または折りたたみに整理される。
- [ ] 既存のレビュー差分、文章化、CE3、診断機能への到達導線は失われない。
- [ ] Playwrightで「カード選択後に選択確認が可視範囲へ入る」ことを検証する。

## 6) 実装タスク分解 / Task breakdown

- [ ] T1 右側パネルの領域を「選択対象」「レビュー/文章化」「高度ツール」に分類する。
- [ ] T2 カード選択後の表示優先順位または自動スクロール方針を実装する。
- [ ] T3 島選択時の表示優先順位も同じ方針に揃える。
- [ ] T4 E2Eでカード選択後の可視性を固定する。

## 7) 検証計画 / Validation plan

- 実行コマンド:
  - `cd 03_Implement/frontend && node .\\node_modules\\typescript\\bin\\tsc --noEmit`
  - `cd 03_Implement/frontend && node .\\node_modules\\vitest\\vitest.mjs run`
  - `cd 03_Implement/frontend && node .\\node_modules\\playwright\\cli.js test <new-selection-panel-spec> --reporter=line`
- 期待結果:
  - 標準サンプルでカード選択後、選択確認領域がviewport内にある。
- 未実施時の理由・代替検証:
  - 自動E2E追加前は、Playwright script の bounding box ログで `カードの確認` / `1 card selected` がviewport内にあることを代替確認する。

## 8) 代替案 / Alternatives considered

- 代替案A: 右側パネル全体を現状のままにし、文書で下へスクロールするよう案内する。操作結果が見えない違和感を解消しないため不十分。
- 代替案B: 選択詳細だけをモーダルにする。キャンバスとの往復が重くなる可能性があるため、まず右側パネル内の文脈優先を検討する。

## 9) リスクとロールバック / Risks & rollback

- 失敗モード: 高度機能を畳みすぎて既存利用者が機能を見つけにくくなる。
- 影響範囲: 右側パネル、カード/島選択、E2E、受け入れ確認。
- ロールバック手順: パネル順序または自動スクロール変更を戻し、既存配置へ戻す。

## 10) Additional context

- 2026-05-14 検証:
  - Edge Chromium（Chrome代替） / `http://127.0.0.1:5173/?locale=ja` / viewport `1440x900`
  - マウスで `ユーザー課題を集める` を選択。
  - `scrollY=0` のまま、`カードの確認` は `y=3956`、`1 card selected` は `y=3987` でviewport外。

---

## Authoring Checklist（人間/生成AI 共通）

- [x] `Source Issue` が運用状態と整合している。
- [x] `Related ADR/Spec` が最低1件ある。
- [x] 受入条件に「安全」「互換」「検証」が含まれる。
- [x] `Validation plan` に具体コマンドがある。
- [x] 非目標が明記されスコープ逸脱を防いでいる。
