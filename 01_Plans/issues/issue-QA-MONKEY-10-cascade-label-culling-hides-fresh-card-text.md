# Issue Draft: QA-MONKEY-10 連続作成カードのラベルカリングにより入力直後のテキストが「消えたように見える」

- Type: Bug / UX friction
- Status: Draft
- Lifecycle: Draft -> Open -> In Progress -> Done
- Source Issue: `VALUE-DOGFOOD-01`（初回ドッグフード走行での発見）
- Priority: P2
- Owner: TBD
- Scope: `03_Implement/frontend/src/canvas/CanvasShell.tsx`（labelCullingResult / acceptedLabelIds）, `03_Implement/frontend/src/App.tsx`（createCardAtPosition のカスケード配置）, `03_Implement/frontend/src/canvas/CardView.tsx`（showLabelText）
- Related Backlog: `QA-MONKEY-10`
- Related ADR/Spec: `01_Plans/adr/ADR-0042-value-realness-validation-and-notice-exit.md`（ドッグフード発見元）
- Expected verification level: `e2e`

## 背景

VALUE-DOGFOOD-01 の初回ドッグフード走行（2026-07-10、実バックエンド構成 db+api+web）で、
新規カードを4枚連続で作成しテキストを入力したところ、**入力を確定した直後のテキストが
交互のカード（あるラウンドでは0枚目と2枚目、別のラウンドでは1枚目と3枚目）で画面から消える**
現象を再現性をもって観測した（6回の独立した走行すべてで発生）。

当初はデータ喪失（コミット競合）を疑ったが、保存後の実文書を postgres から直接取得して確認した結果、
**4枚全カードのテキストは文書モデル・永続化層に完全に保持されていた**。データ喪失ではない。

## 根本原因（コードリーディングで確認済み）

1. `createCardAtPosition`（`App.tsx`）は新規カードをアンカーカード（選択中 or 末尾）から
   (+40, +40) のカスケード位置に配置する。連続作成すると各カードは前のカードと大きく重なる。
2. `CanvasShell.tsx` の `labelCullingResult` は全カードのテキストをラベル候補として
   `cullLabels()` にかけ、**ラベル矩形が重なった場合に片方を落とす**。
   落とされたカードは `showLabelText=false` となり、`CardView` は本文テキストを一切描画しない。
3. カスケード重なりのため、連続作成した隣接カードのラベル矩形は常に衝突し、
   交互のカードのテキストが非表示になる（カリングの勝者が交互になる）。

## なぜ問題か（価値毀損の観点）

- 利用者視点では「いま入力したテキストが消えた」ようにしか見えない。本ツールの根幹価値
  「思考の断片を安心して外に置ける」に対する直接の信頼毀損（実際にドッグフード中、
  データ喪失バグと誤認して原因究明に相当の時間を要した）。
- さらに悪いことに、「消えた」テキストを再入力して確定しても
  `handleCommitCardText` が `nextText === targetCard.text` で no-op になるため
  **見た目上は何も起きない**。利用者の修復行動が完全に無反応になる。
- 密集ボードでの視覚ノイズ削減というカリング自体の設計意図は正当。問題は
  「作成・編集直後のカード」にまで無差別に適用されることと、
  非表示が「テキスト欠落」と区別できない表現であること。

## 対応案（設計判断が必要）

- 案A: 選択中・編集直後（直近の編集対象）のカードをカリング対象から除外する。
- 案B: 新規カードのカスケード配置を、既存カードと重ならない位置の探索に変える。
- 案C: カリングで本文を隠す際、完全空白ではなく省略表現（例: 先頭数文字＋…）や
  「重なりのため省略」を示すマーカーを描画する。
- 案A+C の併用が有力候補（配置アルゴリズム変更より影響範囲が小さい）。

## 副次的観測（同根・記録のみ）

- カスケード重なりはポインタ操作も阻害する: 覆われたカードの中心へのクリックは
  "intercepts pointer events" となり、露出している左上隅を狙う必要があった
  （Playwright 自動操作での観測だが、実利用でも重なったカードはクリックしづらい）。
- 選択済みカードの shift-click 追加選択も、重なり順の影響で意図しないカードに
  当たり得る（島作成が有効化されないケースを観測）。

## 受け入れ条件（案）

- [ ] AC-1: 連続作成した重なりカードで、直近に編集したカードのテキストが常に表示される。
- [ ] AC-2: テキストが視覚的に省略される場合、省略されていることが利用者に分かる表現になる（完全空白にしない）。
- [ ] AC-3: 再現e2e（カード4枚連続作成→全カードのテキスト表示確認）が追加される。

## Traceability

- Derived-from: `01_Plans/issues/issue-VALUE-DOGFOOD-01-first-dogfood-run-and-friction-log.md`
- Related: `01_Plans/dogfood-log-2026-07-10.md`（発見の経緯・全証跡）
- Related: `03_Implement/frontend/scripts/dogfood_run_20260709.mjs`(再現スクリプト)
